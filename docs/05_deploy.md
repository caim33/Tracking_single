# 单动作 deploy 与 MuJoCo

deploy 加载一个策略包，并在每个策略周期使用该动作的一帧参考状态。它运行 policy 来产生目标关节位置；GMR 几何回放本身不等于策略部署。

## 1. 包结构与绑定关系

```text
bundles/dance/
  policy.onnx       # [1,154] → [1,29]
  motion.npz        # 命名参考轨迹，通常 50 Hz
  manifest.json    # 关节顺序、PD、缩放、周期、观测顺序和 SHA-256
```

不要分别替换里面的文件。加载时验证策略和动作 SHA-256、名称、数组形状和控制频率。修改动作或训练配置后，从训练入口重新导出。manifest 本身是配置文件，不能通过改校验和掩盖误配。

## 2. 与训练完全相同的观测排列

| 零起始区间 | 项 | 维度 | 定义 |
|---|---|---|---|
| 0–28 | command 关节位置 | 29 | 当前参考绝对关节角 |
| 29–57 | command 关节速度 | 29 | 当前参考关节速度 |
| 58–63 | motion_anchor_ori_b | 6 | 机器人 anchor 到参考 anchor 的旋转矩阵前两列 |
| 64–66 | base_ang_vel | 3 | pelvis 坐标系角速度 |
| 67–95 | joint_pos | 29 | 实测关节角减训练默认值 |
| 96–124 | joint_vel | 29 | 实测速度减训练默认速度 |
| 125–153 | actions | 29 | 上一周期动作，首次为零 |

六维旋转必须用 `R[:, :2].reshape(-1)`，不是把第一列和第二列分别拼接。参考及机器人 anchor 默认是 `torso_link`，base gyro 是 pelvis；两者不能混用。所有关节数组先按 manifest 的名称顺序映射。

动作转换为 `default_joint_pos + action_scale * action`，与源 `joint_actions.h` 的缩放/偏置契约一致。动作 clip 取导出配置。MuJoCo 用导出的 kp/kd 计算 PD 力矩，再按训练力矩上限限幅。示例不包含历史观测、外部物体状态或根平移观测。

## 3. 无窗口短程检查

```bash
conda activate tracking-tools
cd "$TRACKING_ROOT"
python -m Deploy.sim2sim --bundle bundles/dance \
  --headless --steps 100 --output outputs/dance_sim_smoke.npz
```

应完成指定策略步数，或在参考结束时停止。输出记录 `observation[T,154]`、`joint_pos[T,29]`、`target[T,29]` 和 `root_height[T]`。检测到非有限状态或 pelvis 高度低于 0.25 米会报错结束。输出文件必须是新路径。

## 4. 可视化完整动作

```bash
python -m Deploy.sim2sim --bundle bundles/dance
```

初始化到参考首帧的根位姿、关节角及速度，从 frame 0 顺序推理。参考不会自动循环或跳回开头。关掉窗口也会退出。默认 MuJoCo 步长 0.005 秒，在一个 0.02 秒策略周期内执行四个物理子步；不整除的控制周期会报错。

地面和灯光是在迁移后的 GMR XML 上添加的，关节名和物理参数来自该模型。训练使用对应 URDF；跨仿真的碰撞、惯量导入和接触效果仍需比较。短程推理成功只能证明接口可运行，不能证明某个动作已经稳定跟踪。

## 5. 自定义接入与每个文件职责

- `runtime.py`：`TrackingPolicy(bundle)` 加载/校验；`step(frame,q,dq,base_gyro,anchor_wxyz)` 返回关节目标和完整观测；`reset()` 清空上一帧动作。
- `sim2sim.py`：模型、时钟、PD 和窗口/日志；可以作为独立仿真入口。
- `export.py`：从活跃 Isaac 环境提取参数；由训练入口调用，不单独执行。
- `robot_state.py`：通过真实关节 FK 统一 pelvis/torso IMU；用于真机输入适配。
- `sim2real.py`：SDK2 的读状态、启动核对、策略更新和低层发布。
- `reference/*.h`：从源 deploy 保留的关节映射、观测、动作接口对照。它们依赖原 C++ 框架，不作为本提取版的独立可编译控制器。本版可运行部署入口是上述 Python 实现。

## 常见错误

`[1,154] -> [1,29]` 检查失败：导出了错误任务或策略结构。checksum 失败：包中至少一个文件被替换。fps 不匹配：重做动作转换并导出。名字不匹配：模型不一致。站立后倒地：检查策略训练质量、碰撞模型、关节顺序、PD、参考时间和 IMU 坐标，不要仅凭没有异常输出判断部署成功。
