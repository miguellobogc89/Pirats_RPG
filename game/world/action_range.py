"""Shared grid-based player reach for all world interactions."""
from game.world.grid_manager import TILE_SIZE

def occupied_cells(player, width=10, height=6):
    x, y = player["x"], player["y"]
    # Match player_controller foot collision footprint.
    left, right = x - width / 2, x + width / 2
    top, bottom = y + 6, y + 6 + height
    return {(gx, gy) for gx in range(int(left // TILE_SIZE), int(right // TILE_SIZE) + 1)
            for gy in range(int(top // TILE_SIZE), int(bottom // TILE_SIZE) + 1)}

def reachable_cells(player):
    occupied = occupied_cells(player)
    return {(x + dx, y + dy) for x, y in occupied
            for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - occupied

def can_interact_cell(player, gx, gy, include_occupied=False):
    cells = reachable_cells(player)
    if include_occupied:
        cells |= occupied_cells(player)
    return (gx, gy) in cells

def can_interact_point(player, x, y):
    return can_interact_cell(player, int(x // TILE_SIZE), int(y // TILE_SIZE))
