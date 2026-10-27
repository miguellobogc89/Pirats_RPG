import pygame
from functools import lru_cache

from game.scenes.scene_state import get_current_scene_state
from game.world.grid_manager import TILE_SIZE, grid_to_world
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.data.item_database import get_item_data
from game.world.collision_manager import BLOCKED_CELLS, get_scene_collision_rects
from game.ui.sprite_renderer import draw_item_sprite


GB_WHITE = (240, 240, 240)
GB_LIGHT = (184, 184, 184)
GB_MID = (104, 104, 104)
GB_BLACK = (24, 24, 24)
GRID_COLOR = GB_LIGHT
TILLED_COLOR = GB_MID
WATERED_COLOR = GB_BLACK
SEED_COLOR = GB_BLACK
SPROUT_COLOR = GB_BLACK
GROWN_COLOR = GB_MID


@lru_cache(maxsize=4)
def _grass_tile(variant):
    """Hierba de 32 px en cuatro tonos de gris puro."""
    tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
    tile.fill(GB_WHITE)
    for x, y in (((5, 9), (19, 21), (26, 4)),
                 ((9, 24), (23, 8), (4, 4)),
                 ((3, 17), (15, 4), (25, 25)),
                 ((9, 5), (21, 15), (5, 26)))[variant]:
        pygame.draw.rect(tile, GB_LIGHT, (x, y, 2, 4))
        pygame.draw.rect(tile, GB_LIGHT, (x + 3, y + 1, 2, 3))
        pygame.draw.rect(tile, GB_MID, (x + 2, y + 4, 1, 1))
    return tile


def _draw_grass(screen, camera_x, camera_y, bounds):
    left, top, width, height = bounds
    rect = pygame.Rect(int(left-camera_x), int(top-camera_y), int(width), int(height))
    visible = rect.clip(screen.get_rect())
    if not visible.width or not visible.height:
        return
    old_clip = screen.get_clip()
    screen.set_clip(visible)
    for gx in range(int(left // TILE_SIZE), int((left+width-1) // TILE_SIZE)+1):
        x = int(gx*TILE_SIZE-camera_x)
        if x >= visible.right or x+TILE_SIZE <= visible.left:
            continue
        for gy in range(int(top // TILE_SIZE), int((top+height-1) // TILE_SIZE)+1):
            y = int(gy*TILE_SIZE-camera_y)
            if y >= visible.bottom or y+TILE_SIZE <= visible.top:
                continue
            screen.blit(_grass_tile((gx*3+gy*7+gx*gy) % 4), (x, y))
    screen.set_clip(old_clip)


def _draw_soil(screen, rect, wet=False):
    pygame.draw.rect(screen, GB_BLACK if wet else GB_MID, rect)
    for offset in (5, 14, 23):
        pygame.draw.rect(screen, GB_MID if wet else GB_LIGHT, (rect.x+3, rect.y+offset, TILE_SIZE-6, 2))
        pygame.draw.rect(screen, GB_LIGHT, (rect.x+7, rect.y+offset+4, 3, 1))
    if wet:
        for dx, dy in ((5, 3), (24, 12), (13, 27)):
            pygame.draw.rect(screen, GB_LIGHT, (rect.x+dx, rect.y+dy, 2, 2))

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
    for gx, gy in get_current_scene_state(state).get("tilled_cells", []):
        x, y = grid_to_world(gx, gy)
        _draw_soil(screen, pygame.Rect(int(x-camera_x), int(y-camera_y), TILE_SIZE, TILE_SIZE))


def draw_crops(screen, state, camera_x, camera_y):
    """Cultivos por etapas con siluetas pixeladas, sin suavizado."""
    for crop in get_current_scene_state(state).get("crops", []):
        wx, wy = grid_to_world(crop["grid_x"], crop["grid_y"])
        x, y = int(wx-camera_x), int(wy-camera_y)
        stage = crop.get("stage", 0)
        if crop.get("dead", False):
            shade = GB_LIGHT if crop.get("dead_days", 0) >= 1 else GB_MID
            pygame.draw.rect(screen, shade, (x+15, y+15, 2, 13))
            pygame.draw.rect(screen, shade, (x+8, y+23, 8, 2))
            pygame.draw.rect(screen, shade, (x+17, y+21, 9, 2))
        elif stage == 0:
            for dx, dy in ((10, 19), (16, 17), (22, 20)):
                pygame.draw.rect(screen, GB_BLACK, (x+dx, y+dy, 3, 2))
        else:
            height = min(26, 6+stage*7)
            pygame.draw.rect(screen, GB_BLACK, (x+15, y+29-height, 3, height))
            pygame.draw.rect(screen, GB_LIGHT, (x+16, y+31-height, 1, max(1,height-4)))
            pygame.draw.rect(screen, GB_BLACK, (x+8, y+18, 8, 3))
            pygame.draw.rect(screen, GB_MID, (x+10, y+16, 6, 2))
            if stage >= 2:
                pygame.draw.rect(screen, GB_BLACK, (x+17, y+13, 8, 3))
                pygame.draw.rect(screen, GB_MID, (x+17, y+11, 6, 2))
            if stage >= 3:
                pygame.draw.rect(screen, GB_BLACK, (x+12, y+5, 8, 12))
                pygame.draw.rect(screen, GB_LIGHT, (x+14, y+7, 4, 7))
                pygame.draw.rect(screen, GB_MID, (x+13, y+9, 6, 2))


def draw_watered_cells(screen, state, camera_x, camera_y):
    for gx, gy in get_current_scene_state(state).get("watered_cells", []):
        x, y = grid_to_world(gx, gy)
        _draw_soil(screen, pygame.Rect(int(x-camera_x), int(y-camera_y), TILE_SIZE, TILE_SIZE), wet=True)

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
    """Terreno dibujado en pixeles y alcance indicado sin cuadricula masiva."""
    from game.world.action_range import occupied_cells, reachable_cells
    _draw_grass(screen, camera_x, camera_y, bounds)
    left, top, width, height = bounds
    reach = reachable_cells(player, mode)
    feet = occupied_cells(player)
    for gx in range(int(left//TILE_SIZE), int((left+width)//TILE_SIZE)+1):
        for gy in range(int(top//TILE_SIZE), int((top+height)//TILE_SIZE)+1):
            if (gx, gy) not in feet and (gx, gy) not in reach:
                continue
            rect = pygame.Rect(int(gx*TILE_SIZE-camera_x), int(gy*TILE_SIZE-camera_y), TILE_SIZE, TILE_SIZE)
            if (gx, gy) in feet:
                pygame.draw.rect(screen, GB_LIGHT, rect)
                pygame.draw.rect(screen, GB_BLACK, rect, 2)
            else:
                pygame.draw.rect(screen, GB_LIGHT, rect, 1)
                pygame.draw.rect(screen, GB_MID, rect.inflate(-4, -4), 1)

def draw_wild_bushes(screen, state, camera_x, camera_y):
    """Matorrales con volumen y sombreado de cuatro grises."""
    for gx, gy in get_current_scene_state(state).get("wild_bushes", []):
        wx, wy = grid_to_world(gx, gy)
        x, y = int(wx-camera_x), int(wy-camera_y)
        for color, dx, dy, w, h in (
            (GB_BLACK, 6, 18, 21, 10), (GB_BLACK, 9, 11, 15, 18),
            (GB_BLACK, 13, 6, 8, 21), (GB_MID, 8, 19, 17, 6),
            (GB_MID, 10, 12, 12, 12), (GB_LIGHT, 11, 13, 5, 5),
            (GB_LIGHT, 18, 18, 5, 4), (GB_LIGHT, 9, 23, 5, 2),
            (GB_BLACK, 15, 27, 3, 3)):
            pygame.draw.rect(screen, color, (x+dx, y+dy, w, h))

def draw_placeable_fallback(screen, item_id, rect):
    """Cofres, vallas y tablones en estilo pixel art de grises."""
    inset = rect.inflate(-max(4, rect.width//10), -max(4, rect.height//10))
    if item_id == "wooden_chest":
        pygame.draw.rect(screen, GB_BLACK, inset)
        pygame.draw.rect(screen, GB_MID, inset.inflate(-4,-4))
        pygame.draw.rect(screen, GB_LIGHT, (inset.left+3, inset.top+3, inset.width-6, 3))
        pygame.draw.rect(screen, GB_BLACK, (inset.left, inset.centery, inset.width, 3))
        pygame.draw.rect(screen, GB_WHITE, (rect.centerx-2, rect.centery-2, 4, 5))
    elif item_id == "wooden_fence":
        for x in (inset.left+3, inset.right-7):
            pygame.draw.rect(screen, GB_BLACK, (x, inset.top, 6, inset.height))
            pygame.draw.rect(screen, GB_LIGHT, (x+1, inset.top+2, 2, inset.height-4))
        for y in (inset.top+inset.height//3, inset.top+2*inset.height//3):
            pygame.draw.rect(screen, GB_MID, (inset.left, y, inset.width, 6))
            pygame.draw.rect(screen, GB_LIGHT, (inset.left+2, y+1, inset.width-4, 2))
    elif item_id == "wood_floor":
        pygame.draw.rect(screen, GB_LIGHT, inset)
        for y in (inset.top+inset.height//3, inset.top+2*inset.height//3):
            pygame.draw.rect(screen, GB_MID, (inset.left, y, inset.width, 2))
    else:
        pygame.draw.rect(screen, GB_MID, inset)
        pygame.draw.rect(screen, GB_BLACK, inset, 2)
