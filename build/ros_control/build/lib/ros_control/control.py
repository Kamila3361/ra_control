#!/usr/bin/env python3
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

# Protocol version
PROTOCOL_VERSION = 2.0  # Default Protocol version of DYNAMIXEL X series.

# Default settings
# Motor IDs
LEFT_MOTOR_ID = 1   # Left motor (Position Control)
RIGHT_MOTOR_ID = 2  # Right motor (Position Control)
DRIVE_MOTOR_ID_3 = 3  # First Drive motor (Velocity Control)
DRIVE_MOTOR_ID_4 = 4  # Second Drive motor (Velocity Control)
BAUDRATE = 1000000  # Dynamixel default baudrate : 57600
DEVICE_NAME = '/dev/ttyUSB0'  # Check which port is being used on your controller

TORQUE_ENABLE = 1  # Value for enabling the torque
TORQUE_DISABLE = 0  # Value for disabling the torque
POSITION_CONTROL = 3  # Value for position control mode
VELOCITY_CONTROL = 1  # Value for velocity control mode

# Position mapping for the left motor (ID 1)
LEFT_POSITION_MIN = -300000  # Starting position for left motor (Joystick neutral for left movement)
LEFT_POSITION_MAX = 185000   # Max position for left motor (Joystick full left)

# Position mapping for the right motor (ID 2)
RIGHT_POSITION_MAX = 300000  # Starting position for right motor (Joystick neutral for right movement)
RIGHT_POSITION_MIN = -185000  # Max position for right motor (Joystick full right)

# Velocity settings for the drive motors (ID 3 and ID 4)
MAX_RPM = 2000  # Dynamixel velocity format for 10 RPM

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

        if not self.port_handler.openPort():
            self.get_logger().error('Failed to open the port!')
            return
        self.get_logger().info('Succeeded to open the port.')

        if not self.port_handler.setBaudRate(BAUDRATE):
            self.get_logger().error('Failed to set the baudrate!')
            return
        self.get_logger().info('Succeeded to set the baudrate.')

        self.setup_dynamixel()

        # Initialize position to neutral
        left_motor = MotorCommand()
        left_motor.name = 'left'
        left_motor.value = LEFT_POSITION_MIN
        right_motor = MotorCommand()
        right_motor.name = 'right'
        right_motor.value = RIGHT_POSITION_MAX
        self.set_position_callback([left_motor])
        self.set_position_callback([right_motor])

        qos = QoSProfile(depth=1)

        self.subscription = self.create_subscription(
            Joystick,
            'joy',
            self.move_callback,
            qos
        )

        # self.srv = self.create_service(GetPosition, 'get_position', self.get_position_callback)

    def setup_dynamixel(self):
        for dxl_id in self.position_motor_ids.values():
            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
                self.port_handler, dxl_id, ADDR_OPERATING_MODE, POSITION_CONTROL
            )
            if dxl_comm_result != COMM_SUCCESS:
                self.get_logger().error(f'Failed to set Position Control Mode: \
                                    {self.packet_handler.getTxRxResult(dxl_comm_result)}')
            else:
                self.get_logger().info('Succeeded to set Position Control Mode.')

        for dxl_id in self.velocity_motor_ids.values():
            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
                self.port_handler, dxl_id, ADDR_OPERATING_MODE, VELOCITY_CONTROL
            )
            if dxl_comm_result != COMM_SUCCESS:
                self.get_logger().error(f'Failed to set Velocity Control Mode: \
                                    {self.packet_handler.getTxRxResult(dxl_comm_result)}')
            else:
                self.get_logger().info('Succeeded to set Velocity Control Mode.')

        for dxl_id in chain(self.position_motor_ids.values(), self.velocity_motor_ids.values()):
            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
                self.port_handler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE
            )
            if dxl_comm_result != COMM_SUCCESS:
                self.get_logger().error(f'Failed to enable torque: \
                                    {self.packet_handler.getTxRxResult(dxl_comm_result)}')
            else:
                self.get_logger().info('Succeeded to enable torque.')

    def set_position_callback(self, positions):
        pos = {
            "name": positions[0].name,
            "value": positions[0].value
        }

        dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(
            self.port_handler, self.position_motor_ids[pos["name"]], ADDR_GOAL_POSITION, pos["value"]
        )
        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'Error: \
                                {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        elif dxl_error != 0:
            self.get_logger().error(f'Error: {self.packet_handler.getRxPacketError(dxl_error)}')
        else:
            self.get_logger().info(f'Set [ID: {self.position_motor_ids[pos["name"]]}] [Goal Position: {pos["value"]}]')

    def set_velocity_callback(self, velocities):
        
        vels = {
            "drive_3": velocities[0].value,
            "drive_4": velocities[1].value
        }

        for name in vels.keys():
            # print(f'Set [ID: {self.velocity_motor_ids[name]}] [Goal Velocity: {vels[name]}]')
            dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(
                self.port_handler, self.velocity_motor_ids[name], ADDR_GOAL_VELOCITY, vels[name]
            )
            if dxl_comm_result != COMM_SUCCESS:
                self.get_logger().error(f'Error: \
                                    {self.packet_handler.getTxRxResult(dxl_comm_result)}')
            elif dxl_error != 0:
                self.get_logger().error(f'Error: {self.packet_handler.getRxPacketError(dxl_error)}')
            else:
                self.get_logger().info(f'Set [ID: {self.velocity_motor_ids[name]}] [Goal Velocity: {vels[name]}]')

    def move_callback(self, msg):
        self.set_position_callback(msg.positions)
        self.set_velocity_callback(msg.velocities)

    # def get_position_callback(self, request, response):
    #     dxl_present_position, dxl_comm_result, dxl_error = self.packet_handler.read4ByteTxRx(
    #         self.port_handler, request.id, ADDR_PRESENT_POSITION
    #     )

    #     if dxl_comm_result != COMM_SUCCESS:
    #         self.get_logger().error(f'Error: {self.packet_handler.getTxRxResult(dxl_comm_result)}')
    #     elif dxl_error != 0:
    #         self.get_logger().error(f'Error: {self.packet_handler.getRxPacketError(dxl_error)}')
    #     else:
    #         self.get_logger().info(f'Get [ID: {request.id}] \
    #                                [Present Position: {dxl_present_position}]')

    #     response.position = dxl_present_position
    #     return response

    def __del__(self):
        self.packet_handler.write1ByteTxRx(self.port_handler,
                                           0,
                                           ADDR_TORQUE_ENABLE,
                                           TORQUE_DISABLE)
        self.port_handler.closePort()
        self.get_logger().info('Shutting down control')


def main(args=None):
    rclpy.init(args=args)
    node = Control()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()