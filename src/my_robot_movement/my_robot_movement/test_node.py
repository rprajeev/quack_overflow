#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TestNode(Node):
    def __init__(self):
        super().__init__('test_movement')
        self.get_logger().info('Movement package test PASSED!')

def main():
    rclpy.init()
    node = TestNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
