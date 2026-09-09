"""Preview one GMR motion and close the viewer/recorder cleanly. See docs/02_video.md."""
import argparse
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--robot', choices=['unitree_g1'], default='unitree_g1')
    parser.add_argument('--robot_motion_path', type=Path, required=True)
    parser.add_argument('--record_video', action='store_true')
    parser.add_argument('--video_path', type=Path, default=Path('videos/example.mp4'))
    parser.add_argument('--loop', action='store_true', help='Repeat until Ctrl+C; default is one pass')
    args=parser.parse_args()
    if not args.robot_motion_path.is_file():
        raise FileNotFoundError(args.robot_motion_path)
    from general_motion_retargeting import RobotMotionViewer, load_robot_motion
    _,fps,pos,rot,joints,_,_=load_robot_motion(args.robot_motion_path)
    if len(pos)==0:
        raise ValueError('Motion contains no frames')
    if args.record_video:
        if args.video_path.exists(): raise FileExistsError(args.video_path)
        args.video_path.parent.mkdir(parents=True,exist_ok=True)
    viewer=RobotMotionViewer(robot_type=args.robot,motion_fps=fps,camera_follow=False,
                              record_video=args.record_video,video_path=str(args.video_path))
    try:
        while True:
            for index in range(len(pos)):
                viewer.step(pos[index],rot[index],joints[index],rate_limit=True)
            if not args.loop: break
    except KeyboardInterrupt:
        pass
    finally:
        viewer.close()

if __name__=='__main__':
    main()
