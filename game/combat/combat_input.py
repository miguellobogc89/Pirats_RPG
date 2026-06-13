import pygame

from game.combat.combat_turns import execute_player_action
from game.combat.combat_targeting import ability_requires_manual_target
from game.combat.ui.combat_layout import get_actor_by_unit_id


def handle_combat_event(manager, event):
    if not manager.active:
        return

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            manager.combat["ui"]["pending_action"] = None
            manager.end_combat()
            return

        if manager.combat.get("combat_result") is not None:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                manager.end_combat()
                return

    if manager.combat.get("combat_result") is not None:
        return

    if event.type != pygame.MOUSEBUTTONDOWN:
        return

    if event.button != 1:
        return

    mouse_x, mouse_y = event.pos

    pending_action = manager.combat["ui"].get("pending_action")

    if pending_action is not None:
        for button in manager.combat["ui"]["target_buttons"]:
            if not button["enabled"]:
                continue

            if button["rect"].collidepoint(mouse_x, mouse_y):
                execute_player_action(
                    manager,
                    pending_action["actor_id"],
                    pending_action["ability_index"],
                    button["target_id"],
                )
                manager.combat["ui"]["pending_action"] = None
                return

    for button in manager.combat["ui"]["action_buttons"]:
        if not button["enabled"]:
            continue

        if not button["rect"].collidepoint(mouse_x, mouse_y):
            continue

        actor = get_actor_by_unit_id(manager.combat, button["actor_id"])

        if actor is None:
            return

        ability = actor["abilities"][button["ability_index"]]

        if ability_requires_manual_target(ability):
            manager.combat["ui"]["pending_action"] = {
                "actor_id": button["actor_id"],
                "ability_index": button["ability_index"],
            }
            manager.add_log("Selecciona objetivo.")
            return

        execute_player_action(
            manager,
            button["actor_id"],
            button["ability_index"],
            None,
        )
        return