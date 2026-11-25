"""Sprites: people, moving obstacles and props, all drawn with pygame shapes."""
import math
import random

import pygame

from robot_info.display import (
    BLACK, BRASS, BULB_COLORS, GOLD, GREY, ORANGE, RED, TOP_BAR, WHITE, WOOD, WOOD_DARK,
    YELLOW)
from robot_info.renderer import alpha_ellipse, glow, shade


def draw_shadow(s, x, fy, width=90):
    alpha_ellipse(s, BLACK, 110, (x - width // 2, fy - 8, width, 18))


def draw_person(s, x, fy, style, accent, body=None, step=0.0):
    """Draws a figure standing with its feet at (x, fy). step makes the legs walk."""
    body = body or (16, 16, 20)
    rim = shade(body, 28)
    skin = (225, 225, 225) if style == "clown" else (62, 62, 68)
    hair = (26, 26, 30)
    wide = style in ("countess", "pianist", "singer", "fortune")
    big = style == "strongman"
    left_foot = x - 10 + int(step * 9)
    right_foot = x + 10 - int(step * 9)
    pygame.draw.line(s, body, (x - 10, fy - 60), (left_foot, fy - 4), 13)
    pygame.draw.line(s, body, (x + 10, fy - 60), (right_foot, fy - 4), 13)
    pygame.draw.ellipse(s, body, (left_foot - 12, fy - 6, 22, 10))
    pygame.draw.ellipse(s, body, (right_foot - 10, fy - 6, 22, 10))
    sh = 34 if big else 24
    if wide:
        torso = [(x - 42, fy), (x + 42, fy), (x + 24, fy - 132), (x - 24, fy - 132)]
    else:
        torso = [(x - 30, fy - 55), (x + 30, fy - 55), (x + sh, fy - 132), (x - sh, fy - 132)]
    pygame.draw.polygon(s, body, torso)
    arm_l = [(x - sh, fy - 130), (x - sh - 10, fy - 127), (x - sh - 16, fy - 70), (x - sh - 6, fy - 68)]
    arm_r = [(x + sh, fy - 130), (x + sh + 10, fy - 127), (x + sh + 16, fy - 70), (x + sh + 6, fy - 68)]
    pygame.draw.polygon(s, body, arm_l)
    pygame.draw.polygon(s, body, arm_r)
    # rim light on the right side makes the figures look less flat
    pygame.draw.line(s, rim, torso[1] if wide else (x + 30, fy - 55), torso[2], 2)
    pygame.draw.line(s, rim, arm_r[1], arm_r[2], 2)

    # hair / scarves behind the head
    if style in ("weber", "countess", "labcoat"):
        pygame.draw.circle(s, hair, (x, fy - 178), 9)
        pygame.draw.circle(s, hair, (x, fy - 158), 20)
    elif style in ("pianist", "acrobat"):
        pygame.draw.rect(s, hair, (x - 21, fy - 165, 42, 45), border_radius=8)
        pygame.draw.circle(s, hair, (x, fy - 158), 21)
    elif style == "journalist":
        pygame.draw.rect(s, hair, (x - 21, fy - 168, 42, 28), border_radius=8)
    elif style == "singer":
        for dx, dy in ((-16, -168), (0, -176), (16, -168), (-20, -150), (20, -150)):
            pygame.draw.circle(s, hair, (x + dx, fy + dy), 12)
    elif style == "doctor":
        pygame.draw.polygon(s, accent, [(x - 24, fy - 128), (x + 24, fy - 128), (x + 20, fy - 150),
                                        (x - 20, fy - 150)])
        pygame.draw.circle(s, accent, (x, fy - 157), 22)
    elif style == "fortune":
        pygame.draw.polygon(s, accent, [(x - 22, fy - 160), (x + 22, fy - 160), (x + 30, fy - 120),
                                        (x - 30, fy - 120)])
        pygame.draw.circle(s, accent, (x, fy - 160), 21)
    pygame.draw.rect(s, skin, (x - 6, fy - 142, 12, 12))
    head_r = 14 if style == "doctor" else 17
    pygame.draw.circle(s, skin, (x, fy - 155), head_r)
    eye = BLACK if style == "clown" else (120, 120, 128)
    pygame.draw.circle(s, eye, (x - 6, fy - 158), 2)
    pygame.draw.circle(s, eye, (x + 6, fy - 158), 2)

    if style == "detective":
        pygame.draw.polygon(s, body, [(x - 30, fy - 132), (x, fy - 112), (x + 30, fy - 132)])
        pygame.draw.ellipse(s, body, (x - 32, fy - 174, 64, 11))
        pygame.draw.rect(s, body, (x - 18, fy - 196, 36, 26), border_radius=6)
        pygame.draw.rect(s, (70, 30, 30), (x - 18, fy - 176, 36, 5))
    elif style == "karl":
        pygame.draw.rect(s, accent, (x - 20, fy - 112, 40, 58))
        pygame.draw.line(s, accent, (x - 16, fy - 112), (x - 12, fy - 130), 4)
        pygame.draw.line(s, accent, (x + 16, fy - 112), (x + 12, fy - 130), 4)
        pygame.draw.rect(s, shade(accent, -30), (x - 10, fy - 104, 20, 14))
        pygame.draw.ellipse(s, accent, (x - 18, fy - 178, 36, 18))
        pygame.draw.rect(s, accent, (x, fy - 168, 26, 5))
    elif style == "weber":
        pygame.draw.polygon(s, accent, [(x - 15, fy - 138), (x + 15, fy - 138),
                                        (x + 8, fy - 108), (x - 2, fy - 116)])
        pygame.draw.line(s, accent, (x - 5, fy - 146), (x + 5, fy - 146), 3)
    elif style == "leon":
        pygame.draw.ellipse(s, accent, (x - 22, fy - 180, 42, 15))
        pygame.draw.circle(s, accent, (x, fy - 181), 3)
        pygame.draw.rect(s, accent, (x - 16, fy - 137, 32, 8))
        pygame.draw.rect(s, accent, (x + 6, fy - 132, 9, 48))
    elif style == "ole":
        pygame.draw.rect(s, body, (x - 18, fy - 180, 36, 15), border_radius=4)
        pygame.draw.rect(s, body, (x - 22, fy - 168, 44, 5))
        pygame.draw.circle(s, accent, (x, fy - 173), 3)
        pygame.draw.circle(s, accent, (x - 13, fy - 112), 5)
    elif style == "countess":
        pygame.draw.polygon(s, accent, [(x - 10, fy - 172), (x - 5, fy - 184), (x, fy - 174),
                                        (x + 5, fy - 184), (x + 10, fy - 172)])
        pygame.draw.arc(s, accent, (x - 30, fy - 150, 60, 50), math.pi, 2 * math.pi, 6)
        pygame.draw.line(s, (90, 90, 96), (x - 9, fy - 132), (x + 9, fy - 132), 2)
    elif style == "manager":
        pygame.draw.arc(s, hair, (x - 18, fy - 174, 36, 30), 0, math.pi, 7)
        pygame.draw.polygon(s, WHITE, [(x - 9, fy - 132), (x + 9, fy - 132), (x, fy - 112)])
        pygame.draw.polygon(s, accent, [(x - 10, fy - 134), (x, fy - 129), (x - 10, fy - 124)])
        pygame.draw.polygon(s, accent, [(x + 10, fy - 134), (x, fy - 129), (x + 10, fy - 124)])
    elif style == "chef":
        pygame.draw.rect(s, (210, 210, 210), (x - 15, fy - 196, 30, 26))
        for cx in (x - 10, x, x + 10):
            pygame.draw.circle(s, (210, 210, 210), (cx, fy - 196), 9)
        pygame.draw.rect(s, (190, 190, 190), (x - 20, fy - 115, 40, 75))
        pygame.draw.polygon(s, accent, [(x - 12, fy - 136), (x + 12, fy - 136), (x, fy - 122)])
    elif style == "pianist":
        pygame.draw.rect(s, accent, (x - 22, fy - 172, 12, 6))
        pygame.draw.circle(s, accent, (x, fy - 118), 5)
    elif style == "labcoat":
        pygame.draw.polygon(s, (200, 200, 200), [(x - 32, fy - 40), (x - 4, fy - 40),
                                                 (x - 4, fy - 128), (x - 24, fy - 132)])
        pygame.draw.polygon(s, (200, 200, 200), [(x + 32, fy - 40), (x + 4, fy - 40),
                                                 (x + 4, fy - 128), (x + 24, fy - 132)])
        pygame.draw.circle(s, accent, (x - 7, fy - 157), 6, 2)
        pygame.draw.circle(s, accent, (x + 7, fy - 157), 6, 2)
    elif style == "nephew":
        for hx in range(x - 16, x + 17, 8):
            pygame.draw.circle(s, hair, (hx, fy - 170), 7)
        for y in (fy - 120, fy - 100, fy - 80):
            pygame.draw.line(s, accent, (x - 26, y), (x + 26, y), 4)
    elif style == "butler":
        pygame.draw.polygon(s, WHITE, [(x - 10, fy - 132), (x + 10, fy - 132), (x, fy - 100)])
        pygame.draw.polygon(s, body, [(x - 9, fy - 133), (x, fy - 128), (x - 9, fy - 123)])
        pygame.draw.polygon(s, body, [(x + 9, fy - 133), (x, fy - 128), (x + 9, fy - 123)])
        pygame.draw.arc(s, (110, 110, 116), (x - 10, fy - 170, 14, 10), 0.5, 2.5, 2)
        pygame.draw.ellipse(s, accent, (x + 30, fy - 100, 50, 10))
    elif style == "journalist":
        pygame.draw.line(s, accent, (x - 20, fy - 132), (x + 4, fy - 100), 2)
        pygame.draw.rect(s, accent, (x - 6, fy - 108, 24, 16), border_radius=3)
        pygame.draw.circle(s, body, (x + 6, fy - 100), 5)
    elif style == "partner":
        pygame.draw.rect(s, body, (x - 15, fy - 210, 30, 38))
        pygame.draw.rect(s, body, (x - 24, fy - 175, 48, 6))
        pygame.draw.rect(s, (150, 40, 40), (x - 15, fy - 182, 30, 5))
        pygame.draw.line(s, hair, (x - 8, fy - 147), (x + 8, fy - 147), 3)
        pygame.draw.line(s, (120, 90, 60), (x + 6, fy - 143), (x + 24, fy - 140), 3)
        pygame.draw.circle(s, accent, (x + 25, fy - 140), 3)
    elif style == "conductor":
        pygame.draw.rect(s, body, (x - 18, fy - 182, 36, 16), border_radius=3)
        pygame.draw.rect(s, body, (x - 4, fy - 170, 26, 5))
        pygame.draw.circle(s, accent, (x, fy - 175), 4)
        for row in range(4):
            pygame.draw.circle(s, accent, (x - 8, fy - 120 + row * 16), 3)
            pygame.draw.circle(s, accent, (x + 8, fy - 120 + row * 16), 3)
        pygame.draw.line(s, accent, (x + 8, fy - 70), (x + 26, fy - 58), 2)
    elif style == "singer":
        pygame.draw.arc(s, accent, (x - 34, fy - 148, 68, 52), math.pi, 2 * math.pi, 7)
        for k in range(7):
            a = math.pi + k * math.pi / 6
            pygame.draw.circle(s, accent, (int(x + 34 * math.cos(a)), int(fy - 122 - 26 * math.sin(a))), 5)
        pygame.draw.circle(s, accent, (x - 15, fy - 146), 3)
        pygame.draw.circle(s, accent, (x + 15, fy - 146), 3)
        pygame.draw.line(s, RED, (x - 5, fy - 147), (x + 5, fy - 147), 3)
    elif style == "baron":
        pygame.draw.line(s, accent, (x - 22, fy - 128), (x + 24, fy - 62), 6)
        pygame.draw.circle(s, accent, (x + 6, fy - 158), 6, 2)
        pygame.draw.line(s, accent, (x + 12, fy - 156), (x + 18, fy - 130), 1)
        pygame.draw.arc(s, hair, (x - 16, fy - 152, 16, 10), 0, math.pi, 3)
        pygame.draw.arc(s, hair, (x, fy - 152, 16, 10), 0, math.pi, 3)
        pygame.draw.circle(s, accent, (x - 12, fy - 112), 5)
    elif style == "doctor":
        pygame.draw.arc(s, (190, 190, 200), (x - 16, fy - 140, 32, 40), math.pi, 2 * math.pi, 2)
        pygame.draw.line(s, (190, 190, 200), (x + 16, fy - 120), (x + 14, fy - 92), 2)
        pygame.draw.circle(s, (190, 190, 200), (x + 14, fy - 88), 5)
    elif style == "waiter":
        pygame.draw.polygon(s, (205, 205, 205), [(x - 30, fy - 70), (x + 30, fy - 70),
                                                 (x + 24, fy - 132), (x - 24, fy - 132)])
        pygame.draw.polygon(s, body, [(x - 9, fy - 134), (x, fy - 129), (x - 9, fy - 124)])
        pygame.draw.polygon(s, body, [(x + 9, fy - 134), (x, fy - 129), (x + 9, fy - 124)])
        pygame.draw.ellipse(s, accent, (x + 28, fy - 104, 46, 9))
        pygame.draw.rect(s, (200, 220, 230), (x + 46, fy - 120, 8, 16))
        pygame.draw.arc(s, hair, (x - 18, fy - 174, 36, 26), 0, math.pi, 6)
    elif style == "ringmaster":
        pygame.draw.polygon(s, (120, 28, 34), [(x - 30, fy - 55), (x - 4, fy - 55),
                                               (x - 4, fy - 130), (x - 24, fy - 132)])
        pygame.draw.polygon(s, (120, 28, 34), [(x + 30, fy - 55), (x + 4, fy - 55),
                                               (x + 4, fy - 130), (x + 24, fy - 132)])
        for row in range(3):
            pygame.draw.circle(s, GOLD, (x - 10, fy - 118 + row * 18), 3)
        pygame.draw.rect(s, body, (x - 16, fy - 214, 32, 42))
        pygame.draw.rect(s, body, (x - 26, fy - 176, 52, 6))
        pygame.draw.rect(s, accent, (x - 16, fy - 186, 32, 6))
        pygame.draw.arc(s, hair, (x - 18, fy - 152, 18, 12), 0, math.pi, 3)
        pygame.draw.arc(s, hair, (x, fy - 152, 18, 12), 0, math.pi, 3)
    elif style == "clown":
        for dx in (-22, -16, 16, 22):
            pygame.draw.circle(s, ORANGE, (x + dx, fy - 162 + abs(dx) // 3), 8)
        pygame.draw.circle(s, accent, (x, fy - 151), 6)
        pygame.draw.arc(s, accent, (x - 9, fy - 152, 18, 12), math.pi + 0.3, 2 * math.pi - 0.3, 2)
        for k in range(6):
            pygame.draw.circle(s, WHITE, (x - 20 + k * 8, fy - 134), 6)
        for px, py in ((x - 12, fy - 112), (x + 10, fy - 96), (x - 6, fy - 78), (x + 14, fy - 66)):
            pygame.draw.circle(s, accent, (px, py), 5)
    elif style == "acrobat":
        pygame.draw.polygon(s, accent, [(x - 22, fy - 55), (x + 22, fy - 55),
                                        (x + 22, fy - 128), (x - 22, fy - 128)])
        pygame.draw.line(s, WHITE, (x - 20, fy - 120), (x + 20, fy - 70), 2)
        pygame.draw.circle(s, hair, (x + 18, fy - 168), 8)
        pygame.draw.line(s, hair, (x + 22, fy - 166), (x + 30, fy - 140), 6)
    elif style == "fortune":
        for k in range(5):
            pygame.draw.circle(s, GOLD, (x - 16 + k * 8, fy - 170), 3)
        pygame.draw.circle(s, GOLD, (x - 17, fy - 142), 7, 2)
        pygame.draw.circle(s, GOLD, (x + 17, fy - 142), 7, 2)
        pygame.draw.polygon(s, shade(accent, -40), [(x - 32, fy - 128), (x + 32, fy - 128), (x, fy - 80)])
    elif style == "strongman":
        for y in range(int(fy - 126), int(fy - 56), 10):
            pygame.draw.line(s, accent, (x - 28, y), (x + 28, y), 4)
        pygame.draw.arc(s, hair, (x - 22, fy - 152, 22, 16), 0, math.pi, 4)
        pygame.draw.arc(s, hair, (x, fy - 152, 22, 16), 0, math.pi, 4)
        pygame.draw.circle(s, (80, 80, 86), (x - 4, fy - 166), 4)
    elif style == "rival":
        pygame.draw.polygon(s, (54, 56, 62), [(x - 30, fy - 55), (x + 30, fy - 55),
                                              (x + 24, fy - 132), (x - 24, fy - 132)])
        pygame.draw.polygon(s, WHITE, [(x - 8, fy - 132), (x + 8, fy - 132), (x, fy - 108)])
        pygame.draw.line(s, (30, 30, 34), (x, fy - 130), (x, fy - 104), 3)
        pygame.draw.circle(s, accent, (x + 2, fy - 118), 2)
        pygame.draw.ellipse(s, body, (x - 22, fy - 176, 44, 10))
        pygame.draw.ellipse(s, body, (x - 15, fy - 192, 30, 24))
        pygame.draw.line(s, (90, 70, 50), (x + 44, fy - 70), (x + 52, fy), 3)


def draw_tick(s, pos):
    x, y = pos
    pygame.draw.circle(s, BLACK, pos, 11)
    pygame.draw.circle(s, GOLD, pos, 11, 2)
    pygame.draw.lines(s, GOLD, False, [(x - 5, y), (x - 1, y + 4), (x + 6, y - 5)], 3)


def draw_crate(s, rect):
    x, y, w, h = rect
    pygame.draw.rect(s, WOOD, rect)
    for k in range(1, 4):
        pygame.draw.line(s, shade(WOOD, -10), (x, y + k * h // 4), (x + w, y + k * h // 4), 1)
    pygame.draw.rect(s, WOOD_DARK, rect, 4)
    pygame.draw.line(s, WOOD_DARK, (x, y), (x + w, y + h), 4)
    pygame.draw.line(s, shade(WOOD, 18), (x + 4, y + 4), (x + w - 4, y + 4), 1)


def draw_suitcase(s, rect, color):
    r = pygame.Rect(rect)
    pygame.draw.rect(s, color, r, border_radius=6)
    pygame.draw.rect(s, shade(color, -25), r, 2, border_radius=6)
    pygame.draw.rect(s, shade(color, -25), (r.centerx - 12, r.y - 8, 24, 10), 3, border_radius=3)
    for bx in (r.x + 12, r.right - 18):
        pygame.draw.rect(s, BRASS, (bx, r.y + 4, 6, 8))
    pygame.draw.line(s, shade(color, 20), (r.x + 6, r.y + 3), (r.right - 6, r.y + 3), 1)


def draw_chandelier(s, x, y, lit=True):
    pygame.draw.line(s, BLACK, (x, TOP_BAR), (x, y), 2)
    pygame.draw.arc(s, (120, 110, 80), (x - 50, y - 10, 100, 30), math.pi, 2 * math.pi, 3)
    for dx in (-45, -22, 0, 22, 45):
        cy = y + 5 - abs(dx) // 10
        pygame.draw.rect(s, (200, 200, 200), (x + dx - 2, cy - 10, 4, 10))
        pygame.draw.line(s, (170, 190, 200), (x + dx, cy + 2), (x + dx, cy + 12), 1)
        if lit:
            pygame.draw.circle(s, YELLOW, (x + dx, cy - 13), 3)
    if lit:
        glow(s, (x, y), 80, YELLOW, 70)


def draw_wall_lamp(s, x, y, color=YELLOW):
    pygame.draw.rect(s, BRASS, (x - 3, y, 6, 18))
    pygame.draw.polygon(s, (220, 200, 160), [(x - 12, y - 6), (x + 12, y - 6), (x + 8, y - 22), (x - 8, y - 22)])
    glow(s, (x, y - 10), 45, color, 70)


def draw_shelf_of_books(s, rect, seed):
    x, y, w, h = rect
    pygame.draw.rect(s, WOOD_DARK, rect)
    rng = random.Random(seed)
    for row in range(5):
        by = y + 12 + row * (h - 20) // 5
        bx = x + 8
        while bx < x + w - 14:
            bw = rng.randint(8, 16)
            bh = rng.randint(35, 50)
            tone = rng.randint(55, 105)
            book = (tone, tone - 6, tone - 10)
            pygame.draw.rect(s, book, (bx, by + 52 - bh, bw, bh))
            pygame.draw.line(s, shade(book, 25), (bx + 2, by + 56 - bh), (bx + bw - 3, by + 56 - bh), 1)
            bx += bw + 2
        pygame.draw.rect(s, WOOD, (x, by + 52, w, 8))
    pygame.draw.rect(s, WOOD, rect, 6)


def draw_string_lights(s, start, end, sag, t, count=14):
    (x1, y1), (x2, y2) = start, end
    points = []
    for i in range(41):
        f = i / 40
        points.append((x1 + (x2 - x1) * f, y1 + (y2 - y1) * f + sag * 4 * f * (1 - f)))
    pygame.draw.lines(s, (30, 30, 34), False, points, 2)
    for i in range(1, count):
        f = i / count
        bx = x1 + (x2 - x1) * f
        by = y1 + (y2 - y1) * f + sag * 4 * f * (1 - f) + 5
        color = BULB_COLORS[(i + int(t * 2)) % len(BULB_COLORS)]
        pygame.draw.circle(s, color, (int(bx), int(by)), 4)
        glow(s, (bx, by), 14, color, 60)


def draw_enemy(s, kind, x, y, t, vx):
    x, y = int(x), int(y)
    facing = 1 if vx >= 0 else -1
    draw_shadow(s, x, y, 70)
    if kind == "polisher":
        pygame.draw.line(s, (90, 92, 98), (x - 10 * facing, y - 26), (x - 34 * facing, y - 80), 4)
        pygame.draw.line(s, (40, 40, 44), (x - 42 * facing, y - 84), (x - 26 * facing, y - 76), 7)
        pygame.draw.ellipse(s, (120, 124, 132), (x - 32, y - 30, 64, 26))
        pygame.draw.ellipse(s, (160, 164, 172), (x - 22, y - 36, 44, 16))
        pygame.draw.ellipse(s, (40, 40, 44), (x - 34, y - 10, 68, 12))
        for k in range(6):
            a = t * 14 + k
            pygame.draw.line(s, (200, 200, 200), (x, y - 4), (x + 30 * math.cos(a), y - 4 + 5 * math.sin(a)), 1)
        pygame.draw.circle(s, RED if int(t * 6) % 2 else (90, 20, 20), (x + 14 * facing, y - 30), 4)
    elif kind == "trolley":
        pygame.draw.rect(s, BRASS, (x - 40, y - 18, 80, 8))
        pygame.draw.line(s, BRASS, (x - 34, y - 18), (x - 34, y - 110), 4)
        pygame.draw.line(s, BRASS, (x + 34, y - 18), (x + 34, y - 110), 4)
        pygame.draw.arc(s, BRASS, (x - 34, y - 140, 68, 60), 0, math.pi, 4)
        draw_suitcase(s, (x - 30, y - 50, 60, 32), (120, 40, 50))
        draw_suitcase(s, (x - 24, y - 84, 48, 28), (60, 80, 120))
        for wx in (x - 32, x + 32):
            pygame.draw.circle(s, BLACK, (wx, y - 4), 7)
            pygame.draw.circle(s, GREY, (wx, y - 4), 3)
    elif kind == "dog":
        run = math.sin(t * 16)
        body = (14, 14, 16)
        pygame.draw.ellipse(s, body, (x - 34, y - 46, 68, 28))
        for lx, ph in ((x - 22, run), (x - 10, -run), (x + 12, run), (x + 24, -run)):
            pygame.draw.line(s, body, (lx, y - 24), (lx + int(ph * 7), y - 2), 6)
        hx = x + 34 * facing
        pygame.draw.circle(s, body, (hx, y - 52), 14)
        pygame.draw.polygon(s, body, [(hx + 8 * facing, y - 54), (hx + 26 * facing, y - 48), (hx + 8 * facing, y - 42)])
        pygame.draw.polygon(s, body, [(hx - 8, y - 62), (hx - 2, y - 78), (hx + 4, y - 62)])
        pygame.draw.circle(s, RED, (hx + 6 * facing, y - 56), 3)
        glow(s, (hx + 6 * facing, y - 56), 10, RED, 120)
        pygame.draw.line(s, body, (x - 34 * facing, y - 40), (x - 50 * facing, y - 54 + int(run * 6)), 5)
    elif kind == "suitcase":
        tilt = math.sin(t * 6) * 8
        case = pygame.Surface((70, 50), pygame.SRCALPHA)
        draw_suitcase(case, (5, 12, 60, 36), (110, 70, 40))
        case = pygame.transform.rotate(case, tilt)
        s.blit(case, case.get_rect(midbottom=(x, y + 2)))
        for k in range(3):
            pygame.draw.line(s, (200, 206, 218), (x - 40 * facing - k * 6 * facing, y - 12 - k * 10),
                             (x - 56 * facing - k * 6 * facing, y - 12 - k * 10), 2)
    elif kind == "ball":
        hop = abs(math.sin(t * 5)) * 40
        cy = int(y - 24 - hop)
        pygame.draw.circle(s, (230, 216, 196), (x, cy), 24)
        for k, color in enumerate(((200, 40, 55), (60, 100, 200), (240, 200, 60))):
            a = t * 4 * facing + k * 2.1
            pygame.draw.polygon(s, color, [(x, cy), (x + 24 * math.cos(a), cy + 24 * math.sin(a)),
                                           (x + 24 * math.cos(a + 0.9), cy + 24 * math.sin(a + 0.9))])
        pygame.draw.circle(s, (40, 20, 30), (x, cy), 24, 2)
        pygame.draw.circle(s, WHITE, (x - 8, cy - 9), 4)
