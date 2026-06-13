from game.world.collision_manager import (
    is_map_cell_blocked,
    is_world_object_cell_blocked,
)

def ensure_construction_state(state):
    if "placed_objects" not in state:
        state["placed_objects"] = []


def is_cell_occupied(state, grid_x, grid_y):
    ensure_construction_state(state)

    if is_map_cell_blocked(grid_x, grid_y):
        return True
    if is_world_object_cell_blocked(state, grid_x, grid_y):
        return True

    for obj in state["placed_objects"]:
        start_x = obj["grid_x"]
        start_y = obj["grid_y"]

        width = obj["width"]
        height = obj["height"]

        if (
            grid_x >= start_x
            and grid_x < start_x + width
            and grid_y >= start_y
            and grid_y < start_y + height
        ):
            return True

    return False


def can_place_object(state, grid_x, grid_y, width, height):
    for x in range(grid_x, grid_x + width):
        for y in range(grid_y, grid_y + height):
            if is_cell_occupied(state, x, y):
                return False

    return True


def place_object(state, item_id, grid_x, grid_y, width, height):
    ensure_construction_state(state)

    if not can_place_object(state, grid_x, grid_y, width, height):
        return False

    state["placed_objects"].append({
        "item_id": item_id,
        "grid_x": grid_x,
        "grid_y": grid_y,
        "width": width,
        "height": height,
    })

    return True