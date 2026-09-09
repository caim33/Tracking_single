"""CPU ONNX/FK/transport contract tests; no robot or learned checkpoint needed."""
import json
import subprocess
import sys
import numpy as np
import pytest
from scipy.spatial.transform import Rotation
from Deploy.runtime import TrackingPolicy, observation
from Deploy.robot_state import RobotState, MOTOR_NAMES

def test_observation_layout_and_orientation():
    zero=np.zeros(29)
    ref=Rotation.from_euler('z',90,degrees=True).as_quat()[[3,0,1,2]]
    obs=observation(zero+1,zero+2,ref,np.array([1,0,0,0]),[3,4,5],zero+6,zero+7,zero,zero,zero+8)
    assert obs.shape==(154,)
    np.testing.assert_equal(obs[:29],1); np.testing.assert_equal(obs[29:58],2)
    np.testing.assert_allclose(obs[58:64],[0,-1,1,0,0,0],atol=1e-6)
    np.testing.assert_equal(obs[64:67],[3,4,5])
    np.testing.assert_equal(obs[67:96],6); np.testing.assert_equal(obs[96:125],7)
    np.testing.assert_equal(obs[125:],8)

def test_bundle_inference_and_motion_end(bundle):
    policy=TrackingPolicy(bundle)
    q=np.zeros(29)
    target,obs=policy.step(0,q,q,np.zeros(3),np.array([1,0,0,0]))
    np.testing.assert_equal(target,0)
    assert obs.shape==(154,)
    with pytest.raises(IndexError): policy.step(31,q,q,np.zeros(3),[1,0,0,0])

def test_bundle_checksum_detects_swapped_motion(bundle):
    with (bundle/'motion.npz').open('ab') as f: f.write(b'changed')
    with pytest.raises(ValueError,match='checksum'): TrackingPolicy(bundle)

def test_bad_observation_order_rejected(bundle):
    p=bundle/'manifest.json'; cfg=json.loads(p.read_text())
    cfg['observation_terms'].reverse(); p.write_text(json.dumps(cfg))
    with pytest.raises(ValueError,match='observation'): TrackingPolicy(bundle)

def test_cpu_dynamic_smoke_with_synthetic_zero_policy(bundle,tmp_path):
    trace=tmp_path/'trace.npz'
    result=subprocess.run([sys.executable,'-m','Deploy.sim2sim','--bundle',str(bundle),
                           '--headless','--steps','5','--output',str(trace)],capture_output=True,text=True)
    assert result.returncode==0, result.stdout+result.stderr
    with np.load(trace) as a:
        assert a['observation'].shape==(5,154)
        assert np.isfinite(a['joint_pos']).all()

def test_pelvis_and_torso_imu_equivalence():
    estimator=RobotState(MOTOR_NAMES)
    q=np.zeros(29); q[12:15]=[0.2,0.1,-0.1]
    gyro=np.array([0.1,0.2,0.3]); dq=np.zeros(29)
    base=Rotation.from_euler('xyz',[0.1,0.2,0.3])
    bq=base.as_quat()[[3,0,1,2]]
    g1,a1,_=estimator.estimate(q,dq,bq,gyro,'pelvis')
    relative=Rotation.from_quat(estimator.data.xquat[estimator.torso][[1,2,3,0]])
    torso=base*relative
    g2,a2,_=estimator.estimate(q,dq,torso.as_quat()[[3,0,1,2]],relative.inv().apply(gyro),'torso')
    np.testing.assert_allclose(g1,g2,atol=1e-6)
    np.testing.assert_allclose(a1,a2,atol=1e-6)
