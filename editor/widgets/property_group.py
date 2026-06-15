import pygame

from editor.widgets.inspector_panel import (
    GODOT_BORDER,
    GODOT_SECTION,
    GODOT_TEXT,
    draw_text,
)


def draw_property_group(screen, rect, title, expanded=True):
    pygame.draw.rect(screen, GODOT_SECTION, rect)
    pygame.draw.line(screen, GODOT_BORDER, rect.bottomleft, rect.bottomright)

    arrow = "v" if expanded else ">"
    draw_text(screen, arrow, rect.x + 8, rect.y + 6, GODOT_TEXT, 12, True)
    draw_text(screen, title, rect.x + 24, rect.y + 5, GODOT_TEXT, 13, True)

    return {
        "rect": rect,
        "action": "object_toggle_group",
        "group": title,
    }
