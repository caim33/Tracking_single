"""Exercise actual CLI serialization and the original dropped-frame regression."""
from pathlib import Path
import pickle
import subprocess
import sys
import types
import numpy as np
import pytest
from GMR.pipeline.motion import load_motion

def test_convert_cli_from_gmr_to_named_archive(tmp_path,model):
    raw=dict(root_pos=np.tile([0,0,0.8],(31,1)),root_rot=np.tile([0,0,0,1],(31,1)),dof_pos=np.zeros((31,29)),fps=30)
    input_path=tmp_path/'gmr.pkl';output=tmp_path/'motion.npz'
    input_path.write_bytes(pickle.dumps(raw))
    command=[sys.executable,'-m','GMR.pipeline.convert','--input',str(input_path),'--output',str(output)]
    result=subprocess.run(command,capture_output=True,text=True,cwd=tmp_path)
    assert result.returncode==0,result.stderr
    motion=load_motion(output)
    assert len(motion['joint_pos'])==51 and motion['fps']==50
    assert subprocess.run(command,capture_output=True,cwd=tmp_path).returncode!=0

@pytest.mark.parametrize('frame_count',[2,31])
def test_gmr_export_includes_frame_zero_and_exact_count(monkeypatch,tmp_path,model,frame_count):
    import importlib.util
    path=Path(__file__).resolve().parents[2]/'GMR/scripts/gvhmr_to_robot.py'
    spec=importlib.util.spec_from_file_location('gvhmr_export_regression',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    source=tmp_path/'result.pt';source.touch()
    dest=tmp_path/'result.pkl'
    class FakeRetarget:
        def __init__(self,**kwargs): self.model=model
        def retarget(self,frame):
            pose=model.qpos0.copy();pose[0]=frame;return pose
    package=types.ModuleType('general_motion_retargeting')
    package.GeneralMotionRetargeting=FakeRetarget
    package.RobotMotionViewer=lambda **kw: pytest.fail('headless must not create a viewer')
    smpl=types.ModuleType('general_motion_retargeting.utils.smpl')
    smpl.load_gvhmr_pred_file=lambda *args: (None,None,None,1.7)
    smpl.get_gvhmr_data_offline_fast=lambda *args,**kwargs: (list(range(frame_count)),30)
    monkeypatch.setitem(sys.modules,'general_motion_retargeting',package)
    monkeypatch.setitem(sys.modules,'general_motion_retargeting.utils.smpl',smpl)
    monkeypatch.setattr(sys,'argv',[str(path),'--gvhmr_pred_file',str(source),'--save_path',str(dest),'--body-models',str(tmp_path),'--headless'])
    module.main()
    data=pickle.loads(dest.read_bytes())
    np.testing.assert_equal(data['root_pos'][:,0],np.arange(frame_count))
    assert len(data['joint_names'])==29
