"""Convert trusted GMR pickle to a named 50 Hz training archive; see docs/03_motion.md."""
import argparse
from pathlib import Path
from .motion import ROBOT_XML, resample_qpos, qpos_to_motion

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='Trusted local GMR .pkl (pickle executes code)')
    parser.add_argument('--output', required=True, type=Path, help='Output .npz archive')
    parser.add_argument('--fps', type=float, default=50, help='Must equal tracking control rate (default 50 Hz)')
    parser.add_argument('--robot-xml', type=Path, default=ROBOT_XML)
    args = parser.parse_args()
    if args.output.suffix != '.npz':
        parser.error('--output must end in .npz')
    if args.output.exists():
        raise FileExistsError(args.output)
    import pickle
    import numpy as np
    import mujoco
    with args.input.open('rb') as handle:
        data = pickle.load(handle)
    qpos = resample_qpos(data['root_pos'], data['root_rot'], data['dof_pos'], float(data['fps']), args.fps)
    model = mujoco.MjModel.from_xml_path(str(args.robot_xml.resolve()))
    motion = qpos_to_motion(qpos, args.fps, model)
    if 'joint_names' in data and list(data['joint_names']) != list(motion['joint_names']):
        raise ValueError('GMR joint_names differ from selected XML order')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **motion)
    print(f"Saved {args.output}: {len(qpos)} frames at {args.fps:g} Hz, duration {(len(qpos)-1)/args.fps:.3f}s")

if __name__ == '__main__':
    main()
