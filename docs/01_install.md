# 安装与资源准备

本项目的完整运行目标是 Ubuntu、NVIDIA GPU 和 G1 29 DoF。Windows 可以运行动作转换、CPU ONNX 和 MuJoCo 检查；GVHMR、Isaac Lab 和 SDK2 真机环境需要单独准备。各阶段通过文件衔接，不要求装进一个 Python 环境。

## 1. 克隆与目录

```bash
git clone https://github.com/caim33/Tracking_single.git
cd Tracking_single
export TRACKING_ROOT="$PWD"
mkdir -p data outputs bundles
```

以下命令默认在仓库根目录，明确写了 `cd` 的 GVHMR/GMR 命令除外。项目采用 editable 安装，机器人网格位于源码树中；不要把单独安装的 wheel 当成完整资源包。

## 2. 动作转换和 MuJoCo

```bash
conda create -n tracking-tools python=3.10 -y
conda activate tracking-tools
python -m pip install -e ".[test,deploy]"
python -m pytest -q
python tools/audit_docs.py
```

依赖范围记录在根目录 `pyproject.toml`。SciPy 限定在 1.14–1.15，兼容源 GMR 的旋转接口。当前实际 CPU 验证版本另见 [验证记录](07_validation.md)。不要直接把这个环境的 torch 版本覆盖进 Isaac 环境。

## 3. GVHMR 推理环境

```bash
conda create -n tracking-gvhmr python=3.10 -y
conda activate tracking-gvhmr
cd "$TRACKING_ROOT/Retargeting/GVHMR"
python -m pip install -r requirements.txt
python -m pip install -e .
```

源项目锁定 torch 2.3.0 + CUDA 12.1、torchvision 0.18.0，PyTorch3D 下载地址也是 Python 3.10/Linux/CUDA 12.1 的特定构建。系统还需可用的 `ffmpeg`。CUDA 驱动、GPU 内存和上述轮子必须匹配，不能用 CPU 环境替代完整视频推理。

从 [GVHMR 官方安装说明](https://github.com/zju3dv/GVHMR/blob/main/docs/INSTALL.md) 获取预训练资源；下载前按相应网站完成许可证步骤。最终目录必须是：

```text
Retargeting/GVHMR/inputs/checkpoints/
  body_models/smplx/SMPLX_NEUTRAL.npz
  body_models/smpl/SMPL_NEUTRAL.pkl
  gvhmr/gvhmr_siga24_release.ckpt
  hmr2/epoch=10-step=25000.ckpt
  vitpose/vitpose-h-multi-coco.pth
  yolo/yolov8x.pt
```

这里列出默认中性模型所需文件；切换模型性别或附加评估时还需相应模型。SMPL/SMPL-X 权重与视频没有包含在仓库中。支持文件中的关节回归矩阵已经随源代码迁移，不能把它们误当成 SMPL 模型权重。

本提取版只支持 GVHMR 视频推理；缺失训练数据集的 GVHMR 重训练入口已排除。移动相机使用 SimpleVO，固定相机使用 `-s`；DPVO 未打包。

## 4. GMR 环境

```bash
conda create -n tracking-gmr python=3.10 -y
conda activate tracking-gmr
python -m pip install "numpy>=1.23.5,<2.3" "scipy>=1.14,<1.16"
python -m pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
cd "$TRACKING_ROOT/Retargeting/GMR"
python -m pip install -e .
```

GMR 的 SMPL 前向和 IK 可以用 CPU；这不等于 GVHMR 视频网络可以用 CPU。默认 IK 选择 `daqp`，安装声明已经补齐相应 solver。把自己取得授权的 SMPL-X 资源放在：

```text
Retargeting/GMR/assets/body_models/smplx/SMPLX_NEUTRAL.npz
```

也可通过 `--body-models /absolute/body_models` 指定目录。文件内模型变体必须与 SMPL-X 库要求一致。

## 5. Isaac Lab 训练环境

按 [Isaac Lab v2.3 文档](https://isaac-sim.github.io/IsaacLab/v2.3.0/) 安装兼容的 Isaac Sim/Isaac Lab。确认该环境能运行官方示例后，再执行：

```bash
cd "$TRACKING_ROOT"
python -m pip install -e ".[deploy]"
python -m pip install -e RL_envs/source/WBC
python -m pip install rsl-rl-lib==3.0.1 onnx
python RL_envs/scripts/tracking.py --help
```

`python` 必须是该 Isaac 环境中的解释器。若使用 `isaaclab.sh -p`，将后续教程中的 `python` 替换为该启动方式。本入口固定使用 RSL-RL 3.0.1 的策略和观测 API；更换大版本前需要适配并重新验证。

## 6. 安装完成判据

CPU 环境中测试和教程审计通过；GVHMR 权重目录齐全；Isaac 官方示例成功；GMR 能加载机器人 XML。真机 SDK2 环境另外按 [真机教程](06_real_robot.md) 配置。只有满足相关阶段判据后，才继续该阶段。
