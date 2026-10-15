"""Shared tile interaction reach: occupied tiles and edge-sharing neighbors."""
from game.world.grid_manager import TILE_SIZE

def occupied_cells(player, width=26, height=26):
    """All tiles touched by the visible player marker (normally up to four)."""
    x, y = player["x"], player["y"]
    left, right = x - width / 2, x + width / 2
    top, bottom = y - height / 2, y + height / 2
    epsilon = 0.0001
    return {(gx, gy)
            for gx in range(int(left // TILE_SIZE), int((right - epsilon) // TILE_SIZE) + 1)
            for gy in range(int(top // TILE_SIZE), int((bottom - epsilon) // TILE_SIZE) + 1)}

def reachable_cells(player):
    """Tiles beneath the player plus cardinal neighbors; never diagonals."""
    occupied = occupied_cells(player)
    cardinal = ((-1, 0), (1, 0), (0, -1), (0, 1))
    return occupied | {(x + dx, y + dy) for x, y in occupied for dx, dy in cardinal}

def can_interact_cell(player, gx, gy, include_occupied=False):
    # Retain the optional argument for existing farming callers.
    return (gx, gy) in reachable_cells(player)

def can_interact_point(player, x, y):
    return can_interact_cell(player, int(x // TILE_SIZE), int(y // TILE_SIZE))
