import pygame

from game.combat.ui.combat_layout import get_actor_by_unit_id


ACTION_READY = (248, 244, 220)
ACTION_DISABLED = (170, 160, 140)
ACTION_HOVER = (255, 250, 225)
ACTION_TEXT_DISABLED = (95, 82, 62)
ACTION_LIST_X = 24
ACTION_LIST_Y = 490
ACTION_LIST_WIDTH = 520
ACTION_ROW_HEIGHT = 30
ACTION_ROW_GAP = 8
MAX_VISIBLE_ACTIONS = 4


def draw_actions(app, combat):
    combat["ui"]["action_buttons"] = []

    if combat.get("combat_result") is not None:
        app.draw_text("Combate finalizado.", ACTION_LIST_X, ACTION_LIST_Y, app.DARK, app.small_font)
        return

    active_unit_id = combat.get("active_unit_id")

    if active_unit_id is None:
        app.draw_text(
            "Esperando a que una barra se llene...",
            ACTION_LIST_X,
            ACTION_LIST_Y,
            app.DARK,
            app.small_font,
        )
        return

    actor = get_actor_by_unit_id(combat, active_unit_id)

    if actor is None:
        return

    if actor["team"] != "player":
        app.draw_text("Turno enemigo...", ACTION_LIST_X, ACTION_LIST_Y, app.WARN, app.small_font)
        return

    mouse_pos = pygame.mouse.get_pos()

    for ability_index, ability in enumerate(actor["abilities"][:MAX_VISIBLE_ACTIONS]):
        cooldown_left = actor["ability_cooldowns"].get(ability["id"], 0)
        enabled = cooldown_left <= 0

        rect = pygame.Rect(
            ACTION_LIST_X,
            ACTION_LIST_Y + ability_index * (ACTION_ROW_HEIGHT + ACTION_ROW_GAP),
            ACTION_LIST_WIDTH,
            ACTION_ROW_HEIGHT,
        )

        color = ACTION_READY

        if not enabled:
            color = ACTION_DISABLED

        if enabled and rect.collidepoint(mouse_pos):
            color = ACTION_HOVER

        pygame.draw.rect(app.screen, color, rect, border_radius=6)
        pygame.draw.rect(app.screen, app.DARK, rect, 1, border_radius=6)

        text = ability["name"]
        text_color = app.DARK

        if cooldown_left > 0:
            text = f"{text} [CD {int(cooldown_left) + 1}]"
            text_color = ACTION_TEXT_DISABLED

        app.draw_text(text, rect.x + 12, rect.y + 7, text_color, app.small_font)

        combat["ui"]["action_buttons"].append(
            {
                "rect": rect,
                "actor_id": actor["unit_id"],
                "ability_index": ability_index,
                "enabled": enabled,
            }
        )
