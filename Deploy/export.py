"""Export policy/reference/control parameters together. See RL_envs/docs/04_training.md."""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from .runtime import OBSERVATIONS, validate_manifest

def export_actor_onnx(policy, path):
    """Export the actor and its normalizer on CPU without importing the simulator."""
    import copy
    import torch
    if policy.is_recurrent:
        raise ValueError('Only a stateless MLP actor can be exported')
    actor = torch.nn.Sequential(copy.deepcopy(policy.actor_obs_normalizer),
                                copy.deepcopy(policy.actor)).cpu().eval()
    # Explicitly use the stable TorchScript exporter, including on newer Torch
    # versions whose default exporter uses dynamo and additional dependencies.
    torch.onnx.export(actor, torch.zeros(1, 154), str(path), export_params=True,
                      opset_version=18, input_names=['obs'], output_names=['actions'],
                      dynamic_axes={}, dynamo=False)

def export_bundle(env, runner, motion_path, output, task, action_clip):
    """Derive mapping, offsets, gains and scaling from the running training task."""
    output = Path(output)
    robot = env.scene['robot']
    action = env.action_manager.get_term('joint_pos')
    actual_terms = list(env.observation_manager.active_terms['policy'])
    if actual_terms != [name for name, _ in OBSERVATIONS]:
        raise ValueError(f'Unsupported actor observation order: {actual_terms}')
    if runner.alg.policy.is_recurrent:
        raise ValueError('Only the migrated stateless MLP actor is supported')
    def array(value):
        if hasattr(value, 'detach'):
            value = value.detach().cpu().numpy()
        a = np.asarray(value)
        if a.ndim == 2:
            a = a[0]
        if a.ndim == 0:
            a = np.repeat(a, 29)
        return a.tolist()
    config = dict(schema_version=1, task=task, joint_names=list(robot.joint_names),
                  anchor_body_name=env.cfg.commands.motion.anchor_body_name,
                  control_dt=float(env.step_dt), observation_terms=[list(x) for x in OBSERVATIONS],
                  default_joint_pos=array(robot.data.default_joint_pos),
                  default_joint_vel=array(robot.data.default_joint_vel),
                  action_scale=array(action._scale), action_clip=action_clip,
                  kp=array(robot.data.joint_stiffness), kd=array(robot.data.joint_damping),
                  torque_limits=array(robot.data.joint_effort_limits))
    if not np.allclose(array(action._offset), config['default_joint_pos']):
        raise ValueError('Action offset differs from the default position observation convention')
    validate_manifest(config)
    output.mkdir(parents=True, exist_ok=False)
    export_actor_onnx(runner.alg.policy, output/'policy.onnx')
    shutil.copyfile(motion_path, output/'motion.npz')
    config['sha256'] = {name: hashlib.sha256((output/name).read_bytes()).hexdigest() for name in ('policy.onnx','motion.npz')}
    (output/'manifest.json').write_text(json.dumps(config, indent=2)+'\n',encoding='utf-8')
    from .runtime import TrackingPolicy
    TrackingPolicy(output)
    print(f'Exported validated bundle: {output}')
