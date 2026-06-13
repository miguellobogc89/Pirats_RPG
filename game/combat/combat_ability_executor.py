from game.combat.combat_status import (
    tick_statuses,
    apply_ability_cooldown,
    apply_status,
)


def use_ability(manager, actor, targets, ability):
    reset_last_feedback(manager)

    actor["action_charge"] = 0
    manager.combat["active_unit_id"] = None

    apply_ability_cooldown(actor, ability)
    tick_statuses(actor)

    actor_id = actor["unit_id"]
    effect = ability["effect"]

    if effect == "status_all_allies":
        apply_status_to_targets(manager, actor, targets, ability)
        return

    if effect == "damage":
        apply_damage_to_targets(manager, actor, targets, ability, False)
        return

    if effect == "damage_status":
        apply_damage_to_targets(manager, actor, targets, ability, True)
        return


def apply_status_to_targets(manager, actor, targets, ability):
    affected_names = []

    for target in targets:
        applied = apply_status(target, ability["status_id"])

        if applied:
            affected_names.append(target["name"])

    start_action_animation(manager, actor["unit_id"], actor["unit_id"])

    if len(affected_names) == 0:
        manager.add_log(f"{actor['name']} usa {ability['name']}, pero no afecta a nadie.")
    else:
        manager.add_log(f"{actor['name']} usa {ability['name']}.")

    clamp_defeated_units(manager)
    check_combat_end(manager)


def apply_damage_to_targets(manager, actor, targets, ability, should_apply_status):
    first_target_id = actor["unit_id"]

    for target in targets:
        if target["hp"] <= 0:
            continue

        if first_target_id == actor["unit_id"]:
            first_target_id = target["unit_id"]

        damage_result = manager.calculate_damage(actor, target, ability)

        if damage_result["missed"]:
            target["last_missed"] = True
            manager.add_log(f"{actor['name']} falla {ability['name']} contra {target['name']}.")
            continue

        target["hp"] -= damage_result["damage"]
        target["last_damage"] = damage_result["damage"]
        target["last_critical"] = damage_result["critical"]

        if target.get("guarding", False):
            target["guarding"] = False

        if should_apply_status:
            applied = apply_status(target, ability["status_id"])

            if applied:
                manager.add_log(f"{target['name']} sufre un estado alterado.")

        if damage_result["critical"]:
            manager.add_log(f"¡Crítico! {actor['name']} causa {damage_result['damage']} daño a {target['name']}.")
        else:
            manager.add_log(f"{actor['name']} usa {ability['name']} contra {target['name']} y causa {damage_result['damage']} daño.")

    start_action_animation(manager, actor["unit_id"], first_target_id)

    clamp_defeated_units(manager)
    check_combat_end(manager)


def reset_last_feedback(manager):
    manager.combat["player"]["last_damage"] = 0
    manager.combat["player"]["last_missed"] = False
    manager.combat["player"]["last_critical"] = False

    for creature in manager.combat["creatures"]:
        creature["last_damage"] = 0
        creature["last_missed"] = False
        creature["last_critical"] = False

    for enemy in manager.combat["enemies"]:
        enemy["last_damage"] = 0
        enemy["last_missed"] = False
        enemy["last_critical"] = False


def start_action_animation(manager, actor_id, target_id):
    manager.combat["last_actor"] = actor_id
    manager.combat["last_target"] = target_id
    manager.combat["animation_timer"] = manager.combat["animation_duration"]


def clamp_defeated_units(manager):
    player = manager.combat["player"]

    if player["hp"] < 0:
        player["hp"] = 0

    for creature in manager.combat["creatures"]:
        if creature["hp"] < 0:
            creature["hp"] = 0

    for enemy in manager.combat["enemies"]:
        if enemy["hp"] < 0:
            enemy["hp"] = 0


def check_combat_end(manager):
    player = manager.combat["player"]

    living_enemy = False

    for enemy in manager.combat["enemies"]:
        if enemy["hp"] > 0:
            living_enemy = True

    if not living_enemy:
        manager.combat["combat_result"] = "victory"
        manager.add_log("Has ganado el combate.")
        manager.app.skill_manager.register_action("combat_won")
        return True

    if player["hp"] <= 0:
        player["hp"] = 0
        manager.combat["combat_result"] = "defeat"
        manager.add_log("Has perdido el combate.")
        return True

    living_creature = False

    for creature in manager.combat["creatures"]:
        if creature["hp"] > 0:
            living_creature = True

    if not living_creature:
        manager.combat["combat_result"] = "defeat"
        manager.add_log("Tus criaturas han caído.")
        return True

    return False