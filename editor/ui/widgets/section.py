import pygame

from editor.ui.widgets.inspector_panel import (
    GODOT_ACCENT,
    GODOT_BORDER,
    GODOT_FIELD,
    GODOT_TEXT,
    draw_text,
)


def draw_section_header(screen, rect, title, expanded=True, action=None, section_id=None):
    pygame.draw.rect(screen, GODOT_FIELD, rect, border_radius=4)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=4)

    marker = "v" if expanded else ">"
    draw_text(screen, marker, rect.x + 8, rect.y + 7, GODOT_ACCENT, 13, True)
    draw_text(screen, title, rect.x + 26, rect.y + 7, GODOT_TEXT, 13, True)

    return {
        "rect": rect,
        "action": action,
        "section_id": section_id,
    }