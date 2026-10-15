"""Shared physical-contact grid reach for all world interactions."""
from game.world.grid_manager import TILE_SIZE

def occupied_cells(player, width=10, height=6):
    """Cells intersected by the player's foot collision rectangle (up to four)."""
    x, y = player["x"], player["y"]
    left, right = x - width / 2, x + width / 2
    top, bottom = y + 6, y + 6 + height
    epsilon = 0.0001
    return {(gx, gy)
            for gx in range(int(left // TILE_SIZE), int((right - epsilon) // TILE_SIZE) + 1)
            for gy in range(int(top // TILE_SIZE), int((bottom - epsilon) // TILE_SIZE) + 1)}

def reachable_cells(player):
    """Physical contact only; never add an outer ring of neighboring tiles."""
    return occupied_cells(player)

def can_interact_cell(player, gx, gy, include_occupied=False):
    # Retain the optional argument for existing farming callers.
    return (gx, gy) in reachable_cells(player)

def can_interact_point(player, x, y):
    return can_interact_cell(player, int(x // TILE_SIZE), int(y // TILE_SIZE))
