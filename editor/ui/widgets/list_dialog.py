import pygame

from editor.ui.widgets.editor_button import draw_editor_button
from editor.ui.widgets.inspector_panel import (
    GODOT_BORDER,
    GODOT_FIELD,
    GODOT_MUTED,
    GODOT_PANEL,
    GODOT_TEXT,
    get_font,
)


def draw_list_dialog(
    screen,
    title,
    items,
    draw_row_callback,
    empty_message,
    close_action,
    width=520,
    height=360,
    row_height=30,
    scroll_y=0,
):
    screen_rect = screen.get_rect()
    modal_rect = pygame.Rect(0, 0, width, height)
    modal_rect.center = screen_rect.center

    pygame.draw.rect(screen, GODOT_PANEL, modal_rect, border_radius=8)
    pygame.draw.rect(screen, GODOT_BORDER, modal_rect, 1, border_radius=8)

    title_font = get_font(15, True)
    title_surface = title_font.render(str(title), True, GODOT_TEXT)
    screen.blit(title_surface, (modal_rect.x + 16, modal_rect.y + 12))

    close_rect = pygame.Rect(modal_rect.right - 34, modal_rect.y + 10, 24, 24)
    buttons = [draw_editor_button(screen, close_rect, "X", close_action, compact=True)]

    list_rect = pygame.Rect(
        modal_rect.x + 14,
        modal_rect.y + 48,
        modal_rect.w - 28,
        modal_rect.h - 64,
    )

    pygame.draw.rect(screen, GODOT_FIELD, list_rect, border_radius=4)
    pygame.draw.rect(screen, GODOT_BORDER, list_rect, 1, border_radius=4)

    if len(items) == 0:
        draw_row_text(screen, empty_message, list_rect.x + 12, list_rect.y + 12, GODOT_MUTED)
        return buttons

    previous_clip = screen.get_clip()
    screen.set_clip(list_rect)

    y = list_rect.y - scroll_y
    for item in items:
        row = pygame.Rect(list_rect.x + 4, y, list_rect.w - 8, row_height)
        if row.bottom >= list_rect.y and row.y <= list_rect.bottom:
            row_buttons = draw_row_callback(screen, row, item)
            buttons.extend(row_buttons)

        y += row_height

    screen.set_clip(previous_clip)

    return buttons


def draw_list_row_background(screen, row):
    pygame.draw.rect(screen, GODOT_FIELD, row, border_radius=3)
    pygame.draw.rect(screen, GODOT_BORDER, row, 1, border_radius=3)


def draw_row_text(screen, text, x, y, color=GODOT_TEXT):
    font = get_font(13)
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))