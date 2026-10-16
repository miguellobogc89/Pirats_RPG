TARGET_ENEMY_SINGLE = "enemy_single"
TARGET_ENEMY_ALL = "enemy_all"
TARGET_ALLY_SINGLE = "ally_single"
TARGET_ALLY_ALL = "ally_all"
TARGET_SELF = "self"
TARGET_PLAYER = "player"


def ability_requires_manual_target(ability):
    target_type = ability.get("target_type", TARGET_ENEMY_SINGLE)

    if target_type == TARGET_ENEMY_SINGLE:
        return True

    if target_type == TARGET_ALLY_SINGLE:
        return True

    return False


def get_valid_targets(manager, actor, ability):
    target_type = ability.get("target_type", TARGET_ENEMY_SINGLE)

    if target_type == TARGET_ENEMY_SINGLE:
        return get_living_opponents(manager, actor)

    if target_type == TARGET_ENEMY_ALL:
        return get_living_opponents(manager, actor)

    if target_type == TARGET_ALLY_SINGLE:
        return get_living_allies(manager, actor)

    if target_type == TARGET_ALLY_ALL:
        return get_living_allies(manager, actor)

    if target_type == TARGET_SELF:
        return [actor]

    if target_type == TARGET_PLAYER:
        player = manager.combat["player"]

        if player["hp"] > 0:
            return [player]

    return []


def get_living_opponents(manager, actor):
    opponents = []

    if actor["team"] == "player":
        for enemy in manager.combat["enemies"]:
            if enemy["hp"] > 0 and not enemy.get("hidden", False):
                opponents.append(enemy)

    if actor["team"] == "enemy":
        player = manager.combat["player"]

        if player["hp"] > 0:
            opponents.append(player)

        for creature in manager.combat["creatures"]:
            if creature["hp"] > 0:
                opponents.append(creature)

    return opponents


def get_living_allies(manager, actor):
    allies = []

    if actor["team"] == "player":
        player = manager.combat["player"]

        if player["hp"] > 0:
            allies.append(player)

        for creature in manager.combat["creatures"]:
            if creature["hp"] > 0:
                allies.append(creature)

    if actor["team"] == "enemy":
        for enemy in manager.combat["enemies"]:
            if enemy["hp"] > 0 and not enemy.get("hidden", False):
                allies.append(enemy)

    return allies