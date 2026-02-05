#!/usr/bin/env python3
"""
Odometry Subscriber Node
Subscribes to encoder data and publishes odometry
Runs independently from motor control
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from ros_control_interfaces.msg import EncoderStamped
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, Quaternion
from tf2_ros import TransformBroadcaster
from std_srvs.srv import Empty

import numpy as np
import threading


class Pose2D:
    """Represents a 2D pose (x, y, theta)"""
    def __init__(self, x=0.0, y=0.0, theta=0.0):
        self.x = x
        self.y = y
        self.theta = theta
    
    def __repr__(self):
        return f"Pose2D(x={self.x:.4f}m, y={self.y:.4f}m, θ={np.degrees(self.theta):.2f}°)"


class OdometryComputer:
    """
    Computes odometry from encoder readings
    Uses differential drive kinematics
    """
    
    def __init__(self, wheel_radius, wheelbase, encoder_resolution, gear_ratio=1.0):
        self.wheel_radius = wheel_radius
        self.wheelbase = wheelbase
        self.encoder_resolution = encoder_resolution
        self.gear_ratio = gear_ratio  # wheel_rotations / motor_rotations (e.g. 1.4)
        
        # Current pose
        self.pose = Pose2D()
        
        # Previous encoder values
        self.prev_left_ticks = None
        self.prev_right_ticks = None
        self.prev_time = None
        
        # Velocity estimates
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        
        # Statistics
        self.total_distance = 0.0
        self.initialized = False
    
    def reset(self, x=0.0, y=0.0, theta=0.0):
        """Reset odometry to a specific pose"""
        self.pose = Pose2D(x, y, theta)
        self.total_distance = 0.0
        self.prev_left_ticks = None
        self.prev_right_ticks = None
        self.prev_time = None
        self.initialized = False
    
    def ticks_to_meters(self, ticks):
        """Convert encoder ticks to linear distance"""
        motor_revolutions = ticks / self.encoder_resolution
        wheel_revolutions = motor_revolutions * self.gear_ratio
        distance = wheel_revolutions * 2.0 * np.pi * self.wheel_radius
        return distance
    
    def update(self, left_ticks, right_ticks, timestamp):
        """
        Update odometry based on new encoder readings
        
        Args:
            left_ticks: Current left encoder reading
            right_ticks: Current right encoder reading
            timestamp: Message timestamp (rclpy.time.Time)
        
        Returns:
            (pose, linear_vel, angular_vel)
        """
        # Initialize on first reading
        if not self.initialized:
            self.prev_left_ticks = left_ticks
            self.prev_right_ticks = right_ticks
            self.prev_time = timestamp
            self.initialized = True
            return self.pose, 0.0, 0.0
        
        # Calculate time delta
        dt = (timestamp - self.prev_time).nanoseconds / 1e9
        if dt <= 0:
            return self.pose, self.linear_velocity, self.angular_velocity
        
        # Calculate change in encoder ticks
        delta_left_ticks = left_ticks - self.prev_left_ticks
        delta_right_ticks = right_ticks - self.prev_right_ticks

        delta_left_ticks *= -1  # Invert left encoder
        
        # Convert to linear distances
        delta_left = self.ticks_to_meters(delta_left_ticks)
        delta_right = self.ticks_to_meters(delta_right_ticks)
        
        # Calculate displacement and rotation
        delta_s = (delta_left + delta_right) / 2.0  # Linear displacement
        delta_theta = (delta_right - delta_left) / self.wheelbase  # Angular displacement
        
        # Update pose using differential drive kinematics
        # Using midpoint method for better accuracy
        if abs(delta_theta) < 1e-6:  # Straight line motion
            delta_x = delta_s * np.cos(self.pose.theta)
            delta_y = delta_s * np.sin(self.pose.theta)
        else:
            # Arc motion
            delta_x = delta_s * np.cos(self.pose.theta + delta_theta / 2.0)
            delta_y = delta_s * np.sin(self.pose.theta + delta_theta / 2.0)
        
        # Update pose
        self.pose.x += delta_x
        self.pose.y += delta_y
        self.pose.theta += delta_theta
        
        # Normalize theta to [-pi, pi]
        self.pose.theta = np.arctan2(np.sin(self.pose.theta), np.cos(self.pose.theta))
        
        # Update velocities
        self.linear_velocity = delta_s / dt
        self.angular_velocity = delta_theta / dt
        
        # Update statistics
        self.total_distance += abs(delta_s)
        
        # Store current values for next iteration
        self.prev_left_ticks = left_ticks
        self.prev_right_ticks = right_ticks
        self.prev_time = timestamp
        
        return self.pose, self.linear_velocity, self.angular_velocity


class OdometrySubscriberNode(Node):
    """
    ROS 2 Node that subscribes to encoder data and publishes odometry
    """
    
    def __init__(self):
        super().__init__('odometry_subscriber_node')
        
        # Declare parameters
        self.declare_parameters(
            namespace='',
            parameters=[
                # Robot physical parameters
                ('wheel_radius', 0.2575),
                ('wheelbase', 0.45),
                ('encoder_resolution', 607500),
                ('gear_ratio', 1.4),
                
                # ROS parameters
                ('encoder_topic', 'encoder'),
                ('odom_topic', 'odom'),
                ('odom_frame', 'odom'),
                ('base_frame', 'base_footprint'),
                ('publish_tf', True),
            ]
        )
        
        # Get parameters
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.wheelbase = self.get_parameter('wheelbase').value
        self.encoder_resolution = self.get_parameter('encoder_resolution').value
        self.gear_ratio = self.get_parameter('gear_ratio').value
        
        self.encoder_topic = self.get_parameter('encoder_topic').value
        self.odom_topic = self.get_parameter('odom_topic').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        self.publish_tf = self.get_parameter('publish_tf').value
        
        # Log parameters
        self.get_logger().info('='*60)
        self.get_logger().info('Odometry Subscriber Node Starting')
        self.get_logger().info('='*60)
        self.get_logger().info(f'Wheel Radius: {self.wheel_radius} m')
        self.get_logger().info(f'Wheelbase: {self.wheelbase} m')
        self.get_logger().info(f'Encoder Resolution: {self.encoder_resolution}')
        self.get_logger().info(f'Encoder Topic: {self.encoder_topic}')
        self.get_logger().info(f'Odometry Topic: {self.odom_topic}')
        self.get_logger().info(f'Odometry Frame: {self.odom_frame}')
        self.get_logger().info(f'Base Frame: {self.base_frame}')
        self.get_logger().info(f'Publish TF: {self.publish_tf}')
        
        # Initialize odometry computer
        self.odom_computer = OdometryComputer(
            self.wheel_radius,
            self.wheelbase,
            self.encoder_resolution,
            self.gear_ratio
        )
        
        # QoS profiles
        encoder_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        odom_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # Create subscriber
        self.encoder_sub = self.create_subscription(
            EncoderStamped,
            self.encoder_topic,
            self.encoder_callback,
            encoder_qos
        )
        
        # Create publisher
        self.odom_pub = self.create_publisher(
            Odometry,
            self.odom_topic,
            odom_qos
        )
        
        # Create TF broadcaster
        if self.publish_tf:
            self.tf_broadcaster = TransformBroadcaster(self)
        
        # Create service to reset odometry
        self.reset_service = self.create_service(
            Empty,
            '~/reset_odometry',
            self.reset_odometry_callback
        )
        
        # Thread lock
        self.lock = threading.Lock()
        
        self.get_logger().info('Odometry subscriber initialized successfully')
        self.get_logger().info(f'Subscribing to: {self.encoder_topic}')
        self.get_logger().info(f'Publishing to: {self.odom_topic}')
        self.get_logger().info('='*60)
    
    def encoder_callback(self, msg):
        """
        Callback for encoder messages
        Computes and publishes odometry
        """
        try:
            with self.lock:
                # Get timestamp from message
                timestamp = rclpy.time.Time.from_msg(msg.header.stamp)
                
                # Update odometry
                pose, linear_vel, angular_vel = self.odom_computer.update(
                    msg.left_encoder,
                    msg.right_encoder,
                    timestamp
                )
            
            # Create and publish odometry message
            odom_msg = self.create_odometry_message(
                pose, linear_vel, angular_vel, msg.header.stamp
            )
            self.odom_pub.publish(odom_msg)
            
            # Broadcast TF if enabled
            if self.publish_tf:
                self.broadcast_tf(pose, msg.header.stamp)
                
        except Exception as e:
            self.get_logger().error(f'Error in encoder callback: {e}')
    
    def create_odometry_message(self, pose, linear_vel, angular_vel, timestamp):
        """Create nav_msgs/Odometry message"""
        odom = Odometry()
        odom.header.stamp = timestamp
        odom.header.frame_id = self.odom_frame
        odom.child_frame_id = self.base_frame
        
        # Position
        odom.pose.pose.position.x = pose.x
        odom.pose.pose.position.y = pose.y
        odom.pose.pose.position.z = 0.0
        
        # Orientation (convert theta to quaternion)
        odom.pose.pose.orientation = self.theta_to_quaternion(pose.theta)
        
        # Velocity
        odom.twist.twist.linear.x = linear_vel
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.linear.z = 0.0
        odom.twist.twist.angular.x = 0.0
        odom.twist.twist.angular.y = 0.0
        odom.twist.twist.angular.z = angular_vel
        
        # Covariance matrices
        # Position covariance (x, y, z, rotation about X, Y, Z)
        odom.pose.covariance = [
            1e-3, 0.0,  0.0,  0.0,  0.0,  0.0,
            0.0,  1e-3, 0.0,  0.0,  0.0,  0.0,
            0.0,  0.0,  1e6,  0.0,  0.0,  0.0,
            0.0,  0.0,  0.0,  1e6,  0.0,  0.0,
            0.0,  0.0,  0.0,  0.0,  1e6,  0.0,
            0.0,  0.0,  0.0,  0.0,  0.0,  1e-3
        ]
        
        # Velocity covariance
        odom.twist.covariance = [
            1e-3, 0.0,  0.0,  0.0,  0.0,  0.0,
            0.0,  1e6,  0.0,  0.0,  0.0,  0.0,
            0.0,  0.0,  1e6,  0.0,  0.0,  0.0,
            0.0,  0.0,  0.0,  1e6,  0.0,  0.0,
            0.0,  0.0,  0.0,  0.0,  1e6,  0.0,
            0.0,  0.0,  0.0,  0.0,  0.0,  1e-3
        ]
        
        return odom
    
    def broadcast_tf(self, pose, timestamp):
        """Broadcast TF transform"""
        transform = TransformStamped()
        transform.header.stamp = timestamp
        transform.header.frame_id = self.odom_frame
        transform.child_frame_id = self.base_frame
        
        # Translation
        transform.transform.translation.x = pose.x
        transform.transform.translation.y = pose.y
        transform.transform.translation.z = 0.0
        
        # Rotation
        transform.transform.rotation = self.theta_to_quaternion(pose.theta)
        
        # Broadcast
        self.tf_broadcaster.sendTransform(transform)
    
    def theta_to_quaternion(self, theta):
        """Convert yaw angle to quaternion"""
        quat = Quaternion()
        quat.x = 0.0
        quat.y = 0.0
        quat.z = np.sin(theta / 2.0)
        quat.w = np.cos(theta / 2.0)
        return quat
    
    def reset_odometry_callback(self, request, response):
        """Service callback to reset odometry"""
        with self.lock:
            self.odom_computer.reset()
        
        self.get_logger().info('Odometry reset to origin')
        return response


def main(args=None):
    rclpy.init(args=args)
    
    try:
        node = OdometrySubscriberNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()