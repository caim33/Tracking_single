"""Train, play or export a single reference. See RL_envs/docs/04_training.md.
Requires Isaac Lab 2.3.x and RSL-RL 3.0.1. Help does not start Isaac.
"""
import argparse
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['train', 'play', 'export'])
    parser.add_argument('--motion', required=True, type=Path)
    parser.add_argument('--task', default='G1-Tracking-Dance-demo')
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--num-envs', type=int, default=4096)
    parser.add_argument('--iterations', type=int, default=5000)
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=42)
    if '-h' in sys.argv or '--help' in sys.argv:
        parser.print_help()
        print('Also accepts AppLauncher options: --headless --device cuda:0 --enable_cameras')
        return
    from isaaclab.app import AppLauncher
    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args()
    if args.mode in ('play', 'export') and (args.checkpoint is None or not args.checkpoint.is_file()):
        parser.error('play/export require an existing --checkpoint')
    if min(args.num_envs, args.iterations, args.steps) <= 0:
        parser.error('num-envs, iterations and steps must be positive')
    if args.mode == 'export' and args.output is None:
        parser.error('export requires --output')
    if args.output is not None and args.output.exists():
        parser.error('--output must be a new directory')
    from GMR.pipeline.motion import load_motion
    motion = load_motion(args.motion)
    app = AppLauncher(args).app
    env = None
    try:
        import importlib.metadata
        if importlib.metadata.version('rsl-rl-lib') != '3.0.1':
            raise RuntimeError('This entry point requires rsl-rl-lib==3.0.1')
        import gymnasium as gym
        import numpy as np
        import torch
        import WBC.tasks
        from isaaclab_tasks.utils import parse_env_cfg, load_cfg_from_registry
        from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
        from rsl_rl.runners import OnPolicyRunner
        from datetime import datetime
        cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs if args.mode=='train' else 1)
        cfg.commands.motion.motion_file = str(args.motion.resolve())
        cfg.commands.motion.debug_vis = args.mode == 'play'
        cfg.seed = args.seed
        if not np.isclose(float(motion['fps']) * cfg.decimation * cfg.sim.dt, 1):
            raise ValueError('Motion fps must match configured control frequency')
        if args.mode != 'train':
            cfg.observations.policy.enable_corruption = False
            cfg.events = None
            cfg.terminations.time_out = None
            cfg.commands.motion.start_frame = 0
            cfg.commands.motion.pose_range = {}
            cfg.commands.motion.velocity_range = {}
            cfg.commands.motion.joint_position_range = (0.0, 0.0)
        agent = load_cfg_from_registry(args.task, 'rsl_rl_cfg_entry_point')
        agent.seed, agent.device = args.seed, args.device
        agent.max_iterations = args.iterations
        config = agent.to_dict()
        config['obs_groups'] = {'policy': ['policy'], 'critic': ['critic']}
        config['algorithm'].pop('share_cnn_encoders', None)
        config['algorithm'].pop('cnn_cfg', None)
        output = args.output or Path('logs')/datetime.now().strftime('%Y%m%d_%H%M%S')
        if args.mode == 'train':
            output.mkdir(parents=True, exist_ok=False)
        env = gym.make(args.task, cfg=cfg)
        env = RslRlVecEnvWrapper(env, clip_actions=agent.clip_actions)
        runner = OnPolicyRunner(env, config, log_dir=str(output) if args.mode=='train' else None, device=args.device)
        if args.checkpoint:
            runner.load(str(args.checkpoint.resolve()), load_optimizer=args.mode=='train')
            if args.mode == 'train':
                runner.alg.learning_rate = runner.alg.optimizer.param_groups[0]['lr']
        if args.mode == 'train':
            from isaaclab.utils.io import dump_yaml
            dump_yaml(str(output/'env.yaml'), cfg)
            dump_yaml(str(output/'agent.yaml'), agent)
            runner.learn(num_learning_iterations=args.iterations, init_at_random_ep_len=True)
        elif args.mode == 'export':
            from Deploy.export import export_bundle
            export_bundle(env.unwrapped, runner, args.motion, output, args.task, agent.clip_actions)
        else:
            infer = runner.get_inference_policy(device=args.device)
            obs = env.get_observations()
            for _ in range(args.steps):
                if not app.is_running():
                    break
                with torch.inference_mode():
                    obs, _, _, _ = env.step(infer(obs))
    finally:
        if env is not None:
            env.close()
        app.close()

if __name__ == '__main__':
    main()
