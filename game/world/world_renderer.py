"""Fondo neutro provisional: sin hierba, texturas ni color."""
import pygame

from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT

BACKGROUND = (248, 248, 248)
BOUNDARY = (193, 193, 193)


def draw_world_background(screen, camera_x, camera_y):
    screen.fill(BACKGROUND)
    bounds = pygame.Rect(-camera_x, -camera_y, WORLD_WIDTH, WORLD_HEIGHT)
    pygame.draw.rect(screen, BOUNDARY, bounds, 1)
