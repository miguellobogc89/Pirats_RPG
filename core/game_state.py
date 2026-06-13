from game.skills.skill_database import SKILL_DATABASE
from game.skills.skill_state import create_default_skills_state
from game.bestiary.bestiary_state import create_default_bestiary_state
from game.cartography.cartography_manager import CartographyManager
from game.inventory.inventory_state import ensure_inventory_state


DEFAULT_CONFIG = {
    "initial_day": 1,
    "initial_season_index": 0,
    "max_energy": 10,
    "initial_wind": "calm",
}


def create_default_inventory_state():
    state = {}
    ensure_inventory_state(state)
    return state["inventory"]


def get_config_value(game_data, key):
    config = game_data.get("config", {}) if game_data else {}
    return config.get(key, DEFAULT_CONFIG[key])


def create_default_energy_state(game_data):
    max_energy = get_config_value(game_data, "max_energy")

    return {
        "current": max_energy,
        "max": max_energy,
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

    return {
        "resources": {
            "gold": 100,
        },
        "inventory": create_default_inventory_state(),
        "player": {
            "x": 400,
            "y": 300,
        },
        "time": {
            "day": initial_day,
            "hour": 6,
            "minute": 0,
        },
        "day": initial_day,
        "season_index": get_config_value(game_data, "initial_season_index"),
        "energy": create_default_energy_state(game_data),
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
        "skills": create_default_skills_state(SKILL_DATABASE),
        "cartography": CartographyManager().get_save_data(),
        "bestiary": create_default_bestiary_state(),
    }


def normalize_state(state, game_data=None):
    if "resources" not in state:
        state["resources"] = {}

    if not isinstance(state.get("inventory"), dict):
        state["legacy_inventory"] = state.get("inventory", [])
        state["inventory"] = create_default_inventory_state()
    else:
        ensure_inventory_state(state)

    if "hotbar" in state:
        state["legacy_hotbar"] = state["hotbar"]
        del state["hotbar"]

    if "player" not in state:
        state["player"] = {
            "x": 400,
            "y": 300,
        }

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

    if not isinstance(state.get("energy"), dict):
        state["energy"] = create_default_energy_state(game_data)

    if "current" not in state["energy"]:
        state["energy"]["current"] = state["energy"].get("max", get_config_value(game_data, "max_energy"))

    if "max" not in state["energy"]:
        state["energy"]["max"] = get_config_value(game_data, "max_energy")

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

    if "skills" not in state:
        state["skills"] = create_default_skills_state(SKILL_DATABASE)

    if "cartography" not in state:
        state["cartography"] = CartographyManager().get_save_data()

    if "bestiary" not in state:
        state["bestiary"] = create_default_bestiary_state()

    default_skills = create_default_skills_state(SKILL_DATABASE)

    for skill_id in default_skills:
        if skill_id not in state["skills"]:
            state["skills"][skill_id] = default_skills[skill_id]

        if "level" not in state["skills"][skill_id]:
            state["skills"][skill_id]["level"] = 1

        if "xp" not in state["skills"][skill_id]:
            state["skills"][skill_id]["xp"] = 0

    return state
