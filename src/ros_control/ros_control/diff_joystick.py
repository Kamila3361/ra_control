#!/usr/bin/env python3
"""
Joystick publisher — Twist on /cmd_vel + incremental position control.

Axis mapping (PS-style controller)
------------------------------------
  Axis 0  → angular.z   (turn left / right)
  Axis 1  → linear.x    (forward / backward)
  Axis 2  → LEFT  wheel position increment/decrement
  Axis 5  → RIGHT wheel position increment/decrement

Position control behaviour
---------------------------
  Axis 2/5 act like a velocity input into an integrator:
    - held positive  → position increases (ramps up) at up to
                        POSITION_INCREMENT_RATE units/sec at full deflection
    - held negative  → position decreases at the same max rate
    - released (within deadband) → position holds its last value (no drift)
  The integrated position is clamped to the motor's
  [POSITION_MIN, POSITION_MAX] range and published every tick on
  /wheel_position_cmd as Int32MultiArray = [left_position, right_position].
"""

import time
import rclpy
from rclpy.node import Node
import pygame

from geometry_msgs.msg import Twist
from std_msgs.msg import Int32MultiArray

# ── Joystick filtering ─────────────────────────────────────────────────────
ALPHA              = 0.2    # low-pass filter weight (0 = frozen, 1 = raw)
DEADBAND_THRESHOLD = 0.05

# ── Robot drive limits ─────────────────────────────────────────────────────
MAX_LINEAR_SPEED  = 1.0     # m/s
MAX_ANGULAR_SPEED = 3.0     # rad/s

# ── Position motor mapping ─────────────────────────────────────────────────
LEFT_POSITION_MIN  = -300000
LEFT_POSITION_MAX  =  185000
RIGHT_POSITION_MAX =  300000
RIGHT_POSITION_MIN = -185000

# ── Incremental position control ───────────────────────────────────────────
POSITION_INCREMENT_RATE = 15000.0   # units/sec at full axis deflection


class JoystickPublisher(Node):

    def __init__(self):
        super().__init__('joystick_publisher')

        # ── Parameters ────────────────────────────────────────────────────
        self.declare_parameter('publish_rate',      50.0)
        self.declare_parameter('alpha',              ALPHA)
        self.declare_parameter('deadband',           DEADBAND_THRESHOLD)
        self.declare_parameter('max_linear',         MAX_LINEAR_SPEED)
        self.declare_parameter('max_angular',        MAX_ANGULAR_SPEED)
        self.declare_parameter('position_increment_rate', POSITION_INCREMENT_RATE)

        self.alpha          = self.get_parameter('alpha').value
        self.deadband       = self.get_parameter('deadband').value
        self.max_linear     = self.get_parameter('max_linear').value
        self.max_angular    = self.get_parameter('max_angular').value
        self.increment_rate = self.get_parameter('position_increment_rate').value
        publish_rate        = self.get_parameter('publish_rate').value
        self.dt              = 1.0 / publish_rate

        # ── Publishers ────────────────────────────────────────────────────
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 1)
        self.position_pub = self.create_publisher(
            Int32MultiArray, 'wheel_position_cmd', 1
        )

        # ── State ─────────────────────────────────────────────────────────
        self.smoothed_linear  = 0.0   # axis 1
        self.smoothed_angular = 0.0   # axis 0
        self.smoothed_left_position  = 0.0   # axis 2 (filtered rate input)
        self.smoothed_right_position = 0.0   # axis 5 (filtered rate input)

        # Integrated absolute positions — start at the motors' neutral ends,
        # matching the original control.py _initialize_positions() behaviour.
        self.left_position  = float(LEFT_POSITION_MIN)
        self.right_position = float(RIGHT_POSITION_MAX)

        # ── Joystick init ─────────────────────────────────────────────────
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self._connect_joystick()

        self.timer = self.create_timer(self.dt, self._timer_callback)
        self.get_logger().info(
            f'Joystick publisher ready at {publish_rate} Hz — '
            f'Twist on /cmd_vel, positions on /wheel_position_cmd'
        )

    # ── Joystick connection ────────────────────────────────────────────────

    def _connect_joystick(self):
        self.get_logger().info('Waiting for joystick...')
        while self.joystick is None and rclpy.ok():
            pygame.joystick.quit()
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.get_logger().info(
                    f'Joystick "{self.joystick.get_name()}" connected'
                )
            else:
                self.get_logger().warn('No joystick found. Retrying...')
                time.sleep(1)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _filter(self, raw, previous):
        """Deadband + exponential low-pass filter."""
        if abs(raw) < self.deadband:
            raw = 0.0
        return self.alpha * raw + (1.0 - self.alpha) * previous

    # ── Main callback ──────────────────────────────────────────────────────

    def _timer_callback(self):
        if self.joystick is None:
            return

        pygame.event.pump()

        # ── Read axes ─────────────────────────────────────────────────────
        raw_angular         = -self.joystick.get_axis(0)   # turn left/right
        raw_linear           =  self.joystick.get_axis(1)   # forward/back
        raw_left_position   =  self.joystick.get_axis(2)   # left position rate
        raw_right_position  =  self.joystick.get_axis(5)   # right position rate

        # ── Filter ────────────────────────────────────────────────────────
        self.smoothed_linear  = self._filter(raw_linear,  self.smoothed_linear)
        self.smoothed_angular = self._filter(raw_angular, self.smoothed_angular)
        self.smoothed_left_position = self._filter(
            raw_left_position, self.smoothed_left_position
        )
        self.smoothed_right_position = self._filter(
            raw_right_position, self.smoothed_right_position
        )

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
        self.position_pub.publish(pos_msg)

    # ── Shutdown ───────────────────────────────────────────────────────────

    def destroy_node(self):
        # Send a zero-velocity Twist on exit
        self.cmd_vel_pub.publish(Twist())
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