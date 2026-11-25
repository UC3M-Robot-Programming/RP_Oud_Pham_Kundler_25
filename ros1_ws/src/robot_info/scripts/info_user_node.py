#!/usr/bin/env python3
"""INFO_USER_NODE - asks the player for full name, username, age and difficulty in the
terminal, validates the answers, sets the difficulty with the /difficulty service of
game_node (robotinfo_msgs/SetGameDifficulty) and publishes the player data once on
/user_information (robotinfo_msgs/GameUserMsg).

The difficulty is set BEFORE the player data is published: until then game_node is sure
to be in phase1, the only phase in which the difficulty may change.
The topic is latched, so game_node and result_game_node also receive the player data
when they are started after this node.
"""
import re

import rospy
from robotinfo_msgs.msg import GameUserMsg
from robotinfo_msgs.srv import SetGameDifficulty


class InfoUserNode:
    NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ' .-]*$")
    USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,20}$")
    MIN_AGE, MAX_AGE = 1, 120
    DIFFICULTIES = ("easy", "medium", "hard")
    SERVICE_TIMEOUT = 10.0

    def __init__(self):
        rospy.init_node("info_user_node")
        self.publisher = rospy.Publisher("/user_information", GameUserMsg, queue_size=1, latch=True)
        self.name = None
        self.username = None
        self.age = None
        self.difficulty = None
        self.difficulty_client = rospy.ServiceProxy("/difficulty", SetGameDifficulty)
        rospy.loginfo("info_user_node started - publishing player data on /user_information")

    # ------------------------------------------------------------- questions

    def ask(self, question):
        """Reads one line from the terminal (raises EOFError / KeyboardInterrupt on Ctrl+D / Ctrl+C)."""
        return input(question).strip()

    def ask_name(self):
        while not rospy.is_shutdown():
            name = " ".join(self.ask("Full name: ").split())
            if len(name) >= 2 and self.NAME_PATTERN.match(name):
                return name
            print("  Please enter your full name with letters only (at least 2 characters).")

    def ask_username(self):
        while not rospy.is_shutdown():
            username = self.ask("Username: ")
            if self.USERNAME_PATTERN.match(username):
                return username
            print("  A username has 3 to 20 characters: letters, digits or _ (no spaces).")

    def ask_age(self):
        while not rospy.is_shutdown():
            text = self.ask("Age: ")
            if text.isdigit() and self.MIN_AGE <= int(text) <= self.MAX_AGE:
                return int(text)
            print("  Please enter your age as a whole number between %d and %d." % (self.MIN_AGE, self.MAX_AGE))

    def ask_difficulty(self):
        while not rospy.is_shutdown():
            text = self.ask("Difficulty (easy / medium / hard) [medium]: ").lower() or "medium"
            if text in self.DIFFICULTIES:
                return text
            print("  Please type easy, medium or hard (or just ENTER for medium).")

    def request_information(self):
        print("\n=== SHADOW DETECTIVE - new player ===")
        self.name = self.ask_name()
        self.username = self.ask_username()
        self.age = self.ask_age()
        self.difficulty = self.ask_difficulty()
        rospy.loginfo("Player data validated: name='%s', username='%s', age=%d, difficulty=%s",
                      self.name, self.username, self.age, self.difficulty)

    # ------------------------------------------------------------- service call

    def request_difficulty(self):
        """Calls game_node's /difficulty service. Returns True if the game accepted the level."""
        try:
            rospy.wait_for_service("/difficulty", timeout=self.SERVICE_TIMEOUT)
            rospy.loginfo("Calling /difficulty with '%s'", self.difficulty)
            response = self.difficulty_client(self.difficulty)
        except (rospy.ROSException, rospy.ServiceException) as error:
            rospy.logwarn("Service /difficulty not reachable (%s) - is game_node running?", error)
            return False
        if response.success:
            rospy.loginfo("/difficulty accepted: the game is set to '%s'", self.difficulty)
        else:
            rospy.logwarn("/difficulty refused: the game is not in phase1 any more")
        return response.success

    # ------------------------------------------------------------- publishing

    def publish_information(self):
        message = GameUserMsg()
        message.name = self.name
        message.username = self.username
        message.age = self.age
        self.publisher.publish(message)
        rospy.loginfo("Published player data on /user_information for game_node and result_game_node")

    def run(self):
        try:
            self.request_information()
        except (EOFError, KeyboardInterrupt):
            rospy.logwarn("Input cancelled - no player data published")
            return
        if rospy.is_shutdown():
            return
        accepted = self.request_difficulty()
        print("Difficulty %s: %s" % (self.difficulty, "accepted" if accepted else "NOT accepted"))
        self.publish_information()
        print("Thank you, %s! Switch to the game window - good luck, detective." % self.name)
        # keep the node alive so the latched message stays available for late subscribers
        rospy.spin()


if __name__ == "__main__":
    try:
        InfoUserNode().run()
    except rospy.ROSInterruptException:
        pass
