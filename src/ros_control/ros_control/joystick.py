import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import pygame

from ros_control_interfaces.msg import MotorCommand, Joystick

# Velocity settings for the drive motors (ID 3 and ID 4)
MAX_RPM = 500  # Dynamixel velocity format for 10 RPM
DEADBAND_MIN = -0.05
DEADBAND_MAX = 0.05

# Low-pass filter for smoothing joystick values
ALPHA = 0.2
previous_axis_3_value = 0.0  # Initialize smoothed value for Axis 3
previous_axis_1_value = 0.0  # Initialize smoothed value for Axis 1

# Direction toggle for motor ID 3
direction_inverted = False
previous_triangle_button_state = False  # Track previous state to prevent multiple detections
position_motor = 'left'

# Position mapping for the left motor (ID 1)
LEFT_POSITION_MIN = -300000  # Starting position for left motor (Joystick neutral for left movement)
LEFT_POSITION_MAX = 185000   # Max position for left motor (Joystick full left)

# Position mapping for the right motor (ID 2)
RIGHT_POSITION_MAX = 300000  # Starting position for right motor (Joystick neutral for right movement)
RIGHT_POSITION_MIN = -185000  # Max position for right motor (Joystick full right)

class JoystickPublisher(Node):
    def __init__(self):
        super().__init__('joystick_publisher')

        self.publisher_ = self.create_publisher(Joystick, 'joy', 1)

        pygame.init()
        pygame.joystick.init()

        self.joystick = None

        self.get_logger().info('Waiting for joystick connection...')

        while self.joystick is None:
            pygame.joystick.quit()
            pygame.joystick.init()

            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.get_logger().info(
                    f'Joystick "{self.joystick.get_name()}" connected and initialized'
                )
            else:
                self.get_logger().warn('No joystick detected. Retrying...')
                time.sleep(1)

        # self.timer_callback()

        # self.timer = self.create_timer(0.02, self.timer_callback)  # 20 Hz

    def publish_joystick_state(self):
        global previous_axis_3_value, previous_axis_1_value, direction_inverted, previous_triangle_button_state, position_motor
        pygame.event.pump()
        
        # Read joystick axes
        axis_3_value = -self.joystick.get_axis(2)  # Axis 3 for horizontal movement (position control)
        axis_1_value = self.joystick.get_axis(1)  # Axis 1 for vertical movement (velocity control)

        # Apply deadband and low-pass filter for Axis 3 (position control)
        if DEADBAND_MIN < axis_3_value < DEADBAND_MAX:
            axis_3_value = 0.0
        smoothed_axis_3_value = ALPHA * axis_3_value + (1 - ALPHA) * previous_axis_3_value
        previous_axis_3_value = smoothed_axis_3_value

        # Apply deadband and low-pass filter for Axis 1 (velocity control)
        if DEADBAND_MIN < axis_1_value < DEADBAND_MAX:
            axis_1_value = 0.0
        smoothed_axis_1_value = ALPHA * axis_1_value + (1 - ALPHA) * previous_axis_1_value
        previous_axis_1_value = smoothed_axis_1_value

        # Read Triangle button state (button index for Triangle is usually 3)
        triangle_button_state = self.joystick.get_button(3)

        # Toggle direction inversion on Triangle button press (only once per press)
        if triangle_button_state and not previous_triangle_button_state:
            direction_inverted = not direction_inverted
            print(f"Direction inversion toggled. Now {'inverted' if direction_inverted else 'normal'}.")

        # Update the previous button state
        previous_triangle_button_state = triangle_button_state

        drive_motor_velocity = self.map_joystick_to_velocity(smoothed_axis_1_value, MAX_RPM)

        if 0.0 >= smoothed_axis_3_value >= -1.0:
            position_motor = 'left'
            motor_position = self.map_joystick_to_position(smoothed_axis_3_value, LEFT_POSITION_MIN, LEFT_POSITION_MAX)

        if 0.0 <= smoothed_axis_3_value <= 1.0:
            position_motor = 'right'
            motor_position = int(RIGHT_POSITION_MAX - (smoothed_axis_3_value * (RIGHT_POSITION_MAX - RIGHT_POSITION_MIN)))

        msg = Joystick()

        pos = MotorCommand(name = position_motor, value = motor_position)

        vel3 = MotorCommand(name = 'drive_3', value = -drive_motor_velocity if direction_inverted else drive_motor_velocity)
        vel4 = MotorCommand(name = 'drive_4', value = -drive_motor_velocity)

        msg.positions = [pos]
        msg.velocities = [vel3, vel4]

        self.last_3 = axis_3_value
        self.last_1 = axis_1_value

        self.publisher_.publish(msg)

    def map_joystick_to_position(self, value, pos_min, pos_max):
        """Map joystick value to a position range."""
        return int((1 + value) * (pos_min - pos_max) + pos_max)
    
    def map_joystick_to_velocity(self, value, max_rpm):
        """Map joystick value to velocity range."""
        return int(value * max_rpm)
    
    def spin(self):
        # replace ROS timer with manual event loop
        while rclpy.ok():
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                    self.publish_joystick_state()

            # keep ROS callbacks alive (e.g., services, subscriptions)
            rclpy.spin_once(self, timeout_sec=0.01)

def main(args=None):
    rclpy.init(args=args)
    node = JoystickPublisher()
    try:
        node.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        pygame.quit()

if __name__ == '__main__':
    main()