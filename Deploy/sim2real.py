"""G1 29-DoF single-motion transport; read-only unless --execute is supplied.

The low-command transport follows Unitree SDK2's G1 PR-mode protocol. Real robot
validation is still required. See Deploy/docs/06_real_robot.md before executing.
"""
import argparse
from pathlib import Path
import threading
import time
import numpy as np
from GMR.pipeline.motion import name_indices
from .runtime import TrackingPolicy, rotation
from .robot_state import RobotState, MOTOR_NAMES

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--interface', required=True, help='Robot Ethernet interface, e.g. enp3s0')
    parser.add_argument('--imu-frame', required=True, choices=['pelvis','torso'], help='Verify against your firmware')
    parser.add_argument('--execute', action='store_true', help='Enable low-level motor commands after startup checks')
    parser.add_argument('--seconds', type=float, default=10, help='Read-only diagnostic duration')
    args = parser.parse_args()
    if not np.isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    policy = TrackingPolicy(args.bundle)
    c = policy.config
    estimator = RobotState(c['joint_names'], c['anchor_body_name'])
    motor_ids = name_indices(MOTOR_NAMES, c['joint_names'])
    from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber, ChannelPublisher
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_, LowCmd_
    ChannelFactoryInitialize(0, args.interface)
    lock = threading.Lock()
    latest = [None, 0.0]
    def receive(message):
        with lock:
            latest[:] = [message, time.monotonic()]
    subscriber = ChannelSubscriber('rt/lowstate', LowState_)
    subscriber.Init(receive, 10)
    def snapshot():
        with lock:
            msg, stamp = latest
        if msg is None or time.monotonic()-stamp > 0.1:
            raise RuntimeError('LowState missing or stale for >100 ms')
        q = np.asarray([msg.motor_state[i].q for i in motor_ids])
        dq = np.asarray([msg.motor_state[i].dq for i in motor_ids])
        gyro, anchor, base = estimator.estimate(q,dq,msg.imu_state.quaternion,msg.imu_state.gyroscope,args.imu_frame)
        remote = bytes(msg.wireless_remote)
        if len(remote) < 4:
            raise RuntimeError('Wireless remote packet is missing button bits')
        buttons = int.from_bytes(remote[2:4], 'little')
        return msg, q, dq, gyro, anchor, base, buttons
    deadline = time.monotonic()+5
    while latest[0] is None and time.monotonic() < deadline:
        time.sleep(0.01)
    initial = snapshot()
    if not args.execute:
        deadline = time.monotonic()+args.seconds
        while time.monotonic() < deadline:
            msg,q,dq,gyro,anchor,base,buttons = snapshot()
            print(f'Read-only: max |dq|={max(abs(dq)):.3f}, mode={msg.mode_machine}, buttons={buttons}')
            time.sleep(0.5)
        return
    from unitree_sdk2py.comm.motion_switcher.motion_switcher_client import MotionSwitcherClient
    switcher = MotionSwitcherClient()
    switcher.SetTimeout(5.0)
    switcher.Init()
    status, mode = switcher.CheckMode()
    if status != 0 or mode.get('name'):
        raise RuntimeError('Another motion controller is active. Release it using the operator procedure, then retry')
    msg,q,dq,gyro,anchor,base,buttons = snapshot()
    reference_q = policy.motion['joint_pos'][0, policy.indices]
    reference_anchor = policy.motion['body_quat_w'][0, policy.anchor]
    if max(abs(q-reference_q)) > 0.2 or np.linalg.norm((rotation(anchor).inv()*rotation(reference_anchor)).as_rotvec()) > 0.25:
        raise RuntimeError('Robot must be supported and aligned to reference frame 0 (joints <0.2 rad, anchor <0.25 rad)')
    if buttons or max(abs(dq)) > 0.3:
        raise RuntimeError('Release remote buttons and stop robot motion before activation')
    from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
    from unitree_sdk2py.utils.crc import CRC
    from unitree_sdk2py.utils.thread import RecurrentThread
    publisher = ChannelPublisher('rt/lowcmd', LowCmd_)
    publisher.Init()
    crc = CRC()
    command = unitree_hg_msg_dds__LowCmd_()
    command.mode_pr = 0
    command.mode_machine = msg.mode_machine
    target = [q.copy(), 0.0]
    active = threading.Event()
    fault = threading.Event()
    def publish():
        now = time.monotonic()
        with lock:
            desired, stamp = target[0].copy(), target[1]
            state_msg, state_stamp = latest
        state_remote = bytes(state_msg.wireless_remote) if state_msg is not None else b''
        stop_button = len(state_remote) < 4 or int.from_bytes(state_remote[2:4], 'little') != 0
        stale = now-stamp > 0.1 or now-state_stamp > 0.1 or stop_button
        if active.is_set() and stale:
            fault.set()
        driving = active.is_set() and not fault.is_set()
        for j, motor in enumerate(motor_ids):
            m = command.motor_cmd[int(motor)]
            m.mode, m.q, m.dq, m.tau = 1, float(desired[j]), 0., 0.
            m.kp = float(c['kp'][j]) if driving else 0.
            m.kd = float(c['kd'][j]) if driving else 3.
        command.crc = crc.Crc(command)
        publisher.Write(command)
    writer = RecurrentThread(interval=0.002, target=publish, name='tracking_lowcmd')
    writer.Start()
    try:
        start = time.monotonic()
        for frame in range(len(policy.motion['joint_pos'])):
            due = start + frame*c['control_dt']
            time.sleep(max(0, due-time.monotonic()))
            if time.monotonic()-due > c['control_dt'] or fault.is_set():
                raise RuntimeError('Missed policy deadline or transport watchdog stopped control')
            msg,q,dq,gyro,anchor,base,buttons = snapshot()
            if buttons or np.arccos(np.clip(base.as_matrix()[2,2],-1,1)) > 0.8:
                raise RuntimeError('Remote stop or excessive base tilt')
            desired,_ = policy.step(frame,q,dq,gyro,anchor)
            if max(abs(desired-q)) > 0.5:
                raise RuntimeError('Target deviates >0.5 rad from measured joint position')
            with lock:
                target[:] = [desired, time.monotonic()]
            active.set()
        time.sleep(c['control_dt'])
    finally:
        active.clear()
        time.sleep(0.2)
        writer.Wait()
    print('Single motion ended; damping sent for 0.2 s, no automatic replay')

if __name__ == '__main__':
    main()
