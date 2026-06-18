#!/usr/bin/env python3
"""
Joystick publisher — publishes geometry_msgs/Twist to /cmd_vel.

Axis mapping (PS-style controller)
------------------------------------
  Axis 1 (left stick vertical)   → linear.x  (forward / backward)
  Axis 2 (left stick horizontal) → angular.z (turn left / right)

  Raw axis sign conventions vary by controller.  Axis 1 is negated so that
  pushing the stick forward gives a positive (forward) velocity.

Position motors (IDs 1 & 2) are still published separately on /joy so
that diff_drive_control.py can ignore them cleanly.  If you no longer run
control.py alongside this node, you can remove the /joy publisher below.
"""

import time
import math
import rclpy
from rclpy.node import Node
import pygame

from geometry_msgs.msg import Twist
from ros_control_interfaces.msg import MotorCommand, Joystick

# ── Joystick filtering ─────────────────────────────────────────────────────
ALPHA               = 0.2    # low-pass filter weight (0 = frozen, 1 = raw)
DEADBAND_THRESHOLD  = 0.05

# ── Robot limits ───────────────────────────────────────────────────────────
MAX_LINEAR_SPEED    = 1.0    # m/s   (matches diff_drive_control.py)
MAX_ANGULAR_SPEED   = 3.0    # rad/s (tune to taste; ~170 °/s)

# ── Position motor mapping (unchanged from original) ──────────────────────
LEFT_POSITION_MIN  = -300000
LEFT_POSITION_MAX  =  185000
RIGHT_POSITION_MAX =  300000
RIGHT_POSITION_MIN = -185000


class JoystickPublisher(Node):

    def __init__(self):
        super().__init__('joystick_publisher')

        # ── Parameters ────────────────────────────────────────────────────
        self.declare_parameter('publish_rate',    50.0)
        self.declare_parameter('alpha',           ALPHA)
        self.declare_parameter('deadband',        DEADBAND_THRESHOLD)
        self.declare_parameter('max_linear',      MAX_LINEAR_SPEED)
        self.declare_parameter('max_angular',     MAX_ANGULAR_SPEED)

        self.alpha        = self.get_parameter('alpha').value
        self.deadband     = self.get_parameter('deadband').value
        self.max_linear   = self.get_parameter('max_linear').value
        self.max_angular  = self.get_parameter('max_angular').value
        publish_rate      = self.get_parameter('publish_rate').value

        # ── Publishers ────────────────────────────────────────────────────
        # Primary: Twist on /cmd_vel  →  consumed by diff_drive_control.py
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 1)

        # Secondary: position commands on /joy  →  consumed by control.py
        # (remove if you no longer run control.py)
        self.joy_pub = self.create_publisher(Joystick, 'joy', 1)

        # ── State ─────────────────────────────────────────────────────────
        self.smoothed_linear  = 0.0   # axis 1 (forward/back)
        self.smoothed_angular = 0.0   # axis 2 (left/right turn)

        # ── Joystick init ─────────────────────────────────────────────────
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        self._connect_joystick()

        self.timer = self.create_timer(1.0 / publish_rate, self._timer_callback)
        self.get_logger().info(
            f'Joystick publisher ready at {publish_rate} Hz — '
            f'publishing Twist on /cmd_vel'
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

    def _map_to_position(self, value, side):
        """Map joystick axis [-1, 1] → position motor target (unchanged logic)."""
        if side == 'left':
            return int((1 + value) * (LEFT_POSITION_MIN - LEFT_POSITION_MAX)
                       + LEFT_POSITION_MAX)
        else:
            return int(RIGHT_POSITION_MAX
                       - value * (RIGHT_POSITION_MAX - RIGHT_POSITION_MIN))

    # ── Main callback ──────────────────────────────────────────────────────

    def _timer_callback(self):
        if self.joystick is None:
            return

        pygame.event.pump()

        # ── Read axes ─────────────────────────────────────────────────────
        # Axis 1: vertical   (negate so forward = positive)
        # Axis 2: horizontal (negate so left-push = positive angular.z = CCW turn)
        raw_linear  = -self.joystick.get_axis(1)   # forward/back
        raw_angular = -self.joystick.get_axis(2)   # left/right

        self.smoothed_linear  = self._filter(raw_linear,  self.smoothed_linear)
        self.smoothed_angular = self._filter(raw_angular, self.smoothed_angular)

        # ── Publish Twist ─────────────────────────────────────────────────
        twist = Twist()
        twist.linear.x  = self.smoothed_linear  * self.max_linear
        twist.angular.z = self.smoothed_angular * self.max_angular
        self.cmd_vel_pub.publish(twist)

        # ── Publish position commands on /joy (for control.py) ────────────
        axis_pos = self.joystick.get_axis(2)   # raw horizontal for position
        if axis_pos <= 0.0:
            side     = 'left'
            position = self._map_to_position(axis_pos, 'left')
        else:
            side     = 'right'
            position = self._map_to_position(axis_pos, 'right')

        joy_msg = Joystick()
        joy_msg.positions  = [MotorCommand(name=side, value=position)]
        joy_msg.velocities = []   # drive velocity is now handled via cmd_vel
        self.joy_pub.publish(joy_msg)

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