import pygame

from editor.ui.widgets.inspector_panel import (
    GODOT_BORDER,
    GODOT_PANEL,
    GODOT_TEXT,
    draw_text,
)


def draw_property_group(screen, rect, title):
    pygame.draw.rect(screen, GODOT_PANEL, rect, border_radius=5)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=5)

    draw_text(screen, title, rect.x + 10, rect.y + 8, GODOT_TEXT, 13, True)

    return rect.y + 32