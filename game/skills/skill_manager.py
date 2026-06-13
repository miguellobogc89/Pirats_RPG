from game.skills.skill_database import SKILL_DATABASE
from game.skills.skill_state import create_default_skills_state


SKILL_ACTIONS = {
    "item_crafted": {
        "skill_id": "crafting",
        "xp": 10,
    },
    "crop_harvested": {
        "skill_id": "farming",
        "xp": 15,
    },
    "object_placed": {
        "skill_id": "construction",
        "xp": 10,
    },
    "collectable_picked": {
        "skill_id": "gathering",
        "xp": 5,
    },
    "rock_destroyed": {
        "skill_id": "mining",
        "xp": 20,
    },
    "tree_destroyed": {
        "skill_id": "gathering",
        "xp": 15,
    },
    "combat_won": {
        "skill_id": "combat",
        "xp": 20,
    },
    }


class SkillManager:
    def __init__(self, state):
        self.state = state

        if "skills" not in self.state:
            self.state["skills"] = create_default_skills_state(SKILL_DATABASE)

    def register_action(self, action_id, context=None):
        if action_id not in SKILL_ACTIONS:
            return None

        action_data = SKILL_ACTIONS[action_id]

        return self.add_xp(
            action_data["skill_id"],
            action_data["xp"],
        )

    def get_xp_required_for_next_level(self, level):
        return 100 + ((level - 1) * 50)

    def add_xp(self, skill_id, amount):
        if skill_id not in SKILL_DATABASE:
            return None

        if skill_id not in self.state["skills"]:
            self.state["skills"][skill_id] = {
                "level": 1,
                "xp": 0,
                "total_xp": 0,
            }

        skill_state = self.state["skills"][skill_id]
        skill_data = SKILL_DATABASE[skill_id]

        if "total_xp" not in skill_state:
            skill_state["total_xp"] = skill_state.get("xp", 0)

        if skill_state["level"] >= skill_data["max_level"]:
            return {
                "skill_id": skill_id,
                "level": skill_state["level"],
                "xp": skill_state["xp"],
                "total_xp": skill_state["total_xp"],
                "leveled_up": False,
                "max_level_reached": True,
            }

        skill_state["xp"] += amount
        skill_state["total_xp"] += amount

        leveled_up = False

        while skill_state["level"] < skill_data["max_level"]:
            xp_required = self.get_xp_required_for_next_level(skill_state["level"])

            if skill_state["xp"] < xp_required:
                break

            skill_state["xp"] -= xp_required
            skill_state["level"] += 1
            leveled_up = True

        if skill_state["level"] >= skill_data["max_level"]:
            skill_state["xp"] = 0

        return {
            "skill_id": skill_id,
            "level": skill_state["level"],
            "xp": skill_state["xp"],
            "total_xp": skill_state["total_xp"],
            "leveled_up": leveled_up,
            "max_level_reached": skill_state["level"] >= skill_data["max_level"],
        }

    def get_skill_state(self, skill_id):
        if skill_id not in self.state["skills"]:
            return None

        return self.state["skills"][skill_id]

    def get_all_skills(self):
        return self.state["skills"]