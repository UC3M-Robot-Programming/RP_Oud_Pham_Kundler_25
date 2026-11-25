# Shadow Detective – ROS Final Work (Part I + Part II)

**Robot Programming – Final Assignment.** Everything for the final submission is located in `<project_root>/`.

Shadow Detective is a detective game controlled through **ROS1** nodes (Parts I and II) and connected to **ROS2** through `ros1_bridge` (Part II). ROS1 and ROS2 are built in two separate workspaces because `catkin` (ROS1) and `colcon` (ROS2) cannot build the same workspace.

---

## 1. Repository Structure

| Folder / File | Content | Documentation |
|---|---|---|
| [`ros1_ws/`](ros1_ws) | **ROS1 (Noetic)**, catkin workspace.<br>**Part I:** nodes `info_user_node`, `game_node`, `control_node`, `result_game_node`; topics `/user_information` (custom `GameUserMsg`), `/keyboard_control`, `/result_information`.<br>**Part II:** services `/user_score` and `/difficulty`, parameters `user_name`, `change_player_color`, `screen_param`, launcher `robot_info.launch` | [`ros1_ws/README.md`](ros1_ws/README.md) |
| [`ros2_ws/`](ros2_ws) | **ROS2 (Foxy)**, colcon workspace.<br>**Part II:** `ros1_bridge` for `/keyboard_control`, ROS2 package `robot_info2` with `robot_info2_node.py`, rosbag `robot_info2.bag`.<br>**EXTRA:** `robot_info_msgs` + bridge built from source | [`ros2_ws/README.md`](ros2_ws/README.md) |
| [`start_game.sh`](start_game.sh) | **Starts the entire game (ROS1 + Bridge + ROS2) with one command** | Section 5 |

---

## 2. System Architecture & Communication Flow

```text
                     srv /difficulty (SetGameDifficulty)
            ┌────────────────────────────────────────────────┐
            │                                                ▼
   ┌────────────────┐  /user_information (GameUserMsg)  ┌────────────────────────────────┐
   │ info_user_node │ ────────────────────────────────▶ │           game_node            │
   └────────────────┘ ──────────────┐                   │ phase1 Welcome → 2 Game → 3 Final│
                                    │                   │ params: user_name,             │
   ┌──────────────┐ /keyboard_control (std_msgs/String) │   change_player_color,         │
   │ control_node │ ──────────────────────────────────▶ │   screen_param                 │
   └──────────────┘          │                          │ services: /difficulty,         │
                             │                          │           /user_score          │
                             │                          └────────────────────────────────┘
                             │                             │ /result_information   ▲
                             │                             ▼ (std_msgs/Int64)      │ srv /user_score
                             │                    ┌──────────────────┐             │ (GetUserScore)
                             │                    │ result_game_node │ ────────────┘
                             │                    └──────────────────┘ ◀── /user_information
                             ▼
                  ros1_bridge ──▶ ROS2 robot_info2_node (node: info_ros2_node)
                                        └──▶ ros2 bag record ──▶ robot_info2.bag
```

### ROS Interfaces Overview

- **Topics:**
  - `/user_information` (`robotinfo_msgs/GameUserMsg`, latched): Player's full name, username, and age (`info_user_node` → `game_node`, `result_game_node`).
  - `/keyboard_control` (`std_msgs/String`): Key commands (`UP`, `DOWN`, `LEFT`, `RIGHT`, `INTERACT`, `CONFIRM`, `MENU`, `NOTEBOOK`, `CASE_FILE`, `ACCUSE`, `HELP`, `OPTION_1`..`9`, `EXIT`) sent from `control_node` to `game_node` and bridged to `robot_info2_node` in ROS2.
  - `/result_information` (`std_msgs/Int64`, latched): Final score published by `game_node` to `result_game_node` (and bridged to ROS2).
- **Services (offered by `game_node`):**
  - `/difficulty` (`robotinfo_msgs/SetGameDifficulty`): Sets `"easy"`, `"medium"`, or `"hard"` (accepted in `phase1` only).
  - `/user_score` (`robotinfo_msgs/GetUserScore`): Returns the user's final score as a percentage (`0–100`) of the maximum score (`10080`).
- **Parameters (`/game_node/`):**
  - `/game_node/user_name` (`string`): Player name, set when `/user_information` arrives.
  - `/game_node/change_player_color` (`int`): Detective color (`1` Red, `2` Purple [default], `3` Blue) — updated live.
  - `/game_node/screen_param` (`string`): Current game phase (`phase1`, `phase2`, `phase3`).

---

## 3. Dependencies & Installation (Ubuntu 20.04)

Tested environment: **Ubuntu 20.04** with **Python 3.8**, **ROS1 Noetic**, and **ROS2 Foxy**.

### Complete Dependency List

| Category | Packages / Tools |
|---|---|
| **System & Build Tools** | `curl`, `software-properties-common`, `xterm`, `python3-pip`, `python3-colcon-common-extensions` |
| **Python Libraries** | `pygame>=2` *(must be installed via `pip3`, since the Ubuntu 20.04 apt version 1.9 is too old)* |
| **ROS1 (Noetic)** | `ros-noetic-desktop` |
| **ROS2 (Foxy) & Bridge** | `ros-foxy-ros-base`, `ros-foxy-ros1-bridge`, `ros-foxy-rosbag2`, `ros-foxy-ros2bag`, `ros-foxy-rosbag2-storage-default-plugins` |

> **Important:** Do **not** add both `source /opt/ros/noetic/setup.bash` and `source /opt/ros/foxy/setup.bash` to `~/.bashrc`. The start script sources the exact environment required for each window.
>
> **Note:** ROS1 Noetic and ROS2 Foxy have reached EOL. If `apt` cannot locate the packages, use the ROS snapshot repositories (<http://snapshots.ros.org>) or the provided course virtual machine.

### Step 3.1 – Install ROS1 Noetic & Game Dependencies

```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt update
sudo apt install -y curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo apt update
sudo apt install -y ros-noetic-desktop python3-pip xterm
pip3 install --user "pygame>=2"
```

### Step 3.2 – Install ROS2 Foxy, `ros1_bridge` & `rosbag2`

```bash
sudo apt install -y software-properties-common curl
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install -y \
  ros-foxy-ros-base \
  ros-foxy-ros1-bridge \
  ros-foxy-rosbag2 \
  ros-foxy-ros2bag \
  ros-foxy-rosbag2-storage-default-plugins \
  python3-colcon-common-extensions
```

---

## 4. Build Workspaces

Build each workspace once in a **separate, clean terminal** that only sources its respective ROS distribution.

### Build ROS1 Workspace (Terminal with ROS1 only)

```bash
source /opt/ros/noetic/setup.bash
cd <project_root>/ros1_ws
catkin_make
```

Verify generated custom messages and services:

```bash
source devel/setup.bash
rosmsg show robotinfo_msgs/GameUserMsg
rossrv show robotinfo_msgs/GetUserScore
rossrv show robotinfo_msgs/SetGameDifficulty
```

### Build ROS2 Workspace (Terminal with ROS2 only)

```bash
source /opt/ros/foxy/setup.bash
cd <project_root>/ros2_ws
colcon build
```

*(To build only the ROS2 listener without the EXTRA custom interface package, run `colcon build --packages-select robot_info2`.)*

### Optional EXTRA – Build `ros1_bridge` from Source (Custom Types)

The binary `ros-foxy-ros1-bridge` only supports standard ROS types. To bridge custom messages and services (`GameUserMsg`, `GetUserScore`, `SetGameDifficulty`), run the build script in a **new terminal** after both workspaces above have been built:

```bash
<project_root>/ros2_ws/build_bridge_from_source.sh
```

This builds `ros1_bridge` into `~/bridge_ws` (takes ~10–30 minutes). `start_game.sh` automatically detects and uses `~/bridge_ws` if present. Verify the bridged custom pairs with:

```bash
source /opt/ros/noetic/setup.bash && source <project_root>/ros1_ws/devel/setup.bash
source /opt/ros/foxy/setup.bash && source <project_root>/ros2_ws/install/local_setup.bash
source ~/bridge_ws/install/local_setup.bash
ros2 run ros1_bridge dynamic_bridge --print-pairs | grep -i robot
```

---

## 5. Running the Game

Start the entire system with a single command from `<project_root>/`:

```bash
cd <project_root>
./start_game.sh
```

Optional overrides:

```bash
# Set initial detective color (1 = Red, 2 = Purple, 3 = Blue)
PLAYER_COLOR=1 ./start_game.sh

# Specify custom workspace paths
ROS1_WS=/path/to/ros1_ws ROS2_WS=/path/to/ros2_ws ./start_game.sh
```

The start terminal runs `roscore` (via `ros1_ws/src/robot_info/launch/robot_info.launch`) and `ros1_bridge` (`dynamic_bridge --bridge-all-topics`), and opens **five terminal windows** plus the **Pygame window**:

| Window | Node | Role / Action |
|---|---|---|
| `1_game_node` | `game_node` (ROS1) | Game log; opens the **game window** and provides `/user_score` and `/difficulty` |
| `2_info_user_node` | `info_user_node` (ROS1) | Enter full name, username, age, and difficulty (`easy` / `medium` / `hard`) |
| `3_control_node_PLAY_HERE` | `control_node` (ROS1) | **Click into this window to play** (Arrow keys, `SPACE`, `ENTER`, `ESC`, `N/F/A/H`, `1–9`, `X`) |
| `4_result_game_node` | `result_game_node` (ROS1) | Displays final score and percentage via `/user_score` |
| `5_robot_info2_node` | `robot_info2_node` (ROS2) | Logs incoming `/keyboard_control` commands and final score in ROS2 |

**Stopping:** Close the game window, press `X` on the final screen, or press `Ctrl+C` in the start terminal to cleanly stop all nodes, the bridge, and `roscore`.

---

## 6. Recording & Replaying the ROS2 Bag

While the game is running, open a new terminal to record `/keyboard_control` from ROS2 (stop with `Ctrl+C`):

```bash
cd <project_root>/ros2_ws
./record_bag.sh
```

This creates the bag directory `<project_root>/ros2_ws/robot_info2.bag/`. To inspect or replay the recorded commands:

```bash
source /opt/ros/foxy/setup.bash
cd <project_root>/ros2_ws
ros2 bag info robot_info2.bag
ros2 bag play robot_info2.bag
```

---

## 7. Quick CLI Reference (Services, Parameters & Debugging)

### ROS1 Terminal

```bash
source /opt/ros/noetic/setup.bash
source <project_root>/ros1_ws/devel/setup.bash

# Services
rosservice list
rosservice call /difficulty "change_difficulty: 'hard'"
rosservice call /user_score "username: 'ada_99'"

# Parameters
rosparam list /game_node
rosparam get /game_node/screen_param
rosparam get /game_node/user_name
rosparam set /game_node/change_player_color 1

# Debugging
rosnode list
rostopic list
rostopic echo /keyboard_control
rqt_graph
```

### ROS2 Terminal

```bash
source /opt/ros/foxy/setup.bash

ros2 node list
ros2 topic list
ros2 topic echo /keyboard_control
```

---

## 8. Troubleshooting

| Problem | Solution |
|---|---|
| `ROS1 workspace not built` / `ROS2 workspace not built` | Build both workspaces first (Section 4). |
| `pygame 2.0 or newer is needed` | Run `pip3 install --user "pygame>=2"`. |
| `xterm is missing` | Run `sudo apt install -y xterm`. |
| Detective does not move | Click into window **`3_control_node_PLAY_HERE`**, not the Pygame window. |
| `[rosrun] Couldn't find executable` | Run `chmod +x <project_root>/ros1_ws/src/robot_info/scripts/*.py` and rebuild with `catkin_make`. |
| `robot_info2.bag already exists` | `ros2 bag` does not overwrite; delete or rename the existing folder before recording again. |
| `failed to create 2to1 bridge` for `robotinfo_msgs` | Expected with the binary bridge; build the bridge from source for custom types (Section 4). |

---

## 9. Further Documentation

For a detailed breakdown of setup, node internals, design rules, and troubleshooting instructions, please refer to the respective documentation in the workspace directories:

- **ROS 1 Workspace:** [ros1_ws/README.md](ros1_ws/README.md)
- **ROS 2 Workspace:** [ros2_ws/README.md](ros2_ws/README.md)