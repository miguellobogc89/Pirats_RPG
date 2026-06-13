import pygame

from game.hud.ui_helpers import DARK, PANEL, WHITE, draw_text
from game.inventory.hotbar_manager import (
    get_active_hotbar_index,
    get_hotbar_slots,
)
from game.data.item_database import get_item_data
from game.ui.sprite_renderer import draw_item_sprite


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

        fill = WHITE if selected else PANEL
        border_width = 4 if selected else 2

        pygame.draw.rect(app.screen, fill, (x, y, slot_size, slot_size), border_radius=8)
        pygame.draw.rect(app.screen, DARK, (x, y, slot_size, slot_size), border_width, border_radius=8)

        key_text = str(index + 1)
        draw_text(app.screen, app.small_font, key_text, x + 5, y + 38, DARK)

        if slot is None:
            continue

        item_id = slot["item_id"]
        amount = slot["amount"]
        item_data = get_item_data(item_id)

        if item_data is None:
            continue

        draw_item_sprite(
            app.screen,
            item_data,
            pygame.Rect(x + 8, y + 5, 42, 42),
            padding=1,
        )

        if amount > 1:
            draw_text(app.screen, app.small_font, str(amount), x + 38, y + 38, DARK)
