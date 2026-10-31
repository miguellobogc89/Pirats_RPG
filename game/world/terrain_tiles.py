"""Tiles de terreno dibujados por codigo, en rejilla nativa de 32 px.

Una casilla del mapa = 32 x 32 px en pantalla, sin escalar. De momento todo
se ve en escala de grises (el juego convierte la pantalla al final), pero
los tonos estan pensados para poder colorearse mas adelante.
Ver docs/GUIA_ESTILO.md.
"""
import math

import pygame

TILE = 32
ART_SIZE = TILE
SCALE = 1

# Tonos (de claro a oscuro).
WHITE = (250, 250, 250)
PALE = (226, 226, 226)
LIGHT = (196, 196, 196)
MID = (150, 150, 150)
DARK = (104, 104, 104)
DEEP = (66, 66, 66)
INK = (30, 30, 30)

_cache = {}


def _hash(*values):
    """Numero pseudoaleatorio estable a partir de coordenadas (sin random global)."""
    h = 2166136261
    for v in values:
        h = (h ^ (int(v) & 0xFFFFFFFF)) * 16777619 & 0xFFFFFFFF
    # Mezcla final para repartir bien todos los bits.
    h ^= h >> 16
    h = (h * 0x7FEB352D) & 0xFFFFFFFF
    h ^= h >> 15
    h = (h * 0x846CA68B) & 0xFFFFFFFF
    h ^= h >> 16
    return h


def _rand(variant, *salt):
    return (_hash(variant, *salt) % 1000) / 1000.0


def _surface(fill=None):
    surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    surf.fill(fill or (0, 0, 0, 0))
    return surf


def _put(surf, x, y, color):
    if 0 <= x < TILE and 0 <= y < TILE:
        surf.fill(color, (int(x), int(y), 1, 1))


def _speckle(surf, variant, salt, count, colors, size=1):
    for i in range(count):
        h = _hash(variant, salt, i)
        x, y = h % TILE, (h >> 10) % TILE
        surf.fill(colors[i % len(colors)], (x, y, size, size))


# --- Suelos ---------------------------------------------------------------

def _grass(variant):
    surf = _surface(PALE)
    _speckle(surf, variant, 1, 18, (LIGHT,))
    # Matas: tres briznas en abanico.
    for i in range(3 + variant % 2):
        h = _hash(variant, 2, i)
        x, y = 3 + h % 25, 6 + (h >> 8) % 22
        for dx, top in ((-2, 3), (0, 5), (2, 3)):
            for dy in range(top):
                _put(surf, x + dx + (dx * dy) // 6, y - dy, DARK if dy < top - 1 else MID)
    return surf


def _flowers(variant):
    surf = _grass(variant)
    for i in range(2):
        h = _hash(variant, 9, i)
        x, y = 5 + h % 21, 5 + (h >> 8) % 21
        for dx, dy in ((0, -2), (-2, 0), (2, 0), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            _put(surf, x + dx, y + dy, WHITE)
        _put(surf, x, y, DARK)
        _put(surf, x, y + 3, MID)
        _put(surf, x, y + 4, MID)
    return surf


def _path(variant):
    surf = _surface(WHITE)
    _speckle(surf, variant, 3, 14, (PALE, LIGHT))
    for i in range(3):
        h = _hash(variant, 4, i)
        x, y = 2 + h % 27, 2 + (h >> 8) % 27
        surf.fill(LIGHT, (x, y, 3, 2))
        _put(surf, x + 1, y + 2, MID)
    return surf


def _sand(variant):
    surf = _surface(WHITE)
    _speckle(surf, variant, 5, 26, (PALE, PALE, LIGHT))
    if variant % 5 == 0:
        # Concha pequeña.
        h = _hash(variant, 6)
        x, y = 6 + h % 18, 6 + (h >> 8) % 18
        for dx in range(5):
            _put(surf, x + dx, y + 1, LIGHT)
        for dx in (1, 2, 3):
            _put(surf, x + dx, y, MID)
        _put(surf, x + 2, y + 2, DARK)
    return surf


def _wet_sand(variant):
    surf = _surface(PALE)
    _speckle(surf, variant, 7, 20, (LIGHT, WHITE))
    return surf


def _water(variant):
    surf = _surface(MID)
    _speckle(surf, variant, 8, 10, (DARK,))
    # Ondas: arcos claros cortos.
    for i in range(3):
        h = _hash(variant, 10, i)
        x, y = h % 24, 4 + (h >> 8) % 24
        for dx in range(7):
            _put(surf, x + dx, y - (1 if 1 < dx < 5 else 0), LIGHT)
    return surf


def _deep_water(variant):
    surf = _surface(DARK)
    _speckle(surf, variant, 11, 12, (DEEP,))
    for i in range(2):
        h = _hash(variant, 12, i)
        x, y = h % 24, 4 + (h >> 8) % 24
        for dx in range(6):
            _put(surf, x + dx, y - (1 if 1 < dx < 4 else 0), MID)
    return surf


def _planks(variant, horizontal=True):
    surf = _surface(PALE)
    board = 8
    for i in range(0, TILE, board):
        # Cada tablon con un tono algo distinto, junta oscura y vetas.
        tone = (LIGHT, PALE, PALE, WHITE)[(_hash(variant, i) % 4)]
        if horizontal:
            surf.fill(tone, (0, i, TILE, board - 1))
            surf.fill(DARK, (0, i + board - 1, TILE, 1))
            seam = (_hash(variant, i, 1) % 24) + 4
            surf.fill(DARK, (seam, i, 1, board - 1))
            surf.fill(MID, ((seam + 12) % TILE, i + 3, 5, 1))
            _put(surf, (seam + 4) % TILE, i + 2, DEEP)
        else:
            surf.fill(tone, (i, 0, board - 1, TILE))
            surf.fill(DARK, (i + board - 1, 0, 1, TILE))
            seam = (_hash(variant, i, 1) % 24) + 4
            surf.fill(DARK, (i, seam, board - 1, 1))
            surf.fill(MID, (i + 3, (seam + 12) % TILE, 1, 5))
            _put(surf, i + 2, (seam + 4) % TILE, DEEP)
    return surf


def _dock(variant):
    return _planks(variant, horizontal=False)


def _floor(variant):
    return _planks(variant, horizontal=True)


def _wall(variant):
    surf = _surface(LIGHT)
    # Friso de madera vertical con remate y zocalo.
    for x in range(0, TILE, 8):
        surf.fill(MID, (x, 4, 1, 20))
        surf.fill(PALE, (x + 1, 4, 1, 20))
    surf.fill(DARK, (0, 0, TILE, 4))
    surf.fill(WHITE, (0, 4, TILE, 1))
    surf.fill(DEEP, (0, 24, TILE, 8))
    surf.fill(DARK, (0, 24, TILE, 2))
    return surf


def _void(variant):
    return _surface(INK)


def _cave(variant):
    surf = _surface(LIGHT)
    _speckle(surf, variant, 13, 22, (MID, PALE))
    for i in range(3):
        h = _hash(variant, 14, i)
        x, y = 2 + h % 26, 2 + (h >> 8) % 26
        surf.fill(MID, (x, y, 3, 2))
        surf.fill(WHITE, (x, y, 1, 1))
        _put(surf, x + 1, y + 2, DARK)
    return surf


# --- Objetos de una casilla (se dibujan sobre un suelo) -------------------

def _blob(surf, cx, cy, rx, ry, variant, salt, lobes=0.0, light_bias=0.0, palette=(WHITE, LIGHT, MID, DARK)):
    """Forma redondeada con contorno, luz arriba-izquierda y textura estable."""
    for y in range(TILE):
        for x in range(TILE):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            angle = math.atan2(dy, dx)
            edge = 1.0 + lobes * math.sin(angle * 5 + variant) + lobes * 0.6 * math.sin(angle * 3 + salt)
            dist = math.hypot(dx, dy)
            if dist > edge:
                continue
            if dist > edge - 0.12:
                _put(surf, x, y, INK)
                continue
            light = -(dx + dy) * 0.6 + light_bias
            grain = _rand(variant, salt, x, y) - 0.5
            value = light + grain * 0.55 - dist * 0.25
            if value > 0.45:
                color = palette[0]
            elif value > 0.05:
                color = palette[1]
            elif value > -0.35:
                color = palette[2]
            else:
                color = palette[3]
            _put(surf, x, y, color)


def _leaf(surf, cx, cy, angle, length, wrap=False, inside=None):
    """Hoja alargada: borde oscuro, cara iluminada arriba y nervio central."""
    ca, sa = math.cos(angle), math.sin(angle)
    half = length / 2.0
    for t in range(-int(half) - 1, int(half) + 2):
        width = max(0.0, 2.6 * (1 - (t / (half + 0.5)) ** 2))
        for w in range(-3, 4):
            if abs(w) > width + 0.6:
                continue
            x = cx + ca * t - sa * w
            y = cy + sa * t + ca * w
            if wrap:
                x, y = x % TILE, y % TILE
            if inside and not inside(x, y):
                continue
            if abs(w) > width - 0.4:
                color = DEEP
            elif w == 0:
                color = MID
            else:
                color = LIGHT if (w * ca - t * 0.15) < 0 else MID
            _put(surf, x, y, color)


def _foliage(surf, variant, salt, count, wrap=False, inside=None, length=(7, 11)):
    for i in range(count):
        h = _hash(variant, salt, i)
        cx, cy = h % TILE, (h >> 10) % TILE
        if inside and not inside(cx, cy):
            continue
        angle = ((h >> 5) % 628) / 100.0
        size = length[0] + (h >> 3) % (length[1] - length[0] + 1)
        _leaf(surf, cx, cy, angle, size, wrap=wrap, inside=inside)


def _tree(variant):
    """Arbol de copa redonda; repetido forma un bosque que hace de limite."""
    surf = _surface()
    for x in range(7, 27):
        _put(surf, x, 30, DEEP)
        _put(surf, x + 1, 31, DEEP)
    surf.fill(DEEP, (13, 22, 6, 9))
    surf.fill(DARK, (14, 22, 2, 8))
    cx, cy, rx, ry = 16.0, 12.0, 14.5, 11.5

    def inside(x, y):
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0

    for y in range(TILE):
        for x in range(TILE):
            if inside(x, y):
                _put(surf, x, y, DARK)
    _foliage(surf, variant, 21, 26, inside=inside, length=(6, 9))
    # Luz arriba a la izquierda y contorno.
    for y in range(TILE):
        for x in range(TILE):
            if not inside(x, y):
                continue
            if not (inside(x - 1, y) and inside(x + 1, y) and inside(x, y - 1) and inside(x, y + 1)):
                _put(surf, x, y, INK)
            elif (x - cx) + (y - cy) > rx * 0.9 and _rand(variant, x, y) > 0.4:
                _put(surf, x, y, DEEP)
    return surf


def _jungle(variant):
    """Selva densa: hojas grandes superpuestas en todas direcciones (se repite sin cortes)."""
    surf = _surface(DEEP)
    _foliage(surf, variant, 30, 22, wrap=True, length=(9, 14))
    _foliage(surf, variant, 31, 10, wrap=True, length=(6, 9))
    return surf


def _rock(variant):
    """Roca grande con forma variable; algunas llevan un guijarro al lado."""
    surf = _surface()
    wide = variant % 3
    rx, ry = (14.5, 12.0, 13.0)[wide], (11.5, 13.0, 10.5)[wide]
    cy = 31 - ry - 2
    for x in range(int(16 - rx) + 2, int(16 + rx)):
        _put(surf, x, 30, DEEP)
        _put(surf, x + 1, 31, DEEP)
    _blob(surf, 16, cy, rx, ry, variant, 41, lobes=0.08, palette=(WHITE, LIGHT, MID, DARK))
    h = _hash(variant, 42)
    x = 9 + h % 12
    for dy in range(6):
        _put(surf, x + dy // 2, int(cy) - 2 + dy, DEEP)
    if variant % 2:
        small = _surface()
        _blob(small, 27, 27, 4.5, 3.5, variant, 43, palette=(LIGHT, MID, DARK, DEEP))
        surf.blit(small, (0, 0))
    return surf


def _rock_water(variant):
    """Roca que asoma del agua, con espuma alrededor."""
    surf = _surface()
    for angle in range(0, 360, 6):
        rad = math.radians(angle)
        for r in (14.5, 15.5):
            _put(surf, 16 + math.cos(rad) * r, 19 + math.sin(rad) * r * 0.62, WHITE if r < 15 else PALE)
    surf.blit(_rock(variant), (0, -2))
    return surf


_BUILDERS = {
    "grass": (_grass, 4),
    "flowers": (_flowers, 2),
    "path": (_path, 4),
    "sand": (_sand, 6),
    "wet_sand": (_wet_sand, 4),
    "water": (_water, 4),
    "deep_water": (_deep_water, 4),
    "tree": (_tree, 3),
    "jungle": (_jungle, 6),
    "dock": (_dock, 3),
    "floor": (_floor, 3),
    "wall": (_wall, 1),
    "void": (_void, 1),
    "cave": (_cave, 4),
    "rock": (_rock, 6),
    "rock_water": (_rock_water, 3),
}


def get_tile(kind, variant=0):
    """Tile listo para dibujar (32x32). Las variantes evitan que se note la repeticion."""
    builder, count = _BUILDERS[kind]
    key = (kind, variant % count)
    if key not in _cache:
        _cache[key] = builder(variant % count)
    return _cache[key]


def variant_for(x, y):
    return _hash(x, y, 31)


def draw_edges(surface, x, y, sides, color=DARK, width=2):
    """Linea de borde en los lados indicados: 'n', 's', 'e', 'w'."""
    if "n" in sides:
        surface.fill(color, (x, y, TILE, width))
    if "s" in sides:
        surface.fill(color, (x, y + TILE - width, TILE, width))
    if "w" in sides:
        surface.fill(color, (x, y, width, TILE))
    if "e" in sides:
        surface.fill(color, (x + TILE - width, y, width, TILE))


def draw_foam(surface, x, y, sides, variant=0):
    """Espuma ondulada en el borde del agua que toca tierra."""
    for side in sides:
        for i in range(TILE):
            wave = 2 + int(1.5 * math.sin((i + variant % 7) * 0.7))
            for d in range(wave):
                color = WHITE if d < wave - 1 else PALE
                if side == "n":
                    _put_on(surface, x + i, y + d, color)
                elif side == "s":
                    _put_on(surface, x + i, y + TILE - 1 - d, color)
                elif side == "w":
                    _put_on(surface, x + d, y + i, color)
                elif side == "e":
                    _put_on(surface, x + TILE - 1 - d, y + i, color)


def _put_on(surface, x, y, color):
    surface.fill(color, (int(x), int(y), 1, 1))
