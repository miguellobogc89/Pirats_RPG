import pygame

from editor.ui.widgets.inspector_panel import (
    GODOT_BORDER,
    GODOT_BORDER_ACTIVE,
    GODOT_FIELD,
    GODOT_MUTED,
    GODOT_TEXT,
    draw_property_row_bg,
    draw_text,
    get_inspector_font,
)


def draw_text_input(
    screen,
    rect,
    label,
    value,
    action,
    focused=False,
    readonly=False,
    cursor_index=None,
    selection_range=None,
):
    draw_property_row_bg(screen, rect)
    label_rect = pygame.Rect(rect.x + 8, rect.y, 92, rect.h)
    field_rect = pygame.Rect(rect.x + 104, rect.y + 3, rect.w - 112, rect.h - 6)

    draw_text(
        screen,
        label,
        label_rect.x,
        label_rect.y + 6,
        GODOT_MUTED,
        12,
    )

    pygame.draw.rect(screen, GODOT_FIELD, field_rect, border_radius=2)
    border_color = GODOT_BORDER_ACTIVE if focused else GODOT_BORDER
    pygame.draw.rect(screen, border_color, field_rect, 1, border_radius=2)

    text_color = GODOT_MUTED if readonly else GODOT_TEXT
    font = get_inspector_font(12)
    text_value = str(value)
    text_surface = font.render(text_value, True, text_color)
    clipped = field_rect.inflate(-10, -4)
    screen.set_clip(clipped)
    if focused and selection_range and selection_range[0] != selection_range[1]:
        start, end = selection_range
        before_width = font.size(text_value[:start])[0]
        selected_width = font.size(text_value[start:end])[0]
        selection_rect = pygame.Rect(
            field_rect.x + 5 + before_width,
            field_rect.y + 4,
            selected_width,
            field_rect.h - 8,
        )
        pygame.draw.rect(screen, (66, 105, 162), selection_rect)
    screen.blit(text_surface, (field_rect.x + 5, field_rect.y + 5))
    screen.set_clip(None)

    if focused and not readonly:
        if cursor_index is None:
            cursor_index = len(text_value)
        cursor_width = font.size(text_value[:cursor_index])[0]
        cursor_x = min(field_rect.x + 5 + cursor_width + 2, field_rect.right - 5)
        pygame.draw.line(
            screen,
            GODOT_TEXT,
            (cursor_x, field_rect.y + 5),
            (cursor_x, field_rect.bottom - 5),
        )

    return {
        "rect": field_rect,
        "action": action,
    }

