#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

import time
import RPi.GPIO as GPIO
from adafruit_vl53l0x  import VL53L0X  # Gadgetoid library [web:10]

# UPDATE THESE: GPIOs for each sensor XSHUT (BCM numbering)
XSHUT_PINS = [17, 27, 22]

# New I2C addresses for each sensor
SENSOR_ADDRS = [0x30, 0x31, 0x32]

DEFAULT_ADDR = 0x29  # factory default

class VL53L0XTripleNode(Node):
    def __init__(self):
        super().__init__('vl53l0x_triple_node')

        self.publishers = [
            self.create_publisher(Int32, 'vl53l0x/sensor1', 10),
            self.create_publisher(Int32, 'vl53l0x/sensor2', 10),
            self.create_publisher(Int32, 'vl53l0x/sensor3', 10),
        ]
        self.sensors = []

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in XSHUT_PINS:
            GPIO.setup(pin, GPIO.OUT)

        # Ensure all sensors are off
        for pin in XSHUT_PINS:
            GPIO.output(pin, GPIO.LOW)
        time.sleep(0.01)

        # Bring up sensors one by one and assign addresses
        for idx, pin in enumerate(XSHUT_PINS):
            addr = SENSOR_ADDRS[idx]

            # Enable this sensor only
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.05)

            try:
                # First connect at default address
                sensor = VL53L0X(address=DEFAULT_ADDR)
                # Change I2C address
                sensor.change_address(addr)
                # Recreate object at new address
                sensor = VL53L0X(address=addr)
                sensor.start_ranging(VL53L0X.BEST_ACCURACY_MODE)
                self.sensors.append(sensor)
                self.get_logger().info(
                    f'Sensor {idx+1} initialized at address 0x{addr:02X}'
                )
            except Exception as e:
                self.get_logger().error(
                    f'Failed to init sensor {idx+1} on pin {pin}: {e}'
                )
                self.sensors.append(None)

        # Start timer for readings
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        for idx, sensor in enumerate(self.sensors):
            if sensor is None:
                continue
            try:
                distance_mm = sensor.get_distance()
            except Exception as e:
                self.get_logger().error(
                    f'Read error sensor {idx+1}: {e}'
                )
                continue

            msg = Int32()
            msg.data = int(distance_mm)
            self.publishers[idx].publish(msg)
            self.get_logger().info(
                f'S{idx+1} (0x{SENSOR_ADDRS[idx]:02X}): {distance_mm} mm'
            )

    def destroy_node(self):
        for sensor in self.sensors:
            if sensor is not None:
                try:
                    sensor.stop_ranging()
                except Exception:
                    pass
        GPIO.cleanup()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VL53L0XTripleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
