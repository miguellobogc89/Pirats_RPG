import pygame

from game.world.grid_manager import TILE_SIZE, grid_to_world
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT


GRID_COLOR = (90, 130, 80)
TILLED_COLOR = (115, 78, 45)
WATERED_COLOR = (72, 82, 95)
SEED_COLOR = (225, 200, 60)
SPROUT_COLOR = (80, 170, 70)
GROWN_COLOR = (210, 175, 45)


def draw_world_grid(screen, camera_x, camera_y):
    width = screen.get_width()
    height = screen.get_height()

    start_x = int(camera_x // TILE_SIZE) * TILE_SIZE
    end_x = min(camera_x + width, WORLD_WIDTH)

    start_y = int(camera_y // TILE_SIZE) * TILE_SIZE
    end_y = min(camera_y + height, WORLD_HEIGHT)

    x = start_x
    while x <= end_x:
        screen_x = int(x - camera_x)
        pygame.draw.line(screen, GRID_COLOR, (screen_x, 0), (screen_x, height), 1)
        x += TILE_SIZE

    y = start_y
    while y <= end_y:
        screen_y = int(y - camera_y)
        pygame.draw.line(screen, GRID_COLOR, (0, screen_y), (width, screen_y), 1)
        y += TILE_SIZE


def draw_tilled_cells(screen, state, camera_x, camera_y):
    farming = state.get("farming", {})
    tilled_cells = farming.get("tilled_cells", [])

    for cell in tilled_cells:
        grid_x = cell[0]
        grid_y = cell[1]

        world_x, world_y = grid_to_world(grid_x, grid_y)

        screen_x = int(world_x - camera_x)
        screen_y = int(world_y - camera_y)

        rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, TILLED_COLOR, rect)

def draw_crops(screen, state, camera_x, camera_y):
    crops = state.get("farming", {}).get("crops", [])

    for crop in crops:
        world_x, world_y = grid_to_world(crop["grid_x"], crop["grid_y"])

        screen_x = int(world_x - camera_x)
        screen_y = int(world_y - camera_y)

        center_x = screen_x + TILE_SIZE // 2
        center_y = screen_y + TILE_SIZE // 2

        stage = crop.get("stage", 0)

        color = SEED_COLOR
        radius = 3

        if stage == 1:
            color = SPROUT_COLOR
            radius = 4

        elif stage >= 2:
            color = GROWN_COLOR
            radius = 6

        pygame.draw.circle(screen, color, (center_x, center_y), radius)

def draw_watered_cells(screen, state, camera_x, camera_y):
    farming = state.get("farming", {})
    watered_cells = farming.get("watered_cells", [])

    for cell in watered_cells:
        grid_x = cell[0]
        grid_y = cell[1]

        world_x, world_y = grid_to_world(grid_x, grid_y)

        screen_x = int(world_x - camera_x)
        screen_y = int(world_y - camera_y)

        rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, WATERED_COLOR, rect)