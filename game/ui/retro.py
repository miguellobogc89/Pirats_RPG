"""Acabado pixel art del juego (de momento en escala de grises).

- Fuentes pixeladas sin suavizado: familia Jersey (licencia OFL, assets/fonts).
- Marcos de ventana con esquinas suaves, contorno, filete interior y sombra.
- Iconos pequeños dibujados a mano (corazon, sol, luna, flechas).

Regla para el arte: rejilla de 32 px nativa (una casilla = 32 px en pantalla),
escalando siempre con pygame.transform.scale (sin suavizado).
"""
from pathlib import Path

import pygame

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"
# Cada fuente Jersey esta diseñada a la altura de su nombre; se usan a 1x o 2x.
FONT_SMALL_FILE = FONT_DIR / "Jersey10-Regular.ttf"
FONT_TEXT_FILE = FONT_DIR / "Jersey15-Regular.ttf"
FONT_TITLE_FILE = FONT_DIR / "Jersey20-Regular.ttf"
# Compatibilidad con codigo que importaba el nombre anterior.
TITLE_FONT_FILE = FONT_TITLE_FILE

INK = (24, 24, 24)
LINE = (104, 104, 104)
SHADE = (184, 184, 184)
PAPER = (248, 248, 248)
PANEL_FILL = (240, 240, 236)
SHADOW = (56, 56, 56)

FRAME_RADIUS = 6


class PixelFont:
    """Fuente que siempre se dibuja sin suavizado, con la misma API que pygame.font.Font."""

    def __init__(self, path, size, fallback_size=None):
        self.size_px = size
        try:
            self._font = pygame.font.Font(str(path), size)
        except (OSError, FileNotFoundError, pygame.error):
            self._font = pygame.font.SysFont("consolas", fallback_size or size)

    def render(self, text, antialias=False, color=INK, background=None):
        if background is None:
            return self._font.render(str(text), False, color)
        return self._font.render(str(text), False, color, background)

    def __getattr__(self, name):
        return getattr(self._font, name)


def create_pixel_fonts():
    return {
        "small": PixelFont(FONT_SMALL_FILE, 20, 14),
        "normal": PixelFont(FONT_TITLE_FILE, 20, 18),
        "title": PixelFont(FONT_TITLE_FILE, 40, 28),
        "dialogue": PixelFont(FONT_TEXT_FILE, 30, 20),
    }


def draw_frame(screen, rect, fill=PANEL_FILL, border=INK, shadow=True):
    """Ventana: sombra, fondo claro, contorno con esquinas suaves y filete interior."""
    rect = pygame.Rect(rect)
    radius = FRAME_RADIUS if rect.width > 24 and rect.height > 24 else 3
    if shadow:
        pygame.draw.rect(screen, SHADOW, rect.move(3, 3), border_radius=radius)
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, 3, border_radius=radius)
    if rect.width > 20 and rect.height > 20:
        pygame.draw.rect(screen, SHADE, rect.inflate(-10, -10), 1, border_radius=max(1, radius - 3))


def draw_cursor(screen, x, y, size=10, color=INK):
    """Flecha de seleccion apuntando a la derecha."""
    pygame.draw.polygon(screen, color, [(x, y), (x, y + size), (x + size // 2 + 1, y + size // 2)])


def draw_more_arrow(screen, x, y, size=12, color=INK):
    """Triangulo que parpadea para indicar que el texto continua."""
    if (pygame.time.get_ticks() // 400) % 2:
        return
    pygame.draw.polygon(screen, color, [(x, y), (x + size, y), (x + size // 2, y + size // 2 + 2)])


# Iconos en rejilla pequeña: '#' contorno, 'o' relleno, '+' brillo, '.' vacio.
_ICONS = {
    "heart": [
        ".##...##.",
        "#oo#.#oo#",
        "#o+ooooo#",
        "#ooooooo#",
        ".#ooooo#.",
        "..#ooo#..",
        "...#o#...",
        "....#....",
    ],
    "heart_empty": [
        ".##...##.",
        "#..#.#..#",
        "#.......#",
        "#.......#",
        ".#.....#.",
        "..#...#..",
        "...#.#...",
        "....#....",
    ],
    "sun": [
        "....#....",
        ".#..#..#.",
        "..#ooo#..",
        "..o+ooo..",
        "##ooooo##",
        "..ooooo..",
        "..#ooo#..",
        ".#..#..#.",
        "....#....",
    ],
    "moon": [
        "...###...",
        "..#oo....",
        ".#oo.....",
        ".#o+.....",
        ".#oo.....",
        ".#ooo....",
        "..#ooo##.",
        "...####..",
    ],
}

_ICON_COLORS = {"#": INK, "o": LINE, "+": PAPER}
_icon_cache = {}


def get_icon(name, scale=2):
    key = (name, scale)
    if key not in _icon_cache:
        rows = _ICONS[name]
        width = max(len(r) for r in rows)
        surf = pygame.Surface((width, len(rows)), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                if char in _ICON_COLORS:
                    surf.fill(_ICON_COLORS[char], (x, y, 1, 1))
        _icon_cache[key] = pygame.transform.scale(surf, (width * scale, len(rows) * scale))
    return _icon_cache[key]
