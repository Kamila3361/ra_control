from typing import List
from launch import Action, LaunchDescription
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import Node
import isaac_ros_launch_utils as lu
from nvblox_ros_python_utils.nvblox_launch_utils import NvbloxMode, NvbloxCamera
from nvblox_ros_python_utils.nvblox_constants import NVBLOX_CONTAINER_NAME
import isaac_ros_launch_utils.all_types as lut

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

from launch.actions import TimerAction

CAMERA_NAME = 'camera'

TOPIC_WHITELIST = [
    '/nvblox_node/.*_layer',
    '/nvblox_node/static_esdf_pointcloud',
    '/tf',
    '/tf_static',
    '/global_costmap/costmap',
    '/global_costmap/footprint',
    '/local_costmap/costmap',
    '/plan', 
    '/unsmoothed_plan',
    '/goal_pose'
]


def add_ekf(args: lu.ArgumentContainer) -> List[Action]:
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_local_node',
        output='screen',
        parameters=['/home/admin/config/ekf.yaml', {'use_sim_time': False}]
    )
    return [ekf_node]


def add_realsense(args: lu.ArgumentContainer) -> List[Action]:
    realsense_node = ComposableNode(
        namespace=CAMERA_NAME,
        package='realsense2_camera',
        plugin='realsense2_camera::RealSenseNodeFactory',
        parameters=[{
            'camera_name':                    CAMERA_NAME,
            'enable_infra1':                  True,
            'enable_infra2':                  True,
            'enable_color':                   True,
            'enable_depth':                   True,
            'enable_guro': False,
            'enable_accel': False,
            'depth_module.emitter_enabled':   2,       # on
            'depth_module.profile':           '640x360x30',
            'depth_qos': "SENSOR_DATA",
            'depth_info_qos': "SENSOR_DATA",
            'rgb_camera.profile': '640x480x15',
            'color_info_qos': "SENSOR_DATA",
            'color_qos': "SENSOR_DATA"
        }]
    )
    # Loaded into the same container as nvblox and vslam
    actions = []
    actions.append(lu.component_container(args.container_name))
    actions.append(lu.load_composable_nodes(args.container_name, [realsense_node]))
    return actions


def add_visual_slam(args: lu.ArgumentContainer) -> List[Action]:
    visual_slam_node = ComposableNode(
        name='visual_slam_node',
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'enable_image_denoising':     False,
            'rectified_images':           True,
            'enable_imu_fusion':          False,
            'base_frame':                 'base_link',
            'enable_slam_visualization':  False,
            'enable_landmarks_view':      False,
            'enable_observations_view':   False,
            'use_sim_time':               False,
            'publish_map_to_odom_tf':     False,
            'publish_odom_to_base_tf':    False,
            'camera_optical_frames': [
                'camera_infra1_optical_frame',
                'camera_infra2_optical_frame',
            ],
        }],
        remappings=[
            # RealSense publishes infra under /<camera_name>/infra1/...
            ('visual_slam/image_0',       f'/{CAMERA_NAME}/infra1/image_rect_raw'),
            ('visual_slam/camera_info_0', f'/{CAMERA_NAME}/infra1/camera_info'),
            ('visual_slam/image_1',       f'/{CAMERA_NAME}/infra2/image_rect_raw'),
            ('visual_slam/camera_info_1', f'/{CAMERA_NAME}/infra2/camera_info'),
        ],
    )
    # Same container — zero-copy from RealSense to cuVSLAM
    return [lu.load_composable_nodes(args.container_name, [visual_slam_node])]


def add_nvblox_navigation(args: lu.ArgumentContainer) -> List[Action]:
    actions = []
    nav_params_path = '/home/admin/config/nav.yaml'
    actions.append(lut.SetParametersFromFile(str(nav_params_path)))
    actions.append(lut.SetParameter('use_sim_time', False))
    actions.append(
        lu.include(
            'nav2_bringup',
            'launch/navigation_launch.py',
            launch_arguments={
                'params_file':    str(nav_params_path),
                'use_composition': 'False',
                'use_sim_time':   'False',
            },
        ))
    actions.append(
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='map_to_odom_static_tf',
            arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
            parameters=[{'use_sim_time': False}],
            output='screen',
        )
    )
    return actions


def add_nvblox(args: lu.ArgumentContainer) -> List[Action]:
    # base_config = lu.get_path('nvblox_examples_bringup', 'config/nvblox/nvblox_base.yaml')
    nvblox_config = '/home/admin/config/nv.yaml'

    remappings = [
        # nvblox expects depth + color; RealSense publishes under /<camera_name>/...
        ('camera_0/depth/image',       f'/{CAMERA_NAME}/depth/image_rect_raw'),
        ('camera_0/depth/camera_info', f'/{CAMERA_NAME}/depth/camera_info'),
        ('camera_0/color/image',       f'/{CAMERA_NAME}/color/image_raw'),
        ('camera_0/color/camera_info', f'/{CAMERA_NAME}/color/camera_info'),
    ]

    parameters = [
        # base_config,
        nvblox_config,
        {'num_cameras': 1},
        {'use_lidar': False},
        {'use_sim_time': False},
    ]

    nvblox_node = ComposableNode(
        name='nvblox_node',
        package='nvblox_ros',
        plugin='nvblox::NvbloxNode',
        remappings=remappings,
        parameters=parameters,
    )

    actions = []
    actions.append(lu.load_composable_nodes(args.container_name, [nvblox_node]))
    actions.append(lu.log_info("Starting nvblox in static mode with RealSense camera."))
    # actions.append(
    #     lu.include(
    #         'nvblox_examples_bringup',
    #         'launch/visualization/visualization.launch.py',
    #         launch_arguments={
    #             'run_foxglove': True,
    #             'run_rviz': False
    #         }))
    
    return actions

# def add_foxglove_bridge(args: lu.ArgumentContainer) -> List[Action]:
#     foxglove_bridge = IncludeLaunchDescription(
#         AnyLaunchDescriptionSource(
#             os.path.join(
#                 get_package_share_directory('foxglove_bridge'),
#                 'launch',
#                 'foxglove_bridge_launch.xml'
#             )
#         ),
#         launch_arguments={'topic_whitelist': '["' + '","'.join(TOPIC_WHITELIST) + '"]', 'max_qos_depth': '1'}.items()
#     )
#     return [foxglove_bridge]


def generate_launch_description() -> LaunchDescription:
    args = lu.ArgumentContainer()
    args.add_arg('container_name', NVBLOX_CONTAINER_NAME)

    args.add_opaque_function(add_realsense)
    args.add_opaque_function(add_visual_slam)
    args.add_opaque_function(add_nvblox)
    args.add_opaque_function(add_nvblox_navigation)  # separate processes
    args.add_opaque_function(add_ekf)                # separate process
    # args.add_opaque_function(add_foxglove_bridge)

    return LaunchDescription(args.get_launch_actions())