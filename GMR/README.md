# GMR：GVHMR 人体动作 → G1

本目录保留 GMR 的 IK、G1 模型和动作可视化，用于单参考动作管线。

`pipeline/` 包含训练和部署共用的命名动作格式、时间重采样与正向运动学。完成根目录 editable 安装后，从仓库根目录运行 `python -m GMR.pipeline.convert --help`；完整转换示例见下方格式教程。原 `pipeline.convert` 入口已随目录调整改为 `GMR.pipeline.convert`。

- [安装和 SMPL-X 资源](../RL_envs/docs/01_install.md)
- [人体恢复与重定向教程](../GVHMR/docs/02_video.md)
- [GMR PKL 转训练 NPZ](docs/03_motion.md)
- [逐文件 API 与教程索引](../RL_envs/docs/code_reference.md)
- [原始许可](LICENSE)

运行入口为 `scripts/gvhmr_to_robot.py` 和 `scripts/vis_robot_motion.py`，均可先运行 `--help` 查看参数。前者支持 headless、保留第零帧，并输出带 `joint_names` 的单次完整动作。其他输入格式和机器人未纳入本次管线。

[上游原始 README](README.upstream.md) 完整保留作者、论文、许可证和致谢信息。其中关于其他机器人、数据集和脚本的操作仅用于了解完整上游项目，当前提取版按上面教程运行。
