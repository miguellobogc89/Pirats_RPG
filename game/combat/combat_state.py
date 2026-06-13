from game.bestiary.creature_database import get_creature_data, get_enemy_data


def create_combat_actor_from_data(unit_id, team, name, data):
    return {
        "unit_id": unit_id,
        "team": team,
        "name": name,
        "hp": data["max_hp"],
        "display_hp": data["max_hp"],
        "max_hp": data["max_hp"],
        "attack": data["attack"],
        "defense": data["defense"],
        "speed": data["speed"],
        "status_resistance": data["status_resistance"],
        "crit_chance": data["crit_chance"],
        "crit_damage": data["crit_damage"],
        "abilities": data["abilities"],
        "ability_cooldowns": {},
        "action_charge": 0,
        "action_max": 100,
        "action_speed": data["speed"],
        "guarding": False,
        "statuses": [],
        "last_damage": 0,
        "last_missed": False,
        "last_critical": False,
        "death_timer": 0,
        "hidden": False,
    }


def create_test_combat_state(app):
    party = app.bestiary_manager.get_active_party()

    if len(party) == 0:
        return None

    player_creatures = []

    for index, owned_creature in enumerate(party):
        creature_data = get_creature_data(owned_creature["creature_id"])

        if creature_data is None:
            continue

        creature = create_combat_actor_from_data(
            f"creature_{index}",
            "player",
            app.bestiary_manager.get_creature_display_name(owned_creature),
            creature_data,
        )

        creature["creature_id"] = owned_creature["creature_id"]
        player_creatures.append(creature)

    enemy_data = get_enemy_data("farm_slime")

    enemies = []

    for index in range(3):
        enemy = create_combat_actor_from_data(
            f"enemy_{index}",
            "enemy",
            f"{enemy_data['name']} {index + 1}",
            enemy_data,
        )
        enemy["enemy_id"] = "farm_slime"
        enemies.append(enemy)

    player_data = {
        "max_hp": 52,
        "attack": 8,
        "defense": 3,
        "speed": 76,
        "status_resistance": 15,
        "crit_chance": 8,
        "crit_damage": 150,
        "abilities": [
            {
                "id": "player_basic_attack",
                "name": "Ataque básico",
                "power": 0,
                "effect": "damage",
                "cooldown": 0,
            },
            {
                "id": "player_heavy_attack",
                "name": "Golpe fuerte",
                "power": 6,
                "effect": "damage",
                "cooldown": 2,
            },
        ],
    }

    return {
        "round": 1,
        "mode": "active_time",
        "active_unit_id": None,
        "combat_result": None,
        "result_timer": 0,
        "result_exit_delay": 3.0,
        "animation_timer": 0,
        "animation_duration": 0.32,
        "last_actor": None,
        "last_target": None,
        "ui": {
            "action_buttons": [],
            "target_buttons": [],
            "pending_action": None,
        },
        "player": create_combat_actor_from_data(
            "player",
            "player",
            "Jugador",
            player_data,
        ),
        "creatures": player_creatures,
        "enemies": enemies,
        "log": [
            "¡Tres slimes aparecen!",
            "Espera a que una unidad esté lista.",
        ],
    }