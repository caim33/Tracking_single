# GMR → 可训练 reference motion

这一阶段不需要启动 Isaac。它在真实 G1 XML 上做 MuJoCo 正向运动学，并生成训练和部署共用的 NPZ。

## 转换命令

```bash
conda activate tracking-tools
cd "$TRACKING_ROOT"
python -m GMR.pipeline.convert \
  --input outputs/gmr/dance.pkl \
  --output data/dance_50hz.npz --fps 50
```

`--robot-xml` 默认使用随仓库迁移的 `g1_mocap_29dof.xml`。仅在明确采用另一份同关节结构模型时才修改，并同步训练模型和部署模型。输出文件必须是一个新 `.npz`。

## 为什么是 50 Hz

四个源 tracking 配置的仿真步长均为 0.005 秒、decimation 为 4，策略每 0.02 秒更新一次。因此每一步消费一个参考帧时，动作必须为 50 Hz。包括名叫 `dance_mo_fps60` 的历史变体，实际控制频率也为 50 Hz，名称不代表控制频率。

转换器按秒建立时间轴，根平移和关节角线性插值，根四元数用 SLERP。保留第一帧，最后一个采样点不超过原始末帧；当时长不是 1/50 秒的整数倍时，尾端差值小于一个目标采样周期。

## 文件契约

| 字段 | 形状 | 含义 |
|---|---|---|
| schema_version | 标量 | 当前为 1 |
| fps | 标量 | 正数，默认 50 |
| joint_names | [29] | 显式关节名，顺序对应 joint 数组 |
| body_names | [B] | 显式身体名，顺序对应 body 数组 |
| joint_pos / joint_vel | [N,29] | 关节角 / 角速度，rad / rad/s |
| body_pos_w | [N,B,3] | 世界坐标位置，米 |
| body_quat_w | [N,B,4] | 世界朝向，**wxyz** |
| body_lin_vel_w | [N,B,3] | 身体质心的世界线速度，m/s |
| body_ang_vel_w | [N,B,3] | 世界角速度，rad/s |

注意 GMR PKL 的根四元数是 xyzw，训练 NPZ 是 wxyz。转换器只在该边界变换约定。位姿对应 link 原点，线速度对应身体质心，与 Isaac Lab 2.3 的 `body_pos_w` / `body_lin_vel_w` 属性约定一致。线速度用质心位置有限差分，角速度在 SO(3) 上差分，不直接对四元数分量求导。相邻四元数取相反符号也不会引入假角速度。MuJoCo 初始化会把根质心速度换回自由关节原点速度。

## 程序内检查

```python
from GMR.pipeline.motion import load_motion
motion = load_motion("data/dance_50hz.npz")
print(float(motion["fps"]), motion["joint_pos"].shape)
print(motion["joint_names"])
```

加载器关闭 NPZ 文件描述符后再使用数组；拒绝缺字段、非有限数、非单位四元数、重复名称、帧数不足或形状不一致。源仓库历史 NPZ 没有完整名称元数据，不能直接视作新契约文件；优先从 GMR PKL 重建，避免猜测旧关节顺序。

`name_indices(actual, requested)` 把归档名称顺序映射到 Isaac 或部署策略顺序。`qpos_to_motion(qpos, fps, model)` 接受 MuJoCo 的 `[xyz,wxyz,29 joints]`，用于已有 qpos 数据接入。`world_angular_velocity` 与 `resample_qpos` 的定义、参数和调用位置见代码参考。

## 成功判据与排错

应打印帧数、50 Hz 和合理时长；所有数值有限，关节名恰好 29 个。名字不匹配应更换正确模型或重建动作，不能通过排序数组绕过检查。帧率不匹配应重新转换，不能仅修改 NPZ 中的 fps 标量。进入训练前仍要检查实际几何动作质量。
