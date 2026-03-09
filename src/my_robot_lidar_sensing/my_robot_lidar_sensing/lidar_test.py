#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import serial
import time

class SerialLidarTest(Node):
    def __init__(self):
        super().__init__('serial_lidar_test')

        # Change to /dev/serial0 for Pi GPIO pins
        port = '/dev/serial0'
        baud = 115200 

        self.get_logger().info(f'Trying to open {port} at {baud} baud...')

        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=0.5
            )
            
            if self.ser.is_open:
                self.get_logger().info('Serial port opened successfully.')
                # Send the start command to the LiDAR
                self.start_lidar()
                # Create a timer that fires every 0.1 seconds
                self.timer = self.create_timer(0.1, self.read_serial)
                
        except Exception as e:
            self.get_logger().error(f'Failed to open serial port: {e}')
            self.ser = None

    def start_lidar(self):
        """Sends the initialization bytes to wake up the sensor."""
        try:
            self.get_logger().info('Sending start command to LiDAR...')
            # 0x80 (128) is the standard 'Start' for Roomba/Create OI
            # Some LiDARs (like RPLidar) use b'\xa5\x20'
            start_cmd = bytes([0x80]) 
            self.ser.write(start_cmd)
            
            # Small delay to let the motor start spinning
            time.sleep(0.5) 
            
            # Optional: Some sensors need a second byte (like 0x07 or 0x83) 
            # to enter a specific scanning mode.
            # self.ser.write(bytes([0x83])) 
            
            self.get_logger().info('Start command sent.')
        except Exception as e:
            self.get_logger().error(f'Failed to send start command: {e}')

    def read_serial(self):
        if self.ser is None or not self.ser.is_open:
            return

        try:
            # Read whatever is in the buffer
            data = self.ser.read(self.ser.in_waiting or 1)
            if data:
                hex_string = ' '.join(f'{b:02X}' for b in data)
                self.get_logger().info(f'Received {len(data)} bytes: {hex_string}')
        except Exception as e:
            self.get_logger().error(f'Error reading from serial: {e}')
            time.sleep(0.5)

def main(args=None):
    rclpy.init(args=args)
    node = SerialLidarTest()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.ser is not None and node.ser.is_open:
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
