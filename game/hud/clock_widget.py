"""Recuadro de dia y hora, con sol o luna segun la hora."""
from game.time.time_manager import get_time_text
from game.ui.retro import INK, LINE, draw_frame, get_icon

WIDTH, HEIGHT = 168, 60


def draw_clock_widget(app):
    screen = app.screen
    x, y = screen.get_width() - WIDTH - 16, 14
    draw_frame(screen, (x, y, WIDTH, HEIGHT))
    time_state = app.state.get("time", {})
    day = app.state.get("day", time_state.get("day", 1))
    hour = int(time_state.get("hour", 12))
    icon = get_icon("sun" if 6 <= hour < 20 else "moon", 3)
    screen.blit(icon, (x + 14, y + (HEIGHT - icon.get_height()) // 2))
    day_label = app.small_font.render(f"DÍA {day}", False, LINE)
    clock_label = app.font.render(get_time_text(app.state), False, INK)
    text_x = x + 56
    screen.blit(day_label, (text_x, y + 8))
    screen.blit(clock_label, (text_x, y + 30))
