import pygame

from game.hud.ui_helpers import DARK, PANEL, WHITE, draw_text


def draw_hotbar_widget(app):
    slots = [
        {"key": "1", "name": "Hacha", "tool": "axe", "icon": "A"},
        {"key": "2", "name": "Pico", "tool": "pickaxe", "icon": "P"},
        {"key": "3", "name": "Caña", "tool": "fishing_rod", "icon": "C"},
    ]

    from game.player.player_state import get_active_tool
    active_tool = get_active_tool(app.state)

    slot_size = 58
    gap = 10
    total_width = len(slots) * slot_size + (len(slots) - 1) * gap

    start_x = (960 - total_width) // 2
    y = 565

    for index, slot in enumerate(slots):
        x = start_x + index * (slot_size + gap)
        selected = active_tool == slot["tool"]

        fill = WHITE if selected else PANEL
        border_width = 4 if selected else 2

        pygame.draw.rect(app.screen, fill, (x, y, slot_size, slot_size), border_radius=8)
        pygame.draw.rect(app.screen, DARK, (x, y, slot_size, slot_size), border_width, border_radius=8)

        draw_text(app.screen, app.big_font, slot["icon"], x + 20, y + 8, DARK)
        draw_text(app.screen, app.small_font, slot["key"], x + 5, y + 38, DARK)