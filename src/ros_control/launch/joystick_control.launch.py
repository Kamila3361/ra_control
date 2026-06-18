from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """
    Launch file for joystick-controlled Dynamixel motor system.
    
    Launches:
    - joystick_publisher: Reads joystick input and publishes commands
    - dynamixel_control: Controls Dynamixel motors based on joystick commands
    """
    
    # Declare launch arguments for easy configuration
    declare_publish_rate = DeclareLaunchArgument(
        'publish_rate',
        default_value='50.0',
        description='Joystick publishing rate in Hz'
    )
    
    declare_alpha = DeclareLaunchArgument(
        'alpha',
        default_value='0.2',
        description='Low-pass filter coefficient (0.0-1.0)'
    )
    
    declare_deadband = DeclareLaunchArgument(
        'deadband',
        default_value='0.05',
        description='Joystick deadband threshold'
    )
    
    declare_max_rpm = DeclareLaunchArgument(
        'max_rpm',
        default_value='500',
        description='Maximum RPM for drive motors'
    )
    
    declare_device_name = DeclareLaunchArgument(
        'device_name',
        default_value='/dev/ttyUSB0',
        description='Dynamixel USB device path'
    )
    
    # Joystick publisher node
    joystick_node = Node(
        package='ros_control',  # Replace with your actual package name
        executable='joystick',
        name='joystick_publisher',
        output='screen',
        parameters=[{
            'publish_rate': LaunchConfiguration('publish_rate'),
            'alpha': LaunchConfiguration('alpha'),
            'deadband': LaunchConfiguration('deadband'),
            'max_rpm': LaunchConfiguration('max_rpm'),
        }],
        emulate_tty=True,
    )
    
    # Dynamixel control node
    control_node = Node(
        package='ros_control',  # Replace with your actual package name
        executable='control',
        name='control',
        output='screen',
        parameters=[{
            'device_name': LaunchConfiguration('device_name'),
        }],
        emulate_tty=True,
    )

    static_camera_tf_camera = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_camera_tf',
        arguments=[
            '0.1560543', '0', '0.301835',          # translation x y z (meters)
            '0', '-0.27680922', '0',      # roll pitch yaw (radians)
            'base_link',
            'camera_link'
        ],
        output='screen',
    )

    static_camera_tf_imu = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_imu_tf',
        arguments=[
            '0', '0', '0.3070197',          # translation x y z (meters)
            '0', '-0.27680922', '0',      # roll pitch yaw (radians)
            'base_link',
            'imu_link'
        ],
        output='screen',
    )

    return LaunchDescription([
        # Launch arguments
        declare_publish_rate,
        declare_alpha,
        declare_deadband,
        declare_max_rpm,
        declare_device_name,
        
        # Nodes
        joystick_node,
        control_node,
        static_camera_tf_camera,
        static_camera_tf_imu,
    ])
