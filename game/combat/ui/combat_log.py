import pygame


INNER_PANEL = (220, 207, 170)


def draw_log(app, combat):
    pygame.draw.rect(app.screen, INNER_PANEL, (620, 465, 280, 120), border_radius=12)
    pygame.draw.rect(app.screen, app.DARK, (620, 465, 280, 120), 3, border_radius=12)

    title = "REGISTRO"

    if combat.get("combat_result") == "victory":
        title = "VICTORIA"

    if combat.get("combat_result") == "defeat":
        title = "DERROTA"

    app.draw_text(title, 640, 480, app.DARK, app.font)

    log_y = 508
    visible_messages = combat["log"][-4:]

    for message in visible_messages:
        app.draw_text(message, 640, log_y, app.DARK, app.small_font)
        log_y += 20

    if combat.get("combat_result") is not None:
        app.draw_text("Saliendo del combate...", 700, 562, app.DARK, app.small_font)
    else:
        app.draw_text("ESC salir", 810, 562, app.DARK, app.small_font)