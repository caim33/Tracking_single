# 逐文件教程与 API 参考

本索引覆盖 **157 个代码文件**。由 `python tools/audit_docs.py --write` 生成并随代码提交。

先阅读对应阶段教程完成环境、输入、运行、输出检查和排错，再进入函数或配置。库模块不应逐个直接运行。
API 索引来自语法树；命令参数来自显式 add_argument 定义。动态框架参数在阶段教程解释。索引覆盖不等于 GPU/真机验收。

## `Deploy/__init__.py`

[源码](../Deploy/__init__.py) · [使用教程](05_deploy.md) · 内容指纹 `5ece58365c11`

职责：单动作策略包、观测、PD 与仿真接口。

模块说明：Single-motion ONNX deployment. See docs/05_deploy.md.

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Deploy/export.py`

[源码](../Deploy/export.py) · [使用教程](05_deploy.md) · 内容指纹 `eb4334faf769`

职责：单动作策略包、观测、PD 与仿真接口。

模块说明：Export policy/reference/control parameters together. See docs/04_training.md.

接口与职责：

- `export_bundle(env, runner, motion_path, output, task, action_clip)` — Derive mapping, offsets, gains and scaling from the running training task.

## `Deploy/reference/joint_actions.h`

[源码](../Deploy/reference/joint_actions.h) · [使用教程](05_deploy.md) · 内容指纹 `f4b401cccb86`

职责：单动作策略包、观测、PD 与仿真接口。

使用方式：原 deploy 接口参考，当前 Python 单动作控制路径不直接编译此文件。依赖与替代入口见 deploy 教程。

## `Deploy/reference/observations.h`

[源码](../Deploy/reference/observations.h) · [使用教程](05_deploy.md) · 内容指纹 `25b663543783`

职责：单动作策略包、观测、PD 与仿真接口。

使用方式：原 deploy 接口参考，当前 Python 单动作控制路径不直接编译此文件。依赖与替代入口见 deploy 教程。

## `Deploy/reference/unitree_articulation.h`

[源码](../Deploy/reference/unitree_articulation.h) · [使用教程](05_deploy.md) · 内容指纹 `3ded89029b63`

职责：单动作策略包、观测、PD 与仿真接口。

使用方式：原 deploy 接口参考，当前 Python 单动作控制路径不直接编译此文件。依赖与替代入口见 deploy 教程。

## `Deploy/robot_state.py`

[源码](../Deploy/robot_state.py) · [使用教程](06_real_robot.md) · 内容指纹 `1d6ee1a1efc9`

职责：实测电机/IMU 到训练坐标系的转换。

模块说明：Convert Unitree motor/IMU measurements to the actor's pelvis/torso frames.

接口与职责：

- `class RobotState()` — Use migrated robot FK, including waist motion, to resolve the anchor IMU.
- `RobotState.__init__(self, joint_names, anchor='torso_link', robot_xml=ROBOT_XML)` — 行为见对应阶段教程及源码。
- `RobotState.estimate(self, q, dq, imu_wxyz, gyro, imu_frame)` — Return pelvis gyro and world anchor quaternion from pelvis or torso IMU.

## `Deploy/runtime.py`

[源码](../Deploy/runtime.py) · [使用教程](05_deploy.md) · 内容指纹 `ae08f2961159`

职责：单动作策略包、观测、PD 与仿真接口。

模块说明：Training-identical single-motion observations and ONNX actions.

接口与职责：

- `rotation(wxyz)` — Convert a unit wxyz quaternion to SciPy's xyzw rotation convention.
- `observation(ref_q, ref_dq, ref_anchor, robot_anchor, base_gyro, q, dq, default_q, default_dq, previous_action)` — 154 values; rotation uses matrix[:, :2].reshape(-1), matching Isaac.
- `validate_manifest(config)` — Reject incompatible models before inference or any control operation.
- `class TrackingPolicy()` — One bundle binds policy.onnx, motion.npz, checksums and a named manifest.
- `TrackingPolicy.__init__(self, bundle)` — 行为见对应阶段教程及源码。
- `TrackingPolicy.reset(self)` — Clear previous action; called once before starting frame zero.
- `TrackingPolicy.step(self, frame, q, dq, base_gyro, anchor_wxyz)` — Consume one reference frame; refuse wraparound at the motion boundary.

## `Deploy/sim2real.py`

[源码](../Deploy/sim2real.py) · [使用教程](06_real_robot.md) · 内容指纹 `8f9a91cdd7a1`

职责：SDK2 单次动作发布、只读检查和停控。

模块说明：G1 29-DoF single-motion transport; read-only unless --execute is supplied.

接口与职责：

- `main()` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `--bundle` — required=True
- `--interface` — required=True; help='Robot Ethernet interface, e.g. enp3s0'
- `--imu-frame` — required=True; choices=['pelvis', 'torso']; help='Verify against your firmware'
- `--execute` — action='store_true'; help='Enable low-level motor commands after startup checks'
- `--seconds` — default=10; help='Read-only diagnostic duration'

## `Deploy/sim2sim.py`

[源码](../Deploy/sim2sim.py) · [使用教程](05_deploy.md) · 内容指纹 `812d1c97579f`

职责：单动作策略包、观测、PD 与仿真接口。

模块说明：Run a single reference policy in MuJoCo, with CPU ONNX inference.

接口与职责：

- `simulation_model(xml_path, dt=0.005)` — Keep the migrated GMR model and add ground/light for dynamic playback.
- `main()` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `--bundle` — required=True
- `--robot-xml` — default=ROBOT_XML
- `--headless` — action='store_true'
- `--steps` — help='Optional upper bound; defaults to full reference'
- `--output` — help='Optional .npz trace: observations, q, targets, root height'

## `pipeline/__init__.py`

[源码](../pipeline/__init__.py) · [使用教程](03_motion.md) · 内容指纹 `89b6a7ed6026`

职责：命名动作、时间采样、四元数和正向运动学。

模块说明：Portable motion conversion and validation. See docs/03_motion.md.

使用方式：包注册、常量或参数配置，由上级模块导入。

## `pipeline/convert.py`

[源码](../pipeline/convert.py) · [使用教程](03_motion.md) · 内容指纹 `471c30a43de2`

职责：命名动作、时间采样、四元数和正向运动学。

模块说明：Convert trusted GMR pickle to a named 50 Hz training archive; see docs/03_motion.md.

接口与职责：

- `main()` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `--input` — required=True; help='Trusted local GMR .pkl (pickle executes code)'
- `--output` — required=True; help='Output .npz archive'
- `--fps` — default=50; help='Must equal tracking control rate (default 50 Hz)'
- `--robot-xml` — default=ROBOT_XML

## `pipeline/motion.py`

[源码](../pipeline/motion.py) · [使用教程](03_motion.md) · 内容指纹 `116d2767314d`

职责：命名动作、时间采样、四元数和正向运动学。

模块说明：Named, validated tracking archive shared by training and deployment.

接口与职责：

- `validate_motion(data)` — Reject ambiguous names, corrupt quaternions, mismatched shapes and NaNs.
- `load_motion(path)` — Load a non-pickle NPZ, close its descriptor, then validate its contract.
- `name_indices(actual, requested)` — Map names explicitly; never assume MuJoCo and Isaac use the same order.
- `resample_qpos(root_pos, root_xyzw, joints, source_fps, target_fps)` — Resample on a seconds-based grid without extending beyond the last frame.
- `world_angular_velocity(quaternions, fps)` — Differentiate wxyz rotations in the world frame, with sign-invariant SO(3) differences.
- `qpos_to_motion(qpos, fps, model)` — Evaluate every named link using MuJoCo FK; preserve explicit joint order.

## `Retargeting/GMR/__init__.py`

[源码](../Retargeting/GMR/__init__.py) · [使用教程](02_video.md) · 内容指纹 `e3b0c44298fc`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GMR/general_motion_retargeting/__init__.py`

[源码](../Retargeting/GMR/general_motion_retargeting/__init__.py) · [使用教程](02_video.md) · 内容指纹 `b1c238b2fd52`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GMR/general_motion_retargeting/data_loader.py`

[源码](../Retargeting/GMR/general_motion_retargeting/data_loader.py) · [使用教程](02_video.md) · 内容指纹 `3811cd168bc0`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `load_robot_motion(motion_file)` — Load robot motion data from a pickle file.

## `Retargeting/GMR/general_motion_retargeting/kinematics_model.py`

[源码](../Retargeting/GMR/general_motion_retargeting/kinematics_model.py) · [使用教程](02_video.md) · 内容指纹 `869e1bd0d0be`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class Joint()` — 行为见对应阶段教程及源码。
- `Joint.__init__(self, name, dof_dim, axis)` — 行为见对应阶段教程及源码。
- `Joint.set_dof_idx(self, dof_idx)` — 行为见对应阶段教程及源码。
- `Joint.dof_to_rot(self, dof)` — 行为见对应阶段教程及源码。
- `Joint.rot_to_dof(self, rot)` — 行为见对应阶段教程及源码。
- `Joint.dof_dim(self)` — 行为见对应阶段教程及源码。
- `Joint.name(self)` — 行为见对应阶段教程及源码。
- `Joint.dof_idx(self)` — 行为见对应阶段教程及源码。
- `class KinematicsModel()` — 行为见对应阶段教程及源码。
- `KinematicsModel.__init__(self, file_path, device)` — 行为见对应阶段教程及源码。
- `KinematicsModel._build_kinematics_model(self)` — 行为见对应阶段教程及源码。
- `KinematicsModel._parse_xml(self)` — 行为见对应阶段教程及源码。
- `KinematicsModel._set_dof_indices(self)` — 行为见对应阶段教程及源码。
- `KinematicsModel.dof_to_rot(self, dof)` — 行为见对应阶段教程及源码。
- `KinematicsModel.rot_to_dof(self, rot)` — 行为见对应阶段教程及源码。
- `KinematicsModel.convert_local_rot_to_global(self, local_rot)` — 行为见对应阶段教程及源码。
- `KinematicsModel.forward_kinematics(self, root_pos, root_rot, dof_pos, fitted_shape=None)` — 行为见对应阶段教程及源码。
- `KinematicsModel.get_body_idx(self, body_name)` — 行为见对应阶段教程及源码。
- `KinematicsModel.body_names(self)` — 行为见对应阶段教程及源码。
- `KinematicsModel.num_dof(self)` — 行为见对应阶段教程及源码。
- `KinematicsModel.num_joint(self)` — 行为见对应阶段教程及源码。
- `KinematicsModel.joint_dof_idx(self)` — 行为见对应阶段教程及源码。
- `KinematicsModel.parent_indices(self)` — 行为见对应阶段教程及源码。
- `KinematicsModel.get_parent_idx(self, idx)` — 行为见对应阶段教程及源码。
- `KinematicsModel.get_dof_limits(self)` — 行为见对应阶段教程及源码。

## `Retargeting/GMR/general_motion_retargeting/motion_retarget.py`

[源码](../Retargeting/GMR/general_motion_retargeting/motion_retarget.py) · [使用教程](02_video.md) · 内容指纹 `5c3347df2333`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class GeneralMotionRetargeting()` — General Motion Retargeting (GMR).
- `GeneralMotionRetargeting.__init__(self, src_human: str, tgt_robot: str, actual_human_height: float=None, solver: str='daqp', damping: float=0.5, verbose: bool=True, use_velocity_limit: bool=False) -> None` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.setup_retarget_configuration(self)` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.update_targets(self, human_data, offset_to_ground=False)` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.retarget(self, human_data, offset_to_ground=False)` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.error1(self)` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.error2(self)` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.to_numpy(self, human_data)` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.scale_human_data(self, human_data, human_root_name, human_scale_table)` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.offset_human_data(self, human_data, pos_offsets, rot_offsets)` — the pos offsets are applied in the local frame
- `GeneralMotionRetargeting.offset_human_data_to_ground(self, human_data)` — find the lowest point of the human data and offset the human data to the ground
- `GeneralMotionRetargeting.set_ground_offset(self, ground_offset)` — 行为见对应阶段教程及源码。
- `GeneralMotionRetargeting.apply_ground_offset(self, human_data)` — 行为见对应阶段教程及源码。

## `Retargeting/GMR/general_motion_retargeting/params.py`

[源码](../Retargeting/GMR/general_motion_retargeting/params.py) · [使用教程](02_video.md) · 内容指纹 `ab6beccf980b`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`HERE`, `IK_CONFIG_ROOT`, `ASSET_ROOT`, `ROBOT_XML_DICT`, `IK_CONFIG_DICT`, `ROBOT_BASE_DICT`, `VIEWER_CAM_DISTANCE_DICT`.

## `Retargeting/GMR/general_motion_retargeting/robot_motion_viewer.py`

[源码](../Retargeting/GMR/general_motion_retargeting/robot_motion_viewer.py) · [使用教程](02_video.md) · 内容指纹 `802c3fb659f0`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `draw_frame(pos, mat, v, size, joint_name=None, orientation_correction=R.from_euler('xyz', [0, 0, 0]), pos_offset=np.array([0, 0, 0]))` — 行为见对应阶段教程及源码。
- `class RobotMotionViewer()` — 行为见对应阶段教程及源码。
- `RobotMotionViewer.__init__(self, robot_type, camera_follow=True, motion_fps=30, transparent_robot=0, record_video=False, video_path=None, video_width=640, video_height=480)` — 行为见对应阶段教程及源码。
- `RobotMotionViewer.step(self, root_pos, root_rot, dof_pos, human_motion_data=None, show_human_body_name=False, human_point_scale=0.1, human_pos_offset=np.array([0.0, 0.0, 0]), rate_limit=True, follow_camera=True)` — by default visualize robot motion. also support visualize human motion by providing human_motion_data, to compare with robot motion.
- `RobotMotionViewer.close(self)` — 行为见对应阶段教程及源码。

## `Retargeting/GMR/general_motion_retargeting/rot_utils.py`

[源码](../Retargeting/GMR/general_motion_retargeting/rot_utils.py) · [使用教程](02_video.md) · 内容指纹 `e968bbc7a6c3`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `quatToEuler(quat)` — 将四元数转换为欧拉角(roll, pitch, yaw)。
- `quat_mul_np(x, y, scalar_first=True)` — Performs quaternion multiplication on arrays of quaternions :param x: tensor of quaternions of shape (..., 4) :param y: tensor of quaternions of shape (..., 4) :param scalar_first: True if quaternions are in [w, x, y, z] format :return: quaternion multiplication result in same format
- `quat_rotate_inverse(q, v)` — 将向量 v 以四元数 q 的逆旋转进行变换。 为保持一致，以下代码与原脚本中的实现相同。
- `quat_rotate_inverse_torch(q, v, scalar_first=True)` — 行为见对应阶段教程及源码。
- `quat_rotate_inverse_np(q, v, scalar_first=True)` — 行为见对应阶段教程及源码。
- `euler_from_quaternion_torch(quat_angle, scalar_first=True)` — Convert a quaternion into euler angles (roll, pitch, yaw) roll is rotation around x in radians (counterclockwise) pitch is rotation around y in radians (counterclockwise) yaw is rotation around z in radians (counterclockwise)
- `euler_from_quaternion_np(quat, scalar_first=True)` — 行为见对应阶段教程及源码。
- `quat_diff_np(q1, q2, scalar_first=True)` — 行为见对应阶段教程及源码。

## `Retargeting/GMR/general_motion_retargeting/torch_utils.py`

[源码](../Retargeting/GMR/general_motion_retargeting/torch_utils.py) · [使用教程](02_video.md) · 内容指纹 `7f135802a296`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `euler_from_quaternion(quat_angle)` — Convert a quaternion into euler angles (roll, pitch, yaw) roll is rotation around x in radians (counterclockwise) pitch is rotation around y in radians (counterclockwise) yaw is rotation around z in radians (counterclockwise)
- `normalize(x, eps: float=1e-09)` — 行为见对应阶段教程及源码。
- `normalize_angle(x)` — 行为见对应阶段教程及源码。
- `quat_rotate(q, v)` — 行为见对应阶段教程及源码。
- `quat_rotate_inverse(q, v)` — 行为见对应阶段教程及源码。
- `quat_from_euler_xyz(roll, pitch, yaw)` — 行为见对应阶段教程及源码。
- `quat_unit(a)` — 行为见对应阶段教程及源码。
- `quat_from_angle_axis(angle, axis)` — 行为见对应阶段教程及源码。
- `quat_mul(a, b)` — 行为见对应阶段教程及源码。
- `quat_conjugate(a)` — 行为见对应阶段教程及源码。
- `quat_to_angle_axis(q)` — 行为见对应阶段教程及源码。
- `angle_axis_to_exp_map(angle, axis)` — 行为见对应阶段教程及源码。
- `quat_to_exp_map(q)` — 行为见对应阶段教程及源码。
- `quat_to_tan_norm(q)` — 行为见对应阶段教程及源码。
- `euler_xyz_to_exp_map(roll, pitch, yaw)` — 行为见对应阶段教程及源码。
- `exp_map_to_angle_axis(exp_map)` — 行为见对应阶段教程及源码。
- `exp_map_to_quat(exp_map)` — 行为见对应阶段教程及源码。
- `slerp(q0, q1, t)` — 行为见对应阶段教程及源码。
- `slerp2(q0, q1, t)` — 行为见对应阶段教程及源码。
- `calc_heading(q)` — 行为见对应阶段教程及源码。
- `calc_heading_quat(q)` — 行为见对应阶段教程及源码。
- `calc_heading_quat_inv(q)` — 行为见对应阶段教程及源码。
- `quat_pos(x)` — 行为见对应阶段教程及源码。
- `quat_to_axis_angle(q)` — 行为见对应阶段教程及源码。
- `quat_diff(q0, q1)` — 行为见对应阶段教程及源码。
- `quat_diff_angle(q0, q1)` — 行为见对应阶段教程及源码。
- `axis_angle_to_quat(axis, angle)` — 行为见对应阶段教程及源码。

## `Retargeting/GMR/general_motion_retargeting/utils/__init__.py`

[源码](../Retargeting/GMR/general_motion_retargeting/utils/__init__.py) · [使用教程](02_video.md) · 内容指纹 `e3b0c44298fc`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GMR/general_motion_retargeting/utils/lafan1.py`

[源码](../Retargeting/GMR/general_motion_retargeting/utils/lafan1.py) · [使用教程](02_video.md) · 内容指纹 `83c549b420cd`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `load_lafan1_file(bvh_file)` — Must return a dictionary with the following structure: {     "Hips": (position, orientation),     "Spine": (position, orientation),     ... }

## `Retargeting/GMR/general_motion_retargeting/utils/lafan_vendor/__init__.py`

[源码](../Retargeting/GMR/general_motion_retargeting/utils/lafan_vendor/__init__.py) · [使用教程](02_video.md) · 内容指纹 `e3b0c44298fc`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GMR/general_motion_retargeting/utils/lafan_vendor/extract.py`

[源码](../Retargeting/GMR/general_motion_retargeting/utils/lafan_vendor/extract.py) · [使用教程](02_video.md) · 内容指纹 `861165a4fbac`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class Anim(object)` — A very basic animation object
- `Anim.__init__(self, quats, pos, offsets, parents, bones)` — :param quats: local quaternions tensor :param pos: local positions tensor :param offsets: local joint offsets :param parents: bone hierarchy :param bones: bone names
- `read_bvh(filename, start=None, end=None, order=None)` — Reads a BVH file and extracts animation information.
- `get_lafan1_set(bvh_path, actors, window=50, offset=20)` — Extract the same test set as in the article, given the location of the BVH files.
- `get_train_stats(bvh_folder, train_set)` — Extract the same training set as in the paper in order to compute the normalizing statistics :return: Tuple of (local position mean vector, local position standard deviation vector, local joint offsets tensor)

## `Retargeting/GMR/general_motion_retargeting/utils/lafan_vendor/utils.py`

[源码](../Retargeting/GMR/general_motion_retargeting/utils/lafan_vendor/utils.py) · [使用教程](02_video.md) · 内容指纹 `9d15e75bb4f5`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `length(x, axis=-1, keepdims=True)` — Computes vector norm along a tensor axis(axes)
- `normalize(x, axis=-1, eps=1e-08)` — Normalizes a tensor over some axis (axes)
- `quat_normalize(x, eps=1e-08)` — Normalizes a quaternion tensor
- `angle_axis_to_quat(angle, axis)` — Converts from and angle-axis representation to a quaternion representation
- `euler_to_quat(e, order='zyx')` — Converts from an euler representation to a quaternion representation
- `quat_inv(q)` — Inverts a tensor of quaternions
- `quat_fk(lrot, lpos, parents)` — Performs Forward Kinematics (FK) on local quaternions and local positions to retrieve global representations
- `quat_ik(grot, gpos, parents)` — Performs Inverse Kinematics (IK) on global quaternions and global positions to retrieve local representations
- `quat_mul(x, y)` — Performs quaternion multiplication on arrays of quaternions
- `quat_mul_vec(q, x)` — Performs multiplication of an array of 3D vectors by an array of quaternions (rotation).
- `quat_slerp(x, y, a)` — Performs spherical linear interpolation (SLERP) between x and y, with proportion a
- `quat_between(x, y)` — Quaternion rotations between two 3D-vector arrays
- `interpolate_local(lcl_r_mb, lcl_q_mb, n_past, n_future)` — Performs interpolation between 2 frames of an animation sequence.
- `remove_quat_discontinuities(rotations)` — Removing quat discontinuities on the time dimension (removing flips)
- `rotate_at_frame(X, Q, parents, n_past=10)` — Re-orients the animation data according to the last frame of past context.
- `extract_feet_contacts(pos, lfoot_idx, rfoot_idx, velfactor=0.02)` — Extracts binary tensors of feet contacts

## `Retargeting/GMR/general_motion_retargeting/utils/smpl.py`

[源码](../Retargeting/GMR/general_motion_retargeting/utils/smpl.py) · [使用教程](02_video.md) · 内容指纹 `a188049b1ed8`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `load_smpl_file(smpl_file)` — 行为见对应阶段教程及源码。
- `load_smplx_file(smplx_file, smplx_body_model_path)` — 行为见对应阶段教程及源码。
- `load_gvhmr_pred_file(gvhmr_pred_file, smplx_body_model_path)` — 行为见对应阶段教程及源码。
- `get_smplx_data(smplx_data, body_model, smplx_output, curr_frame)` — Must return a dictionary with the following structure: {     "Hips": (position, orientation),     "Spine": (position, orientation),     ... }
- `slerp(rot1, rot2, t)` — Spherical linear interpolation between two rotations.
- `get_smplx_data_offline_fast(smplx_data, body_model, smplx_output, tgt_fps=30)` — Must return a dictionary with the following structure: {     "Hips": (position, orientation),     "Spine": (position, orientation),     ... }
- `get_gvhmr_data_offline_fast(smplx_data, body_model, smplx_output, tgt_fps=30)` — Must return a dictionary with the following structure: {     "Hips": (position, orientation),     "Spine": (position, orientation),     ... }

## `Retargeting/GMR/scripts/gvhmr_to_robot.py`

[源码](../Retargeting/GMR/scripts/gvhmr_to_robot.py) · [使用教程](02_video.md) · 内容指纹 `8ad24e99c5d9`

职责：人体恢复、重定向及其内部数学/网络模块。

模块说明：Retarget every GVHMR frame to G1; headless CLI. See docs/02_video.md.

接口与职责：

- `main()` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `--gvhmr_pred_file` — required=True
- `--save_path` — required=True
- `--robot` — default='unitree_g1'; choices=['unitree_g1']
- `--body-models` — default=Path(__file__).resolve().parents[1] / 'assets/body_models'
- `--headless` — action='store_true'
- `--rate_limit` — action='store_true'

## `Retargeting/GMR/scripts/vis_robot_motion.py`

[源码](../Retargeting/GMR/scripts/vis_robot_motion.py) · [使用教程](02_video.md) · 内容指纹 `d7c70196c250`

职责：人体恢复、重定向及其内部数学/网络模块。

模块说明：Preview one GMR motion and close the viewer/recorder cleanly. See docs/02_video.md.

接口与职责：

- `main()` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `--robot` — default='unitree_g1'; choices=['unitree_g1']
- `--robot_motion_path` — required=True
- `--record_video` — action='store_true'
- `--video_path` — default=Path('videos/example.mp4')
- `--loop` — action='store_true'; help='Repeat until Ctrl+C; default is one pass'

## `Retargeting/GMR/setup.py`

[源码](../Retargeting/GMR/setup.py) · [使用教程](02_video.md) · 内容指纹 `15dbddb85731`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/__init__.py) · [使用教程](02_video.md) · 内容指纹 `e8d5a0266592`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `os_chdir_to_proj_root()` — useful for running notebooks in different directories.

## `Retargeting/GVHMR/hmr4d/build_gvhmr.py`

[源码](../Retargeting/GVHMR/hmr4d/build_gvhmr.py) · [使用教程](02_video.md) · 内容指纹 `b89c4ebbc104`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `build_gvhmr_demo()` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/configs/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/configs/__init__.py) · [使用教程](02_video.md) · 内容指纹 `7607de90bd8c`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `register_store_gvhmr()` — Register group options to MainStore
- `parse_args_to_cfg()` — Use minimal Hydra API to parse args and return cfg. This function don't do _run_hydra which create log file hierarchy.

命令行参数（运行所在目录与完整例子见上方教程）：

- `--config-name, -cn` — default='train'
- `overrides` — help='Any key=value arguments to override config values (use dots for.nested=overrides)'

## `Retargeting/GVHMR/hmr4d/model/gvhmr/gvhmr_pl_demo.py`

[源码](../Retargeting/GVHMR/hmr4d/model/gvhmr/gvhmr_pl_demo.py) · [使用教程](02_video.md) · 内容指纹 `0e866c8f486b`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class DemoPL(pl.LightningModule)` — 行为见对应阶段教程及源码。
- `DemoPL.__init__(self, pipeline)` — 行为见对应阶段教程及源码。
- `DemoPL.predict(self, data, static_cam=False)` — auto add batch dim data: {     "length": int, or Torch.Tensor,     "kp2d": (F, 3)     "bbx_xys": (F, 3)     "K_fullimg": (F, 3, 3)     "cam_angvel": (F, 3)     "f_imgseq": (F, 3, 256, 256) }
- `DemoPL.load_pretrained_model(self, ckpt_path)` — Load pretrained checkpoint, and assign each weight to the corresponding part.

## `Retargeting/GVHMR/hmr4d/model/gvhmr/pipeline/gvhmr_pipeline.py`

[源码](../Retargeting/GVHMR/hmr4d/model/gvhmr/pipeline/gvhmr_pipeline.py) · [使用教程](02_video.md) · 内容指纹 `c99d514136d3`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class Pipeline(nn.Module)` — 行为见对应阶段教程及源码。
- `Pipeline.__init__(self, args, args_denoiser3d, **kwargs)` — 行为见对应阶段教程及源码。
- `Pipeline.forward(self, inputs, train=False, postproc=False, static_cam=False)` — 行为见对应阶段教程及源码。
- `randomly_set_null_condition(f_condition, uncond_prob=0.1)` — Conditions are in shape (B, L, *)
- `compute_extra_incam_loss(inputs, outputs, ppl)` — 行为见对应阶段教程及源码。
- `compute_extra_global_loss(inputs, outputs, ppl)` — 行为见对应阶段教程及源码。
- `get_smpl_params_w_Rt_v2(global_orient_gv, local_transl_vel, global_orient_c, cam_angvel)` — Get global R,t in GV0(ay) Args:     cam_angvel: (B, L, 6), defined as R @ R_{w2c}^{t} = R_{w2c}^{t+1}

## `Retargeting/GVHMR/hmr4d/model/gvhmr/utils/endecoder.py`

[源码](../Retargeting/GVHMR/hmr4d/model/gvhmr/utils/endecoder.py) · [使用教程](02_video.md) · 内容指纹 `dd26cda551ec`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class EnDecoder(nn.Module)` — 行为见对应阶段教程及源码。
- `EnDecoder.__init__(self, stats_name='DEFAULT_01', noise_pose_k=10)` — 行为见对应阶段教程及源码。
- `EnDecoder.get_noisyobs(self, data, return_type='r6d')` — Noisy observation contains local pose with noise Args:     data (dict):         body_pose: (B, L, J*3) or (B, L, J, 3) Returns:     noisy_bosy_pose: (B, L, J, 6) or (B, L, J, 3) or (B, L, 3, 3) depends on return_type
- `EnDecoder.normalize_body_pose_r6d(self, body_pose_r6d)` — body_pose_r6d: (B, L, {J*6}/{J, 6}) ->  (B, L, J*6)
- `EnDecoder.fk_v2(self, body_pose, betas, global_orient=None, transl=None, get_intermediate=False)` — Args:     body_pose: (B, L, 63)     betas: (B, L, 10)     global_orient: (B, L, 3) Returns:     joints: (B, L, 22, 3)
- `EnDecoder.get_local_pos(self, betas)` — 行为见对应阶段教程及源码。
- `EnDecoder.encode(self, inputs)` — definition: {         body_pose_r6d,  # (B, L, (J-1)*6) -> 0:126         betas, # (B, L, 10) -> 126:136         global_orient_r6d,  # (B, L, 6) -> 136:142  incam         global_orient_gv_r6d: # (B, L, 6) -> 142:148  gv         local_transl_vel,  # (B, L, 3) -> 148:151, smpl-coord     }
- `EnDecoder.encode_translw(self, inputs)` — definition: {         body_pose_r6d,  # (B, L, (J-1)*6) -> 0:126         betas, # (B, L, 10) -> 126:136         global_orient_r6d,  # (B, L, 6) -> 136:142  incam         global_orient_gv_r6d: # (B, L, 6) -> 142:148  gv         local_transl_vel,  # (B, L, 3) -> 148:151, smpl-coord     }
- `EnDecoder.decode_translw(self, x_norm)` — 行为见对应阶段教程及源码。
- `EnDecoder.decode(self, x_norm)` — x_norm: (B, L, C)

## `Retargeting/GVHMR/hmr4d/model/gvhmr/utils/postprocess.py`

[源码](../Retargeting/GVHMR/hmr4d/model/gvhmr/utils/postprocess.py) · [使用教程](02_video.md) · 内容指纹 `4125839f3925`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `pp_static_joint(outputs, endecoder: EnDecoder)` — 行为见对应阶段教程及源码。
- `pp_static_joint_cam(outputs, endecoder: EnDecoder)` — Use static joint and static camera assumption to postprocess the global transl
- `process_ik(outputs, endecoder)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/model/gvhmr/utils/stats_compose.py`

[源码](../Retargeting/GVHMR/hmr4d/model/gvhmr/utils/stats_compose.py) · [使用教程](02_video.md) · 内容指纹 `102d34db55d5`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `compose(targets, sources)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/network/base_arch/embeddings/rotary_embedding.py`

[源码](../Retargeting/GVHMR/hmr4d/network/base_arch/embeddings/rotary_embedding.py) · [使用教程](02_video.md) · 内容指纹 `590f00248bc5`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `rotate_half(x)` — 行为见对应阶段教程及源码。
- `apply_rotary_emb(freqs, t, start_index=0, scale=1.0, seq_dim=-2)` — 行为见对应阶段教程及源码。
- `get_encoding(d_model, max_seq_len=4096)` — Return: (L, D)
- `class ROPE(nn.Module)` — Minimal impl of a lang-style positional encoding.
- `ROPE.__init__(self, d_model, max_seq_len=4096)` — 行为见对应阶段教程及源码。
- `ROPE.rotate_queries_or_keys(self, x)` — Args:     x : (B, H, L, D) Returns:     rotated_x: (B, H, L, D)

## `Retargeting/GVHMR/hmr4d/network/base_arch/transformer/encoder_rope.py`

[源码](../Retargeting/GVHMR/hmr4d/network/base_arch/transformer/encoder_rope.py) · [使用教程](02_video.md) · 内容指纹 `ee979aff549f`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class RoPEAttention(nn.Module)` — 行为见对应阶段教程及源码。
- `RoPEAttention.__init__(self, embed_dim, num_heads, dropout=0.1)` — 行为见对应阶段教程及源码。
- `RoPEAttention.forward(self, x, attn_mask=None, key_padding_mask=None)` — 行为见对应阶段教程及源码。
- `class EncoderRoPEBlock(nn.Module)` — 行为见对应阶段教程及源码。
- `EncoderRoPEBlock.__init__(self, hidden_size, num_heads, mlp_ratio=4.0, dropout=0.1, **block_kwargs)` — 行为见对应阶段教程及源码。
- `EncoderRoPEBlock.forward(self, x, attn_mask=None, tgt_key_padding_mask=None)` — 行为见对应阶段教程及源码。
- `EncoderRoPEBlock._sa_block(self, x, attn_mask=None, key_padding_mask=None)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/network/base_arch/transformer/layer.py`

[源码](../Retargeting/GVHMR/hmr4d/network/base_arch/transformer/layer.py) · [使用教程](02_video.md) · 内容指纹 `17394bafe0a8`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `zero_module(module)` — Zero out the parameters of a module and return it.

## `Retargeting/GVHMR/hmr4d/network/gvhmr/relative_transformer.py`

[源码](../Retargeting/GVHMR/hmr4d/network/gvhmr/relative_transformer.py) · [使用教程](02_video.md) · 内容指纹 `436fc3d71232`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class NetworkEncoderRoPE(nn.Module)` — 行为见对应阶段教程及源码。
- `NetworkEncoderRoPE.__init__(self, output_dim=151, max_len=120, cliffcam_dim=3, cam_angvel_dim=6, imgseq_dim=1024, latent_dim=512, num_layers=12, num_heads=8, mlp_ratio=4.0, pred_cam_dim=3, static_conf_dim=6, dropout=0.1, avgbeta=True)` — 行为见对应阶段教程及源码。
- `NetworkEncoderRoPE._build_condition_embedder(self)` — 行为见对应阶段教程及源码。
- `NetworkEncoderRoPE.forward(self, length, obs=None, f_cliffcam=None, f_cam_angvel=None, f_imgseq=None)` — Args:     x: None we do not use it     timesteps: (B,)     length: (B), valid length of x, if None then use x.shape[2]     f_imgseq: (B, L, C)     f_cliffcam: (B, L, 3), CLIFF-Cam parameters (bbx-detection in the full-image)     f_noisyobs: (B, L, C), nosiy pose observation     f_cam_angvel: (B, L, 6), Camera angular velocity

## `Retargeting/GVHMR/hmr4d/network/hmr2/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/__init__.py) · [使用教程](02_video.md) · 内容指纹 `4cd96c68e3cc`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `load_hmr2(checkpoint_path=HMR2A_CKPT)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/network/hmr2/components/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/components/__init__.py) · [使用教程](02_video.md) · 内容指纹 `e3b0c44298fc`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/network/hmr2/components/pose_transformer.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/components/pose_transformer.py) · [使用教程](02_video.md) · 内容指纹 `36419f21f247`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `exists(val)` — 行为见对应阶段教程及源码。
- `default(val, d)` — 行为见对应阶段教程及源码。
- `class PreNorm(nn.Module)` — 行为见对应阶段教程及源码。
- `PreNorm.__init__(self, dim: int, fn: Callable, norm: str='layer', norm_cond_dim: int=-1)` — 行为见对应阶段教程及源码。
- `PreNorm.forward(self, x: torch.Tensor, *args, **kwargs)` — 行为见对应阶段教程及源码。
- `class FeedForward(nn.Module)` — 行为见对应阶段教程及源码。
- `FeedForward.__init__(self, dim, hidden_dim, dropout=0.0)` — 行为见对应阶段教程及源码。
- `FeedForward.forward(self, x)` — 行为见对应阶段教程及源码。
- `class Attention(nn.Module)` — 行为见对应阶段教程及源码。
- `Attention.__init__(self, dim, heads=8, dim_head=64, dropout=0.0)` — 行为见对应阶段教程及源码。
- `Attention.forward(self, x)` — 行为见对应阶段教程及源码。
- `class CrossAttention(nn.Module)` — 行为见对应阶段教程及源码。
- `CrossAttention.__init__(self, dim, context_dim=None, heads=8, dim_head=64, dropout=0.0)` — 行为见对应阶段教程及源码。
- `CrossAttention.forward(self, x, context=None)` — 行为见对应阶段教程及源码。
- `class Transformer(nn.Module)` — 行为见对应阶段教程及源码。
- `Transformer.__init__(self, dim: int, depth: int, heads: int, dim_head: int, mlp_dim: int, dropout: float=0.0, norm: str='layer', norm_cond_dim: int=-1)` — 行为见对应阶段教程及源码。
- `Transformer.forward(self, x: torch.Tensor, *args)` — 行为见对应阶段教程及源码。
- `class TransformerCrossAttn(nn.Module)` — 行为见对应阶段教程及源码。
- `TransformerCrossAttn.__init__(self, dim: int, depth: int, heads: int, dim_head: int, mlp_dim: int, dropout: float=0.0, norm: str='layer', norm_cond_dim: int=-1, context_dim: Optional[int]=None)` — 行为见对应阶段教程及源码。
- `TransformerCrossAttn.forward(self, x: torch.Tensor, *args, context=None, context_list=None)` — 行为见对应阶段教程及源码。
- `class DropTokenDropout(nn.Module)` — 行为见对应阶段教程及源码。
- `DropTokenDropout.__init__(self, p: float=0.1)` — 行为见对应阶段教程及源码。
- `DropTokenDropout.forward(self, x: torch.Tensor)` — 行为见对应阶段教程及源码。
- `class ZeroTokenDropout(nn.Module)` — 行为见对应阶段教程及源码。
- `ZeroTokenDropout.__init__(self, p: float=0.1)` — 行为见对应阶段教程及源码。
- `ZeroTokenDropout.forward(self, x: torch.Tensor)` — 行为见对应阶段教程及源码。
- `class TransformerEncoder(nn.Module)` — 行为见对应阶段教程及源码。
- `TransformerEncoder.__init__(self, num_tokens: int, token_dim: int, dim: int, depth: int, heads: int, mlp_dim: int, dim_head: int=64, dropout: float=0.0, emb_dropout: float=0.0, emb_dropout_type: str='drop', emb_dropout_loc: str='token', norm: str='layer', norm_cond_dim: int=-1, token_pe_numfreq: int=-1)` — 行为见对应阶段教程及源码。
- `TransformerEncoder.forward(self, inp: torch.Tensor, *args, **kwargs)` — 行为见对应阶段教程及源码。
- `class TransformerDecoder(nn.Module)` — 行为见对应阶段教程及源码。
- `TransformerDecoder.__init__(self, num_tokens: int, token_dim: int, dim: int, depth: int, heads: int, mlp_dim: int, dim_head: int=64, dropout: float=0.0, emb_dropout: float=0.0, emb_dropout_type: str='drop', norm: str='layer', norm_cond_dim: int=-1, context_dim: Optional[int]=None, skip_token_embedding: bool=False)` — 行为见对应阶段教程及源码。
- `TransformerDecoder.forward(self, inp: torch.Tensor, *args, context=None, context_list=None)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/network/hmr2/components/t_cond_mlp.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/components/t_cond_mlp.py) · [使用教程](02_video.md) · 内容指纹 `7346d751ffaf`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class AdaptiveLayerNorm1D(torch.nn.Module)` — 行为见对应阶段教程及源码。
- `AdaptiveLayerNorm1D.__init__(self, data_dim: int, norm_cond_dim: int)` — 行为见对应阶段教程及源码。
- `AdaptiveLayerNorm1D.forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `class SequentialCond(torch.nn.Sequential)` — 行为见对应阶段教程及源码。
- `SequentialCond.forward(self, input, *args, **kwargs)` — 行为见对应阶段教程及源码。
- `normalization_layer(norm: Optional[str], dim: int, norm_cond_dim: int=-1)` — 行为见对应阶段教程及源码。
- `linear_norm_activ_dropout(input_dim: int, output_dim: int, activation: torch.nn.Module=torch.nn.ReLU(), bias: bool=True, norm: Optional[str]='layer', dropout: float=0.0, norm_cond_dim: int=-1) -> SequentialCond` — 行为见对应阶段教程及源码。
- `create_simple_mlp(input_dim: int, hidden_dims: List[int], output_dim: int, activation: torch.nn.Module=torch.nn.ReLU(), bias: bool=True, norm: Optional[str]='layer', dropout: float=0.0, norm_cond_dim: int=-1) -> SequentialCond` — 行为见对应阶段教程及源码。
- `class ResidualMLPBlock(torch.nn.Module)` — 行为见对应阶段教程及源码。
- `ResidualMLPBlock.__init__(self, input_dim: int, hidden_dim: int, num_hidden_layers: int, output_dim: int, activation: torch.nn.Module=torch.nn.ReLU(), bias: bool=True, norm: Optional[str]='layer', dropout: float=0.0, norm_cond_dim: int=-1)` — 行为见对应阶段教程及源码。
- `ResidualMLPBlock.forward(self, x: torch.Tensor, *args, **kwargs) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `class ResidualMLP(torch.nn.Module)` — 行为见对应阶段教程及源码。
- `ResidualMLP.__init__(self, input_dim: int, hidden_dim: int, num_hidden_layers: int, output_dim: int, activation: torch.nn.Module=torch.nn.ReLU(), bias: bool=True, norm: Optional[str]='layer', dropout: float=0.0, num_blocks: int=1, norm_cond_dim: int=-1)` — 行为见对应阶段教程及源码。
- `ResidualMLP.forward(self, x: torch.Tensor, *args, **kwargs) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `class FrequencyEmbedder(torch.nn.Module)` — 行为见对应阶段教程及源码。
- `FrequencyEmbedder.__init__(self, num_frequencies, max_freq_log2)` — 行为见对应阶段教程及源码。
- `FrequencyEmbedder.forward(self, x)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/network/hmr2/configs/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/configs/__init__.py) · [使用教程](02_video.md) · 内容指纹 `3d995db69b12`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `to_lower(x: Dict) -> Dict` — Convert all dictionary keys to lowercase Args:   x (dict): Input dictionary Returns:   dict: Output dictionary with all keys converted to lowercase
- `default_config() -> CN` — Get a yacs CfgNode object with the default config values.
- `dataset_config(name='datasets_tar.yaml') -> CN` — Get dataset config file Returns:   CfgNode: Dataset config as a yacs CfgNode object.
- `dataset_eval_config() -> CN` — 行为见对应阶段教程及源码。
- `get_config(config_file: str, merge: bool=True) -> CN` — Read a config file and optionally merge it with the default config file. Args:   config_file (str): Path to config file.   merge (bool): Whether to merge with the default config or not. Returns:   CfgNode: Config as a yacs CfgNode object.

## `Retargeting/GVHMR/hmr4d/network/hmr2/hmr2.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/hmr2.py) · [使用教程](02_video.md) · 内容指纹 `486676043f87`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class HMR2(pl.LightningModule)` — 行为见对应阶段教程及源码。
- `HMR2.__init__(self, cfg: CfgNode)` — 行为见对应阶段教程及源码。
- `HMR2.forward(self, batch, feat_mode=True)` — this file has been modified Args:     feat_mode: default True, as we only need the feature token output for the HMR4D project;                when False, the full process of HMR2 will be executed.

## `Retargeting/GVHMR/hmr4d/network/hmr2/smpl_head.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/smpl_head.py) · [使用教程](02_video.md) · 内容指纹 `72008bf76b23`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class SMPLTransformerDecoderHead(nn.Module)` — Cross-attention based SMPL Transformer decoder
- `SMPLTransformerDecoderHead.__init__(self, cfg)` — 行为见对应阶段教程及源码。
- `SMPLTransformerDecoderHead.forward(self, x, only_return_token_out=False)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/network/hmr2/utils/geometry.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/utils/geometry.py) · [使用教程](02_video.md) · 内容指纹 `6c39dcf44e0b`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `aa_to_rotmat(theta: torch.Tensor)` — Convert axis-angle representation to rotation matrix. Works by first converting it to a quaternion. Args:     theta (torch.Tensor): Tensor of shape (B, 3) containing axis-angle representations. Returns:     torch.Tensor: Corresponding rotation matrices with shape (B, 3, 3).
- `quat_to_rotmat(quat: torch.Tensor) -> torch.Tensor` — Convert quaternion representation to rotation matrix. Args:     quat (torch.Tensor) of shape (B, 4); 4 <===> (w, x, y, z). Returns:     torch.Tensor: Corresponding rotation matrices with shape (B, 3, 3).
- `rot6d_to_rotmat(x: torch.Tensor) -> torch.Tensor` — Convert 6D rotation representation to 3x3 rotation matrix. Based on Zhou et al., "On the Continuity of Rotation Representations in Neural Networks", CVPR 2019 Args:     x (torch.Tensor): (B,6) Batch of 6-D rotation representations. Returns:     torch.Tensor: Batch of corresponding rotation matrices with shape (B,3,3).
- `perspective_projection(points: torch.Tensor, translation: torch.Tensor, focal_length: torch.Tensor, camera_center: Optional[torch.Tensor]=None, rotation: Optional[torch.Tensor]=None) -> torch.Tensor` — Computes the perspective projection of a set of 3D points. Args:     points (torch.Tensor): Tensor of shape (B, N, 3) containing the input 3D points.     translation (torch.Tensor): Tensor of shape (B, 3) containing the 3D camera translation.     focal_length (torch.Tensor): Tensor of shape (B, 2) containing the focal length in pixels.     camera_c

## `Retargeting/GVHMR/hmr4d/network/hmr2/utils/preproc.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/utils/preproc.py) · [使用教程](02_video.md) · 内容指纹 `79c2c177f2f6`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `expand_to_aspect_ratio(input_shape, target_aspect_ratio=[192, 256])` — Increase the size of the bounding box to match the target shape.
- `crop_and_resize(img, bbx_xy, bbx_s, dst_size=256, enlarge_ratio=1.2)` — Args:     img: (H, W, 3)     bbx_xy: (2,)     bbx_s: scalar

## `Retargeting/GVHMR/hmr4d/network/hmr2/utils/smpl_wrapper.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/utils/smpl_wrapper.py) · [使用教程](02_video.md) · 内容指纹 `b2c49a214ae8`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class SMPL(smplx.SMPLLayer)` — 行为见对应阶段教程及源码。
- `SMPL.__init__(self, *args, joint_regressor_extra: Optional[str]=None, update_hips: bool=False, **kwargs)` — Extension of the official SMPL implementation to support more joints. Args:     Same as SMPLLayer.     joint_regressor_extra (str): Path to extra joint regressor.
- `SMPL.forward(self, *args, **kwargs) -> SMPLOutput` — Run forward pass. Same as SMPL and also append an extra set of joints if joint_regressor_extra is specified.

## `Retargeting/GVHMR/hmr4d/network/hmr2/vit.py`

[源码](../Retargeting/GVHMR/hmr4d/network/hmr2/vit.py) · [使用教程](02_video.md) · 内容指纹 `faf546a0d9a2`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `vit(cfg)` — 行为见对应阶段教程及源码。
- `get_abs_pos(abs_pos, h, w, ori_h, ori_w, has_cls_token=True)` — Calculate absolute positional embeddings. If needed, resize embeddings and remove cls_token     dimension for the original embeddings. Args:     abs_pos (Tensor): absolute positional embeddings with (1, num_position, C).     has_cls_token (bool): If true, has 1 embedding in abs_pos for cls token.     hw (Tuple): size of input image tokens.
- `class DropPath(nn.Module)` — Drop paths (Stochastic Depth) per sample  (when applied in main path of residual blocks).
- `DropPath.__init__(self, drop_prob=None)` — 行为见对应阶段教程及源码。
- `DropPath.forward(self, x)` — 行为见对应阶段教程及源码。
- `DropPath.extra_repr(self)` — 行为见对应阶段教程及源码。
- `class Mlp(nn.Module)` — 行为见对应阶段教程及源码。
- `Mlp.__init__(self, in_features, hidden_features=None, out_features=None, act_layer=nn.GELU, drop=0.0)` — 行为见对应阶段教程及源码。
- `Mlp.forward(self, x)` — 行为见对应阶段教程及源码。
- `class Attention(nn.Module)` — 行为见对应阶段教程及源码。
- `Attention.__init__(self, dim, num_heads=8, qkv_bias=False, qk_scale=None, attn_drop=0.0, proj_drop=0.0, attn_head_dim=None)` — 行为见对应阶段教程及源码。
- `Attention.forward(self, x)` — 行为见对应阶段教程及源码。
- `class Block(nn.Module)` — 行为见对应阶段教程及源码。
- `Block.__init__(self, dim, num_heads, mlp_ratio=4.0, qkv_bias=False, qk_scale=None, drop=0.0, attn_drop=0.0, drop_path=0.0, act_layer=nn.GELU, norm_layer=nn.LayerNorm, attn_head_dim=None)` — 行为见对应阶段教程及源码。
- `Block.forward(self, x)` — 行为见对应阶段教程及源码。
- `class PatchEmbed(nn.Module)` — Image to Patch Embedding
- `PatchEmbed.__init__(self, img_size=224, patch_size=16, in_chans=3, embed_dim=768, ratio=1)` — 行为见对应阶段教程及源码。
- `PatchEmbed.forward(self, x, **kwargs)` — 行为见对应阶段教程及源码。
- `class HybridEmbed(nn.Module)` — CNN Feature Map Embedding Extract feature map from CNN, flatten, project to embedding dim.
- `HybridEmbed.__init__(self, backbone, img_size=224, feature_size=None, in_chans=3, embed_dim=768)` — 行为见对应阶段教程及源码。
- `HybridEmbed.forward(self, x)` — 行为见对应阶段教程及源码。
- `class ViT(nn.Module)` — 行为见对应阶段教程及源码。
- `ViT.__init__(self, img_size=224, patch_size=16, in_chans=3, num_classes=80, embed_dim=768, depth=12, num_heads=12, mlp_ratio=4.0, qkv_bias=False, qk_scale=None, drop_rate=0.0, attn_drop_rate=0.0, drop_path_rate=0.0, hybrid_backbone=None, norm_layer=None, use_checkpoint=False, frozen_stages=-1, ratio=1, last_norm=True, patch_padding='pad', freeze_attn=False, freeze_ffn=False)` — 行为见对应阶段教程及源码。
- `ViT._freeze_stages(self)` — Freeze parameters.
- `ViT.init_weights(self)` — Initialize the weights in backbone. Args:     pretrained (str, optional): Path to pre-trained weights.         Defaults to None.
- `ViT.get_num_layers(self)` — 行为见对应阶段教程及源码。
- `ViT.no_weight_decay(self)` — 行为见对应阶段教程及源码。
- `ViT.forward_features(self, x)` — 行为见对应阶段教程及源码。
- `ViT.forward(self, x)` — 行为见对应阶段教程及源码。
- `ViT.train(self, mode=True)` — Convert the model into training mode.

## `Retargeting/GVHMR/hmr4d/utils/body_model/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/body_model/__init__.py) · [使用教程](02_video.md) · 内容指纹 `ab0b77594374`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/utils/body_model/body_model.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/body_model/body_model.py) · [使用教程](02_video.md) · 内容指纹 `4f5789bcc883`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class BodyModel(nn.Module)` — Wrapper around SMPLX body model class. modified by Zehong Shen
- `BodyModel.__init__(self, bm_path, num_betas=16, use_vtx_selector=False, model_type='smplh')` — 行为见对应阶段教程及源码。
- `BodyModel.forward(self, root_orient=None, pose_body=None, pose_hand=None, pose_jaw=None, pose_eye=None, betas=None, trans=None, dmpls=None, expression=None, return_dict=False, **kwargs)` — Note dmpls are not supported.
- `BodyModel.forward_motion(self, **kwargs)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/body_model/body_model_smplh.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/body_model/body_model_smplh.py) · [使用教程](02_video.md) · 内容指纹 `a55922e3d908`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class BodyModelSMPLH(nn.Module)` — Support Batch inference
- `BodyModelSMPLH.__init__(self, model_path, **kwargs)` — 行为见对应阶段教程及源码。
- `BodyModelSMPLH.forward(self, betas=None, global_orient=None, transl=None, body_pose=None, left_hand_pose=None, right_hand_pose=None, **kwargs)` — 行为见对应阶段教程及源码。
- `BodyModelSMPLH.get_skeleton(self, betas)` — betas: (*, 10) -> skeleton_beta: (*, 22, 3)

## `Retargeting/GVHMR/hmr4d/utils/body_model/body_model_smplx.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/body_model/body_model_smplx.py) · [使用教程](02_video.md) · 内容指纹 `89205d282f26`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class BodyModelSMPLX(nn.Module)` — Support Batch inference
- `BodyModelSMPLX.__init__(self, model_path, **kwargs)` — 行为见对应阶段教程及源码。
- `BodyModelSMPLX.forward(self, betas=None, global_orient=None, transl=None, body_pose=None, left_hand_pose=None, right_hand_pose=None, expression=None, jaw_pose=None, leye_pose=None, reye_pose=None, **kwargs)` — 行为见对应阶段教程及源码。
- `BodyModelSMPLX.get_skeleton(self, betas)` — betas: (*, 10) -> skeleton_beta: (*, 22, 3)
- `BodyModelSMPLX.forward_bfc(self, **kwargs)` — Wrap (B, F, C) to (B*F, C) and unwrap (B*F, C) to (B, F, C)

## `Retargeting/GVHMR/hmr4d/utils/body_model/min_lbs.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/body_model/min_lbs.py) · [使用教程](02_video.md) · 内容指纹 `ab2a94fb71d9`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class MinimalLBS(nn.Module)` — 行为见对应阶段教程及源码。
- `MinimalLBS.__init__(self, sp_ids, bm_dir='models/smplh', num_betas=16, model_type='smplh', **kwargs)` — 行为见对应阶段教程及源码。
- `MinimalLBS.load_struct_on_sp(self, bm_path, prefix='m')` — Load 4 weights from body-model-struct. Keep the sensor points only. Use prefix to label different bm.
- `MinimalLBS.forward(self, root_orient=None, pose_body=None, trans=None, betas=None, A=None, recompute_A=False, genders=None, joints_zero=None)` — Args:     root_orient, Optional: (B, T, 3)     pose_body: (B, T, J*3)     trans: (B, T, 3)     betas: (B, T, 16)     A, Optional: (B, T, J+1, 4, 4)     recompute_A: if True, root_orient should be given, otherwise use A     genders, List: ['male', 'female', ...]     joints_zero: (B, J+1, 3), required when recompute_A is True Returns:     sensor_vert

## `Retargeting/GVHMR/hmr4d/utils/body_model/smpl_lite.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/body_model/smpl_lite.py) · [使用教程](02_video.md) · 内容指纹 `ff88785ea067`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class SmplLite(nn.Module)` — 行为见对应阶段教程及源码。
- `SmplLite.__init__(self, model_path='inputs/checkpoints/body_models/smpl', gender='neutral', num_betas=10)` — 行为见对应阶段教程及源码。
- `SmplLite.register_smpl_buffers(self, data_struct, num_betas)` — 行为见对应阶段教程及源码。
- `SmplLite.register_fast_skeleton_computing_buffers(self)` — 行为见对应阶段教程及源码。
- `SmplLite.get_skeleton(self, betas)` — 行为见对应阶段教程及源码。
- `SmplLite.forward(self, body_pose, betas, global_orient, transl)` — Args:     body_pose: (B, L, 63)     betas: (B, L, 10)     global_orient: (B, L, 3)     transl: (B, L, 3) Returns:     vertices: (B, L, V, 3)
- `class SmplxLiteJ24(SmplLite)` — 行为见对应阶段教程及源码。
- `SmplxLiteJ24.__init__(self, **kwargs)` — 行为见对应阶段教程及源码。
- `SmplxLiteJ24.forward(self, body_pose, betas, global_orient, transl)` — Returns: joints (*, J, 3). (B, L) or  (B,) are both supported.

## `Retargeting/GVHMR/hmr4d/utils/body_model/smplx_lite.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/body_model/smplx_lite.py) · [使用教程](02_video.md) · 内容指纹 `f64ce5c324ab`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class SmplxLite(nn.Module)` — 行为见对应阶段教程及源码。
- `SmplxLite.__init__(self, model_path=PROJ_ROOT / 'inputs/checkpoints/body_models/smplx', gender='neutral', num_betas=10)` — 行为见对应阶段教程及源码。
- `SmplxLite.register_smpl_buffers(self, data_struct, num_betas)` — 行为见对应阶段教程及源码。
- `SmplxLite.register_smplh_buffers(self, data_struct, num_pca_comps, flat_hand_mean)` — 行为见对应阶段教程及源码。
- `SmplxLite.register_smplx_buffers(self, data_struct)` — 行为见对应阶段教程及源码。
- `SmplxLite.register_fast_skeleton_computing_buffers(self)` — 行为见对应阶段教程及源码。
- `SmplxLite.get_skeleton(self, betas)` — 行为见对应阶段教程及源码。
- `SmplxLite.forward(self, body_pose, betas, global_orient, transl=None, rotation_type='aa')` — Args:     body_pose: (B, L, 63)     betas: (B, L, 10)     global_orient: (B, L, 3)     transl: (B, L, 3) Returns:     vertices: (B, L, V, 3)
- `class SmplxLiteCoco17(SmplxLite)` — Output COCO17 joints (Faster, but cannot output vertices)
- `SmplxLiteCoco17.__init__(self, **kwargs)` — 行为见对应阶段教程及源码。
- `SmplxLiteCoco17.forward(self, body_pose, betas, global_orient, transl)` — Returns: joints (*, 17, 3). (B, L) or  (B,) are both supported.
- `class SmplxLiteV437Coco17(SmplxLite)` — 行为见对应阶段教程及源码。
- `SmplxLiteV437Coco17.__init__(self, **kwargs)` — 行为见对应阶段教程及源码。
- `SmplxLiteV437Coco17.forward(self, body_pose, betas, global_orient, transl)` — Returns:     verts_437: (*, 437, 3)     joints (*, 17, 3). (B, L) or  (B,) are both supported.
- `class SmplxLiteSmplN24(SmplxLite)` — Output SMPL(not smplx)-Neutral 24 joints (Faster, but cannot output vertices)
- `SmplxLiteSmplN24.__init__(self, **kwargs)` — 行为见对应阶段教程及源码。
- `SmplxLiteSmplN24.forward(self, body_pose, betas, global_orient, transl)` — Returns: joints (*, J, 3). (B, L) or  (B,) are both supported.
- `batch_rigid_transform_v2(rot_mats, joints, parents)` — Args:     rot_mats: (*, J, 3, 3)     joints: (*, J, 3)
- `sync_time()` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/body_model/utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/body_model/utils.py) · [使用教程](02_video.md) · 内容指纹 `dec29039e53a`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `smpl_to_openpose(model_type='smplx', use_hands=True, use_face=True, use_face_contour=False, openpose_format='coco25')` — Returns the indices of the permutation that maps SMPL to OpenPose

## `Retargeting/GVHMR/hmr4d/utils/eval/eval_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/eval/eval_utils.py) · [使用教程](02_video.md) · 内容指纹 `6c32fea0b006`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `compute_camcoord_metrics(batch, pelvis_idxs=[1, 2], fps=30, mask=None)` — Args:     batch (dict): {         "pred_j3d": (..., J, 3) tensor         "target_j3d":         "pred_verts":         "target_verts":     } Returns:     cam_coord_metrics (dict): {         "pa_mpjpe": (..., ) numpy array         "mpjpe":         "pve":         "accel":     }
- `compute_global_metrics(batch, mask=None)` — Follow WHAM, the input has skipped invalid frames Args:     batch (dict): {         "pred_j3d_glob": (F, J, 3) tensor         "target_j3d_glob":         "pred_verts_glob":         "target_verts_glob":     } Returns:     global_metrics (dict): {         "wa2_mpjpe": (F, ) numpy array         "waa_mpjpe":         "rte":         "jitter":         "fs"
- `compute_camcoord_perjoint_metrics(batch, pelvis_idxs=[1, 2])` — Args:     batch (dict): {         "pred_j3d": (..., J, 3) tensor         "target_j3d":     } Returns:     cam_coord_metrics (dict): {         "pa_mpjpe": (..., ) numpy array         "mpjpe":         "pve":         "accel":     }
- `compute_jpe(S1, S2)` — 行为见对应阶段教程及源码。
- `compute_perjoint_jpe(S1, S2)` — 行为见对应阶段教程及源码。
- `batch_align_by_pelvis(data_list, pelvis_idxs=[1, 2])` — Assumes data is given as [pred_j3d, target_j3d, pred_verts, target_verts]. Each data is in shape of (frames, num_points, 3) Pelvis is notated as one / two joints indices. Align all data to the corresponding pelvis location.
- `batch_compute_similarity_transform_torch(S1, S2)` — Computes a similarity transform (sR, t) that takes a set of 3D points S1 (3 x N) closest to a set of 3D points S2, where R is an 3x3 rotation matrix, t 3x1 translation, s scale. i.e. solves the orthogonal Procrutes problem.
- `compute_error_accel(joints_gt, joints_pred, valid_mask=None, fps=None)` — Use [i-1, i, i+1] to compute acc at frame_i. The acceleration error: 1/(n-2) sum_{i=1}^{n-1} X_{i-1} - 2X_i + X_{i+1} Note that for each frame that is not visible, three entries(-1, 0, +1) in the acceleration error will be zero'd out. Args:     joints_gt : (F, J, 3)     joints_pred : (F, J, 3)     valid_mask : (F) Returns:     error_accel (F-2) whe
- `compute_rte(target_trans, pred_trans)` — 行为见对应阶段教程及源码。
- `compute_jitter(joints, fps=30)` — compute jitter of the motion Args:     joints (N, J, 3).     fps (float). Returns:     jitter (N-3).
- `compute_foot_sliding(target_verts, pred_verts, thr=0.01)` — compute foot sliding error The foot ground contact label is computed by the threshold of 1 cm/frame Args:     target_verts (N, 6890, 3).     pred_verts (N, 6890, 3). Returns:     error (N frames in contact).
- `convert_joints22_to_24(joints22, ratio2220=0.3438, ratio2321=0.3345)` — 行为见对应阶段教程及源码。
- `align_pcl(Y, X, weight=None, fixed_scale=False)` — align similarity transform to align X with Y using umeyama method X' = s * R * X + t is aligned with Y :param Y (*, N, 3) first trajectory :param X (*, N, 3) second trajectory :param weight (*, N, 1) optional weight of valid correspondences :returns s (*, 1), R (*, 3, 3), t (*, 3)
- `global_align_joints(gt_joints, pred_joints)` — :param gt_joints (T, J, 3) :param pred_joints (T, J, 3)
- `first_align_joints(gt_joints, pred_joints)` — align the first two frames :param gt_joints (T, J, 3) :param pred_joints (T, J, 3)
- `rearrange_by_mask(x, mask)` — x (L, *) mask (M,), M >= L
- `as_np_array(d)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/geo/augment_noisy_pose.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/geo/augment_noisy_pose.py) · [使用教程](02_video.md) · 内容指纹 `5fb1ddffea99`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `gaussian_augment(body_pose, std_angle=10.0, to_R=True)` — Args:     body_pose torch.Tensor: (..., J, 3) axis-angle if to_R is True, else rotmat (..., J, 3, 3)     std_angle: scalar or list, in degree
- `get_jitter(shape=(8, 120), s_jittering=0.05)` — Guassian jitter modeling.
- `get_jitter_cuda(shape=(8, 120), s_jittering=0.05)` — 行为见对应阶段教程及源码。
- `get_lfhp(shape=(8, 120), s_peak=0.3, s_peak_mask=0.005)` — Low-frequency high-peak noise modeling.
- `get_lfhp_cuda(shape=(8, 120), s_peak=0.3, s_peak_mask=0.005)` — 行为见对应阶段教程及源码。
- `get_bias(shape=(8, 120), s_bias=0.1)` — Bias noise modeling.
- `get_bias_cuda(shape=(8, 120), s_bias=0.1)` — 行为见对应阶段教程及源码。
- `get_wham_aug_kp3d(shape=(8, 120))` — 行为见对应阶段教程及源码。
- `get_visible_mask(shape=(8, 120), s_mask=0.03)` — Mask modeling.
- `get_invisible_legs_mask(shape, s_mask=0.03)` — Both legs are invisible for a random duration.
- `randomly_occlude_lower_half(i_x2d, s_mask=0.03)` — Randomly occlude the lower half of the image.
- `randomly_modify_hands_legs(j3d)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/geo/flip_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/geo/flip_utils.py) · [使用教程](02_video.md) · 内容指纹 `c0c8190637e9`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `flip_heatmap_coco17(output_flipped)` — 行为见对应阶段教程及源码。
- `flip_bbx_xys(bbx_xys, w)` — bbx_xys: (F, 3)
- `flip_kp2d_coco17(kp2d, w)` — Flip keypoints.
- `flip_smplx_params(smplx_params)` — Flip pose. The flipping is based on SMPLX parameters.
- `avg_smplx_aa(aa1, aa2)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/geo/hmr_cam.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/geo/hmr_cam.py) · [使用教程](02_video.md) · 内容指纹 `d81e2528b10a`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `estimate_focal_length(img_w, img_h)` — 行为见对应阶段教程及源码。
- `estimate_K(img_w, img_h)` — 行为见对应阶段教程及源码。
- `convert_K_to_K4(K)` — 行为见对应阶段教程及源码。
- `convert_f_to_K(focal_length, img_w, img_h)` — 行为见对应阶段教程及源码。
- `resize_K(K, f=0.5)` — 行为见对应阶段教程及源码。
- `create_camera_sensor(width=None, height=None, f_fullframe=None)` — 行为见对应阶段教程及源码。
- `convert_xys_to_cliff_cam_wham(xys, res)` — Args:     xys: (N, 3) in pixel. Note s should not be touched by 200     res: (2), e.g. [4112., 3008.]  (w,h) Returns:     cliff_cam: (N, 3), normalized representation
- `compute_bbox_info_bedlam(bbx_xys, K_fullimg)` — impl as in BEDLAM Args:     bbx_xys: ((B), N, 3), in pixel space described by K_fullimg     K_fullimg: ((B), (N), 3, 3) Returns:     bbox_info: ((B), N, 3)
- `compute_transl_full_cam(pred_cam, bbx_xys, K_fullimg)` — 行为见对应阶段教程及源码。
- `get_a_pred_cam(transl, bbx_xys, K_fullimg)` — Inverse operation of compute_transl_full_cam
- `project_to_bi01(points, bbx_xys, K_fullimg)` — points: (B, L, J, 3) bbx_xys: (B, L, 3) K_fullimg: (B, L, 3, 3)
- `perspective_projection(points, K)` — 行为见对应阶段教程及源码。
- `normalize_kp2d(obs_kp2d, bbx_xys, clamp_scale_min=False)` — Args:     obs_kp2d: (B, L, J, 3) [x, y, c]     bbx_xys: (B, L, 3) Returns:     obs: (B, L, J, 3)  [x, y, c]
- `get_bbx_xys(i_j2d, bbx_ratio=[192, 256], do_augment=False, base_enlarge=1.2)` — Args: (B, L, J, 3) [x,y,c] -> Returns: (B, L, 3)
- `safely_render_x3d_K(x3d, K_fullimg, thr)` — Args:     x3d: (B, L, V, 3), should as least have a safe points (not examined here)     K_fullimg: (B, L, 3, 3) Returns:     bbx_xys: (B, L, 3)     i_x2d: (B, L, V, 2)
- `get_bbx_xys_from_xyxy(bbx_xyxy, base_enlarge=1.2)` — Args:     bbx_xyxy: (N, 4) [x1, y1, x2, y2] Returns:     bbx_xys: (N, 3) [center_x, center_y, size]
- `bbx_xyxy_from_x(p2d)` — Args:     p2d: (*, V, 2) - Tensor containing 2D points.
- `bbx_xyxy_from_masked_x(p2d, mask)` — Args:     p2d: (*, V, 2) - Tensor containing 2D points.     mask: (*, V) - Boolean tensor indicating valid points.
- `bbx_xyxy_ratio(xyxy1, xyxy2)` — Designed for fov/unbounded Args:     xyxy1: (*, 4)     xyxy2: (*, 4) Return:     ratio: (*), squared_area(xyxy1) / squared_area(xyxy2)
- `get_mesh_in_fov_category(mask)` — mask: (L, V) The definition: 1. FullyVisible: The mesh in every frame is entirely within the field of view (FOV). 2. PartiallyVisible: In some frames, parts of the mesh are outside the FOV, while other parts are within the FOV. 3. PartiallyOut: In some frames, the mesh is completely outside the FOV, while in others, it is visible. 4. FullyOut: The
- `get_infov_mask(p2d, w_real, h_real)` — Args:     p2d: (B, L, V, 2)     w_real, h_real: (B, L) or int Returns:     mask: (B, L, V)

## `Retargeting/GVHMR/hmr4d/utils/geo/hmr_global.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/geo/hmr_global.py) · [使用教程](02_video.md) · 内容指纹 `2bf268e8b504`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `get_R_c2gv(R_w2c, axis_gravity_in_w=[0, 0, -1])` — Args:     R_w2c: (*, 3, 3) Returns:     R_c2gv: (*, 3, 3)
- `get_tgtcoord_rootparam(global_orient, transl, gravity_vec=None, tgt_gravity_vec=None, tsf='ay->ay')` — Rotate around the origin center, to match the new gravity direction Args:     global_orient: torch.tensor, (*, 3)     transl: torch.tensor, (*, 3)     gravity_vec: torch.tensor, (3,)     tgt_gravity_vec: torch.tensor, (3,) Returns:     tgt_global_orient: torch.tensor, (*, 3)     tgt_transl: torch.tensor, (*, 3)     R_g2tg: (3, 3)
- `get_c_rootparam(global_orient, transl, T_w2c, offset)` — Args:     global_orient: torch.tensor, (F, 3)     transl: torch.tensor, (F, 3)     T_w2c: torch.tensor, (*, 4, 4)     offset: torch.tensor, (3,) Returns:     R_c: torch.tensor, (F, 3)     t_c: torch.tensor, (F, 3)
- `get_T_w2c_from_wcparams(global_orient_w, transl_w, global_orient_c, transl_c, offset)` — Args:     global_orient_w: torch.tensor, (F, 3)     transl_w: torch.tensor, (F, 3)     global_orient_c: torch.tensor, (F, 3)     transl_c: torch.tensor, (F, 3)     offset: torch.tensor, (*, 3) Returns:     T_w2c: torch.tensor, (F, 4, 4)
- `get_local_transl_vel(transl, global_orient)` — transl velocity is in local coordinate (or, SMPL-coord) Args:     transl: (*, L, 3)     global_orient: (*, L, 3) Returns:     transl_vel: (*, L, 3)
- `rollout_local_transl_vel(local_transl_vel, global_orient, transl_0=None)` — transl velocity is in local coordinate (or, SMPL-coord) Args:     local_transl_vel: (*, L, 3)     global_orient: (*, L, 3)     transl_0: (*, 1, 3), if not provided, the start point is 0 Returns:     transl: (*, L, 3)
- `get_local_transl_vel_alignhead(transl, global_orient)` — 行为见对应阶段教程及源码。
- `rollout_local_transl_vel_alignhead(local_transl_vel_alignhead, global_orient, transl_0=None)` — 行为见对应阶段教程及源码。
- `get_local_transl_vel_alignhead_absy(transl, global_orient)` — 行为见对应阶段教程及源码。
- `rollout_local_transl_vel_alignhead_absy(local_transl_vel_alignhead_absy, global_orient, transl_0=None)` — 行为见对应阶段教程及源码。
- `get_local_transl_vel_alignhead_absgy(transl, global_orient)` — 行为见对应阶段教程及源码。
- `rollout_local_transl_vel_alignhead_absgy(local_transl_vel_alignhead_absgy, global_orient, transl_0=None)` — 行为见对应阶段教程及源码。
- `rollout_vel(vel, transl_0=None)` — Args:     vel: (*, L, 3)     transl_0: (*, 1, 3), if not provided, the start point is 0 Returns:     transl: (*, L, 3)
- `get_static_joint_mask(w_j3d, vel_thr=0.25, smooth=False, repeat_last=False)` — w_j3d: (*, L, J, 3) vel_thr: HuMoR uses 0.15m/s

## `Retargeting/GVHMR/hmr4d/utils/geo/quaternion.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/geo/quaternion.py) · [使用教程](02_video.md) · 内容指纹 `dc59c87e253a`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `qinv(q)` — 行为见对应阶段教程及源码。
- `qinv_np(q)` — 行为见对应阶段教程及源码。
- `qnormalize(q)` — 行为见对应阶段教程及源码。
- `qmul(q, r)` — Multiply quaternion(s) q with quaternion(s) r. Expects two equally-sized tensors of shape (*, 4), where * denotes any number of dimensions. Returns q*r as a tensor of shape (*, 4).
- `qrot(q, v)` — Rotate vector(s) v about the rotation described by quaternion(s) q. Expects a tensor of shape (*, 4) for q and a tensor of shape (*, 3) for v, where * denotes any number of dimensions. Returns a tensor of shape (*, 3).
- `qeuler(q, order, epsilon=0, deg=True)` — Convert quaternion(s) q to Euler angles. Expects a tensor of shape (*, 4), where * denotes any number of dimensions. Returns a tensor of shape (*, 3).
- `qmul_np(q, r)` — 行为见对应阶段教程及源码。
- `qrot_np(q, v)` — 行为见对应阶段教程及源码。
- `qeuler_np(q, order, epsilon=0, use_gpu=False)` — 行为见对应阶段教程及源码。
- `qfix(q)` — Enforce quaternion continuity across the time dimension by selecting the representation (q or -q) with minimal distance (or, equivalently, maximal dot product) between two consecutive frames.
- `euler2quat(e, order, deg=True)` — Convert Euler angles to quaternions.
- `expmap_to_quaternion(e)` — Convert axis-angle rotations (aka exponential maps) to quaternions. Stable formula from "Practical Parameterization of Rotations Using the Exponential Map". Expects a tensor of shape (*, 3), where * denotes any number of dimensions. Returns a tensor of shape (*, 4).
- `euler_to_quaternion(e, order)` — Convert Euler angles to quaternions.
- `quaternion_to_matrix(quaternions)` — Convert rotations given as quaternions to rotation matrices. Args:     quaternions: quaternions with real part first,         as tensor of shape (..., 4). Returns:     Rotation matrices as tensor of shape (..., 3, 3).
- `quaternion_to_matrix_np(quaternions)` — 行为见对应阶段教程及源码。
- `quaternion_to_cont6d_np(quaternions)` — 行为见对应阶段教程及源码。
- `quaternion_to_cont6d(quaternions)` — 行为见对应阶段教程及源码。
- `cont6d_to_matrix(cont6d)` — 行为见对应阶段教程及源码。
- `cont6d_to_matrix_np(cont6d)` — 行为见对应阶段教程及源码。
- `qpow(q0, t, dtype=torch.float)` — q0 : tensor of quaternions t: tensor of powers
- `qslerp(q0, q1, t)` — q0: starting quaternion q1: ending quaternion t: array of points along the way
- `qbetween(v0, v1)` — find the quaternion used to rotate v0 to v1
- `qbetween_np(v0, v1)` — find the quaternion used to rotate v0 to v1
- `lerp(p0, p1, t)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/geo/transforms.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/geo/transforms.py) · [使用教程](02_video.md) · 内容指纹 `5c3a46a082d4`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `axis_rotate_to_matrix(angle, axis='x')` — Get rotation matrix for rotating around one axis Args:     angle: (N, 1) Returns:     R: (N, 3, 3)

## `Retargeting/GVHMR/hmr4d/utils/geo_transform.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/geo_transform.py) · [使用教程](02_video.md) · 内容指纹 `36bd9bfb09c3`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `homo_points(points)` — Args:     points: (..., C) Returns: (..., C+1), with 1 padded
- `apply_Ts_on_seq_points(points, Ts)` — perform translation matrix on related point Args:     points: (..., N, 3)     Ts: (..., N, 4, 4) Returns: (..., N, 3)
- `apply_T_on_points(points, T)` — Args:     points: (..., N, 3)     T: (..., 4, 4) Returns: (..., N, 3)
- `T_transforms_points(T, points, pattern)` — manual mode of apply_T_on_points T: (..., 4, 4) points: (..., 3) pattern: "... c d, ... d -> ... c"
- `project_p2d(points, K=None, is_pinhole=True)` — Args:     points: (..., (N), 3)     K: (..., 3, 3) Returns: shape is similar to points but without z
- `gen_uv_from_HW(H, W, device='cpu')` — Returns: (H, W, 2), as float. Note: uv not ij
- `unproject_p2d(uv, z, K)` — we assume a pinhole camera for unprojection uv: (B, N, 2) z: (B, N, 1) K: (B, 3, 3) Returns: (B, N, 3)
- `cvt_p2d_from_i_to_c(uv, K)` — Args:     uv: (..., 2) or (..., N, 2)     K: (..., 3, 3) Returns: the same shape as input uv
- `cvt_to_bi01_p2d(p2d, bbx_lurb)` — p2d: (..., (N), 2) bbx_lurb: (..., 4)
- `cvt_from_bi01_p2d(bi01_p2d, bbx_lurb)` — Use bbx_lurb to resize bi01_p2d to p2d (image-coordinates) Args:     p2d: (..., 2) or (..., N, 2)     bbx_lurb: (..., 4) Returns:     p2d: shape is the same as input
- `cvt_p2d_from_bi01_to_c(bi01, bbxs_lurb, Ks)` — Args:     bi01: (..., (N), 2), value in range (0,1), the point in the bbx image     bbxs_lurb: (..., 4)     Ks: (..., 3, 3) Returns:     c: (..., (N), 2)
- `cvt_p2d_from_pm1_to_i(p2d_pm1, bbx_xys)` — Args:     p2d_pm1: (..., (N), 2), value in range (-1,1), the point in the bbx image     bbx_xys: (..., 3) Returns:     p2d: (..., (N), 2)
- `uv2l_index(uv, W)` — 行为见对应阶段教程及源码。
- `l2uv_index(l, W)` — 行为见对应阶段教程及源码。
- `transform_mat(R, t)` — Args:     R: Bx3x3 array of a batch of rotation matrices     t: Bx3x(1) array of a batch of translation vectors Returns:     T: Bx4x4 Transformation matrix
- `axis_angle_to_matrix_exp_map(aa)` — use pytorch3d so3_exp_map Args:     aa: (*, 3) Returns:     R: (*, 3, 3)
- `matrix_to_axis_angle_log_map(R)` — use pytorch3d so3_log_map Args:     aa: (*, 3, 3) Returns:     R: (*, 3)
- `matrix_to_axis_angle(R)` — use pytorch3d so3_log_map Args:     aa: (*, 3, 3) Returns:     R: (*, 3)
- `ransac_PnP(K, pts_2d, pts_3d, err_thr=10)` — solve pnp
- `ransac_PnP_batch(K_raw, pts_2d, pts_3d, err_thr=10)` — 行为见对应阶段教程及源码。
- `triangulate_point(Ts_w2c, c_p2d, **kwargs)` — 行为见对应阶段教程及源码。
- `triangulate_point_ortho(Ts_w2c, c_p2d, **kwargs)` — 行为见对应阶段教程及源码。
- `get_nearby_points(points, query_verts, padding=0.0, p=1)` — points: (S, 3) query_verts: (V, 3)
- `unproj_bbx_to_fst(bbx_lurb, K, near_z=0.5, far_z=12.5)` — 行为见对应阶段教程及源码。
- `convert_bbx_xys_to_lurb(bbx_xys)` — Args: bbx_xys (..., 3) -> bbx_lurb (..., 4)
- `convert_lurb_to_bbx_xys(bbx_lurb)` — Args: bbx_lurb (..., 4) -> bbx_xys (..., 3) be aware that it is squared
- `compute_T_ayf2az(joints, inverse=False)` — Args:     joints: (B, J, 3), in the start-frame, az-coordinate Returns:     if inverse == False:        T_af2az: (B, 4, 4)     else :         T_az2af: (B, 4, 4)
- `compute_T_ayfz2ay(joints, inverse=False)` — Args:     joints: (B, J, 3), in the start-frame, ay-coordinate Returns:     if inverse == False:         T_ayfz2ay: (B, 4, 4)     else :         T_ay2ayfz: (B, 4, 4)
- `compute_T_ay2ayrot(joints)` — Args:     joints: (B, J, 3), in the start-frame, ay-coordinate Returns:     T_ay2ayrot: (B, 4, 4)
- `compute_root_quaternion_ay(joints)` — Args:     joints: (B, J, 3), in the start-frame, ay-coordinate Returns:     root_quat: (B, 4) from z-axis to fz
- `similarity_transform_batch(S1, S2)` — Computes a similarity transform (sR, t) that solves the orthogonal Procrutes problem. Args:     S1, S2: (*, L, 3)
- `kabsch_algorithm_batch(X1, X2)` — Computes a rigid transform (R, t) Args:     X1, X2: (*, L, 3)
- `compute_cam_angvel(R_w2c, padding_last=True)` — R_w2c : (F, 3, 3)
- `ransac_gravity_vec(xyz, num_iterations=100, threshold=0.05, verbose=False)` — 行为见对应阶段教程及源码。
- `sequence_best_cammat(w_j3d, c_j3d, cam_rot)` — 行为见对应阶段教程及源码。
- `get_sequence_cammat(w_j3d, c_j3d, cam_rot)` — 行为见对应阶段教程及源码。
- `ransac_vec(vel, min_multiply=20, verbose=False)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/ik/ccd_ik.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/ik/ccd_ik.py) · [使用教程](02_video.md) · 内容指纹 `7894d191b232`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class CCD_IK()` — 行为见对应阶段教程及源码。
- `CCD_IK.__init__(self, local_mat, parent, target_ind, target_pos=None, target_rot=None, kinematic_chain=None, max_iter=2, threshold=0.001, pos_weight=1.0, rot_weight=0.0)` — 行为见对应阶段教程及源码。
- `CCD_IK.is_converged(self)` — 行为见对应阶段教程及源码。
- `CCD_IK.solve(self)` — 行为见对应阶段教程及源码。
- `CCD_IK.optimize(self, i)` — 行为见对应阶段教程及源码。
- `CCD_IK.get_weight(self, i)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/kpts/kp2d_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/kpts/kp2d_utils.py) · [使用教程](02_video.md) · 内容指纹 `781114ac9cc5`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `_taylor(heatmap, coord)` — Distribution aware coordinate decoding method.
- `_get_max_preds(heatmaps)` — Get keypoint predictions from score maps.
- `post_dark_udp(coords, batch_heatmaps, kernel=3)` — DARK post-pocessing. Implemented by udp. Paper ref: Huang et al. The Devil is in the Details: Delving into Unbiased Data Processing for Human Pose Estimation (CVPR 2020). Zhang et al. Distribution-Aware Coordinate Representation for Human Pose Estimation (CVPR 2020).
- `_gaussian_blur(heatmaps, kernel=11)` — Modulate heatmap distribution with Gaussian.  sigma = 0.3*((kernel_size-1)*0.5-1)+0.8  sigma~=3 if k=17  sigma=2 if k=11;  sigma~=1.5 if k=7;  sigma~=1 if k=3;
- `keypoints_from_heatmaps(heatmaps, center, scale, unbiased=False, post_process='default', kernel=11, valid_radius_factor=0.0546875, use_udp=False, target_type='GaussianHeatmap')` — Get final keypoint predictions from heatmaps and transform them back to the image.
- `transform_preds(coords, center, scale, output_size, use_udp=False)` — Get final keypoint predictions from heatmaps and apply scaling and translation to map them back to the image.

## `Retargeting/GVHMR/hmr4d/utils/matrix.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/matrix.py) · [使用教程](02_video.md) · 内容指纹 `998b0c18dcad`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `identity_mat(x=None, device='cpu', is_numpy=False)` — 行为见对应阶段教程及源码。
- `vec2mat(vec)` — _summary_
- `mat2vec(mat)` — _summary_
- `vec2mat_batch(vec)` — _summary_
- `rotmat2tan_norm(mat)` — _summary_
- `mat2tan_norm(mat)` — _summary_
- `rotmat2tan_norm(mat)` — _summary_
- `tan_norm2rotmat(tan_norm)` — _summary_
- `rotmat332vec_batch(mat)` — _summary_
- `rotmat2vec_batch(mat)` — _summary_
- `mat2vec_batch(mat)` — _summary_
- `mat2pose_batch(mat, returnvel=True)` — _summary_
- `get_mat_BinA(matCtoA, matCtoB)` —     given matrix of the same object in two coordinate A and B,     return matrix B in the coordinate of A
- `get_mat_BtoA(matA, matB)` —     return matrix B in the coordinate of A
- `get_mat_BfromA(matA, matBtoA)` —     return world matrix B given matrix A and mat B realtive to A
- `get_relative_position_to(pos, mat)` — _summary_
- `get_rotation(mat)` — _summary_
- `set_rotation(mat, rotmat)` — _summary_
- `set_position(mat, pos)` — _summary_
- `get_position(mat)` — _summary_
- `get_position_from(pos, mat)` — _summary_
- `get_position_from_rotmat(pos, mat)` — _summary_
- `get_relative_direction_to(dir, mat)` — _summary_
- `get_direction_from(dir, mat)` — _summary_
- `get_coord_vis(pos, rot_mat, scale=1.0)` — 行为见对应阶段教程及源码。
- `project_vec(vec)` — _summary_
- `xz2xyz(vec)` — 行为见对应阶段教程及源码。
- `normalized(vec)` — 行为见对应阶段教程及源码。
- `normalized_matrix(mat)` — 行为见对应阶段教程及源码。
- `get_rot_mat_from_forward(forward)` — _summary_
- `get_rot_mat_from_forward_up(forward, up)` — _summary_
- `get_rot_mat_from_pose_vec(vec)` — _summary_
- `get_TRS(rot_mat, pos)` — _summary_
- `xzvec2mat(vec)` — _summary_
- `distance(vec1, vec2)` — 行为见对应阶段教程及源码。
- `get_relative_pose_from_vec(pose, root, N)` — 行为见对应阶段教程及源码。
- `get_forward_from_pos(pos)` — _summary_
- `project_point_along_ray(p, ray, keepnorm=False)` — _summary_
- `solve_point_along_ray_with_constraint(c, ray, p, constraint='x')` — _summary_
- `calc_cosine(vec1, vec2, return_angle=False)` — _summary_
- `quat_xyzw2wxyz(quat)` — 行为见对应阶段教程及源码。
- `quat_wxyz2xyzw(quat)` — 行为见对应阶段教程及源码。
- `quat_mul(a, b)` — quaternion multiplication
- `quat_pos(x)` — make all the real part of the quaternion positive
- `quat_abs(x)` — quaternion norm (unit quaternion represents a 3D rotation, which has norm of 1)
- `quat_unit(x)` — normalized quaternion with norm of 1
- `quat_conjugate(x)` — quaternion with its imaginary part negated
- `quat_real(x)` — real component of the quaternion
- `quat_imaginary(x)` — imaginary components of the quaternion
- `quat_norm_check(x)` — verify that a quaternion has norm 1
- `quat_normalize(q)` — Construct 3D rotation from quaternion (the quaternion needs not to be normalized).
- `quat_from_xyz(xyz)` — Construct 3D rotation from the imaginary component
- `quat_identity(shape: List[int])` — Construct 3D identity rotation given shape
- `tgm_quat_from_angle_axis(angle, axis, degree: bool=False)` — Create a 3D rotation from angle and axis of rotation. The rotation is counter-clockwise along the axis.
- `quat_from_rotation_matrix(m)` — Construct a 3D rotation from a valid 3x3 rotation matrices. Reference can be found here: http://www.cg.info.hiroshima-cu.ac.jp/~miyazaki/knowledge/teche52.html
- `quat_mul_norm(x, y)` — Combine two sets of 3D rotations together using the multiplication operator. The shape needs to be broadcastable
- `quat_rotate(rot, vec)` — Rotate a 3D vector with the 3D rotation
- `quat_inverse(x)` — The inverse of the rotation
- `quat_identity_like(x)` — Construct identity 3D rotation with the same shape
- `quat_angle_axis(x)` — The (angle, axis) representation of the rotation. The axis is normalized to unit length. The angle is guaranteed to be between [0, pi].
- `quat_yaw_rotation(x, z_up: bool=True)` — Yaw rotation (rotation along z-axis)
- `transform_from_rotation_translation(r: Optional[torch.Tensor]=None, t: Optional[torch.Tensor]=None)` — Construct a transform from a quaternion and 3D translation. Only one of them can be None.
- `transform_identity(shape: List[int])` — Identity transformation with given shape
- `transform_rotation(x)` — Get rotation from transform
- `transform_translation(x)` — Get translation from transform
- `transform_inverse(x)` — Inverse transformation
- `transform_identity_like(x)` — identity transformation with the same shape
- `transform_mul(x, y)` — Combine two transformation together
- `transform_apply(rot, vec)` — Transform a 3D vector
- `rot_matrix_det(x)` — Return the determinant of the 3x3 matrix. The shape of the tensor will be as same as the shape of the matrix
- `rot_matrix_integrity_check(x)` — Verify that a rotation matrix has a determinant of one and is orthogonal
- `rot_matrix_from_quaternion(q)` — Construct rotation matrix from quaternion
- `euclidean_to_rotation_matrix(x)` — Get the rotation matrix on the top-left corner of a Euclidean transformation matrix
- `euclidean_integrity_check(x)` — 行为见对应阶段教程及源码。
- `euclidean_translation(x)` — Get the translation vector located at the last column of the matrix
- `euclidean_inverse(x)` — Compute the matrix that represents the inverse rotation
- `euclidean_to_transform(transformation_matrix)` — Construct a transform from a Euclidean transformation matrix
- `to_torch(x, dtype=torch.float, device='cuda:0', requires_grad=False)` — 行为见对应阶段教程及源码。
- `quat_mul(a, b)` — 行为见对应阶段教程及源码。
- `normalize(x, eps: float=1e-09)` — 行为见对应阶段教程及源码。
- `quat_apply(a, b)` — 行为见对应阶段教程及源码。
- `quat_rotate(q, v)` — 行为见对应阶段教程及源码。
- `quat_rotate_inverse(q, v)` — 行为见对应阶段教程及源码。
- `quat_conjugate(a)` — 行为见对应阶段教程及源码。
- `quat_unit(a)` — 行为见对应阶段教程及源码。
- `quat_from_angle_axis(angle, axis)` — 行为见对应阶段教程及源码。
- `normalize_angle(x)` — 行为见对应阶段教程及源码。
- `tf_inverse(q, t)` — 行为见对应阶段教程及源码。
- `tf_apply(q, t, v)` — 行为见对应阶段教程及源码。
- `tf_vector(q, v)` — 行为见对应阶段教程及源码。
- `tf_combine(q1, t1, q2, t2)` — 行为见对应阶段教程及源码。
- `get_basis_vector(q, v)` — 行为见对应阶段教程及源码。
- `get_axis_params(value, axis_idx, x_value=0.0, dtype=float, n_dims=3)` — construct arguments to `Vec` according to axis index.
- `copysign(a, b)` — 行为见对应阶段教程及源码。
- `get_euler_xyz(q)` — 行为见对应阶段教程及源码。
- `quat_from_euler_xyz(roll, pitch, yaw)` — 行为见对应阶段教程及源码。
- `torch_rand_float(lower, upper, shape, device)` — 行为见对应阶段教程及源码。
- `torch_random_dir_2(shape, device)` — 行为见对应阶段教程及源码。
- `tensor_clamp(t, min_t, max_t)` — 行为见对应阶段教程及源码。
- `scale(x, lower, upper)` — 行为见对应阶段教程及源码。
- `unscale(x, lower, upper)` — 行为见对应阶段教程及源码。
- `unscale_np(x, lower, upper)` — 行为见对应阶段教程及源码。
- `quat_to_angle_axis(q)` — 行为见对应阶段教程及源码。
- `angle_axis_to_exp_map(angle, axis)` — 行为见对应阶段教程及源码。
- `quat_to_exp_map(q)` — 行为见对应阶段教程及源码。
- `quat_to_tan_norm(q)` — 行为见对应阶段教程及源码。
- `euler_xyz_to_exp_map(roll, pitch, yaw)` — 行为见对应阶段教程及源码。
- `exp_map_to_angle_axis(exp_map)` — 行为见对应阶段教程及源码。
- `exp_map_to_quat(exp_map)` — 行为见对应阶段教程及源码。
- `slerp(q0, q1, t)` — 行为见对应阶段教程及源码。
- `calc_heading_vec(q, head_ind=0)` — 行为见对应阶段教程及源码。
- `calc_heading(q, head_ind=0, gravity_axis='z')` — 行为见对应阶段教程及源码。
- `calc_heading_quat(q, head_ind=0, gravity_axis='z')` — 行为见对应阶段教程及源码。
- `calc_heading_quat_inv(q, head_ind=0)` — 行为见对应阶段教程及源码。
- `forward_kinematics(mat, parent)` — _summary_

## `Retargeting/GVHMR/hmr4d/utils/net_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/net_utils.py) · [使用教程](02_video.md) · 内容指纹 `4fee83600d51`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `load_pretrained_model(model, ckpt_path)` — Load ckpt to model with strategy
- `find_last_ckpt_path(dirpath)` — Assume ckpt is named as e{}* or last*, following the convention of pytorch-lightning.
- `get_resume_ckpt_path(resume_mode, ckpt_dir=None)` — 行为见对应阶段教程及源码。
- `select_state_dict_by_prefix(state_dict, prefix, new_prefix='')` — For each weight that start with {old_prefix}, remove the {old_prefic} and form a new state_dict. Args:     state_dict: dict     prefix: str     new_prefix: str, if exists, the new key will be {new_prefix} + {old_key[len(prefix):]} Returns:     state_dict_new: dict
- `detach_to_cpu(in_dict)` — 行为见对应阶段教程及源码。
- `to_cuda(data)` — Move data in the batch to cuda(), carefully handle data that is not tensor
- `get_valid_mask(max_len, valid_len, device='cpu')` — 行为见对应阶段教程及源码。
- `length_to_mask(lengths, max_len)` — Returns: (B, max_len)
- `repeat_to_max_len(x, max_len, dim=0)` — Repeat last frame to max_len along dim
- `repeat_to_max_len_dict(x_dict, max_len, dim=0)` — 行为见对应阶段教程及源码。
- `class Transpose(nn.Module)` — 行为见对应阶段教程及源码。
- `Transpose.__init__(self, dim1, dim2)` — 行为见对应阶段教程及源码。
- `Transpose.forward(self, x)` — 行为见对应阶段教程及源码。
- `class GaussianSmooth(nn.Module)` — 行为见对应阶段教程及源码。
- `GaussianSmooth.__init__(self, sigma=3, dim=-1)` — 行为见对应阶段教程及源码。
- `GaussianSmooth.forward(self, x)` — x (..., f, ...) f at dim
- `gaussian_smooth(x, sigma=3, dim=-1)` — 行为见对应阶段教程及源码。
- `moving_average_smooth(x, window_size=5, dim=-1)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/__init__.py) · [使用教程](02_video.md) · 内容指纹 `1ecb4e4dfe59`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/utils/preproc/relpose/matcher_wrapper.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/relpose/matcher_wrapper.py) · [使用教程](02_video.md) · 内容指纹 `3eee39e19b1a`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class Matcher()` — 行为见对应阶段教程及源码。
- `Matcher.__init__(self, matcher='sift', args=None)` — 行为见对应阶段教程及源码。
- `Matcher.match_np(self, img0, img1)` — Args:     img0: np.ndarray, shape (H, W, 3), dtype=np.uint8     img1: np.ndarray, shape (H, W, 3), dtype=np.uint8 Returns:     pts0: np.ndarray, shape (N, 2), dtype=np.float32     pts1: np.ndarray, shape (N, 2), dtype=np.float32

## `Retargeting/GVHMR/hmr4d/utils/preproc/relpose/model/base_matcher.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/relpose/model/base_matcher.py) · [使用教程](02_video.md) · 内容指纹 `2b65b623d1a1`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class BaseMatcher()` — 行为见对应阶段教程及源码。
- `BaseMatcher.__init__(self, args=None)` — 行为见对应阶段教程及源码。
- `BaseMatcher.match_np(self, img0, img1)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/relpose/model/cv2_matcher.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/relpose/model/cv2_matcher.py) · [使用教程](02_video.md) · 内容指纹 `489460b304bd`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class CV2SIFTMather(BaseMatcher)` — 行为见对应阶段教程及源码。
- `CV2SIFTMather.__init__(self, args=None)` — 行为见对应阶段教程及源码。
- `CV2SIFTMather.match_np(self, img0, img1)` — 行为见对应阶段教程及源码。
- `class CV2ORBMather(BaseMatcher)` — 行为见对应阶段教程及源码。
- `CV2ORBMather.__init__(self, args=None)` — 行为见对应阶段教程及源码。
- `CV2ORBMather.match_np(self, img0, img1)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/relpose/simple_vo.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/relpose/simple_vo.py) · [使用教程](02_video.md) · 内容指纹 `4190dd977ef2`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class SimpleVO()` — 行为见对应阶段教程及源码。
- `SimpleVO.__init__(self, video_path, scale=0.5, step=8, method='sift', f_mm=None)` — 行为见对应阶段教程及源码。
- `SimpleVO.compute(self)` — 行为见对应阶段教程及源码。
- `SimpleVO.process_video_T_w2c_list_np(self, frames, matcher: Matcher, solver: TwoPairSolver)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/relpose/solver_two_view.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/relpose/solver_two_view.py) · [使用教程](02_video.md) · 内容指纹 `62b55ad081c0`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class CameraParams()` — 行为见对应阶段教程及源码。
- `class Cv2RansacEssentialSolver()` — 行为见对应阶段教程及源码。
- `Cv2RansacEssentialSolver.__init__(self, camera_params: CameraParams)` — 行为见对应阶段教程及源码。
- `Cv2RansacEssentialSolver.get_K(self)` — Returns:     K: np.ndarray, shape (3, 3), dtype=np.float32
- `Cv2RansacEssentialSolver.solve(self, pts0, pts1)` — 行为见对应阶段教程及源码。
- `class PycolmapRansacTwoViewGeometrySolver()` — 行为见对应阶段教程及源码。
- `PycolmapRansacTwoViewGeometrySolver.__init__(self, camera_params: CameraParams)` — 行为见对应阶段教程及源码。
- `PycolmapRansacTwoViewGeometrySolver.get_K(self)` — 行为见对应阶段教程及源码。
- `PycolmapRansacTwoViewGeometrySolver.solve(self, pts0, pts1)` — 行为见对应阶段教程及源码。
- `class TwoPairSolver()` — 行为见对应阶段教程及源码。
- `TwoPairSolver.__init__(self, params: CameraParams, solver: str='pycolmap')` — 行为见对应阶段教程及源码。
- `TwoPairSolver.get_K(self)` — Returns:     K: np.ndarray, shape (3, 3), dtype=np.float32
- `TwoPairSolver.solve(self, pts0, pts1)` — Args:     pts0: np.ndarray, shape (N, 2), dtype=np.float32     pts1: np.ndarray, shape (N, 2), dtype=np.float32 Returns:     T: np.ndarray, shape (4, 4), dtype=np.float32
- `interpolate_missing_frames(T_w2c_list, sample_idxs)` — 对给定的 T_w2c_list（已知帧的变换矩阵）进行平滑插值，生成所有帧的变换矩阵。 其中：   - 平移部分采用线性插值；   - 旋转部分采用自实现的SLERP球面线性插值，保证旋转过渡平滑。

## `Retargeting/GVHMR/hmr4d/utils/preproc/relpose/transformation_np.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/relpose/transformation_np.py) · [使用教程](02_video.md) · 内容指纹 `77119cf87540`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `rotation_matrix_to_quaternion(R)` — 将 3x3 旋转矩阵 R 转换为四元数 [w, x, y, z] 的形式。
- `quaternion_to_rotation_matrix(q)` — 将四元数 [w, x, y, z] 转换为 3x3 旋转矩阵。
- `slerp(q0, q1, t)` — 对两个四元数 q0 和 q1 进行球面线性插值（SLERP）。
- `lerp_missing_frames(T_w2c_list, sample_idxs)` — 对给定的 T_w2c_list（已知帧的变换矩阵）进行平滑插值，生成所有帧的变换矩阵。 其中：   - 平移部分采用线性插值；   - 旋转部分采用自实现的SLERP球面线性插值，保证旋转过渡平滑。

## `Retargeting/GVHMR/hmr4d/utils/preproc/relpose/utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/relpose/utils.py) · [使用教程](02_video.md) · 内容指纹 `6e54d5fe6a96`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `visualize_matches(img0, img1, kp0, kp1, output_dir)` — Visualize the matched features between two images.
- `visualize_T_w2c_rotations(T_w2c_list, output_dir)` — 可视化相机旋转轨迹，并考虑 OpenCV 坐标系转换， 使得相机的 x 轴保持右向，z 轴（光轴）变为水平前向， 而相机的 y 轴（朝下）对应于 plt 的 -z 轴（即向下）。
- `visualize_rotation_angles(T_w2c_list, output_dir)` — Visualize rotation as Euler angles over time.
- `read_video_frame_np(video_path, frame_index)` — 行为见对应阶段教程及源码。
- `focal_length_from_mm(width, height, mm=24)` — Convert full-frame focal length to image sensor focal length.

## `Retargeting/GVHMR/hmr4d/utils/preproc/relpose/viz2d.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/relpose/viz2d.py) · [使用教程](02_video.md) · 内容指纹 `f3f92b190a5e`

职责：人体恢复、重定向及其内部数学/网络模块。

模块说明：2D visualization primitives based on Matplotlib. 1) Plot images with `plot_images`. 2) Call `plot_keypoints` or `plot_matches` any number of times. 3) Optionally: save a .png or .pdf plot (nice in papers!) with `save_plot`.

接口与职责：

- `cm_RdGn(x)` — Custom colormap: red (0) -> yellow (0.5) -> green (1).
- `cm_BlRdGn(x_)` — Custom colormap: blue (-1) -> red (0.0) -> green (1).
- `cm_prune(x_)` — Custom colormap to visualize pruning
- `plot_images(imgs, titles=None, cmaps='gray', dpi=100, pad=0.5, adaptive=True)` — Plot a set of images horizontally. Args:     imgs: list of NumPy RGB (H, W, 3) or PyTorch RGB (3, H, W) or mono (H, W).     titles: a list of strings, as titles for each image.     cmaps: colormaps for monochrome images.     adaptive: whether the figure size should fit the image aspect ratios.
- `plot_keypoints(kpts, colors='lime', ps=4, axes=None, a=1.0)` — Plot keypoints for existing images. Args:     kpts: list of ndarrays of size (N, 2).     colors: string, or list of list of tuples (one for each keypoints).     ps: size of the keypoints as float.
- `plot_matches(kpts0, kpts1, color=None, lw=1.5, ps=4, a=1.0, labels=None, axes=None)` — Plot matches for a pair of existing images. Args:     kpts0, kpts1: corresponding keypoints of size (N, 2).     color: color of each match, string or RGB tuple. Random if not given.     lw: width of the lines.     ps: size of the end points (no endpoint if ps=0)     indices: indices of the images to draw the matches on.     a: alpha opacity of the
- `add_text(idx, text, pos=(0.01, 0.99), fs=15, color='w', lcolor='k', lwidth=2, ha='left', va='top')` — 行为见对应阶段教程及源码。
- `save_plot(path, **kw)` — Save the current figure without any white margin.

## `Retargeting/GVHMR/hmr4d/utils/preproc/slam.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/slam.py) · [使用教程](02_video.md) · 内容指纹 `4bf43d120024`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class SLAMModel(object)` — 行为见对应阶段教程及源码。
- `SLAMModel.__init__(self, video_path, width, height, intrinsics=None, stride=1, skip=0, buffer=2048, resize=0.5)` — Args:     intrinsics: [fx, fy, cx, cy]
- `SLAMModel.track(self)` — 行为见对应阶段教程及源码。
- `SLAMModel.process(self)` — 行为见对应阶段教程及源码。
- `video_stream(queue, imagedir, intrinsics, stride, skip=0, resize=0.5)` — video generator

## `Retargeting/GVHMR/hmr4d/utils/preproc/tracker.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/tracker.py) · [使用教程](02_video.md) · 内容指纹 `0b32eeaddbdd`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class Tracker()` — 行为见对应阶段教程及源码。
- `Tracker.__init__(self) -> None` — 行为见对应阶段教程及源码。
- `Tracker.track(self, video_path)` — 行为见对应阶段教程及源码。
- `Tracker.sort_track_length(track_history, video_path)` — This handles the track history from YOLO tracker.
- `Tracker.get_one_track(self, video_path)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitfeat_extractor.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitfeat_extractor.py) · [使用教程](02_video.md) · 内容指纹 `c6cb61ba4b57`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `get_batch(input_path, bbx_xys, img_ds=0.5, img_dst_size=256, path_type='video')` — 行为见对应阶段教程及源码。
- `class Extractor()` — 行为见对应阶段教程及源码。
- `Extractor.__init__(self, tqdm_leave=True)` — 行为见对应阶段教程及源码。
- `Extractor.extract_video_features(self, video_path, bbx_xys, img_ds=0.5)` — img_ds makes the image smaller, which is useful for faster processing

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose.py) · [使用教程](02_video.md) · 内容指纹 `0cf3561d064b`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class VitPoseExtractor()` — 行为见对应阶段教程及源码。
- `VitPoseExtractor.__init__(self, tqdm_leave=True)` — 行为见对应阶段教程及源码。
- `VitPoseExtractor.extract(self, video_path, bbx_xys, img_ds=0.5)` — 行为见对应阶段教程及源码。
- `get_heatmap_preds(heatmap, normalize_keypoints=True, thr=0.0, soft=False)` — heatmap: (B, J, H, W)
- `soft_patch_dx_dy(p)` — p (B,J,P,P)

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/__init__.py) · [使用教程](02_video.md) · 内容指纹 `31e2153aa6e7`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/__init__.py) · [使用教程](02_video.md) · 内容指纹 `e3b0c44298fc`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/__init__.py) · [使用教程](02_video.md) · 内容指纹 `e3b0c44298fc`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/backbones/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/backbones/__init__.py) · [使用教程](02_video.md) · 内容指纹 `a03caae1b968`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/backbones/vit.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/backbones/vit.py) · [使用教程](02_video.md) · 内容指纹 `dc0eafd1f71e`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class DropPath(nn.Module)` — Drop paths (Stochastic Depth) per sample  (when applied in main path of residual blocks).
- `DropPath.__init__(self, drop_prob=None)` — 行为见对应阶段教程及源码。
- `DropPath.forward(self, x)` — 行为见对应阶段教程及源码。
- `DropPath.extra_repr(self)` — 行为见对应阶段教程及源码。
- `class Mlp(nn.Module)` — 行为见对应阶段教程及源码。
- `Mlp.__init__(self, in_features, hidden_features=None, out_features=None, act_layer=nn.GELU, drop=0.0)` — 行为见对应阶段教程及源码。
- `Mlp.forward(self, x)` — 行为见对应阶段教程及源码。
- `class Attention(nn.Module)` — 行为见对应阶段教程及源码。
- `Attention.__init__(self, dim, num_heads=8, qkv_bias=False, qk_scale=None, attn_drop=0.0, proj_drop=0.0, attn_head_dim=None)` — 行为见对应阶段教程及源码。
- `Attention.forward(self, x)` — 行为见对应阶段教程及源码。
- `class Block(nn.Module)` — 行为见对应阶段教程及源码。
- `Block.__init__(self, dim, num_heads, mlp_ratio=4.0, qkv_bias=False, qk_scale=None, drop=0.0, attn_drop=0.0, drop_path=0.0, act_layer=nn.GELU, norm_layer=nn.LayerNorm, attn_head_dim=None)` — 行为见对应阶段教程及源码。
- `Block.forward(self, x)` — 行为见对应阶段教程及源码。
- `class PatchEmbed(nn.Module)` — Image to Patch Embedding
- `PatchEmbed.__init__(self, img_size=224, patch_size=16, in_chans=3, embed_dim=768, ratio=1)` — 行为见对应阶段教程及源码。
- `PatchEmbed.forward(self, x, **kwargs)` — 行为见对应阶段教程及源码。
- `class HybridEmbed(nn.Module)` — CNN Feature Map Embedding Extract feature map from CNN, flatten, project to embedding dim.
- `HybridEmbed.__init__(self, backbone, img_size=224, feature_size=None, in_chans=3, embed_dim=768)` — 行为见对应阶段教程及源码。
- `HybridEmbed.forward(self, x)` — 行为见对应阶段教程及源码。
- `class ViT(nn.Module)` — 行为见对应阶段教程及源码。
- `ViT.__init__(self, img_size=224, patch_size=16, in_chans=3, num_classes=80, embed_dim=768, depth=12, num_heads=12, mlp_ratio=4.0, qkv_bias=False, qk_scale=None, drop_rate=0.0, attn_drop_rate=0.0, drop_path_rate=0.0, hybrid_backbone=None, norm_layer=None, use_checkpoint=False, frozen_stages=-1, ratio=1, last_norm=True, patch_padding='pad', freeze_attn=False, freeze_ffn=False)` — 行为见对应阶段教程及源码。
- `ViT._freeze_stages(self)` — Freeze parameters.
- `ViT.init_weights(self, pretrained=None)` — Initialize the weights in backbone. Args:     pretrained (str, optional): Path to pre-trained weights.         Defaults to None.
- `ViT.get_num_layers(self)` — 行为见对应阶段教程及源码。
- `ViT.no_weight_decay(self)` — 行为见对应阶段教程及源码。
- `ViT.forward_features(self, x)` — 行为见对应阶段教程及源码。
- `ViT.forward(self, x)` — 行为见对应阶段教程及源码。
- `ViT.train(self, mode=True)` — Convert the model into training mode.

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/heads/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/heads/__init__.py) · [使用教程](02_video.md) · 内容指纹 `4d3d444fb3bd`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/heads/topdown_heatmap_base_head.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/heads/topdown_heatmap_base_head.py) · [使用教程](02_video.md) · 内容指纹 `0fd1fab21cfe`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class TopdownHeatmapBaseHead(nn.Module)` — Base class for top-down heatmap heads.
- `TopdownHeatmapBaseHead.get_loss(self, **kwargs)` — Gets the loss.
- `TopdownHeatmapBaseHead.get_accuracy(self, **kwargs)` — Gets the accuracy.
- `TopdownHeatmapBaseHead.forward(self, **kwargs)` — Forward function.
- `TopdownHeatmapBaseHead.inference_model(self, **kwargs)` — Inference function.
- `TopdownHeatmapBaseHead.decode(self, img_metas, output, **kwargs)` — Decode keypoints from heatmaps.
- `TopdownHeatmapBaseHead._get_deconv_cfg(deconv_kernel)` — Get configurations for deconv layers.

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/heads/topdown_heatmap_simple_head.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/builder/heads/topdown_heatmap_simple_head.py) · [使用教程](02_video.md) · 内容指纹 `8804cb8b8ae7`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `build_conv_layer(cfg, *args, **kwargs) -> nn.Module` — LICENSE
- `build_upsample_layer(cfg, *args, **kwargs) -> nn.Module` — 行为见对应阶段教程及源码。
- `class TopdownHeatmapSimpleHead(TopdownHeatmapBaseHead)` — Top-down heatmap simple head. paper ref: Bin Xiao et al. ``Simple Baselines for Human Pose Estimation and Tracking``.
- `TopdownHeatmapSimpleHead.__init__(self, in_channels, out_channels, num_deconv_layers=3, num_deconv_filters=(256, 256, 256), num_deconv_kernels=(4, 4, 4), extra=None, in_index=0, input_transform=None, align_corners=False, loss_keypoint=None, train_cfg=None, test_cfg=None, upsample=0)` — 行为见对应阶段教程及源码。
- `TopdownHeatmapSimpleHead.get_loss(self, output, target, target_weight)` — Calculate top-down keypoint loss.
- `TopdownHeatmapSimpleHead.get_accuracy(self, output, target, target_weight)` — Calculate accuracy for top-down keypoint loss.
- `TopdownHeatmapSimpleHead.forward(self, x)` — Forward function.
- `TopdownHeatmapSimpleHead.inference_model(self, x, flip_pairs=None)` — Inference function.
- `TopdownHeatmapSimpleHead._init_inputs(self, in_channels, in_index, input_transform)` — Check and initialize input transforms.
- `TopdownHeatmapSimpleHead._transform_inputs(self, inputs)` — Transform inputs for decoder.
- `TopdownHeatmapSimpleHead._make_deconv_layer(self, num_layers, num_filters, num_kernels)` — Make deconv layers.
- `TopdownHeatmapSimpleHead.init_weights(self)` — Initialize model weights.

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/model_builder.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/model_builder.py) · [使用教程](02_video.md) · 内容指纹 `97cb0e67a9f7`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `build_model(model_name, checkpoint=None)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/__init__.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/__init__.py) · [使用教程](02_video.md) · 内容指纹 `e3b0c44298fc`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/convert_to_trt.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/convert_to_trt.py) · [使用教程](02_video.md) · 内容指纹 `f253e8deeeed`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`pose`, `x`, `net_trt`.

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/general_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/general_utils.py) · [使用教程](02_video.md) · 内容指纹 `d8e25fcf789d`

职责：人体恢复、重定向及其内部数学/网络模块。

模块说明：Created on Wed Jun 15 15:49:22 2022

接口与职责：

- `make_parser()` — 行为见对应阶段教程及源码。
- `jitter(tracking, temp, id1)` — 行为见对应阶段教程及源码。
- `jitter2(tracking, temp, id1)` — 行为见对应阶段教程及源码。
- `create_json_rabbitmq(FRAME_ID, pose)` — 行为见对应阶段教程及源码。
- `producer_rabbitmq()` — 行为见对应阶段教程及源码。
- `fix_head(xyz)` — 行为见对应阶段教程及源码。
- `flatten_lst(x)` — 行为见对应阶段教程及源码。
- `polys_from_pose(pts)` — 行为见对应阶段教程及源码。
- `fix_list_order(list_, list2)` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `--track_thresh` — default=0.2; help='tracking confidence threshold'
- `--track_buffer` — default=240; help='the frames for keep lost tracks'
- `--match_thresh` — default=0.8; help='matching threshold for tracking'
- `--aspect_ratio_thresh` — default=1.6; help='threshold for filtering out boxes of which aspect ratio are above the given value.'
- `--min_box_area` — default=10; help='filter out tiny boxes'
- `--mot20` — default=False; action='store_true'; help='test mot20.'

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/inference_test.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/inference_test.py) · [使用教程](02_video.md) · 内容指纹 `25e4dc5813e9`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`pose`, `device`, `dummy_input`, `repetitions`, `total_time`, `Throughput`.

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/logger_helper.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/logger_helper.py) · [使用教程](02_video.md) · 内容指纹 `73cabf060827`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class CustomFormatter(logging.Formatter)` — 行为见对应阶段教程及源码。
- `CustomFormatter.format(self, record)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/pose_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/pose_utils.py) · [使用教程](02_video.md) · 内容指纹 `2470d4c1fc27`

职责：人体恢复、重定向及其内部数学/网络模块。

模块说明：Created on Wed Jun 15 15:45:33 2022

接口与职责：

- `pose_points_yolo5(detector, image, pose, tracker, tensorrt)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/pose_viz.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/pose_viz.py) · [使用教程](02_video.md) · 内容指纹 `26d307984ac1`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `joints_dict()` — 行为见对应阶段教程及源码。
- `draw_points(image, points, color_palette='tab20', palette_samples=16, confidence_threshold=0.5)` — Draws `points` on `image`.
- `draw_skeleton(image, points, skeleton, color_palette='Set2', palette_samples=8, person_index=0, confidence_threshold=0.5)` — Draws a `skeleton` on `image`.
- `draw_points_and_skeleton(image, points, skeleton, points_color_palette='tab20', points_palette_samples=16, skeleton_color_palette='Set2', skeleton_palette_samples=8, person_index=0, confidence_threshold=0.5)` — Draws `points` and `skeleton` on `image`.
- `save_images(images, target, joint_target, output, joint_output, joint_visibility, summary_writer=None, step=0, prefix='')` — Creates a grid of images with gt joints and a grid with predicted joints. This is a basic function for debugging purposes only.
- `check_video_rotation(filename)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/timerr.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/timerr.py) · [使用教程](02_video.md) · 内容指纹 `72a834269d16`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `class Timer(object)` — A simple timer.
- `Timer.__init__(self)` — 行为见对应阶段教程及源码。
- `Timer.tic(self)` — 行为见对应阶段教程及源码。
- `Timer.toc(self, average=True)` — 行为见对应阶段教程及源码。
- `Timer.clear(self)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/visualizer.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/visualizer.py) · [使用教程](02_video.md) · 内容指纹 `2bce4edc1c9c`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `vis(img, boxes, scores, cls_ids, conf=0.5, class_names=None)` — 行为见对应阶段教程及源码。
- `get_color(idx)` — 行为见对应阶段教程及源码。
- `plot_tracking(image, tlwhs, obj_ids, scores=None, frame_id=0, fps=0.0, ids2=None)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/ViTPose_trt.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/preproc/vitpose_pytorch/src/vitpose_infer/pose_utils/ViTPose_trt.py) · [使用教程](02_video.md) · 内容指纹 `eb4b353f89a3`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `torch_device_from_trt(device)` — 行为见对应阶段教程及源码。
- `torch_dtype_from_trt(dtype)` — 行为见对应阶段教程及源码。
- `class TRTModule_ViTPose(torch.nn.Module)` — 行为见对应阶段教程及源码。
- `TRTModule_ViTPose.__init__(self, engine=None, input_names=None, output_names=None, input_flattener=None, output_flattener=None, path=None, device=None)` — 行为见对应阶段教程及源码。
- `TRTModule_ViTPose.forward(self, *inputs)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/pylogger.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/pylogger.py) · [使用教程](02_video.md) · 内容指纹 `7a30993a4190`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `sync_time()` — 行为见对应阶段教程及源码。
- `timer(sync_cuda=False, mem=False, loop=1)` — Args:     func: function     sync_cuda: bool, whether to synchronize cuda     mem: bool, whether to log memory
- `timed(fn)` — example usage: timed(lambda: model(inp))

## `Retargeting/GVHMR/hmr4d/utils/seq_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/seq_utils.py) · [使用教程](02_video.md) · 内容指纹 `b36e307f9a70`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `get_frame_id_list_from_mask(mask)` — Vectorized approach to get frame id list from a boolean mask.
- `get_batch_frame_id_lists_from_mask_BLC(masks)` — 处理三维掩码数组，为每个批次和通道提取连续True区段的索引列表。
- `get_frame_id_list_from_frame_id(frame_id)` — 行为见对应阶段教程及源码。
- `rearrange_by_mask(x, mask)` — x (L, *) mask (M,), M >= L
- `frame_id_to_mask(frame_id, max_len)` — 行为见对应阶段教程及源码。
- `mask_to_frame_id(mask)` — 行为见对应阶段教程及源码。
- `linear_interpolate_frame_ids(data, frame_id_list)` — 行为见对应阶段教程及源码。
- `linear_interpolate(data, N_middle_frames)` — Args:     data: (2, C) Returns:     data_interpolated: (1+N+1, C)
- `find_top_k_span(mask, k=3)` — Args:     mask: (L,) Return:     topk_span: List of tuple, usage: [start, end)

## `Retargeting/GVHMR/hmr4d/utils/smplx_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/smplx_utils.py) · [使用教程](02_video.md) · 内容指纹 `e4f9a663a068`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `make_smplx(type='neu_fullpose', **kwargs)` — 行为见对应阶段教程及源码。
- `load_parents(npz_path='models/smplx/SMPLX_NEUTRAL.npz')` — 行为见对应阶段教程及源码。
- `load_smpl_faces(npz_path='models/smplh/SMPLH_FEMALE.pkl')` — 行为见对应阶段教程及源码。
- `decompose_fullpose(fullpose, model_type='smplx')` — 行为见对应阶段教程及源码。
- `compose_fullpose(fullpose_dict, model_type='smplx')` — 行为见对应阶段教程及源码。
- `compute_R_from_kinetree(rot_mats, parents)` — operation of lbs/batch_rigid_transform, focus on 3x3 R only Parameters ---------- rot_mats: torch.tensor BxNx3x3     Tensor of rotation matrices parents : torch.tensor BxN     The kinematic tree of each object
- `compute_relR_from_kinetree(R, parents)` — Inverse operation of lbs/batch_rigid_transform, focus on 3x3 R only Parameters ---------- R : torch.tensor BxNx4x4 or BxNx3x3     Tensor of rotation matrices parents : torch.tensor BxN     The kinematic tree of each object
- `quat_mul(x, y)` — Performs quaternion multiplication on arrays of quaternions
- `quat_inv(q)` — Inverts a tensor of quaternions
- `quat_mul_vec(q, x)` — Performs multiplication of an array of 3D vectors by an array of quaternions (rotation).
- `inverse_kinematics_motion(global_pos, global_rot, parents=SMPLH_PARENTS)` — Args:     global_pos : (B, T, J-1, 3)     global_rot (q) : (B, T, J-1, 4)     parents : SMPLH_PARENTS Returns:     local_pos : (B, T, J-1, 3)     local_rot (q) : (B, T, J-1, 4)
- `transform_mat(R, t)` — Creates a batch of transformation matrices Args:     - R: Bx3x3 array of a batch of rotation matrices     - t: Bx3x1 array of a batch of translation vectors Returns:     - T: Bx4x4 Transformation matrix
- `normalize_joints(joints)` — Args:     joints: (B, *, J, 3)
- `compute_Rt_af2az(joints, inverse=False)` — Assume z coord is upward Args:     joints: (B, J, 3), in the start-frame Returns:     R_af2az: (B, 3, 3)     t_af2az: (B, 3)
- `finite_difference_forward(x, dim_t=1, dup_last=True)` — 行为见对应阶段教程及源码。
- `compute_joints_zero(betas, gender)` — Args:     betas: (16)     gender: 'male' or 'female' Returns:     joints_zero: (22, 3)

## `Retargeting/GVHMR/hmr4d/utils/video_io_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/video_io_utils.py) · [使用教程](02_video.md) · 内容指纹 `849dfd99c287`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `get_video_lwh(video_path)` — 行为见对应阶段教程及源码。
- `read_video_np(video_path, start_frame=0, end_frame=-1, scale=1.0)` — Args:     video_path: str Returns:     frames: np.array, (N, H, W, 3) RGB, uint8
- `get_video_reader(video_path)` — 行为见对应阶段教程及源码。
- `read_images_np(image_paths, verbose=False)` — Args:     image_paths: list of str Returns:     images: np.array, (N, H, W, 3) RGB, uint8
- `save_video(images, video_path, fps=30, crf=17)` — Args:     images: (N, H, W, 3) RGB, uint8     crf: 17 is visually lossless, 23 is default, +6 results in half the bitrate 0 is lossless, https://trac.ffmpeg.org/wiki/Encode/H.264#crf
- `get_writer(video_path, fps=30, crf=17)` — remember to .close()
- `copy_file(video_path, out_video_path, overwrite=True)` — 行为见对应阶段教程及源码。
- `merge_videos_horizontal(in_video_paths: list, out_video_path: str)` — 行为见对应阶段教程及源码。
- `merge_videos_vertical(in_video_paths: list, out_video_path: str)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/vis/cv2_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/vis/cv2_utils.py) · [使用教程](02_video.md) · 内容指纹 `6f944c1cb3e9`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `to_numpy(x)` — 行为见对应阶段教程及源码。
- `draw_bbx_xys_on_image(bbx_xys, image, conf=True)` — 行为见对应阶段教程及源码。
- `draw_bbx_xys_on_image_batch(bbx_xys_batch, image_batch, conf=None)` — conf: if provided, list of bool
- `draw_bbx_xyxy_on_image(bbx_xys, image, conf=True)` — 行为见对应阶段教程及源码。
- `draw_bbx_xyxy_on_image_batch(bbx_xyxy_batch, image_batch, mask=None, conf=None)` — Args:     conf: if provided, list of bool, mutually exclusive with mask     mask: whether to draw, historically used
- `draw_kpts(frame, keypoints, color=(0, 255, 0), thickness=2)` — 行为见对应阶段教程及源码。
- `draw_kpts_with_conf(frame, kp2d, conf, thickness=2)` — Args:     kp2d: (J, 2),     conf: (J,)
- `draw_kpts_with_conf_batch(frames, kp2d_batch, conf_batch, thickness=2)` — Args:     kp2d_batch: (B, J, 2),     conf_batch: (B, J)
- `draw_coco17_skeleton(img, keypoints, conf_thr=0)` — 行为见对应阶段教程及源码。
- `draw_coco17_skeleton_batch(imgs, keypoints_batch, conf_thr=0)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/vis/renderer.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/vis/renderer.py) · [使用教程](02_video.md) · 内容指纹 `3124701b4365`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `overlay_image_onto_background(image, mask, bbox, background)` — 行为见对应阶段教程及源码。
- `update_intrinsics_from_bbox(K_org, bbox)` — 行为见对应阶段教程及源码。
- `perspective_projection(x3d, K, R=None, T=None)` — 行为见对应阶段教程及源码。
- `compute_bbox_from_points(X, img_w, img_h, scaleFactor=1.2)` — 行为见对应阶段教程及源码。
- `class Renderer()` — 行为见对应阶段教程及源码。
- `Renderer.__init__(self, width, height, focal_length=None, device='cuda', faces=None, K=None, bin_size=None)` — set bin_size to 0 for no binning
- `Renderer.create_renderer(self)` — 行为见对应阶段教程及源码。
- `Renderer.create_camera(self, R=None, T=None)` — 行为见对应阶段教程及源码。
- `Renderer.initialize_camera_params(self, focal_length, K)` — 行为见对应阶段教程及源码。
- `Renderer.set_intrinsic(self, K)` — 行为见对应阶段教程及源码。
- `Renderer.set_ground(self, length, center_x, center_z)` — 行为见对应阶段教程及源码。
- `Renderer.update_bbox(self, x3d, scale=2.0, mask=None)` — Update bbox of cameras from the given 3d points
- `Renderer.reset_bbox(self)` — 行为见对应阶段教程及源码。
- `Renderer.render_mesh(self, vertices, background=None, colors=[0.8, 0.8, 0.8], VI=50)` — 行为见对应阶段教程及源码。
- `Renderer.render_with_ground(self, verts, colors, cameras, lights, faces=None)` — :param verts (N, V, 3), potential multiple people :param colors (N, 3) or (N, V, 3) :param faces (N, F, 3), optional, otherwise self.faces is used will be used
- `create_meshes(verts, faces, colors)` — :param verts (B, V, 3) :param faces (B, F, 3) :param colors (B, V, 3)
- `get_global_cameras(verts, device='cuda', distance=5, position=(-5.0, 5.0, 0.0))` — This always put object at the center of view
- `get_global_cameras_static(verts, beta=4.0, cam_height_degree=30, target_center_height=1.0, use_long_axis=False, vec_rot=45, device='cuda')` — 行为见对应阶段教程及源码。
- `get_ground_params_from_points(root_points, vert_points)` — xz-plane is the ground plane Args:     root_points: (L, 3), to decide center     vert_points: (L, V, 3), to decide scale

## `Retargeting/GVHMR/hmr4d/utils/vis/renderer_tools.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/vis/renderer_tools.py) · [使用教程](02_video.md) · 内容指纹 `a15206240963`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `read_image(path, scale=1)` — 行为见对应阶段教程及源码。
- `transform_torch3d(T_c2w)` — :param T_c2w (*, 4, 4) returns (*, 3, 3), (*, 3)
- `transform_pyrender(T_c2w)` — :param T_c2w (*, 4, 4)
- `smpl_to_geometry(verts, faces, vis_mask=None, track_ids=None)` — :param verts (B, T, V, 3) :param faces (F, 3) :param vis_mask (optional) (B, T) visibility of each person :param track_ids (optional) (B,) returns list of T verts (B, V, 3), faces (F, 3), colors (B, 3) where B is different depending on the visibility of the people
- `filter_visible_meshes(verts, colors, faces, vis_mask=None, vis_opacity=False)` — :param verts (B, T, V, 3) :param colors (B, 3) :param faces (F, 3) :param vis_mask (optional tensor, default None) (B, T) ternary mask     -1 if not in frame      0 if temporarily occluded      1 if visible :param vis_opacity (optional bool, default False)     if True, make occluded people alpha=0.5, otherwise alpha=1 returns a list of T lists vert
- `get_bboxes(verts, vis_mask)` — return bb_min, bb_max, and mean for each track (B, 3) over entire trajectory :param verts (B, T, V, 3) :param vis_mask (B, T)
- `track_to_colors(track_ids)` — :param track_ids (B)
- `get_colors()` — 行为见对应阶段教程及源码。
- `checkerboard_geometry(length=12.0, color0=[0.8, 0.9, 0.9], color1=[0.6, 0.7, 0.7], tile_width=0.5, alpha=1.0, up='y', c1=0.0, c2=0.0)` — 行为见对应阶段教程及源码。
- `camera_marker_geometry(radius, height, up)` — 行为见对应阶段教程及源码。
- `vis_keypoints(keypts_list, img_size, radius=6, thickness=3, kpt_score_thr=0.3, dataset='TopDownCocoDataset')` — Visualize keypoints From ViTPose/mmpose/apis/inference.py
- `imshow_keypoints(img, pose_result, skeleton=None, kpt_score_thr=0.3, pose_kpt_color=None, pose_link_color=None, radius=4, thickness=1, show_keypoint_weight=False)` — Draw keypoints and links on an image. From ViTPose/mmpose/core/visualization/image.py

## `Retargeting/GVHMR/hmr4d/utils/vis/renderer_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/vis/renderer_utils.py) · [使用教程](02_video.md) · 内容指纹 `2e92146d1301`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `simple_render_mesh(render_dict)` — Render an camera-space mesh, blank background
- `simple_render_mesh_background(render_dict, VI=50, colors=[0.8, 0.8, 0.8])` — Render an camera-space mesh, blank background

## `Retargeting/GVHMR/hmr4d/utils/vis/rich_logger.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/vis/rich_logger.py) · [使用教程](02_video.md) · 内容指纹 `c53cc8223aa2`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `print_cfg(cfg: DictConfig, use_rich: bool=False)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/hmr4d/utils/wis3d_utils.py`

[源码](../Retargeting/GVHMR/hmr4d/utils/wis3d_utils.py) · [使用教程](02_video.md) · 内容指纹 `388be6be8f7a`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `make_wis3d(output_dir='outputs/wis3d', name='debug', time_postfix=False)` — Make a Wis3D instance. e.g.:     from hmr4d.utils.wis3d_utils import make_wis3d     wis3d = make_wis3d(time_postfix=True)
- `get_gradient_colors(scheme='red', num_points=120, alpha=1.0)` — Return a list of colors that are gradient from start to end.
- `get_const_colors(name='red', partial_shape=(120, 5), alpha=1.0)` — Return colors (partial_shape, 4)
- `get_colors_by_conf(conf, low='red', high='green')` — 行为见对应阶段教程及源码。
- `convert_motion_as_line_mesh(motion, skeleton_type='smpl22', const_color=None)` — 行为见对应阶段教程及源码。
- `add_motion_as_lines(motion, wis3d, name='joints22', skeleton_type='smpl22', const_color=None, offset=0)` — Args:     motion (tensor): (L, J, 3)
- `add_prog_motion_as_lines(motion, wis3d, name='joints22', skeleton_type='smpl22')` — Args:     motion (tensor): (P, L, J, 3)
- `add_joints_motion_as_spheres(joints, wis3d, radius=0.05, name='joints', label_each_joint=False)` — Visualize skeleton as spheres to explore the skeleton. Args:     joints: (NF, NJ, 3)     wis3d     radius: radius of the spheres     name     label_each_joint: if True, each joints will have a label in wis3d (then you can interact with it, but it's slower)
- `create_skeleton_mesh(p1, p2, radius, color, resolution=4, return_merged=True)` — Create mesh between p1 and p2. Args:     p1 (torch.Tensor): (N, 3),     p2 (torch.Tensor): (N, 3),     radius (float): radius,     color (torch.Tensor): (N, 3)     resolution (int): number of vertices in one circle, denoted as Q Returns:     vertices (torch.Tensor): (N * 2Q, 3), if return_merged is False (N, 2Q, 3)     faces (torch.Tensor): (M', 3)
- `get_lines_of_my_frustum(frustum_points)` — frustum_points: (B, 8, 3), in (near {lu ru rd ld}, far {lu ru rd ld})
- `draw_colored_vec(wis3d, vec, name, radius=0.02, colors='r', starts=None, l=1.0)` — Args:     vec: (3) or (L, 3), should be the same length as colors, like 'rgb'
- `draw_T_w2c(wis3d, T_w2c, name, radius=0.01, all_in_one=True, l=0.1)` — Draw a camera trajectory in world coordinate. Args:     T_w2c: (L, 4, 4)
- `create_checkerboard_mesh(y=0.0, grid_size=1.0, bounds=((-3, -3), (3, 3)))` — example usage:     vertices, faces, vertex_colors = create_checkerboard_mesh()     wis3d.add_mesh(vertices=vertices, faces=faces, vertex_colors=vertex_colors, name="one")
- `add_a_trimesh(mesh, wis3d, name)` — 行为见对应阶段教程及源码。

## `Retargeting/GVHMR/setup.py`

[源码](../Retargeting/GVHMR/setup.py) · [使用教程](02_video.md) · 内容指纹 `2df0237d08e9`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `Retargeting/GVHMR/tools/demo/demo.py`

[源码](../Retargeting/GVHMR/tools/demo/demo.py) · [使用教程](02_video.md) · 内容指纹 `ca02504405cd`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `parse_args_to_cfg()` — 行为见对应阶段教程及源码。
- `run_preprocess(cfg)` — 行为见对应阶段教程及源码。
- `load_data_dict(cfg)` — 行为见对应阶段教程及源码。
- `render_incam(cfg)` — 行为见对应阶段教程及源码。
- `render_global(cfg)` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `--video` — default='inputs/demo/dance_3.mp4'
- `--output_root` — default=None; help='by default to outputs/demo'
- `-s, --static_cam` — action='store_true'; help='If true, skip DPVO'
- `--use_dpvo` — action='store_true'; help='If true, use DPVO. By default not using DPVO.'
- `--f_mm` — default=None; help='Focal length of fullframe camera in mm. Leave it as None to use default values.For iPhone 15p, the [0.5x, 1x, 2x, 3x] lens have typical values [13, 24, 48, 77].If the camera zoom in a lot, you can try 135, 200 or even larger values.'
- `--verbose` — action='store_true'; help='If true, draw intermediate results'

## `Retargeting/GVHMR/tools/demo/demo_folder.py`

[源码](../Retargeting/GVHMR/tools/demo/demo_folder.py) · [使用教程](02_video.md) · 内容指纹 `ca35b2cfbdb6`

职责：人体恢复、重定向及其内部数学/网络模块。

使用方式：包注册、常量或参数配置，由上级模块导入。

命令行参数（运行所在目录与完整例子见上方教程）：

- `-f, --folder` — required=True
- `-d, --output_root` — default=None
- `-s, --static_cam` — action='store_true'; help='If true, skip DPVO'

## `Retargeting/GVHMR/tools/video/merge_folder.py`

[源码](../Retargeting/GVHMR/tools/video/merge_folder.py) · [使用教程](02_video.md) · 内容指纹 `cf592cb9d367`

职责：人体恢复、重定向及其内部数学/网络模块。

模块说明：This script will glob two folder, check the mp4 files are one-to-one match precisely, then call merge_horizontal.py to merge them one by one

接口与职责：

- `main()` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `input_dir1`
- `input_dir2`
- `output_dir`
- `--vertical` — action='store_true'

## `Retargeting/GVHMR/tools/video/merge_horizontal.py`

[源码](../Retargeting/GVHMR/tools/video/merge_horizontal.py) · [使用教程](02_video.md) · 内容指纹 `91a7142860c0`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `parse_args()` — python tools/video/merge_horizontal.py a.mp4 b.mp4 c.mp4 -o out.mp4

命令行参数（运行所在目录与完整例子见上方教程）：

- `input_videos` — help='Input video paths'
- `-o, --output` — required=True; help='Output video path'

## `Retargeting/GVHMR/tools/video/merge_vertical.py`

[源码](../Retargeting/GVHMR/tools/video/merge_vertical.py) · [使用教程](02_video.md) · 内容指纹 `ea249422e5d0`

职责：人体恢复、重定向及其内部数学/网络模块。

接口与职责：

- `parse_args()` — python tools/video/merge_vertical.py a.mp4 b.mp4 c.mp4 -o out.mp4

命令行参数（运行所在目录与完整例子见上方教程）：

- `input_videos` — help='Input video paths'
- `-o, --output` — required=True; help='Output video path'

## `RL_envs/scripts/tracking.py`

[源码](../RL_envs/scripts/tracking.py) · [使用教程](04_training.md) · 内容指纹 `86fd82cbe534`

职责：tracking_single 的训练、配置与 MDP。

模块说明：Train, play or export a single reference. See docs/04_training.md. Requires Isaac Lab 2.3.x and RSL-RL 3.0.1. Help does not start Isaac.

接口与职责：

- `main()` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `mode` — choices=['train', 'play', 'export']
- `--motion` — required=True
- `--task` — default='G1-Tracking-Dance-demo'
- `--checkpoint`
- `--output`
- `--num-envs` — default=4096
- `--iterations` — default=5000
- `--steps` — default=1000
- `--seed` — default=42

## `RL_envs/source/WBC/setup.py`

[源码](../RL_envs/source/WBC/setup.py) · [使用教程](04_training.md) · 内容指纹 `8b247c61b3aa`

职责：tracking_single 的训练、配置与 MDP。

模块说明：Install only the extracted single-motion WBC task (editable install).

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/__init__.py`

[源码](../RL_envs/source/WBC/WBC/__init__.py) · [使用教程](04_training.md) · 内容指纹 `6c5f6194937e`

职责：tracking_single 的训练、配置与 MDP。

模块说明：WBC: capability-layered RL package for G1 humanoid loco-manipulation.

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`__all__`.

## `RL_envs/source/WBC/WBC/assets/__init__.py`

[源码](../RL_envs/source/WBC/WBC/assets/__init__.py) · [使用教程](04_training.md) · 内容指纹 `d8a22be14aab`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`ASSET_DIR`.

## `RL_envs/source/WBC/WBC/tasks/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/__init__.py) · [使用教程](04_training.md) · 内容指纹 `432ce95be658`

职责：tracking_single 的训练、配置与 MDP。

模块说明：Register only the four migrated tracking environments after AppLauncher starts.

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/__init__.py) · [使用教程](04_training.md) · 内容指纹 `07b7c09af478`

职责：tracking_single 的训练、配置与 MDP。

模块说明：Single-motion manager-based tasks.

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/__init__.py) · [使用教程](04_training.md) · 内容指纹 `e3b0c44298fc`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/agents/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/agents/__init__.py) · [使用教程](04_training.md) · 内容指纹 `3849c25159e7`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/agents/rsl_rl_ppo_cfg.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/agents/rsl_rl_ppo_cfg.py) · [使用教程](04_training.md) · 内容指纹 `4fd03aedc7d7`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `class G1TrackingPPORunnerCfg(RslRlOnPolicyRunnerCfg)` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/__init__.py) · [使用教程](04_training.md) · 内容指纹 `ed866b92f65e`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/commands.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/commands.py) · [使用教程](04_training.md) · 内容指纹 `75a7b116c225`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `class MotionLoader()` — 行为见对应阶段教程及源码。
- `MotionLoader.__init__(self, motion_file: str, body_names: Sequence[str], joint_names: Sequence[str], device: str='cpu')` — 行为见对应阶段教程及源码。
- `MotionLoader.body_pos_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionLoader.body_quat_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionLoader.body_lin_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionLoader.body_ang_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `class MotionCommand(CommandTerm)` — 行为见对应阶段教程及源码。
- `MotionCommand.__init__(self, cfg: MotionCommandCfg, env: ManagerBasedRLEnv)` — 行为见对应阶段教程及源码。
- `MotionCommand.command(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.joint_pos(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.joint_vel(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.body_pos_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.body_quat_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.body_lin_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.body_ang_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.anchor_pos_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.anchor_quat_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.anchor_lin_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.anchor_ang_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_joint_pos(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_joint_vel(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_body_pos_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_body_quat_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_body_lin_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_body_ang_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_anchor_pos_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_anchor_quat_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_anchor_lin_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand.robot_anchor_ang_vel_w(self) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `MotionCommand._update_metrics(self)` — 行为见对应阶段教程及源码。
- `MotionCommand._adaptive_sampling(self, env_ids: Sequence[int])` — 行为见对应阶段教程及源码。
- `MotionCommand._resample_command(self, env_ids: Sequence[int])` — 行为见对应阶段教程及源码。
- `MotionCommand._update_command(self)` — 行为见对应阶段教程及源码。
- `MotionCommand._set_debug_vis_impl(self, debug_vis: bool)` — 行为见对应阶段教程及源码。
- `MotionCommand._debug_vis_callback(self, event)` — 行为见对应阶段教程及源码。
- `class MotionCommandCfg(CommandTermCfg)` — Configuration for the motion command.

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/events.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/events.py) · [使用教程](04_training.md) · 内容指纹 `544cd928c1d0`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `randomize_joint_default_pos(env: ManagerBasedEnv, env_ids: torch.Tensor | None, asset_cfg: SceneEntityCfg, pos_distribution_params: tuple[float, float] | None=None, operation: Literal['add', 'scale', 'abs']='abs', distribution: Literal['uniform', 'log_uniform', 'gaussian']='uniform')` — 行为见对应阶段教程及源码。
- `randomize_rigid_body_com(env: ManagerBasedEnv, env_ids: torch.Tensor | None, com_range: dict[str, tuple[float, float]], asset_cfg: SceneEntityCfg)` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/observations.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/observations.py) · [使用教程](04_training.md) · 内容指纹 `84f0bef77e08`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `robot_anchor_ori_w(env: ManagerBasedEnv, command_name: str) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `robot_anchor_lin_vel_w(env: ManagerBasedEnv, command_name: str) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `robot_anchor_ang_vel_w(env: ManagerBasedEnv, command_name: str) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `robot_body_pos_b(env: ManagerBasedEnv, command_name: str) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `robot_body_ori_b(env: ManagerBasedEnv, command_name: str) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `motion_anchor_pos_b(env: ManagerBasedEnv, command_name: str) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `motion_anchor_ori_b(env: ManagerBasedEnv, command_name: str) -> torch.Tensor` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/rewards.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/rewards.py) · [使用教程](04_training.md) · 内容指纹 `5d24b072398c`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `_get_body_indexes(command: MotionCommand, body_names: list[str] | None) -> list[int]` — 行为见对应阶段教程及源码。
- `motion_global_anchor_position_error_exp(env: ManagerBasedRLEnv, command_name: str, std: float) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `motion_global_anchor_orientation_error_exp(env: ManagerBasedRLEnv, command_name: str, std: float) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `motion_relative_body_position_error_exp(env: ManagerBasedRLEnv, command_name: str, std: float, body_names: list[str] | None=None) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `motion_relative_body_orientation_error_exp(env: ManagerBasedRLEnv, command_name: str, std: float, body_names: list[str] | None=None) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `motion_global_body_linear_velocity_error_exp(env: ManagerBasedRLEnv, command_name: str, std: float, body_names: list[str] | None=None) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `motion_global_body_angular_velocity_error_exp(env: ManagerBasedRLEnv, command_name: str, std: float, body_names: list[str] | None=None) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `feet_contact_time(env: ManagerBasedRLEnv, sensor_cfg: SceneEntityCfg, threshold: float) -> torch.Tensor` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/terminations.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/mdp/terminations.py) · [使用教程](04_training.md) · 内容指纹 `7bc154d8021a`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `bad_anchor_pos(env: ManagerBasedRLEnv, command_name: str, threshold: float) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `bad_anchor_pos_z_only(env: ManagerBasedRLEnv, command_name: str, threshold: float) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `bad_anchor_ori(env: ManagerBasedRLEnv, asset_cfg: SceneEntityCfg, command_name: str, threshold: float) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `bad_motion_body_pos(env: ManagerBasedRLEnv, command_name: str, threshold: float, body_names: list[str] | None=None) -> torch.Tensor` — 行为见对应阶段教程及源码。
- `bad_motion_body_pos_z_only(env: ManagerBasedRLEnv, command_name: str, threshold: float, body_names: list[str] | None=None) -> torch.Tensor` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/__init__.py) · [使用教程](04_training.md) · 内容指纹 `8864c8928c14`

职责：tracking_single 的训练、配置与 MDP。

模块说明：G1 robot variants for single-reference tracking; see docs/04_training.md.

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/actuator.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/actuator.py) · [使用教程](04_training.md) · 内容指纹 `b095687e937f`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `class DelayedImplicitActuator(ImplicitActuator)` — Ideal PD actuator with delayed command application.
- `DelayedImplicitActuator.__init__(self, cfg: DelayedImplicitActuatorCfg, *args, **kwargs)` — 行为见对应阶段教程及源码。
- `DelayedImplicitActuator.reset(self, env_ids: Sequence[int])` — 行为见对应阶段教程及源码。
- `DelayedImplicitActuator.compute(self, control_action: ArticulationActions, joint_pos: torch.Tensor, joint_vel: torch.Tensor) -> ArticulationActions` — 行为见对应阶段教程及源码。
- `class DelayedImplicitActuatorCfg(ImplicitActuatorCfg)` — Configuration for a delayed PD actuator.

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/__init__.py) · [使用教程](04_training.md) · 内容指纹 `e3b0c44298fc`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_demo/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_demo/__init__.py) · [使用教程](04_training.md) · 内容指纹 `3e5042c3cfc7`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_demo/g1.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_demo/g1.py) · [使用教程](04_training.md) · 内容指纹 `3b1dad411aa2`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`ARMATURE_5020`, `ARMATURE_7520_14`, `ARMATURE_7520_22`, `ARMATURE_4010`, `NATURAL_FREQ`, `DAMPING_RATIO`, `STIFFNESS_5020`, `STIFFNESS_7520_14`, `STIFFNESS_7520_22`, `STIFFNESS_4010`, `DAMPING_5020`, `DAMPING_7520_14`, `DAMPING_7520_22`, `DAMPING_4010`, `G1_CYLINDER_CFG`, `G1_ACTION_SCALE`.

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_demo/tracking_env_cfg.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_demo/tracking_env_cfg.py) · [使用教程](04_training.md) · 内容指纹 `9ce02a574eb0`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `class TrackingSceneCfg(InteractiveSceneCfg)` — 行为见对应阶段教程及源码。
- `class TrackingCommandsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingObservationsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingActionsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingTerminationsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingEventsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingRewardsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingCurriculumCfg()` — 行为见对应阶段教程及源码。
- `class TrackingEnvCfg(ManagerBasedRLEnvCfg)` — 行为见对应阶段教程及源码。
- `TrackingEnvCfg.__post_init__(self)` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo/__init__.py) · [使用教程](04_training.md) · 内容指纹 `0e642282ad62`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo/g1.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo/g1.py) · [使用教程](04_training.md) · 内容指纹 `3b1dad411aa2`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`ARMATURE_5020`, `ARMATURE_7520_14`, `ARMATURE_7520_22`, `ARMATURE_4010`, `NATURAL_FREQ`, `DAMPING_RATIO`, `STIFFNESS_5020`, `STIFFNESS_7520_14`, `STIFFNESS_7520_22`, `STIFFNESS_4010`, `DAMPING_5020`, `DAMPING_7520_14`, `DAMPING_7520_22`, `DAMPING_4010`, `G1_CYLINDER_CFG`, `G1_ACTION_SCALE`.

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo/tracking_env_cfg.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo/tracking_env_cfg.py) · [使用教程](04_training.md) · 内容指纹 `9ce02a574eb0`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `class TrackingSceneCfg(InteractiveSceneCfg)` — 行为见对应阶段教程及源码。
- `class TrackingCommandsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingObservationsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingActionsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingTerminationsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingEventsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingRewardsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingCurriculumCfg()` — 行为见对应阶段教程及源码。
- `class TrackingEnvCfg(ManagerBasedRLEnvCfg)` — 行为见对应阶段教程及源码。
- `TrackingEnvCfg.__post_init__(self)` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo1_0/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo1_0/__init__.py) · [使用教程](04_training.md) · 内容指纹 `7a625636b5e7`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo1_0/g1.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo1_0/g1.py) · [使用教程](04_training.md) · 内容指纹 `3b1dad411aa2`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`ARMATURE_5020`, `ARMATURE_7520_14`, `ARMATURE_7520_22`, `ARMATURE_4010`, `NATURAL_FREQ`, `DAMPING_RATIO`, `STIFFNESS_5020`, `STIFFNESS_7520_14`, `STIFFNESS_7520_22`, `STIFFNESS_4010`, `DAMPING_5020`, `DAMPING_7520_14`, `DAMPING_7520_22`, `DAMPING_4010`, `G1_CYLINDER_CFG`, `G1_ACTION_SCALE`.

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo1_0/tracking_env_cfg.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo1_0/tracking_env_cfg.py) · [使用教程](04_training.md) · 内容指纹 `9ce02a574eb0`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `class TrackingSceneCfg(InteractiveSceneCfg)` — 行为见对应阶段教程及源码。
- `class TrackingCommandsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingObservationsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingActionsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingTerminationsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingEventsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingRewardsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingCurriculumCfg()` — 行为见对应阶段教程及源码。
- `class TrackingEnvCfg(ManagerBasedRLEnvCfg)` — 行为见对应阶段教程及源码。
- `TrackingEnvCfg.__post_init__(self)` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo_fps60/__init__.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo_fps60/__init__.py) · [使用教程](04_training.md) · 内容指纹 `4b74ae7d7053`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo_fps60/g1.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo_fps60/g1.py) · [使用教程](04_training.md) · 内容指纹 `3b1dad411aa2`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`ARMATURE_5020`, `ARMATURE_7520_14`, `ARMATURE_7520_22`, `ARMATURE_4010`, `NATURAL_FREQ`, `DAMPING_RATIO`, `STIFFNESS_5020`, `STIFFNESS_7520_14`, `STIFFNESS_7520_22`, `STIFFNESS_4010`, `DAMPING_5020`, `DAMPING_7520_14`, `DAMPING_7520_22`, `DAMPING_4010`, `G1_CYLINDER_CFG`, `G1_ACTION_SCALE`.

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo_fps60/tracking_env_cfg.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/g1_29dof/dance_mo_fps60/tracking_env_cfg.py) · [使用教程](04_training.md) · 内容指纹 `9ce02a574eb0`

职责：tracking_single 的训练、配置与 MDP。

接口与职责：

- `class TrackingSceneCfg(InteractiveSceneCfg)` — 行为见对应阶段教程及源码。
- `class TrackingCommandsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingObservationsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingActionsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingTerminationsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingEventsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingRewardsCfg()` — 行为见对应阶段教程及源码。
- `class TrackingCurriculumCfg()` — 行为见对应阶段教程及源码。
- `class TrackingEnvCfg(ManagerBasedRLEnvCfg)` — 行为见对应阶段教程及源码。
- `TrackingEnvCfg.__post_init__(self)` — 行为见对应阶段教程及源码。

## `RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/smpl.py`

[源码](../RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/robots/smpl.py) · [使用教程](04_training.md) · 内容指纹 `d043f68af8f2`

职责：tracking_single 的训练、配置与 MDP。

使用方式：包注册、常量或参数配置，由上级模块导入。 顶层配置：`SMPL_HUMANOID_CFG`.

## `tests/conftest.py`

[源码](../tests/conftest.py) · [使用教程](07_validation.md) · 内容指纹 `e369124fcc8e`

职责：离线回归测试；按测试函数查看保护的行为。

模块说明：Synthetic infrastructure fixtures, never represented as a trained policy.

接口与职责：

- `model()` — 行为见对应阶段教程及源码。
- `motion(model)` — 行为见对应阶段教程及源码。
- `bundle(tmp_path, motion)` — 行为见对应阶段教程及源码。

## `tests/test_conversion_cli.py`

[源码](../tests/test_conversion_cli.py) · [使用教程](07_validation.md) · 内容指纹 `cdf9bafc66ad`

职责：离线回归测试；按测试函数查看保护的行为。

模块说明：Exercise actual CLI serialization and the original dropped-frame regression.

接口与职责：

- `test_convert_cli_from_gmr_to_named_archive(tmp_path, model)` — 行为见对应阶段教程及源码。
- `test_gmr_export_includes_frame_zero_and_exact_count(monkeypatch, tmp_path, model, frame_count)` — 行为见对应阶段教程及源码。

## `tests/test_deploy.py`

[源码](../tests/test_deploy.py) · [使用教程](07_validation.md) · 内容指纹 `54cf8a5d3656`

职责：离线回归测试；按测试函数查看保护的行为。

模块说明：CPU ONNX/FK/transport contract tests; no robot or learned checkpoint needed.

接口与职责：

- `test_observation_layout_and_orientation()` — 行为见对应阶段教程及源码。
- `test_bundle_inference_and_motion_end(bundle)` — 行为见对应阶段教程及源码。
- `test_bundle_checksum_detects_swapped_motion(bundle)` — 行为见对应阶段教程及源码。
- `test_bad_observation_order_rejected(bundle)` — 行为见对应阶段教程及源码。
- `test_cpu_dynamic_smoke_with_synthetic_zero_policy(bundle, tmp_path)` — 行为见对应阶段教程及源码。
- `test_pelvis_and_torso_imu_equivalence()` — 行为见对应阶段教程及源码。

## `tests/test_motion.py`

[源码](../tests/test_motion.py) · [使用教程](07_validation.md) · 内容指纹 `5bc2e8c200e5`

职责：离线回归测试；按测试函数查看保护的行为。

模块说明：Regression coverage for timing, quaternions, names and real robot assets.

接口与职责：

- `test_resampling_preserves_first_frame_duration_and_rotation()` — 行为见对应阶段教程及源码。
- `test_bad_fps_rejected(motion, fps)` — 行为见对应阶段教程及源码。
- `test_duplicate_names_and_nan_rejected(motion)` — 行为见对应阶段教程及源码。
- `test_order_mapping()` — 行为见对应阶段教程及源码。
- `test_angular_velocity_is_world_frame_and_sign_invariant()` — 行为见对应阶段教程及源码。
- `test_real_g1_archive_has_named_29_dof_and_unit_quaternions(motion)` — 行为见对应阶段教程及源码。
- `test_linear_velocity_tracks_com_when_link_origin_is_stationary(model)` — 行为见对应阶段教程及源码。
- `test_urdf_joint_names_and_meshes_are_complete(model)` — 行为见对应阶段教程及源码。

## `tools/audit_docs.py`

[源码](../tools/audit_docs.py) · [使用教程](07_validation.md) · 内容指纹 `41980b835d0d`

职责：维护教程覆盖及检查记录。

模块说明：Generate/check a per-file tutorial and API index. See docs/07_validation.md.

接口与职责：

- `sources()` — 行为见对应阶段教程及源码。
- `guide_for(path)` — 行为见对应阶段教程及源码。
- `signature(node)` — 行为见对应阶段教程及源码。
- `render()` — 行为见对应阶段教程及源码。
- `main()` — 行为见对应阶段教程及源码。

命令行参数（运行所在目录与完整例子见上方教程）：

- `--write` — action='store_true'; help='Regenerate code_reference.md after reviewing guides'
