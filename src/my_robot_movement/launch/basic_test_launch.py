from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_robot_movement',
            executable='test_node',
            name='movement_test'
        ),
    ])
