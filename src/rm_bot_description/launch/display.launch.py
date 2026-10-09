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
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_gui = LaunchConfiguration('use_gui')
    xacro_file = PathJoinSubstitution(
        [FindPackageShare('rm_bot_description'), 'urdf', 'rm_bot.urdf.xacro'])
    rviz_file = PathJoinSubstitution(
        [FindPackageShare('rm_bot_description'), 'rviz', 'rm_bot.rviz'])
    robot_description = {
        'robot_description': Command([
            FindExecutable(name='xacro'), ' ', xacro_file])}

    return LaunchDescription([
        DeclareLaunchArgument('use_gui', default_value='true'),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             output='screen', parameters=[robot_description]),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui',
             condition=__import__('launch').conditions.IfCondition(use_gui)),
        Node(package='rviz2', executable='rviz2', output='screen', arguments=['-d', rviz_file]),
    ])
