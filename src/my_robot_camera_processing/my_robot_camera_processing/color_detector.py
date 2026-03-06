#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np

class CompetitionColorDetector(Node):
    def __init__(self):
        super().__init__('competition_color_detector')
        self.bridge = CvBridge()
        self.color_pub = self.create_publisher(String, '/led_color', 10)
        self.sub = self.create_subscription(
            Image, '/image_raw', self.image_callback, 10)
        self.get_logger().info('🚀 SOUTHEASTCON COMPETITION: Arducam LED Detector READY')
        self.last_color = None

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            
            # Arducam color correction for competition LEDs
            cv_image = cv2.convertScaleAbs(cv_image, alpha=1.2, beta=15)
            
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Competition LED ranges (tested for bright LEDs)
            red1_lower = np.array([0, 120, 100])
            red1_upper = np.array([10, 255, 255])
            red2_lower = np.array([170, 120, 100])
            red2_upper = np.array([180, 255, 255])
            
            green_lower = np.array([45, 120, 100])
            green_upper = np.array([75, 255, 255])
            
            blue_lower = np.array([100, 120, 100])
            blue_upper = np.array([130, 255, 255])
            
            red_mask1 = cv2.inRange(hsv, red1_lower, red1_upper)
            red_mask2 = cv2.inRange(hsv, red2_lower, red2_upper)
            red_mask = red_mask1 + red_mask2
            
            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            
            # Competition threshold (adjust if needed)
            pixel_count = 2000  # Minimum pixels for detection
            
            if cv2.countNonZero(red_mask) > pixel_count:
                color = "RED"
            elif cv2.countNonZero(green_mask) > pixel_count:
                color = "GREEN"
            elif cv2.countNonZero(blue_mask) > pixel_count:
                color = "BLUE"
            else:
                return
            
            if color != self.last_color:
                self.last_color = color
                msg = String()
                msg.data = f"ANTENNA_LED:{color}"
                self.color_pub.publish(msg)
                self.get_logger().info(f'🎯 DETECTED: {color} LED! Published to /led_color')
                
        except Exception as e:
            self.get_logger().warn(f'Camera error: {str(e)}')

def main():
    rclpy.init()
    node = CompetitionColorDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
