import random
import pygame


GRASS_BASE = (76, 145, 68)
GRASS_DARK = (55, 115, 52)
GRASS_LIGHT = (105, 170, 82)


def create_grass_texture(width, height, seed=1):
    random.seed(seed)

    surface = pygame.Surface((width, height))
    surface.fill(GRASS_BASE)

    for _ in range((width * height) // 180):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 3)

        color = GRASS_DARK

        if random.random() > 0.5:
            color = GRASS_LIGHT

        blade_height = random.randint(1, 3)

        for i in range(blade_height):
            surface.set_at((x, y - i), color)

    return surface