"""Tile-based action ranges, anchored to the one tile beneath the player."""
from game.world.grid_manager import TILE_SIZE

CARDINAL = ((0, -1), (0, 1), (-1, 0), (1, 0))
EIGHT = tuple((dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy)

def player_cell(player):
    return int(player["x"] // TILE_SIZE), int(player["y"] // TILE_SIZE)

def occupied_cells(player, width=26, height=26):
    """The single logical tile under the player."""
    return {player_cell(player)}

def reachable_cells(player, mode="cardinal"):
    x, y = player_cell(player)
    offsets = EIGHT if mode == "eight" else CARDINAL
    return {(x + dx, y + dy) for dx, dy in offsets}

def can_interact_cell(player, gx, gy, include_occupied=False, mode="cardinal"):
    return (gx, gy) in reachable_cells(player, mode) or (include_occupied and (gx, gy) in occupied_cells(player))

def can_interact_point(player, x, y):
    return can_interact_cell(player, int(x // TILE_SIZE), int(y // TILE_SIZE))

def face_target(player, gx, gy):
    """Face the clicked tile without changing position."""
    px, py = player_cell(player)
    dx, dy = gx - px, gy - py
    if abs(dx) >= abs(dy) and dx:
        player["direction"] = "right" if dx > 0 else "left"
    elif dy:
        player["direction"] = "down" if dy > 0 else "up"
