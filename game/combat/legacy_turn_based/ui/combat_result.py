import pygame


def draw_result_panel(app, combat):
    result = combat.get("combat_result")

    if result is None:
        return

    text = "VICTORIA"

    if result == "defeat":
        text = "DERROTA"

    pygame.draw.rect(app.screen, (245, 232, 188), (310, 225, 340, 120), border_radius=14)
    pygame.draw.rect(app.screen, app.DARK, (310, 225, 340, 120), 4, border_radius=14)

    app.draw_text(text, 405, 255, app.DARK, app.big_font)
    app.draw_text("Recompensas proximamente", 365, 300, app.DARK, app.small_font)