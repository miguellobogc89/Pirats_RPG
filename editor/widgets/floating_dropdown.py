import pygame

from editor.widgets.inspector_panel import (
    GODOT_BORDER,
    GODOT_FIELD,
    GODOT_MUTED,
    GODOT_PANEL,
    GODOT_TEXT,
    draw_property_row_bg,
    draw_text,
)


OPTION_HEIGHT = 24


def draw_dropdown_field(screen, rect, label, value, action):
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
    return buttons, field_rect


def draw_floating_dropdown(
    screen,
    anchor_rect,
    options,
    selected_value,
    select_action,
    option_key,
    scroll_y=0,
    max_visible_options=6,
    allow_new=False,
    new_action=None,
    new_label="+ Nueva categoria",
):
    buttons = []
    visible_count = min(max_visible_options, len(options) + (1 if allow_new else 0))

    if visible_count <= 0:
        return {
            "buttons": [],
            "max_scroll": 0,
            "rect": pygame.Rect(anchor_rect.x, anchor_rect.bottom, anchor_rect.w, 0),
        }

    total_rows = len(options) + (1 if allow_new else 0)
    dropdown_h = visible_count * OPTION_HEIGHT
    dropdown_rect = pygame.Rect(anchor_rect.x, anchor_rect.bottom + 2, anchor_rect.w, dropdown_h)

    if dropdown_rect.bottom > screen.get_height() - 8:
        dropdown_rect.bottom = anchor_rect.top - 2

    max_scroll = max(0, total_rows * OPTION_HEIGHT - dropdown_rect.h)
    scroll_y = max(0, min(scroll_y, max_scroll))

    pygame.draw.rect(screen, GODOT_PANEL, dropdown_rect, border_radius=2)
    pygame.draw.rect(screen, GODOT_BORDER, dropdown_rect, 1, border_radius=2)

    previous_clip = screen.get_clip()
    screen.set_clip(dropdown_rect)

    for index, option in enumerate(options):
        option_rect = pygame.Rect(
            dropdown_rect.x,
            dropdown_rect.y + index * OPTION_HEIGHT - scroll_y,
            dropdown_rect.w,
            OPTION_HEIGHT,
        )

        if option_rect.bottom < dropdown_rect.y or option_rect.y > dropdown_rect.bottom:
            continue

        if option_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (55, 59, 66), option_rect)
        elif option == selected_value:
            pygame.draw.rect(screen, (48, 62, 79), option_rect)

        draw_text(screen, option, option_rect.x + 6, option_rect.y + 5, GODOT_TEXT, 12)
        buttons.append({
            "rect": option_rect,
            "action": select_action,
            option_key: option,
        })

    if allow_new:
        new_index = len(options)
        new_rect = pygame.Rect(
            dropdown_rect.x,
            dropdown_rect.y + new_index * OPTION_HEIGHT - scroll_y,
            dropdown_rect.w,
            OPTION_HEIGHT,
        )

        if new_rect.bottom >= dropdown_rect.y and new_rect.y <= dropdown_rect.bottom:
            pygame.draw.line(screen, GODOT_BORDER, new_rect.topleft, new_rect.topright)
            if new_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (55, 59, 66), new_rect)
            draw_text(screen, new_label, new_rect.x + 6, new_rect.y + 5, (86, 145, 214), 12)
            buttons.append({
                "rect": new_rect,
                "action": new_action,
            })

    screen.set_clip(previous_clip)

    if max_scroll > 0:
        draw_dropdown_scrollbar(screen, dropdown_rect, scroll_y, max_scroll)

    return {
        "buttons": buttons,
        "max_scroll": max_scroll,
        "rect": dropdown_rect,
    }


def draw_dropdown_scrollbar(screen, rect, scroll_y, max_scroll):
    track = pygame.Rect(rect.right - 6, rect.y + 4, 3, rect.h - 8)
    pygame.draw.rect(screen, (24, 26, 31), track, border_radius=2)
    thumb_h = max(18, int(track.h * rect.h / (rect.h + max_scroll)))
    thumb_y = track.y + int((track.h - thumb_h) * scroll_y / max(1, max_scroll))
    thumb = pygame.Rect(track.x, thumb_y, track.w, thumb_h)
    pygame.draw.rect(screen, GODOT_BORDER, thumb, border_radius=2)
