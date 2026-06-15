import pygame

from editor.widgets.inspector_panel import (
    GODOT_ACCENT,
    GODOT_BORDER,
    GODOT_FIELD,
    GODOT_MUTED,
    GODOT_PANEL,
    GODOT_TEXT,
    draw_property_row_bg,
    draw_text,
)


def draw_dropdown(
    screen,
    rect,
    label,
    value,
    options,
    action,
    expanded=False,
    select_action="object_category_select",
    option_key="category",
    allow_new=True,
):
    buttons = []
    draw_property_row_bg(screen, rect)
    draw_text(screen, label, rect.x + 8, rect.y + 6, GODOT_MUTED, 12)

    field_rect = pygame.Rect(rect.x + 104, rect.y + 3, rect.w - 112, rect.h - 6)
    pygame.draw.rect(screen, GODOT_FIELD, field_rect, border_radius=2)
    pygame.draw.rect(screen, GODOT_BORDER, field_rect, 1, border_radius=2)
    draw_text(screen, value, field_rect.x + 6, field_rect.y + 5, GODOT_TEXT, 12)
    draw_text(screen, "v", field_rect.right - 15, field_rect.y + 5, GODOT_MUTED, 12, True)

    buttons.append({
        "rect": field_rect,
        "action": action,
    })

    if expanded:
        option_y = rect.bottom
        option_height = 24
        option_count = len(options) + (1 if allow_new else 0)
        dropdown_rect = pygame.Rect(
            field_rect.x,
            option_y,
            field_rect.w,
            option_height * option_count,
        )
        pygame.draw.rect(screen, GODOT_PANEL, dropdown_rect, border_radius=2)
        pygame.draw.rect(screen, GODOT_BORDER, dropdown_rect, 1, border_radius=2)

        for index, option in enumerate(options):
            option_rect = pygame.Rect(
                field_rect.x,
                option_y + index * option_height,
                field_rect.w,
                option_height,
            )
            if option == value:
                pygame.draw.rect(screen, (48, 62, 79), option_rect)
            draw_text(screen, option, option_rect.x + 6, option_rect.y + 5, GODOT_TEXT, 12)
            buttons.append({
                "rect": option_rect,
                "action": select_action,
                option_key: option,
            })

        if allow_new:
            new_rect = pygame.Rect(
                field_rect.x,
                option_y + len(options) * option_height,
                field_rect.w,
                option_height,
            )
            pygame.draw.line(screen, GODOT_BORDER, new_rect.topleft, new_rect.topright)
            draw_text(screen, "+ Nueva categoria", new_rect.x + 6, new_rect.y + 5, GODOT_ACCENT, 12)
            buttons.append({
                "rect": new_rect,
                "action": "object_category_new",
            })

    return buttons
