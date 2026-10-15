"""Crop lifecycle operations."""
from game.data.crop_database import get_crop_data
from game.world.grid_manager import world_to_grid
from game.farming.farming_state import ensure_farming_state

def get_crop_at_cell(state, grid_x, grid_y):
    ensure_farming_state(state)

    for crop in state["farming"]["crops"]:
        if crop["grid_x"] == grid_x and crop["grid_y"] == grid_y:
            return crop

    return None

def plant_crop(state, world_x, world_y, crop_id):
    ensure_farming_state(state)

    grid_x, grid_y = world_to_grid(world_x, world_y)

    if [grid_x, grid_y] in state["farming"]["wild_bushes"]:
        return "occupied"

    if [grid_x, grid_y] not in state["farming"]["tilled_cells"]:
        return "not_tilled"

    existing_crop = get_crop_at_cell(state, grid_x, grid_y)

    if existing_crop is not None:
        return "occupied"

    crop = {
        "crop_id": crop_id,
        "grid_x": grid_x,
        "grid_y": grid_y,
        "stage": 0,
        "days_in_stage": 0,
        "dry_days": 0,
        "times_watered": 0,
        "dead": False,
        "dead_days": 0,
    }

    state["farming"]["tilled_idle_days"].pop(f"{grid_x},{grid_y}", None)
    state["farming"]["crops"].append(crop)
    return "planted"

def advance_crop_growth(crop, crop_data):
    days_per_stage = crop_data.get("days_per_stage", [])

    if crop["stage"] >= len(days_per_stage):
        return

    crop["days_in_stage"] += 1

    required_days = days_per_stage[crop["stage"]]

    if crop["days_in_stage"] < required_days:
        return

    crop["days_in_stage"] = 0
    crop["stage"] += 1

def is_crop_ready(crop):
    crop_data = get_crop_data(crop["crop_id"])

    if crop_data is None:
        return False

    days_per_stage = crop_data.get("days_per_stage", [])

    return not crop.get("dead", False) and crop["stage"] >= len(days_per_stage)

def harvest_crop(state, world_x, world_y):
    ensure_farming_state(state)

    grid_x, grid_y = world_to_grid(world_x, world_y)
    crop = get_crop_at_cell(state, grid_x, grid_y)

    if crop is None:
        return {
            "status": "no_crop",
        }

    if crop.get("dead", False):
        state["farming"]["crops"].remove(crop)

        return {
            "status": "removed_dead",
        }

    if not is_crop_ready(crop):
        return {
            "status": "not_ready",
        }

    crop_data = get_crop_data(crop["crop_id"])

    state["farming"]["crops"].remove(crop)

    return {
        "status": "harvested",
        "item_id": crop_data["harvest_item"],
        "amount": crop_data.get("harvest_amount", 1),
    }

