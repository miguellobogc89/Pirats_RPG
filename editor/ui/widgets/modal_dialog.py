import pygame

from editor.ui.widgets.editor_button import draw_editor_button
from editor.ui.widgets.inspector_panel import (
    GODOT_BORDER,
    GODOT_FIELD,
    GODOT_PANEL,
    GODOT_TEXT,
    GODOT_MUTED,
    get_font,
)


def draw_modal_dialog(screen, title, width=420, height=220, close_action=None):
    screen_rect = screen.get_rect()
    rect = pygame.Rect(0, 0, width, height)
    rect.center = screen_rect.center

    pygame.draw.rect(screen, GODOT_PANEL, rect, border_radius=8)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=8)

    title_font = get_font(15, True)
    title_surface = title_font.render(str(title), True, GODOT_TEXT)
    screen.blit(title_surface, (rect.x + 16, rect.y + 12))

    close_rect = pygame.Rect(rect.right - 34, rect.y + 10, 24, 24)
    close_button = draw_editor_button(screen, close_rect, "X", close_action, compact=True)

    content_rect = pygame.Rect(rect.x + 14, rect.y + 44, rect.w - 28, rect.h - 92)

    return {
        "rect": rect,
        "content_rect": content_rect,
        "close_button": close_button,
    }


def draw_modal_label(screen, text, x, y):
    font = get_font(13)
    surface = font.render(str(text), True, GODOT_MUTED)
    screen.blit(surface, (x, y))


def draw_modal_text_input(screen, rect, value):
    pygame.draw.rect(screen, GODOT_FIELD, rect, border_radius=4)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=4)

    font = get_font(13)
    surface = font.render(str(value), True, GODOT_TEXT)
    screen.blit(surface, (rect.x + 8, rect.y + 8))


def draw_modal_footer_buttons(screen, modal_rect, button_defs, button_width=100):
    buttons = []
    gap = 8
    button_h = 28

    total_w = len(button_defs) * button_width + max(0, len(button_defs) - 1) * gap
    x = modal_rect.right - total_w - 16
    y = modal_rect.bottom - button_h - 14

    for button_def in button_defs:
        rect = pygame.Rect(x, y, button_width, button_h)
        button = draw_editor_button(
            screen,
            rect,
            button_def["label"],
            button_def["action"],
            compact=True,
            danger=button_def.get("danger", False),
        )
        buttons.append(button)
        x += button_width + gap

    return buttons


def draw_wrapped_text(screen, text, rect, color=GODOT_TEXT, size=13):
    font = get_font(size)
    words = str(text).split(" ")
    line = ""
    y = rect.y

    for word in words:
        test_line = word if line == "" else line + " " + word
        test_surface = font.render(test_line, True, color)

        if test_surface.get_width() > rect.w and line != "":
            surface = font.render(line, True, color)
            screen.blit(surface, (rect.x, y))
            y += surface.get_height() + 4
            line = word
        else:
            line = test_line

    if line != "":
        surface = font.render(line, True, color)
        screen.blit(surface, (rect.x, y))