import pygame

from game.scenes.scene_state import get_current_scene_state
from game.world.grid_manager import TILE_SIZE, grid_to_world
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.data.item_database import get_item_data
from game.world.collision_manager import BLOCKED_CELLS, get_scene_collision_rects
from game.ui.sprite_renderer import draw_item_sprite


GRID_COLOR = (175, 175, 175)
TILLED_COLOR = (207, 207, 207)
WATERED_COLOR = (176, 176, 176)
SEED_COLOR = (100, 100, 100)
SPROUT_COLOR = (90, 90, 90)
GROWN_COLOR = (65, 65, 65)


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
    """Simple monochrome seed, sprout and mature maize silhouettes."""
    crops = get_current_scene_state(state).get("crops", [])
    for crop in crops:
        x, y = grid_to_world(crop["grid_x"], crop["grid_y"])
        x, y = int(x - camera_x), int(y - camera_y)
        stage = crop.get("stage", 0)
        if crop.get("dead", False):
            faded = crop.get("dead_days", 0) >= 1
            stem = (194, 181, 164) if faded else (115, 95, 75)
            leaf = (207, 196, 177) if faded else (150, 125, 90)
            pygame.draw.line(screen, stem, (x + 16, y + 28), (x + 19, y + 18), 3)
            pygame.draw.line(screen, stem, (x + 19, y + 18), (x + 24, y + 24), 2)
            pygame.draw.line(screen, leaf, (x + 18, y + 22), (x + 10, y + 25), 2)
            pygame.draw.ellipse(screen, leaf, (x + 21, y + 22, 8, 4))
            continue
        if stage == 0:
            for dx, dy in ((10, 19), (16, 17), (22, 20)):
                pygame.draw.circle(screen, SEED_COLOR, (x + dx, y + dy), 2)
            continue
        height = min(27, 7 + stage * 7)
        bottom = y + 28
        pygame.draw.line(screen, SPROUT_COLOR, (x + 16, bottom), (x + 16, bottom - height), 2)
        pygame.draw.line(screen, SPROUT_COLOR, (x + 16, bottom - height // 2),
                         (x + 9, bottom - height // 2 - 6), 2)
        if stage >= 2:
            pygame.draw.line(screen, SPROUT_COLOR, (x + 16, bottom - height // 2 - 3),
                             (x + 24, bottom - height // 2 - 10), 2)
        if stage >= 3:
            for dx, dy in ((-5, -11), (5, -15), (-3, -22)):
                pygame.draw.ellipse(screen, GROWN_COLOR, (x + 16 + dx, bottom + dy, 6, 10))



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
            if draw_item_sprite(screen, item_data, rect, padding=2) is None:
                draw_placeable_fallback(screen, obj["item_id"], rect)

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

def draw_farm_reach_grid(screen, player, camera_x, camera_y, bounds, mode="cardinal"):
    """Debug grid and reach overlay, monochrome and only on chapter farm."""
    from game.world.action_range import occupied_cells, reachable_cells
    left, top, width, height = bounds
    x0, y0 = int(left // TILE_SIZE), int(top // TILE_SIZE)
    x1, y1 = int((left + width) // TILE_SIZE), int((top + height) // TILE_SIZE)
    reach = reachable_cells(player, mode)
    feet = occupied_cells(player)
    for gx in range(x0, x1 + 1):
        for gy in range(y0, y1 + 1):
            rect = pygame.Rect(int(gx * TILE_SIZE - camera_x), int(gy * TILE_SIZE - camera_y), TILE_SIZE, TILE_SIZE)
            if (gx, gy) in feet:
                pygame.draw.rect(screen, (185, 185, 185), rect)
            elif (gx, gy) in reach:
                pygame.draw.rect(screen, (224, 224, 224), rect)
            pygame.draw.rect(screen, (225, 225, 225), rect, 1)

def draw_wild_bushes(screen, state, camera_x, camera_y):
    """Draw wild shrub silhouettes."""
    bushes = get_current_scene_state(state).get("wild_bushes", [])
    for gx, gy in bushes:
        wx, wy = grid_to_world(gx, gy)
        x, y = int(wx - camera_x), int(wy - camera_y)
        pygame.draw.polygon(screen, (78, 105, 71), [(x+4,y+25),(x+8,y+13),(x+14,y+16),(x+17,y+7),(x+23,y+15),(x+28,y+13),(x+29,y+26)])
        pygame.draw.polygon(screen, (105, 132, 85), [(x+6,y+22),(x+12,y+11),(x+18,y+17),(x+22,y+10),(x+27,y+23)])


def draw_placeable_fallback(screen, item_id, rect):
    """Visible world art for placeables that do not yet have PNG assets."""
    import pygame
    inset = rect.inflate(-max(4, rect.width // 10), -max(4, rect.height // 10))
    if item_id == "wooden_chest":
        pygame.draw.rect(screen, (106, 65, 37), inset, border_radius=3)
        pygame.draw.rect(screen, (174, 112, 59), inset.inflate(-6, -6), border_radius=2)
        pygame.draw.line(screen, (83, 54, 31), (inset.left, inset.centery), (inset.right, inset.centery), 3)
        pygame.draw.rect(screen, (222, 183, 79), (rect.centerx - 3, rect.centery - 4, 6, 9))
    elif item_id == "wooden_fence":
        for x in (inset.left + 3, inset.right - 7):
            pygame.draw.rect(screen, (118, 73, 43), (x, inset.top, 6, inset.height))
        for y in (inset.top + inset.height // 3, inset.top + 2 * inset.height // 3):
            pygame.draw.rect(screen, (174, 116, 65), (inset.left, y, inset.width, 6))
    elif item_id == "wood_floor":
        pygame.draw.rect(screen, (167, 113, 70), inset)
        for y in (inset.top + inset.height // 3, inset.top + 2 * inset.height // 3):
            pygame.draw.line(screen, (108, 71, 44), (inset.left, y), (inset.right, y), 2)
    else:
        pygame.draw.rect(screen, (129, 95, 61), inset, border_radius=3)
        pygame.draw.rect(screen, (77, 58, 43), inset, 2, border_radius=3)
