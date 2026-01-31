#!/usr/bin/env python3
from time import time, sleep
from dynamixel_sdk import COMM_SUCCESS
from dynamixel_sdk import PacketHandler
from dynamixel_sdk import PortHandler
from dynamixel_sdk_custom_interfaces.msg import SetPosition
from dynamixel_sdk_custom_interfaces.srv import GetPosition

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

from ros_control_interfaces.msg import MotorCommand, Joystick

from itertools import chain

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
DRIVE_MOTOR_ID_3 = 3  # First Drive motor (Velocity Control)
DRIVE_MOTOR_ID_4 = 4  # Second Drive motor (Velocity Control)

# Default settings
BAUDRATE = 1000000 
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

VELOCITY_LIMIT_RPM = 5
VELOCITY_LIMIT_VALUE = int(VELOCITY_LIMIT_RPM / 0.01)  # Convert RPM to Dynamixel velocity format

class Control(Node):

    def __init__(self):
        super().__init__('control')

        #Initialize port and packet
        self.port_handler = PortHandler(DEVICE_NAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)

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

        qos = QoSProfile(depth=1)
        self.subscription = self.create_subscription(
            Joystick,
            'joy',
            self.joystick_callback,
            qos
        )

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
            self.get_logger().error(
                f'Motor {motor_id}: {self.packet_handler.getTxRxResult(dxl_comm_result)}'
            )
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
                    f'Motor {motor_id}: Velocity limit set to {VELOCITY_LIMIT_RPM} RPM'
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
                    f'Motor {motor_id}: Velocity limit set to {VELOCITY_LIMIT_RPM} RPM'
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

    def joystick_callback(self, msg):
        """Handle incoming joystick commands."""
        # Update positions
        for position_cmd in msg.positions:
            self._set_position(position_cmd.name, position_cmd.value)

        # Update velocities
        for velocity_cmd in msg.velocities:
            self._set_velocity(velocity_cmd.name, velocity_cmd.value)

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
    node = Control()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()