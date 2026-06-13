import pygame

from game.combat.ui.combat_layout import get_actor_by_unit_id


INNER_PANEL = (220, 207, 170)
ACTION_READY = (248, 244, 220)
ACTION_DISABLED = (170, 160, 140)


def draw_actions(app, combat):
    combat["ui"]["action_buttons"] = []

    pygame.draw.rect(app.screen, INNER_PANEL, (60, 465, 540, 120), border_radius=12)
    pygame.draw.rect(app.screen, app.DARK, (60, 465, 540, 120), 3, border_radius=12)

    app.draw_text("ACCIONES", 82, 480, app.DARK, app.font)

    if combat.get("combat_result") is not None:
        app.draw_text("Combate finalizado.", 82, 520, app.DARK, app.small_font)
        return

    active_unit_id = combat.get("active_unit_id")

    if active_unit_id is None:
        app.draw_text("Esperando a que una barra se llene...", 82, 520, app.DARK, app.small_font)
        return

    actor = get_actor_by_unit_id(combat, active_unit_id)

    if actor is None:
        return

    if actor["team"] != "player":
        app.draw_text("Turno enemigo...", 82, 520, app.WARN, app.small_font)
        return

    app.draw_text(f"Actúa: {actor['name']}", 210, 482, app.DARK, app.small_font)

    x = 82
    y = 518

    for ability_index, ability in enumerate(actor["abilities"]):
        cooldown_left = actor["ability_cooldowns"].get(ability["id"], 0)
        enabled = cooldown_left <= 0

        rect = pygame.Rect(x, y, 235, 38)

        color = ACTION_READY

        if not enabled:
            color = ACTION_DISABLED

        pygame.draw.rect(app.screen, color, rect, border_radius=8)
        pygame.draw.rect(app.screen, app.DARK, rect, 2, border_radius=8)

        text = ability["name"]

        if cooldown_left > 0:
            text = f"{text} [CD {int(cooldown_left) + 1}]"

        app.draw_text(text, x + 12, y + 10, app.DARK, app.small_font)

        combat["ui"]["action_buttons"].append(
            {
                "rect": rect,
                "actor_id": actor["unit_id"],
                "ability_index": ability_index,
                "enabled": enabled,
            }
        )

        x += 250