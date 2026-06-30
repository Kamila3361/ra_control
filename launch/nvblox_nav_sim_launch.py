from typing import List
from launch import Action, LaunchDescription
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import Node
import isaac_ros_launch_utils as lu
from nvblox_ros_python_utils.nvblox_launch_utils import NvbloxMode, NvbloxCamera
from nvblox_ros_python_utils.nvblox_constants import NVBLOX_CONTAINER_NAME
import isaac_ros_launch_utils.all_types as lut

def add_ekf(args: lu.ArgumentContainer) -> List[Action]:
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_local_node',
        output='screen',
        parameters=['/home/admin/config/ekf.yaml', {'use_sim_time': True}]
    )
    return [ekf_node]

def add_visual_slam(args: lu.ArgumentContainer) -> List[Action]:
    visual_slam_node = ComposableNode(
        name='visual_slam_node',
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'enable_image_denoising':  False,
            'rectified_images':        True,
            'enable_imu_fusion':       False,
            'base_frame':              'base_link',
            'enable_slam_visualization': False,
            'enable_landmarks_view':   False,
            'enable_observations_view': False,
            'use_sim_time':            True,
            'publish_map_to_odom_tf':  False,
            'publish_odom_to_base_tf': False,
        }],
        remappings=[
            ('visual_slam/image_0',        'camera/infra1/image_rect_raw'),
            ('visual_slam/camera_info_0',  'camera/infra1/camera_info'),
            ('visual_slam/image_1',        'camera/infra2/image_rect_raw'),
            ('visual_slam/camera_info_1',  'camera/infra2/camera_info'),
        ],
    )

    actions = []
    actions.append(lu.component_container('visual_slam_launch_container'))
    actions.append(lu.load_composable_nodes('visual_slam_launch_container', [visual_slam_node]))
    return actions

# def add_nvblox_navigation(args: lu.ArgumentContainer) -> List[Action]:
#     # Nav2 base parameter file
#     actions = []
#     # nav_params_path = lu.get_path('nvblox_examples_bringup', 'config/navigation/carter_nav2.yaml')
#     nav_params_path = '/home/admin/config/nav.yaml'
#     actions.append(lut.SetParametersFromFile(str(nav_params_path)))
#     actions.append(lut.SetParameter('use_sim_time', True))

#     # Running carter navigation
#     actions.append(
#         lu.include(
#             'nav2_bringup',
#             'launch/navigation_launch.py',
#             launch_arguments={
#                 'params_file': str(nav_params_path),
#                 # 'container_name': args.container_name,
#                 'use_composition': 'False',
#                 'use_sim_time': 'True',
#             },
#         ))
#     actions.append(
#         Node(
#             package='tf2_ros',
#             executable='static_transform_publisher',
#             name='map_to_odom_static_tf',
#             arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
#             parameters=[{'use_sim_time': True}],
#             output='screen',
#         )
#     )

#     return actions


def add_nvblox(args: lu.ArgumentContainer) -> List[Action]:
    mode = NvbloxMode[args.mode]
    camera = NvbloxCamera[args.camera]

    base_config = lu.get_path('nvblox_examples_bringup', 'config/nvblox/nvblox_base.yaml')
    # isaac_sim_config = lu.get_path(
    #     'nvblox_examples_bringup',
    #     'config/nvblox/specializations/nvblox_sim.yaml'
    # )
    isaac_sim_config = '/home/admin/config/nv.yaml'

    remappings = [

        ('camera_0/depth/image',       '/depth/ground_truth'),
        ('camera_0/depth/camera_info', '/depth/camera_info'),
        ('camera_0/color/image',       '/rgb/image_rect_raw'),
        ('camera_0/color/camera_info', '/rgb/camera_info'),
    ]

    parameters = [
        base_config,
        {},  # mode_config placeholder
        isaac_sim_config,
        {'num_cameras': 1},
        {'use_lidar': False},
    ]

    nvblox_node = ComposableNode(
        name='nvblox_node',
        package='nvblox_ros',
        plugin='nvblox::NvbloxNode',
        remappings=remappings,
        parameters=parameters,
    )

    actions = []
    actions.append(lu.component_container(args.container_name))
    actions.append(lu.load_composable_nodes(args.container_name, [nvblox_node]))
    actions.append(lu.log_info([
        "Starting nvblox with the '", str(camera),
        "' camera in '", str(mode), "' mode."
    ]))

    actions.append(
        lu.include(
            'nvblox_examples_bringup',
            'launch/visualization/visualization.launch.py',
            launch_arguments={
                'mode': args.mode,
                'camera': NvbloxCamera.isaac_sim,
            }))

    return actions


def generate_launch_description() -> LaunchDescription:
    args = lu.ArgumentContainer()
    args.add_arg('mode', NvbloxMode.static)
    args.add_arg('camera', NvbloxCamera.isaac_sim)
    args.add_arg('container_name', NVBLOX_CONTAINER_NAME)
    # args.add_arg('container_name', 'visual_slam_launch_container')
    # args.add_opaque_function(add_nvblox_navigation)
    args.add_opaque_function(add_nvblox)
    args.add_opaque_function(add_visual_slam)
    args.add_opaque_function(add_ekf)
    return LaunchDescription(args.get_launch_actions())