#!/bin/bash

set -e

WORKSPACE=~/quack_overflow
PACKAGE=my_robot_sensor_fusion
NODE=tof1_test

echo "---- Enter workspace ----"
cd $WORKSPACE

echo "---- Git pull ----"
git pull

echo "---- Remove old ROS2 build artifacts ----"
rm -rf build install log

echo "---- Source ROS2 ----"
source /opt/ros/humble/setup.bash

echo "---- Build workspace ----"
colcon build --symlink-install

echo "---- Source workspace ----"
source install/setup.bash

echo "---- Run node ----"
ros2 run $PACKAGE $NODE