"""Suelo por casillas a partir de las zonas transitables de una escena.

Cada escena usa un tema (estilo Pokemon Rojo/Azul):
- village / farm: hierba en zonas amplias, camino en calles; fuera, bosque.
- port: muelle de tablones y caminos; fuera, mar.
- interior: suelo de madera; alrededor, pared y negro.
- cave: suelo de cueva; fuera, rocas.

El suelo se dibuja una sola vez y se guarda; cada fotograma solo se copia.
"""
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
