# 视频 → GVHMR → GMR

目标：从一个单人视频得到 G1 的根位姿与 29 个关节轨迹。输入、输出、姿态网络、SMPL-X 与 IK 的内部文件索引见 [代码参考](code_reference.md)。

## 1. 准备 30 fps 视频

GVHMR 的这份实现把输出帧率固定为 30；原始 60 fps 视频直接输入会改变动作时间。本提取版增加检查，要求先真正重采样：

```bash
ffmpeg -i /absolute/input.mp4 -vf fps=30 -an "$TRACKING_ROOT/data/dance_30fps.mp4"
```

选取清晰、完整的人体，避免镜头中多人互相遮挡。截取范围也在视频阶段完成。对不同输入使用不同文件名和输出目录，避免上游按同名视频复用预处理缓存。

## 2. GVHMR

```bash
conda activate tracking-gvhmr
cd "$TRACKING_ROOT/Retargeting/GVHMR"
python tools/demo/demo.py \
  --video "$TRACKING_ROOT/data/dance_30fps.mp4" \
  --output_root "$TRACKING_ROOT/outputs/gvhmr" -s
```

`-s` 仅用于固定相机；移动相机去掉 `-s`，默认使用 SimpleVO。`--f_mm` 可填写已知的等效焦距；不确定时保留默认估计。`--verbose` 输出更多可视化诊断。

成功后检查：

```text
outputs/gvhmr/dance_30fps/hmr4d_results.pt
outputs/gvhmr/dance_30fps/1_incam.mp4
outputs/gvhmr/dance_30fps/2_global.mp4
```

先看相机视角与世界视角视频：人体不应跳变，身体朝向和地面关系应合理，再进入 IK。`.pt` 中使用 `smpl_params_global`，不是相机坐标的 SMPL 参数。

批处理入口 `tools/demo/demo_folder.py` 接收 `-f` 输入视频目录、`-d` 输出目录和 `-s` 固定相机选项；先对每个输入完成 30 fps 处理，并检查每个子任务的输出。它内部调用同一个 `demo.py`。

## 3. GMR

```bash
conda activate tracking-gmr
cd "$TRACKING_ROOT/Retargeting/GMR"
python scripts/gvhmr_to_robot.py \
  --gvhmr_pred_file "$TRACKING_ROOT/outputs/gvhmr/dance_30fps/hmr4d_results.pt" \
  --save_path "$TRACKING_ROOT/outputs/gmr/dance.pkl" \
  --robot unitree_g1 --headless
```

`--headless` 不创建窗口，适用于服务器；去掉它可以看 IK 过程。`--rate_limit` 让可视化按参考速度播放，不改变保存的帧率。输入和保存路径都必须明确提供，输出已存在时会报错。

该入口现在从第 0 帧开始，仅处理一遍，结束后保存。PKL 包含 `fps`、`root_pos[N,3]`、`root_rot[N,4]`、`dof_pos[N,29]`、`joint_names[29]`。根四元数是 **xyzw**，位置单位为米，角度单位为弧度。

## 4. 检查机器人动作

```bash
python scripts/vis_robot_motion.py \
  --robot unitree_g1 \
  --robot_motion_path "$TRACKING_ROOT/outputs/gmr/dance.pkl"
```

这个入口是几何回放，不运行策略。检查脚是否漂浮/穿地、关节是否突跳、根部朝向是否正确。默认播放一次后关闭，使用 `--loop` 时重复播放，按 Ctrl+C 结束。保存视频用 `--record_video --video_path /absolute/preview.mp4`，退出时会关闭并写完录制文件。

## 5. 内部代码怎么查

`hmr4d/utils/preproc` 负责检测、跟踪、特征、2D 姿态与相机运动；`hmr4d/network` 是模型结构；`gvhmr_pl_demo.py` 组织推理；`pipeline/gvhmr_pipeline.py` 解码并做后处理；`utils/body_model` 与 `utils/geo` 实现人体模型、坐标和旋转运算。它们是库模块，通过视频入口使用，不逐个执行。

GMR 的 `utils/smpl.py` 把 SMPL-X 输出转成命名人体关节；`motion_retarget.py` 构建/迭代 IK；`ik_configs/smplx_to_g1.json` 定义人体到机器人的约束；`robot_motion_viewer.py` 负责可视化。`params.py` 中保留上游其他机器人的映射，但本仓库只打包并支持 G1，其他机器人不能直接使用。

## 常见失败

缺少 SMPL 文件时检查模型目录；找不到 ViTPose builder 时检查是否使用了本仓库的 editable install；无 DISPLAY 时用 `--headless` 运行 GMR；视频帧率错误时先执行 ffmpeg 重采样；IK 大幅失真时回看 GVHMR 世界轨迹与人体尺度。PKL/PT 只读取自己信任的文件，它们可能包含可执行序列化内容。
