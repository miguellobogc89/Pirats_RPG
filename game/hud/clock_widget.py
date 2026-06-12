from game.hud.ui_helpers import DARK, PANEL, draw_text
from game.time_manager import get_calendar_text, get_time_text


def draw_clock_widget(app):
    x = 720
    y = 12
    width = 220
    height = 92

    gold = app.state["resources"].get("gold", 0)

    draw_text(
        app.screen,
        app.small_font,
        get_calendar_text(app.state, app.game_data),
        x,
        y,
        DARK,
    )

    draw_text(
        app.screen,
        app.big_font,
        get_time_text(app.state),
        x,
        y + 22,
        DARK,
    )

    draw_text(
        app.screen,
        app.font,
        f"🪙 {gold}",
        x,
        y + 62,
        DARK,
    )