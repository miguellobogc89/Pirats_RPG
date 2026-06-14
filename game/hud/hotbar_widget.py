import pygame

from game.hud.ui_helpers import DARK, PANEL, WHITE
from game.inventory.hotbar_manager import (
    get_active_hotbar_index,
    get_hotbar_slots,
)
from game.ui.slot_renderer import draw_slot


def draw_hotbar_widget(app):
    slots = get_hotbar_slots(app.state)
    active_index = get_active_hotbar_index(app.state)

    slot_size = 58
    gap = 10
    total_width = len(slots) * slot_size + (len(slots) - 1) * gap

    start_x = (960 - total_width) // 2
    y = 565

    for index, slot in enumerate(slots):
        x = start_x + index * (slot_size + gap)
        selected = active_index == index
        slot_rect = pygame.Rect(x, y, slot_size, slot_size)

        draw_slot(
            app.screen,
            slot_rect,
            slot,
            app.font,
            app.small_font,
            selected=selected,
            hotkey_label=str(index + 1),
            fill_color=PANEL,
            selected_fill_color=WHITE,
            border_color=DARK,
            text_color=DARK,
            hotkey_position="bottom",
        )
