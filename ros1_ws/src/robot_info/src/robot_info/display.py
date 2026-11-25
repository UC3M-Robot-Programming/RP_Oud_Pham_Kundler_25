"""Window and screen setup: screen size, frame rate, colours and fonts."""
import pygame


# The screen size is fixed - everything is drawn for 960 x 600 pixels
WIDTH, HEIGHT = 960, 600
FPS = 60                     # the clock keeps the game at 60 frames per second
TOP_BAR = 50
FLOOR_Y = 430
PLAYER_PURPLE = (128, 62, 196)

# Colours of the detective for the ROS parameter change_player_color (1 Red, 2 Purple, 3 Blue)
PLAYER_COLORS = {1: ("Red", (196, 52, 60)), 2: ("Purple", PLAYER_PURPLE), 3: ("Blue", (50, 100, 205))}

# Colours: the world is mostly grey - clues and accents get colour
BLACK = (8, 8, 10)
DARK = (18, 18, 22)
FLOOR_LINE = (40, 42, 47)
GREY = (90, 92, 98)
LIGHT_GREY = (150, 152, 158)
WHITE = (232, 232, 232)
PAPER = (232, 221, 190)
INK = (40, 32, 24)
WOOD = (62, 48, 36)
WOOD_DARK = (40, 30, 22)
BRASS = (170, 135, 70)
GOLD = (212, 164, 58)
YELLOW = (255, 217, 119)
RED = (230, 45, 60)
ORANGE = (255, 138, 31)
GREEN_LIGHT = (110, 220, 140)
BULB_COLORS = [(255, 90, 90), (255, 210, 90), (110, 220, 140), (110, 170, 255), (230, 120, 255)]


def load_font(size, bold=False, italic=False):
    for name in ("georgia", "timesnewroman", "times", "dejavuserif"):
        path = pygame.font.match_font(name, bold, italic)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size + 6)


class Display:
    """Opens the game window and keeps the frame clock."""

    def __init__(self, title="Shadow Detective"):
        pygame.init()
        if pygame.version.vernum < (2, 0):
            raise RuntimeError("pygame 2.0 or newer is needed (found %s). Install it with: "
                               "pip3 install --user 'pygame>=2'" % pygame.version.ver)
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

    def tick(self):
        """Waits for the next frame and returns the passed time in seconds."""
        return self.clock.tick(FPS) / 1000

    def flip(self):
        pygame.display.flip()

    def close(self):
        pygame.quit()
