"""Suelo por casillas a partir de las zonas transitables de una escena.

Cada escena usa un tema (estilo Pokemon Rojo/Azul):
- village / farm: hierba en zonas amplias, camino en calles; fuera, bosque.
- port: muelle de tablones y caminos; fuera, mar.
- interior: suelo de madera; alrededor, pared y negro.
- cave: suelo de cueva; fuera, rocas.

El suelo se dibuja una sola vez y se guarda; cada fotograma solo se copia.
"""
import math

import pygame

from game.world.terrain_tiles import TILE, draw_edges, get_tile, variant_for

# Una zona transitable cuyo lado corto mide esto o menos se considera calle.
STREET_MAX_WIDTH = 140

THEMES = {
    "village": {"wide": "grass", "street": "path", "outside": "tree", "base": "grass"},
    "farm": {"wide": "grass", "street": "path", "outside": "tree", "base": "grass"},
    "port": {"wide": "dock", "street": "path", "outside": "water", "base": "water"},
    "interior": {"wide": "floor", "street": "floor", "outside": "wall", "base": "void"},
    "cave": {"wide": "cave", "street": "cave", "outside": "rock", "base": "cave"},
}

# Tiles que tapan por completo la casilla: no necesitan linea de borde al lado.
SOLID = {"tree", "wall", "void", "rock"}
# Tiles de objeto que se dibujan sobre el suelo base del tema.
OVERLAY = {"tree", "rock"}

_ground_cache = {}


def _cell_center(col, row):
    return col * TILE + TILE // 2, row * TILE + TILE // 2


def _inside(rects, x, y):
    return any(rx <= x < rx + rw and ry <= y < ry + rh for rx, ry, rw, rh in rects)


def build_terrain_grid(layout, theme="village"):
    """Devuelve una lista de filas con el tipo de tile de cada casilla."""
    spec = THEMES[theme]
    width, height = layout["width"], layout["height"]
    walkable = [tuple(r) for r in layout.get("walkable", [])]
    streets = [r for r in walkable if min(r[2], r[3]) <= STREET_MAX_WIDTH]
    cols = -(-width // TILE)
    rows = -(-height // TILE)
    grid = []
    for row in range(rows):
        line = []
        for col in range(cols):
            x, y = _cell_center(col, row)
            if not _inside(walkable, x, y):
                line.append(spec["outside"])
            elif _inside(streets, x, y):
                line.append(spec["street"])
            else:
                line.append(spec["wide"])
        grid.append(line)
    if spec["outside"] == "wall":
        # Como en los interiores de Pokemon: pared solo encima del suelo
        # (la que se ve de frente); los laterales y el resto quedan en negro.
        walk = {spec["wide"], spec["street"]}
        for row, line in enumerate(grid):
            for col, kind in enumerate(line):
                if kind == "wall" and not (row + 1 < rows and grid[row + 1][col] in walk):
                    line[col] = "void"
    return grid


def render_ground(layout, theme="village"):
    spec = THEMES[theme]
    grid = build_terrain_grid(layout, theme)
    rows, cols = len(grid), len(grid[0])
    surface = pygame.Surface((cols * TILE, rows * TILE))
    for row, line in enumerate(grid):
        for col, kind in enumerate(line):
            x, y = col * TILE, row * TILE
            variant = variant_for(col, row)
            base = spec["base"] if kind in OVERLAY else kind
            if base == "grass" and variant % 11 == 0:
                base = "flowers"
            surface.blit(get_tile(base, variant), (x, y))
            if kind in OVERLAY:
                surface.blit(get_tile(kind, variant), (x, y))
            if kind in SOLID or kind == spec["outside"]:
                continue

            def differs(dc, dr):
                r, c = row + dr, col + dc
                if not (0 <= r < rows and 0 <= c < cols):
                    return False
                neighbor = grid[r][c]
                return neighbor != kind and neighbor not in SOLID

            sides = "".join(
                side for side, dc, dr in (("n", 0, -1), ("s", 0, 1), ("w", -1, 0), ("e", 1, 0))
                if differs(dc, dr)
            )
            if sides:
                draw_edges(surface, x, y, sides)
    return surface


def draw_ground(screen, layout, camera_x, camera_y, theme="village", cache_key=None):
    key = (cache_key or layout.get("id") or id(layout), theme)
    if key not in _ground_cache:
        _ground_cache[key] = render_ground(layout, theme)
    screen.blit(_ground_cache[key], (-camera_x, -camera_y))


def theme_for_scene(scene_id):
    if "madriguera" in scene_id:
        return "cave"
    if scene_id in ("brumazul_casa_almarin", "brumazul_taller_almarin", "brumazul_taller_sylvarin",
                    "brumazul_posada", "brumazul_taberna"):
        return "interior"
    if scene_id == "brumazul_puerto":
        return "port"
    if scene_id == "brumazul_granja":
        return "farm"
    return "village"


# --- Mapas dibujados casilla a casilla (texto en el JSON de la escena) ------
#
# "tilemap": {"rows": ["JJss~~", ...]} con una letra por casilla de 32 px.
CHAR_KINDS = {
    "J": "jungle",
    "T": "tree",
    "s": "sand",
    "w": "wet_sand",
    "g": "grass",
    "p": "path",
    "~": "water",
    "=": "deep_water",
    "R": "rock",
    "r": "rock_water",
    "d": "dock",
}
# Que suelo va debajo de los objetos de una casilla.
CHAR_BASE = {"rock": "sand", "tree": "grass"}
BLOCKING_KINDS = {"jungle", "tree", "water", "deep_water", "rock", "rock_water", "wall", "void"}
WATER_KINDS = {"water", "deep_water", "rock_water"}
LAND_KINDS = {"sand", "wet_sand", "grass", "path", "rock", "dock"}


def _kind_at(rows, col, row):
    if 0 <= row < len(rows) and 0 <= col < len(rows[row]):
        return CHAR_KINDS.get(rows[row][col], "sand")
    return None


def _is_water(rows, col, row):
    col = min(max(col, 0), len(rows[0]) - 1)
    row = min(max(row, 0), len(rows) - 1)
    return _kind_at(rows, col, row) in WATER_KINDS


def _is_deep(rows, col, row):
    col = min(max(col, 0), len(rows[0]) - 1)
    row = min(max(row, 0), len(rows) - 1)
    kind = _kind_at(rows, col, row)
    return kind == "deep_water" or (kind == "rock_water" and _deep_majority(rows, col, row))


def _deep_majority(rows, col, row):
    kinds = [_kind_at(rows, col + dc, row + dr) for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    return sum(k == "deep_water" for k in kinds) > sum(k == "water" for k in kinds)


def _field(value_at, px, py):
    """Interpolacion bilineal entre centros de casilla (1 = si, 0 = no)."""
    fx, fy = px / TILE - 0.5, py / TILE - 0.5
    c0, r0 = int(fx // 1), int(fy // 1)
    tx, ty = fx - c0, fy - r0
    a, b = value_at(c0, r0), value_at(c0 + 1, r0)
    c, d = value_at(c0, r0 + 1), value_at(c0 + 1, r0 + 1)
    top = a + (b - a) * tx
    bottom = c + (d - c) * tx
    return top + (bottom - top) * ty


def _noise(px, py):
    from game.world.terrain_tiles import _hash
    grain = (_hash(px // 2, py // 2, 3) % 100) / 100.0 - 0.5
    wave = math.sin(px * 0.11 + py * 0.05) * 0.5 + math.sin(py * 0.17 - px * 0.07) * 0.5
    return grain * 0.06 + wave * 0.07


def _smooth_shore(surface, rows):
    """Costa organica: arena mojada, espuma y agua en vez de escalones cuadrados."""
    from game.world.terrain_tiles import DEEP, LIGHT, PALE, WHITE, get_tile

    height, width = len(rows), len(rows[0])
    for row in range(height):
        for col in range(width):
            around = [_is_water(rows, col + dc, row + dr) for dc in (-1, 0, 1) for dr in (-1, 0, 1)]
            if all(around) or not any(around):
                continue
            variant = variant_for(col, row)
            water_tile = get_tile("deep_water" if _is_deep(rows, col, row) else "water", variant)
            wet_tile = get_tile("wet_sand", variant)
            for y in range(TILE):
                for x in range(TILE):
                    px, py = col * TILE + x, row * TILE + y
                    land = 1.0 - _field(lambda c, r: 1.0 if _is_water(rows, c, r) else 0.0, px, py)
                    land += _noise(px, py)
                    if land > 0.6:
                        if _is_water(rows, col, row):
                            surface.set_at((px, py), wet_tile.get_at((x, y)))
                        continue
                    if land > 0.52:
                        color = wet_tile.get_at((x, y))
                    elif land > 0.47:
                        color = WHITE
                    elif land > 0.43:
                        color = PALE if (px + py) % 3 else LIGHT
                    else:
                        color = water_tile.get_at((x, y))
                    surface.set_at((px, py), color)
    # Transicion suave entre agua y agua profunda.
    for row in range(height):
        for col in range(width):
            if not _is_water(rows, col, row):
                continue
            around = [_is_deep(rows, col + dc, row + dr) for dc in (-1, 0, 1) for dr in (-1, 0, 1)]
            if all(around) or not any(around):
                continue
            variant = variant_for(col, row)
            shallow, deep = get_tile("water", variant), get_tile("deep_water", variant)
            for y in range(TILE):
                for x in range(TILE):
                    px, py = col * TILE + x, row * TILE + y
                    if _field(lambda c, r: 1.0 if _is_water(rows, c, r) else 0.0, px, py) < 0.99:
                        continue
                    v = _field(lambda c, r: 1.0 if _is_deep(rows, c, r) else 0.0, px, py) + _noise(px, py)
                    tile = deep if v > 0.5 else shallow
                    color = tile.get_at((x, y))
                    if 0.48 < v <= 0.5:
                        color = DEEP
                    surface.set_at((px, py), color)


def render_char_map(rows):
    from game.world.terrain_tiles import get_tile, _leaf, DEEP

    height, width = len(rows), max(len(r) for r in rows)
    rows = [r.ljust(width, "s") for r in rows]
    surface = pygame.Surface((width * TILE, height * TILE))
    sides = (("n", 0, -1), ("s", 0, 1), ("w", -1, 0), ("e", 1, 0))
    # 1) Suelos.
    for row in range(height):
        for col in range(width):
            kind = _kind_at(rows, col, row)
            variant = variant_for(col, row)
            if kind == "rock_water":
                base = "deep_water" if _deep_majority(rows, col, row) else "water"
            else:
                base = CHAR_BASE.get(kind, kind)
                if base == "wet_sand":
                    # La arena mojada la pinta la costa suave; aqui va arena normal.
                    base = "sand"
            surface.blit(get_tile(base, variant), (col * TILE, row * TILE))
    # 2) Costa suave.
    _smooth_shore(surface, rows)
    # 3) Objetos de una casilla y bordes de la selva.
    for row in range(height):
        for col in range(width):
            kind = _kind_at(rows, col, row)
            x, y = col * TILE, row * TILE
            variant = variant_for(col, row)
            if kind in ("rock", "rock_water", "tree"):
                surface.blit(get_tile(kind, variant), (x, y))
            if kind in ("sand", "wet_sand", "grass", "path"):
                # Sombra y hojas que asoman de la selva sobre el suelo.
                fringe = None
                for side, dc, dr in sides:
                    if _kind_at(rows, col + dc, row + dr) != "jungle":
                        continue
                    if fringe is None:
                        fringe = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                        fringe.fill((0, 0, 0, 0))
                    if side == "n":
                        fringe.fill(DEEP, (0, 0, TILE, 3))
                    for i in range(3):
                        h = variant_for(col * 7 + i, row * 13 + ord(side))
                        t = 4 + h % 24
                        depth = 2 + (h >> 6) % 4
                        angle = ((h >> 3) % 100) / 100.0 * 1.2 - 0.6
                        if side == "n":
                            _leaf(fringe, t, depth, 1.57 + angle, 8)
                        elif side == "s":
                            _leaf(fringe, t, TILE - depth, 1.57 + angle, 8)
                        elif side == "w":
                            _leaf(fringe, depth, t, angle, 8)
                        else:
                            _leaf(fringe, TILE - depth, t, angle, 8)
                if fringe is not None:
                    surface.blit(fringe, (x, y))
    return surface


def collisions_from_rows(rows):
    """Rectangulos (en px) que bloquean el paso, unidos para que sean pocos."""
    height, width = len(rows), max(len(r) for r in rows)
    blocked = [[_kind_at(rows, c, r) in BLOCKING_KINDS for c in range(width)] for r in range(height)]
    used = [[False] * width for _ in range(height)]
    rects = []
    for r in range(height):
        for c in range(width):
            if not blocked[r][c] or used[r][c]:
                continue
            w = 1
            while c + w < width and blocked[r][c + w] and not used[r][c + w]:
                w += 1
            h = 1
            while r + h < height and all(blocked[r + h][c + i] and not used[r + h][c + i] for i in range(w)):
                h += 1
            for rr in range(r, r + h):
                for cc in range(c, c + w):
                    used[rr][cc] = True
            rects.append({"x": c * TILE, "y": r * TILE, "w": w * TILE, "h": h * TILE})
    return rects


def draw_char_map(screen, rows, camera_x, camera_y, cache_key):
    key = ("char", cache_key)
    if key not in _ground_cache:
        _ground_cache[key] = render_char_map(rows)
    screen.blit(_ground_cache[key], (-camera_x, -camera_y))
