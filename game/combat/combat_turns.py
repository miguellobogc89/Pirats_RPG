import random

from game.combat.combat_status import tick_actor_cooldowns_on_turn_start
from game.combat.combat_targeting import get_valid_targets
from game.combat.combat_ability_executor import use_ability


ACTION_BAR_SPEED_MULTIPLIER = 4.0


def update_combat(manager, dt):
    if manager.combat.get("combat_result") is not None:
        return

    if manager.combat["animation_timer"] > 0:
        return

    update_death_timers(manager, dt)
    update_action_charges(manager, dt)
    update_active_unit(manager)
    try_enemy_action(manager)


def update_death_timers(manager, dt):
    for enemy in manager.combat["enemies"]:
        if enemy["hp"] > 0:
            continue

        if enemy["hidden"]:
            continue

        if enemy["death_timer"] <= 0:
            enemy["death_timer"] = 0.6
            continue

        enemy["death_timer"] -= dt

        if enemy["death_timer"] <= 0:
            enemy["hidden"] = True


def update_action_charges(manager, dt):
    active_unit = manager.combat.get("active_unit_id")

    if active_unit is not None:
        return

    for actor in get_all_living_actors(manager):
        if actor["action_charge"] >= actor["action_max"]:
            continue

        actor["action_charge"] += (
            actor["action_speed"]
            * ACTION_BAR_SPEED_MULTIPLIER
            * dt
        )

        if actor["action_charge"] > actor["action_max"]:
            actor["action_charge"] = actor["action_max"]


def update_active_unit(manager):
    if manager.combat.get("active_unit_id") is not None:
        return

    ready_actors = []

    for actor in get_all_living_actors(manager):
        if actor["action_charge"] >= actor["action_max"]:
            ready_actors.append(actor)

    if len(ready_actors) == 0:
        return

    selected_actor = ready_actors[0]

    for actor in ready_actors:
        if actor["speed"] > selected_actor["speed"]:
            selected_actor = actor

    manager.combat["active_unit_id"] = selected_actor["unit_id"]
    tick_actor_cooldowns_on_turn_start(selected_actor)
    manager.add_log(f"{selected_actor['name']} está listo.")


def try_enemy_action(manager):
    active_unit_id = manager.combat.get("active_unit_id")

    if active_unit_id is None:
        return

    actor = get_actor_by_id(manager, active_unit_id)

    if actor is None:
        return

    if actor["team"] != "enemy":
        return

    enemy_action(manager, actor)


def execute_player_action(manager, actor_id, ability_index, target_id):
    active_unit_id = manager.combat.get("active_unit_id")

    if active_unit_id != actor_id:
        return

    actor = get_actor_by_id(manager, actor_id)

    if actor is None:
        return

    if actor["hp"] <= 0:
        return

    if ability_index >= len(actor["abilities"]):
        return

    ability = actor["abilities"][ability_index]
    cooldown_left = actor["ability_cooldowns"].get(ability["id"], 0)

    if cooldown_left > 0:
        manager.add_log(f"{ability['name']} está recargando.")
        return

    targets = get_valid_targets(manager, actor, ability)

    if len(targets) == 0:
        return

    if target_id is not None:
        target = get_actor_by_id(manager, target_id)

        if target not in targets:
            return

        use_ability(manager, actor, [target], ability)
        return

    use_ability(manager, actor, targets, ability)


def enemy_action(manager, enemy):
    ability = enemy["abilities"][0]
    targets = get_valid_targets(manager, enemy, ability)

    if len(targets) == 0:
        return

    target = random.choice(targets)
    use_ability(manager, enemy, [target], ability)


def tick_all_ability_cooldowns(manager, dt):
    tick_ability_cooldowns(manager.combat["player"], dt)

    for creature in manager.combat["creatures"]:
        tick_ability_cooldowns(creature, dt)

    for enemy in manager.combat["enemies"]:
        tick_ability_cooldowns(enemy, dt)


def get_all_living_actors(manager):
    actors = []

    player = manager.combat["player"]

    if player["hp"] > 0:
        actors.append(player)

    for creature in manager.combat["creatures"]:
        if creature["hp"] > 0:
            actors.append(creature)

    for enemy in manager.combat["enemies"]:
        if enemy["hp"] > 0 and not enemy["hidden"]:
            actors.append(enemy)

    return actors


def get_actor_by_id(manager, actor_id):
    if manager.combat["player"]["unit_id"] == actor_id:
        return manager.combat["player"]

    for creature in manager.combat["creatures"]:
        if creature["unit_id"] == actor_id:
            return creature

    for enemy in manager.combat["enemies"]:
        if enemy["unit_id"] == actor_id:
            return enemy

    return None