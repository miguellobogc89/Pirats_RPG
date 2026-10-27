import pygame


COLOR_DARK = (24, 24, 24)
COLOR_PANEL = (184, 184, 184)
COLOR_PANEL_INNER = (104, 104, 104)
COLOR_PANEL_LIGHT = (240, 240, 240)

COLOR_ACCENT = (104, 104, 104)
COLOR_WARN = (24, 24, 24)

COLOR_BUTTON = (240, 240, 240)
COLOR_BUTTON_HOVER = (184, 184, 184)
COLOR_BUTTON_PRESSED = (104, 104, 104)
COLOR_BUTTON_DISABLED = (184, 184, 184)

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