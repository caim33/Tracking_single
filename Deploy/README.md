# 单动作策略部署

本目录加载 `RL_envs` 导出的一个策略包，按参考动作从第 0 帧顺序推理，参考结束后退出。默认不循环、不切换其他动作。

- [策略包、154 维观测、MuJoCo 运行及排错](../docs/05_deploy.md)
- [G1 通信、IMU、只读检查和单次执行](../docs/06_real_robot.md)
- [逐文件职责和 API 索引](../docs/code_reference.md)
- [验证范围与待验收项目](../docs/07_validation.md)

完成安装和策略导出后，在仓库根目录运行：

```bash
python -m Deploy.sim2sim --bundle bundles/dance --headless --steps 100
python -m Deploy.sim2sim --bundle bundles/dance
```

将 `bundles/dance` 换成实际导出目录；其中应同时包含 `policy.onnx`、`motion.npz` 和 `manifest.json`。第一条命令最多运行 100 个策略周期，第二条打开 MuJoCo 窗口执行完整参考动作。

`runtime.py` 负责包校验、观测排列和推理；`export.py` 由训练入口调用；`sim2sim.py` 实现仿真控制；`robot_state.py` 与 `sim2real.py` 实现 G1 状态转换和单次动作控制。`reference/` 的原 C++ 头文件用于接口对照，实际部署入口为本目录 Python 模块。

真机入口默认只读，只有显式传入 `--execute` 才会发布电机指令。执行前的准备、首帧核对和结束后的阻尼行为必须按真机教程操作。当前已通过 CPU 接口与 MuJoCo 短程检查；完整 GPU 管线、真实策略跟踪效果和真机控制尚待对应设备验收。
