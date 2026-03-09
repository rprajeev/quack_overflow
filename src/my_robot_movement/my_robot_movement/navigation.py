#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, Float32


class LidarCameraNavigator(Node):
    def __init__(self):
        super().__init__('lidar_camera_navigator')

        # Publisher: robot velocity
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscribers
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10
        )
        self.cam_ok_sub = self.create_subscription(
            Bool, '/camera_target_ok', self.camera_ok_callback, 10
        )
        self.cam_err_sub = self.create_subscription(
            Float32, '/camera_heading_error', self.camera_err_callback, 10
        )

        # Internal state
        self.camera_ok = False
        self.camera_heading_error = 0.0      # >0 = target to right, <0 = left
        self.min_front = float('inf')        # closest obstacle in front cone

        # Parameters
        self.safe_distance = 0.40            # meters; stop if obstacle closer
        self.slow_distance = 0.70            # start slowing down
        self.max_speed = 0.25                # m/s forward
        self.turn_gain = 0.01                # camera error -> angular speed

        # Control loop at 10 Hz
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('LidarCameraNavigator started.')

    # --------- Callbacks ---------
    def camera_ok_callback(self, msg: Bool):
        self.camera_ok = msg.data

    def camera_err_callback(self, msg: Float32):
        self.camera_heading_error = msg.data

    def scan_callback(self, msg: LaserScan):
        # Look ±25° in front of robot for safety
        front_min = float('inf')
        angle = msg.angle_min

        for r in msg.ranges:
            if -math.radians(25) <= angle <= math.radians(25):
                if msg.range_min < r < msg.range_max:
                    front_min = min(front_min, r)
            angle += msg.angle_increment

        self.min_front = front_min

    # --------- Main control loop ---------
    def control_loop(self):
        cmd = Twist()

        # 1) LIDAR SAFETY CHECK
        if self.min_front < self.safe_distance:
            # Too close: back up and turn away
            self.get_logger().warn(
                f'Obstacle at {self.min_front:.2f} m: backing up.'
            )
            cmd.linear.x = -0.05
            cmd.angular.z = 0.5
        else:
            # 2) PATH FOLLOWING WHEN LIDAR IS CLEAR
            if self.camera_ok:
                # Forward speed depends on how close obstacle is
                if self.min_front < self.slow_distance:
                    speed = 0.10
                else:
                    speed = self.max_speed

                cmd.linear.x = speed

                # Turn according to camera heading error
                # (Example: error in pixels or degrees)
                cmd.angular.z = -self.turn_gain * self.camera_heading_error
            else:
                # Camera has no good target: stop and slowly turn
                cmd.linear.x = 0.0
                cmd.angular.z = 0.2

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = LidarCameraNavigator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
