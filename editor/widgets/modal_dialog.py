import pygame

from editor.widgets.editor_button import draw_editor_button
from editor.widgets.inspector_panel import (
    GODOT_BG,
    GODOT_BORDER,
    GODOT_FIELD,
    GODOT_MUTED,
    GODOT_TEXT,
    draw_text,
    get_inspector_font,
)


def draw_modal_dialog(
    screen,
    title,
    width=None,
    height=None,
    width_ratio=0.9,
    height_ratio=0.84,
    close_action="object_cancel",
):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (0, 0))

    modal_w = width if width is not None else int(screen.get_width() * width_ratio)
    modal_h = height if height is not None else int(screen.get_height() * height_ratio)
    modal_x = (screen.get_width() - modal_w) // 2
    modal_y = (screen.get_height() - modal_h) // 2
    modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

    pygame.draw.rect(screen, GODOT_BG, modal_rect, border_radius=5)
    pygame.draw.rect(screen, GODOT_BORDER, modal_rect, 1, border_radius=5)

    header_h = 34
    draw_text(screen, title, modal_x + 12, modal_y + 9, GODOT_TEXT, 13, True)
    pygame.draw.line(
        screen,
        GODOT_BORDER,
        (modal_x, modal_y + header_h),
        (modal_x + modal_w, modal_y + header_h),
    )

    close_rect = pygame.Rect(modal_rect.right - 30, modal_rect.y + 6, 22, 22)
    mouse_pos = pygame.mouse.get_pos()
    close_bg = (55, 59, 68) if close_rect.collidepoint(mouse_pos) else (40, 43, 50)
    pygame.draw.rect(screen, close_bg, close_rect, border_radius=3)
    pygame.draw.rect(screen, GODOT_BORDER, close_rect, 1, border_radius=3)
    draw_text(screen, "X", close_rect.x + 7, close_rect.y + 3, GODOT_TEXT, 12, True)

    content_rect = pygame.Rect(
        modal_rect.x + 10,
        modal_rect.y + header_h + 10,
        modal_rect.w - 20,
        modal_rect.h - header_h - 20,
    )

    return {
        "rect": modal_rect,
        "content_rect": content_rect,
        "close_button": {
            "rect": close_rect,
            "action": close_action,
        },
    }


def wrap_text(text, max_width, font_size=13, bold=False):
    font = get_inspector_font(font_size, bold)
    lines = []

    for raw_line in str(text).splitlines() or [""]:
        words = raw_line.split(" ")
        current_line = ""

        for word in words:
            test_line = word if not current_line else f"{current_line} {word}"

            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

    return lines


def draw_wrapped_text(
    screen,
    text,
    rect,
    color=GODOT_TEXT,
    font_size=13,
    bold=False,
    line_gap=5,
):
    lines = wrap_text(text, rect.w, font_size, bold)
    line_height = font_size + line_gap

    for index, line in enumerate(lines):
        y = rect.y + index * line_height

        if y + line_height > rect.bottom:
            break

        draw_text(screen, line, rect.x, y, color, font_size, bold)

    return len(lines) * line_height


def draw_modal_footer_buttons(screen, modal_rect, button_specs, button_width=112):
    buttons = []
    gap = 10
    button_h = 28
    total_w = len(button_specs) * button_width + max(0, len(button_specs) - 1) * gap
    x = modal_rect.centerx - total_w // 2
    y = modal_rect.bottom - 44

    for index, spec in enumerate(button_specs):
        label = spec["label"]
        action = spec["action"]
        danger = spec.get("danger", False)
        rect = pygame.Rect(x + index * (button_width + gap), y, button_width, button_h)
        buttons.append(
            draw_editor_button(
                screen,
                rect,
                label,
                action,
                compact=True,
                danger=danger,
            )
        )

    return buttons


def draw_modal_text_input(screen, rect, value, focused=True):
    pygame.draw.rect(screen, GODOT_FIELD, rect, border_radius=3)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=3)

    display_text = str(value)
    if focused and pygame.time.get_ticks() // 500 % 2 == 0:
        display_text += "|"

    font = get_inspector_font(13)
    previous_clip = screen.get_clip()
    clip_rect = rect.inflate(-12, -6)
    screen.set_clip(clip_rect)
    text_surface = font.render(display_text, True, GODOT_TEXT)
    screen.blit(text_surface, (rect.x + 8, rect.y + 8))
    screen.set_clip(previous_clip)


def draw_modal_label(screen, text, x, y):
    draw_text(screen, text, x, y, GODOT_MUTED, 13)
