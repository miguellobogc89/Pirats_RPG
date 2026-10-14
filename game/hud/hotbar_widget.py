from game.inventory.hotbar_manager import get_active_hotbar_index, get_hotbar_slots
from game.ui.slot_renderer import draw_slot
import pygame


def draw_hotbar_widget(app):
    slots = get_hotbar_slots(app.state)
    active = get_active_hotbar_index(app.state)
    size, gap = 50, 7
    start = (app.screen.get_width() - len(slots) * (size + gap) + gap) // 2
    y = app.screen.get_height() - size - 12
    for index, stack in enumerate(slots):
        rect = pygame.Rect(start + index * (size + gap), y, size, size)
        draw_slot(
            app.screen, rect, stack, app.font, app.small_font,
            selected=index == active,
            hotkey_label=str(index + 1),
            hotkey_position="top",
        )
