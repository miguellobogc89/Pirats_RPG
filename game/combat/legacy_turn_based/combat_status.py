import random


STATUS_DEFINITIONS = {
    "defense_up": {
        "name": "Defensa aumentada",
        "duration": 3,
        "defense_multiplier": 1.10,
        "icon": "D+",
    },
    "defense_down": {
        "name": "Defensa reducida",
        "duration": 3,
        "defense_multiplier": 0.90,
        "icon": "D-",
    },
    "crit_up": {
        "name": "Crítico aumentado",
        "duration": 3,
        "crit_chance_bonus": 10,
        "icon": "C+",
    },
    "miss_up": {
        "name": "Precisión reducida",
        "duration": 2,
        "miss_chance_bonus": 20,
        "icon": "M",
    },
}


def apply_ability_cooldown(actor, ability):
    cooldown = ability.get("cooldown", 0)

    if cooldown < 0:
        cooldown = 0

    actor["ability_cooldowns"][ability["id"]] = cooldown


def tick_ability_cooldowns(actor, dt=None):
    # No usamos dt: el cooldown baja por acción propia, no por tiempo real.
    return


def tick_actor_cooldowns_on_turn_start(actor):
    for ability_id in list(actor["ability_cooldowns"].keys()):
        if actor["ability_cooldowns"][ability_id] <= 0:
            actor["ability_cooldowns"][ability_id] = 0
            continue

        actor["ability_cooldowns"][ability_id] -= 1

        if actor["ability_cooldowns"][ability_id] < 0:
            actor["ability_cooldowns"][ability_id] = 0


def apply_status(actor, status_id):
    if status_id not in STATUS_DEFINITIONS:
        return False

    resistance = actor.get("status_resistance", 0)
    roll = random.randint(1, 100)

    if roll <= resistance:
        return False

    status_data = STATUS_DEFINITIONS[status_id]

    for status in actor["statuses"]:
        if status["id"] == status_id:
            status["turns_left"] = status_data["duration"]
            return True

    actor["statuses"].append(
        {
            "id": status_id,
            "turns_left": status_data["duration"],
        }
    )

    return True


def tick_statuses(actor):
    remaining_statuses = []

    for status in actor["statuses"]:
        status["turns_left"] -= 1

        if status["turns_left"] > 0:
            remaining_statuses.append(status)

    actor["statuses"] = remaining_statuses


def get_status_definition(status_id):
    return STATUS_DEFINITIONS.get(status_id)


def get_modified_defense(actor):
    defense = actor["defense"]

    for status in actor["statuses"]:
        status_data = get_status_definition(status["id"])

        if status_data is None:
            continue

        if "defense_multiplier" in status_data:
            defense = defense * status_data["defense_multiplier"]

    return int(defense)


def get_modified_crit_chance(actor):
    crit_chance = actor.get("crit_chance", 0)

    for status in actor["statuses"]:
        status_data = get_status_definition(status["id"])

        if status_data is None:
            continue

        if "crit_chance_bonus" in status_data:
            crit_chance += status_data["crit_chance_bonus"]

    return crit_chance


def get_modified_miss_chance(actor):
    miss_chance = 0

    for status in actor["statuses"]:
        status_data = get_status_definition(status["id"])

        if status_data is None:
            continue

        if "miss_chance_bonus" in status_data:
            miss_chance += status_data["miss_chance_bonus"]

    return miss_chance