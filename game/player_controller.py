import pygame

from game.construction.construction_manager import is_cell_occupied
from game.world.grid_manager import world_to_grid

PLAYER_FOOT_OFFSET_Y = 6
PLAYER_COLLISION_WIDTH = 10
PLAYER_COLLISION_HEIGHT = 6


def update_player_movement(state, speed, dt):
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
            if is_cell_occupied(state, grid_x, grid_y):
                blocked = True
                break

        if not blocked:
            player["x"] = next_x
            player["y"] = next_y

    player["x"] = max(20, min(1580, player["x"]))
    player["y"] = max(20, min(1180, player["y"]))