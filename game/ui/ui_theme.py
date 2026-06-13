import pygame


COLOR_DARK = (48, 55, 43)
COLOR_PANEL = (238, 230, 204)
COLOR_PANEL_INNER = (220, 207, 170)
COLOR_PANEL_LIGHT = (250, 248, 235)

COLOR_ACCENT = (119, 146, 88)
COLOR_WARN = (151, 76, 60)

COLOR_BUTTON = (248, 244, 220)
COLOR_BUTTON_HOVER = (255, 250, 225)
COLOR_BUTTON_PRESSED = (210, 196, 160)
COLOR_BUTTON_DISABLED = (170, 160, 140)

COLOR_OVERLAY = (0, 0, 0, 195)

BORDER_RADIUS_SMALL = 6
BORDER_RADIUS_MEDIUM = 10
BORDER_RADIUS_LARGE = 16

BORDER_WIDTH = 2


def create_game_fonts():
    return {
        "small": pygame.font.SysFont("consolas", 14),
        "normal": pygame.font.SysFont("consolas", 18),
        "title": pygame.font.SysFont("consolas", 28, bold=True),
    }