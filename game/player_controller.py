import pygame

from game.construction.construction_manager import is_cell_occupied
from game.world.grid_manager import world_to_grid
from game.world.occupancy import movement_multiplier
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT

PLAYER_FOOT_OFFSET_Y = 6
PLAYER_COLLISION_WIDTH = 10
PLAYER_COLLISION_HEIGHT = 6


def update_player_movement(state, speed, dt, world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT, world_objects=None):
    keys = pygame.key.get_pressed()
    player = state["player"]

    if "direction" not in player:
        player["direction"] = "down"

    dx = 0
    dy = 0

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += 1
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += 1

    if dx < 0:
        player["direction"] = "left"
    elif dx > 0:
        player["direction"] = "right"
    elif dy < 0:
        player["direction"] = "up"
    elif dy > 0:
        player["direction"] = "down"

    if dx != 0 or dy != 0:
        length = (dx * dx + dy * dy) ** 0.5

        speed *= movement_multiplier(state, player["x"], player["y"])
        next_x = player["x"] + dx / length * speed * dt
        next_y = player["y"] + dy / length * speed * dt

        left = next_x - PLAYER_COLLISION_WIDTH // 2
        right = next_x + PLAYER_COLLISION_WIDTH // 2

        top = next_y + PLAYER_FOOT_OFFSET_Y
        bottom = top + PLAYER_COLLISION_HEIGHT

        collision_points = [
            world_to_grid(left, top),
            world_to_grid(right, top),
            world_to_grid(left, bottom),
            world_to_grid(right, bottom),
        ]

        blocked = False

        for grid_x, grid_y in collision_points:
            if is_cell_occupied(state, grid_x, grid_y, world_objects):
                blocked = True
                break

        if not blocked:
            player["x"] = next_x
            player["y"] = next_y

    player["x"] = max(20, min(world_width - 20, player["x"]))
    player["y"] = max(20, min(world_height - 20, player["y"]))


def position_for_tile_action(player, target, walkable=None):
    """Choose a standing tile and facing for a nearby clicked tile.

    Directly reachable tiles: stand at the target center.
    One tile farther: stand at the closest reachable cardinal neighbor,
    facing the clicked tile. Return None for unreachable destinations.
    """
    from game.world.action_range import reachable_cells
    from game.world.grid_manager import TILE_SIZE
    tx, ty = target
    reach = reachable_cells(player)
    if target in reach:
        # Already within reach: turn in place, never snap onto the clicked tile.
        dx = tx * TILE_SIZE + TILE_SIZE / 2 - player["x"]
        dy = ty * TILE_SIZE + TILE_SIZE / 2 - player["y"]
        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        elif abs(dy) > 0:
            direction = "down" if dy > 0 else "up"
        else:
            direction = player.get("direction", "down")
        return player["x"], player["y"], direction
    candidates = [(tx + dx, ty + dy) for dx, dy in
                  ((-1, 0), (1, 0), (0, -1), (0, 1))
                  if (tx + dx, ty + dy) in reach]
    candidates.sort(key=lambda c: (c[0] * TILE_SIZE + TILE_SIZE / 2 - player["x"]) ** 2
                    + (c[1] * TILE_SIZE + TILE_SIZE / 2 - player["y"]) ** 2)
    for sx, sy in candidates:
        x, y = sx * TILE_SIZE + TILE_SIZE / 2, sy * TILE_SIZE + TILE_SIZE / 2
        if walkable is not None and not walkable(x, y):
            continue
        if (sx, sy) == target:
            direction = player.get("direction", "down")
        elif tx > sx:
            direction = "right"
        elif tx < sx:
            direction = "left"
        elif ty > sy:
            direction = "down"
        else:
            direction = "up"
        return x, y, direction
    return None
