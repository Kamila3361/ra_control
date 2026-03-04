from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('imu')
    default_config = os.path.join(pkg_share, 'config', 'params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=default_config,
            description='Path to the YAML parameters file'
        ),

        Node(
            package='imu',
            executable='wt901b_imu_node',
            name='wt901b_imu_node',
            output='screen',
            parameters=[LaunchConfiguration('params_file')],
            remappings=[
                # Remap topics if needed, e.g. to standard /imu/data
                # ('imu/data', '/imu/data'),
            ]
        )
    ])