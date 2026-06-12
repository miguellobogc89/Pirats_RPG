from game.data.crop_database import get_crop_data
from game.world.grid_manager import world_to_grid


def ensure_farming_state(state):
    if "farming" not in state:
        state["farming"] = {}

    if "tilled_cells" not in state["farming"]:
        state["farming"]["tilled_cells"] = []

    if "watered_cells" not in state["farming"]:
        state["farming"]["watered_cells"] = []

    if "crops" not in state["farming"]:
        state["farming"]["crops"] = []


def till_cell(state, world_x, world_y):
    ensure_farming_state(state)

    cell = world_to_grid(world_x, world_y)

    if cell in state["farming"]["tilled_cells"]:
        return False

    state["farming"]["tilled_cells"].append(cell)
    return True


def water_cell(state, world_x, world_y):
    ensure_farming_state(state)

    cell = world_to_grid(world_x, world_y)

    if cell not in state["farming"]["tilled_cells"]:
        return "not_tilled"

    if cell in state["farming"]["watered_cells"]:
        return "already_watered"

    state["farming"]["watered_cells"].append(cell)
    return "watered"


def is_tilled(state, grid_x, grid_y):
    ensure_farming_state(state)
    return (grid_x, grid_y) in state["farming"]["tilled_cells"]


def is_watered(state, grid_x, grid_y):
    ensure_farming_state(state)
    return (grid_x, grid_y) in state["farming"]["watered_cells"]


def get_crop_at_cell(state, grid_x, grid_y):
    ensure_farming_state(state)

    for crop in state["farming"]["crops"]:
        if crop["grid_x"] == grid_x and crop["grid_y"] == grid_y:
            return crop

    return None


def plant_crop(state, world_x, world_y, crop_id):
    ensure_farming_state(state)

    grid_x, grid_y = world_to_grid(world_x, world_y)

    if not is_tilled(state, grid_x, grid_y):
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
    }

    state["farming"]["crops"].append(crop)
    return "planted"


def advance_farming_day(state):
    ensure_farming_state(state)

    dead_crops = []

    for crop in state["farming"]["crops"]:
        if crop.get("dead", False):
            continue

        crop_data = get_crop_data(crop["crop_id"])

        if crop_data is None:
            continue

        watered = is_watered(state, crop["grid_x"], crop["grid_y"])

        if watered:
            crop["dry_days"] = 0
            crop["times_watered"] += 1
            advance_crop_growth(crop, crop_data)
        else:
            crop["dry_days"] += 1

            if crop["dry_days"] >= crop_data.get("max_dry_days", 2):
                crop["dead"] = True
                dead_crops.append(crop)

    state["farming"]["watered_cells"] = []

    return dead_crops


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

    return crop["stage"] >= len(days_per_stage)


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