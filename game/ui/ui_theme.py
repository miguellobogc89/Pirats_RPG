

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

# Estilo Game Boy: esquinas cuadradas.
BORDER_RADIUS_SMALL = 0
BORDER_RADIUS_MEDIUM = 0
BORDER_RADIUS_LARGE = 0

BORDER_WIDTH = 2


def create_game_fonts():
    """Fuentes pixeladas (ver game/ui/retro.py)."""
    from game.ui.retro import create_pixel_fonts
    return create_pixel_fonts()