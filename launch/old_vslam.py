import launch
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    """Launch file which brings up visual slam node configured for RealSense."""
    realsense_camera_node = ComposableNode(
        name='camera',
        namespace='camera',
        package='realsense2_camera',
        executable='realsense2_camera_node',
        parameters=[{
            'enable_infra1': True,
            'enable_infra2': True,
            'enable_color': True,
            'enable_depth': True,
            'depth_module.emitter_enabled': 0,
            'depth_module.profile': '640x360x90',
        }],
    )

    static_camera_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_camera_tf',
        arguments=[
            '0', '0', '0.25',          # translation x y z (meters)
            '0', '-0.261799', '0',      # roll pitch yaw (radians)
            'base_link',
            'camera_link'
        ],
        output='screen',
    )

    visual_slam_node = ComposableNode(
        name='visual_slam_node',
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'enable_image_denoising': False,
            'rectified_images': True,
            'enable_imu_fusion': True,
            'gyro_noise_density': 0.000244,
            'gyro_random_walk': 0.000019393,
            'accel_noise_density': 0.001862,
            'accel_random_walk': 0.003,
            'calibration_frequency': 200.0,
            'image_jitter_threshold_ms': 22.00,
            'base_frame': 'base_link',
            'imu_frame': 'camera_gyro_optical_frame',
            'enable_slam_visualization': True,
            'enable_landmarks_view': True,
            'enable_observations_view': True,
            'camera_optical_frames': [
                'camera_infra1_optical_frame',
                'camera_infra2_optical_frame',
            ],
            'publish_map_to_odom_tf': False,            
            'publish_odom_to_base_tf': False,            
            'enable_localization_n_mapping': False
        }],
        remappings=[
            ('visual_slam/image_0', 'camera/infra1/image_rect_raw'),
            ('visual_slam/camera_info_0', 'camera/infra1/camera_info'),
            ('visual_slam/image_1', 'camera/infra2/image_rect_raw'),
            ('visual_slam/camera_info_1', 'camera/infra2/camera_info'),
            ('visual_slam/imu', 'camera/imu'),
        ],
    )

    visual_slam_launch_container = ComposableNodeContainer(
        name='visual_slam_launch_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[visual_slam_node],
        output='screen',
    )

    return launch.LaunchDescription([static_camera_tf, visual_slam_launch_container, realsense_camera_node])
