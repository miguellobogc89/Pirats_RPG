import pygame

from game.time.time_manager import get_calendar_text, get_time_text
from game.ui.ui_components import (
    PARCHMENT_LIGHT,
    TEXT_DARK,
    draw_content_panel,
    draw_panel,
    draw_text,
)


def draw_clock_widget(app):
    x = 720
    y = 12
    width = 220
    height = 112

    gold = app.state["resources"].get("gold", 0)

    panel_rect = pygame.Rect(x, y, width, height)
    draw_panel(app.screen, panel_rect)

    content_rect = pygame.Rect(x + 12, y + 12, width - 24, height - 24)

    draw_text(
        app.screen,
        app.small_font,
        get_calendar_text(app.state, app.game_data),
        content_rect.x,
        content_rect.y,
        TEXT_DARK,
    )

    clock_rect = pygame.Rect(
        content_rect.x,
        content_rect.y + 24,
        content_rect.width,
        36,
    )

    pygame.draw.rect(app.screen, PARCHMENT_LIGHT, clock_rect, border_radius=6)

    draw_text(
        app.screen,
        app.big_font,
        get_time_text(app.state),
        clock_rect.x + 12,
        clock_rect.y + 2,
        TEXT_DARK,
    )

    draw_text(
        app.screen,
        app.font,
        f"🪙 {gold}",
        content_rect.x,
        content_rect.y + 68,
        TEXT_DARK,
    )