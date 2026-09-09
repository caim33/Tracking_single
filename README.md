# Tracking_single

将单人视频恢复为人体动作，重定向到 G1 29 DoF，训练单参考动作跟踪策略，并导出到 MuJoCo / G1 部署。

```text
video (30 fps)
  → GVHMR: hmr4d_results.pt
  → GMR: robot motion.pkl (xyzw, 30 Hz)
  → pipeline.convert: named motion.npz (wxyz, 50 Hz)
  → tracking_single PPO: checkpoint
  → export: policy.onnx + motion.npz + manifest.json
  → Deploy: MuJoCo / Unitree G1
```

| 阅读顺序 | 教程 |
|---|---|
| 1 | [安装、环境和模型资源](docs/01_install.md) |
| 2 | [视频恢复与 GMR 重定向](docs/02_video.md) |
| 3 | [动作转换、帧率和坐标格式](docs/03_motion.md) |
| 4 | [单动作训练、回放、导出](docs/04_training.md) |
| 5 | [单动作 deploy 与 MuJoCo](docs/05_deploy.md) |
| 6 | [G1 真机只读检查与执行](docs/06_real_robot.md) |
| 7 | [验证结果、迁移边界与待验收项](docs/07_validation.md) |
| 按文件查 | [全部保留代码的教程和 API 索引](docs/code_reference.md) |

先在普通 Python 环境验证基础部分：

```bash
python -m pip install -e ".[test,deploy]"
python -m pytest -q
python tools/audit_docs.py
```

完整视频、训练和实机流程还需要授权 SMPL/SMPL-X 模型、GVHMR 权重、Linux CUDA/Isaac Lab 环境及实际机器人。CPU 自动检查已经覆盖文件格式、推理接口和 MuJoCo 短程运行；尚未完成完整 GPU 管线或真机动作质量验收。不要把测试用零输出策略当成训练结果。

源码提取自 humanoid-lab 的固定版本，迁移记录在 `docs/migration_manifest.json`。源配置依赖未入库的机器人 URDF，本版统一使用已迁移的 GMR G1 模型；旧 checkpoint 需重新验证模型一致性。发布与使用请阅读 [来源及许可证说明](THIRD_PARTY_NOTICES.md)。
