#!/usr/bin/env python3
"""
WT901B IMU ROS2 Humble Node — I2C Interface
=============================================
Reads acceleration, angular velocity, and quaternion from the WitMotion
WT901B over I2C using the smbus2 library, and publishes:
  - /imu/data        (sensor_msgs/Imu)       — with quaternion + accel + gyro
  - /imu/data_raw    (sensor_msgs/Imu)       — raw accel + gyro, no orientation
  - /imu/mag         (sensor_msgs/MagneticField)

WT901B I2C Register Map (each register = 2 signed bytes, LSB first):
  0x34 AX   0x35 AY   0x36 AZ   — Acceleration
  0x37 GX   0x38 GY   0x39 GZ   — Angular Velocity
  0x3A HX   0x3B HY   0x3C HZ   — Magnetometer
  0x3D Roll 0x3E Pitch 0x3F Yaw — Euler Angles
  0x51 Q0   0x52 Q1   0x53 Q2   0x54 Q3 — Quaternion

Default I2C address: 0x50
"""

import struct
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from sensor_msgs.msg import Imu, MagneticField
from std_msgs.msg import Header
import math

try:
    import smbus2
except ImportError:
    raise ImportError(
        "smbus2 is not installed. Run: pip3 install smbus2 --break-system-packages"
    )

# ── Register addresses ──────────────────────────────────────────────────────
REG_AX    = 0x34
REG_AY    = 0x35
REG_AZ    = 0x36
REG_GX    = 0x37
REG_GY    = 0x38
REG_GZ    = 0x39
REG_HX    = 0x3A
REG_HY    = 0x3B
REG_HZ    = 0x3C
REG_ROLL  = 0x3D
REG_PITCH = 0x3E
REG_YAW   = 0x3F
REG_Q0    = 0x51
REG_Q1    = 0x52
REG_Q2    = 0x53
REG_Q3    = 0x54

# ── Physical scale factors ───────────────────────────────────────────────────
ACC_SCALE  = 16.0 * 9.80665 / 32768.0   # → m/s²
GYRO_SCALE = 2000.0 * math.pi / 180.0 / 32768.0  # → rad/s
MAG_SCALE  = 1.0 / 100.0                # → µT  (raw is in 0.01 µT units)
QUAT_SCALE = 1.0 / 32768.0             # → normalised


def _to_int16(low: int, high: int) -> int:
    """Combine two bytes into a signed 16-bit integer."""
    raw = (high << 8) | low
    return struct.unpack('h', struct.pack('H', raw))[0]


class WT901BImuNode(Node):
    """ROS 2 Humble node that reads the WT901B over I2C and publishes IMU data."""

    def __init__(self):
        super().__init__('wt901b_imu_node')

        # ── Declare parameters ───────────────────────────────────────────────
        self.declare_parameter('i2c_bus',     1)        # /dev/i2c-N
        self.declare_parameter('i2c_address', 0x50)    # default WT901B addr
        self.declare_parameter('publish_rate', 100.0)  # Hz
        self.declare_parameter('frame_id',    'imu_link')
        self.declare_parameter('publish_mag',  True)
        self.declare_parameter('publish_raw',  True)

        self.i2c_bus     = self.get_parameter('i2c_bus').value
        self.i2c_address = self.get_parameter('i2c_address').value
        self.publish_rate = self.get_parameter('publish_rate').value
        self.frame_id    = self.get_parameter('frame_id').value
        self.publish_mag = self.get_parameter('publish_mag').value
        self.publish_raw = self.get_parameter('publish_raw').value

        self.get_logger().info(
            f'WT901B I2C — bus=/dev/i2c-{self.i2c_bus}, '
            f'address=0x{self.i2c_address:02X}, '
            f'rate={self.publish_rate} Hz'
        )

        # ── Open I2C bus ─────────────────────────────────────────────────────
        try:
            self.bus = smbus2.SMBus(self.i2c_bus)
        except Exception as e:
            self.get_logger().fatal(
                f'Cannot open /dev/i2c-{self.i2c_bus}: {e}\n'
                'Make sure i2c is enabled and user is in the i2c group:\n'
                '  sudo usermod -aG i2c $USER'
            )
            raise

        # ── Publishers ───────────────────────────────────────────────────────
        self.pub_imu = self.create_publisher(Imu, 'imu/data', 10)

        if self.publish_raw:
            self.pub_raw = self.create_publisher(Imu, 'imu/data_raw', 10)

        if self.publish_mag:
            self.pub_mag = self.create_publisher(MagneticField, 'imu/mag', 10)

        # ── Timer ────────────────────────────────────────────────────────────
        period = 1.0 / self.publish_rate
        self.timer = self.create_timer(period, self.read_and_publish)

        self.get_logger().info('WT901B IMU node started successfully.')

    # ── I2C helpers ──────────────────────────────────────────────────────────

    def _read_register(self, reg: int) -> int:
        """Read a single 16-bit signed register (2 bytes, LSB first)."""
        data = self.bus.read_i2c_block_data(self.i2c_address, reg, 2)
        return _to_int16(data[0], data[1])

    def _read_block(self, start_reg: int, num_regs: int) -> list[int]:
        """Read `num_regs` consecutive 16-bit registers starting at start_reg."""
        num_bytes = num_regs * 2
        data = self.bus.read_i2c_block_data(self.i2c_address, start_reg, num_bytes)
        values = []
        for i in range(num_regs):
            values.append(_to_int16(data[i * 2], data[i * 2 + 1]))
        return values

    # ── Main callback ─────────────────────────────────────────────────────────

    def read_and_publish(self):
        now = self.get_clock().now().to_msg()
        header = Header(stamp=now, frame_id=self.frame_id)

        try:
            # Read acceleration + gyro in one 6-register burst (12 bytes)
            raw_acc_gyr = self._read_block(REG_AX, 6)
            ax_raw, ay_raw, az_raw = raw_acc_gyr[0], raw_acc_gyr[1], raw_acc_gyr[2]
            gx_raw, gy_raw, gz_raw = raw_acc_gyr[3], raw_acc_gyr[4], raw_acc_gyr[5]

            # Read quaternion in one 4-register burst (8 bytes)
            raw_quat = self._read_block(REG_Q0, 4)
            q0_raw, q1_raw, q2_raw, q3_raw = raw_quat

            # Scale
            ax = ax_raw * ACC_SCALE
            ay = ay_raw * ACC_SCALE
            az = az_raw * ACC_SCALE

            gx = gx_raw * GYRO_SCALE
            gy = gy_raw * GYRO_SCALE
            gz = gz_raw * GYRO_SCALE

            # Normalise quaternion (q0=w, q1=x, q2=y, q3=z in WitMotion convention)
            q_w = q0_raw * QUAT_SCALE
            q_x = q1_raw * QUAT_SCALE
            q_y = q2_raw * QUAT_SCALE
            q_z = q3_raw * QUAT_SCALE

            norm = math.sqrt(q_w**2 + q_x**2 + q_y**2 + q_z**2)
            if norm > 0.001:
                q_w /= norm
                q_x /= norm
                q_y /= norm
                q_z /= norm
            else:
                # Fallback to identity quaternion if reading is garbage
                q_w, q_x, q_y, q_z = 1.0, 0.0, 0.0, 0.0

        except Exception as e:
            self.get_logger().warn(f'I2C read error: {e}', throttle_duration_sec=2.0)
            return

        # ── Publish /imu/data (orientation + accel + gyro) ───────────────────
        imu_msg = Imu()
        imu_msg.header = header

        imu_msg.orientation.w = q_w
        imu_msg.orientation.x = q_x
        imu_msg.orientation.y = q_y
        imu_msg.orientation.z = q_z
        # Covariance — diagonal, tuned for WT901B (0.05° accuracy = ~0.001 rad)
        imu_msg.orientation_covariance = [
            1e-4, 0.0, 0.0,
            0.0, 1e-4, 0.0,
            0.0, 0.0, 1e-3,   # yaw is less accurate
        ]

        imu_msg.angular_velocity.x = gx
        imu_msg.angular_velocity.y = gy
        imu_msg.angular_velocity.z = gz
        imu_msg.angular_velocity_covariance = [
            1e-5, 0.0, 0.0,
            0.0, 1e-5, 0.0,
            0.0, 0.0, 1e-5,
        ]

        imu_msg.linear_acceleration.x = ax
        imu_msg.linear_acceleration.y = ay
        imu_msg.linear_acceleration.z = az
        imu_msg.linear_acceleration_covariance = [
            1e-4, 0.0, 0.0,
            0.0, 1e-4, 0.0,
            0.0, 0.0, 1e-4,
        ]

        self.pub_imu.publish(imu_msg)

        # ── Publish /imu/data_raw (no orientation) ───────────────────────────
        if self.publish_raw:
            raw_msg = Imu()
            raw_msg.header = header
            # Orientation unknown → fill covariance with -1 in first element
            raw_msg.orientation_covariance[0] = -1.0
            raw_msg.angular_velocity.x = gx
            raw_msg.angular_velocity.y = gy
            raw_msg.angular_velocity.z = gz
            raw_msg.angular_velocity_covariance = imu_msg.angular_velocity_covariance
            raw_msg.linear_acceleration.x = ax
            raw_msg.linear_acceleration.y = ay
            raw_msg.linear_acceleration.z = az
            raw_msg.linear_acceleration_covariance = imu_msg.linear_acceleration_covariance
            self.pub_raw.publish(raw_msg)

        # ── Publish /imu/mag ─────────────────────────────────────────────────
        if self.publish_mag:
            try:
                raw_mag = self._read_block(REG_HX, 3)
                mag_msg = MagneticField()
                mag_msg.header = header
                # Convert to Tesla (raw is µT * 100 → /1e8 to get T)
                mag_msg.magnetic_field.x = raw_mag[0] * MAG_SCALE * 1e-6
                mag_msg.magnetic_field.y = raw_mag[1] * MAG_SCALE * 1e-6
                mag_msg.magnetic_field.z = raw_mag[2] * MAG_SCALE * 1e-6
                mag_msg.magnetic_field_covariance = [
                    1e-12, 0.0, 0.0,
                    0.0, 1e-12, 0.0,
                    0.0, 0.0, 1e-12,
                ]
                self.pub_mag.publish(mag_msg)
            except Exception as e:
                self.get_logger().warn(f'Magnetometer read error: {e}',
                                       throttle_duration_sec=5.0)

    def destroy_node(self):
        """Close I2C bus on shutdown."""
        try:
            self.bus.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WT901BImuNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()