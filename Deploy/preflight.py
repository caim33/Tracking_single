"""Check training/deployment prerequisites without starting Isaac or robot transport.

Run from the repository root: python -m Deploy.preflight --stage train --motion data/motion.npz
See Deploy/docs/07_validation.md. Passing does not establish tracking quality.
"""
import argparse
import ast
import importlib.metadata
import importlib.util
from pathlib import Path
import re
import socket
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / 'RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_demo'


def dependency(distribution, module, minimum=None, series=None, exact=None):
    """Check installed metadata and module discovery without importing simulator modules."""
    version = importlib.metadata.version(distribution)
    if importlib.util.find_spec(module) is None:
        raise ValueError(f'{module} cannot be imported; reinstall {distribution}')
    numbers = tuple(map(int, re.match(r'\d+(?:\.\d+)*', version)[0].split('.')))
    if minimum is not None and numbers < minimum:
        raise ValueError(f'{distribution} {version}; requires >= {minimum}')
    if series is not None and numbers[:len(series)] != series:
        raise ValueError(f'{distribution} {version}; requires series {series}')
    if exact is not None and version != exact:
        raise ValueError(f'{distribution} {version}; requires {exact}')
    return f'{distribution} {version}'


def available_module(module):
    """Support simulator modules provided by the Isaac launcher as well as pip installs."""
    if importlib.util.find_spec(module) is None:
        raise ImportError(f'{module} is unavailable in this Python; use the configured Isaac launcher')
    return f'{module} available'


def robot_assets():
    """Check XML/URDF joint declarations and every referenced mesh path."""
    directory = ROOT / 'GMR/assets/unitree_g1'
    ROBOT_XML = directory / 'g1_mocap_29dof.xml'
    ROBOT_URDF = directory / 'g1_custom_collision_29dof.urdf'
    xml = ET.parse(ROBOT_XML).getroot()
    urdf = ET.parse(ROBOT_URDF).getroot()
    missing = [mesh.get('filename') for mesh in urdf.findall('.//mesh')
               if not (ROBOT_URDF.parent / mesh.get('filename')).is_file()]
    compiler = xml.find('compiler')
    mesh_dir = ROBOT_XML.parent / (compiler.get('meshdir', '.') if compiler is not None else '.')
    missing += [mesh.get('file') for mesh in xml.findall('./asset/mesh')
                if not (mesh_dir / mesh.get('file')).is_file()]
    if missing:
        raise FileNotFoundError(f'Robot meshes missing: {missing}')
    actual = {joint.get('name') for joint in xml.findall('.//worldbody//joint') if joint.get('type', 'hinge') == 'hinge'}
    described = {joint.get('name') for joint in urdf.findall('joint') if joint.get('type') != 'fixed'}
    if actual != described or len(actual) != 29:
        raise ValueError('URDF and MuJoCo joint names differ')
    return 'G1 XML, URDF, 29 joints and referenced meshes available'


def training_motion(path):
    """Validate a real reference against the retained training task and robot model."""
    import mujoco
    import numpy as np
    from GMR.pipeline.motion import ROBOT_XML, load_motion, name_indices
    if path is None:
        raise ValueError('Provide --motion with your converted reference .npz')
    data = load_motion(path)
    if not np.isclose(float(data['fps']), 50):
        raise ValueError('The retained task requires 50 Hz reference motion')
    model = mujoco.MjModel.from_xml_path(str(ROBOT_XML))
    name_indices(data['joint_names'], [model.joint(i).name for i in range(model.njnt)
                                     if model.jnt_type[i] == mujoco.mjtJoint.mjJNT_HINGE])
    tree = ast.parse((TASK_DIR / 'tracking_env_cfg.py').read_text(encoding='utf-8'))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and node.func.attr == 'MotionCommandCfg']
    if len(calls) != 1:
        raise ValueError('Expected one MotionCommandCfg in the retained task')
    bodies = next(ast.literal_eval(kw.value) for kw in calls[0].keywords if kw.arg == 'body_names')
    name_indices(data['body_names'], bodies)
    return f'{len(data["joint_pos"])} frames at 50 Hz; task joints and bodies match'


def deploy_bundle(path):
    """Validate policy/motion/checksums and their mapping to the actual robot."""
    from Deploy.runtime import TrackingPolicy
    from Deploy.robot_state import RobotState
    if path is None:
        raise ValueError('Provide --bundle exported by RL_envs/scripts/tracking.py export')
    policy = TrackingPolicy(path)
    RobotState(policy.config['joint_names'], policy.config['anchor_body_name'])
    motion = policy.motion
    policy.step(0, motion['joint_pos'][0, policy.indices], motion['joint_vel'][0, policy.indices],
                [0., 0., 0.], motion['body_quat_w'][0, policy.anchor])
    return f'Policy [1,154] -> [1,29], first inference, manifest, checksums and {len(motion["joint_pos"])} reference frames'


def check_setup(stage, motion=None, bundle=None, interface=None):
    """Collect every prerequisite failure; never create a robot command publisher."""
    results = []

    def check(name, function):
        try:
            results.append((name, True, str(function())))
        except Exception as exc:
            results.append((name, False, f'{type(exc).__name__}: {exc}'))

    for distribution, module in [('tracking-single-pipeline', 'GMR'), ('numpy', 'numpy'),
                                  ('scipy', 'scipy'), ('mujoco', 'mujoco')]:
        check(module, lambda d=distribution, m=module: dependency(d, m))
    check('robot assets', robot_assets)
    if stage == 'train':
        check('Isaac Sim', lambda: available_module('isaacsim'))
        for distribution, module, limits in [
            ('isaaclab', 'isaaclab', {'series': (2, 3)}),
            ('isaaclab_rl', 'isaaclab_rl', {}), ('isaaclab_tasks', 'isaaclab_tasks', {}),
            ('WBC-tracking-single', 'WBC', {}), ('torch', 'torch', {'minimum': (2, 7)}),
            ('gymnasium', 'gymnasium', {}), ('tensordict', 'tensordict', {}), ('tensorboard', 'tensorboard', {}),
            ('rsl-rl-lib', 'rsl_rl', {'exact': '3.0.1'}), ('numpy', 'numpy', {'series': (1,)}),
            ('onnx', 'onnx', {}), ('onnxruntime', 'onnxruntime', {}),
            ('onnxscript', 'onnxscript', {'minimum': (0, 5)}),
        ]:
            check(distribution, lambda d=distribution, m=module, limits=limits: dependency(d, m, **limits))

        def cuda():
            import torch
            if not torch.cuda.is_available():
                raise RuntimeError('CUDA unavailable; use the prepared Isaac/NVIDIA environment')
            return torch.cuda.get_device_name(0)

        check('CUDA', cuda)
        check('reference motion', lambda: training_motion(motion))
    else:
        check('onnxruntime', lambda: dependency('onnxruntime', 'onnxruntime'))
        check('deployment bundle', lambda: deploy_bundle(bundle))
        if stage == 'sim2real':
            def transport():
                if not sys.platform.startswith('linux'):
                    raise RuntimeError('SDK2 recurrent transport requires Linux timerfd')
                # Import resolves CycloneDDS/native libraries, without initializing DDS.
                from unitree_sdk2py.core.channel import ChannelFactoryInitialize
                from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
                from unitree_sdk2py.utils.thread import RecurrentThread
                from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
                from unitree_sdk2py.utils.crc import CRC
                from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
                if interface not in {name for _, name in socket.if_nameindex()}:
                    raise ValueError('Provide --interface naming an existing robot Ethernet interface')
                return 'SDK2 G1 messages, CycloneDDS, timerfd and local interface available; no robot connection made'
            check('SDK2 transport', transport)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', required=True, choices=['train', 'sim2sim', 'sim2real'])
    parser.add_argument('--motion', type=Path)
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--interface')
    args = parser.parse_args()
    results = check_setup(args.stage, args.motion, args.bundle, args.interface)
    for name, ok, detail in results:
        print(f'{"PASS" if ok else "FAIL"} {name}: {detail}')
    print('Prerequisite checks only; simulator startup, learned tracking and hardware execution need separate validation.')
    raise SystemExit(0 if all(ok for _, ok, _ in results) else 1)


if __name__ == '__main__':
    main()
