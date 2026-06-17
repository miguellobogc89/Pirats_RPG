import pygame


COLOR_BUTTON = (58, 64, 74)
COLOR_BUTTON_HOVER = (72, 80, 92)
COLOR_BORDER = (95, 100, 110)
COLOR_TEXT = (230, 230, 230)
COLOR_DISABLED = (42, 46, 54)
COLOR_DANGER = (116, 56, 59)


def draw_editor_button(screen, rect, label, action, compact=False, danger=False, disabled=False):
    mouse_pos = pygame.mouse.get_pos()

    color = COLOR_BUTTON
    if danger:
        color = COLOR_DANGER

    if disabled:
        color = COLOR_DISABLED

    if rect.collidepoint(mouse_pos) and not disabled:
        color = COLOR_BUTTON_HOVER

    pygame.draw.rect(screen, color, rect, border_radius=3)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=3)

    font_size = 12 if compact else 14
    font = pygame.font.SysFont("segoeui", font_size)
    text = font.render(str(label), True, COLOR_TEXT)

    screen.blit(
        text,
        (
            rect.centerx - text.get_width() // 2,
            rect.centery - text.get_height() // 2,
        ),
    )

    return {
        "rect": rect,
        "action": action,
    }

