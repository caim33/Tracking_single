"""Training-identical single-motion observations and ONNX actions.

Adapts the joint mapping and affine action contract preserved in reference/.
No transport or robot command is issued here. See docs/05_deploy.md.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.spatial.transform import Rotation
from pipeline.motion import load_motion, name_indices

OBSERVATIONS = [('command', 58), ('motion_anchor_ori_b', 6), ('base_ang_vel', 3),
                ('joint_pos', 29), ('joint_vel', 29), ('actions', 29)]

def rotation(wxyz):
    """Convert a unit wxyz quaternion to SciPy's xyzw rotation convention."""
    q = np.asarray(wxyz)
    if q.shape != (4,) or not np.isfinite(q).all() or not np.isclose(np.linalg.norm(q), 1, atol=1e-3):
        raise ValueError('Expected one finite unit wxyz quaternion')
    return Rotation.from_quat(q[[1, 2, 3, 0]])

def observation(ref_q, ref_dq, ref_anchor, robot_anchor, base_gyro, q, dq, default_q, default_dq, previous_action):
    """154 values; rotation uses matrix[:, :2].reshape(-1), matching Isaac."""
    relative = rotation(robot_anchor).inv() * rotation(ref_anchor)
    result = np.concatenate((ref_q, ref_dq, relative.as_matrix()[:, :2].reshape(-1),
                             base_gyro, q-default_q, dq-default_dq, previous_action)).astype(np.float32)
    if result.shape != (154,) or not np.isfinite(result).all():
        raise ValueError('Policy observation must have 154 finite values')
    return result

def validate_manifest(config):
    """Reject incompatible models before inference or any control operation."""
    if config.get('schema_version') != 1 or config.get('observation_terms') != [list(x) for x in OBSERVATIONS]:
        raise ValueError('Unsupported deploy schema or observation term order')
    names = config['joint_names']
    if len(names) != 29 or len(set(names)) != 29:
        raise ValueError('Manifest must contain 29 unique joint names')
    for key in ('default_joint_pos', 'default_joint_vel', 'action_scale', 'kp', 'kd', 'torque_limits'):
        a = np.asarray(config[key])
        if a.shape != (29,) or not np.isfinite(a).all():
            raise ValueError(f'Manifest {key} must contain 29 finite values')
    for key in ('kp', 'kd', 'torque_limits'):
        if np.any(np.asarray(config[key]) < 0) or (key == 'torque_limits' and min(config[key]) <= 0):
            raise ValueError(f'Invalid {key}')
    if not np.isfinite(config['control_dt']) or config['control_dt'] <= 0:
        raise ValueError('Invalid control_dt')
    clip = config.get('action_clip')
    if clip is not None and (not np.isfinite(clip) or clip <= 0):
        raise ValueError('action_clip must be null or finite and positive')
    return config

class TrackingPolicy:
    """One bundle binds policy.onnx, motion.npz, checksums and a named manifest."""
    def __init__(self, bundle):
        import onnxruntime as ort
        self.bundle = Path(bundle)
        self.config = validate_manifest(json.loads((self.bundle / 'manifest.json').read_text(encoding='utf-8')))
        for name in ('policy.onnx', 'motion.npz'):
            actual = hashlib.sha256((self.bundle / name).read_bytes()).hexdigest()
            if self.config['sha256'][name] != actual:
                raise ValueError(f'Bundle checksum mismatch: {name}')
        self.motion = load_motion(self.bundle / 'motion.npz')
        self.indices = name_indices(self.motion['joint_names'], self.config['joint_names'])
        self.anchor = list(self.motion['body_names']).index(self.config['anchor_body_name'])
        if not np.isclose(float(self.motion['fps']) * self.config['control_dt'], 1, atol=1e-6):
            raise ValueError('Motion fps does not match policy control_dt')
        self.session = ort.InferenceSession(str(self.bundle / 'policy.onnx'), providers=['CPUExecutionProvider'])
        ins, outs = self.session.get_inputs(), self.session.get_outputs()
        if len(ins) != 1 or len(outs) != 1 or ins[0].shape != [1, 154] or outs[0].shape != [1, 29]:
            raise ValueError('Expected stateless ONNX [1,154] -> [1,29]')
        self.input_name = ins[0].name
        self.reset()

    def reset(self):
        """Clear previous action; called once before starting frame zero."""
        self.previous_action = np.zeros(29, dtype=np.float32)

    def step(self, frame, q, dq, base_gyro, anchor_wxyz):
        """Consume one reference frame; refuse wraparound at the motion boundary."""
        if frame < 0 or frame >= len(self.motion['joint_pos']):
            raise IndexError('Reference motion finished; caller must stop control')
        c, m, j = self.config, self.motion, self.indices
        obs = observation(m['joint_pos'][frame, j], m['joint_vel'][frame, j],
                          m['body_quat_w'][frame, self.anchor], anchor_wxyz,
                          np.asarray(base_gyro), np.asarray(q), np.asarray(dq),
                          np.asarray(c['default_joint_pos']), np.asarray(c['default_joint_vel']), self.previous_action)
        action = self.session.run(None, {self.input_name: obs[None]})[0][0]
        if action.shape != (29,) or not np.isfinite(action).all():
            raise ValueError('Nonfinite or incorrectly shaped ONNX action')
        if c.get('action_clip') is not None:
            action = np.clip(action, -c['action_clip'], c['action_clip'])
        target = np.asarray(c['default_joint_pos']) + np.asarray(c['action_scale']) * action
        self.previous_action = action.copy()
        return target, obs
