import pygame

from game.scenes.scene_state import get_current_scene_state
from game.world.grid_manager import TILE_SIZE, grid_to_world
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.data.item_database import get_item_data
from game.world.collision_manager import BLOCKED_CELLS, get_scene_collision_rects
from game.ui.sprite_renderer import draw_item_sprite


GRID_COLOR = (90, 130, 80)
TILLED_COLOR = (115, 78, 45)
WATERED_COLOR = (72, 82, 95)
SEED_COLOR = (225, 200, 60)
SPROUT_COLOR = (80, 170, 70)
GROWN_COLOR = (210, 175, 45)


def draw_world_grid(screen, camera_x, camera_y, world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT):
    width = screen.get_width()
    height = screen.get_height()

    start_x = int(camera_x // TILE_SIZE) * TILE_SIZE
    end_x = min(camera_x + width, world_width)

    start_y = int(camera_y // TILE_SIZE) * TILE_SIZE
    end_y = min(camera_y + height, world_height)

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
    farming = get_current_scene_state(state)
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
    crops = get_current_scene_state(state).get("crops", [])

    for crop in crops:
        world_x, world_y = grid_to_world(crop["grid_x"], crop["grid_y"])

        screen_x = int(world_x - camera_x)
        screen_y = int(world_y - camera_y)

        stage = crop.get("stage", 0)

        sprite_item_id = "corn_seed"
        sprite_size = 18

        if stage == 1:
            sprite_item_id = "corn_seed"
            sprite_size = 24

        elif stage >= 2:
            sprite_item_id = "corn"
            sprite_size = 34

        item_data = get_item_data(sprite_item_id)

        if item_data is None:
            continue

        draw_item_sprite(
            screen,
            item_data,
            pygame.Rect(
                screen_x + (TILE_SIZE - sprite_size) // 2,
                screen_y + TILE_SIZE - sprite_size,
                sprite_size,
                sprite_size,
            ),
            padding=0,
        )

def draw_watered_cells(screen, state, camera_x, camera_y):
    farming = get_current_scene_state(state)
    watered_cells = farming.get("watered_cells", [])

    for cell in watered_cells:
        grid_x = cell[0]
        grid_y = cell[1]

        world_x, world_y = grid_to_world(grid_x, grid_y)

        screen_x = int(world_x - camera_x)
        screen_y = int(world_y - camera_y)

        rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, WATERED_COLOR, rect)

def draw_placed_objects(screen, state, camera_x, camera_y):
    placed_objects = get_current_scene_state(state).get("placed_objects", [])

    for obj in placed_objects:
        world_x, world_y = grid_to_world(obj["grid_x"], obj["grid_y"])

        screen_x = int(world_x - camera_x)
        screen_y = int(world_y - camera_y)

        rect = pygame.Rect(
            screen_x,
            screen_y,
            obj["width"] * TILE_SIZE,
            obj["height"] * TILE_SIZE,
        )

        item_data = get_item_data(obj["item_id"])
        if item_data is not None:
            draw_item_sprite(screen, item_data, rect, padding=2)

def draw_occupied_cells_debug(screen, state, camera_x, camera_y):
    placed_objects = get_current_scene_state(state).get("placed_objects", [])

    for obj in placed_objects:
        start_x = obj["grid_x"]
        start_y = obj["grid_y"]

        for grid_x in range(start_x, start_x + obj["width"]):
            for grid_y in range(start_y, start_y + obj["height"]):
                world_x, world_y = grid_to_world(grid_x, grid_y)

                screen_x = int(world_x - camera_x)
                screen_y = int(world_y - camera_y)

                rect = pygame.Rect(
                    screen_x,
                    screen_y,
                    TILE_SIZE,
                    TILE_SIZE,
                )

                pygame.draw.rect(screen, (190, 60, 60), rect, 2)


def draw_collision_debug(screen, camera_x, camera_y):
    for grid_x, grid_y in BLOCKED_CELLS:
        world_x, world_y = grid_to_world(grid_x, grid_y)

        screen_x = int(world_x - camera_x)
        screen_y = int(world_y - camera_y)

        rect = pygame.Rect(
            screen_x,
            screen_y,
            TILE_SIZE,
            TILE_SIZE,
        )

        pygame.draw.rect(screen, (255, 0, 0), rect, 1)

    for collision_rect in get_scene_collision_rects():
        rect = pygame.Rect(
            int(collision_rect.x - camera_x),
            int(collision_rect.y - camera_y),
            collision_rect.width,
            collision_rect.height,
        )

        pygame.draw.rect(screen, (255, 80, 80), rect, 2)
