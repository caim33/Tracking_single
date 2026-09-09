"""Run a single reference policy in MuJoCo, with CPU ONNX inference.

python -m Deploy.sim2sim --bundle bundles/dance --headless --steps 100
See docs/05_deploy.md. A mechanics smoke test does not establish policy quality.
"""
import argparse
import contextlib
from pathlib import Path
import time
import xml.etree.ElementTree as ET
import numpy as np
from pipeline.motion import ROBOT_XML, name_indices
from .runtime import TrackingPolicy, rotation

def simulation_model(xml_path, dt=0.005):
    """Keep the migrated GMR model and add ground/light for dynamic playback."""
    import mujoco
    xml_path = Path(xml_path).resolve()
    tree = ET.parse(xml_path)
    root = tree.getroot()
    compiler = root.find('compiler')
    compiler.set('meshdir', str(xml_path.parent / compiler.get('meshdir', '.')))
    option = root.find('option')
    if option is None:
        option = ET.SubElement(root, 'option')
    option.set('timestep', str(dt))
    world = root.find('worldbody')
    ET.SubElement(world, 'geom', name='tracking_ground', type='plane', size='0 0 0.1', friction='1 0.005 0.0001', rgba='0.25 0.28 0.32 1')
    ET.SubElement(world, 'light', pos='0 0 3', dir='0 0 -1')
    return mujoco.MjModel.from_xml_string(ET.tostring(root, encoding='unicode'))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--robot-xml', type=Path, default=ROBOT_XML)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--steps', type=int, help='Optional upper bound; defaults to full reference')
    parser.add_argument('--output', type=Path, help='Optional .npz trace: observations, q, targets, root height')
    args = parser.parse_args()
    if args.steps is not None and args.steps <= 0:
        parser.error('--steps must be positive')
    import mujoco
    policy = TrackingPolicy(args.bundle)
    model = simulation_model(args.robot_xml)
    state = mujoco.MjData(model)
    joint_ids = np.asarray([model.joint(n).id for n in policy.config['joint_names']])
    qa, va = model.jnt_qposadr[joint_ids], model.jnt_dofadr[joint_ids]
    anchor_id = model.body(policy.config['anchor_body_name']).id
    pelvis = list(policy.motion['body_names']).index('pelvis')
    state.qpos[:3] = policy.motion['body_pos_w'][0, pelvis]
    state.qpos[3:7] = policy.motion['body_quat_w'][0, pelvis]
    state.qpos[qa] = policy.motion['joint_pos'][0, policy.indices]
    state.qvel[va] = policy.motion['joint_vel'][0, policy.indices]
    omega = policy.motion['body_ang_vel_w'][0, pelvis]
    pelvis_id = model.body('pelvis').id
    com_offset_w = rotation(state.qpos[3:7]).apply(model.body_ipos[pelvis_id])
    state.qvel[:3] = policy.motion['body_lin_vel_w'][0, pelvis] - np.cross(omega, com_offset_w)
    state.qvel[3:6] = rotation(state.qpos[3:7]).inv().apply(policy.motion['body_ang_vel_w'][0, pelvis])
    mujoco.mj_forward(model, state)
    # External generalized forces apply the same PD targets without assuming an
    # actuator order or changing the source model's motor gearing.
    if model.nu:
        state.ctrl[:] = 0
    dt = policy.config['control_dt']
    substeps = round(dt / model.opt.timestep)
    if substeps < 1 or not np.isclose(substeps * model.opt.timestep, dt):
        raise ValueError('Policy period must be an integer multiple of simulation dt')
    count = len(policy.motion['joint_pos'])
    if args.steps is not None:
        count = min(count, args.steps)
    trace = {k: [] for k in ('observation', 'joint_pos', 'target', 'root_height')}
    if args.headless:
        viewer = contextlib.nullcontext(None)
    else:
        import mujoco.viewer
        viewer = mujoco.viewer.launch_passive(model, state)
    with viewer as display:
        for frame in range(count):
            start = time.monotonic()
            if display is not None and not display.is_running():
                break
            if not np.isfinite(state.qpos).all() or state.qpos[2] < 0.25:
                raise RuntimeError(f'Unstable simulation or fall at frame {frame}')
            target, obs = policy.step(frame, state.qpos[qa], state.qvel[va], state.qvel[3:6], state.xquat[anchor_id])
            trace['observation'].append(obs)
            trace['joint_pos'].append(state.qpos[qa].copy())
            trace['target'].append(target)
            trace['root_height'].append(state.qpos[2])
            for _ in range(substeps):
                torque = np.asarray(policy.config['kp']) * (target-state.qpos[qa]) - np.asarray(policy.config['kd']) * state.qvel[va]
                torque = np.clip(torque, -np.asarray(policy.config['torque_limits']), policy.config['torque_limits'])
                state.qfrc_applied[:] = 0
                state.qfrc_applied[va] = torque
                mujoco.mj_step(model, state)
            if display is not None:
                display.sync()
                time.sleep(max(0, dt - (time.monotonic()-start)))
    if args.output:
        if args.output.suffix != '.npz' or args.output.exists():
            raise ValueError('--output must be a new .npz path')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.output, **{k: np.asarray(v) for k, v in trace.items()})
    print(f"Completed {len(trace['target'])} policy steps; reference does not wrap")

if __name__ == '__main__':
    main()
