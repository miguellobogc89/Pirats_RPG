import pygame

from editor.widgets.inspector_panel import (
    GODOT_BG,
    GODOT_BORDER,
    GODOT_TEXT,
    draw_text,
)


def draw_modal_dialog(screen, title, width_ratio=0.9, height_ratio=0.84):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (0, 0))

    modal_w = int(screen.get_width() * width_ratio)
    modal_h = int(screen.get_height() * height_ratio)
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
            "action": "object_cancel",
        },
    }
