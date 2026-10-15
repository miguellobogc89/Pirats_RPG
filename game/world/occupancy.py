"""Shared occupancy rules for world objects, ground items, and vegetation."""
from game.scenes.scene_state import get_current_scene_state
from game.world.grid_manager import TILE_SIZE, world_to_grid

BUSH_SPEED_MULTIPLIER = 0.60
BLOCKING_TYPES = frozenset(("tree", "rock", "ground_item", "item"))


def _covers(obj, gx, gy):
    if "grid_x" in obj and "grid_y" in obj:
        x, y = obj["grid_x"], obj["grid_y"]
    elif "x" in obj and "y" in obj:
        x, y = world_to_grid(obj["x"], obj["y"])
    else:
        return False
    width, height = obj.get("footprint", [obj.get("width", 1), obj.get("height", 1)])
    return x <= gx < x + width and y <= gy < y + height


def cell_occupants(state, gx, gy, world_objects=None):
    scene = get_current_scene_state(state)
    occupants = []
    if [gx, gy] in scene["wild_bushes"]:
        occupants.append({"type": "bush", "blocks_movement": False,
                          "blocks_farming": True, "speed_multiplier": BUSH_SPEED_MULTIPLIER})
    for obj in scene.get("placed_objects", []):
        if _covers(obj, gx, gy):
            occupants.append({"type": "placed", "blocks_movement": True, "blocks_farming": True})
    for obj in (world_objects if world_objects is not None else state.get("world_objects", [])):
        if _covers(obj, gx, gy):
            occupants.append(obj)
    for item in state.get("collectables", []):
        if item.get("scene_id", state.get("current_scene")) == state.get("current_scene") and _covers(item, gx, gy):
            occupants.append({"type": "ground_item", "blocks_movement": True,
                              "blocks_farming": True})
    return occupants


def blocks_movement(state, gx, gy, world_objects=None):
    return any(obj.get("blocks_movement", obj.get("type") in BLOCKING_TYPES)
               for obj in cell_occupants(state, gx, gy, world_objects))


def blocks_farming(state, gx, gy):
    return any(obj.get("blocks_farming", obj.get("type") in BLOCKING_TYPES or obj.get("type") == "bush")
               for obj in cell_occupants(state, gx, gy))


def movement_multiplier(state, x, y):
    gx, gy = world_to_grid(x, y)
    result = 1.0
    for obj in cell_occupants(state, gx, gy):
        result = min(result, obj.get("speed_multiplier", BUSH_SPEED_MULTIPLIER if obj.get("type") == "bush" else 1.0))
    return result
