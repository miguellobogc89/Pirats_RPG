from game.world.collision_manager import (
    is_map_cell_blocked,
    is_world_object_cell_blocked,
)
from game.scenes.scene_state import get_current_scene_state

def ensure_construction_state(state):
    scene_state = get_current_scene_state(state)
    state["placed_objects"] = scene_state["placed_objects"]

    if "construction" not in state:
        state["construction"] = {}

    state["construction"]["placed_objects"] = scene_state["placed_objects"]


def is_cell_occupied(state, grid_x, grid_y, world_objects=None):
    ensure_construction_state(state)

    if is_map_cell_blocked(grid_x, grid_y):
        return True
    if is_world_object_cell_blocked(state, grid_x, grid_y, world_objects):
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


def remove_placed_object(state, grid_x, grid_y):
    """Pick up a placed object, including a footprint cell under the player."""
    from game.inventory.item_transactions import can_receive, receive
    placed = get_current_scene_state(state)["placed_objects"]
    for obj in reversed(placed):
        if (obj["grid_x"] <= grid_x < obj["grid_x"] + obj["width"] and
                obj["grid_y"] <= grid_y < obj["grid_y"] + obj["height"]):
            item_id = obj["item_id"]
            if not can_receive(state, item_id, 1):
                return "inventory_full"
            if not receive(state, item_id, 1):
                return "inventory_full"
            placed.remove(obj)
            return "removed"
    return "not_found"
