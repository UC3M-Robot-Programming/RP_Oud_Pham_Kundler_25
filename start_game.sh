#!/usr/bin/env bash
# Shadow Detective - starts EVERYTHING with one command (Ubuntu 20.04, ROS1 Noetic + ROS2 Foxy):
#
#   ./start_game.sh                  (detective colour: PLAYER_COLOR=1 ./start_game.sh for red)
#
# Opens 5 terminal windows - one for every node - and the game window:
#   1_game_node                ROS1  log of the game, opens the game window
#   2_info_user_node           ROS1  type full name, username, age and difficulty here
#   3_control_node_PLAY_HERE   ROS1  keep this window selected and play with the arrow keys
#   4_result_game_node         ROS1  shows the final result with the percentage
#   5_robot_info2_node         ROS2  receives /keyboard_control through ros1_bridge
# This terminal runs roscore (via roslaunch) and ros1_bridge.
#
# Closing the game window (or X on the final screen) stops everything. Ctrl+C here does too.
#
# Both workspaces must be built first (see README.md):
#   ros1_ws: source /opt/ros/noetic/setup.bash && cd ros1_ws && catkin_make
#   ros2_ws: source /opt/ros/foxy/setup.bash   && cd ros2_ws && colcon build
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS1_WS="${ROS1_WS:-$HERE/ros1_ws}"
ROS2_WS="${ROS2_WS:-$HERE/ros2_ws}"
BRIDGE_WS="${BRIDGE_WS:-$HOME/bridge_ws}"
PLAYER_COLOR="${PLAYER_COLOR:-2}"
NOETIC_SETUP="${NOETIC_SETUP:-/opt/ros/noetic/setup.bash}"
FOXY_SETUP="${FOXY_SETUP:-/opt/ros/foxy/setup.bash}"
TERM_CMD="xterm -fa Monospace -fs 10"

# ---------------------------------------------------------------- checks
fail() { echo "ERROR: $1"; exit 1; }
[ -f "$NOETIC_SETUP" ] || fail "ROS1 Noetic not found ($NOETIC_SETUP)."
[ -f "$FOXY_SETUP" ] || fail "ROS2 Foxy not found ($FOXY_SETUP)."
command -v xterm >/dev/null 2>&1 || fail "xterm is missing: sudo apt install xterm"
[ -f "$ROS1_WS/devel/setup.bash" ] || fail "ROS1 workspace not built: source $NOETIC_SETUP && cd $ROS1_WS && catkin_make"
[ -f "$ROS2_WS/install/setup.bash" ] || fail "ROS2 workspace not built: source $FOXY_SETUP && cd $ROS2_WS && colcon build"
[ -n "${DISPLAY:-}" ] || fail "No graphical desktop (DISPLAY is empty) - start this from a terminal on the Ubuntu desktop."

export ROS_MASTER_URI="${ROS_MASTER_URI:-http://localhost:11311}"
PIDS=()
cleanup() {
  trap - EXIT INT TERM
  echo
  echo "Stopping all nodes, the bridge and roscore ..."
  # ask nicely first (like Ctrl+C), then TERM, then KILL - so this never hangs
  for signal in INT TERM KILL; do
    alive=0
    for pid in ${PIDS[@]+"${PIDS[@]}"}; do
      if kill -0 "$pid" 2>/dev/null; then kill "-$signal" "$pid" 2>/dev/null; alive=1; fi
    done
    [ "$alive" = 0 ] && break
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      still=0
      for pid in ${PIDS[@]+"${PIDS[@]}"}; do kill -0 "$pid" 2>/dev/null && still=1; done
      [ "$still" = 0 ] && break
      sleep 0.5
    done
  done
  echo "Done."
}
trap cleanup EXIT INT TERM

# ---------------------------------------------------------------- 1. ROS1: roscore + windows 1-4
echo "Starting roscore and the four ROS1 nodes (windows 1-4) ..."
( source "$NOETIC_SETUP"
  source "$ROS1_WS/devel/setup.bash"
  exec roslaunch robot_info robot_info.launch player_color:="$PLAYER_COLOR" ) &
ROSLAUNCH_PID=$!
PIDS+=("$ROSLAUNCH_PID")

# wait until roscore answers
( source "$NOETIC_SETUP"
  for _ in $(seq 1 30); do rosnode list >/dev/null 2>&1 && exit 0; sleep 1; done
  exit 1 ) || fail "roscore did not start."

# ---------------------------------------------------------------- 2. ros1_bridge (this terminal)
echo "Starting ros1_bridge ..."
( ROS1_WS="$ROS1_WS" ROS2_WS="$ROS2_WS" BRIDGE_WS="$BRIDGE_WS" exec "$ROS2_WS/start_bridge.sh" ) &
PIDS+=($!)

# ---------------------------------------------------------------- 3. ROS2: window 5
echo "Starting the ROS2 node (window 5) ..."
$TERM_CMD -T 5_robot_info2_node -geometry 92x16-0+420 -e bash -c "
  source '$FOXY_SETUP'
  source '$ROS2_WS/install/setup.bash'
  ros2 run robot_info2 robot_info2_node
  echo; read -p 'robot_info2_node stopped - press ENTER to close this window'" &
PIDS+=($!)

echo
echo "================================================================"
echo " Shadow Detective is running:"
echo "   window 2_info_user_node:         type your data + difficulty"
echo "   window 3_control_node_PLAY_HERE: click into it, then play"
echo " Close the game window (or press X on the final screen) to stop."
echo "================================================================"
echo

# roslaunch ends when game_node ends (required="true"), then cleanup stops the rest
wait "$ROSLAUNCH_PID"
