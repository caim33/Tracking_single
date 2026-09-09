from __future__ import annotations

import torch
from typing import TYPE_CHECKING, Literal

import isaaclab.utils.math as math_utils
from isaaclab.assets import Articulation
from isaaclab.envs.mdp.events import _randomize_prop_by_op
from isaaclab.managers import SceneEntityCfg

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedEnv


##
# Randomize the robot's joint default positions
# Randomize the joint default positions which may be different from URDF due to calibration errors.
##

def randomize_joint_default_pos(
    #参数
    env: ManagerBasedEnv,
    env_ids: torch.Tensor | None,
    asset_cfg: SceneEntityCfg,
    pos_distribution_params: tuple[float, float] | None = None,
    operation: Literal["add", "scale", "abs"] = "abs",
    distribution: Literal["uniform", "log_uniform", "gaussian"] = "uniform",
):

    #提取机器人资产
    asset: Articulation = env.scene[asset_cfg.name]

    #保存机器人原始(默认)位置
    asset.data.default_joint_pos_nominal = torch.clone(asset.data.default_joint_pos[0])

    #确定环境ID
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=asset.device)

    #确定关节ID
    if asset_cfg.joint_ids == slice(None):
        joint_ids = slice(None)
    else:
        joint_ids = torch.tensor(asset_cfg.joint_ids, dtype=torch.int, device=asset.device)

    #随机化关节位置
    if pos_distribution_params is not None:
        pos = asset.data.default_joint_pos.to(asset.device).clone()
        pos = _randomize_prop_by_op(
            pos, pos_distribution_params, env_ids, joint_ids, operation=operation, distribution=distribution
        )[env_ids][:, joint_ids]

        #更新关节位置
        if env_ids != slice(None) and joint_ids != slice(None):
            env_ids = env_ids[:, None]
        asset.data.default_joint_pos[env_ids, joint_ids] = pos
        #更新动作偏移量
        env.action_manager.get_term("joint_pos")._offset[env_ids, joint_ids] = pos

##
# Randomize the center of mass (CoM) of rigid bodies
# Randomize the center of mass (CoM) of rigid bodies by adding a random value sampled from the given ranges.
#   note::
#   This function uses CPU tensors to assign the CoM. It is recommended to use this function only during the initialization of the environment.
##

def randomize_rigid_body_com(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor | None,
    com_range: dict[str, tuple[float, float]],
    asset_cfg: SceneEntityCfg,
):

    #提取机器人资产
    asset: Articulation = env.scene[asset_cfg.name]
    #确定环境ID
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device="cpu")
    else:
        env_ids = env_ids.cpu()

    #确定刚体部件索引
    if asset_cfg.body_ids == slice(None):
        body_ids = torch.arange(asset.num_bodies, dtype=torch.int, device="cpu")
    else:
        body_ids = torch.tensor(asset_cfg.body_ids, dtype=torch.int, device="cpu")

    #采样随机的质量中心（CoM）偏移量
    range_list = [com_range.get(key, (0.0, 0.0)) for key in ["x", "y", "z"]]
    ranges = torch.tensor(range_list, device="cpu")
    rand_samples = math_utils.sample_uniform(ranges[:, 0], ranges[:, 1], (len(env_ids), 3), device="cpu").unsqueeze(1)

    #获取当前刚体的质量中心（CoM）
    coms = asset.root_physx_view.get_coms().clone()

    #随机化质量中心
    coms[:, body_ids, :3] += rand_samples

    #更新质量中心
    asset.root_physx_view.set_coms(coms, env_ids)
