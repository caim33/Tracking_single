"""Synthetic infrastructure fixtures, never represented as a trained policy."""
import hashlib
import json
import numpy as np
import pytest
from pipeline.motion import ROBOT_XML, qpos_to_motion
from Deploy.runtime import OBSERVATIONS

@pytest.fixture(scope='session')
def model():
    import mujoco
    return mujoco.MjModel.from_xml_path(str(ROBOT_XML))

@pytest.fixture
def motion(model):
    qpos = np.tile(model.qpos0, (31,1))
    return qpos_to_motion(qpos, 50, model)

@pytest.fixture
def bundle(tmp_path, motion):
    import onnx
    from onnx import helper, TensorProto
    p = tmp_path/'bundle'
    p.mkdir()
    np.savez_compressed(p/'motion.npz', **motion)
    graph = helper.make_graph([
        helper.make_node('MatMul',['obs','weight'],['actions'])], 'test-only-zero-policy',
        [helper.make_tensor_value_info('obs',TensorProto.FLOAT,[1,154])],
        [helper.make_tensor_value_info('actions',TensorProto.FLOAT,[1,29])],
        [helper.make_tensor('weight',TensorProto.FLOAT,[154,29],np.zeros(154*29,dtype=np.float32))])
    network=helper.make_model(graph,opset_imports=[helper.make_opsetid('',17)])
    network.ir_version=8
    onnx.save(network,p/'policy.onnx')
    cfg=dict(schema_version=1,task='test-fixture',joint_names=list(motion['joint_names']),
             anchor_body_name='torso_link',control_dt=0.02,observation_terms=[list(x) for x in OBSERVATIONS],
             default_joint_pos=[0.]*29,default_joint_vel=[0.]*29,action_scale=[0.1]*29,
             action_clip=None,kp=[50.]*29,kd=[2.]*29,torque_limits=[30.]*29)
    cfg['sha256']={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in ('motion.npz','policy.onnx')}
    (p/'manifest.json').write_text(json.dumps(cfg))
    return p
