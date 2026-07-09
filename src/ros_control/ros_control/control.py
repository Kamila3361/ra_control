#!/usr/bin/env python3
from time import time, sleep
from dynamixel_sdk import COMM_SUCCESS
from dynamixel_sdk import PacketHandler
from dynamixel_sdk import PortHandler
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32MultiArray

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from ros_control_interfaces.msg import Joystick, EncoderStamped

from itertools import chain
import threading
import math

# Control table address
ADDR_OPERATING_MODE = 11  # Control table address is different in Dynamixel model
ADDR_TORQUE_ENABLE = 512
ADDR_GOAL_POSITION = 564
ADDR_PRESENT_POSITION = 580
ADDR_GOAL_VELOCITY = 552
ADDR_PRESENT_VELOCITY = 576
ADDR_VELOCITY_LIMIT   = 44

# Protocol version
PROTOCOL_VERSION = 2.0  # Default Protocol version of DYNAMIXEL X series.

# Default settings
# Motor IDs
LEFT_MOTOR_ID = 1   # Left motor (Position Control)
RIGHT_MOTOR_ID = 2  # Right motor (Position Control)
DRIVE_MOTOR_ID_3 = 3  # First Drive motor (Velocity Control), right_wheel
DRIVE_MOTOR_ID_4 = 4  # Second Drive motor (Velocity Control), left_wheel

# Default settings
BAUDRATE = 115200 
DEVICE_NAME = '/dev/ttyUSB0'  # Check which port is being used on your controller

TORQUE_ENABLE = 1  # Value for enabling the torque
TORQUE_DISABLE = 0  # Value for disabling the torque
POSITION_CONTROL = 3  # Value for position control mode
VELOCITY_CONTROL = 1  # Value for velocity control mode

# Position mapping for the left motor (ID 1)
LEFT_POSITION_MIN = -300000
LEFT_POSITION_MAX = 185000

# Position mapping for the right motor (ID 2)
RIGHT_POSITION_MAX = 300000
RIGHT_POSITION_MIN = -185000

# Velocity settings for the drive motors (ID 3 and ID 4)
MAX_RPM = 2000  # Dynamixel velocity format for 10 RPM

# ── Velocity limits ────────────────────────────────────────────────────────
# 1.0 m/s  ÷  (2π × 0.1875 m)  ×  60  =  50.9 RPM
MAX_LINEAR_SPEED   = 0.2          # m/s  — robot-level limit
NOMINAL_WHEEL_RADIUS = 0.2575     # m
DYNAMIXEL_RPM_UNIT = 0.01         # RPM per unit
MAX_WHEEL_RPM      = (MAX_LINEAR_SPEED / NOMINAL_WHEEL_RADIUS) * (60 / (2 * math.pi))
MAX_VEL_UNIT       = int(MAX_WHEEL_RPM / DYNAMIXEL_RPM_UNIT)   

# Velocity limit written to hardware (same value — motor cannot exceed this)
VELOCITY_LIMIT_VALUE = MAX_VEL_UNIT

# MAX_WHEEL_RPM = 5
# VELOCITY_LIMIT_VALUE = int(MAX_WHEEL_RPM / 0.01)  # Convert RPM to Dynamixel velocity format

class DiffDriveControl(Node):

    def __init__(self):
        super().__init__('diff_drive_control')

        # ── Parameters ────────────────────────────────────────────────────
        self.declare_parameter('wheelbase', 0.45)          # m, distance between wheels
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

        # Desired velocities (Dynamixel units); updated by cmd_vel callback
        self._cmd_left_vel  = 0
        self._cmd_right_vel = 0

        #Initialize port and packet
        self.port_handler = PortHandler(DEVICE_NAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)

        # Thread lock
        self.lock = threading.Lock()

        #set motor ids
        self.position_motor_ids = {
            'left': LEFT_MOTOR_ID,
            'right': RIGHT_MOTOR_ID
        }
        self.velocity_motor_ids = {
            'drive_3': DRIVE_MOTOR_ID_3,
            'drive_4': DRIVE_MOTOR_ID_4
        }

        self.all_motor_ids = list(self.position_motor_ids.values()) + \
                             list(self.velocity_motor_ids.values())
        
        self._establish_connection()
        self._setup_motors()
        self._initialize_positions()

        # ── Subscriptions & publishers ────────────────────────────────────
        cmd_vel_qos = QoSProfile(depth=1)
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            'cmd_vel',
            self._cmd_vel_callback,
            cmd_vel_qos
        )

        qos = QoSProfile(depth=1)
        self.subscription = self.create_subscription(
            Int32MultiArray,
            'position',
            self.pos_callback,
            qos
        )

        # QoS profile for encoder data (sensor data)
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Create publisher
        self.encoder_pub = self.create_publisher(
            EncoderStamped,
            'encoder',
            qos_profile
        )

        #create publisher for wheel radii (for dynamic TF)
        self.wheel_radii_pub = self.create_publisher(
            Float32MultiArray,
            'wheel_radii',
            qos_profile
        )
        
        # Create timer for publishing
        self.timer = self.create_timer(1.0 / publish_rate, self.timer_callback)

        self.get_logger().info('Control node initialized successfully')
        self.get_logger().info('Publishing to: encoder topic at 50 Hz')
        self.get_logger().info('='*60)

    def _establish_connection(self):
        self.get_logger().info('Searching for Dynamixel motors...')

        while rclpy.ok():
            try:
                # Open port
                if not self.port_handler.openPort():
                    self.get_logger().warn('Failed to open port. Retrying...')
                    sleep(1)
                    continue

                # Set baudrate
                if not self.port_handler.setBaudRate(BAUDRATE):
                    self.get_logger().warn('Failed to set baudrate. Retrying...')
                    self.port_handler.closePort()
                    sleep(1)
                    continue

                # Ping first motor to verify connection
                test_id = self.all_motor_ids[0]
                dxl_model, dxl_comm_result, dxl_error = \
                    self.packet_handler.ping(self.port_handler, test_id)

                if dxl_comm_result != COMM_SUCCESS:
                    self.get_logger().warn(
                        'No response from Dynamixel. Retrying...'
                    )
                    self.port_handler.closePort()
                    sleep(1)
                    continue

                self.get_logger().info(
                    f'Connected! Model number: {dxl_model}'
                )
                break

            except FileNotFoundError:
                self.get_logger().warn('Device not found. Waiting for USB...')
                sleep(1)
                continue

        self.get_logger().info('Dynamixel connection established.')

    def _reset_port(self):
        """Reset port when SDK gets stuck in 'Port is in use' state."""
        self.get_logger().warn('Resetting port due to communication failure...')
        try:
            self.port_handler.closePort()
            sleep(0.5)
            self.port_handler.openPort()
            self.port_handler.setBaudRate(BAUDRATE)
            self.get_logger().info('Port reset successful.')
        except Exception as e:
            self.get_logger().error(f'Port reset failed: {e}')

    def _write_with_error_check(self, motor_id, address, value, byte_size=1):
        """Write to motor with error checking."""
        write_func = {
            1: self.packet_handler.write1ByteTxRx,
            4: self.packet_handler.write4ByteTxRx
        }[byte_size]

        dxl_comm_result, dxl_error = write_func(
            self.port_handler, motor_id, address, value
        )

        if dxl_comm_result != COMM_SUCCESS:
            error_msg = self.packet_handler.getTxRxResult(dxl_comm_result)
            self.get_logger().error(
                f'Motor {motor_id}: {error_msg}'
            )

            if 'in use' in error_msg.lower() or 'no status' in error_msg.lower():
                self._reset_port()
            return False
        elif dxl_error != 0:
            self.get_logger().error(
                f'Motor {motor_id}: {self.packet_handler.getRxPacketError(dxl_error)}'
            )
            return False
        
        return True

    def _setup_motors(self):
        """Configure all motors with appropriate control modes."""
        self.get_logger().info('Configuring motors...')

        # Disable torque for all motors
        for motor_id in self.all_motor_ids:
            if self._write_with_error_check(
                motor_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE
            ):
                self.get_logger().debug(f'Motor {motor_id}: Torque disabled')

        # Set position control mode for position motors
        for name, motor_id in self.position_motor_ids.items():
            if self._write_with_error_check(
                motor_id, ADDR_OPERATING_MODE, POSITION_CONTROL
            ):
                self.get_logger().info(
                    f'Motor {motor_id} ({name}): Position control enabled'
                )
            
            # Set velocity limit
            if self._write_with_error_check(
                motor_id, ADDR_VELOCITY_LIMIT, VELOCITY_LIMIT_VALUE, byte_size=4
            ):
                self.get_logger().debug(
                    f'Motor {motor_id}: Velocity limit set to {MAX_WHEEL_RPM} RPM'
                )

        # Set velocity control mode for drive motors
        for name, motor_id in self.velocity_motor_ids.items():
            if self._write_with_error_check(
                motor_id, ADDR_OPERATING_MODE, VELOCITY_CONTROL
            ):
                self.get_logger().info(
                    f'Motor {motor_id} ({name}): Velocity control enabled'
                )
            
            # Set velocity limit
            if self._write_with_error_check(
                motor_id, ADDR_VELOCITY_LIMIT, VELOCITY_LIMIT_VALUE, byte_size=4
            ):
                self.get_logger().debug(
                    f'Motor {motor_id}: Velocity limit set to {MAX_WHEEL_RPM} RPM'
                )

        # Enable torque for all motors
        for motor_id in self.all_motor_ids:
            if self._write_with_error_check(
                motor_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE
            ):
                self.get_logger().debug(f'Motor {motor_id}: Torque enabled')

        self.get_logger().info('Motor configuration complete')

    def _initialize_positions(self):
        self.get_logger().info('Moving to neutral positions...')
        
        # Left motor to minimum position
        self._set_position('left', LEFT_POSITION_MIN)

        # Right motor to maximum position
        self._set_position('right', RIGHT_POSITION_MAX)

    def _set_position(self, motor_name, position):
        """Set goal position for a position-controlled motor."""
        motor_id = self.position_motor_ids.get(motor_name)
        if motor_id is None:
            self.get_logger().error(f'Unknown motor: {motor_name}')
            return

        if self._write_with_error_check(
            motor_id, ADDR_GOAL_POSITION, position, byte_size=4
        ):
            self.get_logger().debug(
                f'Motor {motor_id} ({motor_name}): Position set to {position}'
            )

    def _set_velocity(self, motor_name, velocity):
        """Set goal velocity for a velocity-controlled motor."""
        motor_id = self.velocity_motor_ids.get(motor_name)
        if motor_id is None:
            self.get_logger().error(f'Unknown motor: {motor_name}')
            return

        if self._write_with_error_check(
            motor_id, ADDR_GOAL_VELOCITY, velocity, byte_size=4
        ):
            self.get_logger().debug(
                f'Motor {motor_id} ({motor_name}): Velocity set to {velocity}'
            )

    def pos_callback(self, msg):
        """Handle incoming joystick commands."""
        with self.lock:
            # Update positions
            self._write_with_error_check(1, ADDR_GOAL_POSITION, msg.data[0], byte_size=4)
            self._write_with_error_check(2, ADDR_GOAL_POSITION, msg.data[1], byte_size=4)

    
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
        v_left  = v + w * (self.wheelbase / 2.0)
        v_right = v - w * (self.wheelbase / 2.0)

        # Convert m/s → RPM → Dynamixel units
        def to_dxl(wheel_speed_ms):
            rpm  = (wheel_speed_ms / self.wheel_radius) * (60.0 / (2.0 * math.pi))
            unit = int(rpm / DYNAMIXEL_RPM_UNIT)
            return max(-self._max_vel_unit, min(self._max_vel_unit, unit))

        left_unit  = to_dxl(v_left)
        right_unit = -to_dxl(v_right)   # negate: motor 4 mounted mirrored

        with self.lock:
            self._cmd_left_vel  = left_unit
            self._cmd_right_vel = right_unit

        # Send immediately (low latency)
        self._write_with_error_check(4,  ADDR_GOAL_VELOCITY, left_unit,  byte_size=4)
        self._write_with_error_check(3, ADDR_GOAL_VELOCITY, right_unit, byte_size=4)

        self.get_logger().debug(
            f'cmd_vel → v={v:.3f} m/s  ω={w:.3f} rad/s | '
            f'L={left_unit}  R={right_unit} units'
        )

    def read_encoder(self, motor_id, address=ADDR_PRESENT_POSITION):
        """Read encoder position from a motor"""
        dxl_present_position, dxl_comm_result, dxl_error = \
            self.packet_handler.read4ByteTxRx(
                self.port_handler, 
                motor_id, 
                address
            )
        
        if dxl_comm_result != COMM_SUCCESS:
            error_msg = self.packet_handler.getTxRxResult(dxl_comm_result)
            self.get_logger().error(
                f'Failed to read motor {motor_id}: '
                f'{error_msg}'
            )
            #Auto-recover here too
            if 'in use' in error_msg.lower() or 'no status' in error_msg.lower():
                self._reset_port()
            return None
        
        # Convert from unsigned to signed (32-bit)
        if dxl_present_position > 2147483647:
            dxl_present_position -= 4294967296
        
        return dxl_present_position
    
    def _position_to_radius(self, motor_name: str, position: int) -> float:
        """Map encoder position to wheel radius via linear interpolation."""
        if motor_name == 'left':
            pos_min, pos_max = LEFT_POSITION_MIN, LEFT_POSITION_MAX   # -300000, 185000
            rad_at_min, rad_at_max = 0.2575, 0.1375                   # inverted: min pos → max radius
        elif motor_name == 'right':
            pos_min, pos_max = RIGHT_POSITION_MIN, RIGHT_POSITION_MAX  # -185000, 300000
            rad_at_min, rad_at_max = 0.1375, 0.2575
        else:
            self.get_logger().error(f'Unknown motor name: {motor_name}')
            return 0.0

        t = (position - pos_min) / (pos_max - pos_min)
        t = max(0.0, min(1.0, t))   # clamp to [0, 1] — safety against out-of-range positions
        return abs(rad_at_min + t * (rad_at_max - rad_at_min))
    
    def timer_callback(self):
        """Timer callback to read and publish encoder data"""
        try:
            with self.lock:
                # Read encoder positions
                left_encoder = self.read_encoder(self.velocity_motor_ids['drive_3'])
                right_encoder = self.read_encoder(self.velocity_motor_ids['drive_4'])
                left_velocity = self.read_encoder(self.velocity_motor_ids['drive_3'], address=ADDR_PRESENT_VELOCITY)
                right_velocity = self.read_encoder(self.velocity_motor_ids['drive_4'], address=ADDR_PRESENT_VELOCITY)

                # Position motor encoders (new)
                left_pos  = self.read_encoder(self.position_motor_ids['left'])
                right_pos = self.read_encoder(self.position_motor_ids['right'])
            
            # ✅ Skip publish if any read failed
            if any(v is None for v in [left_encoder, right_encoder, left_velocity, right_velocity, left_pos, right_pos]):
                self.get_logger().warn('Skipping publish — encoder read failed')
                return

            # Create and publish message
            msg = EncoderStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'base_footprint'
            msg.left_encoder = left_encoder
            msg.right_encoder = right_encoder
            msg.left_velocity = left_velocity
            msg.right_velocity = right_velocity

            self.encoder_pub.publish(msg)

            if left_pos is not None and right_pos is not None:
                radii_msg = Float32MultiArray()
                radii_msg.data = [
                    self._position_to_radius('left',  left_pos),
                    self._position_to_radius('right', right_pos),
                ]
                self.wheel_radii_pub.publish(radii_msg)
            else:
                self.get_logger().warn('Skipping wheel_radii publish — position read failed')
            
        except Exception as e:
            self.get_logger().error(f'Error in timer callback: {e}')

    def destroy_node(self):
        """Clean shutdown - disable torque and close port."""
        self.get_logger().info('Shutting down...')
        
        # Disable torque for all motors
        for motor_id in self.all_motor_ids:
            self._write_with_error_check(
                motor_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE
            )
        
        # Close port
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
