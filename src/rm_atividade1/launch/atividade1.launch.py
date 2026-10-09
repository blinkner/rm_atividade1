from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    share = FindPackageShare('rm_atividade1')
    mode = LaunchConfiguration('mode')

    return LaunchDescription([
        DeclareLaunchArgument('mode', default_value='manual', choices=['manual', 'auto']),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument('rviz', default_value='true'),

        # Inclui a simulação do robô
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([FindPackageShare('rm_bot_sim'), 'launch', 'rm_bot.launch.py'])
            ),
            launch_arguments={
                'world': PathJoinSubstitution([share, 'worlds', 'world_without_obs.sdf']),
                'rviz_config': PathJoinSubstitution([share, 'rviz', 'aula04.rviz']),
                'headless': LaunchConfiguration('headless'),
                'rviz': LaunchConfiguration('rviz')
            }.items()
        ),

        # Nó portão de comandos
        Node(
            package='rm_atividade1',
            executable='command_gate',
            parameters=[{'mode': mode}],
            output='screen'
        ),

        # Nó antigo de navegação (caso ainda queira usar em modo auto)
        Node(
            package='rm_atividade1',
            executable='navigator',
            parameters=[PathJoinSubstitution([share, 'config', 'navigation.yaml'])],
            output='screen',
            condition=IfCondition(PythonExpression(["'", mode, "' == 'auto'"]))
        ),
    ])