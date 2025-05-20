from Episode_API import EpisodeAPP
import time
# 全局唯一实例（也可以使用 Singleton）
robot = EpisodeAPP(ip="localhost", port=12345)

def gripper_servo_open():
    """
    控制夹爪开关，夹爪的运动范围是0-110°
    """
    rest = robot.servo_gripper(20)
    if rest is not None:
        time.sleep(rest)
        return True
    else:
        return False

def gripper_servo_close():
    """
    控制夹爪开关，夹爪的运动范围是0-110°，建议闭合选择95°
    """
    rest = robot.servo_gripper(95)
    if rest is not None:
        time.sleep(rest)
        return True
    else:
        return False

def move_to_xyz(position):
    """
    控制机械臂移动到指定位置，并在内部处理 IK 检查与延时等待。

    参数：
        position (list): [x, y, z] 坐标

    返回：
        True 表示成功移动，False 表示 IK 无解
    """
    # 固定姿态 [180, 0, 0]，使用 xyz 顺序
    orientation = [180, 0, 0]
    result = robot.move_xyz_rotation(position, orientation, "xyz")

    print(f"控制机械臂移动到 {position}，耗时: {result}s")

    if result == -1:
        print("IK 无解，退出执行")
        return False

    # 等待运动完成
    time.sleep(result)
    return True

def emergency_stop(enable: int):
    return robot.emergency_stop(enable)

def get_pose(order="xyz"):
    result = robot.get_pose(rotation_order=order)
    return result.tolist() if result is not None else None

def move_relative(offset):
    """
    控制机械臂根据当前位置向指定方向移动指定距离，并在内部处理 IK 检查与延时等待。

    参数：
        offset (list): [x, y, z] 三个方向上想要移动的距离

    返回：
        True 表示成功移动，False 表示 IK 无解
    """
    current = robot.get_pose()
    new_position = [
        current[0] + offset[0],
        current[1] + offset[1],
        current[2] + offset[2],
    ]
    return move_to_xyz(new_position)

def get_robot_status():
    pose = robot.get_pose()
    angles = robot.get_motor_angles()

    if pose is None or angles is None:
        return "无法获取当前机械臂状态。"

    x, y, z = pose[0:3]
    roll, pitch, yaw = pose[3:6]
    joints = angles

    response = (
        f"机械臂末端执行器的位置为：\n"
        f"x = {x:.1f} mm, y = {y:.1f} mm, z = {z:.1f} mm\n"
        f"姿态为：\n"
        f"roll = {roll:.1f}°, pitch = {pitch:.1f}°, yaw = {yaw:.1f}°\n\n"
        f"各关节角度为：\n"
        f"关节1 = {joints[0]:.1f}°，关节2 = {joints[1]:.1f}°，关节3 = {joints[2]:.1f}°，\n"
        f"关节4 = {joints[3]:.1f}°，关节5 = {joints[4]:.1f}°，关节6 = {joints[5]:.1f}°"
    )
    return response