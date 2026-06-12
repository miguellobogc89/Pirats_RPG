from copy import deepcopy
from game.inventory.inventory_state import ensure_inventory_state
from game.farming.farming_manager import ensure_farming_state
from game.collectable_manager import ensure_collectables_state
from game.time_manager import ensure_time_state


def create_initial_state(game_data):
    config = game_data["config"]
    resources = {}

    for key, resource in game_data["resources"].items():
        resources[key] = resource.get("initial", 0)

    upgrades = {}
    for key in game_data["upgrades"].keys():
        upgrades[key] = False

    state = {
        "day": config["initial_day"],
        "season_index": config["initial_season_index"],
        "health": {"current": config["max_health"], "max": config["max_health"]},
        "energy": {"current": config["max_energy"], "max": config["max_energy"]},
        "resources": resources,
        "upgrades": upgrades,
        "destroyed_world_objects": [],
        "wind": config["initial_wind"],
        "ship": {
            "status": "available",
            "days_left": 0,
            "route": None,
            "success_rate": 0,
            "pending_event": None,
            "secured_reward": {},
        },
        "player": {
            "zone": "dock",
            "x": game_data["zones"]["dock"]["x"],
            "y": game_data["zones"]["dock"]["y"],
        },
        "log": ["Nueva partida iniciada."],
    }

    ensure_inventory_state(state)
    ensure_farming_state(state)
    ensure_collectables_state(state)
    ensure_time_state(state)

    return state

def clone_state(state):
    return deepcopy(state)

def normalize_state(state):
    ensure_inventory_state(state)
    ensure_farming_state(state)
    ensure_collectables_state(state)
    ensure_time_state(state)
    if "destroyed_world_objects" not in state:
        state["destroyed_world_objects"] = []

    return state