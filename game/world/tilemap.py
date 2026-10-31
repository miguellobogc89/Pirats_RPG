"""Suelo por casillas a partir de las zonas transitables de una escena.

Reglas (estilo Pokemon Rojo/Azul):
- Fuera de las zonas transitables: bosque. Los arboles hacen de limite del mapa.
- Calles estrechas: camino de tierra con borde.
- Zonas amplias: hierba, con alguna flor.

El suelo se dibuja una sola vez y se guarda; cada fotograma solo se copia.
"""
import pygame

from game.world.terrain_tiles import TILE, draw_edges, get_tile, variant_for

# Una zona transitable cuyo lado corto mide esto o menos se considera calle.
STREET_MAX_WIDTH = 140

_ground_cache = {}


def _cell_center(col, row):
    return col * TILE + TILE // 2, row * TILE + TILE // 2


def _inside(rects, x, y):
    return any(rx <= x < rx + rw and ry <= y < ry + rh for rx, ry, rw, rh in rects)


def build_terrain_grid(layout):
    """Devuelve una lista de filas con 'tree', 'path' o 'grass' por casilla."""
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
                line.append("tree")
            elif _inside(streets, x, y):
                line.append("path")
            else:
                line.append("grass")
        grid.append(line)
    return grid


def render_ground(layout):
    grid = build_terrain_grid(layout)
    surface = pygame.Surface((len(grid[0]) * TILE, len(grid) * TILE))
    for row, line in enumerate(grid):
        for col, kind in enumerate(line):
            x, y = col * TILE, row * TILE
            variant = variant_for(col, row)
            if kind == "grass" and variant % 11 == 0:
                surface.blit(get_tile("flowers", variant), (x, y))
            else:
                surface.blit(get_tile("path" if kind == "path" else "grass", variant), (x, y))
            if kind == "tree":
                surface.blit(get_tile("tree", variant), (x, y))
            elif kind == "path":
                def other(dc, dr):
                    r, c = row + dr, col + dc
                    return 0 <= r < len(grid) and 0 <= c < len(line) and grid[r][c] != "path"
                sides = "".join(side for side, dc, dr in (("n", 0, -1), ("s", 0, 1), ("w", -1, 0), ("e", 1, 0)) if other(dc, dr))
                draw_edges(surface, x, y, sides)
    return surface


def draw_ground(screen, layout, camera_x, camera_y, cache_key=None):
    key = cache_key or layout.get("id") or id(layout)
    if key not in _ground_cache:
        _ground_cache[key] = render_ground(layout)
    screen.blit(_ground_cache[key], (-camera_x, -camera_y))
