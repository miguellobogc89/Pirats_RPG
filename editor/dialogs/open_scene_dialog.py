import pygame

COLOR_OVERLAY = (0, 0, 0)
COLOR_DIALOG = (38, 41, 46)
COLOR_HEADER = (24, 26, 30)
COLOR_BORDER = (95, 100, 110)
COLOR_ROW_HOVER = (55, 59, 66)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_MUTED = (165, 170, 178)


def draw_open_scene_dialog(screen, saved_scenes):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(120)
    overlay.fill(COLOR_OVERLAY)
    screen.blit(overlay, (0, 0))

    dialog_width = 520
    dialog_height = 360

    dialog_x = (screen.get_width() - dialog_width) // 2
    dialog_y = (screen.get_height() - dialog_height) // 2

    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

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

    title = title_font.render("Abrir escena", True, COLOR_TEXT)
    screen.blit(title, (dialog_x + 14, dialog_y + 10))

    buttons = []

    list_x = dialog_x + 18
    list_y = dialog_y + 58
    list_w = dialog_width - 36
    row_h = 30

    if len(saved_scenes) == 0:
        empty_text = text_font.render("No hay escenas guardadas.", True, COLOR_TEXT_MUTED)
        screen.blit(empty_text, (list_x, list_y))
    else:
        for index, scene_info in enumerate(saved_scenes):
            rect = pygame.Rect(
                list_x,
                list_y + index * row_h,
                list_w,
                row_h,
            )

            if rect.bottom > dialog_y + dialog_height - 58:
                break

            mouse_pos = pygame.mouse.get_pos()

            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, COLOR_ROW_HOVER, rect)

            pygame.draw.line(
                screen,
                COLOR_BORDER,
                (rect.x, rect.bottom),
                (rect.right, rect.bottom),
            )

            label = f"{scene_info['name']}  ({scene_info['id']})"
            text = text_font.render(label, True, COLOR_TEXT)
            screen.blit(text, (rect.x + 8, rect.y + 7))

            buttons.append({
                "rect": rect,
                "action": "open_scene_select",
                "scene_id": scene_info["id"],
            })

    cancel_rect = pygame.Rect(
        dialog_x + dialog_width - 138,
        dialog_y + dialog_height - 42,
        120,
        28,
    )

    mouse_pos = pygame.mouse.get_pos()

    if cancel_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, COLOR_ROW_HOVER, cancel_rect)

    pygame.draw.rect(screen, COLOR_BORDER, cancel_rect, 1)

    cancel_text = text_font.render("Cancelar", True, COLOR_TEXT)
    screen.blit(
        cancel_text,
        (
            cancel_rect.x + (cancel_rect.width - cancel_text.get_width()) // 2,
            cancel_rect.y + (cancel_rect.height - cancel_text.get_height()) // 2,
        ),
    )

    buttons.append({
        "rect": cancel_rect,
        "action": "open_scene_cancel",
    })

    return buttons