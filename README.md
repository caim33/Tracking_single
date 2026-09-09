# Tracking_single

将单人视频恢复为人体动作，重定向到 G1 29 DoF，训练单参考动作跟踪策略，并导出到 MuJoCo / G1 部署。

```text
video (30 fps)
  → GVHMR: hmr4d_results.pt
  → GMR: robot motion.pkl (xyzw, 30 Hz)
  → GMR.pipeline.convert: named motion.npz (wxyz, 50 Hz)
  → tracking_single PPO: checkpoint
  → export: policy.onnx + motion.npz + manifest.json
  → Deploy: MuJoCo / Unitree G1
```

仓库顶层只有四个模块文件夹，辅助代码和教程归入对应模块：

```text
Tracking_single/
├── GVHMR/       # 视频 → 人体动作；docs/ 包含视频教程和依赖来源
├── GMR/         # 人体动作 → G1；pipeline/ 动作转换；docs/ 格式教程
├── RL_envs/     # 训练、回放和导出；docs/ 安装、训练、全量索引及文件记录
└── Deploy/      # 单动作部署；docs/ 部署和验收；tests/ 回归；tools/ 文档检查
```

| 阅读顺序 | 教程 |
|---|---|
| 1 | [安装、环境和模型资源](RL_envs/docs/01_install.md) |
| 2 | [视频恢复与 GMR 重定向](GVHMR/docs/02_video.md) |
| 3 | [动作转换、帧率和坐标格式](GMR/docs/03_motion.md) |
| 4 | [单动作训练、回放、导出](RL_envs/docs/04_training.md) |
| 5 | [单动作 deploy 与 MuJoCo](Deploy/docs/05_deploy.md) |
| 6 | [G1 真机只读检查与执行](Deploy/docs/06_real_robot.md) |
| 7 | [验证结果、迁移边界与待验收项](Deploy/docs/07_validation.md) |
| 按文件查 | [全部保留代码的教程和 API 索引](RL_envs/docs/code_reference.md) |

先在普通 Python 环境验证基础部分：

```bash
python -m pip install -e ".[test,deploy]"
python -m pytest -q
python Deploy/tools/audit_docs.py
```

完整视频、训练和实机流程还需要授权 SMPL/SMPL-X 模型、GVHMR 权重、Linux CUDA/Isaac Lab 环境及实际机器人。CPU 自动检查已经覆盖文件格式、推理接口和 MuJoCo 短程运行；尚未完成完整 GPU 管线或真机动作质量验收。不要把测试用零输出策略当成训练结果。

本仓库统一使用 GMR G1 模型进行动作转换、训练和部署。使用已有 checkpoint 时，请核对机器人模型、关节顺序及控制参数的一致性。各组件的作者与许可信息见 [第三方组件与许可证说明](THIRD_PARTY_NOTICES.md)。
