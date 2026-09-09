"""Convert Unitree motor/IMU measurements to the actor's pelvis/torso frames.

The selected IMU frame must match the robot firmware. See Deploy/docs/06_real_robot.md.
"""
import numpy as np
from GMR.pipeline.motion import ROBOT_XML
from .runtime import rotation

MOTOR_NAMES = (
    [f'{side}_{joint}_joint' for side in ('left','right') for joint in
     ('hip_pitch','hip_roll','hip_yaw','knee','ankle_pitch','ankle_roll')]
    + ['waist_yaw_joint','waist_roll_joint','waist_pitch_joint']
    + [f'{side}_{joint}_joint' for side in ('left','right') for joint in
       ('shoulder_pitch','shoulder_roll','shoulder_yaw','elbow','wrist_roll','wrist_pitch','wrist_yaw')]
)

class RobotState:
    """Use migrated robot FK, including waist motion, to resolve the anchor IMU."""
    def __init__(self, joint_names, anchor='torso_link', robot_xml=ROBOT_XML):
        import mujoco
        self.model = mujoco.MjModel.from_xml_path(str(robot_xml))
        self.data = mujoco.MjData(self.model)
        ids = [self.model.joint(n).id for n in joint_names]
        self.qa = self.model.jnt_qposadr[ids]
        self.va = self.model.jnt_dofadr[ids]
        self.anchor = self.model.body(anchor).id
        self.torso = self.model.body('torso_link').id

    def estimate(self, q, dq, imu_wxyz, gyro, imu_frame):
        """Return pelvis gyro and world anchor quaternion from pelvis or torso IMU."""
        import mujoco
        q, dq, gyro = map(np.asarray, (q,dq,gyro))
        if q.shape != (29,) or dq.shape != (29,) or gyro.shape != (3,) or not all(np.isfinite(x).all() for x in (q,dq,gyro)):
            raise ValueError('Invalid joint or gyro measurements')
        self.data.qpos[:] = 0
        self.data.qpos[3] = 1
        self.data.qvel[:] = 0
        self.data.qpos[self.qa] = q
        self.data.qvel[self.va] = dq
        mujoco.mj_forward(self.model, self.data)
        measured = rotation(imu_wxyz)
        if imu_frame == 'pelvis':
            base, base_gyro = measured, gyro
        elif imu_frame == 'torso':
            relative = rotation(self.data.xquat[self.torso])
            base = measured * relative.inv()
            velocity = np.zeros(6)
            mujoco.mj_objectVelocity(self.model, self.data, mujoco.mjtObj.mjOBJ_BODY, self.torso, velocity, 0)
            base_gyro = relative.apply(gyro) - velocity[:3]
        else:
            raise ValueError('imu_frame must be explicitly pelvis or torso')
        anchor = base * rotation(self.data.xquat[self.anchor])
        anchor_xyzw = anchor.as_quat()
        return base_gyro, anchor_xyzw[[3,0,1,2]], base
