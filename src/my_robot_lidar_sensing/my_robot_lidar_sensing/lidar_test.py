#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import serial
import time

class SerialLidarTest(Node):
    def __init__(self):
        super().__init__('serial_lidar_test')

        # CHANGE THIS if your device is different
        port = '/dev/ttyUSB0'
        baud = 115200  # common start value; we can try others later

        self.get_logger().info(f'Trying to open {port} at {baud} baud...')

        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=0.5
            )
        except Exception as e:
            self.get_logger().error(f'Failed to open serial port: {e}')
            self.ser = None

        if self.ser is not None:
            self.get_logger().info('Serial port opened successfully.')
            # Create a timer that fires every 0.1 seconds
            self.timer = self.create_timer(0.1, self.read_serial)
        else:
            self.get_logger().error('Serial port is not available. Node will not read data.')

    def read_serial(self):
        if self.ser is None:
            return

        try:
            # Read up to 256 bytes from the lidar
            data = self.ser.read(256)
            if data:
                # Print as hex so you can see patterns even if not ASCII
                hex_string = ' '.join(f'{b:02X}' for b in data)
                self.get_logger().info(f'Received {len(data)} bytes: {hex_string}')
        except Exception as e:
            self.get_logger().error(f'Error reading from serial: {e}')
            # Wait a bit before trying again
            time.sleep(0.5)

def main(args=None):
    rclpy.init(args=args)
    node = SerialLidarTest()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    if getattr(node, 'ser', None) is not None:
        node.ser.close()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
