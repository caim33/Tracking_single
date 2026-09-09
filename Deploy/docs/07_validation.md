# 验证、迁移边界与待验收项

## 自动检查

在仓库根目录运行：

```bash
python -m pytest -q
python Deploy/tools/audit_docs.py
python -m compileall -q GVHMR GMR RL_envs Deploy
```

CPU 回归检查覆盖：GMR 导出包含第零帧且帧数一致；30→50 Hz 的真实时间插值；PKL→NPZ CLI；文件防覆盖；非有限帧率/重复名称；四元数规范和世界角速度；154 维观测排列；ONNX 包校验；参考结束不回绕；pelvis/torso IMU 坐标一致性；真实 G1 网格加载和短程动力学运行。

依赖复核后增加了单任务注册/内部导入检查、启动前资源检查，以及真实 RSL-RL CPU PPO 更新与 ONNX 导出数值对比。目前完整检查为 27 项通过；其中 3 项需要 Torch 和 RSL-RL，没有安装时会明确跳过。PPO 检查使用合成观测，不包含 Isaac 环境步进；导出检查覆盖带/不带观测归一化的真实网络，并将 ONNX 输出与 PyTorch 输出比较。

测试中的零输出 ONNX 和静态参考是临时生成的测试数据，运行后由测试环境清理；它们不是训练成果，也不用于证明机器人能跟踪动作。

本次本地验证环境：Windows、Python 3.12、NumPy 2.2.6、SciPy 1.15.3、MuJoCo 3.12.0、ONNX 1.22.0、ONNX Runtime 1.29.0。安装教程中的 Python 3.10 是为了匹配 GVHMR 原有 CUDA 轮子；完整 Linux 环境仍需实际确认。

扩展检查使用 Torch 2.7.0 CPU、RSL-RL 3.0.1。这里的 NumPy 2.2.6 是 CPU 工具环境版本，不能直接作为 Isaac 环境要求；`train` 依赖组按 Isaac Lab 2.3 的要求限制 NumPy <2。

## 训练和 Deploy 需要哪些内容

| 阶段 | 仓库已经提供 | 仍需在运行环境准备 |
|---|---|---|
| 训练 | 唯一 `dance_demo` 任务、Gym 注册、MDP/PPO 配置、训练/回放/导出入口、G1 URDF/XML 和网格、命名动作加载器 | Isaac Sim/Isaac Lab 2.3、兼容 CUDA Torch/GPU 驱动、`train` 依赖和 WBC 安装、实际 50 Hz 参考动作 |
| MuJoCo 部署 | 观测构造、ONNX 加载、关节映射、PD、单次动作停止、G1 模型 | CPU 工具及 deploy 依赖、由实际训练导出的完整 bundle |
| G1 真机 | SDK2 适配、IMU 坐标转换、启动核对和停控入口 | Linux、Unitree SDK2/CycloneDDS、网卡与机器人、匹配的固件/IMU 定义、已验收的 bundle |

在对应环境、仓库根目录运行启动前检查：

```bash
python -m Deploy.preflight --stage train --motion data/dance_50hz.npz
python -m Deploy.preflight --stage sim2sim --bundle bundles/dance
python -m Deploy.preflight --stage sim2real --bundle bundles/dance --interface enp3s0
```

把动作、策略包和网卡替换为真实输入。退出码 0 表示当前阶段的这些前置条件通过；1 表示有缺失或不匹配，并逐项打印原因。检查不启动 Isaac、不连接机器人，也不代替两轮 Isaac 启动检查、完整 sim2sim 或真机验收。默认场景使用本地材质；可选 `--debug-vis` 坐标轴依赖 Isaac Nucleus 的 frame USD。

本次实际运行 train 前置检查时，机器人资源和已安装的 CPU 组件通过；Isaac 安装、CUDA、训练用 NumPy 1.x 和实际参考动作未通过，因此没有宣称已完成仿真训练。仓库不附实际动作数据、训练 checkpoint 或可用于跟踪的预训练策略。

## 仍须在对应设备验收

| 阶段 | 当前能确认的内容 | 完成条件 |
|---|---|---|
| GVHMR | 源码、推理配置、缺失 ViTPose 文件、权重路径说明已整理 | 授权模型齐全，在 GPU 上完成一个视频并检查世界轨迹 |
| GMR | 首帧与输出契约回归通过，G1 模型可加载 | 用实际 SMPL-X 预测完成 IK 并检查脚和关节 |
| Isaac | 单任务注册、配置/入口和 CPU PPO 软件接口已检查，帧率和命名检查已实现 | Linux Isaac 中两轮 smoke、训练、回放与导出成功 |
| MuJoCo | CPU ONNX 与真实机器人模型短程测试通过 | 用真实训练策略完成整段动作并检查稳定性 |
| 真机 | SDK2 入口、IMU 转换和停控路径已实现 | G1 上只读、短程、急停/超时、完整动作逐项验收 |

## 代码适配与文件记录

[文件记录](../../RL_envs/docs/migration_manifest.json) 保存输入版本、仓库起点、原始文件 SHA-256 和整理范围。source 记录输入文件路径，destination 以仓库根目录为起点，指向当前文件。修改后的文件可能不再与 source_sha256 相同；该值用于回溯原始输入，不是最终文件校验。

[依赖恢复记录](../../GVHMR/docs/upstream_recovery.json) 记录从官方 GVHMR 固定提交补齐的 6 个 ViTPose builder 文件。推理模型会直接引用这些文件，运行时必须保留。

主要修改包括：删除 GMR 导出首帧丢失和无限循环保存路径；增加 headless；替换未入库 URDF；命名动作格式及真实时间重采样；训练加载时映射名称并检查频率；修复两个不存在的 anchor velocity 属性；修复短动作采样熵除零；推理只注册实际存在的模型组件；单动作训练/导出/deploy 入口。

本仓库没有迁移完整 teacher/student、物体操作、parkour、感知标定、数据集、机器私有路径或训练输出。GVHMR 重训练和 GMR 的其他输入格式入口不在本次范围。原 deploy 的三个头文件保留为接口依据，当前可执行控制路径已专门实现为 `Deploy` 下的 Python 单动作控制器。

## 教程覆盖的定义

[逐文件索引](../../RL_envs/docs/code_reference.md) 为每个保留的 Python/C++ 头文件给出职责、对应分阶段教程、函数/类索引和可解析的命令行参数；库文件明确标为由主入口调用。`Deploy/tools/audit_docs.py` 检查文件清单与索引一致，新增或修改文件后应重新生成并人工检查说明。

覆盖索引通过表示“每个文件有可追溯使用入口与 API 索引”，不表示每个上游内部函数都有独立实验教程，也不等于所有硬件路径都已经执行验证。持续维护时应把新增行为补进对应阶段教程和必要回归测试。
