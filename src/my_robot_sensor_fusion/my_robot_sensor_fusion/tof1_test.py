#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import board
import busio
import time
import RPi.GPIO as GPIO
from adafruit_vl53l0x  import VL53L0X  # from Gadgetoid/VL53L0X-python [web:10]

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)  # Initialize sensor on default I2C address
# UPDATE THIS: GPIO connected to the single sensor's XSHUT pin
XSHUT_PIN = 11         # BCM numbering
SENSOR_I2C_ADDR = 0x29  # default address; no need to change for 1 sensor

class VL53L0XSingleNode(Node):
    def __init__(self):
        self.sensor = VL53L0X(i2c, address=SENSOR_I2C_ADDR)  # Initialize sensor
        super().__init__('vl53l0x_single_node')
        self.publisher_ = self.create_publisher(Int32, 'vl53l0x/range', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Setup GPIO and sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(XSHUT_PIN, GPIO.OUT)

        # Reset sensor
        GPIO.output(XSHUT_PIN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(XSHUT_PIN, GPIO.HIGH)
        time.sleep(0.05)

        # Initialize sensor
        try:
            self.sensor = VL53L0X(address=SENSOR_I2C_ADDR)
            self.sensor.start_ranging(VL53L0X.BEST_ACCURACY_MODE)
            self.get_logger().info('VL53L0X single sensor initialized')
        except Exception as e:
            self.get_logger().error(f'Failed to init VL53L0X: {e}')
            self.sensor = None

   def timer_callback(self):
    if self.sensor is None:
        return
    
    try:
        distance_mm = self.sensor.range  # This goes HERE - Adafruit driver property [web:1][web:5]
    except Exception as e:
        self.get_logger().error(f'Read error: {e}')
        return
    
    msg = Int32()
    msg.data = int(distance_mm)
    self.publisher_.publish(msg)
    self.get_logger().info(f'Distance: {distance_mm} mm')


    def destroy_node(self):
        if getattr(self, 'sensor', None) is not None:
            try:
                self.sensor.stop_ranging()
            except Exception:
                pass
        GPIO.cleanup()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VL53L0XSingleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
