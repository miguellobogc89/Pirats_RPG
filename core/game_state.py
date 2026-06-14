from game.skills.skill_database import SKILL_DATABASE
from game.skills.skill_state import create_default_skills_state
from game.bestiary.bestiary_state import create_default_bestiary_state
from game.cartography.cartography_manager import CartographyManager
from game.inventory.inventory_state import ensure_inventory_state
from game.inventory.stash_state import create_default_stash_state, ensure_stash_state
from game.scenes.scene_loader import load_scene_data
from game.scenes.scene_state import create_default_scene_state, ensure_scene_states
from game.story.story_state import create_default_story_state, ensure_story_state
from game.story_events.story_event_state import (
    create_default_story_event_state,
    ensure_story_event_state,
)


DEFAULT_CONFIG = {
    "initial_day": 1,
    "initial_season_index": 0,
    "max_energy": 10,
    "max_health": 10,
    "max_magic": 0,
    "initial_wind": "calm",
}


def create_default_inventory_state():
    state = {}
    ensure_inventory_state(state)
    return state["inventory"]


def create_default_player_stash_state():
    return create_default_stash_state()


def get_config_value(game_data, key):
    config = game_data.get("config", {}) if game_data else {}
    return config.get(key, DEFAULT_CONFIG[key])


def create_default_energy_state(game_data):
    max_energy = get_config_value(game_data, "max_energy")

    return {
        "current": max_energy,
        "max": max_energy,
    }


def create_default_health_state(game_data):
    max_health = get_config_value(game_data, "max_health")

    return {
        "current": max_health,
        "max": max_health,
    }


def create_default_magic_state(game_data):
    max_magic = get_config_value(game_data, "max_magic")

    return {
        "current": max_magic,
        "max": max_magic,
    }


def create_default_ship_state():
    return {
        "status": "available",
        "days_left": 0,
        "route": None,
        "success_rate": 0,
        "pending_event": None,
        "secured_reward": {},
    }


def create_default_upgrades_state(game_data):
    upgrades = game_data.get("upgrades", {}) if game_data else {}
    return {
        upgrade_id: False
        for upgrade_id in upgrades
    }


def create_initial_state(game_data):
    initial_day = get_config_value(game_data, "initial_day")
    initial_scene_id = "farm"
    initial_scene = load_scene_data(initial_scene_id)
    player_spawn = {"x": 400, "y": 300}

    if initial_scene is not None:
        player_spawn = initial_scene["player_spawn"]

    return {
        "resources": {
            "gold": 100,
        },
        "inventory": create_default_inventory_state(),
        "stash": create_default_player_stash_state(),
        "player": {
            "x": player_spawn["x"],
            "y": player_spawn["y"],
            "name": "",
            "gender": "neutral",
        },
        "time": {
            "day": initial_day,
            "hour": 6,
            "minute": 0,
        },
        "day": initial_day,
        "season_index": get_config_value(game_data, "initial_season_index"),
        "health": create_default_health_state(game_data),
        "energy": create_default_energy_state(game_data),
        "magic": create_default_magic_state(game_data),
        "wind": get_config_value(game_data, "initial_wind"),
        "ship": create_default_ship_state(),
        "upgrades": create_default_upgrades_state(game_data),
        "farming": {
            "tilled_cells": [],
            "watered_cells": [],
            "crops": [],
        },
        "construction": {
            "placed_objects": [],
        },
        "destroyed_objects": [],
        "collectables": [],
        "log": [],
        "scene_states": {
            initial_scene_id: create_default_scene_state(),
        },
        "skills": create_default_skills_state(SKILL_DATABASE),
        "cartography": CartographyManager().get_save_data(),
        "bestiary": create_default_bestiary_state(),
        "story": create_default_story_state(),
        "story_events": create_default_story_event_state(),
        "current_scene": initial_scene_id,
    }


def create_new_game_state(player_name, player_gender, game_data):
    state = create_initial_state(game_data)
    state["player"]["name"] = player_name
    state["player"]["gender"] = player_gender
    return state


def normalize_state(state, game_data=None):
    if "resources" not in state:
        state["resources"] = {}

    if not isinstance(state.get("inventory"), dict):
        state["legacy_inventory"] = state.get("inventory", [])
        state["inventory"] = create_default_inventory_state()
    else:
        ensure_inventory_state(state)

    ensure_stash_state(state)

    if "hotbar" in state:
        state["legacy_hotbar"] = state["hotbar"]
        del state["hotbar"]

    if "player" not in state:
        state["player"] = {
            "x": 400,
            "y": 300,
        }

    if "name" not in state["player"]:
        state["player"]["name"] = ""

    if "gender" not in state["player"]:
        state["player"]["gender"] = "neutral"

    if not isinstance(state.get("time"), dict):
        state["time"] = {
            "day": get_config_value(game_data, "initial_day"),
            "hour": 6,
            "minute": 0,
        }

    if "day" not in state:
        state["day"] = state["time"].get("day", get_config_value(game_data, "initial_day"))

    state["time"]["day"] = state["day"]

    if "season_index" not in state:
        state["season_index"] = get_config_value(game_data, "initial_season_index")

    if not isinstance(state.get("health"), dict):
        state["health"] = create_default_health_state(game_data)

    if "current" not in state["health"]:
        state["health"]["current"] = state["health"].get("max", get_config_value(game_data, "max_health"))

    if "max" not in state["health"]:
        state["health"]["max"] = get_config_value(game_data, "max_health")

    if not isinstance(state.get("energy"), dict):
        state["energy"] = create_default_energy_state(game_data)

    if "current" not in state["energy"]:
        state["energy"]["current"] = state["energy"].get("max", get_config_value(game_data, "max_energy"))

    if "max" not in state["energy"]:
        state["energy"]["max"] = get_config_value(game_data, "max_energy")

    if not isinstance(state.get("magic"), dict):
        state["magic"] = create_default_magic_state(game_data)

    if "current" not in state["magic"]:
        state["magic"]["current"] = state["magic"].get("max", get_config_value(game_data, "max_magic"))

    if "max" not in state["magic"]:
        state["magic"]["max"] = get_config_value(game_data, "max_magic")

    if "wind" not in state:
        state["wind"] = get_config_value(game_data, "initial_wind")

    if not isinstance(state.get("ship"), dict):
        state["ship"] = create_default_ship_state()

    default_ship = create_default_ship_state()

    for ship_key, ship_value in default_ship.items():
        if ship_key not in state["ship"]:
            state["ship"][ship_key] = ship_value

    if not isinstance(state.get("upgrades"), dict):
        state["upgrades"] = create_default_upgrades_state(game_data)

    default_upgrades = create_default_upgrades_state(game_data)

    for upgrade_id, default_value in default_upgrades.items():
        if upgrade_id not in state["upgrades"]:
            state["upgrades"][upgrade_id] = default_value

    if "farming" not in state:
        state["farming"] = {
            "tilled_cells": [],
            "watered_cells": [],
            "crops": [],
        }

    if "tilled_cells" not in state["farming"]:
        state["farming"]["tilled_cells"] = []

    if "watered_cells" not in state["farming"]:
        state["farming"]["watered_cells"] = []

    if "crops" not in state["farming"]:
        state["farming"]["crops"] = []

    if "construction" not in state:
        state["construction"] = {
            "placed_objects": [],
        }

    if "placed_objects" not in state["construction"]:
        state["construction"]["placed_objects"] = []

    if "destroyed_objects" not in state:
        state["destroyed_objects"] = []

    if "collectables" not in state:
        state["collectables"] = []

    if "log" not in state:
        state["log"] = []

    if "current_scene" not in state:
        state["current_scene"] = "farm"

    ensure_scene_states(state)

    if "skills" not in state:
        state["skills"] = create_default_skills_state(SKILL_DATABASE)

    if "cartography" not in state:
        state["cartography"] = CartographyManager().get_save_data()

    if "bestiary" not in state:
        state["bestiary"] = create_default_bestiary_state()

    ensure_story_state(state)
    ensure_story_event_state(state)

    default_skills = create_default_skills_state(SKILL_DATABASE)

    for skill_id in default_skills:
        if skill_id not in state["skills"]:
            state["skills"][skill_id] = default_skills[skill_id]

        if "level" not in state["skills"][skill_id]:
            state["skills"][skill_id]["level"] = 1

        if "xp" not in state["skills"][skill_id]:
            state["skills"][skill_id]["xp"] = 0

    return state
