import pygame

from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.art.terrain_textures import create_grass_texture


_grass_texture = None


def draw_world_background(screen, camera_x, camera_y):
    global _grass_texture

    if _grass_texture is None:
        _grass_texture = create_grass_texture(WORLD_WIDTH, WORLD_HEIGHT, seed=10)

    screen.blit(_grass_texture, (-camera_x, -camera_y))