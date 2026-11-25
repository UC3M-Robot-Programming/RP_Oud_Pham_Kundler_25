"""Room artist: draws the walls, floors, doors and furniture of every room.

DetectiveGame inherits from RoomArtist, so these methods can use the game state
(found clues, the time for animations, the player position, ...).
"""
import math
import random

import pygame

from robot_info.display import (
    BLACK, BRASS, BULB_COLORS, DARK, FLOOR_Y, GOLD, GREEN_LIGHT, GREY, HEIGHT, INK,
    LIGHT_GREY, ORANGE, PAPER, RED, TOP_BAR, WHITE, WIDTH, WOOD,
    WOOD_DARK, YELLOW)
from robot_info.renderer import (
    alpha_ellipse, alpha_polygon, draw_text, glow, lerp_color, shade, vertical_gradient)
from robot_info.sprites import (
    draw_chandelier, draw_crate, draw_enemy, draw_person, draw_shadow,
    draw_shelf_of_books, draw_string_lights, draw_suitcase, draw_tick, draw_wall_lamp)


class RoomArtist:
    def draw_room(self, s):
        room = self.case["rooms"][self.room]
        self.draw_wall(s, room)
        self.draw_floor(s, room)
        strength = self.case["glow"]
        if strength > 0:
            for spot in room["spots"]:
                if "clue" in spot and spot["clue"] not in self.found:
                    r = pygame.Rect(spot["rect"])
                    radius = min(60, max(30, min(r.w, r.h) // 2 + 15))
                    alpha = (55 + 35 * math.sin(self.t * 3)) * strength
                    glow(s, r.center, radius, spot.get("color", GOLD), alpha)
        for who, x, fy, behind in room["people"]:
            if behind:
                sus = self.suspects[who]
                draw_person(s, x, fy, sus["style"], sus["accent"])
        getattr(self, "draw_" + room["draw"])(s)
        for door in room["doors"]:
            self.draw_door(s, door["rect"], door["sign"], door.get("ajar", False))
        for spot in room["spots"]:
            if "clue" in spot and spot["clue"] in self.found:
                draw_tick(s, pygame.Rect(spot["rect"]).topright)
        # people, obstacles and the player are drawn from back to front
        actors = []
        for who, x, fy, behind in room["people"]:
            if not behind:
                actors.append((fy, "person", (who, x, fy)))
        for e in self.enemies:
            actors.append((e[1], "enemy", e))
        actors.append((self.py, "player", None))
        for _, kind, data in sorted(actors, key=lambda a: a[0]):
            if kind == "person":
                who, x, fy = data
                sus = self.suspects[who]
                draw_shadow(s, x, fy)
                draw_person(s, x, fy, sus["style"], sus["accent"])
            elif kind == "enemy":
                draw_enemy(s, self.theme["enemy"], data[0], data[1], data[4], data[2])
            else:
                self.draw_player(s)
        self.draw_atmosphere(s)

    def draw_player(self, s):
        x, y = int(self.px), int(self.py)
        if self.invulnerable > 0 and int(self.invulnerable * 12) % 2 == 0:
            return
        color = self.player_color            # set by the ROS parameter change_player_color
        alpha_ellipse(s, color, 90, (x - 46, y - 12, 92, 24))
        pygame.draw.ellipse(s, shade(color, 70), (x - 40, y - 9, 80, 18), 2)
        draw_person(s, x, y, "detective", RED, body=color, step=math.sin(self.walk))

    def draw_atmosphere(self, s):
        # floating dust in the light
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x, y, phase in self.motes:
            a = int(40 + 30 * math.sin(phase * 2))
            pygame.draw.circle(layer, (230, 225, 200, a), (int(x + 6 * math.sin(phase)), int(y)), 1)
        s.blit(layer, (0, 0))
        # colour mood of the case
        tint = self.theme["tint"]
        if self.case_index not in self.tints:
            t = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            t.fill(tint)
            self.tints[self.case_index] = t
        s.blit(self.tints[self.case_index], (0, 0))
        if self.theme.get("lightning") and self.flash > 0.3:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((210, 220, 255, int(45 * self.flash)))
            s.blit(flash, (0, 0))
        s.blit(self.vignette, (0, 0))

    def draw_wall(self, s, room):
        wall = room["wall"]
        style = room.get("wall_style", self.theme["wall_style"])
        top = TOP_BAR + 22
        pygame.draw.rect(s, wall, (0, TOP_BAR, WIDTH, FLOOR_Y - TOP_BAR))
        if style == "wallpaper":
            for x in range(0, WIDTH, 32):
                pygame.draw.rect(s, shade(wall, 7), (x, top, 14, 300 - top))
                for y in range(top + 20, 290, 44):
                    pygame.draw.polygon(s, shade(wall, 14), [(x + 23, y - 5), (x + 28, y),
                                                             (x + 23, y + 5), (x + 18, y)])
        if style in ("wainscot", "wallpaper"):
            pygame.draw.rect(s, shade(wall, -14), (0, 300, WIDTH, FLOOR_Y - 300))
            pygame.draw.rect(s, shade(wall, 18), (0, 296, WIDTH, 6))
            for x in range(14, WIDTH, 112):
                pygame.draw.rect(s, shade(wall, -26), (x, 314, 92, 100), 2)
                pygame.draw.line(s, shade(wall, 4), (x + 2, 413), (x + 91, 413), 1)
        elif style == "brick":
            for row, y in enumerate(range(top, FLOOR_Y, 22)):
                pygame.draw.line(s, shade(wall, -14), (0, y), (WIDTH, y), 2)
                off = 0 if row % 2 == 0 else 30
                for x in range(off, WIDTH, 60):
                    pygame.draw.line(s, shade(wall, -14), (x, y), (x, y + 22), 2)
                    if (x * 7 + row * 13) % 5 == 0:
                        pygame.draw.rect(s, shade(wall, 6), (x + 2, y + 2, 56, 18))
        elif style == "train":
            pygame.draw.rect(s, shade(wall, -18), (0, 310, WIDTH, FLOOR_Y - 310))
            pygame.draw.rect(s, BRASS, (0, 306, WIDTH, 4))
            for x in range(0, WIDTH, 120):
                pygame.draw.line(s, shade(wall, -12), (x, top), (x, FLOOR_Y), 2)
                pygame.draw.line(s, shade(wall, 10), (x + 3, top), (x + 3, FLOOR_Y), 1)
            # curved ceiling and luggage rack
            pygame.draw.rect(s, shade(wall, -30), (0, TOP_BAR, WIDTH, 26))
            pygame.draw.ellipse(s, shade(wall, -10), (-60, TOP_BAR - 20, WIDTH + 120, 70))
            for x in range(0, WIDTH, 6):
                pygame.draw.line(s, (120, 100, 60), (x, 92), (x, 98), 1)
            pygame.draw.line(s, BRASS, (0, 92), (WIDTH, 92), 3)
            pygame.draw.line(s, BRASS, (0, 99), (WIDTH, 99), 2)
        elif style == "metal":
            for y in range(top, FLOOR_Y, 90):
                for x in range(0, WIDTH, 160):
                    pygame.draw.rect(s, shade(wall, -10), (x, y, 160, 90), 2)
                    for rx, ry in ((x + 8, y + 8), (x + 152, y + 8), (x + 8, y + 82), (x + 152, y + 82)):
                        pygame.draw.circle(s, shade(wall, 20), (rx, ry), 3)
        elif style == "tent":
            second = room.get("wall2", shade(wall, 40))
            for i, x in enumerate(range(0, WIDTH, 60)):
                color = wall if i % 2 == 0 else second
                pygame.draw.polygon(s, color, [(x, TOP_BAR), (x + 60, TOP_BAR), (x + 64, FLOOR_Y), (x - 4, FLOOR_Y)])
                pygame.draw.line(s, shade(color, -25), (x + 58, TOP_BAR), (x + 62, FLOOR_Y), 3)
            for x in range(0, WIDTH, 60):
                pygame.draw.circle(s, shade(wall, -25), (x + 30, TOP_BAR + 6), 30, 0,
                                   draw_bottom_left=True, draw_bottom_right=True)
                pygame.draw.circle(s, GOLD, (x + 30, TOP_BAR + 36), 3)
        elif style == "drape":
            for x in range(0, WIDTH, 24):
                pygame.draw.line(s, shade(wall, 10 if (x // 24) % 2 else -8), (x, TOP_BAR), (x + 6, FLOOR_Y), 8)
            rng = random.Random(7)
            for _ in range(40):
                sx, sy = rng.randint(0, WIDTH), rng.randint(TOP_BAR + 30, 300)
                a = 120 + int(100 * math.sin(self.t * 2 + sx))
                pygame.draw.circle(s, (min(255, a + 60), min(255, a + 30), 80), (sx, sy), 2)
        elif style == "night":
            vertical_gradient(s, (0, TOP_BAR, WIDTH, FLOOR_Y - TOP_BAR), (8, 8, 26), (46, 24, 56))
            rng = random.Random(11)
            for _ in range(80):
                sx, sy = rng.randint(0, WIDTH), rng.randint(TOP_BAR, 330)
                twinkle = 150 + int(90 * math.sin(self.t * 3 + sx * 0.1))
                pygame.draw.circle(s, (twinkle, twinkle, min(255, twinkle + 30)), (sx, sy), 1)
            return
        if style not in ("tent", "drape"):
            pygame.draw.rect(s, shade(wall, -22), (0, TOP_BAR, WIDTH, 22))
            pygame.draw.line(s, shade(wall, 22), (0, top), (WIDTH, top), 2)
            pygame.draw.line(s, shade(wall, -30), (0, top + 3), (WIDTH, top + 3), 1)

    def draw_floor(self, s, room):
        color = room.get("floor_color", self.theme["floor_color"])
        style = room.get("floor", self.theme["floor"])
        pygame.draw.rect(s, color, (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y))
        rows = [430, 442, 457, 476, 500, 530, 566, 600]
        if style == "tiles":
            for i, y in enumerate(rows):
                pygame.draw.line(s, shade(color, 12), (0, y), (WIDTH, y), 2)
            for i in range(-7, 8):
                pygame.draw.line(s, shade(color, 12), (480 + i * 85, FLOOR_Y), (480 + i * 230, HEIGHT), 2)
        elif style in ("wood", "planks"):
            rng = random.Random(2)
            step = 1 if style == "wood" else 2
            for i in range(0, len(rows) - 1, step):
                y1 = rows[i]
                y2 = rows[min(i + step, len(rows) - 1)]
                tone = shade(color, rng.randint(-6, 6))
                pygame.draw.rect(s, tone, (0, y1, WIDTH, y2 - y1))
                pygame.draw.line(s, shade(color, -18), (0, y1), (WIDTH, y1), 2)
                pygame.draw.line(s, shade(color, 10), (0, y1 + 2), (WIDTH, y1 + 2), 1)
                x = rng.randint(0, 200)
                while x < WIDTH:
                    pygame.draw.line(s, shade(color, -18), (x, y1), (x, y2), 2)
                    x += rng.randint(160, 320)
        elif style == "carpet":
            rug = [(130, 444), (830, 444), (930, 596), (30, 596)]
            pygame.draw.polygon(s, shade(color, 14), rug)
            pygame.draw.polygon(s, (150, 118, 66), rug, 3)
            inner = [(160, 452), (800, 452), (888, 588), (72, 588)]
            pygame.draw.polygon(s, (150, 118, 66), inner, 1)
            for k in range(12):
                f = (k + 0.5) / 12
                dx = 160 + (800 - 160) * f
                pygame.draw.polygon(s, shade(color, 30), [(dx, 456), (dx + 6, 462), (dx, 468), (dx - 6, 462)])
        elif style == "concrete":
            rng = random.Random(8)
            for _ in range(12):
                x, y = rng.randint(0, WIDTH), rng.randint(FLOOR_Y + 10, HEIGHT)
                alpha_ellipse(s, BLACK, 40, (x, y, rng.randint(40, 120), rng.randint(10, 26)))
            for _ in range(5):
                x, y = rng.randint(0, WIDTH), rng.randint(FLOOR_Y, HEIGHT - 30)
                pygame.draw.lines(s, shade(color, -16), False,
                                  [(x, y), (x + 20, y + 12), (x + 26, y + 30), (x + 50, y + 38)], 1)
        elif style == "sawdust":
            rng = random.Random(6)
            for _ in range(500):
                x, y = rng.randint(0, WIDTH), rng.randint(FLOOR_Y, HEIGHT)
                pygame.draw.circle(s, shade(color, rng.randint(-25, 25)), (x, y), 1)
        elif style == "grass":
            rng = random.Random(12)
            for _ in range(260):
                x, y = rng.randint(0, WIDTH), rng.randint(FLOOR_Y + 4, HEIGHT)
                h = 4 + (y - FLOOR_Y) // 20
                pygame.draw.line(s, shade(color, rng.randint(0, 25)), (x, y), (x + rng.randint(-3, 3), y - h), 1)
        elif style == "stone":
            for i, y in enumerate(rows):
                pygame.draw.line(s, shade(color, -14), (0, y), (WIDTH, y), 2)
                off = (i * 53) % 140
                y2 = rows[min(i + 1, len(rows) - 1)]
                for x in range(off, WIDTH, 140 + i * 12):
                    pygame.draw.line(s, shade(color, -14), (x, y), (x, y2), 2)
        pygame.draw.rect(s, DARK, (0, FLOOR_Y - 8, WIDTH, 8))
        pygame.draw.line(s, shade(room["wall"], 15), (0, FLOOR_Y - 8), (WIDTH, FLOOR_Y - 8), 1)

    def draw_door(self, s, rect, label, ajar=False):
        r = pygame.Rect(rect)
        kind = self.theme["door"]
        if kind == "flap":
            pygame.draw.rect(s, (14, 10, 16), r)
            glow(s, r.center, 60, (255, 205, 120), 40)
            pygame.draw.polygon(s, (150, 40, 50), [r.topleft, (r.x + 40, r.y), (r.x + 20, r.bottom), r.bottomleft])
            pygame.draw.polygon(s, (220, 205, 185), [r.topright, (r.right - 40, r.y), (r.right - 20, r.bottom), r.bottomright])
            pygame.draw.line(s, GOLD, (r.x + 6, r.centery), (r.x + 30, r.centery + 10), 3)
            pygame.draw.line(s, GOLD, (r.right - 6, r.centery), (r.right - 30, r.centery + 10), 3)
        elif kind == "train":
            pygame.draw.rect(s, (70, 48, 34), r)
            pygame.draw.rect(s, BRASS, r, 3)
            pane = pygame.Rect(r.x + 20, r.y + 18, r.w - 40, 70)
            pygame.draw.rect(s, (30, 40, 60), pane, border_radius=6)
            pygame.draw.rect(s, BRASS, pane, 2, border_radius=6)
            pygame.draw.polygon(s, (200, 210, 225), [pane.bottomleft, (pane.x + 18, pane.bottom), (pane.x, pane.bottom - 12)])
            pygame.draw.rect(s, BRASS, (r.right - 18, r.centery, 5, 40), border_radius=2)
            pygame.draw.rect(s, shade((70, 48, 34), -15), (r.x + 14, r.y + 110, r.w - 28, 70), 2)
        else:
            pygame.draw.rect(s, BLACK, r)
            if ajar:
                pygame.draw.polygon(s, (58, 52, 46), [r.topleft, (r.x + 65, r.y + 10),
                                                      (r.x + 65, r.bottom - 5), r.bottomleft])
                alpha_polygon(s, YELLOW, 80, [(r.x + 65, r.y + 10), r.topright,
                                              r.bottomright, (r.x + 65, r.bottom - 5)])
            else:
                pygame.draw.rect(s, (58, 50, 42), r.inflate(-12, -8))
                pygame.draw.rect(s, (48, 41, 35), (r.x + 18, r.y + 20, r.w - 36, 60))
                pygame.draw.rect(s, (48, 41, 35), (r.x + 18, r.y + 100, r.w - 36, 80))
                pygame.draw.line(s, (70, 62, 54), (r.x + 18, r.y + 20), (r.right - 18, r.y + 20), 1)
                pygame.draw.circle(s, LIGHT_GREY, (r.right - 20, r.centery + 10), 4)
            pygame.draw.rect(s, GREY, r, 4)
        sign = pygame.Rect(0, 0, 130, 20)
        sign.midbottom = (r.centerx, r.y - 6)
        pygame.draw.rect(s, DARK, sign)
        pygame.draw.rect(s, GREY, sign, 1)
        draw_text(s, label, self.font_tiny, LIGHT_GREY, sign.center, center=True)

    def draw_window(self, s, rect, lightning=False, mountains=False):
        """A window looking out into the weather of the current case."""
        r = pygame.Rect(rect)
        sky_top, sky_bottom = (22, 28, 44), (40, 48, 66)
        if lightning and self.flash > 0:
            sky_top = lerp_color(sky_top, (200, 210, 230), self.flash)
            sky_bottom = lerp_color(sky_bottom, (200, 210, 230), self.flash)
        vertical_gradient(s, r, sky_top, sky_bottom)
        s.set_clip(r)
        if mountains:
            peaks = [(r.x - 10, r.bottom - 20), (r.x + r.w * 0.3, r.y + 30), (r.x + r.w * 0.55, r.bottom - 40),
                     (r.x + r.w * 0.8, r.y + 20), (r.right + 10, r.bottom - 30)]
            pygame.draw.polygon(s, (58, 66, 90), peaks + [r.bottomright, r.bottomleft])
            for px, py in peaks[1:4:2]:
                pygame.draw.polygon(s, (220, 225, 235), [(px, py), (px - 16, py + 18), (px + 16, py + 18)])
            pygame.draw.rect(s, (200, 206, 218), (r.x, r.bottom - 16, r.w, 16))
        weather = self.theme["weather"]
        for i in range(max(6, r.w // 10)):
            if weather == "snow":
                x = r.x + (i * 37 + 10 * math.sin(self.t + i)) % r.w
                y = r.y + (i * 53 + self.t * (25 + i % 3 * 10)) % r.h
                pygame.draw.circle(s, (235, 238, 245), (int(x), int(y)), 1 + i % 2)
            else:
                x = r.x + (i * 37) % r.w + 10
                y = r.y + (i * 53 + self.t * 320) % (r.h + 20) - 10
                pygame.draw.line(s, (120, 130, 150), (x, y), (x - 3, y + 11), 1)
        alpha_polygon(s, (255, 255, 255), 18, [r.topleft, (r.x + r.w // 3, r.y), (r.x, r.y + r.h // 2)])
        s.set_clip(None)

    def draw_window_rain(self, s, rect, lightning=False):
        self.draw_window(s, rect, lightning)

    def draw_hall(self, s):
        draw_chandelier(s, 480, 100)
        pygame.draw.rect(s, (24, 25, 29), (400, 190, 160, 240))
        self.draw_window(s, (412, 205, 56, 130))
        self.draw_window(s, (492, 205, 56, 130))
        pygame.draw.rect(s, GREY, (400, 190, 160, 240), 4)
        pygame.draw.line(s, GREY, (480, 190), (480, 430), 4)
        pygame.draw.rect(s, BRASS, (470, 340, 6, 30))
        pygame.draw.rect(s, BRASS, (484, 340, 6, 30))
        draw_text(s, "CITY MUSEUM OF GREYHAVEN", self.font_small, LIGHT_GREY, (480, 165), center=True)

        # key board - one hook is empty
        pygame.draw.rect(s, WOOD, (185, 170, 160, 90))
        pygame.draw.rect(s, WOOD_DARK, (185, 170, 160, 90), 3)
        for i, lab in enumerate(["HALL", "OFFC", "STOR", "ROOF"]):
            hx = 208 + i * 38
            pygame.draw.circle(s, LIGHT_GREY, (hx, 188), 3)
            if lab == "STOR":
                color = RED if "key" not in self.found else (150, 70, 70)
            else:
                pygame.draw.line(s, LIGHT_GREY, (hx, 188), (hx, 200), 2)
                pygame.draw.circle(s, LIGHT_GREY, (hx, 210), 7, 3)
                pygame.draw.rect(s, LIGHT_GREY, (hx - 2, 216, 4, 10))
                color = GREY
            pygame.draw.rect(s, color, (hx - 17, 230, 34, 13))
            draw_text(s, lab, self.font_tiny, BLACK, (hx, 237), center=True)

        # camera and control panel
        pygame.draw.rect(s, DARK, (870, 72, 8, 24))
        pygame.draw.rect(s, (40, 41, 46), (826, 92, 52, 22))
        pygame.draw.rect(s, BLACK, (816, 96, 12, 14))
        pygame.draw.lines(s, BLACK, False, [(874, 114), (874, 140), (740, 140), (720, 160)], 2)
        pygame.draw.rect(s, (36, 37, 42), (620, 160, 120, 90), border_radius=4)
        pygame.draw.rect(s, BLACK, (632, 172, 96, 50))
        draw_text(s, "CAM 1", self.font_tiny, LIGHT_GREY, (638, 176))
        if "camera" in self.found or int(self.t * 2) % 2 == 0:
            draw_text(s, "OFF 22:10", self.font_small, YELLOW, (638, 194))
        for i in range(4):
            pygame.draw.circle(s, GREY, (640 + i * 25, 236), 5)

        # reception desk
        pygame.draw.rect(s, WOOD, (170, 395, 220, 70))
        pygame.draw.rect(s, (80, 64, 48), (162, 388, 236, 12))
        for px in (180, 280):
            pygame.draw.rect(s, WOOD_DARK, (px, 408, 90, 48), 2)
        pygame.draw.rect(s, PAPER, (220, 378, 40, 12))
        pygame.draw.rect(s, PAPER, (228, 372, 40, 12))

    def draw_exhibition(self, s):
        pygame.draw.rect(s, (91, 93, 99), (180, 120, 120, 150))
        pygame.draw.circle(s, (122, 124, 130), (240, 175), 25)
        pygame.draw.rect(s, (70, 72, 77), (205, 210, 70, 50))
        pygame.draw.rect(s, (139, 141, 146), (180, 120, 120, 150), 7)
        pygame.draw.rect(s, (85, 87, 92), (640, 120, 110, 90))
        pygame.draw.polygon(s, (110, 112, 118), [(650, 200), (690, 145), (730, 200)])
        pygame.draw.circle(s, (150, 150, 150), (715, 140), 8)
        pygame.draw.rect(s, (139, 141, 146), (640, 120, 110, 90), 7)
        pygame.draw.line(s, GREY, (0, 96), (WIDTH, 96), 2)

        pygame.draw.rect(s, BLACK, (465, TOP_BAR + 18, 30, 12))
        alpha_polygon(s, (255, 242, 196), 45, [(470, 80), (490, 80), (610, 430), (350, 430)])
        glow(s, (480, 195), 140, GOLD, 60)
        pygame.draw.rect(s, (43, 44, 48), (380, 110, 200, 170))
        pygame.draw.rect(s, (60, 61, 66), (395, 125, 170, 140), 1)
        pygame.draw.rect(s, GOLD, (380, 110, 200, 170), 12)
        pygame.draw.rect(s, shade(GOLD, 40), (380, 110, 200, 170), 2)
        pygame.draw.circle(s, LIGHT_GREY, (480, 104), 3)
        pygame.draw.rect(s, (200, 200, 200), (440, 290, 80, 18))
        draw_text(s, "The Moonlit Night", self.font_tiny, BLACK, (480, 299), center=True)

        for px in (360, 600):
            pygame.draw.rect(s, (150, 152, 158), (px - 3, 330, 6, 70))
            pygame.draw.ellipse(s, (150, 152, 158), (px - 14, 396, 28, 8))
            pygame.draw.circle(s, (150, 152, 158), (px, 328), 7)
        pygame.draw.lines(s, (110, 30, 40), False, [(363, 333), (390, 365), (420, 395)], 5)
        pygame.draw.lines(s, (110, 30, 40), False, [(597, 333), (575, 370), (560, 398)], 5)

        steps = [(480, 515), (520, 500), (565, 488), (605, 474), (650, 463),
                 (695, 452), (740, 443), (785, 435)]
        for i, (x, y) in enumerate(steps):
            w = 18 - i
            pygame.draw.ellipse(s, ORANGE, (x - w // 2, y + (6 if i % 2 else 0), w, w // 2 + 1))

    def draw_office(self, s):
        self.draw_window(s, (80, 110, 180, 170))
        pygame.draw.rect(s, GREY, (80, 110, 180, 170), 6)
        pygame.draw.line(s, GREY, (170, 110), (170, 280), 4)
        pygame.draw.line(s, GREY, (80, 195), (260, 195), 4)
        pygame.draw.polygon(s, (70, 40, 44), [(70, 100), (110, 100), (100, 290), (64, 290)])
        pygame.draw.polygon(s, (70, 40, 44), [(270, 100), (230, 100), (240, 290), (276, 290)])
        pygame.draw.rect(s, (200, 200, 200), (560, 130, 90, 110))
        pygame.draw.rect(s, (110, 112, 118), (568, 138, 74, 94))
        pygame.draw.circle(s, (30, 30, 34), (605, 170), 18)
        pygame.draw.circle(s, (70, 70, 76), (605, 175), 13)
        pygame.draw.line(s, RED, (600, 182), (610, 182), 3)
        pygame.draw.rect(s, (30, 30, 34), (585, 192, 40, 40))
        pygame.draw.rect(s, (60, 62, 68), (690, 320, 100, 110))
        pygame.draw.rect(s, (30, 31, 35), (700, 330, 80, 90))
        for i in range(4):
            pygame.draw.rect(s, PAPER, (708 + i * 3, 395 - i * 8, 60, 6))
        pygame.draw.rect(s, (80, 82, 88), (690, 320, 100, 110), 3)
        pygame.draw.rect(s, (50, 40, 32), (290, 380, 30, 50))
        for a in (-0.7, -0.3, 0.1, 0.5, 0.9):
            pygame.draw.line(s, (60, 70, 60), (305, 380),
                             (305 + 40 * math.sin(a), 380 - 50 * math.cos(a)), 4)
        draw_wall_lamp(s, 470, 200)
        # desk with the insurance contract (Weber stands behind it)
        pygame.draw.rect(s, WOOD, (330, 360, 340, 100))
        pygame.draw.rect(s, (80, 64, 48), (320, 352, 360, 14))
        pygame.draw.rect(s, WOOD_DARK, (340, 375, 120, 70), 2)
        pygame.draw.circle(s, LIGHT_GREY, (400, 410), 4)
        pygame.draw.polygon(s, PAPER, [(500, 352), (580, 346), (585, 360), (505, 366)])
        pygame.draw.polygon(s, PAPER, [(505, 350), (575, 340), (580, 354), (510, 362)])
        pygame.draw.circle(s, RED, (560, 350), 5)
        pygame.draw.rect(s, (40, 60, 50), (620, 330, 10, 24))
        pygame.draw.polygon(s, (90, 120, 100), [(608, 330), (642, 330), (634, 316), (616, 316)])
        glow(s, (625, 330), 30, YELLOW, 60)

    def draw_storage(self, s):
        pygame.draw.line(s, BLACK, (480, TOP_BAR), (480, 80), 2)
        pygame.draw.circle(s, YELLOW, (480, 86), 8)
        alpha_polygon(s, YELLOW, 28, [(474, 90), (486, 90), (700, 430), (260, 430)])
        glow(s, (480, 86), 60, YELLOW, 90)
        pygame.draw.rect(s, WOOD, (560, 150, 220, 8))
        for i, c in enumerate(((120, 120, 120), (100, 100, 104), (140, 136, 130))):
            pygame.draw.rect(s, c, (575 + i * 60, 118, 36, 32))
        # hidden painting behind the crates
        pygame.draw.polygon(s, (90, 90, 96), [(695, 240), (785, 230), (790, 330), (690, 335)])
        pygame.draw.line(s, (70, 70, 76), (700, 260), (780, 300), 3)
        pygame.draw.polygon(s, GOLD, [(785, 230), (765, 232), (787, 252)])
        for rect in ((640, 320, 110, 110), (745, 330, 90, 100), (300, 350, 140, 80)):
            draw_crate(s, rect)
        # coffee cup with lipstick
        pygame.draw.polygon(s, (230, 230, 230), [(354, 320), (378, 320), (375, 348), (357, 348)])
        pygame.draw.arc(s, (230, 230, 230), (372, 326, 14, 14), -1.6, 1.6, 3)
        pygame.draw.line(s, RED, (357, 321), (366, 321), 3)
        for i in range(2):
            ox = 361 + i * 9
            pygame.draw.line(s, GREY, (ox, 314), (ox + math.sin(self.t * 2 + i) * 3, 302), 2)
        # mop, bucket and boots
        pygame.draw.line(s, (120, 100, 80), (205, 295), (215, 420), 5)
        pygame.draw.polygon(s, (130, 130, 130), [(198, 410), (230, 410), (240, 432), (190, 432)])
        pygame.draw.polygon(s, (75, 77, 82), [(180, 385), (230, 385), (225, 432), (185, 432)])
        pygame.draw.ellipse(s, (60, 70, 90), (184, 380, 42, 10))
        for bx in (252, 288):
            pygame.draw.ellipse(s, BLACK, (bx, 413, 34, 18))
            pygame.draw.rect(s, BLACK, (bx + 2, 396, 18, 25))

    def draw_lobby(self, s):
        draw_chandelier(s, 480, 95)
        for x in (110, 850):
            draw_wall_lamp(s, x, 180)
        # portrait of the founder
        pygame.draw.rect(s, (100, 96, 90), (180, 110, 110, 130))
        pygame.draw.circle(s, (130, 126, 120), (235, 160), 22)
        pygame.draw.rect(s, (80, 76, 70), (210, 190, 50, 50))
        pygame.draw.rect(s, GOLD, (180, 110, 110, 130), 6)
        # key rack
        pygame.draw.rect(s, WOOD, (555, 175, 130, 80))
        pygame.draw.rect(s, WOOD_DARK, (555, 175, 130, 80), 3)
        for i in range(5):
            kx = 575 + i * 22
            pygame.draw.line(s, LIGHT_GREY, (kx, 190), (kx, 205), 2)
            pygame.draw.circle(s, LIGHT_GREY, (kx, 212), 6, 2)
            pygame.draw.rect(s, LIGHT_GREY, (kx - 1, 217, 3, 14))
        draw_text(s, "KEYS", self.font_tiny, LIGHT_GREY, (620, 244), center=True)
        # reception desk (Finch stands behind it)
        pygame.draw.rect(s, WOOD, (330, 352, 300, 78))
        pygame.draw.rect(s, (80, 64, 48), (320, 344, 320, 14))
        pygame.draw.line(s, GOLD, (320, 358), (640, 358), 2)
        for px in (370, 450, 530):
            pygame.draw.rect(s, WOOD_DARK, (px, 368, 60, 50), 2)
        pygame.draw.circle(s, GOLD, (365, 338), 9)
        pygame.draw.rect(s, GOLD, (354, 338, 22, 5))
        # the key log book
        pygame.draw.polygon(s, PAPER, [(520, 344), (558, 330), (596, 344), (558, 350)])
        pygame.draw.line(s, INK, (558, 330), (558, 350), 1)
        for i in range(3):
            pygame.draw.line(s, (150, 140, 120), (530 + i * 6, 342 - i * 2), (550, 335 - i * 2), 1)
        # vase of lilies
        pygame.draw.rect(s, (180, 180, 186), (600, 318, 16, 26))
        for a in (-0.5, 0, 0.5):
            end = (608 + 22 * math.sin(a), 318 - 25 * math.cos(a))
            pygame.draw.line(s, (70, 90, 70), (608, 318), end, 2)
            pygame.draw.circle(s, (230, 230, 230), (int(end[0]), int(end[1])), 5)
        # potted palms
        for px in (300, 700):
            pygame.draw.polygon(s, (90, 60, 40), [(px - 18, 430), (px + 18, 430), (px + 14, 400), (px - 14, 400)])
            for a in (-1.0, -0.5, 0, 0.5, 1.0):
                pygame.draw.line(s, (50, 75, 55), (px, 400), (px + 40 * math.sin(a), 400 - 50 * math.cos(a)), 4)

    def draw_ballroom(self, s):
        draw_chandelier(s, 480, 90, lit=False)
        self.draw_window(s, (540, 100, 100, 140))
        pygame.draw.rect(s, GREY, (540, 100, 100, 140), 5)
        pygame.draw.line(s, GREY, (590, 100), (590, 240), 3)
        for cx in (530, 650):
            pygame.draw.polygon(s, (90, 30, 50), [(cx - 6, 92), (cx + 14, 92), (cx + 8, 250), (cx - 10, 250)])
        # grand piano with open lid
        black = (12, 12, 14)
        pygame.draw.polygon(s, black, [(250, 300), (480, 300), (490, 340), (480, 370), (250, 370)])
        pygame.draw.line(s, (60, 60, 70), (252, 302), (478, 302), 2)
        pygame.draw.polygon(s, black, [(300, 300), (470, 300), (430, 220)])
        pygame.draw.line(s, (60, 60, 70), (300, 300), (430, 220), 2)
        pygame.draw.line(s, (60, 60, 66), (430, 220), (420, 300), 2)
        pygame.draw.rect(s, (230, 230, 230), (255, 352, 130, 12))
        for kx in range(258, 385, 9):
            pygame.draw.rect(s, black, (kx + 5, 352, 4, 7))
        for lx in (265, 470):
            pygame.draw.rect(s, black, (lx, 370, 8, 60))
        # tape recorder hidden in the piano
        pygame.draw.rect(s, (60, 60, 66), (385, 292, 48, 22))
        pygame.draw.circle(s, (120, 120, 126), (397, 303), 6, 2)
        pygame.draw.circle(s, (120, 120, 126), (421, 303), 6, 2)
        if int(self.t * 2) % 2 == 0:
            pygame.draw.circle(s, RED, (429, 296), 2)
        pygame.draw.rect(s, PAPER, (300, 330, 40, 22))
        # bench and the broken clasp under it
        pygame.draw.rect(s, black, (290, 400, 110, 16))
        pygame.draw.rect(s, black, (296, 416, 6, 22))
        pygame.draw.rect(s, black, (388, 416, 6, 22))
        pygame.draw.arc(s, (190, 225, 255), (348, 437, 16, 12), 0, 4.5, 2)
        pygame.draw.circle(s, (190, 225, 255), (366, 442), 2)
        # empty display case
        pygame.draw.rect(s, (70, 70, 76), (630, 360, 80, 70))
        pygame.draw.rect(s, (90, 30, 40), (642, 338, 56, 22))
        alpha_polygon(s, (200, 220, 240), 40, [(625, 280), (715, 280), (715, 360), (625, 360)])
        pygame.draw.rect(s, (160, 170, 180), (625, 280, 90, 80), 2)
        pygame.draw.line(s, (160, 170, 180), (625, 280), (600, 262), 2)
        pygame.draw.line(s, (160, 170, 180), (715, 280), (690, 262), 2)
        pygame.draw.line(s, (160, 170, 180), (600, 262), (690, 262), 2)

    def draw_kitchen(self, s):
        for x in range(0, WIDTH, 40):
            pygame.draw.line(s, (70, 72, 70), (x, TOP_BAR + 22), (x, FLOOR_Y - 8), 1)
        for y in range(TOP_BAR + 22, FLOOR_Y - 8, 40):
            pygame.draw.line(s, (70, 72, 70), (0, y), (WIDTH, y), 1)
        # hanging pans
        pygame.draw.line(s, (90, 90, 96), (420, 100), (520, 100), 3)
        for px in (430, 465, 500):
            pygame.draw.line(s, (90, 90, 96), (px, 100), (px, 116), 2)
            pygame.draw.circle(s, (60, 60, 66), (px, 132), 15)
            pygame.draw.circle(s, (80, 80, 86), (px, 132), 15, 2)
        # shelf with egg timers - one is missing
        pygame.draw.rect(s, WOOD, (190, 195, 170, 10))
        for i in range(6):
            tx = 210 + i * 27
            if i == 3:
                pygame.draw.circle(s, (80, 82, 80), (tx, 182), 9, 1)
                continue
            pygame.draw.ellipse(s, (205, 205, 200), (tx - 9, 168, 18, 26))
            pygame.draw.line(s, (90, 90, 90), (tx, 174), (tx, 182), 2)
        # counter with flour bag and glove
        pygame.draw.rect(s, (90, 92, 96), (160, 340, 300, 90))
        pygame.draw.rect(s, (130, 132, 136), (152, 332, 316, 12))
        for dx in (170, 270, 370):
            pygame.draw.rect(s, (80, 82, 86), (dx, 352, 80, 70), 2)
        pygame.draw.polygon(s, (200, 195, 180), [(190, 332), (232, 332), (226, 290), (196, 290)])
        draw_text(s, "FLOUR", self.font_tiny, (110, 100, 80), (211, 314), center=True)
        pygame.draw.ellipse(s, (240, 240, 235), (290, 318, 34, 16))
        for fx in range(292, 300, 3):
            pygame.draw.line(s, (240, 240, 235), (fx + 30, 322), (fx + 38, 314), 4)
        # stove with pots and hood
        pygame.draw.polygon(s, (70, 72, 76), [(540, 140), (720, 140), (690, 200), (570, 200)])
        pygame.draw.rect(s, (50, 51, 55), (555, 315, 150, 115))
        pygame.draw.rect(s, BLACK, (575, 360, 110, 55))
        glow(s, (630, 395), 40, ORANGE, 40)
        for px in (585, 640):
            pygame.draw.rect(s, (120, 122, 126), (px, 285, 45, 32))
            for i in range(2):
                sx = px + 15 + i * 14
                pygame.draw.line(s, GREY, (sx, 280), (sx + math.sin(self.t * 2 + i + px) * 4, 262), 2)
        # rubbish bin with a crumpled letter
        pygame.draw.polygon(s, (80, 82, 86), [(716, 360), (772, 360), (766, 432), (722, 432)])
        pygame.draw.rect(s, (100, 102, 106), (712, 354, 64, 8))
        pygame.draw.circle(s, PAPER, (744, 350), 11)
        pygame.draw.line(s, (180, 170, 150), (736, 346), (750, 354), 1)
        # cake on the floor
        pygame.draw.ellipse(s, (70, 45, 30), (360, 462, 90, 26))
        pygame.draw.ellipse(s, (95, 60, 40), (372, 456, 50, 18))

    def draw_fuseroom(self, s):
        for y in (95, 115):
            pygame.draw.rect(s, (70, 72, 76), (0, y, WIDTH, 10))
            pygame.draw.line(s, (100, 102, 106), (0, y + 2), (WIDTH, y + 2), 1)
        pygame.draw.rect(s, (70, 72, 76), (360, 95, 10, 335))
        pygame.draw.line(s, BLACK, (480, TOP_BAR), (480, 130), 2)
        pygame.draw.circle(s, YELLOW, (480, 136), 6)
        glow(s, (480, 136), 60, YELLOW, 80)
        alpha_polygon(s, YELLOW, 22, [(476, 140), (484, 140), (640, 430), (320, 430)])
        # fuse box with egg timer
        pygame.draw.rect(s, (80, 84, 90), (420, 160, 140, 165))
        pygame.draw.rect(s, (40, 42, 46), (432, 172, 116, 120))
        for row in range(3):
            for col in range(4):
                pygame.draw.rect(s, (150, 150, 150), (442 + col * 27, 182 + row * 35, 12, 22))
        pygame.draw.rect(s, RED, (520, 292, 22, 28))
        pygame.draw.polygon(s, (90, 94, 100), [(420, 160), (380, 175), (380, 340), (420, 325)])
        draw_text(s, "DANGER", self.font_tiny, YELLOW, (490, 310), center=True)
        pygame.draw.ellipse(s, (240, 240, 230), (512, 258, 28, 36))
        pygame.draw.line(s, ORANGE, (526, 266), (526, 278), 2)
        pygame.draw.line(s, ORANGE, (526, 278), (533, 281), 2)
        pygame.draw.lines(s, RED, False, [(540, 280), (555, 290), (535, 306)], 2)
        # sheet music on the floor
        pygame.draw.polygon(s, PAPER, [(590, 470), (655, 460), (665, 488), (598, 496)])
        for i in range(4):
            y = 469 + i * 6
            pygame.draw.line(s, (120, 110, 90), (598, y + 2), (655, y - 6), 1)
        pygame.draw.circle(s, INK, (620, 472), 2)
        pygame.draw.circle(s, INK, (634, 474), 2)
        # boiler
        pygame.draw.rect(s, (70, 64, 58), (700, 190, 100, 240), border_radius=30)
        pygame.draw.line(s, (90, 84, 78), (708, 210), (708, 410), 3)
        pygame.draw.circle(s, (40, 36, 32), (750, 260), 20)
        pygame.draw.circle(s, (180, 180, 180), (750, 260), 16, 2)
        pygame.draw.line(s, RED, (750, 260), (758 + 3 * math.sin(self.t * 5), 250), 2)
        pygame.draw.circle(s, ORANGE if int(self.t * 3) % 2 else (150, 80, 20), (750, 360), 5)

    def draw_dining(self, s):
        self.draw_window(s, (440, 100, 120, 150), lightning=True)
        pygame.draw.rect(s, GREY, (440, 100, 120, 150), 6)
        pygame.draw.line(s, GREY, (500, 100), (500, 250), 3)
        for cx in (420, 566):
            pygame.draw.polygon(s, (90, 26, 30), [(cx, 90), (cx + 16, 90), (cx + 20, 270), (cx - 4, 270)])
        # portrait of the professor
        pygame.draw.rect(s, (100, 96, 90), (300, 105, 100, 130))
        pygame.draw.circle(s, (40, 40, 44), (350, 160), 22)
        pygame.draw.circle(s, (130, 126, 120), (350, 165), 16)
        pygame.draw.circle(s, (60, 60, 66), (344, 165), 5, 1)
        pygame.draw.circle(s, (60, 60, 66), (356, 165), 5, 1)
        pygame.draw.rect(s, (60, 58, 56), (325, 190, 50, 45))
        pygame.draw.rect(s, GOLD, (300, 105, 100, 130), 6)
        draw_chandelier(s, 260, 110)
        # sideboard with the butler's notes
        pygame.draw.rect(s, WOOD, (590, 270, 160, 85))
        pygame.draw.rect(s, WOOD_DARK, (590, 270, 160, 85), 3)
        pygame.draw.line(s, WOOD_DARK, (670, 270), (670, 355), 2)
        pygame.draw.polygon(s, PAPER, [(625, 262), (685, 256), (690, 268), (630, 272)])
        for i in range(3):
            pygame.draw.line(s, (150, 140, 120), (632, 269 - i * 2), (680, 264 - i * 2), 1)
        pygame.draw.rect(s, (200, 200, 205), (710, 240, 14, 30))
        # long dinner table
        pygame.draw.rect(s, (225, 222, 215), (180, 358, 600, 20))
        pygame.draw.rect(s, WOOD, (180, 378, 600, 55))
        for k in range(8):
            pygame.draw.line(s, (205, 202, 195), (190 + k * 75, 378), (196 + k * 75, 392), 2)
        for px in range(215, 780, 85):
            pygame.draw.ellipse(s, (245, 245, 245), (px - 18, 350, 36, 12))
            pygame.draw.ellipse(s, (210, 210, 210), (px - 10, 352, 20, 7), 1)
        for cx in (300, 480, 660):
            pygame.draw.rect(s, (230, 230, 220), (cx - 3, 325, 6, 28))
            pygame.draw.circle(s, YELLOW, (cx, 321 + int(math.sin(self.t * 8 + cx))), 4)
            glow(s, (cx, 321), 28, YELLOW, 80)
        # ashtray with a cigar
        pygame.draw.ellipse(s, (120, 120, 126), (630, 345, 40, 12))
        pygame.draw.line(s, (120, 90, 60), (640, 347), (665, 342), 4)
        pygame.draw.line(s, (130, 130, 130), (666, 340), (668 + math.sin(self.t * 2) * 3, 322), 1)

    def draw_library(self, s):
        draw_shelf_of_books(s, (160, 90, 190, 330), 1)
        if "passage" in self.found:
            pygame.draw.rect(s, BLACK, (590, 90, 120, 330))
            draw_shelf_of_books(s, (690, 90, 190, 330), 2)
        else:
            draw_shelf_of_books(s, (590, 90, 190, 330), 2)
            pygame.draw.circle(s, (110, 90, 60), (600, 260), 3)
        # fireplace with a half-burnt telegram
        pygame.draw.rect(s, (90, 88, 86), (370, 250, 150, 180))
        for y in range(262, 430, 16):
            pygame.draw.line(s, (78, 76, 74), (370, y), (520, y), 1)
        pygame.draw.rect(s, (110, 108, 104), (360, 240, 170, 16))
        pygame.draw.rect(s, BLACK, (395, 300, 100, 130))
        for i in range(3):
            fx = 420 + i * 22
            h = 26 + 8 * math.sin(self.t * 6 + i * 2)
            pygame.draw.polygon(s, ORANGE, [(fx - 9, 430), (fx + 9, 430), (fx, 430 - h)])
            pygame.draw.polygon(s, YELLOW, [(fx - 4, 430), (fx + 4, 430), (fx, 430 - h * 0.5)])
        glow(s, (445, 410), 70, ORANGE, 80)
        pygame.draw.polygon(s, PAPER, [(440, 410), (500, 404), (505, 424), (446, 428)])
        pygame.draw.polygon(s, (40, 30, 20), [(440, 410), (458, 408), (450, 428), (446, 428)])
        pygame.draw.rect(s, GOLD, (400, 222, 14, 18))
        pygame.draw.rect(s, (200, 200, 205), (470, 226, 8, 14))
        # side table with Lily's camera
        pygame.draw.rect(s, WOOD, (530, 385, 50, 8))
        pygame.draw.rect(s, WOOD_DARK, (550, 393, 8, 37))
        pygame.draw.rect(s, (40, 40, 46), (532, 364, 40, 22), border_radius=3)
        pygame.draw.circle(s, (110, 180, 210), (552, 375), 7, 2)

    def draw_lab(self, s):
        for x in range(60, WIDTH, 220):
            pygame.draw.rect(s, (210, 220, 230), (x, TOP_BAR + 6, 120, 8))
            alpha_polygon(s, (220, 235, 255), 18, [(x, TOP_BAR + 14), (x + 120, TOP_BAR + 14),
                                                    (x + 170, 430), (x - 50, 430)])
        # blackboard
        pygame.draw.rect(s, (30, 44, 36), (300, 105, 260, 135))
        pygame.draw.rect(s, WOOD, (300, 105, 260, 135), 6)
        for i, line in enumerate(["E = U * I * t", "Li + C6 -> LiC6", "10x STRONGER!", "  ???"]):
            draw_text(s, line, self.font_small, (200, 205, 200), (320, 118 + i * 26))
        # lab bench with flasks
        pygame.draw.rect(s, (70, 72, 76), (150, 350, 300, 80))
        pygame.draw.rect(s, (110, 112, 116), (142, 342, 316, 12))
        for fx, liquid in ((190, (120, 150, 130)), (240, (140, 120, 150)), (300, (150, 150, 120))):
            pygame.draw.polygon(s, liquid, [(fx - 10, 324), (fx + 10, 324), (fx + 15, 340), (fx - 15, 340)])
            pygame.draw.polygon(s, (200, 205, 210), [(fx - 4, 300), (fx + 4, 300),
                                                     (fx + 16, 342), (fx - 16, 342)], 2)
            for b in range(2):
                by = 336 - (self.t * 20 + b * 7 + fx) % 14
                pygame.draw.circle(s, shade(liquid, 50), (fx - 3 + b * 6, int(by)), 2)
        pygame.draw.ellipse(s, (180, 160, 120), (370, 330, 40, 14))
        # open safe
        pygame.draw.rect(s, (70, 74, 80), (620, 250, 125, 145))
        pygame.draw.rect(s, BLACK, (632, 262, 101, 121))
        pygame.draw.polygon(s, (90, 94, 100), [(620, 250), (585, 262), (585, 400), (620, 395)])
        pygame.draw.circle(s, LIGHT_GREY, (602, 320), 10, 2)
        pygame.draw.rect(s, (60, 62, 68), (640, 395, 85, 35))
        # hairpin and cigar ash on the floor
        pygame.draw.line(s, (220, 190, 90), (596, 452), (636, 446), 2)
        pygame.draw.line(s, (220, 190, 90), (596, 452), (632, 455), 2)
        pygame.draw.circle(s, (220, 190, 90), (596, 452), 3)
        pygame.draw.ellipse(s, (140, 140, 140), (690, 450, 38, 12))
        pygame.draw.ellipse(s, (170, 170, 170), (700, 448, 18, 7))
        # strange machine
        pygame.draw.rect(s, (60, 62, 68), (800, 360, 90, 70))
        for i in range(3):
            pygame.draw.circle(s, GREEN_LIGHT if int(self.t * 3 + i) % 2 else (40, 60, 40), (820 + i * 22, 385), 5)
        pygame.draw.rect(s, (130, 90, 50), (835, 200, 20, 160))
        for y in range(210, 355, 12):
            pygame.draw.ellipse(s, (170, 110, 60), (825, y, 40, 8), 2)
        pygame.draw.circle(s, (150, 150, 160), (845, 190), 18)
        if int(self.t * 4) % 3 == 0:
            pygame.draw.lines(s, (180, 200, 255), False, [(860, 185), (875, 175), (870, 165), (888, 155)], 2)
            glow(s, (875, 170), 30, (180, 200, 255), 80)

    def draw_greenhouse(self, s):
        self.draw_window(s, (0, TOP_BAR, WIDTH, FLOOR_Y - TOP_BAR - 8), lightning=True)
        for x in range(0, WIDTH, 120):
            pygame.draw.line(s, (150, 160, 160), (x, TOP_BAR), (x, FLOOR_Y), 4)
        for y in (TOP_BAR + 100, TOP_BAR + 230):
            pygame.draw.line(s, (150, 160, 160), (0, y), (WIDTH, y), 4)
        # hanging plants
        for hx in (240, 520):
            pygame.draw.line(s, (60, 60, 60), (hx, TOP_BAR), (hx, 110), 2)
            pygame.draw.ellipse(s, (120, 70, 50), (hx - 18, 108, 36, 20))
            for k in range(5):
                pygame.draw.line(s, (60, 90, 60), (hx - 12 + k * 6, 120), (hx - 20 + k * 10, 160 + k % 2 * 14), 2)
        # flower pots on a bench
        pygame.draw.rect(s, WOOD, (160, 380, 220, 12))
        for leg in (170, 360):
            pygame.draw.rect(s, WOOD_DARK, (leg, 392, 8, 38))
        for i, px in enumerate((185, 240, 295, 345)):
            pygame.draw.polygon(s, (120, 70, 50), [(px - 16, 350), (px + 16, 350), (px + 12, 380), (px - 12, 380)])
            for a in (-0.6, 0, 0.6):
                pygame.draw.line(s, (60, 85, 60), (px, 350), (px + 25 * math.sin(a + i), 350 - 35 * math.cos(a)), 3)
            pygame.draw.circle(s, (200, 120, 160), (px + 6, 318), 4)
        # hidden coat behind the palm
        pygame.draw.polygon(s, (92, 76, 60), [(670, 300), (720, 300), (730, 400), (660, 400)])
        pygame.draw.polygon(s, (120, 100, 80), [(670, 300), (695, 330), (720, 300)])
        for by in (340, 360, 380):
            pygame.draw.circle(s, (40, 32, 26), (695, by), 3)
        pygame.draw.rect(s, PAPER, (704, 352, 14, 8))
        # big palm tree
        pygame.draw.polygon(s, (120, 70, 50), [(640, 430), (720, 430), (705, 390), (655, 390)])
        pygame.draw.line(s, (90, 70, 50), (680, 390), (690, 200), 9)
        for a in (-2.4, -1.9, -1.2, -0.6, 0.0, 0.6):
            end = (690 + 95 * math.cos(a), 200 + 70 * math.sin(a) + 40)
            pygame.draw.line(s, (50, 75, 55), (690, 200), end, 7)

    def draw_train_windows(self, s, xs, width=120):
        for x in xs:
            frame = pygame.Rect(x - 6, 104, width + 12, 132)
            pygame.draw.rect(s, BRASS, frame, border_radius=16)
            pane = pygame.Rect(x, 110, width, 120)
            self.draw_window(s, pane, mountains=True)
            pygame.draw.rect(s, shade(BRASS, -40), pane, 2, border_radius=12)
            pygame.draw.polygon(s, (215, 220, 232), [pane.bottomleft, (pane.x + 26, pane.bottom), (pane.x, pane.bottom - 16)])
            pygame.draw.polygon(s, (215, 220, 232), [pane.bottomright, (pane.right - 22, pane.bottom), (pane.right, pane.bottom - 12)])
            for cx, side in ((x - 4, -1), (x + width + 4, 1)):
                pygame.draw.polygon(s, (110, 40, 46), [(cx, 100), (cx + 14 * side, 100), (cx + 18 * side, 250), (cx - 2 * side, 250)])
        for x in xs[1:]:
            draw_wall_lamp(s, x - 30, 160)

    def draw_lounge(self, s):
        self.draw_train_windows(s, [245], width=170)
        # bar with bottles
        pygame.draw.rect(s, WOOD_DARK, (600, 140, 200, 120))
        for row, y in enumerate((180, 228)):
            pygame.draw.rect(s, BRASS, (600, y, 200, 4))
            for k in range(8):
                bx = 610 + k * 23
                tone = (60 + (k * 37 + row * 11) % 90, 80, 70 + (k * 23) % 80)
                pygame.draw.rect(s, tone, (bx, y - 30, 12, 30), border_radius=3)
                pygame.draw.rect(s, tone, (bx + 4, y - 38, 4, 10))
                pygame.draw.line(s, shade(tone, 50), (bx + 2, y - 26), (bx + 2, y - 6), 1)
        pygame.draw.rect(s, WOOD, (600, 310, 200, 120))
        pygame.draw.rect(s, (90, 64, 44), (590, 300, 220, 14))
        pygame.draw.line(s, BRASS, (600, 420), (800, 420), 3)
        # gramophone
        pygame.draw.rect(s, WOOD_DARK, (700, 280, 50, 22))
        pygame.draw.line(s, BRASS, (725, 280), (730, 262), 3)
        pygame.draw.polygon(s, BRASS, [(728, 266), (765, 236), (775, 256)])
        pygame.draw.ellipse(s, (20, 20, 22), (704, 276, 36, 8))
        # armchair with the telegram
        pygame.draw.rect(s, (90, 40, 46), (180, 360, 110, 70), border_radius=12)
        pygame.draw.rect(s, (110, 50, 56), (190, 340, 90, 40), border_radius=10)
        pygame.draw.rect(s, (80, 34, 40), (172, 360, 22, 60), border_radius=8)
        pygame.draw.rect(s, (80, 34, 40), (276, 360, 22, 60), border_radius=8)
        pygame.draw.polygon(s, PAPER, [(215, 362), (258, 356), (262, 372), (220, 378)])
        # small table with program and champagne
        pygame.draw.ellipse(s, WOOD, (345, 388, 90, 20))
        pygame.draw.rect(s, WOOD_DARK, (386, 398, 8, 32))
        pygame.draw.polygon(s, PAPER, [(360, 384), (400, 378), (416, 390), (372, 396)])
        pygame.draw.circle(s, RED, (392, 386), 3)
        pygame.draw.line(s, (220, 220, 230), (418, 390), (418, 368), 1)
        pygame.draw.polygon(s, (220, 220, 230), [(412, 368), (424, 368), (418, 358)], 1)

    def draw_train_dining(self, s):
        self.draw_train_windows(s, [200, 420, 640])
        for tx in (180, 400):
            pygame.draw.rect(s, (225, 222, 215), (tx, 330, 160, 22))
            pygame.draw.polygon(s, (205, 202, 195), [(tx, 352), (tx + 160, 352), (tx + 154, 380), (tx + 6, 380)])
            pygame.draw.rect(s, WOOD_DARK, (tx + 70, 380, 20, 50))
            pygame.draw.ellipse(s, WHITE, (tx + 20, 322, 34, 10))
            pygame.draw.ellipse(s, WHITE, (tx + 106, 322, 34, 10))
            pygame.draw.rect(s, BRASS, (tx + 76, 300, 6, 24))
            pygame.draw.polygon(s, (170, 50, 50), [(tx + 64, 300), (tx + 94, 300), (tx + 86, 286), (tx + 72, 286)])
            glow(s, (tx + 79, 300), 40, (255, 180, 120), 70)
        # chess board on table 2
        for row in range(3):
            for col in range(8):
                color = (230, 230, 230) if (row + col) % 2 == 0 else (40, 40, 44)
                pygame.draw.rect(s, color, (432 + col * 9, 322 + row * 6, 9, 6))
        pygame.draw.circle(s, WHITE, (450, 316), 3)
        pygame.draw.circle(s, BLACK, (470, 316), 3)
        # serving cart with order slips
        pygame.draw.rect(s, (130, 132, 140), (650, 350, 120, 8))
        pygame.draw.rect(s, (130, 132, 140), (650, 400, 120, 6))
        for lx in (655, 760):
            pygame.draw.line(s, (130, 132, 140), (lx, 350), (lx, 420), 3)
            pygame.draw.circle(s, BLACK, (lx, 424), 6)
        pygame.draw.ellipse(s, (200, 200, 205), (720, 330, 34, 22))
        pygame.draw.line(s, (200, 200, 205), (752, 336), (762, 330), 3)
        pygame.draw.line(s, (90, 90, 96), (700, 348), (700, 322), 2)
        for k in range(3):
            pygame.draw.rect(s, PAPER, (686 + k * 3, 326 + k * 6, 26, 10))

    def draw_sleeper(self, s):
        for i, x in enumerate((165, 305, 445, 585)):
            open_door = i in (1, 3)
            pygame.draw.rect(s, (40, 30, 24), (x, 200, 120, 230))
            if open_door:
                pygame.draw.rect(s, (90, 60, 50), (x + 6, 206, 108, 224))
                pygame.draw.rect(s, (130, 40, 46), (x + 10, 330, 100, 40))
                pygame.draw.rect(s, WHITE, (x + 14, 316, 30, 16), border_radius=4)
                self.draw_window(s, (x + 30, 230, 60, 60))
                glow(s, (x + 60, 300), 60, YELLOW, 40)
            else:
                pygame.draw.rect(s, (82, 58, 42), (x + 6, 206, 108, 224))
                pygame.draw.rect(s, (30, 40, 60), (x + 26, 222, 68, 80), border_radius=6)
                pygame.draw.rect(s, BRASS, (x + 26, 222, 68, 80), 2, border_radius=6)
                pygame.draw.rect(s, BRASS, (x + 96, 320, 5, 34), border_radius=2)
            pygame.draw.rect(s, BRASS, (x, 200, 120, 230), 3)
            pygame.draw.rect(s, BRASS, (x + 45, 180, 30, 16))
            draw_text(s, str(i + 1), self.font_small_bold, BLACK, (x + 60, 188), center=True)
        # doctor's bag in compartment 2
        pygame.draw.rect(s, (40, 30, 26), (334, 330, 56, 30), border_radius=6)
        pygame.draw.arc(s, BRASS, (348, 318, 28, 20), 0, math.pi, 3)
        pygame.draw.line(s, BRASS, (334, 340), (390, 340), 2)
        # hatbox in compartment 4
        pygame.draw.ellipse(s, (200, 160, 170), (612, 346, 66, 20))
        pygame.draw.rect(s, (200, 160, 170), (612, 322, 66, 34))
        pygame.draw.ellipse(s, (220, 185, 195), (612, 314, 66, 18))
        pygame.draw.rect(s, BRASS, (638, 336, 14, 12))
        if "egg" in self.found:
            glow(s, (645, 322), 30, GOLD, 90)
        # wet heel prints from the luggage car to compartment 4
        for k in range(7):
            hx = 800 - k * 24
            hy = 448 + (6 if k % 2 else 0)
            alpha_ellipse(s, (140, 170, 210), 120, (hx - 7, hy, 14, 7))
            alpha_ellipse(s, (140, 170, 210), 120, (hx + 9, hy + 2, 4, 4))

    def draw_luggage(self, s):
        # single swinging lamp
        swing = math.sin(self.t * 1.3) * 12
        pygame.draw.line(s, BLACK, (480, TOP_BAR), (480 + swing, 92), 2)
        pygame.draw.circle(s, YELLOW, (int(480 + swing), 96), 7)
        glow(s, (480 + swing, 96), 70, YELLOW, 90)
        alpha_polygon(s, YELLOW, 22, [(476 + swing, 100), (484 + swing, 100), (700, 430), (260, 430)])
        # suitcases and crates
        draw_crate(s, (60, 340, 90, 90))
        draw_suitcase(s, (760, 380, 120, 50), (90, 60, 50))
        draw_suitcase(s, (770, 340, 100, 40), (60, 70, 90))
        draw_suitcase(s, (250, 400, 70, 30), (80, 70, 60))
        # open window with snow blowing in
        self.draw_window(s, (760, 100, 130, 100))
        pygame.draw.rect(s, (80, 84, 90), (760, 100, 130, 100), 5)
        pygame.draw.polygon(s, (90, 94, 100), [(760, 100), (720, 120), (720, 220), (760, 200)])
        for k in range(8):
            fx = 760 - (self.t * 60 + k * 40) % 260
            fy = 140 + k * 8 + 20 * math.sin(self.t * 2 + k)
            pygame.draw.circle(s, (235, 238, 245), (int(fx), int(fy)), 2)
        pygame.draw.polygon(s, (215, 220, 232), [(700, 430), (790, 430), (770, 418), (730, 414)])
        # cage with an empty stand inside
        pygame.draw.rect(s, (40, 30, 26), (440, 330, 100, 100))
        pygame.draw.rect(s, (110, 30, 40), (450, 310, 80, 24))
        pygame.draw.ellipse(s, (130, 40, 50), (462, 300, 56, 16))
        for x in range(300, 640, 20):
            pygame.draw.line(s, (120, 124, 130), (x, 140), (x, 430), 3)
        pygame.draw.line(s, (120, 124, 130), (300, 140), (640, 140), 4)
        pygame.draw.line(s, (120, 124, 130), (300, 300), (640, 300), 2)
        # cage door, swung open
        for k in range(5):
            x = 645 + k * 18
            pygame.draw.line(s, (140, 144, 150), (x, 150 + k * 4), (x, 420 - k * 4), 3)
        pygame.draw.line(s, (140, 144, 150), (645, 150), (717, 166), 3)
        pygame.draw.line(s, (140, 144, 150), (645, 420), (717, 404), 3)
        pygame.draw.rect(s, BRASS, (700, 270, 14, 20))
        # white feather stuck in the door
        pygame.draw.line(s, (235, 235, 235), (684, 270), (708, 246), 2)
        for k in range(6):
            fx = 686 + k * 4
            fy = 268 - k * 4
            pygame.draw.line(s, (235, 235, 235), (fx, fy), (fx - 6, fy - 6), 1)
            pygame.draw.line(s, (235, 235, 235), (fx, fy), (fx + 6, fy + 2), 1)
        # sleeping guard on a chair with a cup next to him
        pygame.draw.rect(s, WOOD_DARK, (180, 380, 70, 8))
        for lx in (184, 240):
            pygame.draw.line(s, WOOD_DARK, (lx, 388), (lx, 430), 4)
        pygame.draw.rect(s, WOOD_DARK, (236, 320, 8, 64))
        pygame.draw.polygon(s, (20, 20, 24), [(190, 382), (240, 382), (232, 322), (198, 326)])
        pygame.draw.rect(s, (20, 20, 24), (196, 386, 14, 40))
        pygame.draw.rect(s, (20, 20, 24), (220, 386, 14, 40))
        pygame.draw.circle(s, (62, 62, 68), (205, 316), 15)
        pygame.draw.rect(s, (20, 20, 24), (190, 296, 32, 10))
        z = int(self.t * 1.5) % 3
        for k in range(z + 1):
            draw_text(s, "z", self.font_bold, LIGHT_GREY, (170 - k * 12, 290 - k * 16))
        draw_crate(s, (262, 396, 48, 34))
        pygame.draw.polygon(s, (220, 220, 220), [(272, 378), (294, 378), (291, 396), (275, 396)])
        pygame.draw.arc(s, (220, 220, 220), (289, 382, 12, 10), -1.6, 1.6, 2)
        pygame.draw.ellipse(s, (110, 70, 50), (274, 377, 18, 4))

    def draw_bigtop(self, s):
        # coloured spotlights
        alpha_polygon(s, (255, 220, 120), 30, [(120, TOP_BAR), (150, TOP_BAR), (520, 520), (380, 520)])
        alpha_polygon(s, (255, 120, 200), 26, [(820, TOP_BAR), (850, TOP_BAR), (580, 520), (440, 520)])
        pygame.draw.line(s, (60, 40, 30), (480, TOP_BAR), (480, 70), 8)
        # ring
        pygame.draw.ellipse(s, (120, 30, 40), (210, 440, 540, 120))
        pygame.draw.ellipse(s, (104, 84, 60), (226, 450, 508, 100))
        pygame.draw.ellipse(s, GOLD, (210, 440, 540, 120), 2)
        for k in range(16):
            a = k * math.pi / 8
            pygame.draw.circle(s, (230, 216, 196), (int(480 + 262 * math.cos(a)), int(500 + 57 * math.sin(a))), 3)
        # trapeze with one snapped rope
        pygame.draw.line(s, (200, 190, 170), (430, TOP_BAR), (430, 160), 2)
        pygame.draw.line(s, (200, 190, 170), (540, TOP_BAR), (540, 110), 2)
        for k in range(4):
            pygame.draw.line(s, (200, 190, 170), (540, 110), (536 + k * 3, 120 + k % 2 * 4), 1)
        sway = math.sin(self.t * 1.5) * 4
        pygame.draw.line(s, (180, 180, 186), (430, 160), (450 + sway, 230), 5)
        # safety net
        net = [(330, 300), (630, 300), (610, 345), (350, 345)]
        pygame.draw.polygon(s, (40, 30, 34), net)
        for k in range(16):
            x = 330 + k * 20
            pygame.draw.line(s, (180, 170, 150), (x, 300), (x - 20 + k * 2.5, 345), 1)
            pygame.draw.line(s, (180, 170, 150), (x, 300), (x + 20 - k * 2.5, 345), 1)
        pygame.draw.polygon(s, (200, 190, 170), net, 2)
        for px in (340, 620):
            pygame.draw.line(s, (110, 110, 116), (px, 300), (px, 440), 3)
        # rope ladder with a white smudge
        for lx in (670, 700):
            pygame.draw.line(s, (180, 160, 120), (lx, TOP_BAR), (lx + 6, 430), 2)
        for y in range(80, 430, 22):
            pygame.draw.line(s, (180, 160, 120), (670 + (y - 50) * 0.016, y), (700 + (y - 50) * 0.016, y), 3)
        pygame.draw.ellipse(s, (240, 240, 240), (676, 250, 16, 8))
        pygame.draw.circle(s, (240, 240, 240), (690, 258), 3)
        # bleachers with seat A1
        for row in range(3):
            y = 340 + row * 28
            pygame.draw.rect(s, (60, 26, 34), (160, y, 140, 24))
            pygame.draw.line(s, GOLD, (160, y), (300, y), 1)
            for k in range(6):
                pygame.draw.circle(s, (20, 14, 20), (172 + k * 23, y - 4), 7)
        draw_text(s, "A1", self.font_tiny, GOLD, (176, 404), center=True)
        pygame.draw.rect(s, PAPER, (196, 378, 30, 14))
        pygame.draw.rect(s, RED, (196, 378, 6, 14))
        for k in range(6):
            pygame.draw.circle(s, (240, 230, 190), (250 + k * 9, 420 + (k * 7) % 10), 2)

    def draw_backstage(self, s):
        # mirror with light bulbs
        pygame.draw.rect(s, WOOD_DARK, (250, 110, 170, 130))
        pygame.draw.rect(s, (130, 140, 150), (262, 122, 146, 106))
        alpha_polygon(s, WHITE, 30, [(262, 122), (330, 122), (262, 200)])
        draw_text(s, "A1 - after the show - 5000", self.font_tiny, (245, 245, 245), (335, 190), center=True)
        for k in range(6):
            for bx, by in ((256 + k * 31, 114), (256 + k * 31, 236)):
                pygame.draw.circle(s, YELLOW, (bx, by), 5)
        glow(s, (335, 175), 110, YELLOW, 50)
        # make-up table
        pygame.draw.rect(s, WOOD, (230, 300, 210, 14))
        pygame.draw.rect(s, WOOD_DARK, (240, 314, 10, 116))
        pygame.draw.rect(s, WOOD_DARK, (420, 314, 10, 116))
        for k, c in enumerate(((240, 240, 240), (220, 60, 60), (60, 120, 220), (240, 200, 60))):
            pygame.draw.rect(s, c, (250 + k * 22, 286, 14, 14), border_radius=3)
        pygame.draw.circle(s, RED, (350, 292), 7)
        # Igor's knife
        pygame.draw.polygon(s, (200, 205, 210), [(384, 296), (412, 290), (414, 294), (386, 300)])
        pygame.draw.rect(s, (90, 60, 40), (412, 289, 14, 7), border_radius=2)
        # costume rack
        pygame.draw.line(s, (120, 120, 126), (480, 140), (620, 140), 4)
        for lx in (484, 616):
            pygame.draw.line(s, (120, 120, 126), (lx, 140), (lx, 430), 3)
        for k, c in enumerate(((150, 40, 60), (60, 90, 150), (200, 170, 60), (90, 140, 90), (180, 90, 160))):
            x = 494 + k * 25
            pygame.draw.polygon(s, c, [(x, 146), (x + 22, 146), (x + 28, 300), (x - 6, 300)])
            pygame.draw.line(s, shade(c, 40), (x + 4, 150), (x + 2, 296), 1)
        # lockers 5, 6, 7
        for i, x in enumerate((640, 694, 748)):
            pygame.draw.rect(s, (80, 92, 100), (x, 160, 54, 270))
            pygame.draw.rect(s, (60, 70, 76), (x, 160, 54, 270), 3)
            for v in range(4):
                pygame.draw.line(s, (50, 58, 64), (x + 14, 180 + v * 8), (x + 40, 180 + v * 8), 2)
            pygame.draw.rect(s, (200, 200, 205), (x + 18, 220, 18, 12))
            draw_text(s, str(5 + i), self.font_tiny, BLACK, (x + 27, 226), center=True)
            pygame.draw.rect(s, (150, 150, 156), (x + 40, 290, 6, 20))
        pygame.draw.circle(s, RED, (775, 260), 6)
        if "locker" in self.found:
            pygame.draw.rect(s, BLACK, (752, 164, 46, 262))
            pygame.draw.rect(s, PAPER, (762, 300, 28, 18))

    def draw_fortune(self, s):
        for lx in (300, 660):
            pygame.draw.line(s, (60, 50, 40), (lx, TOP_BAR), (lx, 120), 2)
            pygame.draw.rect(s, (120, 80, 40), (lx - 12, 120, 24, 30), border_radius=6)
            pygame.draw.rect(s, (255, 190, 100), (lx - 8, 124, 16, 22), border_radius=4)
            glow(s, (lx, 135), 70, (255, 170, 80), 80)
        # poster
        pygame.draw.rect(s, (200, 180, 130), (180, 115, 120, 160))
        pygame.draw.rect(s, (90, 40, 90), (180, 115, 120, 160), 4)
        draw_text(s, "MADAME", self.font_small_bold, (90, 30, 90), (240, 135), center=True)
        draw_text(s, "ZORA", self.font_big, (90, 30, 90), (240, 162), center=True)
        pygame.draw.circle(s, (90, 30, 90), (240, 210), 22, 3)
        for k in range(5):
            a = -math.pi / 2 + k * 2 * math.pi / 5
            pygame.draw.circle(s, GOLD, (int(240 + 30 * math.cos(a)), int(210 + 30 * math.sin(a))), 3)
        draw_text(s, "A star will fall!", self.font_tiny, (90, 30, 90), (240, 256), center=True)
        # round table with crystal ball, cards and book
        pygame.draw.ellipse(s, (70, 30, 80), (360, 362, 240, 40))
        pygame.draw.polygon(s, (70, 30, 80), [(362, 382), (598, 382), (620, 430), (340, 430)])
        for k in range(9):
            x = 350 + k * 30
            pygame.draw.line(s, (90, 46, 100), (x, 386), (x - 4 + k, 430), 2)
        pygame.draw.line(s, GOLD, (340, 430), (620, 430), 3)
        glow(s, (481, 343), 70, (120, 220, 255), 70 + 30 * math.sin(self.t * 2))
        pygame.draw.circle(s, (130, 200, 230), (481, 343), 24)
        pygame.draw.circle(s, (220, 245, 255), (472, 334), 6)
        pygame.draw.rect(s, GOLD, (466, 364, 30, 8))
        for k in range(4):
            pygame.draw.rect(s, (220, 210, 180), (524 + k * 16, 364 + k % 2 * 3, 14, 20), border_radius=2)
            pygame.draw.rect(s, (90, 40, 90), (524 + k * 16, 364 + k % 2 * 3, 14, 20), 1, border_radius=2)
        pygame.draw.rect(s, (60, 30, 30), (396, 362, 48, 16))
        pygame.draw.rect(s, PAPER, (400, 360, 40, 14))
        pygame.draw.line(s, INK, (420, 360), (420, 374), 1)
        # incense smoke
        pygame.draw.rect(s, GOLD, (700, 400, 10, 30))
        for k in range(6):
            pygame.draw.circle(s, (120, 110, 130), (int(705 + 6 * math.sin(self.t * 2 + k)), 392 - k * 12), 3)

    def draw_caravans(self, s):
        # distant ferris wheel
        cx, cy = 640, 210
        pygame.draw.circle(s, (60, 50, 80), (cx, cy), 120, 3)
        for k in range(10):
            a = k * math.pi / 5 + self.t * 0.15
            ex, ey = cx + 120 * math.cos(a), cy + 120 * math.sin(a)
            pygame.draw.line(s, (50, 42, 66), (cx, cy), (ex, ey), 1)
            pygame.draw.circle(s, BULB_COLORS[k % 5], (int(ex), int(ey)), 4)
        pygame.draw.line(s, (50, 42, 66), (cx, cy), (cx - 60, 430), 4)
        pygame.draw.line(s, (50, 42, 66), (cx, cy), (cx + 60, 430), 4)
        draw_string_lights(s, (0, 80), (960, 90), 70, self.t, 18)
        # Pip's caravan
        self.draw_caravan(s, (170, 220, 230, 170), (120, 60, 70))
        pygame.draw.rect(s, (90, 40, 50), (330, 280, 50, 110))
        pygame.draw.circle(s, RED, (355, 310), 12)
        pygame.draw.rect(s, (60, 60, 66), (322, 392, 66, 8))
        pygame.draw.polygon(s, (120, 70, 50), [(336, 400), (372, 400), (368, 432), (340, 432)])
        for a in (-0.5, 0, 0.5):
            end = (354 + 20 * math.sin(a), 400 - 26 * math.cos(a))
            pygame.draw.line(s, (60, 100, 60), (354, 400), end, 2)
            pygame.draw.circle(s, (240, 200, 80), (int(end[0]), int(end[1])), 4)
        # Lia's caravan with a lit window
        self.draw_caravan(s, (540, 230, 230, 160), (60, 80, 110))
        pygame.draw.rect(s, (255, 205, 120), (580, 260, 70, 50))
        glow(s, (615, 285), 60, (255, 205, 120), 70)
        pygame.draw.line(s, (60, 80, 110), (615, 260), (615, 310), 3)
        pygame.draw.rect(s, (60, 60, 66), (680, 392, 60, 8))
        pygame.draw.rect(s, (60, 60, 66), (690, 412, 50, 8))
        pygame.draw.ellipse(s, (230, 230, 230), (694, 404, 38, 28))
        pygame.draw.line(s, (180, 180, 180), (700, 410), (726, 410), 2)
        for k in range(5):
            pygame.draw.circle(s, (240, 240, 240), (712 + k * 5, 436 + k % 2), 1)

    def draw_caravan(self, s, rect, color):
        x, y, w, h = rect
        pygame.draw.rect(s, color, (x, y + 20, w, h - 20), border_radius=10)
        pygame.draw.ellipse(s, shade(color, 15), (x - 6, y, w + 12, 50))
        for k in range(0, w, 18):
            pygame.draw.line(s, shade(color, -15), (x + k, y + 40), (x + k, y + h - 10), 1)
        pygame.draw.line(s, GOLD, (x, y + h - 30), (x + w, y + h - 30), 3)
        for wx in (x + 40, x + w - 40):
            pygame.draw.circle(s, (30, 26, 24), (wx, y + h + 8), 22)
            pygame.draw.circle(s, GOLD, (wx, y + h + 8), 22, 3)
            for k in range(6):
                a = k * math.pi / 3
                pygame.draw.line(s, GOLD, (wx, y + h + 8), (wx + 18 * math.cos(a), y + h + 8 + 18 * math.sin(a)), 2)

    def draw_case_item(self, s, rect, art):
        r = pygame.Rect(rect)
        cx, cy = r.center
        if art == "painting":
            vertical_gradient(s, r, (20, 26, 52), (60, 70, 110))
            pygame.draw.circle(s, (240, 235, 200), (r.right - 34, r.y + 28), 14)
            glow(s, (r.right - 34, r.y + 28), 34, (240, 235, 200), 60)
            pygame.draw.polygon(s, (24, 30, 40), [(r.x, r.bottom - 30), (r.x + 50, r.bottom - 52), (r.x + 90, r.bottom - 34),
                                                  (r.right, r.bottom - 48), r.bottomright, r.bottomleft])
            for k in range(5):
                pygame.draw.line(s, (240, 235, 200), (r.right - 50 + k * 4, r.bottom - 26 + k * 4),
                                 (r.right - 30 - k * 3, r.bottom - 26 + k * 4), 1)
            pygame.draw.polygon(s, (60, 40, 30), [(cx - 20, r.bottom - 14), (cx + 16, r.bottom - 14), (cx + 10, r.bottom - 6), (cx - 14, r.bottom - 6)])
            pygame.draw.line(s, (60, 40, 30), (cx - 2, r.bottom - 14), (cx - 2, r.bottom - 40), 2)
            pygame.draw.rect(s, GOLD, r, 6)
        elif art == "necklace":
            pygame.draw.rect(s, (60, 20, 34), r)
            points = []
            for k in range(21):
                a = math.pi * 0.1 + math.pi * 0.8 * k / 20
                points.append((cx - math.cos(a) * 52, r.y + 14 + math.sin(a) * 60))
            for px, py in points:
                pygame.draw.circle(s, (210, 230, 255), (int(px), int(py)), 3)
            star_center = (cx, r.y + 88)
            glow(s, star_center, 40, (170, 215, 255), 120)
            pts = []
            for k in range(10):
                rad = 18 if k % 2 == 0 else 8
                a = -math.pi / 2 + k * math.pi / 5
                pts.append((star_center[0] + rad * math.cos(a), star_center[1] + rad * math.sin(a)))
            pygame.draw.polygon(s, (215, 240, 255), pts)
            pygame.draw.polygon(s, (120, 170, 220), pts, 1)
            pygame.draw.circle(s, WHITE, (star_center[0] - 4, star_center[1] - 6), 2)
        elif art == "formula":
            pygame.draw.rect(s, (30, 60, 110), r)
            for k in range(0, r.w, 12):
                pygame.draw.line(s, (50, 84, 140), (r.x + k, r.y), (r.x + k, r.bottom), 1)
            for k in range(0, r.h, 12):
                pygame.draw.line(s, (50, 84, 140), (r.x, r.y + k), (r.right, r.y + k), 1)
            pygame.draw.rect(s, (220, 230, 250), (cx - 22, cy - 30, 44, 64), 2)
            pygame.draw.rect(s, (220, 230, 250), (cx - 8, cy - 38, 16, 8), 2)
            for k in range(3):
                pygame.draw.line(s, (220, 230, 250), (cx - 14, cy + 20 - k * 16), (cx + 14, cy + 20 - k * 16), 2)
            draw_text(s, "+", self.font_bold, (220, 230, 250), (cx, cy - 18), center=True)
            draw_text(s, "x10", self.font_small_bold, YELLOW, (r.x + 22, r.y + 14), center=True)
            draw_text(s, "Li-C6", self.font_tiny, (220, 230, 250), (r.right - 26, r.bottom - 12), center=True)
        elif art == "egg":
            pygame.draw.rect(s, (40, 22, 30), r)
            glow(s, (cx, cy - 6), 60, GOLD, 90)
            egg = pygame.Rect(cx - 30, cy - 46, 60, 78)
            pygame.draw.ellipse(s, (226, 178, 62), egg)
            pygame.draw.ellipse(s, (250, 215, 120), egg.inflate(-34, -50).move(-8, -14))
            for k in range(-2, 3):
                pygame.draw.arc(s, (150, 100, 30), egg.inflate(-abs(k) * 18, 0), -1.2, 1.2, 1)
            for k, color in enumerate(((210, 40, 60), (40, 170, 90), (210, 40, 60), (40, 170, 90), (210, 40, 60))):
                pygame.draw.circle(s, color, (cx - 20 + k * 10, cy - 6 + (k % 2) * 6), 4)
            pygame.draw.circle(s, (210, 40, 60), (cx, egg.y + 8), 5)
            pygame.draw.polygon(s, (150, 110, 40), [(cx - 22, egg.bottom - 2), (cx + 22, egg.bottom - 2), (cx + 30, r.bottom - 6), (cx - 30, r.bottom - 6)])
        elif art == "trapeze":
            vertical_gradient(s, r, (60, 14, 30), (20, 8, 20))
            alpha_polygon(s, (255, 220, 120), 50, [(cx - 6, r.y), (cx + 6, r.y), (cx + 50, r.bottom), (cx - 50, r.bottom)])
            pygame.draw.line(s, (220, 210, 190), (cx - 34, r.y), (cx - 34, r.y + 60), 2)
            pygame.draw.line(s, (220, 210, 190), (cx + 34, r.y), (cx + 34, r.y + 26), 2)
            pygame.draw.line(s, (220, 210, 190), (cx + 34, r.y + 26), (cx + 30, r.y + 34), 1)
            pygame.draw.line(s, GOLD, (cx - 34, r.y + 60), (cx + 10, r.y + 84), 4)
            # Stella falling into the net
            pygame.draw.circle(s, (230, 230, 230), (cx + 22, r.y + 70), 6)
            pygame.draw.line(s, (230, 230, 230), (cx + 22, r.y + 76), (cx + 32, r.y + 94), 4)
            pygame.draw.line(s, (230, 230, 230), (cx + 26, r.y + 82), (cx + 40, r.y + 76), 2)
            for k in range(9):
                x = r.x + 10 + k * 14
                pygame.draw.line(s, (200, 190, 170), (x, r.bottom - 22), (x + 10, r.bottom - 8), 1)
                pygame.draw.line(s, (200, 190, 170), (x + 10, r.bottom - 22), (x, r.bottom - 8), 1)
            pygame.draw.line(s, (200, 190, 170), (r.x + 6, r.bottom - 22), (r.right - 6, r.bottom - 22), 2)
