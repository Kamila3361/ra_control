#!/usr/bin/env python3
"""
dynamic_sensor_tf.py

Dynamically publishes camera_link and imu_link TFs from base_link,
correcting for variable left/right wheel radii.

base_link is at ground level, centered between the two wheel contact points.
Sensors are rigidly mounted on the chassis (which is fixed to the wheel axle).

Two effects are corrected:
  1. Both wheels change → axle height changes → sensor Z changes
  2. Wheels are unequal → chassis rolls → sensor Y and Z both change
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Float32MultiArray
from tf2_ros import TransformBroadcaster
import math

from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy


class DynamicSensorTF(Node):

    def __init__(self):
        super().__init__('dynamic_sensor_tf')

        # ── Parameters ───────────────────────────────────────────────────────

        # IMPORTANT: nominal_wheel_radius is the wheel radius at which you
        # measured/calculated your original static TF values.
        # Change this to match your actual robot!
        self.declare_parameter('nominal_wheel_radius', 0.2575)   # ← SET THIS

        # Distance between left and right wheel contact points (meters)
        self.declare_parameter('track_width', 0.45)            # ← SET THIS

        # Camera nominal TF values (from your static_transform_publisher)
        # These are valid only at nominal_wheel_radius with both wheels equal
        self.declare_parameter('cam_x_nom',     0.1560543)
        self.declare_parameter('cam_y_nom',     0.0)
        self.declare_parameter('cam_z_nom',     0.301835)
        self.declare_parameter('cam_roll_nom',  0.0)
        self.declare_parameter('cam_pitch_nom', -0.27680922)
        self.declare_parameter('cam_yaw_nom',   0.0)

        # IMU nominal TF values
        self.declare_parameter('imu_x_nom',     0.0)
        self.declare_parameter('imu_y_nom',     0.0)
        self.declare_parameter('imu_z_nom',     0.3070197)
        self.declare_parameter('imu_roll_nom',  0.0)
        self.declare_parameter('imu_pitch_nom', -0.27680922)
        self.declare_parameter('imu_yaw_nom',   0.0)
        # self.declare_parameter('imu_roll_nom',  0.27680922)
        # self.declare_parameter('imu_pitch_nom', 0)
        # self.declare_parameter('imu_yaw_nom',   -1.5708)

        # ── Derive sensor positions relative to axle center ──────────────────
        #
        # Your nominal TF z-values include the wheel radius:
        #   z_from_ground = z_from_axle + nominal_wheel_radius
        #
        # So we extract the "true" mechanical offset from the axle:
        #   z_from_axle = z_from_ground - nominal_wheel_radius
        #
        # X and Y are not affected by wheel radius (horizontal distances)

        r_nom = self.get_parameter('nominal_wheel_radius').value
        self.track_width = self.get_parameter('track_width').value

        self.cam_from_axle = {
            'x':     self.get_parameter('cam_x_nom').value,
            'y':     self.get_parameter('cam_y_nom').value,
            'z':     self.get_parameter('cam_z_nom').value - r_nom,  # ← key step
            'roll':  self.get_parameter('cam_roll_nom').value,
            'pitch': self.get_parameter('cam_pitch_nom').value,
            'yaw':   self.get_parameter('cam_yaw_nom').value,
        }

        self.imu_from_axle = {
            'x':     self.get_parameter('imu_x_nom').value,
            'y':     self.get_parameter('imu_y_nom').value,
            'z':     self.get_parameter('imu_z_nom').value - r_nom,  # ← key step
            'roll':  self.get_parameter('imu_roll_nom').value,
            'pitch': self.get_parameter('imu_pitch_nom').value,
            'yaw':   self.get_parameter('imu_yaw_nom').value,
        }

        # ── State ─────────────────────────────────────────────────────────────
        self.r_left  = r_nom   # start at nominal
        self.r_right = r_nom

        # ── TF broadcaster ────────────────────────────────────────────────────
        self.tf_broadcaster = TransformBroadcaster(self)

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # ── Subscriber: receives [left_radius, right_radius] in meters ────────
        self.create_subscription(
            Float32MultiArray,
            '/wheel_radii',
            self.wheel_radii_callback,
            qos_profile
        )

        # ── Timer: publish TF at 50 Hz ────────────────────────────────────────
        self.create_timer(0.01, self.publish_transforms)

        self.get_logger().info(
            f'\n=== Dynamic Sensor TF Node Started ===\n'
            f'  Nominal wheel radius : {r_nom} m\n'
            f'  Track width          : {self.track_width} m\n'
            f'  Camera from axle     : x={self.cam_from_axle["x"]:.4f}  '
            f'y={self.cam_from_axle["y"]:.4f}  z={self.cam_from_axle["z"]:.4f}\n'
            f'  IMU from axle        : x={self.imu_from_axle["x"]:.4f}  '
            f'y={self.imu_from_axle["y"]:.4f}  z={self.imu_from_axle["z"]:.4f}'
        )

    # ──────────────────────────────────────────────────────────────────────────
    def wheel_radii_callback(self, msg: Float32MultiArray):
        """
        Receive current wheel radii from your wheel-size motor controller.
        msg.data = [left_radius_meters, right_radius_meters]
        """
        if len(msg.data) >= 2:
            self.r_left  = float(msg.data[0])
            self.r_right = float(msg.data[1])

    # ──────────────────────────────────────────────────────────────────────────
    def sensor_tf_from_base_link(self, sensor: dict) -> tuple:
        """
        Convert a sensor's fixed axle-relative position into
        base_link-relative position, accounting for:

          1. axle_height = average wheel radius
             → sensors go up/down when both wheels change size

          2. chassis_roll = atan2(r_left - r_right, track_width)
             → sensors swing in Y and Z when wheels are unequal

        Coordinate convention:
          X = forward
          Y = left
          Z = up
          Roll rotates around X axis → affects Y and Z

        Args:
            sensor: dict with keys x, y, z (from axle center), roll, pitch, yaw

        Returns:
            (x, y, z, roll, pitch, yaw) relative to base_link
        """

        # ── Effect 1: How high is the axle above the ground? ─────────────────
        axle_height = (self.r_left + self.r_right) / 2.0

        # ── Effect 2: How much is the chassis tilted? ─────────────────────────
        # atan2(height_diff, track_width) gives the roll angle
        # Positive = left wheel bigger = robot rolls to the right
        chassis_roll = math.atan2(
            self.r_left - self.r_right,
            self.track_width
        )

        # ── Rotate sensor position by chassis roll ────────────────────────────
        # Roll is around X axis:
        #   y_new = y * cos(roll) - z * sin(roll)
        #   z_new = y * sin(roll) + z * cos(roll)
        #   x_new = x  (unchanged by roll)
        x = sensor['x']
        y = sensor['y']
        z = sensor['z']

        x_rot = x
        y_rot = y * math.cos(chassis_roll) - z * math.sin(chassis_roll)
        z_rot = y * math.sin(chassis_roll) + z * math.cos(chassis_roll)

        # ── Add axle height to get final Z from base_link (ground) ───────────
        x_final = x_rot
        y_final = y_rot
        z_final = axle_height + z_rot   # axle height + rotated sensor offset

        # ── Orientation: sensor inherits chassis roll ─────────────────────────
        roll_final  = sensor['roll']  + chassis_roll
        pitch_final = sensor['pitch']              # pitch unaffected by left/right tilt
        yaw_final   = sensor['yaw']

        return x_final, y_final, z_final, roll_final, pitch_final, yaw_final

    # ──────────────────────────────────────────────────────────────────────────
    def make_transform(self, parent: str, child: str,
                        x, y, z, roll, pitch, yaw) -> TransformStamped:
        t = TransformStamped()
        t.header.stamp    = self.get_clock().now().to_msg()
        t.header.frame_id = parent
        t.child_frame_id  = child

        t.transform.translation.x = x
        t.transform.translation.y = y
        t.transform.translation.z = z

        # Convert roll/pitch/yaw to quaternion
        cr, sr = math.cos(roll  / 2), math.sin(roll  / 2)
        cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
        cy, sy = math.cos(yaw   / 2), math.sin(yaw   / 2)

        t.transform.rotation.x = sr * cp * cy - cr * sp * sy
        t.transform.rotation.y = cr * sp * cy + sr * cp * sy
        t.transform.rotation.z = cr * cp * sy - sr * sp * cy
        t.transform.rotation.w = cr * cp * cy + sr * sp * sy

        return t

    # ──────────────────────────────────────────────────────────────────────────
    def publish_transforms(self):
        # Camera
        cx, cy, cz, cr, cp, cyw = self.sensor_tf_from_base_link(self.cam_from_axle)
        cam_tf = self.make_transform(
            'base_link', 'camera_link', cx, cy, cz, cr, cp, cyw
        )

        # IMU
        ix, iy, iz, ir, ip, iyw = self.sensor_tf_from_base_link(self.imu_from_axle)
        imu_tf = self.make_transform(
            'base_link', 'imu_link', ix, iy, iz, ir, ip, iyw
        )

        self.tf_broadcaster.sendTransform([cam_tf, imu_tf])


# ──────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = DynamicSensorTF()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
