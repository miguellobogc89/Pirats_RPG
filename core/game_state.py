from game.skills.skill_database import SKILL_DATABASE
from game.skills.skill_state import create_default_skills_state
from game.bestiary.bestiary_state import create_default_bestiary_state
from game.cartography.cartography_manager import CartographyManager


def create_initial_state(game_data):
    return {
        "resources": {},
        "inventory": [],
        "hotbar": [],
        "player": {
            "x": 400,
            "y": 300,
        },
        "time": {
            "day": 1,
            "hour": 6,
            "minute": 0,
        },
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


def normalize_state(state):
    if "resources" not in state:
        state["resources"] = {}

    if "inventory" not in state:
        state["inventory"] = []

    if "hotbar" not in state:
        state["hotbar"] = []

    if "player" not in state:
        state["player"] = {
            "x": 400,
            "y": 300,
        }

    if "time" not in state:
        state["time"] = {
            "day": 1,
            "hour": 6,
            "minute": 0,
        }

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