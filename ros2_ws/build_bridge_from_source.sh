#!/usr/bin/env bash
# EXTRA: builds ros1_bridge from source so it also bridges the custom message and services
# (ROS1 robotinfo_msgs <-> ROS2 robot_info_msgs, see robot_info_msgs/mapping_rules.yaml).
#
# Before running this script:
#   1. ROS1 workspace built:  (new terminal) source /opt/ros/noetic/setup.bash; cd ros_final_work/ros1_ws; catkin_make
#   2. ROS2 workspace built:  (new terminal) source /opt/ros/foxy/setup.bash;   cd ros_final_work/ros2_ws; colcon build
# Then, in a NEW terminal:    ./build_bridge_from_source.sh
# Building ros1_bridge takes a while (10-30 minutes) and needs a few GB of RAM.
set -e
# default: the two workspaces next to each other in ros_final_work
ROS2_WS="${ROS2_WS:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
ROS1_WS="${ROS1_WS:-$(cd "$ROS2_WS/../ros1_ws" && pwd)}"
BRIDGE_WS="${BRIDGE_WS:-$HOME/bridge_ws}"

mkdir -p "$BRIDGE_WS/src"
if [ ! -d "$BRIDGE_WS/src/ros1_bridge" ]; then
  git clone -b foxy https://github.com/ros2/ros1_bridge.git "$BRIDGE_WS/src/ros1_bridge"
fi

# order from the ros1_bridge documentation: ROS1 environment first, then ROS2
source /opt/ros/noetic/setup.bash
source "$ROS1_WS/devel/setup.bash"
source /opt/ros/foxy/setup.bash
source "$ROS2_WS/install/local_setup.bash"

cd "$BRIDGE_WS"
colcon build --symlink-install --packages-select ros1_bridge --cmake-force-configure

source "$BRIDGE_WS/install/local_setup.bash"
echo
echo "Pairs for our packages (should list GameUserMsg, GetUserScore and SetGameDifficulty):"
ros2 run ros1_bridge dynamic_bridge --print-pairs | grep -i robot || {
  echo "No robot_info_msgs pairs found - check that both workspaces were built and sourced."
  exit 1
}
