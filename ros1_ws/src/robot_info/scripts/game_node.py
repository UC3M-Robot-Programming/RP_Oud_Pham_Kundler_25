#!/usr/bin/env python3
"""GAME_NODE - the main node with the game logic, divided into three phases.

Phase 1 - Welcome: wait for the player data on /user_information (robotinfo_msgs/GameUserMsg),
                   greet the player. The difficulty can only be changed here (/difficulty).
Phase 2 - Game:    run Shadow Detective. The detective (and every menu) is controlled only
                   by the commands from control_node on /keyboard_control (std_msgs/String).
Phase 3 - Final:   detect the end of the game, calculate the final score and publish it
                   on /result_information (std_msgs/Int64) for result_game_node.

Services offered (package robotinfo_msgs):
    /user_score  (GetUserScore)       username -> score as percentage (0-100) of the maximum score
    /difficulty  (SetGameDifficulty)  "easy" | "medium" | "hard" -> True only in phase1

Parameters (private, i.e. /game_node/<name>):
    ~user_name            string  the player's name (set when /user_information arrives)
    ~change_player_color  int     1 Red, 2 Purple, 3 Blue - read twice per second, changes live
    ~screen_param         string  current phase: phase1, phase2 or phase3
"""
import queue
import threading

import pygame
import rospy
from robotinfo_msgs.msg import GameUserMsg
from robotinfo_msgs.srv import (GetUserScore, GetUserScoreResponse, SetGameDifficulty,
                                SetGameDifficultyResponse)
from std_msgs.msg import Int64, String

from robot_info.display import PLAYER_COLORS, Display
from robot_info.engine import DIFFICULTIES, STAR_BONUS, DetectiveGame


class GameNode:
    SCREEN_PARAM = {"welcome": "phase1", "game": "phase2", "final": "phase3"}
    PARAM_POLL_SECONDS = 0.5           # reading a parameter is a call to the ROS master - not every frame
    DEFAULT_COLOR = 2                  # purple

    def __init__(self):
        rospy.init_node("game_node")
        self.lock = threading.Lock()   # protects everything the ROS callbacks share with the game loop
        self.user = None               # player data, filled by user_callback
        self.phase = "welcome"         # welcome, game or final
        self.pending_difficulty = None # accepted by /difficulty, applied by the game loop
        self.scores = {}               # username (and name) -> last score in percent, for /user_score
        self.commands = queue.Queue()  # commands from control_node (callbacks run in other threads)
        self.final_score = None
        self.color_value = None
        self.param_timer = 0.0             # time since change_player_color was last read
        # full names of the private parameters, e.g. /game_node/user_name
        self.param = {name: rospy.get_name() + "/" + name
                      for name in ("user_name", "change_player_color", "screen_param")}

        self.display = Display("Shadow Detective - ROS")
        self.game = DetectiveGame(self.display.screen)
        self.setup_parameters()

        self.user_subscriber = rospy.Subscriber("/user_information", GameUserMsg, self.user_callback)
        self.keyboard_subscriber = rospy.Subscriber("/keyboard_control", String, self.keyboard_callback)
        self.result_publisher = rospy.Publisher("/result_information", Int64, queue_size=1, latch=True)
        self.score_service = rospy.Service("/user_score", GetUserScore, self.handle_user_score)
        self.difficulty_service = rospy.Service("/difficulty", SetGameDifficulty, self.handle_difficulty)
        rospy.loginfo("game_node started - services /user_score and /difficulty ready, waiting for the player")

    # ------------------------------------------------------------- parameters

    def setup_parameters(self):
        rospy.set_param(self.param["user_name"], "")
        rospy.set_param(self.param["screen_param"], self.SCREEN_PARAM["welcome"])
        if not rospy.has_param(self.param["change_player_color"]):
            rospy.set_param(self.param["change_player_color"], self.DEFAULT_COLOR)
        self.poll_parameters()
        rospy.loginfo("Parameters created: %s", ", ".join(sorted(self.param.values())))

    def poll_parameters(self):
        """Applies a new value of ~change_player_color (changed e.g. with rosparam set)."""
        raw = rospy.get_param(self.param["change_player_color"], self.DEFAULT_COLOR)
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = None
        if value not in PLAYER_COLORS:
            if raw != self.color_value:
                rospy.logwarn("change_player_color must be 1 (Red), 2 (Purple) or 3 (Blue), got %r", raw)
                self.color_value = raw
            return
        if value != self.color_value:
            self.color_value = value
            self.game.set_player_color(value)
            rospy.loginfo("Player colour is now %s (change_player_color = %d)", PLAYER_COLORS[value][0], value)

    def set_phase(self, phase):
        with self.lock:
            self.phase = phase
        rospy.set_param(self.param["screen_param"], self.SCREEN_PARAM[phase])
        rospy.loginfo("screen_param = %s", self.SCREEN_PARAM[phase])

    # ------------------------------------------------------------- topic callbacks

    def user_callback(self, message):
        with self.lock:
            self.user = {"name": message.name, "username": message.username, "age": message.age}
        rospy.set_param(self.param["user_name"], message.name)
        rospy.loginfo("Received player data: %s (username '%s', age %d) - parameter user_name set",
                      message.name, message.username, message.age)

    def keyboard_callback(self, message):
        self.commands.put(message.data)

    def get_user(self):
        with self.lock:
            return dict(self.user) if self.user else None

    def next_commands(self):
        commands = []
        while not self.commands.empty():
            commands.append(self.commands.get_nowait())
        return commands

    # ------------------------------------------------------------- services

    def handle_difficulty(self, request):
        """SetGameDifficulty: change the difficulty - only accepted in phase1."""
        level = request.change_difficulty.strip().lower()
        if level not in DIFFICULTIES:
            rospy.logwarn("/difficulty: unknown level '%s' (use easy, medium or hard)", request.change_difficulty)
            return SetGameDifficultyResponse(success=False)
        with self.lock:
            if self.phase != "welcome":
                rospy.logwarn("/difficulty: '%s' refused - the difficulty can only be changed in phase1", level)
                return SetGameDifficultyResponse(success=False)
            self.pending_difficulty = level
        rospy.loginfo("/difficulty: difficulty changed to '%s'", level)
        return SetGameDifficultyResponse(success=True)

    def handle_user_score(self, request):
        """GetUserScore: score of a user as a percentage (0-100) of the maximum possible score."""
        key = request.username.strip()
        with self.lock:
            percent = self.scores.get(key)
        if percent is None:
            rospy.logwarn("/user_score: no finished game for user '%s' - returning 0", key)
            return GetUserScoreResponse(score=0)
        rospy.loginfo("/user_score: user '%s' reached %d%% of the maximum score", key, percent)
        return GetUserScoreResponse(score=percent)

    # ------------------------------------------------------------- frame

    def next_frame(self):
        """Waits for the next frame, handles window events, parameters and a new difficulty.
        The window reads neither keyboard nor mouse: every input comes from control_node."""
        dt = self.display.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rospy.signal_shutdown("game window closed")
        self.param_timer += dt
        if self.param_timer >= self.PARAM_POLL_SECONDS:
            self.param_timer = 0.0
            self.poll_parameters()
        with self.lock:
            level, self.pending_difficulty = self.pending_difficulty, None
        if level:
            self.game.set_difficulty(level)
        self.game.t += dt
        self.game.update(dt)
        for event in self.game.pop_events():
            rospy.loginfo(event)
        return dt

    # ------------------------------------------------------------- phase 1

    def welcome_phase(self):
        """Waits for the player data, greets the player and starts the game on any key."""
        self.set_phase("welcome")
        rospy.loginfo("Welcome phase started.")
        self.next_commands()                     # forget keys pressed before this phase
        greeted = False
        while not rospy.is_shutdown():
            self.next_frame()
            user = self.get_user()
            if user and not greeted:
                rospy.loginfo("Welcome, %s! Waiting for a key from control_node to start.", user["name"])
                greeted = True
            commands = self.next_commands()
            if user and commands:
                rospy.loginfo("Key '%s' received - leaving the welcome phase (difficulty %s)",
                              commands[0], self.game.difficulty)
                return True
            self.game.draw_welcome(self.display.screen, user)
            self.display.flip()
        return False

    # ------------------------------------------------------------- phase 2

    def game_phase(self):
        """Runs Shadow Detective until the player solved all cases or chose to finish."""
        self.set_phase("game")
        rospy.loginfo("Game phase started.")
        self.game.new_game()
        while not rospy.is_shutdown() and not self.game.finished:
            self.next_frame()
            for command in self.next_commands():
                self.game.handle_command(command)
            self.game.draw()
            self.display.flip()
        for event in self.game.pop_events():
            rospy.loginfo(event)
        return self.game.finished

    # ------------------------------------------------------------- phase 3

    def calculate_final_score(self):
        """Final score = points collected in the game + a bonus for every star."""
        points = self.game.score
        star_bonus = STAR_BONUS * sum(self.game.stars)
        return points, star_bonus, points + star_bonus

    def score_percent(self, final_score):
        return max(0, min(100, round(100 * final_score / DetectiveGame.max_score())))

    def final_phase(self):
        """Calculates, stores and publishes the final score, then asks: play again or quit?"""
        self.set_phase("final")
        rospy.loginfo("Final phase reached, calculating score.")
        points, star_bonus, self.final_score = self.calculate_final_score()
        percent = self.score_percent(self.final_score)
        rospy.loginfo("Points %d + star bonus %d (%d stars) = final score %d (%d%% of %d)",
                      points, star_bonus, sum(self.game.stars), self.final_score, percent,
                      DetectiveGame.max_score())
        user = self.get_user()
        if user:
            # store first, so /user_score already knows the score when result_game_node asks
            with self.lock:
                self.scores[user["username"]] = percent
                self.scores[user["name"]] = percent
        self.result_publisher.publish(Int64(data=self.final_score))
        rospy.loginfo("Published final score %d on /result_information", self.final_score)
        self.next_commands()
        while not rospy.is_shutdown():
            self.next_frame()
            for command in self.next_commands():
                if command in ("CONFIRM", "INTERACT"):
                    rospy.loginfo("Player wants to play again - back to phase1")
                    return "again"
                if command in ("EXIT", "MENU"):
                    rospy.loginfo("Player quit the game")
                    return "quit"
            self.game.draw_final(self.display.screen, user, points, star_bonus,
                                 self.final_score, published=True, percent=percent)
            self.display.flip()
        return "quit"

    # ------------------------------------------------------------- main loop

    def run(self):
        try:
            while not rospy.is_shutdown():
                if not self.welcome_phase():
                    break
                if not self.game_phase():
                    break
                if self.final_phase() != "again":
                    break
        finally:
            rospy.loginfo("game_node shutting down")
            self.display.close()


if __name__ == "__main__":
    try:
        GameNode().run()
    except rospy.ROSInterruptException:
        pass
