"""Fondo de suelo en pixel art de cuatro grises, estable al mover la camara."""
import pygame
from functools import lru_cache

from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT

BACKGROUND = (240, 240, 240)
BOUNDARY = (104, 104, 104)


@lru_cache(maxsize=4)
def _ground_tile(variant):
    tile = pygame.Surface((32, 32))
    tile.fill(BACKGROUND)
    for x, y in (
        ((4, 6), (20, 23), (25, 8)),
        ((7, 24), (22, 10), (3, 5)),
        ((5, 17), (16, 4), (26, 26)),
        ((9, 6), (22, 17), (4, 26)),
    )[variant]:
        pygame.draw.rect(tile, (184, 184, 184), (x, y, 2, 4))
        pygame.draw.rect(tile, (184, 184, 184), (x + 3, y + 2, 2, 2))
        pygame.draw.rect(tile, (104, 104, 104), (x + 2, y + 4, 1, 1))
    return tile


def draw_world_background(screen, camera_x, camera_y):
    screen.fill(BACKGROUND)
    view = pygame.Rect(0, 0, screen.get_width(), screen.get_height())
    world_view = pygame.Rect(
        int(-camera_x), int(-camera_y), WORLD_WIDTH, WORLD_HEIGHT
    ).clip(view)
    if world_view.width and world_view.height:
        old_clip = screen.get_clip()
        screen.set_clip(world_view)
        gx0 = int(camera_x // 32)
        gy0 = int(camera_y // 32)
        gx1 = int((camera_x + screen.get_width()) // 32) + 1
        gy1 = int((camera_y + screen.get_height()) // 32) + 1
        for gx in range(gx0, gx1 + 1):
            sx = int(gx * 32 - camera_x)
            for gy in range(gy0, gy1 + 1):
                sy = int(gy * 32 - camera_y)
                screen.blit(_ground_tile((gx * 3 + gy * 7 + gx * gy) % 4), (sx, sy))
        screen.set_clip(old_clip)
    pygame.draw.rect(screen, BOUNDARY, (-camera_x, -camera_y, WORLD_WIDTH, WORLD_HEIGHT), 1)
