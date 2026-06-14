import pygame

from game.world.grid_manager import TILE_SIZE
from editor.terrain.terrain_palette import TERRAIN_PALETTE, DEFAULT_TERRAIN_ID
from editor.terrain.terrain_tool import ensure_terrain_data


def draw_editor_terrain(screen, scene_data, camera):
    ensure_terrain_data(scene_data)

    tile_size = int(TILE_SIZE * camera.zoom)
    default_terrain_id = scene_data["terrain"].get("default", DEFAULT_TERRAIN_ID)

    default_color = get_terrain_color(default_terrain_id)

    width = scene_data.get("width", 80)
    height = scene_data.get("height", 60)

    for y in range(height):
        for x in range(width):
            screen_x = int(x * TILE_SIZE * camera.zoom - camera.x)
            screen_y = int(y * TILE_SIZE * camera.zoom - camera.y)

            rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
            pygame.draw.rect(screen, default_color, rect)

    for tile in scene_data["terrain"].get("tiles", []):
        cell = tile.get("cell")
        terrain_id = tile.get("terrain_id")

        if not isinstance(cell, list):
            continue

        if len(cell) < 2:
            continue

        color = get_terrain_color(terrain_id)

        screen_x = int(cell[0] * TILE_SIZE * camera.zoom - camera.x)
        screen_y = int(cell[1] * TILE_SIZE * camera.zoom - camera.y)

        rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
        pygame.draw.rect(screen, color, rect)


def get_terrain_color(terrain_id):
    terrain_data = TERRAIN_PALETTE.get(terrain_id)

    if terrain_data is None:
        terrain_data = TERRAIN_PALETTE[DEFAULT_TERRAIN_ID]

    return terrain_data["color"]