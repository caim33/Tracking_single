"""Retarget every GVHMR frame to G1; headless CLI. See docs/02_video.md."""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gvhmr_pred_file', type=Path, required=True)
    parser.add_argument('--save_path', type=Path, required=True)
    parser.add_argument('--robot', choices=['unitree_g1'], default='unitree_g1')
    parser.add_argument('--body-models', type=Path, default=Path(__file__).resolve().parents[1]/'assets/body_models')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--rate_limit', action='store_true')
    args = parser.parse_args()
    if args.save_path.exists():
        raise FileExistsError(args.save_path)
    if not args.gvhmr_pred_file.is_file() or not args.body_models.is_dir():
        parser.error('Prediction file and licensed SMPL-X body-model directory must exist')
    import numpy as np
    import pickle
    from general_motion_retargeting import GeneralMotionRetargeting, RobotMotionViewer
    from general_motion_retargeting.utils.smpl import load_gvhmr_pred_file, get_gvhmr_data_offline_fast
    data, model, output, height = load_gvhmr_pred_file(args.gvhmr_pred_file, args.body_models)
    frames, fps = get_gvhmr_data_offline_fast(data, model, output, tgt_fps=30)
    if len(frames) < 2:
        raise ValueError('At least two human frames required')
    retarget = GeneralMotionRetargeting(src_human='smplx', tgt_robot=args.robot, actual_human_height=height)
    viewer = None if args.headless else RobotMotionViewer(robot_type=args.robot, motion_fps=fps)
    poses = []
    try:
        for human_frame in frames:
            qpos = retarget.retarget(human_frame).copy()
            if qpos.shape != (36,) or not np.isfinite(qpos).all():
                raise ValueError('IK returned invalid G1 pose')
            poses.append(qpos)
            if viewer is not None:
                viewer.step(root_pos=qpos[:3], root_rot=qpos[3:7], dof_pos=qpos[7:],
                            human_motion_data=retarget.scaled_human_data, rate_limit=args.rate_limit)
    finally:
        if viewer is not None:
            viewer.close()
    poses = np.asarray(poses)
    joints = [retarget.model.joint(i).name for i in range(1, retarget.model.njnt)]
    motion = dict(fps=float(fps), root_pos=poses[:, :3], root_rot=poses[:, [4,5,6,3]],
                  dof_pos=poses[:, 7:], joint_names=joints, local_body_pos=None, link_body_list=None)
    args.save_path.parent.mkdir(parents=True, exist_ok=True)
    with args.save_path.open('xb') as handle:
        pickle.dump(motion, handle)
    print(f'Saved {len(poses)} frames at {fps:g} Hz to {args.save_path}')

if __name__ == '__main__':
    main()
