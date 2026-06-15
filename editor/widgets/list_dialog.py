import pygame

from editor.widgets.editor_button import draw_editor_button
from editor.widgets.inspector_panel import (
    GODOT_BORDER,
    GODOT_MUTED,
    GODOT_PANEL,
    GODOT_TEXT,
    draw_text,
)
from editor.widgets.modal_dialog import draw_modal_dialog


def draw_list_dialog(
    screen,
    title,
    items,
    draw_row,
    empty_text,
    cancel_action,
    width=560,
    height=380,
    row_height=32,
    scroll_y=0,
):
    modal = draw_modal_dialog(
        screen,
        title,
        width=width,
        height=height,
        close_action=cancel_action,
    )
    modal_rect = modal["rect"]
    content_rect = modal["content_rect"]
    footer_h = 48
    list_rect = pygame.Rect(
        content_rect.x + 8,
        content_rect.y + 4,
        content_rect.w - 16,
        content_rect.h - footer_h - 8,
    )

    pygame.draw.rect(screen, GODOT_PANEL, list_rect, border_radius=3)
    pygame.draw.rect(screen, GODOT_BORDER, list_rect, 1, border_radius=3)

    buttons = [modal["close_button"]]
    max_scroll = max(0, len(items) * row_height - list_rect.h)
    scroll_y = max(0, min(scroll_y, max_scroll))

    previous_clip = screen.get_clip()
    screen.set_clip(list_rect)

    if not items:
        draw_text(
            screen,
            empty_text,
            list_rect.x + 10,
            list_rect.y + 12,
            GODOT_MUTED,
            13,
        )
    else:
        for index, item in enumerate(items):
            row = pygame.Rect(
                list_rect.x,
                list_rect.y + index * row_height - scroll_y,
                list_rect.w,
                row_height,
            )

            if row.bottom < list_rect.y or row.y > list_rect.bottom:
                continue

            row_buttons = draw_row(screen, row, item)
            buttons.extend(row_buttons)

    screen.set_clip(previous_clip)

    if max_scroll > 0:
        draw_scrollbar(screen, list_rect, scroll_y, max_scroll)

    cancel_rect = pygame.Rect(modal_rect.right - 132, modal_rect.bottom - 42, 112, 28)
    buttons.append(
        draw_editor_button(
            screen,
            cancel_rect,
            "Cancelar",
            cancel_action,
            compact=True,
        )
    )

    return {
        "buttons": buttons,
        "max_scroll": max_scroll,
        "list_rect": list_rect,
    }


def draw_scrollbar(screen, rect, scroll_y, max_scroll):
    track = pygame.Rect(rect.right - 7, rect.y + 4, 4, rect.h - 8)
    pygame.draw.rect(screen, (24, 26, 31), track, border_radius=2)

    thumb_h = max(28, int(track.h * rect.h / (rect.h + max_scroll)))
    thumb_y = track.y + int((track.h - thumb_h) * scroll_y / max(1, max_scroll))
    thumb = pygame.Rect(track.x, thumb_y, track.w, thumb_h)
    pygame.draw.rect(screen, GODOT_BORDER, thumb, border_radius=2)


def draw_list_row_background(screen, row, active=False):
    if row.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, (55, 59, 66), row)
    elif active:
        pygame.draw.rect(screen, (48, 62, 79), row)

    pygame.draw.line(screen, GODOT_BORDER, row.bottomleft, row.bottomright)


def draw_row_text(screen, text, x, y, color=GODOT_TEXT):
    draw_text(screen, text, x, y, color, 13)
