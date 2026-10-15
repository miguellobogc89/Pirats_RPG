from game.inventory.hotbar_manager import get_active_hotbar_index, get_hotbar_slots
from game.ui.slot_renderer import draw_slot
import pygame


def hotbar_hit_index(app, pos):
    slots = get_hotbar_slots(app.state)
    size, gap = 50, 7
    start = (app.screen.get_width() - len(slots) * (size + gap) + gap) // 2
    y = app.screen.get_height() - size - 12
    for index in range(len(slots)):
        if pygame.Rect(start + index * (size + gap), y, size, size).collidepoint(pos):
            return index
    return None


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
            selected_fill_color=(205, 205, 205),
            border_color=(65, 65, 65) if index == active else (150, 150, 150),
            hotkey_label=str(index + 1),
            hotkey_position="top",
        )

