BLOCKED_CELLS = set()


def is_map_cell_blocked(grid_x, grid_y):
    return (grid_x, grid_y) in BLOCKED_CELLS

def load_test_collisions():
    for x in range(20, 35):
        BLOCKED_CELLS.add((x, 15))

from game.world.grid_manager import world_to_grid
from game.world_objects import WORLD_OBJECTS


def is_world_object_cell_blocked(state, grid_x, grid_y):
    destroyed_objects = state.get("destroyed_world_objects", [])

    for world_object in WORLD_OBJECTS:
        if world_object["id"] in destroyed_objects:
            continue

        if world_object["type"] not in ["tree", "rock", "bush"]:
            continue

        object_grid_x, object_grid_y = world_to_grid(
            world_object["x"],
            world_object["y"],
        )

        if grid_x == object_grid_x and grid_y == object_grid_y:
            return True

    return False