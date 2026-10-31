"""Acabado retro estilo Game Boy (Pokémon Rojo/Azul) en escala de grises.

- Fuentes pixeladas sin suavizado (Press Start 2P y VT323, licencia OFL).
- Marcos de ventana cuadrados con doble borde.

Regla para el arte del mundo: rejilla de 16 px dibujada a escala 2x (tiles de
32 px en pantalla), escalando siempre con pygame.transform.scale (sin suavizado).
"""
from pathlib import Path

import pygame

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"
TITLE_FONT_FILE = FONT_DIR / "PressStart2P-Regular.ttf"  # rejilla 8 px; usar multiplos de 8
TEXT_FONT_FILE = FONT_DIR / "VT323-Regular.ttf"  # rejilla 16 px; nitida a 16 y 32

INK = (24, 24, 24)
LINE = (104, 104, 104)
SHADE = (184, 184, 184)
PAPER = (248, 248, 248)


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
        "small": PixelFont(TEXT_FONT_FILE, 16, 14),
        "normal": PixelFont(TEXT_FONT_FILE, 20, 18),
        "title": PixelFont(TITLE_FONT_FILE, 16, 28),
        # Texto de los cuadros de dialogo, como en los juegos de Game Boy.
        "dialogue": PixelFont(TITLE_FONT_FILE, 16, 18),
    }


def draw_frame(screen, rect, fill=PAPER, border=INK):
    """Ventana clasica: fondo claro, borde grueso y filete interior."""
    rect = pygame.Rect(rect)
    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, border, rect, 4)
    if rect.width > 16 and rect.height > 16:
        pygame.draw.rect(screen, LINE, rect.inflate(-12, -12), 2)


def draw_cursor(screen, x, y, size=10, color=INK):
    """Flecha de seleccion apuntando a la derecha (como en los menus clasicos)."""
    pygame.draw.polygon(screen, color, [(x, y), (x, y + size), (x + size // 2 + 1, y + size // 2)])


def draw_more_arrow(screen, x, y, size=12, color=INK):
    """Triangulo que parpadea para indicar que el texto continua."""
    if (pygame.time.get_ticks() // 400) % 2:
        return
    pygame.draw.polygon(screen, color, [(x, y), (x + size, y), (x + size // 2, y + size // 2 + 2)])
