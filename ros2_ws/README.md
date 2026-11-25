# Shadow Detective – ROS2 workspace (Part II: ros1_bridge)

The ROS1 game (see [`../ros1_ws/README.md`](../ros1_ws/README.md)) is connected to ROS2 with **ros1_bridge**. In ROS2, the node `robot_info2_node` receives the commands that `control_node` sends on `/keyboard_control`, and a **rosbag** `robot_info2.bag` records them.

| | |
|---|---|
| **ROS2 packages** | `robot_info2` (listener node), `robot_info_msgs` (EXTRA: custom message + services) |
| **ROS2 node** | file `robot_info2/robot_info2_node.py`, executable `robot_info2_node`, node name `info_ros2_node` |
| **Bridged topic (required)** | `/keyboard_control` – `std_msgs/String` |
| **rosbag** | `robot_info2.bag` – records `/keyboard_control` from ROS2 |
| **EXTRA** | `/user_information` (GameUserMsg), `/user_score` and `/difficulty` (services) over a bridge built from source |
| **Versions** | Ubuntu 20.04, ROS1 Noetic + ROS2 Foxy, `ros-foxy-ros1-bridge` (binary) |

---

## 1. How it fits together

```
 ROS1 (Noetic)                                                  ROS2 (Foxy)
┌──────────────┐  /keyboard_control   ┌─────────────┐  /keyboard_control   ┌────────────────────────┐
│ control_node │ ───────────────────▶ │ ros1_bridge │ ───────────────────▶ │ robot_info2_node.py    │
└──────────────┘  std_msgs/String     │  (dynamic_  │  std_msgs/String     │ (node: info_ros2_node) │
┌──────────────┐  /result_information │   bridge)   │ ───────────────────▶ └────────────────────────┘
│  game_node   │ ───────────────────▶ │             │                       ros2 bag record
└──────────────┘  std_msgs/Int64      └─────────────┘                       ──▶ robot_info2.bag
        EXTRA (bridge from source): /user_information (GameUserMsg), /user_score, /difficulty
```

`robot_info2_node` logs every command (`Command #12 from ROS1: LEFT`) and, when the game ends, the final score from `/result_information` together with a summary of all received commands.

---

## 2. Installation (Ubuntu 20.04)

ROS1 Noetic must already be installed (see the ROS1 README). Then install ROS2 Foxy and the bridge from the binary packages:

```bash
sudo apt install software-properties-common curl
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install ros-foxy-ros-base ros-foxy-ros1-bridge ros-foxy-rosbag2 ros-foxy-ros2bag \
                 ros-foxy-rosbag2-storage-default-plugins python3-colcon-common-extensions
```

> Do **not** put `source /opt/ros/foxy/setup.bash` and `source /opt/ros/noetic/setup.bash` together in `~/.bashrc`. Each terminal sources only what it needs (see below).
>
> ROS2 Foxy and ROS1 Noetic have reached their end of life. If `apt` cannot find the packages any more, use the ROS snapshot repositories (<http://snapshots.ros.org>) or the class virtual machine.

## 3. Build the ROS2 workspace

Build in place, inside `ros_final_work/`, in a terminal **with only ROS2**:

```bash
source /opt/ros/foxy/setup.bash
cd ros_final_work/ros2_ws
colcon build
```

`colcon build` builds both packages. Without the EXTRA, build only the listener with `colcon build --packages-select robot_info2`.

---

## 4. Run: everything with one command

The ROS1 workspace must be built too (see the ROS1 README). Then:

```bash
cd ros_final_work
./start_game.sh
```

This opens one terminal window per node (1–4 ROS1, **5 = `robot_info2_node` in ROS2**) and the game window. ros1_bridge runs in the start terminal. The table of all windows is in the ROS1 README, section 6.

What the start script does for the ROS2 side:
- **Bridge:** it runs `ros2_ws/start_bridge.sh`, i.e. `ros2 run ros1_bridge dynamic_bridge --bridge-all-topics` with the ROS1 and ROS2 environments sourced.
- **Window 5:** it sources `/opt/ros/foxy/setup.bash` and `ros2_ws/install/setup.bash`, then runs `ros2 run robot_info2 robot_info2_node`.

**Recording the rosbag** while the game runs, in a new terminal (stop with Ctrl+C):

```bash
cd ros_final_work/ros2_ws
./record_bag.sh
#   same as:  source /opt/ros/foxy/setup.bash && ros2 bag record -o robot_info2.bag /keyboard_control
```

The scripts use the workspaces next to them in `ros_final_work/` (and `~/bridge_ws` for the EXTRA). Other folders can be given like this: `ROS1_WS=/path/ros1_ws ROS2_WS=/path/ros2_ws ./start_game.sh`.

Why `--bridge-all-topics`: without it, the bridge only creates the ROS2 side of a topic once a ROS2 node subscribes to it. With the flag, `/keyboard_control` exists in ROS2 right away, so `ros2 bag record` can always find it.

Check from ROS2 that the commands arrive:

```bash
source /opt/ros/foxy/setup.bash
ros2 topic list                     # /keyboard_control, /result_information, ...
ros2 topic echo /keyboard_control   # data: UP, data: INTERACT, ...
ros2 node list                      # /info_ros2_node
```

## 5. The rosbag `robot_info2.bag`

In ROS2, `ros2 bag record -o robot_info2.bag` creates a **folder** called `robot_info2.bag/` that holds `metadata.yaml` and `robot_info2.bag_0.db3` (SQLite). This folder is the rosbag file of the assignment and belongs in the repository.

```bash
source /opt/ros/foxy/setup.bash
cd ros_final_work/ros2_ws
ros2 bag info robot_info2.bag                 # duration, number of messages on /keyboard_control
ros2 bag play robot_info2.bag                 # replays the commands
# while playing, in another ROS2 terminal:
ros2 topic echo /keyboard_control
```

Replaying with the bridge running even sends the recorded commands back to the ROS1 game, so the detective moves on its own.

---

## 6. EXTRA: custom message and services over the bridge

The binary `ros1_bridge` only knows standard types. To bridge our own types, the package **`robot_info_msgs`** (ROS2) defines the same message and services as `robotinfo_msgs` (ROS1), with identical names and fields:

| ROS1 (`robotinfo_msgs`) | ROS2 (`robot_info_msgs`) | Used on |
|---|---|---|
| `GameUserMsg` | `msg/GameUserMsg` | topic `/user_information` |
| `GetUserScore` | `srv/GetUserScore` | service `/user_score` |
| `SetGameDifficulty` | `srv/SetGameDifficulty` | service `/difficulty` |

Because the package names differ, `robot_info_msgs/mapping_rules.yaml` tells the bridge which packages belong together. `package.xml` exports it, and `CMakeLists.txt` installs it:

```yaml
-
  ros1_package_name: 'robotinfo_msgs'
  ros2_package_name: 'robot_info_msgs'
```

### Build ros1_bridge from source

1. Build the ROS1 workspace in a terminal with only ROS1: `source /opt/ros/noetic/setup.bash; cd ros_final_work/ros1_ws; catkin_make`.
2. Build the ROS2 workspace in a terminal with only ROS2: `source /opt/ros/foxy/setup.bash; cd ros_final_work/ros2_ws; colcon build`.
3. In a **new** terminal, run `ros_final_work/ros2_ws/build_bridge_from_source.sh`. It clones the `foxy` branch of ros1_bridge into `~/bridge_ws`, sources ROS1 → ROS1 ws → ROS2 → ROS2 ws (in this order) and runs `colcon build --packages-select ros1_bridge --cmake-force-configure`. This takes 10–30 minutes.

Check the pairs; all three types must appear:

```bash
source /opt/ros/noetic/setup.bash && source ros_final_work/ros1_ws/devel/setup.bash
source /opt/ros/foxy/setup.bash && source ros_final_work/ros2_ws/install/local_setup.bash
source ~/bridge_ws/install/local_setup.bash
ros2 run ros1_bridge dynamic_bridge --print-pairs | grep -i robot
#   - 'robot_info_msgs/msg/GameUserMsg' (ROS 2) <=> 'robotinfo_msgs/GameUserMsg' (ROS 1)
#   - 'robot_info_msgs/srv/GetUserScore' (ROS 2) <=> 'robotinfo_msgs/GetUserScore' (ROS 1)
#   - 'robot_info_msgs/srv/SetGameDifficulty' (ROS 2) <=> 'robotinfo_msgs/SetGameDifficulty' (ROS 1)
```

`start_game.sh` (through `start_bridge.sh`) automatically uses `~/bridge_ws` if it exists. With this bridge:
- `robot_info2_node` also shows the player from `/user_information`, and after the game it calls the ROS1 service `/user_score` **from ROS2** and logs the percentage.
- The services can be called from ROS2 by hand:

```bash
ros2 service call /difficulty robot_info_msgs/srv/SetGameDifficulty "{change_difficulty: 'easy'}"
ros2 service call /user_score robot_info_msgs/srv/GetUserScore "{username: 'ada_99'}"
ros2 topic echo /user_information
```

---

## 7. Files

```
ros2_ws/
├── README.md
├── start_bridge.sh                 starts dynamic_bridge (used by ../start_game.sh)
├── record_bag.sh                   records /keyboard_control into robot_info2.bag
├── build_bridge_from_source.sh     EXTRA: builds ros1_bridge with robot_info_msgs
├── robot_info2.bag/                the recorded rosbag (created with record_bag.sh)
└── src/
    ├── robot_info2/                ament_python package
    │   ├── robot_info2/
    │   │   ├── __init__.py
    │   │   └── robot_info2_node.py
    │   ├── resource/robot_info2
    │   ├── package.xml
    │   ├── setup.cfg
    │   └── setup.py                entry point robot_info2_node
    └── robot_info_msgs/            EXTRA - ament_cmake interface package
        ├── msg/GameUserMsg.msg
        ├── srv/GetUserScore.srv
        ├── srv/SetGameDifficulty.srv
        ├── mapping_rules.yaml
        ├── CMakeLists.txt
        └── package.xml
```

## 8. Troubleshooting

| Problem | Solution |
|---|---|
| `ros2 topic list` shows no `/keyboard_control` | Is `./start_game.sh` running (it starts roscore and the bridge)? Look for errors in the start terminal. |
| `failed to create 2to1 bridge` / unknown type for `robotinfo_msgs` | Normal with the binary bridge: only std types are bridged. For the EXTRA, build the bridge from source (section 6). |
| `--print-pairs` shows no `robot` pairs | Both workspaces must be built and sourced **before** building the bridge; rebuild with `--cmake-force-configure`. |
| `ros2 bag record` writes nothing | Start `./start_game.sh` first, then the recording, then press keys in window 3_control_node_PLAY_HERE. |
| `robot_info2.bag already exists` | `ros2 bag` does not overwrite; rename or delete the old folder. |
