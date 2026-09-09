# 单参考动作 tracking 训练

本目录包含 Isaac Lab 的 G1 29 DoF tracking_single 环境，以及训练、回放和策略导出入口。输入是 GMR 动作经 `GMR.pipeline.convert` 转换得到的命名 `motion.npz`；导出策略包交给顶层 `Deploy`。

仅保留 `robots/g1_29dof/dance_demo` 配置，任务 ID 为 `G1-Tracking-Dance-demo`；不同动作通过 `--motion` 指定。环境、奖励、PPO 配置和机器人资源已包含在仓库中，实际参考动作与 Isaac/GPU 运行环境需要另行准备。可先运行 `python -m Deploy.preflight --stage train --motion data/dance_50hz.npz` 查看缺项。

- [环境安装与版本](docs/01_install.md)
- [准备参考动作](../GMR/docs/03_motion.md)
- [训练、恢复、回放和导出完整教程](docs/04_training.md)
- [逐文件职责和 API 索引](docs/code_reference.md)

从仓库根目录查看入口参数：

```bash
python RL_envs/scripts/tracking.py --help
```

`scripts/tracking.py` 提供 `train`、`play`、`export` 三种模式，均需显式指定 `--motion`。`source/WBC/tasks/manager_based/tracking_single` 保存环境配置、任务注册和 MDP 实现。运行训练还需完成 Isaac Lab、RSL-RL 和 WBC 安装，具体命令见上方教程。

导出目录包含 `policy.onnx`、`motion.npz` 和 `manifest.json`，绑定参考动作、关节顺序和控制参数。当前仅支持 154 维观测、29 维动作的无状态 MLP。Isaac 回放会在动作结束后重置；Deploy 默认只执行一次。完整 GPU 训练尚未在本次本地检查中执行，验收项目见 [验证记录](../Deploy/docs/07_validation.md)。
