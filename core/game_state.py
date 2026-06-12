from copy import deepcopy


def create_initial_state(game_data):
    config = game_data["config"]
    resources = {}

    for key, resource in game_data["resources"].items():
        resources[key] = resource.get("initial", 0)

    upgrades = {}
    for key in game_data["upgrades"].keys():
        upgrades[key] = False

    return {
        "day": config["initial_day"],
        "season_index": config["initial_season_index"],
        "health": {"current": config["max_health"], "max": config["max_health"]},
        "energy": {"current": config["max_energy"], "max": config["max_energy"]},
        "resources": resources,
        "upgrades": upgrades,
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


def clone_state(state):
    return deepcopy(state)
