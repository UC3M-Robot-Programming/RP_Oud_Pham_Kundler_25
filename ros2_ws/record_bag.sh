#!/usr/bin/env bash
# Records the commands of control_node on /keyboard_control from the ROS2 side.
# The game, control_node and the bridge (./start_bridge.sh) must be running.
# Stop the recording with Ctrl+C.
#
#   ./record_bag.sh
#
# Result: the folder robot_info2.bag/ (metadata.yaml + robot_info2.bag_0.db3) next to this script.
set -e
source /opt/ros/foxy/setup.bash
cd "$(dirname "$0")"
if [ -e robot_info2.bag ]; then
  echo "robot_info2.bag already exists here - rename or delete it first (ros2 bag will not overwrite it)."
  exit 1
fi
echo "Recording /keyboard_control into robot_info2.bag - play the game now, Ctrl+C to stop."
ros2 bag record -o robot_info2.bag /keyboard_control
