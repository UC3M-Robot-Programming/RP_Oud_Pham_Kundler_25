"""Intro scenes: one big picture per case (city, hotel, manor, train, carnival)."""
import math
import random

import pygame

from robot_info.display import (
    BLACK, BULB_COLORS, GOLD, GREY, HEIGHT, LIGHT_GREY, PLAYER_PURPLE, RED, WIDTH,
    YELLOW)
from robot_info.renderer import alpha_polygon, draw_text, glow, shade, vertical_gradient
from robot_info.sprites import draw_person, draw_shadow, draw_string_lights


def scene_city(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, HEIGHT), (12, 13, 18), (52, 56, 66))
    pygame.draw.circle(s, (190, 193, 200), (55, 110), 28)
    pygame.draw.ellipse(s, (34, 37, 44), (10, 118, 110, 18))
    for rect in ((0, 200, 110, 300), (100, 240, 90, 260), (770, 210, 100, 290), (860, 170, 100, 330)):
        pygame.draw.rect(s, (38, 41, 48), rect)
    pygame.draw.polygon(s, (48, 52, 60), [(330, 250), (480, 190), (630, 250)])
    pygame.draw.rect(s, (53, 57, 66), (330, 250, 300, 24))
    for i in range(6):
        pygame.draw.rect(s, (60, 65, 75), (345 + i * 52, 274, 18, 160))
        pygame.draw.line(s, (72, 78, 90), (349 + i * 52, 274), (349 + i * 52, 434), 2)
    pygame.draw.rect(s, (53, 57, 66), (322, 434, 316, 14))
    draw_text(s, "M U S E U M", fonts[0], (130, 135, 145), (480, 234), center=True)
    pygame.draw.rect(s, YELLOW, (470, 330, 16, 26))
    pygame.draw.rect(s, (20, 22, 27), (0, 290, 240, 190))
    pygame.draw.polygon(s, (20, 22, 27), [(0, 290), (120, 245), (240, 290)])
    pygame.draw.rect(s, (20, 22, 27), (700, 300, 260, 180))
    for x, y, lit in ((30, 320, 1), (80, 320, 0), (180, 320, 1), (30, 390, 0),
                      (180, 390, 0), (730, 330, 0), (790, 330, 1), (850, 330, 0), (730, 400, 1)):
        pygame.draw.rect(s, YELLOW if lit else (45, 45, 40), (x, y, 24, 32))
        pygame.draw.line(s, (20, 22, 27), (x + 12, y), (x + 12, y + 32), 2)
    pygame.draw.rect(s, (28, 30, 36), (840, 400, 80, 26))
    pygame.draw.rect(s, GREY, (840, 400, 80, 26), 1)
    draw_text(s, "BAR", fonts[0], LIGHT_GREY, (880, 413), center=True)
    pygame.draw.rect(s, (27, 30, 36), (0, 470, WIDTH, 130))
    pygame.draw.rect(s, (42, 46, 54), (0, 470, WIDTH, 16))
    for x in range(0, WIDTH, 70):
        pygame.draw.rect(s, (55, 60, 70), (x, 545, 40, 4))
    alpha_polygon(s, YELLOW, 45, [(648, 170), (672, 170), (790, 486), (530, 486)])
    pygame.draw.rect(s, BLACK, (656, 170, 8, 316))
    pygame.draw.polygon(s, BLACK, [(636, 168), (684, 168), (674, 148), (646, 148)])
    pygame.draw.rect(s, YELLOW, (644, 166, 32, 7))
    glow(s, (660, 170), 80, YELLOW, 120)
    pygame.draw.ellipse(s, (55, 62, 76), (220, 495, 200, 28))
    draw_person(s, 320, 500, "detective", RED, body=PLAYER_PURPLE)
    for i, (x, y) in enumerate(((410, 492), (428, 484), (440, 476), (455, 468), (463, 460))):
        pygame.draw.ellipse(s, RED, (x - 6 + i, y, 12 - i, 6 - i // 2))
    glow(s, (425, 486), 30, RED, 90)


def scene_hotel(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, HEIGHT), (22, 14, 30), (74, 46, 52))
    rng = random.Random(4)
    for x in range(0, WIDTH, 90):
        h = rng.randint(180, 320)
        pygame.draw.rect(s, (36, 28, 38), (x, 470 - h, 86, h))
        for wy in range(470 - h + 15, 450, 28):
            for wx in range(x + 10, x + 80, 22):
                if rng.random() < 0.3:
                    pygame.draw.rect(s, (120, 90, 60), (wx, wy, 10, 14))
    # hotel facade
    pygame.draw.rect(s, (66, 52, 48), (270, 130, 420, 350))
    pygame.draw.rect(s, (86, 70, 62), (260, 120, 440, 14))
    for row in range(6):
        for col in range(7):
            wx, wy = 292 + col * 56, 150 + row * 46
            lit = rng.random() < 0.6
            pygame.draw.rect(s, (255, 205, 120) if lit else (40, 34, 36), (wx, wy, 30, 30))
            pygame.draw.line(s, (66, 52, 48), (wx + 15, wy), (wx + 15, wy + 30), 2)
            pygame.draw.rect(s, (96, 80, 70), (wx - 4, wy + 30, 38, 4))
    # neon sign
    pygame.draw.rect(s, (20, 14, 20), (330, 64, 300, 52), border_radius=6)
    for r in (120, 80):
        glow(s, (480, 90), r, (255, 80, 150), 40)
    draw_text(s, "HOTEL AURORA", fonts[1], (255, 120, 180), (480, 90), center=True)
    # entrance with awning and revolving door
    pygame.draw.rect(s, (255, 205, 120), (440, 400, 80, 70))
    pygame.draw.line(s, (90, 70, 50), (480, 400), (480, 470), 3)
    pygame.draw.polygon(s, (120, 30, 40), [(400, 384), (560, 384), (585, 410), (375, 410)])
    for k in range(8):
        pygame.draw.line(s, (160, 50, 60), (385 + k * 26, 410), (405 + k * 20, 384), 2)
    # street with reflections
    pygame.draw.rect(s, (24, 20, 28), (0, 470, WIDTH, 130))
    pygame.draw.rect(s, (46, 38, 44), (0, 470, WIDTH, 14))
    for x, c in ((480, (255, 80, 150)), (330, (255, 205, 120)), (620, (255, 205, 120))):
        alpha_polygon(s, c, 45, [(x - 30, 486), (x + 30, 486), (x + 12, 600), (x - 12, 600)])
    # car
    pygame.draw.polygon(s, (14, 14, 16), [(600, 470), (610, 440), (660, 425), (760, 425),
                                          (800, 445), (840, 450), (845, 470)])
    for wx in (640, 800):
        pygame.draw.circle(s, BLACK, (wx, 472), 16)
        pygame.draw.circle(s, (60, 60, 66), (wx, 472), 7)
    pygame.draw.circle(s, YELLOW, (842, 456), 5)
    glow(s, (842, 456), 30, YELLOW, 90)
    draw_shadow(s, 190, 500)
    draw_person(s, 190, 500, "detective", RED, body=PLAYER_PURPLE)


def scene_manor(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, HEIGHT), (10, 14, 16), (44, 50, 52))
    for cx, cy, w in ((150, 90, 300), (520, 60, 380), (820, 120, 260)):
        pygame.draw.ellipse(s, (30, 34, 38), (cx - w // 2, cy - 30, w, 70))
    bolt = [(760, 40), (740, 120), (770, 120), (735, 230), (800, 105), (770, 105), (795, 40)]
    glow(s, (770, 130), 120, (180, 200, 255), 50)
    pygame.draw.polygon(s, (220, 230, 255), bolt)
    pygame.draw.polygon(s, (16, 20, 18), [(0, 420), (200, 360), (480, 330), (760, 350), (960, 400),
                                          (960, 600), (0, 600)])
    # mansion
    dark = (24, 26, 28)
    pygame.draw.rect(s, dark, (300, 210, 360, 150))
    for tx in (290, 620):
        pygame.draw.rect(s, dark, (tx, 160, 50, 200))
        pygame.draw.polygon(s, dark, [(tx - 8, 160), (tx + 25, 100), (tx + 58, 160)])
    pygame.draw.polygon(s, dark, [(330, 210), (480, 150), (630, 210)])
    pygame.draw.rect(s, dark, (520, 150, 16, 40))
    rng = random.Random(9)
    for row in range(3):
        for col in range(8):
            wx, wy = 318 + col * 42, 226 + row * 40
            lit = rng.random() < 0.25
            pygame.draw.rect(s, YELLOW if lit else (40, 44, 46), (wx, wy, 18, 24))
            if lit:
                glow(s, (wx + 9, wy + 12), 20, YELLOW, 60)
    pygame.draw.rect(s, (60, 44, 30), (462, 316, 36, 44))
    # dead tree
    def branch(x, y, angle, length, width):
        if length < 8:
            return
        x2 = x + length * math.cos(angle)
        y2 = y - length * math.sin(angle)
        pygame.draw.line(s, (14, 16, 14), (x, y), (x2, y2), width)
        branch(x2, y2, angle + 0.45, length * 0.7, max(1, width - 2))
        branch(x2, y2, angle - 0.35, length * 0.68, max(1, width - 2))
    branch(140, 420, math.pi / 2, 90, 10)
    # iron fence
    for x in range(0, WIDTH, 18):
        if 420 < x < 540:
            continue
        pygame.draw.line(s, (10, 10, 12), (x, 470), (x, 560), 4)
        pygame.draw.polygon(s, (10, 10, 12), [(x - 5, 472), (x, 458), (x + 5, 472)])
    pygame.draw.rect(s, (10, 10, 12), (0, 490, 420, 5))
    pygame.draw.rect(s, (10, 10, 12), (540, 490, 420, 5))
    draw_shadow(s, 480, 575)
    draw_person(s, 480, 575, "detective", RED, body=PLAYER_PURPLE)


def scene_train(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, 440), (8, 12, 30), (46, 60, 96))
    rng = random.Random(3)
    for _ in range(90):
        pygame.draw.circle(s, (220, 225, 240), (rng.randint(0, WIDTH), rng.randint(0, 260)), 1)
    glow(s, (790, 100), 110, (200, 210, 255), 60)
    pygame.draw.circle(s, (230, 232, 240), (790, 100), 40)
    pygame.draw.circle(s, (200, 204, 216), (775, 92), 8)
    for color, base, peaks in (((48, 58, 86), 330, [(0, 300), (140, 170), (260, 280), (420, 150),
                                                    (600, 290), (760, 180), (960, 300)]),
                               ((34, 42, 64), 380, [(0, 350), (180, 230), (330, 340), (520, 220),
                                                    (700, 340), (880, 240), (960, 300)])):
        pygame.draw.polygon(s, color, peaks + [(960, 440), (0, 440)])
        for px, py in peaks[1:-1]:
            if py < 300:
                pygame.draw.polygon(s, (215, 220, 232), [(px, py), (px - 28, py + 30), (px - 8, py + 22),
                                                         (px + 6, py + 32), (px + 26, py + 30)])
    pygame.draw.rect(s, (200, 206, 218), (0, 430, WIDTH, 170))
    vertical_gradient(s, (0, 470, WIDTH, 130), (200, 206, 218), (150, 158, 176))
    pygame.draw.rect(s, (60, 56, 52), (0, 452, WIDTH, 6))
    for x in range(0, WIDTH, 26):
        pygame.draw.rect(s, (90, 80, 70), (x, 456, 14, 6))
    # train cars with warm windows
    for cx in (40, 230, 420):
        pygame.draw.rect(s, (40, 26, 24), (cx, 350, 180, 90), border_radius=6)
        pygame.draw.rect(s, (60, 36, 32), (cx, 344, 180, 10), border_radius=4)
        pygame.draw.rect(s, (220, 225, 235), (cx + 4, 340, 172, 5))
        for wx in range(cx + 14, cx + 170, 32):
            pygame.draw.rect(s, (255, 205, 120), (wx, 368, 20, 26))
            glow(s, (wx + 10, 381), 24, (255, 205, 120), 50)
        pygame.draw.line(s, GOLD, (cx, 410), (cx + 180, 410), 2)
        for wx in (cx + 30, cx + 150):
            pygame.draw.circle(s, BLACK, (wx, 444), 12)
    # locomotive
    pygame.draw.rect(s, (22, 22, 26), (610, 330, 130, 110))
    pygame.draw.rect(s, (22, 22, 26), (730, 360, 110, 80), border_radius=20)
    pygame.draw.rect(s, (22, 22, 26), (780, 320, 26, 44))
    pygame.draw.rect(s, (255, 205, 120), (630, 350, 34, 30))
    for k in range(5):
        glow(s, (795 - k * 30, 300 - k * 45), 30 + k * 10, (160, 165, 180), 60)
    pygame.draw.circle(s, YELLOW, (842, 395), 8)
    alpha_polygon(s, YELLOW, 50, [(842, 388), (960, 340), (960, 470), (842, 402)])
    for wx in (650, 700, 760, 810):
        pygame.draw.circle(s, BLACK, (wx, 442), 15)
        pygame.draw.circle(s, (70, 70, 76), (wx, 442), 5)
    # pine trees
    for tx, ty, h in ((20, 520, 120), (100, 560, 90), (900, 540, 130)):
        for k in range(4):
            w = 40 - k * 7
            y = ty - k * h // 4
            pygame.draw.polygon(s, (16, 30, 24), [(tx - w, y), (tx + w, y), (tx, y - h // 3)])
            pygame.draw.line(s, (220, 225, 235), (tx - w + 6, y - 2), (tx - 4, y - h // 3 + 8), 2)
    draw_shadow(s, 480, 560)
    draw_person(s, 480, 560, "detective", RED, body=PLAYER_PURPLE)


def scene_carnival(s, fonts):
    vertical_gradient(s, (0, 0, WIDTH, HEIGHT), (10, 8, 30), (56, 22, 62))
    rng = random.Random(5)
    for _ in range(70):
        pygame.draw.circle(s, (230, 220, 255), (rng.randint(0, WIDTH), rng.randint(0, 250)), 1)
    # ferris wheel
    cx, cy, r = 200, 250, 150
    pygame.draw.line(s, (60, 50, 70), (cx, cy), (cx - 90, 480), 6)
    pygame.draw.line(s, (60, 50, 70), (cx, cy), (cx + 90, 480), 6)
    pygame.draw.circle(s, (80, 66, 90), (cx, cy), r, 4)
    pygame.draw.circle(s, (80, 66, 90), (cx, cy), r - 20, 2)
    for k in range(12):
        a = k * math.pi / 6
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        pygame.draw.line(s, (70, 58, 80), (cx, cy), (ex, ey), 2)
        pygame.draw.rect(s, BULB_COLORS[k % 5], (ex - 10, ey + 4, 20, 14), border_radius=4)
    for k in range(36):
        a = k * math.pi / 18
        bx, by = cx + r * math.cos(a), cy + r * math.sin(a)
        pygame.draw.circle(s, BULB_COLORS[k % 5], (int(bx), int(by)), 3)
    glow(s, (cx, cy), 60, (255, 210, 90), 60)
    # big top tent
    peak = (670, 130)
    left, right = 470, 870
    for k in range(10):
        x1 = left + k * (right - left) / 10
        x2 = left + (k + 1) * (right - left) / 10
        color = (170, 40, 52) if k % 2 == 0 else (230, 216, 196)
        pygame.draw.polygon(s, color, [peak, (x1, 320), (x2, 320)])
        pygame.draw.polygon(s, shade(color, -30), [(x1, 320), (x2, 320), (x2, 470), (x1, 470)])
    for k in range(10):
        x = left + k * 40 + 20
        pygame.draw.circle(s, (230, 216, 196), (int(x), 322), 18, 0, draw_bottom_left=True,
                           draw_bottom_right=True)
    pygame.draw.line(s, (60, 40, 30), peak, (670, 90), 4)
    pygame.draw.polygon(s, RED, [(670, 90), (705, 100), (670, 110)])
    pygame.draw.polygon(s, (20, 10, 14), [(630, 470), (670, 370), (710, 470)])
    glow(s, (670, 450), 60, (255, 205, 120), 90)
    draw_string_lights(s, (0, 110), (470, 300), 60, 0)
    draw_string_lights(s, (870, 300), (960, 200), 20, 0, 5)
    pygame.draw.rect(s, (22, 16, 26), (0, 470, WIDTH, 130))
    pygame.draw.polygon(s, (40, 30, 40), [(600, 470), (740, 470), (820, 600), (520, 600)])
    # ticket booth
    pygame.draw.rect(s, (110, 30, 40), (380, 390, 70, 80))
    pygame.draw.polygon(s, (230, 216, 196), [(370, 390), (460, 390), (415, 360)])
    pygame.draw.rect(s, (255, 205, 120), (392, 408, 46, 26))
    draw_text(s, "TICKETS", fonts[0], (230, 216, 196), (415, 448), center=True)
    draw_shadow(s, 320, 545)
    draw_person(s, 320, 545, "detective", RED, body=PLAYER_PURPLE)


SCENES = {"city": scene_city, "hotel": scene_hotel, "manor": scene_manor,
          "train": scene_train, "carnival": scene_carnival}
