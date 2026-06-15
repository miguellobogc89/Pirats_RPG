import pygame

from editor.widgets.inspector_panel import (
    GODOT_ACCENT,
    GODOT_BORDER,
    GODOT_FIELD,
    GODOT_MUTED,
    GODOT_TEXT,
    draw_property_row_bg,
    draw_text,
    draw_tooltip,
)


def draw_checkbox(screen, rect, label, checked, action, tooltip=None, disabled=False):
    draw_property_row_bg(screen, rect)
    box_rect = pygame.Rect(rect.x + 8, rect.y + 6, 16, 16)

    pygame.draw.rect(screen, GODOT_FIELD, box_rect, border_radius=2)
    pygame.draw.rect(screen, GODOT_BORDER, box_rect, 1, border_radius=2)

    if checked:
        pygame.draw.line(screen, GODOT_ACCENT, (box_rect.x + 3, box_rect.centery), (box_rect.centerx - 1, box_rect.bottom - 4), 2)
        pygame.draw.line(screen, GODOT_ACCENT, (box_rect.centerx - 1, box_rect.bottom - 4), (box_rect.right - 3, box_rect.y + 4), 2)

    text_color = GODOT_MUTED if disabled else GODOT_TEXT
    draw_text(screen, label, rect.x + 32, rect.y + 6, text_color, 12)

    mouse_pos = pygame.mouse.get_pos()
    if tooltip and rect.collidepoint(mouse_pos):
        draw_text(screen, "?", rect.right - 16, rect.y + 6, GODOT_MUTED, 12, True)
        draw_tooltip(screen, tooltip, mouse_pos)

    return {
        "rect": rect,
        "action": None if disabled else action,
    }
