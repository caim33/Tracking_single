# tracking_single 训练、回放和导出

运行前完成 [安装](01_install.md) 和 [动作转换](../../GMR/docs/03_motion.md)。本地迁移检查没有启动 Isaac，也没有生成一个已学会动作的 checkpoint。

在准备好的 Isaac 环境中先检查依赖与真实参考动作：

```bash
python -m Deploy.preflight --stage train --motion data/dance_50hz.npz
```

检查不启动模拟器。它会报告缺失的 Isaac/WBC/RSL-RL 安装、CUDA、模型、关节/身体名称或动作文件；全部通过后仍需执行下面的两轮启动检查。

## 1. 小规模启动检查

```bash
cd "$TRACKING_ROOT"
python RL_envs/scripts/tracking.py train \
  --motion data/dance_50hz.npz --num-envs 32 --iterations 2 \
  --output logs/dance_smoke --headless --device cuda:0
```

应成功创建 G1、载入动作、收集 rollout、完成两轮 PPO 并写入 checkpoint。它只检验环境与训练入口，不代表策略已经可用。确认日志没有缺资产、NaN 或持续异常终止，再进行正式训练：

```bash
python RL_envs/scripts/tracking.py train \
  --motion data/dance_50hz.npz --num-envs 4096 --iterations 5000 \
  --output logs/dance_train --headless --device cuda:0
```

根据 GPU 显存调整 `--num-envs`。仅保留 `dance_demo` 配置，注册 ID 为 `G1-Tracking-Dance-demo`。不同动作通过 `--motion` 指定，无需复制一套机器人配置。

## 2. 恢复训练

```bash
python RL_envs/scripts/tracking.py train \
  --motion data/dance_50hz.npz --checkpoint logs/dance_train/model_1000.pt \
  --iterations 1000 --output logs/dance_resume --headless
```

将示例 checkpoint 换成真实文件。恢复时同步 PPO 内部 learning_rate 与已恢复 optimizer LR；仍不保证随机数、环境状态和 rollout 与中断前逐位一致。`--iterations` 是此次追加学习轮数。输出必须是新目录，避免混淆两次实验。

## 3. Isaac 回放

```bash
python RL_envs/scripts/tracking.py play \
  --motion data/dance_50hz.npz --checkpoint logs/dance_train/model_4999.pt \
  --steps 1000 --device cuda:0
```

示例文件名须按实际 checkpoint 替换。回放关闭观测噪声和随机事件，从参考第 0 帧开始。失败终止后由 Isaac 重置；完整动作结束也会从第 0 帧重置。这与 deploy 的单次执行后结束不同。训练时继续保留自适应片段采样和源奖励设置。

默认使用本地生成的地面材质，不加载参考坐标轴的外部 USD。需要查看参考坐标轴时增加 `--debug-vis`，并确保 Isaac Nucleus 的 `Props/UIElements/frame_prim.usd` 可访问；无窗口模式下不会开启标记。

## 4. 导出完整部署包

```bash
python RL_envs/scripts/tracking.py export \
  --motion data/dance_50hz.npz --checkpoint logs/dance_train/model_4999.pt \
  --output bundles/dance --headless --device cuda:0
```

输出为 `policy.onnx`、`motion.npz`、`manifest.json`。参数来自当前实例化任务中的真实关节顺序、默认姿态、动作缩放、PD 增益和力矩限制。导出后立即检查 ONNX 的输入/输出形状和文件校验和；需要该 Isaac 环境中安装 onnxruntime。

仅支持当前 154 维观测、29 维动作的无状态 MLP。改变观测项、顺序、历史堆叠或循环策略后，导出器应报错，需要显式更新部署实现。不要把其他 teacher/student/parkour 的 ONNX 放进这个包。

## 5. 源代码阅读顺序

1. `robots/g1_29dof/dance_demo/__init__.py`：唯一 Gym 注册 ID。
2. `tracking_env_cfg.py`：场景、动作、观测、奖励、终止、随机化、控制周期。
3. `g1.py`：URDF、关节初始值、PD 和动作缩放。
4. `agents/rsl_rl_ppo_cfg.py`：MLP 和 PPO 参数。
5. `mdp/commands.py`：命名动作载入、参考状态、片段采样、重置、可视化。
6. `mdp/observations.py`、`rewards.py`、`terminations.py`、`events.py`：对应计算函数。辅助 `actuator.py` 保留供研究阅读，当前 G1 默认配置不直接使用。不包含 SMPL 机器人训练配置。

根 WBC 注册仅导入 tracking_single，不会自动加载源仓库其他任务。

## 模型变更注意

源 tracking 配置指向未入库的 `unitree_description/urdf/g1/main.urdf`。提取版改用同仓库 GMR 已提供、网格完整的 `g1_custom_collision_29dof.urdf`。这解决可复现性问题，但不证明与原未入库模型的质量、碰撞、惯量完全相同。已有 checkpoint 的迁移效果需要重新对比；推荐用本版明确的模型训练并导出，再做 sim2sim。
