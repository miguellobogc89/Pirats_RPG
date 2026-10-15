"""Soil preparation, watering, and idle-soil decay."""
from game.world.grid_manager import world_to_grid
from game.farming.farming_config import FARMING_RULES
from game.scenes.scene_state import get_current_scene_state
from game.farming.farming_state import ensure_farming_state
from game.farming.crop_manager import get_crop_at_cell
from game.world.occupancy import blocks_farming

def till_cell(state, world_x, world_y):
    ensure_farming_state(state)

    cell = list(world_to_grid(world_x, world_y))

    farming = state["farming"]
    if cell in farming["tilled_cells"] or blocks_farming(state, cell[0], cell[1]):
        return False
    if get_crop_at_cell(state, cell[0], cell[1]) is not None:
        return False
    scene_state = get_current_scene_state(state)
    for obj in scene_state.get("placed_objects", []):
        if (obj["grid_x"] <= cell[0] < obj["grid_x"] + obj.get("width", 1)
                and obj["grid_y"] <= cell[1] < obj["grid_y"] + obj.get("height", 1)):
            return False

    state["farming"]["tilled_cells"].append(cell)
    state["farming"]["tilled_idle_days"].pop(f"{cell[0]},{cell[1]}", None)
    return True

def water_cell(state, world_x, world_y):
    ensure_farming_state(state)

    cell = list(world_to_grid(world_x, world_y))

    if cell not in state["farming"]["tilled_cells"]:
        return "not_tilled"

    if cell in state["farming"]["watered_cells"]:
        return "already_watered"

    state["farming"]["watered_cells"].append(cell)
    return "watered"

def is_tilled(state, grid_x, grid_y):
    ensure_farming_state(state)
    return [grid_x, grid_y] in state["farming"]["tilled_cells"]

def is_watered(state, grid_x, grid_y):
    ensure_farming_state(state)
    return [grid_x, grid_y] in state["farming"]["watered_cells"]

def advance_soil_day(farming):
    occupied = {(crop["grid_x"], crop["grid_y"]) for crop in farming["crops"]}
    idle = farming.setdefault("tilled_idle_days", {})
    for cell in farming["tilled_cells"][:]:
        key = f"{cell[0]},{cell[1]}"
        if tuple(cell) in occupied:
            idle.pop(key, None)
            continue
        idle[key] = idle.get(key, 0) + 1
        if idle[key] >= FARMING_RULES["tilled_soil_reset_days"]:
            farming["tilled_cells"].remove(cell)
            idle.pop(key, None)
