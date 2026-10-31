"""Recuadro de vida: nombre, corazones y numero."""
import math

from game.ui.retro import INK, LINE, draw_frame, get_icon

HEARTS = 5
PANEL = (16, 14, 236, 60)


def get_health(app):
    # Algunas escenas (combate de la playa) muestran su propia vida.
    override = getattr(app, "hud_health", None)
    if override:
        return override
    health = app.state.get("health", {})
    return max(0, health.get("current", 10)), max(1, health.get("max", 10))


def draw_status_widget(app):
    current, maximum = get_health(app)
    screen = app.screen
    x, y, width, height = PANEL
    draw_frame(screen, (x, y, width, height))
    name = (app.state.get("player", {}) or {}).get("name") or "VIDA"
    screen.blit(app.small_font.render(str(name).upper(), False, INK), (x + 14, y + 7))
    numbers = app.small_font.render(f"{current}/{maximum}", False, LINE)
    screen.blit(numbers, (x + width - numbers.get_width() - 14, y + 7))
    filled = math.ceil(HEARTS * min(current, maximum) / maximum) if current > 0 else 0
    full, empty = get_icon("heart"), get_icon("heart_empty")
    for i in range(HEARTS):
        screen.blit(full if i < filled else empty, (x + 14 + i * (full.get_width() + 6), y + 32))
