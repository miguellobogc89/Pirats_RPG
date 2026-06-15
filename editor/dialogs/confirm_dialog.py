import pygame

from editor.widgets.editor_button import draw_editor_button
from editor.widgets.inspector_panel import GODOT_BG, GODOT_BORDER, GODOT_TEXT, draw_text


def draw_confirm_dialog(screen, title, message, confirm_action, cancel_action):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    rect = pygame.Rect(0, 0, 420, 170)
    rect.center = screen.get_rect().center
    pygame.draw.rect(screen, GODOT_BG, rect, border_radius=5)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=5)

    draw_text(screen, title, rect.x + 18, rect.y + 16, GODOT_TEXT, 14, True)
    draw_text(screen, message, rect.x + 18, rect.y + 56, GODOT_TEXT, 13)

    buttons = []
    buttons.append(
        draw_editor_button(
            screen,
            pygame.Rect(rect.right - 210, rect.bottom - 44, 92, 28),
            "Eliminar",
            confirm_action,
            compact=True,
            danger=True,
        )
    )
    buttons.append(
        draw_editor_button(
            screen,
            pygame.Rect(rect.right - 108, rect.bottom - 44, 92, 28),
            "Cancelar",
            cancel_action,
            compact=True,
        )
    )
    return buttons
