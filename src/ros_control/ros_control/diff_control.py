#!/usr/bin/env python3
"""
Differential drive control node.

Subscribes to /cmd_vel (geometry_msgs/Twist) and drives motors 3 & 4
via velocity control. Position motors (1 & 2) are untouched here —
they remain under joystick control via the /joy topic in control.py.

Velocity conversion
-------------------
Robot max linear speed  : 1.0 m/s
Nominal wheel radius    : 0.1875 m  (mid-range of 0.1375–0.2575 m)
Max wheel speed         : 1.0 / 0.1875 = 5.33 rad/s  →  50.9 RPM
Dynamixel velocity unit : 0.229 RPM/unit
MAX_VEL_UNIT            : round(50.9 / 0.229) = 222 units  (hardware limit)

Differential kinematics
-----------------------
  v_l = (v - ω × L/2) / r
  v_r = (v + ω × L/2) / r
where L = wheelbase, r = nominal wheel radius.

Drive motor wiring (from control.py)
-------------------------------------
  drive_3  →  left  wheel
  drive_4  →  right wheel  (negated in original joystick code, kept here)
"""

from time import sleep
from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from ros_control_interfaces.msg import EncoderStamped

import threading
import math

# ── Dynamixel control table ────────────────────────────────────────────────
ADDR_OPERATING_MODE  = 11
ADDR_TORQUE_ENABLE   = 512
ADDR_GOAL_VELOCITY   = 552
ADDR_PRESENT_POSITION = 580
ADDR_PRESENT_VELOCITY = 576
ADDR_VELOCITY_LIMIT  = 44

PROTOCOL_VERSION = 2.0

# ── Motor IDs ──────────────────────────────────────────────────────────────
LEFT_MOTOR_ID  = 1   # position motor — not touched here
RIGHT_MOTOR_ID = 2   # position motor — not touched here
DRIVE_LEFT_ID  = 3   # drive_3  →  left wheel
DRIVE_RIGHT_ID = 4   # drive_4  →  right wheel

# ── Port ───────────────────────────────────────────────────────────────────
BAUDRATE    = 115200
DEVICE_NAME = '/dev/ttyUSB0'

TORQUE_ENABLE   = 1
TORQUE_DISABLE  = 0
VELOCITY_CONTROL = 1

# ── Position motor constants (for wheel-radius mapping only) ───────────────
LEFT_POSITION_MIN  = -300000
LEFT_POSITION_MAX  =  185000
RIGHT_POSITION_MIN = -185000
RIGHT_POSITION_MAX =  300000

# ── Velocity limits ────────────────────────────────────────────────────────
# 1.0 m/s  ÷  (2π × 0.1875 m)  ×  60  =  50.9 RPM
# Dynamixel unit = 0.229 RPM  →  50.9 / 0.229 ≈ 222 units
MAX_LINEAR_SPEED   = 1.0          # m/s  — robot-level limit
NOMINAL_WHEEL_RADIUS = 0.1875     # m
DYNAMIXEL_RPM_UNIT = 0.229        # RPM per unit
MAX_WHEEL_RPM      = (MAX_LINEAR_SPEED / NOMINAL_WHEEL_RADIUS) * (60 / (2 * math.pi))
MAX_VEL_UNIT       = int(MAX_WHEEL_RPM / DYNAMIXEL_RPM_UNIT)   # ≈ 222

# Velocity limit written to hardware (same value — motor cannot exceed this)
VELOCITY_LIMIT_VALUE = MAX_VEL_UNIT   # ≈ 222 units


class DiffDriveControl(Node):
    """
    Subscribes to /cmd_vel and converts Twist → Dynamixel velocity commands
    for the two drive motors (IDs 3 & 4). Also publishes encoder and
    wheel_radii topics so the rest of the stack keeps working.
    """

    def __init__(self):
        super().__init__('diff_drive_control')

        # ── Parameters ────────────────────────────────────────────────────
        self.declare_parameter('wheelbase', 0.3)          # m, distance between wheels
        self.declare_parameter('wheel_radius', NOMINAL_WHEEL_RADIUS)
        self.declare_parameter('max_linear_speed', MAX_LINEAR_SPEED)
        self.declare_parameter('publish_rate', 50.0)      # Hz

        self.wheelbase    = self.get_parameter('wheelbase').value
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.max_linear   = self.get_parameter('max_linear_speed').value
        publish_rate      = self.get_parameter('publish_rate').value

        # Recompute max RPM in case wheel_radius param was changed
        self._max_vel_unit = int(
            (self.max_linear / self.wheel_radius) * (60 / (2 * math.pi))
            / DYNAMIXEL_RPM_UNIT
        )

        self.lock = threading.Lock()

        # Desired velocities (Dynamixel units); updated by cmd_vel callback
        self._cmd_left_vel  = 0
        self._cmd_right_vel = 0

        # ── Hardware setup ─────────────────────────────────────────────────
        self.port_handler   = PortHandler(DEVICE_NAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)

        self._establish_connection()
        self._setup_drive_motors()

        # ── Subscriptions & publishers ────────────────────────────────────
        cmd_vel_qos = QoSProfile(depth=1)
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self._cmd_vel_callback,
            cmd_vel_qos
        )

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.encoder_pub     = self.create_publisher(EncoderStamped, 'encoder', sensor_qos)
        self.wheel_radii_pub = self.create_publisher(Float32MultiArray, 'wheel_radii', sensor_qos)

        self.timer = self.create_timer(1.0 / publish_rate, self._timer_callback)

        self.get_logger().info(
            f'DiffDriveControl ready | wheelbase={self.wheelbase} m | '
            f'wheel_radius={self.wheel_radius} m | '
            f'max_vel_unit={self._max_vel_unit} ({MAX_WHEEL_RPM:.1f} RPM)'
        )

    # ── Connection ─────────────────────────────────────────────────────────

    def _establish_connection(self):
        self.get_logger().info('Connecting to Dynamixel bus...')
        while rclpy.ok():
            try:
                if not self.port_handler.openPort():
                    self.get_logger().warn('Cannot open port. Retrying...')
                    sleep(1); continue

                if not self.port_handler.setBaudRate(BAUDRATE):
                    self.get_logger().warn('Cannot set baudrate. Retrying...')
                    self.port_handler.closePort(); sleep(1); continue

                _, result, _ = self.packet_handler.ping(self.port_handler, DRIVE_LEFT_ID)
                if result != COMM_SUCCESS:
                    self.get_logger().warn('No response from drive motor. Retrying...')
                    self.port_handler.closePort(); sleep(1); continue

                self.get_logger().info('Dynamixel connection established.')
                break

            except FileNotFoundError:
                self.get_logger().warn('Device not found. Waiting for USB...')
                sleep(1)

    def _reset_port(self):
        self.get_logger().warn('Resetting port...')
        try:
            self.port_handler.closePort()
            sleep(0.5)
            self.port_handler.openPort()
            self.port_handler.setBaudRate(BAUDRATE)
        except Exception as e:
            self.get_logger().error(f'Port reset failed: {e}')

    # ── Low-level write ────────────────────────────────────────────────────

    def _write(self, motor_id, address, value, byte_size=1):
        write_fn = {
            1: self.packet_handler.write1ByteTxRx,
            4: self.packet_handler.write4ByteTxRx,
        }[byte_size]

        result, error = write_fn(self.port_handler, motor_id, address, value)

        if result != COMM_SUCCESS:
            msg = self.packet_handler.getTxRxResult(result)
            self.get_logger().error(f'Motor {motor_id} write error: {msg}')
            if 'in use' in msg.lower() or 'no status' in msg.lower():
                self._reset_port()
            return False
        if error != 0:
            self.get_logger().error(
                f'Motor {motor_id}: {self.packet_handler.getRxPacketError(error)}'
            )
            return False
        return True

    def _read4(self, motor_id, address):
        value, result, error = self.packet_handler.read4ByteTxRx(
            self.port_handler, motor_id, address
        )
        if result != COMM_SUCCESS:
            msg = self.packet_handler.getTxRxResult(result)
            self.get_logger().error(f'Motor {motor_id} read error: {msg}')
            if 'in use' in msg.lower() or 'no status' in msg.lower():
                self._reset_port()
            return None
        # Convert unsigned → signed 32-bit
        if value > 2147483647:
            value -= 4294967296
        return value

    # ── Motor setup ────────────────────────────────────────────────────────

    def _setup_drive_motors(self):
        self.get_logger().info('Configuring drive motors...')
        for motor_id in (DRIVE_LEFT_ID, DRIVE_RIGHT_ID):
            self._write(motor_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)

        for motor_id in (DRIVE_LEFT_ID, DRIVE_RIGHT_ID):
            self._write(motor_id, ADDR_OPERATING_MODE, VELOCITY_CONTROL)
            self._write(motor_id, ADDR_VELOCITY_LIMIT, VELOCITY_LIMIT_VALUE, byte_size=4)

        for motor_id in (DRIVE_LEFT_ID, DRIVE_RIGHT_ID):
            self._write(motor_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

        self.get_logger().info(
            f'Drive motors ready. Velocity limit = {VELOCITY_LIMIT_VALUE} units '
            f'({VELOCITY_LIMIT_VALUE * DYNAMIXEL_RPM_UNIT:.1f} RPM)'
        )

    # ── cmd_vel callback ───────────────────────────────────────────────────

    def _cmd_vel_callback(self, msg: Twist):
        """
        Convert Twist → per-wheel Dynamixel velocity units.

        Differential kinematics:
            v_l = (v - ω·L/2) / r
            v_r = (v + ω·L/2) / r

        Then scale to Dynamixel units and clamp to ±MAX_VEL_UNIT.
        drive_4 (right) is negated to match physical mounting orientation
        (matches the original joystick code convention).
        """
        v = msg.linear.x
        w = msg.angular.z

        # Clamp incoming commands to robot limits
        v = max(-self.max_linear, min(self.max_linear, v))

        # Wheel linear speeds (m/s)
        v_left  = v - w * (self.wheelbase / 2.0)
        v_right = v + w * (self.wheelbase / 2.0)

        # Convert m/s → RPM → Dynamixel units
        def to_dxl(wheel_speed_ms):
            rpm  = (wheel_speed_ms / self.wheel_radius) * (60.0 / (2.0 * math.pi))
            unit = int(rpm / DYNAMIXEL_RPM_UNIT)
            return max(-self._max_vel_unit, min(self._max_vel_unit, unit))

        left_unit  =  to_dxl(v_left)
        right_unit = -to_dxl(v_right)   # negate: motor 4 mounted mirrored

        with self.lock:
            self._cmd_left_vel  = left_unit
            self._cmd_right_vel = right_unit

        # Send immediately (low latency)
        self._write(DRIVE_LEFT_ID,  ADDR_GOAL_VELOCITY, left_unit,  byte_size=4)
        self._write(DRIVE_RIGHT_ID, ADDR_GOAL_VELOCITY, right_unit, byte_size=4)

        self.get_logger().debug(
            f'cmd_vel → v={v:.3f} m/s  ω={w:.3f} rad/s | '
            f'L={left_unit}  R={right_unit} units'
        )

    # ── Wheel-radius helper (reused from control.py) ───────────────────────

    def _position_to_radius(self, motor_name: str, position: int) -> float:
        if motor_name == 'left':
            pos_min, pos_max = LEFT_POSITION_MIN, LEFT_POSITION_MAX
            r_at_min, r_at_max = 0.2575, 0.1375
        else:
            pos_min, pos_max = RIGHT_POSITION_MIN, RIGHT_POSITION_MAX
            r_at_min, r_at_max = 0.1375, 0.2575

        t = (position - pos_min) / (pos_max - pos_min)
        t = max(0.0, min(1.0, t))
        return abs(r_at_min + t * (r_at_max - r_at_min))

    # ── Timer: read encoders & publish ────────────────────────────────────

    def _timer_callback(self):
        try:
            with self.lock:
                left_enc  = self._read4(DRIVE_LEFT_ID,  ADDR_PRESENT_POSITION)
                right_enc = self._read4(DRIVE_RIGHT_ID, ADDR_PRESENT_POSITION)
                left_vel  = self._read4(DRIVE_LEFT_ID,  ADDR_PRESENT_VELOCITY)
                right_vel = self._read4(DRIVE_RIGHT_ID, ADDR_PRESENT_VELOCITY)
                left_pos  = self._read4(LEFT_MOTOR_ID,  ADDR_PRESENT_POSITION)
                right_pos = self._read4(RIGHT_MOTOR_ID, ADDR_PRESENT_POSITION)

            if any(v is None for v in [left_enc, right_enc, left_vel, right_vel]):
                self.get_logger().warn('Skipping encoder publish — read failed')
                return

            enc_msg = EncoderStamped()
            enc_msg.header.stamp    = self.get_clock().now().to_msg()
            enc_msg.header.frame_id = 'base_footprint'
            enc_msg.left_encoder  = left_enc
            enc_msg.right_encoder = right_enc
            enc_msg.left_velocity  = left_vel
            enc_msg.right_velocity = right_vel
            self.encoder_pub.publish(enc_msg)

            if left_pos is not None and right_pos is not None:
                radii_msg = Float32MultiArray()
                radii_msg.data = [
                    self._position_to_radius('left',  left_pos),
                    self._position_to_radius('right', right_pos),
                ]
                self.wheel_radii_pub.publish(radii_msg)

        except Exception as e:
            self.get_logger().error(f'Timer callback error: {e}')

    # ── Shutdown ───────────────────────────────────────────────────────────

    def destroy_node(self):
        self.get_logger().info('Shutting down — stopping drive motors...')
        self._write(DRIVE_LEFT_ID,  ADDR_GOAL_VELOCITY, 0, byte_size=4)
        self._write(DRIVE_RIGHT_ID, ADDR_GOAL_VELOCITY, 0, byte_size=4)
        for motor_id in (DRIVE_LEFT_ID, DRIVE_RIGHT_ID):
            self._write(motor_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        self.port_handler.closePort()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()