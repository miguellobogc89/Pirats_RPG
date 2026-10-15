"""Daily farming coordinator and backward-compatible public API."""
import random
from game.data.crop_database import get_crop_data
from game.farming.farming_config import FARMING_RULES
from game.scenes.scene_state import ensure_scene_state_entry
from game.farming.farming_state import ensure_farming_state, normalize_scene_crops
from game.farming.crop_manager import (
    get_crop_at_cell, plant_crop, advance_crop_growth, is_crop_ready, harvest_crop,
)
from game.farming.soil_manager import (
    till_cell, water_cell, is_tilled, is_watered, advance_soil_day,
)
from game.farming.wild_growth_manager import spawn_wild_bush


def advance_farming_day(state, scene_id=None):
    if scene_id is None:
        farming = ensure_farming_state(state)
    else:
        farming = ensure_scene_state_entry(state, scene_id)
        normalize_scene_crops(farming["crops"])

    dead_crops = []

    for crop in farming["crops"][:]:
        if crop.get("dead", False):
            # Dead crops remain until cleared with the scythe.
            continue

        crop_data = get_crop_data(crop["crop_id"])

        if crop_data is None:
            continue

        watered = [crop["grid_x"], crop["grid_y"]] in farming["watered_cells"]

        if watered:
            crop["dry_days"] = 0
            crop["times_watered"] += 1
            advance_crop_growth(crop, crop_data)
        else:
            crop["dry_days"] += 1

            if crop["dry_days"] >= crop_data.get("max_dry_days", FARMING_RULES["default_max_dry_days"]):
                crop["dead"] = True
                crop["dead_days"] = 0
                dead_crops.append(crop)

    advance_soil_day(farming)

    if random.random() < FARMING_RULES["wild_growth_chance_by_scene"].get(scene_id, 0.0):
        spawn_wild_bush(state, farming)

    farming["watered_cells"].clear()

    return dead_crops


