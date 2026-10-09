# Copyright 2026 rm_bot contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PythonExpression, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_rviz = LaunchConfiguration('rviz')
    world = LaunchConfiguration('world')
    xacro_file = PathJoinSubstitution([
        FindPackageShare('rm_bot_description'), 'urdf', 'rm_bot.urdf.xacro'])
    rviz_file = LaunchConfiguration('rviz_config')
    description = Command([FindExecutable(name='xacro'), ' ', xacro_file])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution(
            [FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])),
        launch_arguments={'gz_args': [PythonExpression(["'-r -s --headless-rendering -v 3 ' if '", LaunchConfiguration('headless'), "' == 'true' else '-r -v 3 '"]), world], 'on_exit_shutdown': 'true'}.items())

    spawn = Node(package='ros_gz_sim', executable='create', output='screen',
                 arguments=['-name', 'rm_bot', '-topic', 'robot_description',
                            '-x', '0', '-y', '0', '-z', '0.001'])

    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge', output='screen',
                  arguments=[
                      '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                      '/ultrasonic/front/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                      '/ultrasonic/right/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                      '/ultrasonic/left/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                      '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                      '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                      '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                      '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                      '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
                  ],
                  remappings=[('/tf', '/tf')])

    return LaunchDescription([
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', PathJoinSubstitution([FindPackageShare('rm_bot_description'), '..'])),
        DeclareLaunchArgument('world', default_value=PathJoinSubstitution([FindPackageShare('rm_bot_sim'), 'worlds', 'classroom.sdf'])),
        DeclareLaunchArgument('rviz_config', default_value=PathJoinSubstitution([FindPackageShare('rm_bot_description'), 'rviz', 'rm_bot.rviz'])),
        DeclareLaunchArgument('headless', default_value='false', description='Executar sem interface gráfica'),
        DeclareLaunchArgument('rviz', default_value='true', description='Abrir RViz2'),
        gazebo,
        Node(package='robot_state_publisher', executable='robot_state_publisher', output='screen',
             parameters=[{'robot_description': description, 'use_sim_time': True}]),
        bridge,
        TimerAction(period=2.0, actions=[spawn]),
        Node(package='rviz2', executable='rviz2', output='screen', arguments=['-d', rviz_file],
             parameters=[{'use_sim_time': True}],
             condition=__import__('launch').conditions.IfCondition(use_rviz)),
    ])
