import time
import rclpy
from rclpy.node import Node
import pygame

from ros_control_interfaces.msg import MotorCommand, Joystick

# Velocity settings for the drive motors (ID 3 and ID 4)
MAX_RPM = 500  # Dynamixel velocity format for 5 RPM

# Low-pass filter for smoothing joystick values
ALPHA = 0.2
DEADBAND_THRESHOLD = 0.05

# Position mapping for the left motor (ID 1)
LEFT_POSITION_MIN = -300000  # Starting position for left motor (Joystick neutral for left movement)
LEFT_POSITION_MAX = 185000   # Max position for left motor (Joystick full left)

# Position mapping for the right motor (ID 2)
RIGHT_POSITION_MAX = 300000  # Starting position for right motor (Joystick neutral for right movement)
RIGHT_POSITION_MIN = -185000  # Max position for right motor (Joystick full right)

class JoystickPublisher(Node):
    def __init__(self):
        super().__init__('joystick_publisher')

        # Declare and get parameters for easier configuration
        self.declare_parameter('publish_rate', 50.0)  # Hz
        self.declare_parameter('alpha', ALPHA)
        self.declare_parameter('deadband', DEADBAND_THRESHOLD)
        self.declare_parameter('max_rpm', MAX_RPM)

        self.alpha = self.get_parameter('alpha').value
        self.deadband = self.get_parameter('deadband').value
        self.max_rpm = self.get_parameter('max_rpm').value
        publish_rate = self.get_parameter('publish_rate').value

        # Publisher
        self.publisher_ = self.create_publisher(Joystick, 'joy', 1)

        # Initialize state variables
        self.smoothed_axis_2 = 0.0
        self.smoothed_axis_1 = 0.0
        self.direction_inverted = False
        self.previous_triangle_state = False

        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self._connect_joystick()

        # Use timer for consistent publishing rate
        self.timer = self.create_timer(1.0 / publish_rate, self.timer_callback)
        
        self.get_logger().info(
            f'Joystick publisher initialized at {publish_rate} Hz'
        )


    def _connect_joystick(self):
        self.get_logger().info('Waiting for joystick connection...')

        while self.joystick is None and rclpy.ok():
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

    def _apply_deadband_and_filter(self, raw_value, previous_value):
        """Apply deadband and low-pass filter to joystick input."""
        # Apply deadband
        if abs(raw_value) < self.deadband:
            raw_value = 0.0
        
        # Apply low-pass filter
        return self.alpha * raw_value + (1 - self.alpha) * previous_value

    def _handle_direction_toggle(self, triangle_state):
        """Handle direction inversion toggle."""
        if triangle_state and not self.previous_triangle_state:
            self.direction_inverted = not self.direction_inverted
            status = 'inverted' if self.direction_inverted else 'normal'
            self.get_logger().info(f"Direction: {status}")
        
        self.previous_triangle_state = triangle_state

    def _map_to_position(self, value, motor_type):
        """Map joystick value [-1, 1] to motor position."""
        if motor_type == 'left':
            # Map [-1, 0] range
            return int((1 + value) * (LEFT_POSITION_MIN - LEFT_POSITION_MAX) + LEFT_POSITION_MAX)
        else:  # right
            # Map [0, 1] range
            return int(RIGHT_POSITION_MAX - value * (RIGHT_POSITION_MAX - RIGHT_POSITION_MIN))

    def _map_to_velocity(self, value):
        """Map joystick value [-1, 1] to motor velocity."""
        return int(value * self.max_rpm)

    def timer_callback(self):
        """Main callback for publishing joystick state."""
        if self.joystick is None:
            return

        # Process pygame events
        pygame.event.pump()
        
        # Read raw joystick values
        raw_axis_2 = -self.joystick.get_axis(2)  # Horizontal (position)
        raw_axis_1 = self.joystick.get_axis(1)   # Vertical (velocity)
        triangle_button = self.joystick.get_button(3)

        # Apply filtering
        self.smoothed_axis_2 = self._apply_deadband_and_filter(
            raw_axis_2, self.smoothed_axis_2
        )
        self.smoothed_axis_1 = self._apply_deadband_and_filter(
            raw_axis_1, self.smoothed_axis_1
        )

        # Handle direction toggle
        self._handle_direction_toggle(triangle_button)

        # Determine which position motor to control
        if self.smoothed_axis_2 <= 0.0:
            motor_name = 'left'
            position = self._map_to_position(self.smoothed_axis_2, 'left')
        else:
            motor_name = 'right'
            position = self._map_to_position(self.smoothed_axis_2, 'right')

        # Calculate drive velocity
        velocity = self._map_to_velocity(self.smoothed_axis_1)

        # Create and publish message
        msg = Joystick()
        
        msg.positions = [
            MotorCommand(name=motor_name, value=position)
        ]
        
        msg.velocities = [
            MotorCommand(
                name='drive_3',
                value=-velocity if self.direction_inverted else velocity
            ),
            MotorCommand(name='drive_4', value=-velocity)
        ]

        self.publisher_.publish(msg)

    def destroy_node(self):
        """Clean shutdown."""
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = JoystickPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()