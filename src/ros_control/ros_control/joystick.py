import time
import rclpy
from rclpy.node import Node
import pygame

from geometry_msgs.msg import Twist
from std_msgs.msg import Int32MultiArray
from ros_control_interfaces.msg import MotorCommand, Joystick

#robot limits
MAX_LINEAR_SPEED    = 0.4    # m/s   (matches diff_drive_control.py)
MAX_ANGULAR_SPEED   = 1.0    # rad/s (tune to taste; ~170 °/s)

# Low-pass filter for smoothing joystick values
ALPHA = 0.2
DEADBAND_THRESHOLD = 0.05

# Position mapping for the left motor (ID 1)
LEFT_POSITION_MIN = -300000  # Starting position for left motor (Joystick neutral for left movement)
LEFT_POSITION_MAX = 185000   # Max position for left motor (Joystick full left)

# Position mapping for the right motor (ID 2)
RIGHT_POSITION_MAX = 300000  # Starting position for right motor (Joystick neutral for right movement)
RIGHT_POSITION_MIN = -185000  # Max position for right motor (Joystick full right)

# ── Incremental position control ───────────────────────────────────────────
POSITION_INCREMENT_RATE = 15000.0   # units/sec at full axis deflection

class JoystickPublisher(Node):
    def __init__(self):
        super().__init__('joystick_publisher')

        # Declare and get parameters for easier configuration
        self.declare_parameter('publish_rate', 50.0)  # Hz
        self.declare_parameter('alpha', ALPHA)
        self.declare_parameter('deadband', DEADBAND_THRESHOLD)
        self.declare_parameter('max_linear',      MAX_LINEAR_SPEED)
        self.declare_parameter('max_angular',     MAX_ANGULAR_SPEED)
        self.declare_parameter('position_increment_rate', POSITION_INCREMENT_RATE)

        self.alpha = self.get_parameter('alpha').value
        self.deadband = self.get_parameter('deadband').value
        self.max_linear   = self.get_parameter('max_linear').value
        self.max_angular  = self.get_parameter('max_angular').value
        publish_rate = self.get_parameter('publish_rate').value
        self.increment_rate = self.get_parameter('position_increment_rate').value
        self.dt = 1.0 / publish_rate

        # Publisher
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel_joy', 1)
        self.pos_pub = self.create_publisher(Int32MultiArray, 'position', 1)

        # Initialize state variables
        self.smoothed_linear  = 0.0   # axis 1 (forward/back)
        self.smoothed_angular = 0.0   # axis 2 (left/right turn)
        self.smoothed_left_position = 0.0
        self.smoothed_right_position = 0.0

        self.left_position  = float(LEFT_POSITION_MIN)
        self.right_position = float(RIGHT_POSITION_MAX)

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

    def _filter(self, raw_value, previous_value):
        """Apply deadband and low-pass filter to joystick input."""
        # Apply deadband
        if abs(raw_value) < self.deadband:
            raw_value = 0.0
        
        # Apply low-pass filter
        return self.alpha * raw_value + (1 - self.alpha) * previous_value

    def timer_callback(self):
        """Main callback for publishing joystick state."""
        if self.joystick is None:
            return

        # Process pygame events
        pygame.event.pump()
        
        # Read raw joystick values
        raw_angular = -self.joystick.get_axis(0) # Horizontal (angular velocity)
        raw_linear = -self.joystick.get_axis(1)   # Vertical (linear velocity) forward/back
        raw_left_position = self.joystick.get_axis(2)  # Horizontal (position)
        raw_right_position = self.joystick.get_axis(5)  # Horizontal (position)

        # Apply filtering
        self.smoothed_linear  = self._filter(raw_linear,  self.smoothed_linear)
        self.smoothed_angular = self._filter(raw_angular, self.smoothed_angular)
        self.smoothed_left_position = self._filter(raw_left_position, self.smoothed_left_position)
        self.smoothed_right_position = self._filter(raw_right_position, self.smoothed_right_position)

        # ── Publish Twist ─────────────────────────────────────────────────
        twist = Twist()
        twist.linear.x  = self.smoothed_linear  * self.max_linear
        twist.angular.z = self.smoothed_angular * self.max_angular
        self.cmd_vel_pub.publish(twist)
        
        # ── Integrate position commands ──────────────────────────────────
        # Positive axis → position increases; negative → decreases.
        # Zero (within deadband, after filtering) → position holds.
        self.left_position += (
            self.smoothed_left_position * self.increment_rate * self.dt
        )
        self.right_position += (
            self.smoothed_right_position * self.increment_rate * self.dt
        )

        # Clamp to each motor's valid range
        left_lo, left_hi = sorted((LEFT_POSITION_MIN, LEFT_POSITION_MAX))
        right_lo, right_hi = sorted((RIGHT_POSITION_MIN, RIGHT_POSITION_MAX))

        self.left_position = max(left_lo, min(left_hi, self.left_position))
        self.right_position = max(right_lo, min(right_hi, self.right_position))

        # ── Publish positions ────────────────────────────────────────────
        pos_msg = Int32MultiArray()
        pos_msg.data = [int(self.left_position), int(self.right_position)]
        self.pos_pub.publish(pos_msg)

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
