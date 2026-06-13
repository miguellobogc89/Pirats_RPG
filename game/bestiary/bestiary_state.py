def create_default_bestiary_state():
    return {
        "known_creatures": [
            "rock_turtle",
            "fire_worm",
        ],
        "owned_creatures": [
            {
                "creature_id": "rock_turtle",
                "level": 1,
                "xp": 0,
                "nickname": "Roca",
                "equipped_abilities": [
                    "stone_guard",
                    "shell_bash",
                ],
            },
            {
                "creature_id": "fire_worm",
                "level": 1,
                "xp": 0,
                "nickname": "Brasa",
                "equipped_abilities": [
                    "ember_bite",
                    "burning_spit",
                ],
            },
        ],
        "active_party": [
            0,
            1,
        ],
    }


def ensure_bestiary_state(state):
    if "bestiary" not in state:
        state["bestiary"] = create_default_bestiary_state()

    if "known_creatures" not in state["bestiary"]:
        state["bestiary"]["known_creatures"] = []

    if "owned_creatures" not in state["bestiary"]:
        state["bestiary"]["owned_creatures"] = []

    if "active_party" not in state["bestiary"]:
        state["bestiary"]["active_party"] = []