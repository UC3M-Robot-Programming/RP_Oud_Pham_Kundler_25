"""Drawing routines: text, glow, panels, gradients and other basic shapes."""
import math

import pygame

from robot_info.display import GOLD, GREY, HEIGHT, WIDTH, YELLOW


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(color, amount):
    return tuple(max(0, min(255, c + amount)) for c in color[:3])


def wrap(text, font, width):
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split(" "):
            test = current + (" " if current else "") + word
            if font.size(test)[0] <= width:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_text(s, msg, font, color, pos, center=False):
    img = font.render(msg, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    s.blit(img, rect)
    return rect


def draw_text_block(s, msg, font, color, x, y, width, gap=3):
    for line in wrap(msg, font, width):
        s.blit(font.render(line, True, color), (x, y))
        y += font.get_height() + gap
    return y


def glow(s, pos, radius, color, alpha):
    radius = int(radius)
    if radius < 2 or alpha <= 0:
        return
    g = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(6):
        r = int(radius * (1 - i / 6))
        pygame.draw.circle(g, (*color[:3], int(alpha * (i + 1) / 6)), (radius, radius), r)
    s.blit(g, (pos[0] - radius, pos[1] - radius))


def alpha_polygon(s, color, alpha, points):
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*color[:3], alpha), points)
    s.blit(layer, (0, 0))


def alpha_ellipse(s, color, alpha, rect):
    r = pygame.Rect(rect)
    layer = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.ellipse(layer, (*color[:3], alpha), layer.get_rect())
    s.blit(layer, r.topleft)


def panel(s, rect, alpha=225, border=GOLD):
    rect = pygame.Rect(rect)
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(layer, (10, 10, 14, alpha), layer.get_rect(), border_radius=8)
    s.blit(layer, rect.topleft)
    pygame.draw.rect(s, border, rect, 2, border_radius=8)


def shade_screen(s, alpha=170):
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    layer.fill((0, 0, 0, alpha))
    s.blit(layer, (0, 0))


def vertical_gradient(s, rect, top, bottom):
    r = pygame.Rect(rect)
    for y in range(r.h):
        pygame.draw.line(s, lerp_color(top, bottom, y / max(1, r.h - 1)),
                         (r.x, r.y + y), (r.right - 1, r.y + y))


def draw_star(s, center, filled, size=22):
    cx, cy = center
    points = []
    for k in range(10):
        r = size if k % 2 == 0 else size * 0.42
        a = -math.pi / 2 + k * math.pi / 5
        points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pygame.draw.polygon(s, YELLOW if filled else GREY, points)
