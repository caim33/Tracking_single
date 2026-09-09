import gymnasium as gym

from WBC.tasks.manager_based.tracking_single.robots.g1_29dof.dance_mo import tracking_env_cfg
from WBC.tasks.manager_based.tracking_single.agents import rsl_rl_ppo_cfg

gym.register(
    id="G1-Tracking-Dance-mo",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": tracking_env_cfg.TrackingEnvCfg,
        "rsl_rl_cfg_entry_point": rsl_rl_ppo_cfg.G1TrackingPPORunnerCfg,
    },
)
