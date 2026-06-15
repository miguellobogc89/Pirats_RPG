import pygame


COLOR_BG = (28, 31, 36)
COLOR_BORDER = (95, 100, 110)
COLOR_TEXT = (230, 230, 230)
COLOR_MUTED = (165, 170, 178)
COLOR_BUTTON = (58, 64, 74)
COLOR_BUTTON_HOVER = (72, 80, 92)


def draw_number_input(screen, x, y, label, value, minus_action, plus_action):
    font = pygame.font.SysFont("consolas", 14)

    label_surface = font.render(str(label), True, COLOR_MUTED)
    screen.blit(label_surface, (x, y + 7))

    minus_rect = pygame.Rect(x + 28, y, 26, 28)
    value_rect = pygame.Rect(x + 58, y, 42, 28)
    plus_rect = pygame.Rect(x + 104, y, 26, 28)

    buttons = []

    buttons.append(draw_small_button(screen, minus_rect, "-", minus_action))

    pygame.draw.rect(screen, COLOR_BG, value_rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_BORDER, value_rect, 1, border_radius=4)

    value_surface = font.render(str(value), True, COLOR_TEXT)
    screen.blit(
        value_surface,
        (
            value_rect.centerx - value_surface.get_width() // 2,
            value_rect.centery - value_surface.get_height() // 2,
        ),
    )

    buttons.append(draw_small_button(screen, plus_rect, "+", plus_action))

    return buttons


def draw_small_button(screen, rect, label, action):
    mouse_pos = pygame.mouse.get_pos()

    color = COLOR_BUTTON

    if rect.collidepoint(mouse_pos):
        color = COLOR_BUTTON_HOVER

    pygame.draw.rect(screen, color, rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=4)

    font = pygame.font.SysFont("consolas", 14)
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