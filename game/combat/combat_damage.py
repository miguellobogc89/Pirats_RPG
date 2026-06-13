import random

from game.combat.combat_status import (
    get_modified_defense,
    get_modified_crit_chance,
    get_modified_miss_chance,
)


def calculate_damage(actor, target, ability):
    miss_chance = get_modified_miss_chance(actor)
    miss_roll = random.randint(1, 100)

    if miss_roll <= miss_chance:
        return {
            "damage": 0,
            "missed": True,
            "critical": False,
        }

    defense = get_modified_defense(target)
    raw_damage = actor["attack"] + ability["power"] - defense

    if target.get("guarding", False):
        raw_damage -= 5

    if raw_damage < 1:
        raw_damage = 1

    crit_chance = get_modified_crit_chance(actor)
    crit_roll = random.randint(1, 100)
    critical = False

    if crit_roll <= crit_chance:
        critical = True
        raw_damage = int(raw_damage * (actor["crit_damage"] / 100))

        if raw_damage < 1:
            raw_damage = 1

    return {
        "damage": raw_damage,
        "missed": False,
        "critical": critical,
    }