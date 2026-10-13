import pygame

from game.hud.ui_helpers import DARK, PANEL, WHITE
from game.inventory.hotbar_manager import get_active_hotbar_index, get_hotbar_slots
from game.data.item_database import get_item_data


def draw_hotbar_widget(app):
    slots = get_hotbar_slots(app.state)
    active = get_active_hotbar_index(app.state)
    size, gap = 42, 7
    start = (app.screen.get_width() - len(slots) * (size + gap) + gap) // 2
    y = app.screen.get_height() - 55
    for i, stack in enumerate(slots):
        x = start + i * (size + gap)
        border = (155, 155, 155) if i == active else (218, 218, 218)
        pygame.draw.rect(app.screen, border, (x, y, size, size), 1)
        app.screen.blit(app.small_font.render(str(i + 1), True, DARK), (x + 3, y + 2))
        if isinstance(stack, dict) and stack.get("item_id"):
            item = get_item_data(stack["item_id"]) or {}
            symbol = str(item.get("icon") or stack["item_id"][:1])[:2]
            app.screen.blit(app.font.render(symbol, True, DARK), (x + 15, y + 15))
