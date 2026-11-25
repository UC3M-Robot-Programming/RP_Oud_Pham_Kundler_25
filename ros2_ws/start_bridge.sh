#!/usr/bin/env bash
# Starts ros1_bridge (dynamic_bridge) between ROS1 Noetic and ROS2 Foxy.
# Normally started by ../start_game.sh. roscore must already be running.
#
#   ./start_bridge.sh
#
# Workspace locations can be changed: ROS1_WS=/path/to/ros1_ws ./start_bridge.sh
set -e
# default: the two workspaces next to each other in ros_final_work
ROS2_WS="${ROS2_WS:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
ROS1_WS="${ROS1_WS:-$(cd "$ROS2_WS/../ros1_ws" && pwd)}"
BRIDGE_WS="${BRIDGE_WS:-$HOME/bridge_ws}"
export ROS_MASTER_URI="${ROS_MASTER_URI:-http://localhost:11311}"

source /opt/ros/noetic/setup.bash
if [ -f "$ROS1_WS/devel/setup.bash" ]; then source "$ROS1_WS/devel/setup.bash"; fi
source /opt/ros/foxy/setup.bash
if [ -f "$ROS2_WS/install/local_setup.bash" ]; then source "$ROS2_WS/install/local_setup.bash"; fi

if [ -f "$BRIDGE_WS/install/local_setup.bash" ]; then
  source "$BRIDGE_WS/install/local_setup.bash"
  echo "Using ros1_bridge built from source ($BRIDGE_WS) - custom messages and services are bridged too (EXTRA)."
else
  echo "Using ros1_bridge from the binary install - std_msgs such as /keyboard_control are bridged."
fi

# --bridge-all-topics: bridge every ROS1 topic to ROS2 right away, even before a ROS2
# subscriber exists - needed so "ros2 bag record /keyboard_control" can find the topic.
exec ros2 run ros1_bridge dynamic_bridge --bridge-all-topics
