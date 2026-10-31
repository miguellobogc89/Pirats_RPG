"""Barra de objetos rapidos sobre un panel comun."""
import pygame

from game.inventory.hotbar_manager import get_active_hotbar_index, get_hotbar_slots
from game.ui.retro import INK, draw_frame
from game.ui.slot_renderer import draw_slot

SLOT_SIZE, GAP, PADDING, BOTTOM = 48, 6, 10, 14


def _layout(app, count):
    total = count * (SLOT_SIZE + GAP) - GAP
    start = (app.screen.get_width() - total) // 2
    y = app.screen.get_height() - SLOT_SIZE - PADDING - BOTTOM
    return start, y


def hotbar_hit_index(app, pos):
    slots = get_hotbar_slots(app.state)
    start, y = _layout(app, len(slots))
    for index in range(len(slots)):
        if pygame.Rect(start + index * (SLOT_SIZE + GAP), y, SLOT_SIZE, SLOT_SIZE).collidepoint(pos):
            return index
    return None


def draw_hotbar_widget(app):
    slots = get_hotbar_slots(app.state)
    active = get_active_hotbar_index(app.state)
    start, y = _layout(app, len(slots))
    total = len(slots) * (SLOT_SIZE + GAP) - GAP
    draw_frame(app.screen, (start - PADDING, y - PADDING, total + PADDING * 2, SLOT_SIZE + PADDING * 2))
    for index, stack in enumerate(slots):
        rect = pygame.Rect(start + index * (SLOT_SIZE + GAP), y, SLOT_SIZE, SLOT_SIZE)
        draw_slot(
            app.screen, rect, stack, app.font, app.small_font,
            selected=index == active,
            hotkey_label=str(index + 1),
            hotkey_position="top",
        )
        if index == active:
            # Flecha sobre la casilla activa.
            pygame.draw.polygon(app.screen, INK, [(rect.centerx - 6, y - PADDING - 12),
                                                  (rect.centerx + 6, y - PADDING - 12),
                                                  (rect.centerx, y - PADDING - 5)])
