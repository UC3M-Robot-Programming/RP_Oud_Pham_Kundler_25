"""The detective game itself, without any ROS code.

DetectiveGame knows the rules, the rooms and all screens of the game. It does not
read the keyboard: game_node passes it the commands that arrive on the
/keyboard_control topic (handle_command) and asks it to update and draw itself.
"""
import math
import os
import random

import pygame

from robot_info.display import (
    BLACK, BULB_COLORS, DARK, FLOOR_Y, GOLD, GREY, HEIGHT, INK, LIGHT_GREY, ORANGE,
    PAPER, PLAYER_COLORS, RED, TOP_BAR, WHITE, WIDTH, YELLOW, load_font)
from robot_info.story import CASES, HOW_TO_PLAY
from robot_info.renderer import (
    draw_star, draw_text, draw_text_block, glow, panel, shade_screen, vertical_gradient)
from robot_info.sprites import draw_person
from robot_info.scenes import SCENES
from robot_info.rooms import RoomArtist


HIGHSCORE_FILE = os.path.join(os.path.expanduser("~"), ".shadow_detective_highscore")
PLAYER_SPEED = 230           # pixels per second
PLAYER_TOP, PLAYER_BOTTOM = 448, 588
POINTS_CLUE = 100
POINTS_QUESTION = 10
POINTS_SOLVED = 500
POINTS_HIT = -50
POINTS_WRONG = -100
STAR_BONUS = 100             # extra points per star for the final score
MOVE_STEP_TIME = 0.22        # one movement command makes the detective walk this long (seconds)
MOVES = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}

# Difficulty set with the /difficulty service: change of the number of obstacles per room
# and factor for their speed ("medium" is the game exactly as designed in Part I)
DIFFICULTIES = {"easy": (-1, 0.6), "medium": (0, 1.0), "hard": (1, 1.35)}


class DetectiveGame(RoomArtist):
    def __init__(self, screen):
        self.screen = screen
        self.difficulty = "medium"
        self.player_color = PLAYER_COLORS[2][1]
        self.events = []             # short log lines for game_node (see pop_events)
        self.finished = False        # True when the player wants to end the game
        self.move_dir = (0, 0)
        self.move_time = 0.0
        self.font_title = load_font(52, bold=True)
        self.font_big = load_font(28, bold=True)
        self.font = load_font(18)
        self.font_bold = load_font(18, bold=True)
        self.font_small = load_font(14)
        self.font_small_bold = load_font(14, bold=True)
        self.font_tiny = load_font(11, bold=True)
        self.scenes = {}
        for name, builder in SCENES.items():
            surface = pygame.Surface((WIDTH, HEIGHT))
            builder(surface, (self.font_small, self.font_big))
            self.scenes[name] = surface
        self.vignette = self.build_vignette()
        self.tints = {}
        self.particles = [[random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                           random.uniform(0.6, 1.4), random.uniform(0, 6.3)] for _ in range(170)]
        self.motes = [[random.uniform(0, WIDTH), random.uniform(TOP_BAR, HEIGHT),
                       random.uniform(0, 6.3)] for _ in range(28)]
        self.t = 0.0
        self.flash = 0.0
        self.highscore = self.load_highscore()
        self.new_highscore = False
        self.menu_index = 0
        self.new_game()

    def load_highscore(self):
        try:
            with open(HIGHSCORE_FILE) as f:
                return int(f.read().strip() or 0)
        except (OSError, ValueError):
            return 0

    def record_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            self.new_highscore = True
            try:
                with open(HIGHSCORE_FILE, "w") as f:
                    f.write(str(self.score))
            except OSError:
                pass

    def build_vignette(self):
        small = pygame.Surface((96, 60), pygame.SRCALPHA)
        for y in range(60):
            for x in range(96):
                dx = (x - 47.5) / 48
                dy = (y - 29.5) / 30
                d = min(1.0, math.sqrt(dx * dx + dy * dy))
                small.set_at((x, y), (0, 0, 0, int(170 * d ** 2.2)))
        return pygame.transform.smoothscale(small, (WIDTH, HEIGHT))

    def new_game(self):
        self.case_index = 0
        self.stars = []
        self.howto_return = "case_intro"
        self.menu_return = None
        self.score = 0
        self.new_highscore = False
        self.finished = False
        self.events = []
        self.start_case()
        self.state = "howto"        # every new game starts with the how-to-play screen

    def start_case(self, restart=False):
        # a restarted case gives back the points earned in it, so nobody can farm points
        if restart:
            self.score = self.case_start_score
        else:
            self.case_start_score = self.score
        self.case = CASES[self.case_index]
        self.theme = self.case["theme"]
        self.clues = self.case["clues"]
        self.suspects = self.case["suspects"]
        self.room = self.case["start"]
        self.found = []
        self.mistakes = 0
        self.message = None
        self.talk_id = None
        self.talk_text = ""
        self.asked = set()
        self.accuse_step = "suspect"
        self.accuse_suspect = None
        self.selected = []
        self.result = None
        self.file_first = True
        self.bumps = 0
        self.bonus = 0
        self.px, self.py = 480.0, 520.0
        self.walk = 0.0
        self.invulnerable = 0.0
        self.floaters = []
        self.talk_index = 0
        self.accuse_index = 0
        self.evidence_index = 0
        self.move_dir = (0, 0)
        self.move_time = 0.0
        self.spawn_enemies()
        self.state = "case_intro"
        self.log("Case %d started: %s" % (self.case_index + 1, self.case["title"]))

    def attempts_left(self):
        return self.case["attempts"] - self.mistakes

    def log(self, text):
        self.events.append(text)

    def pop_events(self):
        """Returns the log lines since the last call (game_node writes them with rospy.loginfo)."""
        events, self.events = self.events, []
        return events

    def set_difficulty(self, level):
        """Changes the difficulty ("easy", "medium", "hard"). game_node only calls it in phase1."""
        self.difficulty = level
        self.log("Difficulty set to %s" % level)

    def set_player_color(self, value):
        """Recolours the detective (1 Red, 2 Purple, 3 Blue) - from the ROS parameter change_player_color."""
        self.player_color = PLAYER_COLORS[value][1]

    @staticmethod
    def max_score():
        """Highest possible final score: every clue, every question, every case solved without
        a wrong accusation (all attempts left) and all stars."""
        total = 0
        for case in CASES:
            total += POINTS_CLUE * len(case["clues"])
            total += POINTS_QUESTION * sum(len(s["topics"]) for s in case["suspects"].values())
            total += POINTS_SOLVED + 100 * case["attempts"] + 3 * STAR_BONUS
        return total

    def finish_game(self):
        """The player wants to stop - game_node then moves on to the final phase."""
        self.record_highscore()
        self.finished = True
        self.log("Player finished the game in case %d" % (self.case_index + 1))

    def update(self, dt):
        weather = self.theme["weather"]
        speed = {"rain": 650, "snow": 60, "confetti": 45}[weather]
        for p in self.particles:
            p[1] += speed * p[2] * dt
            p[0] -= speed * p[2] * dt * (0.25 if weather == "rain" else 0)
            p[3] += dt * 2
            if p[1] > HEIGHT:
                p[0] = random.uniform(0, WIDTH + 150)
                p[1] = random.uniform(-40, 0)
        for m in self.motes:
            m[1] -= dt * 6
            m[2] += dt
            if m[1] < TOP_BAR:
                m[1] = HEIGHT
                m[0] = random.uniform(0, WIDTH)
        self.flash = max(0.0, self.flash - dt * 3)
        if random.random() < dt / 6:
            self.flash = 1.0
        for f in self.floaters:
            f[3] += dt
        self.floaters = [f for f in self.floaters if f[3] < 1.2]
        if self.state == "explore":
            self.update_player(dt)
            self.update_enemies(dt)

    def update_player(self, dt):
        # every movement command from control_node makes the detective walk for a short time;
        # holding a key down sends repeated commands, so the walk looks smooth
        dx, dy = self.move_dir if self.move_time > 0 else (0, 0)
        self.move_time = max(0.0, self.move_time - dt)
        self.px += dx * PLAYER_SPEED * dt
        self.py += dy * PLAYER_SPEED * 0.6 * dt
        self.py = max(PLAYER_TOP, min(PLAYER_BOTTOM, self.py))
        self.walk = self.walk + dt * 11 if (dx or dy) else 0.0
        self.invulnerable = max(0.0, self.invulnerable - dt)
        # walking out at the left or right edge goes through the door on that side
        if self.px < 24 or self.px > WIDTH - 24:
            side_left = self.px < 24
            for door in self.case["rooms"][self.room]["doors"]:
                if (pygame.Rect(door["rect"]).centerx < WIDTH // 2) == side_left:
                    self.enter_room(door["to"])
                    return
            self.px = max(24, min(WIDTH - 24, self.px))

    def enter_room(self, new_room):
        old_room = self.room
        self.room = new_room
        self.px = 480
        for door in self.case["rooms"][new_room]["doors"]:
            if door["to"] == old_room:
                self.px = 80 if pygame.Rect(door["rect"]).centerx < WIDTH // 2 else WIDTH - 80
        self.py = max(PLAYER_TOP, min(PLAYER_BOTTOM, self.py))
        self.invulnerable = max(self.invulnerable, 0.8)
        self.move_time = 0.0
        self.spawn_enemies()
        self.log("Entered room: %s" % self.case["rooms"][new_room]["name"])

    def spawn_enemies(self):
        theme = self.theme
        extra, speed_factor = DIFFICULTIES[self.difficulty]
        self.enemies = []
        for i in range(max(0, theme["enemies"] + extra)):
            x = random.uniform(120, 840)
            for _ in range(30):
                if abs(x - self.px) > 230:
                    break
                x = random.uniform(120, 840)
            lane = 462 + (i * 41) % 118
            speed = theme["enemy_speed"] * speed_factor * random.uniform(0.85, 1.15)
            if theme["enemy_mode"] == "bounce":
                angle = random.uniform(0.35, 1.0) * random.choice([-1, 1])
                vx = math.cos(angle) * speed * random.choice([-1, 1])
                vy = math.sin(angle) * speed * 0.6
            else:
                vx, vy = speed * random.choice([-1, 1]), 0.0
            self.enemies.append([x, lane, vx, vy, random.uniform(0, 5)])

    def update_enemies(self, dt):
        for e in self.enemies:
            e[0] += e[2] * dt
            e[1] += e[3] * dt
            e[4] += dt
            if not 90 < e[0] < WIDTH - 90:
                e[2] = -e[2]
                e[0] = max(90, min(WIDTH - 90, e[0]))
            if not 456 < e[1] < 588:
                e[3] = -e[3]
                e[1] = max(456, min(588, e[1]))
        if self.invulnerable > 0:
            return
        for e in self.enemies:
            if abs(e[0] - self.px) < 40 and abs(e[1] - self.py) < 18:
                self.hit_by(e)
                break

    def hit_by(self, enemy):
        # bumping into an obstacle costs points and pushes the player back - nobody dies
        self.bumps += 1
        self.add_points(POINTS_HIT, self.px, self.py - 200)
        self.log("Bumped into the %s (%d points, score %d)" % (self.theme["enemy_name"], POINTS_HIT, self.score))
        self.invulnerable = 1.6
        push = 70 if self.px >= enemy[0] else -70
        self.px = max(30, min(WIDTH - 30, self.px + push))

    def add_points(self, points, x, y):
        self.score = max(0, self.score + points)
        text = ("+%d" % points) if points > 0 else str(points)
        self.floaters.append([text, x, y, 0.0, YELLOW if points > 0 else RED])

    def nearby_spot(self):
        best, best_dist = None, 10 ** 9
        for spot in self.hotspots():
            r = spot["rect"]
            if not r.left - 30 <= self.px <= r.right + 30:
                continue
            if spot["kind"] == "talk":
                if abs(self.py - spot["feet"]) > 70:
                    continue
            elif r.bottom > FLOOR_Y + 5:
                if not r.top - 20 <= self.py <= r.bottom + 50:
                    continue
            elif self.py > FLOOR_Y + 75:
                continue
            dist = abs(self.px - r.centerx) + (40 if spot["kind"] == "door" else 0)
            if dist < best_dist:
                best, best_dist = spot, dist
        return best

    def use_spot(self, spot):
        kind = spot["kind"]
        if kind == "clue":
            if spot.get("needs") and spot["needs"] not in self.found:
                self.show_message(*spot["locked"])
                return
            cid = spot["clue"]
            new = cid not in self.found
            if new:
                self.found.append(cid)
                self.add_points(POINTS_CLUE, self.px, self.py - 200)
                self.log("Clue found: %s (%d/%d, score %d)" % (self.clues[cid][0], len(self.found),
                                                              len(self.clues), self.score))
            title, text = self.clues[cid]
            self.show_message(title, text, "New clue added to your notebook! +%d points" % POINTS_CLUE
                              if new else None)
        elif kind == "look":
            self.show_message(*spot["look"])
        elif kind == "door":
            self.enter_room(spot["to"])
        elif kind == "talk":
            self.talk_id = spot["who"]
            self.talk_text = self.suspects[spot["who"]]["greeting"]
            self.talk_index = 0
            self.state = "talk"
            self.log("Talking to %s" % self.suspects[spot["who"]]["name"])

    def handle_command(self, command):
        """Reacts to one command from /keyboard_control, e.g. "UP", "INTERACT" or "OPTION_2"."""
        state = self.state
        option = int(command[7:]) - 1 if command.startswith("OPTION_") and command[7:].isdigit() else None
        if state == "howto":
            self.state = self.howto_return
        elif state == "menu":
            if command == "MENU":
                self.state = self.menu_return
            elif command in ("UP", "LEFT"):
                self.menu_index = (self.menu_index - 1) % len(self.MENU_ITEMS)
            elif command in ("DOWN", "RIGHT"):
                self.menu_index = (self.menu_index + 1) % len(self.MENU_ITEMS)
            elif command in ("CONFIRM", "INTERACT"):
                self.activate_menu(self.MENU_ITEMS[self.menu_index][0])
            elif option is not None and option < len(self.MENU_ITEMS):
                self.activate_menu(self.MENU_ITEMS[option][0])
        elif state == "message":
            if command in ("INTERACT", "CONFIRM", "MENU"):
                self.close_message()
        elif state == "case_intro":
            if command == "MENU":
                self.open_menu()
            else:
                self.file_first = True
                self.state = "case_file"
        elif state == "case_file":
            if command in ("INTERACT", "CONFIRM", "MENU", "CASE_FILE"):
                self.file_first = False
                self.state = "explore"
        elif state == "notebook":
            if command in ("NOTEBOOK", "MENU", "INTERACT", "CONFIRM"):
                self.state = "explore"
        elif state == "talk":
            options = self.talk_options()
            if command == "MENU":
                self.state = "explore"
            elif command in ("UP", "LEFT"):
                self.talk_index = (self.talk_index - 1) % len(options)
            elif command in ("DOWN", "RIGHT"):
                self.talk_index = (self.talk_index + 1) % len(options)
            elif command in ("INTERACT", "CONFIRM"):
                self.choose_topic(options[min(self.talk_index, len(options) - 1)][0][0])
            elif option is not None and option < len(options):
                self.talk_index = option
                self.choose_topic(options[option][0][0])
        elif state == "accuse":
            self.accuse_command(command)
        elif state == "ending":
            if command in ("CONFIRM", "INTERACT"):
                self.end_button_pressed()
            elif command == "EXIT":
                self.finish_game()
            elif command == "MENU":
                self.open_menu()
        elif state == "explore":
            if command in MOVES:
                self.move_dir = MOVES[command]
                self.move_time = MOVE_STEP_TIME
            elif command == "MENU":
                self.open_menu()
            elif command == "INTERACT":
                spot = self.nearby_spot()
                if spot:
                    self.use_spot(spot)
            elif command == "NOTEBOOK":
                self.state = "notebook"
            elif command == "ACCUSE":
                self.start_accuse()
            elif command == "CASE_FILE":
                self.file_first = False
                self.state = "case_file"
            elif command == "HELP":
                self.open_howto("explore")

    def accuse_command(self, command):
        """Arrow keys move the cursor, SPACE picks a clue, ENTER accuses, ESC goes back."""
        if self.accuse_step == "suspect":
            count = len(self.suspects)
            if command in ("LEFT", "UP"):
                self.accuse_index = (self.accuse_index - 1) % count
            elif command in ("RIGHT", "DOWN"):
                self.accuse_index = (self.accuse_index + 1) % count
            elif command in ("CONFIRM", "INTERACT"):
                self.accuse_suspect = list(self.suspects)[self.accuse_index]
                self.accuse_step = "evidence"
                self.evidence_index = 0
            elif command == "MENU":
                self.state = "explore"
            return
        count = len(self.found)
        per_col = count if count <= 4 else (count + 1) // 2
        if command == "UP":
            self.evidence_index = (self.evidence_index - 1) % count
        elif command == "DOWN":
            self.evidence_index = (self.evidence_index + 1) % count
        elif command in ("LEFT", "RIGHT") and count > 4:
            step = per_col if command == "RIGHT" else -per_col
            self.evidence_index = min(count - 1, max(0, self.evidence_index + step))
        elif command == "INTERACT" or (command == "CONFIRM" and len(self.selected) != self.case["evidence"]):
            self.toggle_evidence(self.found[self.evidence_index])
        elif command == "CONFIRM":
            self.judge(self.accuse_suspect, self.selected)
        elif command == "MENU":
            self.accuse_step = "suspect"
            self.selected = []

    def open_howto(self, back_to):
        self.howto_return = back_to
        self.state = "howto"

    def handle_click(self, pos):
        if self.state in ("case_intro", "case_file", "ending") \
                and self.corner_menu_button().collidepoint(pos):
            self.open_menu()
            return
        if self.state == "menu":
            self.click_menu(pos)
        elif self.state == "howto":
            self.state = self.howto_return
        elif self.state == "case_intro":
            self.file_first = True
            self.state = "case_file"
        elif self.state == "case_file":
            self.file_first = False
            self.state = "explore"
        elif self.state == "message":
            self.close_message()
        elif self.state == "notebook":
            self.state = "explore"
        elif self.state == "explore":
            self.click_explore(pos)
        elif self.state == "talk":
            self.click_talk(pos)
        elif self.state == "accuse":
            self.click_accuse(pos)
        elif self.state == "ending":
            if self.end_button_rect().collidepoint(pos):
                self.end_button_pressed()
            elif self.exit_button_rect().collidepoint(pos):
                self.finish_game()

    def click_explore(self, pos):
        if self.menu_button().collidepoint(pos):
            self.open_menu()
            return
        if self.file_button().collidepoint(pos):
            self.file_first = False
            self.state = "case_file"
            return
        if self.notebook_button().collidepoint(pos):
            self.state = "notebook"
            return
        if self.accuse_button().collidepoint(pos):
            self.start_accuse()

    def show_message(self, title, text, note=None, after="explore"):
        self.message = {"title": title, "text": text, "note": note, "after": after}
        self.state = "message"

    def close_message(self):
        self.state = self.message["after"]
        self.message = None

    MENU_ITEMS = [("resume", "Resume"), ("howto", "How to Play"),
                  ("restart", "Restart Case"), ("exit", "Finish Game")]

    def open_menu(self):
        self.menu_return = self.state
        self.menu_index = 0
        self.state = "menu"

    def corner_menu_button(self):
        return pygame.Rect(846, 4, 108, 28)

    def menu_buttons(self):
        return [(key, label, pygame.Rect(360, 196 + i * 60, 240, 46))
                for i, (key, label) in enumerate(self.MENU_ITEMS)]

    def click_menu(self, pos):
        for key, _, rect in self.menu_buttons():
            if rect.collidepoint(pos):
                self.activate_menu(key)

    def activate_menu(self, key):
        if key == "resume":
            self.state = self.menu_return
        elif key == "howto":
            self.open_howto("menu")
        elif key == "restart":
            self.start_case(restart=True)
        elif key == "exit":
            self.state = self.menu_return
            self.finish_game()

    def draw_menu(self, s, mouse):
        shade_screen(s, 170)
        box = pygame.Rect(320, 100, 320, 370)
        panel(s, box, 240)
        draw_text(s, "PAUSED", self.font_big, GOLD, (WIDTH // 2, 140), center=True)
        draw_text(s, "Case %d: %s" % (self.case_index + 1, self.case["title"]),
                  self.font_small, LIGHT_GREY, (WIDTH // 2, 168), center=True)
        for i, (key, label, rect) in enumerate(self.menu_buttons()):
            color = RED if key in ("restart", "exit") else GOLD
            if i == self.menu_index:
                pygame.draw.rect(s, WHITE, rect.inflate(8, 8), 2, border_radius=8)
            self.draw_button(s, rect, label, mouse, color)
        draw_text(s, "Arrows + ENTER to choose  -  ESC: back", self.font_small, GREY,
                  (WIDTH // 2, 448), center=True)

    def menu_button(self):
        return pygame.Rect(478, 8, 34, 34)

    def file_button(self):
        return pygame.Rect(520, 8, 100, 34)

    def notebook_button(self):
        return pygame.Rect(628, 8, 160, 34)

    def accuse_button(self):
        return pygame.Rect(796, 8, 150, 34)

    def draw_button(self, s, rect, label, mouse, color=GOLD, enabled=True):
        if not enabled:
            pygame.draw.rect(s, DARK, rect, border_radius=6)
            pygame.draw.rect(s, (55, 56, 60), rect, 2, border_radius=6)
            draw_text(s, label, self.font, (80, 80, 85), rect.center, center=True)
            return
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(s, (40, 34, 20) if hover else DARK, rect, border_radius=6)
        pygame.draw.rect(s, color, rect, 2, border_radius=6)
        draw_text(s, label, self.font, WHITE if hover else color, rect.center, center=True)

    def draw_top_bar(self, s, mouse):
        pygame.draw.rect(s, BLACK, (0, 0, WIDTH, TOP_BAR))
        pygame.draw.line(s, GOLD, (0, TOP_BAR - 1), (WIDTH, TOP_BAR - 1), 1)
        room_name = self.case["rooms"][self.room]["name"]
        name_font = self.font_big if self.font_big.size(room_name)[0] < 300 else self.font_bold
        draw_text(s, room_name, name_font, GOLD, (18, 8 if name_font is self.font_big else 14))
        draw_text(s, "Case %d of %d" % (self.case_index + 1, len(CASES)),
                  self.font_small_bold, LIGHT_GREY, (325, 3))
        draw_text(s, "Clues: %d/%d  (need %d)" % (len(self.found), len(self.clues),
                                                 self.case["min_clues"]),
                  self.font_small, WHITE, (325, 18))
        draw_text(s, "Attempts left: %d" % self.attempts_left(),
                  self.font_small, LIGHT_GREY, (325, 33))
        self.draw_button(s, self.menu_button(), "", mouse)
        for k in range(3):
            pygame.draw.line(s, GOLD, (486, 17 + k * 8), (503, 17 + k * 8), 2)
        self.draw_button(s, self.file_button(), "File [F]", mouse)
        self.draw_button(s, self.notebook_button(), "Notebook [N]", mouse)
        self.draw_button(s, self.accuse_button(), "Accuse [A]", mouse, RED)

    def hotspots(self):
        room = self.case["rooms"][self.room]
        spots = []
        for spot in room["spots"]:
            entry = dict(spot)
            entry["rect"] = pygame.Rect(spot["rect"])
            entry["kind"] = "clue" if "clue" in spot else "look"
            spots.append(entry)
        for who, x, fy, behind in room["people"]:
            sus = self.suspects[who]
            # people behind a desk or table can only be clicked above it
            height = 110 if behind else 195
            spots.append({"rect": pygame.Rect(x - 40, fy - 195, 80, height), "kind": "talk", "feet": fy,
                          "who": who, "label": "%s, %s" % (sus["name"], sus["role"])})
        for door in room["doors"]:
            spots.append({"rect": pygame.Rect(door["rect"]), "kind": "door", "to": door["to"],
                          "label": "Go to: " + self.case["rooms"][door["to"]]["name"]})
        return spots

    def draw_prompt(self, s):
        spot = self.nearby_spot()
        if not spot:
            return
        pygame.draw.rect(s, (220, 220, 230), spot["rect"], 1, border_radius=4)
        verb = {"clue": "Examine: ", "look": "Examine: ", "talk": "Talk to ", "door": ""}[spot["kind"]]
        img = self.font_small_bold.render("[SPACE]  " + verb + spot["label"], True, WHITE)
        box = img.get_rect().inflate(16, 10)
        box.midbottom = (int(self.px), int(self.py) - 210)
        box.clamp_ip(pygame.Rect(4, TOP_BAR + 4, WIDTH - 8, HEIGHT))
        panel(s, box, 230, (190, 130, 255))
        s.blit(img, img.get_rect(center=box.center))

    def draw_hud(self, s):
        box = pygame.Rect(8, TOP_BAR + 8, 300, 32)
        panel(s, box, 200, GREY)
        draw_text(s, "Score: %d" % self.score, self.font_bold, YELLOW, (box.x + 12, box.y + 5))
        draw_text(s, "Bumps: %d   %s" % (self.bumps, self.difficulty.upper()), self.font_small,
                  LIGHT_GREY, (box.x + 172, box.y + 8))
        for text, x, y, age, color in self.floaters:
            img = self.font_big.render(text, True, color)
            img.set_alpha(int(255 * (1 - age / 1.2)))
            s.blit(img, img.get_rect(center=(int(x), int(y - age * 60))))

    def draw_scene(self, s, name, weather, shade_alpha=0):
        s.blit(self.scenes[name], (0, 0))
        self.draw_weather(s, weather)
        if shade_alpha:
            shade_screen(s, shade_alpha)

    def draw_weather(self, s, weather):
        for x, y, size, phase in self.particles:
            if weather == "rain":
                pygame.draw.line(s, (150, 160, 180), (x, y), (x - 4, y + 14), 1)
            elif weather == "snow":
                pygame.draw.circle(s, (235, 238, 245), (int(x + 12 * math.sin(phase)), int(y)), int(1 + size))
            else:
                color = BULB_COLORS[int(x) % len(BULB_COLORS)]
                w = int(4 * abs(math.cos(phase)) + 1)
                pygame.draw.rect(s, color, (int(x + 10 * math.sin(phase)), int(y), w, 4))

    def draw_case_scene(self, s, shade_alpha=0):
        self.draw_scene(s, self.theme["scene"], self.theme["weather"], shade_alpha)

    def draw_case_file(self, s):
        story = self.case["story"]
        folder = pygame.Rect(36, 34, 888, 548)
        pygame.draw.rect(s, (196, 166, 112), folder, border_radius=8)
        pygame.draw.rect(s, (196, 166, 112), (folder.x, folder.y - 22, 210, 30), border_radius=8)
        draw_text(s, "CASE FILE No. %d" % (self.case_index + 1), self.font_small_bold, INK,
                  (folder.x + 105, folder.y - 8), center=True)
        page = pygame.Rect(54, 50, 852, 500)
        pygame.draw.rect(s, (150, 124, 84), page.move(4, 4), border_radius=4)
        pygame.draw.rect(s, PAPER, page, border_radius=4)
        for y in range(page.y + 40, page.bottom - 10, 22):
            pygame.draw.line(s, (222, 210, 178), (page.x + 10, y), (page.right - 10, y), 1)
        # coffee ring and paper clip for a used look
        pygame.draw.circle(s, (205, 180, 140), (page.right - 70, page.bottom - 60), 30, 4)
        pygame.draw.rect(s, (150, 150, 158), (page.x + 30, page.y - 12, 14, 46), 3, border_radius=7)
        stamp = self.font_big.render("CONFIDENTIAL", True, (190, 40, 50))
        stamp = pygame.transform.rotate(stamp, 12)
        stamp.set_alpha(110)
        s.blit(stamp, (page.x + 120, page.bottom - 110))
        draw_text(s, self.case["title"], self.font_big, INK, (page.x + 60, page.y + 10))

        # left column: the stolen item and the client
        x = page.x + 24
        y = page.y + 56
        draw_text(s, story["item_label"], self.font_small_bold, (160, 30, 40), (x, y))
        picture = pygame.Rect(x, y + 24, 150, 130)
        pygame.draw.rect(s, (30, 30, 36), picture)
        self.draw_case_item(s, picture.inflate(-10, -10), story["art"])
        pygame.draw.rect(s, WHITE, picture, 4)
        pygame.draw.line(s, (170, 170, 170), (picture.x + 8, picture.y - 4), (picture.x + 40, picture.y + 10), 6)
        draw_text(s, story["item"], self.font_bold, INK, (x + 162, y + 22))
        ty = draw_text_block(s, story["about"], self.font_small, INK, x + 162, y + 46, 238, gap=1)
        ty = max(ty, picture.bottom) + 16
        draw_text(s, "THE CLIENT", self.font_small_bold, (160, 30, 40), (x, ty))
        draw_text_block(s, story["client"], self.font_small, INK, x, ty + 20, 400, gap=1)

        # right column: timeline and suspects
        rx = page.x + 446
        pygame.draw.line(s, (200, 180, 140), (rx - 18, page.y + 56), (rx - 18, page.bottom - 16), 2)
        y = page.y + 56
        draw_text(s, "WHAT WE KNOW", self.font_small_bold, (160, 30, 40), (rx, y))
        y += 22
        for time, event in story["timeline"]:
            pygame.draw.circle(s, (160, 30, 40), (rx + 4, y + 8), 4)
            draw_text(s, time, self.font_small_bold, INK, (rx + 14, y))
            y = draw_text_block(s, event, self.font_small, INK, rx + 62, y, 320, gap=0) + 3
        y += 10
        draw_text(s, "THE SUSPECTS", self.font_small_bold, (160, 30, 40), (rx, y))
        y += 22
        for sid, sus in self.suspects.items():
            pygame.draw.circle(s, sus["accent"], (rx + 5, y + 9), 5)
            name = "%s (%s)" % (sus["name"], sus["role"])
            draw_text(s, name, self.font_small_bold, INK, (rx + 16, y))
            y = draw_text_block(s, story["bios"][sid], self.font_small, (80, 64, 48), rx + 16, y + 16, 366, gap=0) + 4

        hint = "Press SPACE to start the investigation" if self.file_first else "Press SPACE or F to close"
        if int(self.t * 1.5) % 2 == 0:
            draw_text(s, hint, self.font_bold, WHITE, (WIDTH // 2, 588), center=True)

    def draw_message(self, s):
        box = pygame.Rect(80, 400, 800, 185)
        panel(s, box)
        draw_text(s, self.message["title"], self.font_big, GOLD, (box.x + 24, box.y + 16))
        y = draw_text_block(s, self.message["text"], self.font, WHITE,
                            box.x + 24, box.y + 58, box.w - 48)
        if self.message["note"]:
            draw_text(s, self.message["note"], self.font_bold, ORANGE, (box.x + 24, y + 6))
        draw_text(s, "SPACE to continue", self.font_small, GREY, (box.right - 140, box.bottom - 24))

    def draw_notebook(self, s):
        shade_screen(s, 150)
        page = pygame.Rect(30, 56, 900, 536)
        pygame.draw.rect(s, PAPER, page, border_radius=6)
        pygame.draw.rect(s, (138, 90, 43), page, 6, border_radius=6)
        pygame.draw.line(s, (200, 120, 120), (page.x + 18, page.y + 10), (page.x + 18, page.bottom - 10), 1)
        draw_text(s, "Detective's Notebook", self.font_big, INK, (page.x + 30, page.y + 14))
        draw_text(s, "%d of %d clues" % (len(self.found), len(self.clues)), self.font,
                  (110, 80, 50), (page.right - 150, page.y + 22))
        pygame.draw.line(s, (180, 150, 110), (page.x + 20, page.y + 56), (page.right - 20, page.y + 56), 2)
        if not self.found:
            draw_text(s, "No clues yet. Look around!", self.font, INK, (page.x + 30, page.y + 76))
        per_col = len(self.found) if len(self.found) <= 4 else (len(self.found) + 1) // 2
        col_w = 820 if len(self.found) <= 4 else 400
        y_start = page.y + 68
        y = y_start
        for i, cid in enumerate(self.found):
            if i == per_col:
                y = y_start
            x = page.x + 30 + (430 if i >= per_col else 0)
            title, text = self.clues[cid]
            draw_text(s, title, self.font_bold, (140, 30, 30), (x, y))
            y = draw_text_block(s, text, self.font_small, INK, x, y + 22, col_w, gap=2) + 10
        draw_text(s, "click or press N to close", self.font_small, (110, 80, 50),
                  (page.centerx, page.bottom - 16), center=True)

    def draw_howto(self, s):
        box = pygame.Rect(70, 30, 820, 540)
        panel(s, box, 240)
        draw_text(s, "How to Play", self.font_title, GOLD, (WIDTH // 2, 72), center=True)
        y = 112
        for i, (title, text) in enumerate(HOW_TO_PLAY):
            pygame.draw.circle(s, GOLD, (118, y + 12), 15)
            draw_text(s, str(i + 1), self.font_bold, BLACK, (118, y + 12), center=True)
            draw_text(s, title, self.font_bold, GOLD, (148, y))
            y = draw_text_block(s, text, self.font_small, WHITE, 148, y + 24, 700) + 12
        keys = "Arrows: walk   SPACE: examine / talk   ENTER: confirm   F: File   N: Notebook   A: Accuse   ESC: Menu"
        draw_text(s, keys, self.font_small_bold, LIGHT_GREY, (WIDTH // 2, y + 10), center=True)
        if int(self.t * 1.5) % 2 == 0:
            draw_text(s, "Press any key to continue", self.font_bold, WHITE, (WIDTH // 2, box.bottom - 26), center=True)

    def talk_options(self):
        topics = self.suspects[self.talk_id]["topics"]
        options = [(i, t["q"]) for i, t in enumerate(topics)
                   if t.get("req") is None or t["req"] in self.found]
        options.append((None, "Goodbye."))
        rects = [pygame.Rect(545, 345 + n * 38, 380, 32) for n in range(len(options))]
        return list(zip(options, rects))

    def click_talk(self, pos):
        for (idx, _), rect in self.talk_options():
            if rect.collidepoint(pos):
                self.choose_topic(idx)

    def choose_topic(self, idx):
        if idx is None:
            self.state = "explore"
            return
        self.talk_text = self.suspects[self.talk_id]["topics"][idx]["a"]
        if (self.talk_id, idx) not in self.asked:
            self.asked.add((self.talk_id, idx))
            self.add_points(POINTS_QUESTION, 480, 320)

    def draw_talk(self, s, mouse):
        sus = self.suspects[self.talk_id]
        box = pygame.Rect(20, 330, 920, 258)
        panel(s, box, 240)
        portrait = pygame.Rect(36, 346, 140, 226)
        vertical_gradient(s, portrait, (56, 58, 66), (24, 24, 28))
        s.set_clip(portrait)
        glow(s, (portrait.centerx, portrait.y + 60), 70, sus["accent"], 50)
        draw_person(s, portrait.centerx, portrait.bottom + 30, sus["style"], sus["accent"])
        s.set_clip(None)
        pygame.draw.rect(s, sus["accent"], portrait, 2, border_radius=6)
        draw_text(s, sus["name"], self.font_big, GOLD, (196, 344))
        draw_text(s, sus["role"], self.font_small, LIGHT_GREY, (196, 378))
        draw_text_block(s, '"' + self.talk_text + '"', self.font, WHITE, 196, 404, 330, gap=1)
        for n, ((idx, question), rect) in enumerate(self.talk_options()):
            hover = rect.collidepoint(mouse) or n == self.talk_index
            asked = (self.talk_id, idx) in self.asked
            color = WHITE if hover else (GREY if asked else GOLD)
            if hover:
                pygame.draw.rect(s, (45, 38, 22), rect, border_radius=5)
            pygame.draw.rect(s, color, rect, 1, border_radius=5)
            number = n + 1
            draw_text(s, "%d.  %s" % (number, question), self.font_small if idx is not None else self.font_bold,
                      color, (rect.x + 10, rect.y + 7))

    def start_accuse(self):
        if len(self.found) < self.case["min_clues"]:
            self.show_message("Not so fast!",
                              "You need at least %d clues before you can accuse anyone. "
                              "You have %d. Keep investigating."
                              % (self.case["min_clues"], len(self.found)))
            return
        self.accuse_step = "suspect"
        self.accuse_suspect = None
        self.accuse_index = 0
        self.selected = []
        self.state = "accuse"

    def suspect_cards(self):
        ids = list(self.suspects)
        w = min(200, (WIDTH - 60) // len(ids) - 16)
        total = len(ids) * w + (len(ids) - 1) * 16
        x0 = (WIDTH - total) // 2
        return [(sid, pygame.Rect(x0 + i * (w + 16), 140, w, 280)) for i, sid in enumerate(ids)]

    def evidence_buttons(self):
        buttons = []
        n = len(self.found)
        per_col = n if n <= 4 else (n + 1) // 2
        for i, cid in enumerate(self.found):
            if n > 4:
                rect = pygame.Rect(120 + (i // per_col) * 370, 140 + (i % per_col) * 56, 350, 46)
            else:
                rect = pygame.Rect(230, 150 + i * 58, 500, 46)
            buttons.append((cid, rect))
        return buttons

    def back_button(self):
        if self.accuse_step == "suspect":
            return pygame.Rect(380, 520, 200, 44)
        return pygame.Rect(250, 520, 200, 44)

    def confirm_button(self):
        return pygame.Rect(510, 520, 200, 44)

    def click_accuse(self, pos):
        if self.back_button().collidepoint(pos):
            if self.accuse_step == "evidence":
                self.accuse_step = "suspect"
                self.selected = []
            else:
                self.state = "explore"
            return
        if self.accuse_step == "suspect":
            for i, (sid, rect) in enumerate(self.suspect_cards()):
                if rect.collidepoint(pos):
                    self.accuse_index = i
                    self.accuse_suspect = sid
                    self.accuse_step = "evidence"
                    self.evidence_index = 0
            return
        for i, (cid, rect) in enumerate(self.evidence_buttons()):
            if rect.collidepoint(pos):
                self.evidence_index = i
                self.toggle_evidence(cid)
        if (self.confirm_button().collidepoint(pos)
                and len(self.selected) == self.case["evidence"]):
            self.judge(self.accuse_suspect, self.selected)

    def toggle_evidence(self, cid):
        if cid in self.selected:
            self.selected.remove(cid)
        else:
            self.selected.append(cid)
            if len(self.selected) > self.case["evidence"]:
                self.selected.pop(0)

    def judge(self, sid, chosen):
        strong = self.case["strong"]
        if sid == self.case["culprit"] and all(c in strong for c in chosen):
            self.result = "win"
            self.bonus = POINTS_SOLVED + 100 * self.attempts_left()
            self.score += self.bonus
            self.record_highscore()
            stars = max(1, 3 - self.mistakes)
            if len(self.stars) > self.case_index:
                # case was replayed from the menu: keep the better result
                self.stars[self.case_index] = max(self.stars[self.case_index], stars)
            else:
                self.stars.append(stars)
            self.state = "ending"
            self.log("Case %d solved! Culprit: %s, bonus %d, score %d" % (
                self.case_index + 1, self.suspects[sid]["name"], self.bonus, self.score))
            return
        self.mistakes += 1
        self.add_points(POINTS_WRONG, 480, 300)
        self.log("Wrong accusation against %s (%d attempts left)" % (self.suspects[sid]["name"],
                                                                    self.attempts_left()))
        if sid != self.case["culprit"]:
            title = "Wrong suspect!"
            text = self.suspects[sid]["innocent"]
        else:
            title = "Not enough proof!"
            weak = [c for c in chosen if c not in strong][0]
            text = self.case["weak_text"].get(
                weak, "'%s' does not prove anything against %s."
                % (self.clues[weak][0], self.suspects[sid]["name"]))
        if self.attempts_left() <= 0:
            self.result = "lose"
            self.record_highscore()
            self.log("Case %d lost - the culprit escaped" % (self.case_index + 1))
            self.show_message(title, text, "That was your last attempt...", after="ending")
        else:
            self.show_message(title, text, "Attempts left: %d" % self.attempts_left())

    def draw_accuse(self, s, mouse):
        shade_screen(s, 210)
        if self.accuse_step == "suspect":
            draw_text(s, self.case["question"], self.font_big, GOLD, (WIDTH // 2, 95), center=True)
            for i, (sid, rect) in enumerate(self.suspect_cards()):
                sus = self.suspects[sid]
                hover = rect.collidepoint(mouse) or i == self.accuse_index
                vertical_gradient(s, rect, (52, 54, 62) if hover else (34, 34, 40), (14, 14, 18))
                pygame.draw.rect(s, sus["accent"] if hover else GREY, rect, 2, border_radius=8)
                s.set_clip(rect)
                if hover:
                    glow(s, (rect.centerx, rect.y + 70), 70, sus["accent"], 60)
                draw_person(s, rect.centerx, rect.y + 215, sus["style"], sus["accent"])
                s.set_clip(None)
                name_font = self.font_bold if self.font_bold.size(sus["name"])[0] < rect.w - 8 else self.font_small_bold
                draw_text(s, sus["name"], name_font, WHITE, (rect.centerx, rect.y + 238), center=True)
                draw_text(s, sus["role"], self.font_small, LIGHT_GREY, (rect.centerx, rect.y + 260), center=True)
            draw_text(s, "Arrows: choose   ENTER: accuse this person   Attempts left: %d"
                      % self.attempts_left(), self.font, LIGHT_GREY, (WIDTH // 2, 470), center=True)
            self.draw_button(s, self.back_button(), "Cancel", mouse, GREY)
            return
        need = self.case["evidence"]
        name = self.suspects[self.accuse_suspect]["name"]
        title = ("Which clue proves that %s did it?" % name if need == 1 else
                 "Choose %d clues that prove %s did it" % (need, name))
        draw_text(s, title, self.font_big, GOLD, (WIDTH // 2, 95), center=True)
        for i, (cid, rect) in enumerate(self.evidence_buttons()):
            chosen = cid in self.selected
            hover = rect.collidepoint(mouse) or i == self.evidence_index
            fill = (70, 25, 30) if chosen else ((45, 38, 22) if hover else DARK)
            pygame.draw.rect(s, fill, rect, border_radius=6)
            pygame.draw.rect(s, RED if chosen else (WHITE if hover else GOLD), rect, 2, border_radius=6)
            label = ("> " if chosen else "") + self.clues[cid][0]
            draw_text(s, label, self.font_bold, WHITE if chosen or hover else GOLD,
                      rect.center, center=True)
        draw_text(s, "SPACE: pick clue   ENTER: accuse   Selected: %d / %d   Attempts left: %d"
                  % (len(self.selected), need, self.attempts_left()),
                  self.font, LIGHT_GREY, (WIDTH // 2, 470), center=True)
        self.draw_button(s, self.back_button(), "Back", mouse, GREY)
        self.draw_button(s, self.confirm_button(), "Accuse!", mouse, RED,
                         enabled=len(self.selected) == need)

    def draw_case_intro(self, s):
        self.draw_case_scene(s, 40)
        box = pygame.Rect(90, 24, 780, 440)
        panel(s, box, 225)
        draw_text(s, "CASE %d" % (self.case_index + 1), self.font_bold, LIGHT_GREY,
                  (WIDTH // 2, 52), center=True)
        draw_text(s, self.case["title"], self.font_title, GOLD, (WIDTH // 2, 94), center=True)
        y = draw_text_block(s, self.case["intro"], self.font, WHITE, 125, 135, 710)
        y += 12
        draw_text(s, "Rules for this case:", self.font_bold, GOLD, (125, y))
        if self.case["glow"] >= 1:
            glow_rule = "Clues glow brightly."
        elif self.case["glow"] > 0:
            glow_rule = "Clues only glow faintly."
        else:
            glow_rule = "Clues do NOT glow - look at everything!"
        evidence = self.case["evidence"]
        attempts = self.case["attempts"]
        rules = [
            "Find at least %d clues before you may accuse someone." % self.case["min_clues"],
            "Pick %d clue%s as evidence when you accuse." % (evidence, "" if evidence == 1 else "s"),
            "You have only 1 attempt - no second chance!" if attempts == 1
            else "You have %d attempts." % attempts,
            glow_rule,
            "Watch out for the %s! Every bump costs 50 points." % self.theme["enemy_name"],
        ]
        for rule in rules:
            y += 24
            pygame.draw.circle(s, GOLD, (135, y + 10), 3)
            draw_text(s, rule, self.font_small, WHITE, (148, y + 2))
        if int(self.t * 1.5) % 2 == 0:
            draw_text(s, "Press any key to open the case file", self.font_bold, WHITE,
                      (WIDTH // 2, 575), center=True)

    def end_button_rect(self):
        return pygame.Rect(250, 520, 220, 44)

    def end_button_pressed(self):
        if self.result == "win":
            if self.case_index + 1 < len(CASES):
                self.case_index += 1
                self.start_case()
            else:
                self.log("All cases solved!")
                self.finish_game()
        else:
            self.start_case(restart=True)

    def exit_button_rect(self):
        return pygame.Rect(490, 520, 220, 44)

    def draw_ending(self, s, mouse):
        self.draw_case_scene(s, 120)
        box = pygame.Rect(100, 24, 760, 482)
        panel(s, box, 230)
        if self.result == "win":
            draw_text(s, "CASE CLOSED", self.font_title, GOLD, (WIDTH // 2, 74), center=True)
            for i in range(3):
                draw_star(s, (WIDTH // 2 - 60 + i * 60, 134), i < self.stars[self.case_index])
            draw_text(s, self.case["confession"], self.font_big, WHITE, (WIDTH // 2, 184), center=True)
            y = draw_text_block(s, self.case["solution"], self.font, LIGHT_GREY,
                                box.x + 36, 214, box.w - 72, gap=2)
            draw_text(s, "What happened next:", self.font_small_bold, GOLD, (box.x + 36, y + 8))
            y = draw_text_block(s, self.case["story"]["epilogue"], self.font_small, WHITE,
                                box.x + 36, y + 26, box.w - 72, gap=2)
            draw_text(s, "Clues: %d of %d     Case bonus: +%d     Score: %d"
                      % (len(self.found), len(self.clues), self.bonus, self.score),
                      self.font_small_bold, YELLOW, (WIDTH // 2, y + 12), center=True)
            last = self.case_index + 1 == len(CASES)
            label = "Final results" if last else "Next case"
        else:
            draw_text(s, "THE CULPRIT ESCAPED", self.font_title, RED, (WIDTH // 2, 85), center=True)
            draw_text(s, "You ran out of attempts.", self.font_big, WHITE, (WIDTH // 2, 160), center=True)
            draw_text(s, "Score: %d" % self.score, self.font_big, YELLOW, (WIDTH // 2, 215), center=True)
            draw_text(s, "High score: %d" % self.highscore, self.font_small_bold, LIGHT_GREY,
                      (WIDTH // 2, 250), center=True)
            tip = ("Tip: Read your notebook carefully and ask every suspect about every clue. "
                   "Who had a reason? Who had the chance? And who is lying?")
            draw_text_block(s, tip, self.font, LIGHT_GREY, box.x + 60, 290, box.w - 120)
            draw_text(s, "Trying again resets the points of this case.", self.font_small, GREY,
                      (WIDTH // 2, 470), center=True)
            label = "Try again"
        self.draw_button(s, self.end_button_rect(), label + " [Enter]", mouse)
        self.draw_button(s, self.exit_button_rect(), "Finish game [X]", mouse, RED)

    # ------------------------------------------------- welcome and final screens
    # game_node uses these two screens for phase 1 (Welcome) and phase 3 (Final)

    def rank(self):
        total, best = sum(self.stars), 3 * len(CASES)
        if total == best:
            return "Master Detective"
        if total >= best * 0.6:
            return "Senior Inspector"
        return "Rookie Detective"

    def draw_welcome(self, s, user):
        """Phase 1: title screen that greets the player (user = None while we still wait)."""
        self.draw_scene(s, "city", "rain")
        panel(s, (130, 24, 700, 250), 215)
        draw_text(s, "SHADOW DETECTIVE", self.font_title, GOLD, (WIDTH // 2, 74), center=True)
        draw_text(s, "Five cases. One detective. Nobody tells the whole truth.",
                  self.font, LIGHT_GREY, (WIDTH // 2, 120), center=True)
        for i, case in enumerate(CASES):
            draw_text(s, "Case %d: %s" % (i + 1, case["title"]), self.font_small,
                      WHITE, (WIDTH // 2, 152 + i * 21), center=True)
        draw_text(s, "High score: %d" % self.highscore, self.font_small_bold, YELLOW,
                  (WIDTH // 2, 258), center=True)
        box = pygame.Rect(400, 292, 520, 190)
        panel(s, box, 225, (190, 130, 255))
        level = "Difficulty: %s   (service /difficulty: easy, medium or hard)" % self.difficulty.upper()
        if user is None:
            dots = "." * (1 + int(self.t * 2) % 3)
            draw_text(s, "Waiting for the player" + dots, self.font_big, WHITE, (box.centerx, box.y + 46), center=True)
            draw_text_block(s, "Start info_user_node in a terminal and enter your full name, "
                               "username, age and difficulty.", self.font, LIGHT_GREY, box.x + 30, box.y + 82, box.w - 60)
            draw_text(s, level, self.font_small_bold, YELLOW, (box.centerx, box.y + 160), center=True)
            return
        draw_text(s, "Hello, %s!" % user["name"], self.font_big, WHITE, (box.centerx, box.y + 36), center=True)
        draw_text(s, "User data received", self.font_small_bold, (150, 230, 160), (box.centerx, box.y + 70), center=True)
        draw_text(s, "Username: %s   -   Age: %d" % (user["username"], user["age"]), self.font,
                  LIGHT_GREY, (box.centerx, box.y + 96), center=True)
        draw_text(s, level, self.font_small_bold, YELLOW, (box.centerx, box.y + 126), center=True)
        if int(self.t * 1.5) % 2 == 0:
            draw_text(s, "Press any key in the control terminal to start", self.font_bold, WHITE,
                      (box.centerx, box.y + 162), center=True)

    def draw_final(self, s, user, points, star_bonus, final_score, published, percent=None):
        """Phase 3: final score, player data and whether the result was published."""
        self.draw_scene(s, "city", "rain", 120)
        box = pygame.Rect(130, 20, 700, 560)
        panel(s, box, 235)
        draw_text(s, "FINAL", self.font_small_bold, LIGHT_GREY, (WIDTH // 2, 44), center=True)
        draw_text(s, "GAME OVER", self.font_title, GOLD, (WIDTH // 2, 86), center=True)
        if user:
            draw_text(s, "Detective %s  (username: %s, age: %d)" % (user["name"], user["username"], user["age"]),
                      self.font, WHITE, (WIDTH // 2, 130), center=True)
        for i, case in enumerate(CASES):
            y = 172 + i * 34
            draw_text(s, "Case %d: %s" % (i + 1, case["title"]), self.font, WHITE, (190, y - 10))
            if i < len(self.stars):
                for k in range(3):
                    draw_star(s, (660 + k * 36, y), k < self.stars[i], 14)
            else:
                draw_text(s, "not solved", self.font_small, GREY, (660, y - 8))
        draw_text(s, "Points %d   +   %d stars x %d   =" % (points, sum(self.stars), STAR_BONUS),
                  self.font, LIGHT_GREY, (WIDTH // 2, 352), center=True)
        draw_text(s, "FINAL SCORE: %d" % final_score, self.font_title, YELLOW, (WIDTH // 2, 398), center=True)
        rank = "Rank: %s" % self.rank()
        if percent is not None:
            rank += "   -   %d%% of the maximum score" % percent
        draw_text(s, rank, self.font_bold, WHITE, (WIDTH // 2, 444), center=True)
        if published:
            draw_text(s, "Result published on /result_information", self.font_small_bold,
                      (150, 230, 160), (WIDTH // 2, 478), center=True)
        draw_text(s, "ENTER: play again        X: quit", self.font_bold, WHITE, (WIDTH // 2, 540), center=True)

    def draw(self):
        s = self.screen
        mouse = pygame.mouse.get_pos()
        if self.state == "menu":
            # draw the paused screen underneath, then the menu on top
            self.state = self.menu_return
            self.draw()
            self.state = "menu"
            self.draw_menu(s, mouse)
            return
        if self.state in ("case_intro", "case_file", "ending"):
            self.draw_screen(s, mouse)
            self.draw_button(s, self.corner_menu_button(), "Menu [Esc]", mouse, GREY)
            return
        self.draw_screen(s, mouse)

    def draw_screen(self, s, mouse):
        if self.state == "case_intro":
            self.draw_case_intro(s)
        elif self.state == "case_file":
            self.draw_case_scene(s, 150)
            self.draw_case_file(s)
        elif self.state == "ending":
            self.draw_ending(s, mouse)
        elif self.state == "howto" and self.howto_return != "explore":
            self.draw_case_scene(s, 100)
            self.draw_howto(s)
        else:
            self.draw_room(s)
            self.draw_top_bar(s, mouse)
            self.draw_hud(s)
            if self.state == "explore":
                self.draw_prompt(s)
            elif self.state == "message":
                self.draw_message(s)
            elif self.state == "notebook":
                self.draw_notebook(s)
            elif self.state == "talk":
                self.draw_talk(s, mouse)
            elif self.state == "accuse":
                self.draw_accuse(s, mouse)
            elif self.state == "howto":
                shade_screen(s, 120)
                self.draw_howto(s)
