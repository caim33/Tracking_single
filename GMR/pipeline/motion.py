"""Named, validated tracking archive shared by training and deployment.

Lengths are metres, angles radians, quaternions wxyz, velocities world-frame.
Use ``python -m GMR.pipeline.convert`` for GMR xyzw pickle conversion.
"""
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation, Slerp

ROOT = Path(__file__).resolve().parents[2]
ROBOT_DIR = ROOT / 'GMR/assets/unitree_g1'
ROBOT_XML = ROBOT_DIR / 'g1_mocap_29dof.xml'
ROBOT_URDF = ROBOT_DIR / 'g1_custom_collision_29dof.urdf'
ARRAY_DIMS = {'joint_pos': (29,), 'joint_vel': (29,), 'body_pos_w': (None, 3),
              'body_quat_w': (None, 4), 'body_lin_vel_w': (None, 3), 'body_ang_vel_w': (None, 3)}

def validate_motion(data):
    """Reject ambiguous names, corrupt quaternions, mismatched shapes and NaNs."""
    required = set(ARRAY_DIMS) | {'fps', 'joint_names', 'body_names', 'schema_version'}
    missing = required - data.keys()
    if missing:
        raise ValueError(f'Motion missing fields {sorted(missing)}; regenerate with GMR.pipeline.convert')
    if np.asarray(data['schema_version']).size != 1 or np.asarray(data['schema_version']).item() != 1:
        raise ValueError('Unsupported motion schema_version')
    fps_array = np.asarray(data['fps'])
    if fps_array.size != 1:
        raise ValueError('fps must be scalar')
    fps = float(fps_array.reshape(-1)[0])
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError('fps must be finite and positive')
    for key in ('joint_names', 'body_names'):
        names = np.asarray(data[key])
        if names.ndim != 1 or names.dtype.kind not in ('U', 'S'):
            raise ValueError(f'{key} must be a one-dimensional string array')
    joint_names = list(map(str, data['joint_names']))
    body_names = list(map(str, data['body_names']))
    if len(joint_names) != 29 or len(set(joint_names)) != 29:
        raise ValueError('Exactly 29 unique joint_names required')
    if not body_names or len(body_names) != len(set(body_names)):
        raise ValueError('body_names must be nonempty and unique')
    n = len(data['joint_pos'])
    if n < 2:
        raise ValueError('At least two motion frames required')
    for key, dims in ARRAY_DIMS.items():
        expected = (n,) + tuple(len(body_names) if d is None else d for d in dims)
        a = np.asarray(data[key])
        if a.shape != expected or not np.issubdtype(a.dtype, np.number) or not np.isfinite(a).all():
            raise ValueError(f'{key}: expected finite numeric {expected}, got {a.shape}')
    if not np.allclose(np.linalg.norm(data['body_quat_w'], axis=-1), 1, atol=1e-3):
        raise ValueError('body_quat_w must contain unit wxyz quaternions')
    return data

def load_motion(path):
    """Load a non-pickle NPZ, close its descriptor, then validate its contract."""
    with np.load(path, allow_pickle=False) as archive:
        data = {k: archive[k] for k in archive.files}
    return validate_motion(data)

def name_indices(actual, requested):
    """Map names explicitly; never assume MuJoCo and Isaac use the same order."""
    actual = list(map(str, actual))
    if len(actual) != len(set(actual)):
        raise ValueError('Duplicate names in source order')
    missing = set(requested) - set(actual)
    if missing:
        raise ValueError(f'Model/motion names missing: {sorted(missing)}')
    return np.asarray([actual.index(name) for name in requested], dtype=int)

def resample_qpos(root_pos, root_xyzw, joints, source_fps, target_fps):
    """Resample on a seconds-based grid without extending beyond the last frame."""
    root_pos, root_xyzw, joints = map(np.asarray, (root_pos, root_xyzw, joints))
    n = len(joints)
    if n < 2 or joints.shape != (n, 29) or root_pos.shape != (n, 3) or root_xyzw.shape != (n, 4):
        raise ValueError('Expected at least 2 frames: root_pos [N,3], root_rot [N,4], dof_pos [N,29]')
    if not all(np.isfinite(a).all() for a in (root_pos, root_xyzw, joints)):
        raise ValueError('GMR input contains nonfinite values')
    if not np.allclose(np.linalg.norm(root_xyzw, axis=1), 1, atol=1e-3):
        raise ValueError('GMR root_rot must be unit xyzw quaternions')
    if not np.isfinite([source_fps, target_fps]).all() or min(source_fps, target_fps) <= 0:
        raise ValueError('Source and target fps must be finite and positive')
    old = np.arange(n) / source_fps
    new = np.arange(int(np.floor(old[-1] * target_fps + 1e-9)) + 1) / target_fps
    if len(new) < 2:
        raise ValueError('Motion is too short for requested target fps')
    linear = np.concatenate((root_pos, joints), axis=1)
    out = np.stack([np.interp(new, old, linear[:, j]) for j in range(32)], axis=1)
    quat = Slerp(old, Rotation.from_quat(root_xyzw))(np.minimum(new, old[-1])).as_quat()
    return np.concatenate((out[:, :3], quat[:, [3, 0, 1, 2]], out[:, 3:]), axis=1)

def world_angular_velocity(quaternions, fps):
    """Differentiate wxyz rotations in the world frame, with sign-invariant SO(3) differences."""
    n, bodies, _ = quaternions.shape
    out = np.empty((n, bodies, 3))
    for b in range(bodies):
        r = Rotation.from_quat(quaternions[:, b, [1, 2, 3, 0]])
        out[0, b] = (r[1] * r[0].inv()).as_rotvec() * fps
        out[-1, b] = (r[-1] * r[-2].inv()).as_rotvec() * fps
        if n > 2:
            out[1:-1, b] = (r[2:] * r[:-2].inv()).as_rotvec() * fps / 2
    return out

def qpos_to_motion(qpos, fps, model):
    """Evaluate every named link using MuJoCo FK; preserve explicit joint order."""
    import mujoco
    qpos = np.asarray(qpos)
    if qpos.ndim != 2 or qpos.shape[1] != 36 or len(qpos) < 2 or not np.isfinite(qpos).all():
        raise ValueError('Expected finite qpos [N>=2,36]')
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError('fps must be finite and positive')
    if not np.allclose(np.linalg.norm(qpos[:,3:7],axis=-1),1,atol=1e-3):
        raise ValueError('qpos root rotations must be unit wxyz quaternions')
    if model.nq != 36 or model.nv != 35:
        raise ValueError('Expected a floating-base 29-DoF G1 model')
    state = mujoco.MjData(model)
    bodies = [i for i in range(1, model.nbody) if model.body(i).name]
    joints = [i for i in range(model.njnt) if model.jnt_type[i] == mujoco.mjtJoint.mjJNT_HINGE]
    if len(joints) != 29:
        raise ValueError('Expected 29 hinge joints')
    pos, quat, com = [], [], []
    for frame in qpos:
        state.qpos[:] = frame
        mujoco.mj_forward(model, state)
        pos.append(state.xpos[bodies].copy())
        quat.append(state.xquat[bodies].copy())
        com.append(state.xipos[bodies].copy())
    pos, quat = np.asarray(pos), np.asarray(quat)
    joint_pos = qpos[:, model.jnt_qposadr[joints]]
    result = dict(schema_version=np.asarray(1), fps=np.asarray(float(fps)),
                  joint_names=np.asarray([model.joint(i).name for i in joints]),
                  body_names=np.asarray([model.body(i).name for i in bodies]),
                  joint_pos=joint_pos.astype(np.float32),
                  joint_vel=np.gradient(joint_pos, 1/fps, axis=0).astype(np.float32),
                  body_pos_w=pos.astype(np.float32), body_quat_w=quat.astype(np.float32),
                  # Isaac Lab body_lin_vel_w aliases body_com_lin_vel_w.
                  body_lin_vel_w=np.gradient(np.asarray(com), 1/fps, axis=0).astype(np.float32),
                  body_ang_vel_w=world_angular_velocity(quat, fps).astype(np.float32))
    return validate_motion(result)
