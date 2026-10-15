import random

from game.data.crop_database import get_crop_data
from game.scenes.scene_state import get_current_scene_state
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

    scene_state = get_current_scene_state(state)
    normalize_scene_crops(scene_state["crops"])
    state["farming"] = {
        "tilled_idle_days": scene_state["tilled_idle_days"],
        "wild_bushes": scene_state["wild_bushes"],
        "tilled_cells": scene_state["tilled_cells"],
        "watered_cells": scene_state["watered_cells"],
        "crops": scene_state["crops"],
    }


def normalize_scene_crops(crops):
    for crop in crops:
        crop.setdefault("stage", 0)
        crop.setdefault("days_in_stage", 0)
        crop.setdefault("dry_days", 0)
        crop.setdefault("times_watered", 0)
        crop.setdefault("dead", False)


def till_cell(state, world_x, world_y):
    ensure_farming_state(state)

    cell = list(world_to_grid(world_x, world_y))

    if cell in state["farming"]["tilled_cells"]:
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

    state["farming"]["tilled_idle_days"].pop(f"{grid_x},{grid_y}", None)
    state["farming"]["crops"].append(crop)
    return "planted"


def advance_farming_day(state, scene_id=None):
    if scene_id is None:
        ensure_farming_state(state)
        farming = state["farming"]
    else:
        from game.scenes.scene_state import ensure_scene_state_entry
        farming = ensure_scene_state_entry(state, scene_id)
        normalize_scene_crops(farming["crops"])

    dead_crops = []

    for crop in farming["crops"]:
        if crop.get("dead", False):
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

            if crop["dry_days"] >= crop_data.get("max_dry_days", 2):
                crop["dead"] = True
                dead_crops.append(crop)

    occupied = {(crop["grid_x"], crop["grid_y"]) for crop in farming["crops"]}
    idle = farming.setdefault("tilled_idle_days", {})
    for cell in farming["tilled_cells"][:]:
        key = f"{cell[0]},{cell[1]}"
        if tuple(cell) in occupied:
            idle.pop(key, None)
            continue
        idle[key] = idle.get(key, 0) + 1
        if idle[key] >= 7:
            farming["tilled_cells"].remove(cell)
            idle.pop(key, None)

    if scene_id == "brumazul_granja" and random.random() < 0.1:
        spawn_wild_bush(state, farming)

    farming["watered_cells"].clear()

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

def spawn_wild_bush(state, farming):
    """One bush on an unoccupied, walkable tile of the chapter farm."""
    import json
    from pathlib import Path
    from game.world.grid_manager import TILE_SIZE
    from game.scenes.chapter_area_navigation import can_walk_chapter_area
    path = Path(__file__).resolve().parents[2] / "data" / "scenes" / "brumazul_granja.json"
    layout = json.loads(path.read_text(encoding="utf-8"))["chapter_layout"]
    occupied = {tuple(c) for c in farming["tilled_cells"]}
    occupied.update((c["grid_x"], c["grid_y"]) for c in farming["crops"])
    occupied.update(tuple(c) for c in farming.setdefault("wild_bushes", []))
    for obj in farming.get("placed_objects", []):
        for gx in range(obj["grid_x"], obj["grid_x"] + obj.get("width", 1)):
            for gy in range(obj["grid_y"], obj["grid_y"] + obj.get("height", 1)):
                occupied.add((gx, gy))
    player = state.get("player", {})
    if state.get("current_scene") == "brumazul_granja" and "x" in player:
        occupied.add((int(player["x"] // TILE_SIZE), int(player["y"] // TILE_SIZE)))
    candidates = []
    for gy in range(2, int(layout["height"] // TILE_SIZE) - 1):
        for gx in range(2, int(layout["width"] // TILE_SIZE) - 1):
            if (gx, gy) in occupied:
                continue
            x, y = (gx + .5) * TILE_SIZE, (gy + .5) * TILE_SIZE
            if not can_walk_chapter_area("brumazul_granja", x, y, layout):
                continue
            if any((x - wx)**2 + (y - wy)**2 < 48**2 for wx, wy in layout.get("wood_piles", [])):
                continue
            if any((x - px)**2 + (y - py)**2 < 48**2 for px, py in
                   (layout.get("spawn", [0, 0]), layout.get("gate", {}).get("position", [0, 0]))):
                continue
            candidates.append([gx, gy])
    if candidates:
        farming["wild_bushes"].append(random.choice(candidates))
