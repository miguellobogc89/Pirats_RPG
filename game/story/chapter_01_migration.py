"""Non-destructive chapter-one save migration into the modular game state.

The old save remains untouched. Scene conversion is deliberately separate:
simulator scene IDs are not valid modular scene IDs yet.
"""
import json
from pathlib import Path

from core.game_state import create_initial_state, normalize_state

CHAPTER_FIELDS = (
    "mission", "mission_stage", "intro_finished", "prologue_finished",
    "wood", "wood_count", "repaired_fences", "elder_met",
    "elder_after_fence", "gate_inspected", "gate_repaired",
    "smith_quest", "rat_quest", "metal_bolt", "sylvarin_boots",
    "rat_reward_claimed", "fathers_sword", "elder_clue", "port_meeting",
    "farm_state", "farm_kills", "farm_boss_hp", "house_key",
    "tools_collected", "time_of_day",
)


def migrate_chapter_save(source, game_data):
    """Convert progress without granting the original prototype's starter items."""
    if not isinstance(source, dict):
        raise ValueError("Chapter save must be a JSON object")
    state = create_initial_state(game_data)
    state["chapter_01"] = {key: source[key] for key in CHAPTER_FIELDS if key in source}
    state["chapter_01"]["legacy_scene"] = source.get("scene", "playa")
    state["chapter_01"]["scene_migration_pending"] = True
    if isinstance(source.get("skills"), dict):
        state["skills"].update(source["skills"])
    for key in ("ship", "upgrades", "resources", "farming"):
        if isinstance(source.get(key), dict):
            state[key].update(source[key])
    if isinstance(source.get("game_clock"), dict):
        clock = source["game_clock"]
        state["time"]["hour"] = int(clock.get("hour", state["time"]["hour"]))
        state["time"]["minute"] = int(clock.get("minute", state["time"]["minute"]))
    # The simulator stores quest items as flags, not as inventory stacks.
    # Item conversion must be performed by the inventory migration phase.
    state["chapter_01"]["inventory_migration_pending"] = True
    return normalize_state(state, game_data)


def migrate_save_file(source_path, destination_path, game_data):
    """Write to a new destination; refuse to overwrite any existing save."""
    source_path = Path(source_path).resolve()
    destination_path = Path(destination_path).resolve()
    if source_path == destination_path:
        raise ValueError("Refusing to overwrite the simulator save")
    with source_path.open(encoding="utf-8") as file:
        source = json.load(file)
    converted = migrate_chapter_save(source, game_data)
    with destination_path.open("x", encoding="utf-8") as file:
        json.dump(converted, file, ensure_ascii=False, indent=2)
    return destination_path
