cmake_minimum_required(VERSION 3.0.2)
project(robot_info)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  robotinfo_msgs
)

# installs the Python package in src/robot_info (display, sprites, renderer, ...)
catkin_python_setup()

catkin_package(
  CATKIN_DEPENDS rospy std_msgs robotinfo_msgs
)

catkin_install_python(PROGRAMS
  scripts/info_user_node.py
  scripts/game_node.py
  scripts/control_node.py
  scripts/result_game_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
