"""Tiles de terreno dibujados por codigo (estilo Game Boy, escala de grises).

Cada tile se diseña en una rejilla de 16x16 y se muestra a escala 2x (32 px),
igual que el resto del juego. Ver docs/GUIA_ESTILO.md.
"""
import math

import pygame

ART_SIZE = 16
SCALE = 2
TILE = ART_SIZE * SCALE

# Cuatro tonos, como una Game Boy (luego el juego lo pasa todo a grises).
WHITE = (248, 248, 248)
LIGHT = (200, 200, 200)
DARK = (112, 112, 112)
INK = (32, 32, 32)

_cache = {}


def _hash(*values):
    """Numero pseudoaleatorio estable a partir de coordenadas (sin random global)."""
    h = 2166136261
    for v in values:
        h = (h ^ (int(v) & 0xFFFFFFFF)) * 16777619 & 0xFFFFFFFF
    return h


def _surface():
    surf = pygame.Surface((ART_SIZE, ART_SIZE), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    return surf


def _put(surf, x, y, color):
    if 0 <= x < ART_SIZE and 0 <= y < ART_SIZE:
        surf.fill(color, (x, y, 1, 1))


def _finish(surf):
    return pygame.transform.scale(surf, (TILE, TILE))


def _grass(variant):
    surf = _surface()
    surf.fill(WHITE)
    # Matas pequeñas en forma de "v", dos o tres por tile, en posiciones estables.
    for i in range(2 + variant % 2):
        h = _hash(variant, i)
        x, y = 2 + h % 11, 3 + (h >> 8) % 10
        _put(surf, x, y, DARK)
        _put(surf, x + 2, y, DARK)
        _put(surf, x + 1, y + 1, DARK)
    return surf


def _flowers(variant):
    surf = _grass(variant)
    for i in range(2):
        h = _hash(variant, 99, i)
        x, y = 3 + h % 9, 3 + (h >> 8) % 9
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            _put(surf, x + dx, y + dy, DARK)
        _put(surf, x, y, WHITE)
    return surf


def _path(variant):
    surf = _surface()
    surf.fill(WHITE)
    for i in range(3):
        h = _hash(variant, 7, i)
        _put(surf, 1 + h % 14, 1 + (h >> 8) % 14, LIGHT)
    return surf


def _sand(variant):
    surf = _surface()
    surf.fill(WHITE)
    for i in range(6):
        h = _hash(variant, 13, i)
        _put(surf, h % 16, (h >> 8) % 16, LIGHT)
    return surf


def _water(variant):
    surf = _surface()
    surf.fill(LIGHT)
    # Olas cortas en zigzag.
    for row, offset in ((4, variant % 4), (11, (variant + 2) % 4)):
        for x in range(offset, 16, 8):
            _put(surf, x, row, WHITE)
            _put(surf, x + 1, row - 1, WHITE)
            _put(surf, x + 2, row - 1, WHITE)
            _put(surf, x + 3, row, WHITE)
    return surf


def _tree(variant):
    """Arbol de una casilla; repetido forma el bosque que hace de limite del mapa."""
    surf = _surface()
    cx, cy, radius = 7.5, 6.5, 7.2
    for y in range(ART_SIZE):
        for x in range(ART_SIZE):
            dx, dy = x - cx, y - cy
            dist = math.hypot(dx, dy)
            if dist > radius:
                continue
            if dist > radius - 1.1:
                _put(surf, x, y, INK)
                continue
            # Luz desde arriba a la izquierda + textura de hojas estable.
            light = -(dx + dy) / (radius * 1.4)
            leaf = (_hash(variant, x, y) % 100) / 100.0
            value = light + (leaf - 0.5) * 0.8
            color = WHITE if value > 0.6 else LIGHT if value > 0.05 else DARK
            _put(surf, x, y, color)
    # Tronco.
    for y in range(13, 16):
        for x in range(6, 10):
            _put(surf, x, y, INK if x in (6, 9) or y == 15 else DARK)
    return surf


def _planks(variant, horizontal=True):
    surf = _surface()
    surf.fill(WHITE)
    # Tablones de 4 px con juntas oscuras y vetas claras.
    for i in range(0, 16, 4):
        if horizontal:
            surf.fill(DARK, (0, i + 3, 16, 1))
            seam = (variant * 5 + i * 3) % 16
            surf.fill(DARK, (seam, i, 1, 3))
            _put(surf, (seam + 7) % 16, i + 1, LIGHT)
        else:
            surf.fill(DARK, (i + 3, 0, 1, 16))
            seam = (variant * 5 + i * 3) % 16
            surf.fill(DARK, (i, seam, 3, 1))
    return surf


def _dock(variant):
    return _planks(variant, horizontal=False)


def _floor(variant):
    return _planks(variant, horizontal=True)


def _wall(variant):
    surf = _surface()
    surf.fill(LIGHT)
    # Friso de madera con zocalo oscuro.
    for x in range(0, 16, 4):
        surf.fill(DARK, (x, 0, 1, 12))
    surf.fill(WHITE, (0, 2, 16, 1))
    surf.fill(INK, (0, 12, 16, 4))
    surf.fill(DARK, (0, 12, 16, 1))
    return surf


def _void(variant):
    surf = _surface()
    surf.fill(INK)
    return surf


def _cave(variant):
    surf = _surface()
    surf.fill(LIGHT)
    for i in range(5):
        h = _hash(variant, 21, i)
        x, y = h % 15, (h >> 8) % 15
        _put(surf, x, y, DARK)
        _put(surf, x + 1, y, WHITE)
    return surf


def _rock(variant):
    """Bloque de roca de una casilla; repetido forma las paredes de una cueva."""
    surf = _surface()
    cx, cy = 7.5, 8.0
    for y in range(ART_SIZE):
        for x in range(ART_SIZE):
            dx, dy = x - cx, y - cy
            # Forma irregular: radio que varia con el angulo.
            angle = math.atan2(dy, dx)
            radius = 7.3 + 0.45 * math.sin(angle * 2 + variant * 1.7) + 0.35 * math.sin(angle * 5 + variant)
            dist = math.hypot(dx, dy)
            if dist > radius:
                continue
            if dist > radius - 1.1:
                _put(surf, x, y, INK)
                continue
            light = -(dx + dy) / 12.0
            grain = (_hash(variant, x, y, 5) % 100) / 100.0
            value = light + (grain - 0.5) * 0.5
            _put(surf, x, y, WHITE if value > 0.5 else LIGHT if value > -0.1 else DARK)
    return surf


_BUILDERS = {
    "grass": (_grass, 4),
    "flowers": (_flowers, 2),
    "path": (_path, 4),
    "sand": (_sand, 4),
    "water": (_water, 4),
    "tree": (_tree, 3),
    "dock": (_dock, 3),
    "floor": (_floor, 3),
    "wall": (_wall, 1),
    "void": (_void, 1),
    "cave": (_cave, 4),
    "rock": (_rock, 4),
}


def get_tile(kind, variant=0):
    """Tile listo para dibujar (32x32). Las variantes evitan que se note la repeticion."""
    builder, count = _BUILDERS[kind]
    key = (kind, variant % count)
    if key not in _cache:
        _cache[key] = _finish(builder(variant % count))
    return _cache[key]


def variant_for(x, y):
    return _hash(x, y, 31)


def draw_edges(surface, x, y, sides, color=DARK):
    """Linea de borde (2 px en pantalla) en los lados indicados: 'n', 's', 'e', 'w'."""
    if "n" in sides:
        surface.fill(color, (x, y, TILE, SCALE))
    if "s" in sides:
        surface.fill(color, (x, y + TILE - SCALE, TILE, SCALE))
    if "w" in sides:
        surface.fill(color, (x, y, SCALE, TILE))
    if "e" in sides:
        surface.fill(color, (x + TILE - SCALE, y, SCALE, TILE))
