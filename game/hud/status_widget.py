import pygame

from game.hud.ui_helpers import DARK, PANEL, WARN, WHITE, draw_bar, draw_text

HEALTH = (170, 65, 55)
ENERGY = (82, 150, 82)
MAGIC = (82, 92, 180)


def draw_status_widget(app):
    x = 18
    y = 42
    width = 250
    height = 100

    pygame.draw.rect(app.screen, PANEL, (x, y, width, height), border_radius=8)
    pygame.draw.rect(app.screen, DARK, (x, y, width, height), 3, border_radius=8)

    health = app.state["health"]
    energy = app.state["energy"]
    magic = app.state.get("magic", {"current": 0, "max": 0})

    draw_status_row(app, "♥", health, x + 18, y + 16, HEALTH)
    draw_status_row(app, "⚡", energy, x + 18, y + 42, ENERGY)
    draw_status_row(app, "✦", magic, x + 18, y + 68, MAGIC)


def draw_status_row(app, icon, stat, x, y, color):
    draw_text(app.screen, app.font, icon, x, y - 3, DARK)

    draw_bar(
        app.screen,
        x + 32,
        y,
        170,
        14,
        stat["current"],
        stat["max"],
        color,
    )