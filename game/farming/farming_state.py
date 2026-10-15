"""Canonical farming scene state and legacy compatibility view."""
from game.scenes.scene_state import get_current_scene_state


def normalize_scene_crops(crops):
    for crop in crops:
        crop.setdefault("stage", 0)
        crop.setdefault("days_in_stage", 0)
        crop.setdefault("dry_days", 0)
        crop.setdefault("times_watered", 0)
        crop.setdefault("dead", False)
        crop.setdefault("dead_days", 0)


def ensure_farming_state(state):
    scene_state = get_current_scene_state(state)
    normalize_scene_crops(scene_state["crops"])
    state["farming"] = {key: scene_state[key] for key in (
        "tilled_idle_days", "wild_bushes", "tilled_cells", "watered_cells", "crops"
    )}
    return scene_state
