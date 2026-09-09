# G1 单动作真机入口

这部分已经实现，但尚未在真实 G1 上执行验证。先完成 Isaac 回放和 MuJoCo 全动作检查。适用对象是解锁腰部和腕部的 29 DoF G1、SDK2 的 `unitree_hg` 消息和 PR 控制模式；23 DoF 或锁腰设备不适用。

## 1. 准备通信环境

在连接机器人网口的 Ubuntu 机器上，按 [Unitree SDK2 Python](https://github.com/unitreerobotics/unitree_sdk2_python) 安装 CycloneDDS 和 SDK。读取 [官方 G1 低层示例](https://github.com/unitreerobotics/unitree_sdk2_python/blob/master/example/g1/low_level/g1_low_level_example.py) 对照固件协议。再安装本项目：

```bash
cd "$TRACKING_ROOT"
python -m pip install -e ".[deploy]"
```

确认网卡名称和机器人网络设置。这里不自动更改系统网络，也不自动退出已有运动控制器。操作员应按设备流程准备吊架、周围空间和物理急停。

## 2. 确认 IMU 所在坐标系

必须明确给出 `--imu-frame pelvis` 或 `--imu-frame torso`，本入口不猜测固件定义。检查 LowState 中 quaternion/gyroscope 的实际含义，并通过只读姿态变化验证。

若 IMU 为 torso，`robot_state.py` 用当前腰部关节 FK 求 pelvis→torso 姿态，恢复 pelvis 的世界姿态；旋转 gyro 到 pelvis 后还会减去腰部关节运动贡献。仅把 torso gyro 直接当成 base gyro 会与训练观测不同。四元数传入约定为 wxyz。

## 3. 只读检查

```bash
python -m Deploy.sim2real --bundle bundles/dance \
  --interface enp3s0 --imu-frame torso --seconds 10
```

把网卡和 IMU 选项换成实际配置。默认只订阅 `rt/lowstate` 并检查数据，不创建 motor-command publisher。应看到实测关节速度、mode 和按键位持续更新。没有数据或数据超过 100 ms 未更新会报错。检查静止时速度接近零，转动机器人时 IMU 的方向与选择相符。

## 4. 执行一次动作

```bash
python -m Deploy.sim2real --bundle bundles/dance \
  --interface enp3s0 --imu-frame torso --execute
```

`--execute` 会发送实际电机指令。启动前要求：其他运动控制器已经由操作员释放；机器人已在支持条件下接近参考第一帧（任一关节误差不超过 0.2 rad、anchor 朝向误差不超过 0.25 rad）；关节速度不超过 0.3 rad/s；遥控按键全部释放。不符合条件直接报错，不自动摆到首帧。

策略按包内频率更新，低层 PD 目标以 500 Hz 发布。SDK motor ID 顺序是左腿 0–5、右腿 6–11、腰 12–14、左臂 15–21、右臂 22–28；运行时按关节名映射策略顺序。

## 5. 停止与动作结束

以下情况停止主动跟踪：参考帧耗尽、Ctrl+C、任意遥控按键、状态/目标超时、策略错过周期、base 倾角超过 0.8 rad、目标与实测任一关节差超过 0.5 rad、推理异常。

结束路径发送 0.2 秒 `kp=0、kd=3` 的阻尼命令，然后停止发布；不会自动回放或恢复其他控制器。阻尼模式不负责站立平衡，操作员必须继续支持机器人，并按设备流程接管。网络断开后的实际行为由机器人固件决定，软件看门狗不代替物理急停。

当前真机目标使用导出的 PD；固件承担低层力矩限制，必须确认固件限制与设备型号一致。本入口不是硬实时进程。首次实机验证应逐项记录接口、IMU frame、固件版本、周期延迟、启动/停止行为和短动作结果，再扩展到完整动作。

## 6. 开发与离线检查

`Deploy/tests/test_deploy.py` 验证 pelvis/torso 姿态变换一致性、154 维观测、ONNX 和 MuJoCo 接口。它没有模拟网络失联或真实电机响应。对硬件入口的任何修改，都需要重新做上面的只读、启动、遥控停止和超时验证，不能把 CPU 测试通过当成实机验收。
