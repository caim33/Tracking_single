"""Regression coverage for timing, quaternions, names and real robot assets."""
import numpy as np
import pytest
from scipy.spatial.transform import Rotation
from pipeline.motion import resample_qpos, validate_motion, name_indices, world_angular_velocity, qpos_to_motion

def test_resampling_preserves_first_frame_duration_and_rotation():
    n=31
    position=np.zeros((n,3)); position[:,0]=np.arange(n)/30
    quat=Rotation.from_euler('z',np.linspace(0,np.pi/2,n)).as_quat()
    out=resample_qpos(position,quat,np.zeros((n,29)),30,50)
    assert out.shape==(51,36)
    np.testing.assert_allclose(out[:,0],np.arange(51)/50)
    np.testing.assert_allclose(out[0,3:7],[1,0,0,0])
    np.testing.assert_allclose(out[-1,3:7],np.array([1,0,0,1])/np.sqrt(2),atol=1e-7)

@pytest.mark.parametrize('fps',[0,-1,float('nan'),float('inf')])
def test_bad_fps_rejected(motion,fps):
    motion['fps']=fps
    with pytest.raises(ValueError): validate_motion(motion)

def test_duplicate_names_and_nan_rejected(motion):
    motion['joint_names'][1]=motion['joint_names'][0]
    with pytest.raises(ValueError): validate_motion(motion)

def test_order_mapping():
    np.testing.assert_equal(name_indices(['b','a','c'],['c','b']),[2,0])
    with pytest.raises(ValueError): name_indices(['a'],['b'])

def test_angular_velocity_is_world_frame_and_sign_invariant():
    angles=np.arange(10)*0.02
    q=Rotation.from_euler('z',angles).as_quat()[:,[3,0,1,2]][:,None,:]
    q[::2]*=-1
    out=world_angular_velocity(q,50)
    np.testing.assert_allclose(out[:,:,2],1,atol=1e-6)
    np.testing.assert_allclose(out[:,:,:2],0,atol=1e-6)

def test_real_g1_archive_has_named_29_dof_and_unit_quaternions(motion):
    assert len(motion['joint_names'])==29
    assert 'torso_link' in motion['body_names']
    np.testing.assert_allclose(np.linalg.norm(motion['body_quat_w'],axis=-1),1,atol=1e-6)
    np.testing.assert_allclose(motion['body_ang_vel_w'],0,atol=1e-6)

def test_linear_velocity_tracks_com_when_link_origin_is_stationary(model):
    qpos=np.tile(model.qpos0,(21,1))
    qpos[:,3:7]=Rotation.from_euler('y',np.arange(21)*0.01).as_quat()[:,[3,0,1,2]]
    data=qpos_to_motion(qpos,100,model)
    pelvis=list(data['body_names']).index('pelvis')
    np.testing.assert_allclose(data['body_pos_w'][:,pelvis],np.tile(qpos[0,:3],(21,1)),atol=1e-6)
    assert np.linalg.norm(data['body_lin_vel_w'][10,pelvis]) > 0.05

def test_urdf_joint_names_and_meshes_are_complete(model):
    import xml.etree.ElementTree as ET
    from pipeline.motion import ROBOT_URDF
    tree=ET.parse(ROBOT_URDF)
    names=[joint.attrib['name'] for joint in tree.findall('joint') if joint.attrib['type']=='revolute']
    assert set(names)=={model.joint(i).name for i in range(1,model.njnt)}
    for mesh in tree.findall('.//mesh'):
        assert (ROBOT_URDF.parent/mesh.attrib['filename']).is_file()
