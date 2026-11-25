#!/usr/bin/env python3
"""RESULT_GAME_NODE - shows the final result of the game.

Subscribes to
    /user_information    (robotinfo_msgs/GameUserMsg)  player data from info_user_node
    /result_information  (std_msgs/Int64)              final score from game_node
Service client of
    /user_score          (robotinfo_msgs/GetUserScore) sends the username, receives the
                                                        score as a percentage
and prints a clear final message with the username, the final score and the percentage.
"""
import threading

import rospy
from robotinfo_msgs.msg import GameUserMsg
from robotinfo_msgs.srv import GetUserScore
from std_msgs.msg import Int64


class ResultGameNode:
    SERVICE_TIMEOUT = 5.0              # seconds to wait for game_node's /user_score service

    def __init__(self):
        rospy.init_node("result_game_node")
        self.lock = threading.Lock()
        self.user = None
        self.pending_score = None      # a score that arrived before the player data
        self.games_shown = 0
        self.user_subscriber = rospy.Subscriber("/user_information", GameUserMsg, self.user_callback)
        self.result_subscriber = rospy.Subscriber("/result_information", Int64, self.result_callback)
        self.score_client = rospy.ServiceProxy("/user_score", GetUserScore)
        rospy.loginfo("result_game_node started - waiting for /user_information and /result_information")

    def user_callback(self, message):
        with self.lock:
            self.user = message
            rospy.loginfo("Received player data: %s (username '%s', age %d)",
                          message.name, message.username, message.age)
            if self.pending_score is not None:
                score, self.pending_score = self.pending_score, None
                self.show_result(score)

    def result_callback(self, message):
        with self.lock:
            rospy.loginfo("Received final score %d from game_node", message.data)
            if self.user is None:
                rospy.logwarn("Final score arrived before the player data - waiting for /user_information")
                self.pending_score = message.data
                return
            self.show_result(message.data)

    # ------------------------------------------------------------- service client

    def request_percentage(self, username):
        """Asks game_node's /user_score service for the score percentage of this user."""
        try:
            rospy.wait_for_service("/user_score", timeout=self.SERVICE_TIMEOUT)
            rospy.loginfo("Calling /user_score for username '%s'", username)
            response = self.score_client(username)
        except (rospy.ROSException, rospy.ServiceException) as error:
            rospy.logerr("Service /user_score failed: %s", error)
            return None
        rospy.loginfo("/user_score answered: %d%%", response.score)
        return response.score

    # ------------------------------------------------------------- output

    def show_result(self, score):
        self.games_shown += 1
        percent = self.request_percentage(self.user.username)
        lines = [
            "SHADOW DETECTIVE - FINAL RESULT" + ("  (game %d)" % self.games_shown if self.games_shown > 1 else ""),
            "",
            "Player:      %s" % self.user.name,
            "Username:    %s" % self.user.username,
            "Age:         %d" % self.user.age,
            "FINAL SCORE: %d" % score,
            "PERCENTAGE:  %s" % ("%d %% of the maximum score" % percent if percent is not None
                                 else "not available (service /user_score failed)"),
        ]
        width = max(len(line) for line in lines) + 4
        print("\n+" + "=" * width + "+")
        for line in lines:
            print("|  " + line.ljust(width - 2) + "|")
        print("+" + "=" * width + "+\n", flush=True)
        rospy.loginfo("Final message shown: username '%s' scored %d points (%s%%)",
                      self.user.username, score, percent if percent is not None else "?")

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        ResultGameNode().run()
    except rospy.ROSInterruptException:
        pass
