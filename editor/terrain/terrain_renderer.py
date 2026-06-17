import pygame

from game.world.grid_manager import TILE_SIZE
from editor.terrain.terrain_palette import TERRAIN_PALETTE, DEFAULT_TERRAIN_ID
from editor.terrain.terrain_tool import ensure_terrain_data


def draw_editor_terrain(screen, scene_data, camera):
    ensure_terrain_data(scene_data)

    tile_size = camera.get_tile_size()

    for tile in scene_data["terrain"].get("tiles", []):
        cell = tile.get("cell")
        terrain_id = tile.get("terrain_id")

        if not isinstance(cell, list):
            continue

        if len(cell) < 2:
            continue

        color = get_terrain_color(terrain_id)

        rect = pygame.Rect(
            cell[0] * tile_size - camera.x,
            cell[1] * tile_size - camera.y,
            tile_size,
            tile_size,
        )

        pygame.draw.rect(screen, color, rect)

def get_terrain_color(terrain_id):
    terrain_data = TERRAIN_PALETTE.get(terrain_id)

    if terrain_data is None:
        terrain_data = TERRAIN_PALETTE[DEFAULT_TERRAIN_ID]

    return terrain_data["color"]
