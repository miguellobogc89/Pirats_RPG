import pygame

from editor.ui.widgets.inspector_panel import (
    GODOT_ACCENT,
    GODOT_MUTED,
    draw_text,
)


def draw_section_header(screen, title, x, y, width):
    draw_text(screen, title, x, y, GODOT_ACCENT, 13, True)

    line_y = y + 18
    pygame.draw.line(
        screen,
        GODOT_MUTED,
        (x, line_y),
        (x + width, line_y),
        1,
    )

    return y + 26