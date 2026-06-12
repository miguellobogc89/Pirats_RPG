from game.hud.clock_widget import draw_clock_widget
from game.hud.hotbar_widget import draw_hotbar_widget
from game.hud.status_widget import draw_status_widget


def draw_hud(app):
    if not app.hud_visible:
        return

    draw_status_widget(app)
    draw_clock_widget(app)
    draw_hotbar_widget(app)