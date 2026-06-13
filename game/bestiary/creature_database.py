CREATURE_DATABASE = {
    "rock_turtle": {
        "name": "Tortuga de Roca",
        "role": "defender",
        "max_hp": 44,
        "attack": 5,
        "defense": 7,
        "speed": 70,
        "status_resistance": 20,
        "crit_chance": 5,
        "crit_damage": 150,
        "abilities": [
            {
                "id": "stone_guard",
                "name": "Guardia pétrea",
                "power": 0,
                "effect": "status_all_allies",
                "status_id": "defense_up",
                "cooldown": 3,
            },
            {
                "id": "shell_bash",
                "name": "Golpe de caparazón",
                "power": 8,
                "effect": "damage",
                "cooldown": 1,
            },
        ],
    },
    "fire_worm": {
        "name": "Gusano de Fuego",
        "role": "attacker",
        "max_hp": 28,
        "attack": 9,
        "defense": 2,
        "speed": 82,
        "status_resistance": 10,
        "crit_chance": 12,
        "crit_damage": 160,
        "abilities": [
            {
                "id": "ember_bite",
                "name": "Mordisco ígneo",
                "power": 9,
                "effect": "damage",
                "cooldown": 1,
            },
            {
                "id": "burning_spit",
                "name": "Escupitajo ardiente",
                "power": 12,
                "effect": "damage",
                "cooldown": 2,
            },
        ],
    },
}


ENEMY_DATABASE = {
    "farm_slime": {
        "name": "Slime de la Granja",
        "max_hp": 44,
        "attack": 6,
        "defense": 2,
        "speed": 58,
        "status_resistance": 5,
        "crit_chance": 5,
        "crit_damage": 140,
        "abilities": [
            {
                "id": "slime_slam",
                "name": "Golpe viscoso",
                "power": 7,
                "effect": "damage_status",
                "status_id": "miss_up",
                "cooldown": 1,
            }
        ],
    }
}


def get_creature_data(creature_id):
    return CREATURE_DATABASE.get(creature_id)


def get_enemy_data(enemy_id):
    return ENEMY_DATABASE.get(enemy_id)


def get_all_creatures():
    return CREATURE_DATABASE