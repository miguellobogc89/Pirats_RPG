from game.hud.ui_helpers import DARK, draw_bar, draw_text

HEALTH = ENERGY = MAGIC = (218, 218, 218)


def draw_status_widget(app):
    # HUD de exploracion: solo vida, sin panel, energia ni magia.
    health = app.state["health"]
    draw_text(app.screen, app.small_font, "VIDA", 18, 20, DARK)
    draw_bar(app.screen, 58, 24, 155, 7, health["current"], health["max"], HEALTH)
