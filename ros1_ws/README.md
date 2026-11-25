# Shadow Detective – ROS1 workspace (Part I + Part II)

**Robot Programming – Final Assignment**
- Part I: publisher, subscriber and custom message
- Part II: services, parameters and launcher (+ ROS2 bridge, see [`../ros2_ws/README.md`](../ros2_ws/README.md))

Our detective game, controlled through ROS1 nodes. The player types their data in one terminal and steers the detective with the arrow keys in a second terminal. The final score travels through ROS topics and services to a node that announces the result.

| | |
|---|---|
| **Packages** | `robot_info` (nodes, launcher, game code), `robotinfo_msgs` (message + services) |
| **Nodes (ROS1)** | `info_user_node`, `game_node`, `control_node`, `result_game_node` |
| **Topics** | `/user_information`, `/keyboard_control`, `/result_information` |
| **Services** | `/user_score` (`GetUserScore`), `/difficulty` (`SetGameDifficulty`) |
| **Parameters** | `/game_node/user_name`, `/game_node/change_player_color`, `/game_node/screen_param` |
| **Launcher** | `robot_info/launch/robot_info.launch` |
| **ROS version** | ROS1 Noetic, Ubuntu 20.04, Python 3 |

---

## 1. Communication flow

```
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
                  ros1_bridge ──▶ ROS2 robot_info2_node (see ../ros2_ws)
```

### Topics

| Topic | Type | Publisher | Subscribers | Content |
|---|---|---|---|---|
| `/user_information` | `robotinfo_msgs/GameUserMsg` | `info_user_node` | `game_node`, `result_game_node` | full name, username, age |
| `/keyboard_control` | `std_msgs/String` | `control_node` | `game_node` (and `robot_info2_node` in ROS2) | one command per key press |
| `/result_information` | `std_msgs/Int64` | `game_node` | `result_game_node` | the final score |

`/user_information` and `/result_information` are **latched**: a node that starts later still receives the last message.

### Services (offered by `game_node`)

| Service | Type | Client | Request → Response |
|---|---|---|---|
| `/difficulty` | `robotinfo_msgs/SetGameDifficulty` | `info_user_node` (or `rosservice call`) | `change_difficulty` = `"easy"`, `"medium"` or `"hard"` → `success` = `True` only in **phase1** |
| `/user_score` | `robotinfo_msgs/GetUserScore` | `result_game_node` | `username` → `score` = the user's final score **in percent** (0–100) of the maximum possible score |

### Parameters (created in `game_node`, private namespace `/game_node/`)

| Parameter | Type | Function |
|---|---|---|
| `/game_node/user_name` | string | the player's name, set when `/user_information` arrives |
| `/game_node/change_player_color` | int | colour of the detective: **1** Red, **2** Purple (default), **3** Blue. Read twice per second, so it can be changed while playing. |
| `/game_node/screen_param` | string | current game phase: `phase1`, `phase2` or `phase3` |

### Custom message and services (`robotinfo_msgs`)

```
# msg/GameUserMsg.msg          # srv/GetUserScore.srv       # srv/SetGameDifficulty.srv
string name                    string username              string change_difficulty
string username                ---                          ---
int64 age                      int64 score                  bool success
```

### Commands on `/keyboard_control`

| Key (in the control_node terminal) | Command | Used for |
|---|---|---|
| ↑ ↓ ← → | `UP` `DOWN` `LEFT` `RIGHT` | walk, move the cursor in menus |
| SPACE | `INTERACT` | examine, talk, pick a clue |
| ENTER | `CONFIRM` | confirm, next case, accuse, play again |
| ESC | `MENU` | pause menu / back |
| N / F / A / H | `NOTEBOOK` / `CASE_FILE` / `ACCUSE` / `HELP` | open the notebook, case file, accusation, help |
| 1 – 9 | `OPTION_1` … `OPTION_9` | choose a question when talking |
| X | `EXIT` | finish the game (end screens and final screen) |
| Q | – | quit control_node |

---

## 2. The nodes

### `info_user_node`
1. Asks for **full name, username, age and difficulty** in the terminal and validates the answers (name: letters only; username: 3–20 letters, digits or `_`; age: 1–120; difficulty: easy/medium/hard, ENTER = medium).
2. **Calls `/difficulty`** with the chosen level. This happens *before* the player data is published: until then `game_node` is sure to be in phase1, the only phase in which the difficulty may change.
3. **Publishes** the player data once as `GameUserMsg` on `/user_information`.

### `game_node` (main node)
The game logic is divided into three phases, each one a separate method of the `GameNode` class:

| Phase | `screen_param` | Method | What happens | Log message |
|---|---|---|---|---|
| 1 – Welcome | `phase1` | `welcome_phase()` | waits for `/user_information`, sets `user_name`, greets the player; **difficulty can be changed**; any key starts the game | `Welcome phase started.` |
| 2 – Game | `phase2` | `game_phase()` | runs the game; the detective and every menu are controlled only by `/keyboard_control` | `Game phase started.` |
| 3 – Final | `phase3` | `final_phase()` | calculates the final score, stores the percentage for `/user_score`, then publishes the score on `/result_information` | `Final phase reached, calculating score.` |

The game ends when all five cases are solved, or when the player chooses **Finish Game** (ESC menu, or X on an end screen). On the final screen, ENTER plays again (**back to phase1**, so the difficulty can be chosen again) and X quits.

**Difficulty** (only in phase1): `easy` = one obstacle fewer per room and 60 % speed, `medium` = the game as designed, `hard` = one obstacle more and 135 % speed.

**Final score** = points collected in the game + 100 per star.
Points: new clue +100, new question +10, solved case +500 plus 100 per attempt left, bumping into an obstacle −50, wrong accusation −100.

**Percentage for `/user_score`** = final score ÷ maximum possible score × 100, rounded and limited to 0–100. The maximum (10080) means: all clues found, all questions asked, all cases solved without a wrong accusation, and all 15 stars. An unknown username returns 0.

### `control_node`
Only responsible for keyboard input. It reads single key presses in its own terminal (no ENTER needed) and publishes the matching command on `/keyboard_control`.

### `result_game_node`
Subscribes to `/user_information` and `/result_information`. When the final score arrives, its **service client** sends the username to `/user_score` and prints the result:

```
+==========================================+
|  SHADOW DETECTIVE - FINAL RESULT         |
|                                          |
|  Player:      Ada Lovelace               |
|  Username:    ada_99                     |
|  Age:         36                         |
|  FINAL SCORE: 7780                       |
|  PERCENTAGE:  77 % of the maximum score  |
+==========================================+
```

---

## 3. Package structure

```
ros1_ws/
├── README.md
└── src/
    ├── robot_info/                     ROS1 nodes package
    │   ├── scripts/                    executable nodes
    │   │   ├── info_user_node.py
    │   │   ├── game_node.py
    │   │   ├── control_node.py
    │   │   └── result_game_node.py
    │   ├── src/robot_info/             importable Python package (game code, no ROS)
    │   │   ├── __init__.py
    │   │   ├── display.py              window and screen setup, colours, fonts
    │   │   ├── sprites.py              people, moving obstacles and props
    │   │   ├── renderer.py             drawing routines (text, glow, panels)
    │   │   ├── scenes.py               intro picture of every case
    │   │   ├── rooms.py                walls, floors and furniture of every room
    │   │   ├── story.py                the five cases
    │   │   └── engine.py               DetectiveGame: rules and screens, controlled by text commands
    │   ├── launch/robot_info.launch    starts all ROS1 nodes
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   └── setup.py                    installs src/robot_info (catkin_python_setup)
    └── robotinfo_msgs/                 message and service package
        ├── msg/GameUserMsg.msg
        ├── srv/GetUserScore.srv
        ├── srv/SetGameDifficulty.srv
        ├── CMakeLists.txt
        └── package.xml
```

### Design rules
- **One class per node, one node per file**, no global variables: publishers, subscribers, services, player data, scores and phase state live inside the classes.
- ROS callbacks (topics and services) run in other threads. `game_node` hands commands to the game loop through a `queue.Queue`, protects shared state (user, phase, scores, requested difficulty) with a lock, and never draws from a callback.
- The game window never reads the keyboard. Every command comes from `control_node` through `/keyboard_control`.
- A `pygame.time.Clock` keeps the game at 60 FPS.

---

## 4. Installation

Tested setup: **Ubuntu 20.04 + ROS Noetic** with Python 3.8.

```bash
# ROS Noetic (if not installed yet - full guide: http://wiki.ros.org/noetic/Installation/Ubuntu)
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt install curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo apt update
sudo apt install ros-noetic-desktop

# other dependencies
sudo apt install python3-pip xterm
pip3 install --user "pygame>=2"
```

- **pygame 2** is needed. The apt package of Ubuntu 20.04 is version 1.9 and too old, so install pygame with pip.
- **xterm** opens the terminal window of every node.
- Do not add `source /opt/ros/noetic/setup.bash` to `~/.bashrc` if ROS2 Foxy is installed too. The start script sources what each window needs.
- The complete game also needs the ROS2 part (bridge + ROS2 node): install ROS2 Foxy as described in [`../ros2_ws/README.md`](../ros2_ws/README.md).

## 5. Build

Build in place, inside `ros_final_work/` (in a terminal with only ROS1):

```bash
source /opt/ros/noetic/setup.bash
cd ros_final_work/ros1_ws
catkin_make
```

Check that the message and services were generated:

```bash
source devel/setup.bash
rosmsg show robotinfo_msgs/GameUserMsg
rossrv show robotinfo_msgs/GetUserScore
rossrv show robotinfo_msgs/SetGameDifficulty
```

Build the ROS2 workspace as well (see [`../ros2_ws/README.md`](../ros2_ws/README.md), section 3).

---

## 6. Run – one command

```bash
cd ros_final_work
./start_game.sh
```

This is the only way to start the game. It opens **one terminal window for every node** plus the **game window**:

| Window | Node | What you do there | Same as |
|---|---|---|---|
| `1_game_node` | game_node (ROS1) | log of the game; it opens the **game window** and offers `/user_score` and `/difficulty` | `rosrun robot_info game_node.py` |
| `2_info_user_node` | info_user_node (ROS1) | **type** full name, username, age and difficulty | `rosrun robot_info info_user_node.py` |
| `3_control_node_PLAY_HERE` | control_node (ROS1) | **click into this window and play**: arrow keys, SPACE, ENTER, ESC … | `rosrun robot_info control_node.py` |
| `4_result_game_node` | result_game_node (ROS1) | shows the final result with the percentage (service client of `/user_score`) | `rosrun robot_info result_game_node.py` |
| `5_robot_info2_node` | robot_info2_node (ROS2) | shows every command that arrives in ROS2 through ros1_bridge | `ros2 run robot_info2 robot_info2_node` |

The terminal in which you run `./start_game.sh` runs **roscore** (through `roslaunch robot_info robot_info.launch`, which opens windows 1–4) and **ros1_bridge**. All nodes stay reachable with `rosnode`, `rostopic`, `rosservice` and `rosparam` from any other terminal (section 7).

The colour of the detective at start: `PLAYER_COLOR=1 ./start_game.sh` (1 Red, 2 Purple, 3 Blue).

**Stopping:** close the game window, or press X on the final screen. All windows, the bridge and roscore then stop. Ctrl+C in the start terminal does the same.

### How a game goes
1. The game window shows *"Waiting for the player…"* (phase1).
2. In window **2_info_user_node**, enter name, username, age and difficulty. The difficulty is sent to `/difficulty`, then the player data to `/user_information`. The game window greets you by name and shows the difficulty.
3. Click into window **3_control_node_PLAY_HERE** and press any key. The game starts (phase2). Window 5 shows every command arriving in ROS2.
4. Solve the cases, or choose **ESC → Finish Game**. The final screen (phase3) shows your score and percentage, and window **4_result_game_node** prints the final message.
5. ENTER plays again (back to phase1), X quits.

---

## 7. Services and parameters from the terminal

While the game runs, open another terminal:

```bash
source /opt/ros/noetic/setup.bash
source ros_final_work/ros1_ws/devel/setup.bash

# services
rosservice list                                              # /difficulty, /user_score, ...
rosservice call /difficulty "change_difficulty: 'hard'"      # success: True only in phase1
rosservice call /user_score "username: 'ada_99'"             # score: percentage of the last game

# parameters
rosparam list /game_node
rosparam get /game_node/screen_param                         # phase1 / phase2 / phase3
rosparam get /game_node/user_name
rosparam set /game_node/change_player_color 1                # 1 Red, 2 Purple, 3 Blue - changes live
```

## 8. Watching the communication (debugging)

```bash
rosnode list
rostopic list
rostopic echo /keyboard_control
rostopic echo /result_information
rqt_graph
```

Example log of `game_node`:

```
[INFO] Parameters created: /game_node/change_player_color, /game_node/screen_param, /game_node/user_name
[INFO] game_node started - services /user_score and /difficulty ready, waiting for the player
[INFO] screen_param = phase1
[INFO] Welcome phase started.
[INFO] /difficulty: difficulty changed to 'hard'
[INFO] Received player data: Ada Lovelace (username 'ada_99', age 36) - parameter user_name set
[INFO] Player colour is now Blue (change_player_color = 3)
[INFO] screen_param = phase2
[INFO] Game phase started.
[WARN] /difficulty: 'easy' refused - the difficulty can only be changed in phase1
[INFO] Final phase reached, calculating score.
[INFO] Points 6280 + star bonus 1500 (15 stars) = final score 7780 (77% of 10080)
[INFO] /user_score: user 'ada_99' reached 77% of the maximum score
```

## 9. Troubleshooting

| Problem | Solution |
|---|---|
| `ROS1 workspace not built` / `ROS2 workspace not built` | Build both workspaces first (section 5). |
| `pygame 2.0 or newer is needed` | `pip3 install --user "pygame>=2"` |
| The detective does not move | Click into window **3_control_node_PLAY_HERE**, not into the game window. |
| `Difficulty …: NOT accepted` | The game had already left phase1 (a key was pressed in window 3 first). Finish the game and choose "play again". |
| `xterm is missing` | `sudo apt install xterm` |
| `[rosrun] Couldn't find executable` | `chmod +x src/robot_info/scripts/*.py`, then `catkin_make` again. |
| Old `build/` or `devel/` from another folder | Delete `build/` and `devel/` and run `catkin_make` again. |
