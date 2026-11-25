#!/usr/bin/env python3
"""CONTROL_NODE - only responsible for keyboard input.

It reads the keys pressed in its own terminal and publishes one command per key press
on /keyboard_control (std_msgs/String). Every command is a descriptive string in
capital letters:

    arrow keys  RIGHT, LEFT, UP, DOWN   (walk / move the cursor)
    SPACE       INTERACT                (examine, talk, pick a clue)
    ENTER       CONFIRM                 (confirm, next case, accuse)
    ESC         MENU                    (pause menu / back)
    N, F, A, H  NOTEBOOK, CASE_FILE, ACCUSE, HELP
    X           EXIT                    (finish the game on the end screen)
    1 - 9       OPTION_1 ... OPTION_9   (choose a question)

Q or Ctrl+C stops the node.
"""
import os
import select
import sys
import termios
import time
import tty

import rospy
from std_msgs.msg import String


class ControlNode:
    ARROWS = {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT"}
    KEYS = {" ": "INTERACT", "\r": "CONFIRM", "\n": "CONFIRM", "\x1b": "MENU",
            "n": "NOTEBOOK", "f": "CASE_FILE", "a": "ACCUSE", "h": "HELP", "x": "EXIT"}
    MOVEMENT = ("UP", "DOWN", "LEFT", "RIGHT")

    def __init__(self):
        rospy.init_node("control_node")
        self.publisher = rospy.Publisher("/keyboard_control", String, queue_size=10)
        self.fd = sys.stdin.fileno()
        self.old_terminal_settings = None
        self.last_logged = (None, 0.0)
        rospy.loginfo("control_node started - publishing commands on /keyboard_control")

    # ------------------------------------------------------------- keyboard

    def read_key(self, timeout=0.1):
        """Returns one key ('a', ' ', 'UP', ...) or None if nothing was pressed."""
        ready, _, _ = select.select([self.fd], [], [], timeout)
        if not ready:
            return None
        char = os.read(self.fd, 1).decode(errors="ignore")
        if char != "\x1b":
            return char
        # an arrow key sends ESC [ A (or ESC O A); a single ESC is the escape key
        ready, _, _ = select.select([self.fd], [], [], 0.03)
        if not ready:
            return char
        sequence = os.read(self.fd, 2).decode(errors="ignore")
        if len(sequence) == 2 and sequence[0] in "[O" and sequence[1] in self.ARROWS:
            return self.ARROWS[sequence[1]]
        return None

    def command_for(self, key):
        if key in self.MOVEMENT:
            return key
        if key.isdigit() and key != "0":
            return "OPTION_" + key
        return self.KEYS.get(key.lower())

    # ------------------------------------------------------------- publishing

    def publish(self, command):
        self.publisher.publish(String(data=command))
        # holding an arrow key repeats it many times per second - log movement at most once per second
        last_command, last_time = self.last_logged
        now = time.time()
        if command not in self.MOVEMENT or command != last_command or now - last_time > 1.0:
            rospy.loginfo("Published command: %s", command)
            self.last_logged = (command, now)

    def print_help(self):
        print("\n=== SHADOW DETECTIVE - controller ===")
        print("Keep this terminal selected and use:")
        print("  Arrow keys  walk / move the cursor      SPACE  examine, talk, pick")
        print("  ENTER       confirm                     ESC    menu / back")
        print("  N notebook   F case file   A accuse   H help   1-9 questions   X finish")
        print("  Q           quit this controller\n")

    def run(self):
        if not os.isatty(self.fd):
            rospy.logerr("control_node needs a terminal - start it with: rosrun robot_info control_node.py")
            return
        self.print_help()
        self.old_terminal_settings = termios.tcgetattr(self.fd)
        try:
            tty.setcbreak(self.fd)           # read single key presses without ENTER
            while not rospy.is_shutdown():
                key = self.read_key()
                if key is None:
                    continue
                if key in ("q", "Q", "\x03"):
                    rospy.loginfo("Quit key pressed - stopping control_node")
                    break
                command = self.command_for(key)
                if command:
                    self.publish(command)
        finally:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_terminal_settings)


if __name__ == "__main__":
    try:
        ControlNode().run()
    except rospy.ROSInterruptException:
        pass
