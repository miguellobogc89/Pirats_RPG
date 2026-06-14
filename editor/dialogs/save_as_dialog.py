import pygame

COLOR_OVERLAY = (0, 0, 0)
COLOR_DIALOG = (38, 41, 46)
COLOR_HEADER = (24, 26, 30)
COLOR_BORDER = (95, 100, 110)
COLOR_BUTTON = (55, 59, 66)
COLOR_BUTTON_HOVER = (68, 73, 82)
COLOR_INPUT = (24, 26, 30)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_MUTED = (165, 170, 178)


def draw_button(screen, rect, label):
    mouse_pos = pygame.mouse.get_pos()

    color = COLOR_BUTTON
    if rect.collidepoint(mouse_pos):
        color = COLOR_BUTTON_HOVER

    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 1)

    font = pygame.font.SysFont("consolas", 15)
    text = font.render(label, True, COLOR_TEXT)

    screen.blit(
        text,
        (
            rect.x + (rect.width - text.get_width()) // 2,
            rect.y + (rect.height - text.get_height()) // 2,
        ),
    )


def draw_save_as_dialog(screen, text_value):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(120)
    overlay.fill(COLOR_OVERLAY)
    screen.blit(overlay, (0, 0))

    dialog_width = 430
    dialog_height = 210

    dialog_x = (screen.get_width() - dialog_width) // 2
    dialog_y = (screen.get_height() - dialog_height) // 2

    dialog_rect = pygame.Rect(
        dialog_x,
        dialog_y,
        dialog_width,
        dialog_height,
    )

    pygame.draw.rect(screen, COLOR_DIALOG, dialog_rect)
    pygame.draw.rect(screen, COLOR_BORDER, dialog_rect, 1)

    header_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, 38)
    pygame.draw.rect(screen, COLOR_HEADER, header_rect)
    pygame.draw.line(
        screen,
        COLOR_BORDER,
        (dialog_x, dialog_y + 38),
        (dialog_x + dialog_width, dialog_y + 38),
    )

    title_font = pygame.font.SysFont("consolas", 17, bold=True)
    text_font = pygame.font.SysFont("consolas", 15)

    title = title_font.render("Guardar escena como", True, COLOR_TEXT)
    screen.blit(title, (dialog_x + 14, dialog_y + 10))

    label = text_font.render("Nombre de la escena:", True, COLOR_TEXT_MUTED)
    screen.blit(label, (dialog_x + 22, dialog_y + 66))

    input_rect = pygame.Rect(
        dialog_x + 22,
        dialog_y + 94,
        dialog_width - 44,
        32,
    )

    pygame.draw.rect(screen, COLOR_INPUT, input_rect)
    pygame.draw.rect(screen, COLOR_BORDER, input_rect, 1)

    display_text = text_value
    if pygame.time.get_ticks() // 500 % 2 == 0:
        display_text += "|"

    text_surface = text_font.render(display_text, True, COLOR_TEXT)
    screen.blit(text_surface, (input_rect.x + 8, input_rect.y + 8))

    buttons = []

    button_y = dialog_y + dialog_height - 48
    button_w = 120
    button_h = 30

    items = [
        ("Guardar", "save_as_confirm"),
        ("Cancelar", "save_as_cancel"),
    ]

    total_width = button_w * 2 + 10
    start_x = dialog_x + (dialog_width - total_width) // 2

    for index, item in enumerate(items):
        label = item[0]
        action = item[1]

        rect = pygame.Rect(
            start_x + index * (button_w + 10),
            button_y,
            button_w,
            button_h,
        )

        draw_button(screen, rect, label)

        buttons.append({
            "rect": rect,
            "action": action,
        })

    return buttons