import pygame


COLOR_OVERLAY = (0, 0, 0)
COLOR_DIALOG = (38, 41, 46)
COLOR_HEADER = (24, 26, 30)
COLOR_BORDER = (95, 100, 110)
COLOR_ROW_HOVER = (55, 59, 66)
COLOR_BUTTON = (58, 64, 74)
COLOR_DANGER = (116, 56, 59)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_MUTED = (165, 170, 178)


def draw_open_object_dialog(screen, object_definitions):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(120)
    overlay.fill(COLOR_OVERLAY)
    screen.blit(overlay, (0, 0))

    dialog_width = 620
    dialog_height = 420
    dialog_x = (screen.get_width() - dialog_width) // 2
    dialog_y = (screen.get_height() - dialog_height) // 2
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

    pygame.draw.rect(screen, COLOR_DIALOG, dialog_rect)
    pygame.draw.rect(screen, COLOR_BORDER, dialog_rect, 1)

    header_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, 38)
    pygame.draw.rect(screen, COLOR_HEADER, header_rect)
    pygame.draw.line(screen, COLOR_BORDER, header_rect.bottomleft, header_rect.bottomright)

    title_font = pygame.font.SysFont("consolas", 17, bold=True)
    text_font = pygame.font.SysFont("consolas", 14)
    title = title_font.render("Abrir objeto", True, COLOR_TEXT)
    screen.blit(title, (dialog_x + 14, dialog_y + 10))

    buttons = []
    list_x = dialog_x + 18
    list_y = dialog_y + 58
    list_w = dialog_width - 36
    row_h = 34
    footer_top = dialog_y + dialog_height - 54

    items = sorted(object_definitions.items())

    if not items:
        empty_text = text_font.render("No hay objetos guardados.", True, COLOR_TEXT_MUTED)
        screen.blit(empty_text, (list_x, list_y))
    else:
        for index, (object_id, object_data) in enumerate(items):
            row = pygame.Rect(list_x, list_y + index * row_h, list_w, row_h)

            if row.bottom > footer_top - 8:
                break

            if row.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, COLOR_ROW_HOVER, row)

            pygame.draw.line(screen, COLOR_BORDER, row.bottomleft, row.bottomright)

            name = object_data.get("name", object_id)
            category = object_data.get("category", "other")
            label = f"{name}  ({object_id})  [{category}]"
            text = text_font.render(label, True, COLOR_TEXT)
            screen.blit(text, (row.x + 8, row.y + 9))

            open_rect = pygame.Rect(row.right - 150, row.y + 5, 66, 24)
            delete_rect = pygame.Rect(row.right - 76, row.y + 5, 66, 24)
            buttons.append(draw_dialog_button(screen, open_rect, "Abrir", {
                "action": "open_object_select",
                "object_id": object_id,
            }))
            buttons.append(draw_dialog_button(screen, delete_rect, "Eliminar", {
                "action": "open_object_delete",
                "object_id": object_id,
            }, danger=True))

    cancel_rect = pygame.Rect(dialog_x + dialog_width - 138, dialog_y + dialog_height - 42, 120, 28)
    buttons.append(draw_dialog_button(screen, cancel_rect, "Cancelar", {"action": "open_object_cancel"}))
    return buttons


def draw_dialog_button(screen, rect, label, action_data, danger=False):
    color = COLOR_DANGER if danger else COLOR_BUTTON

    if rect.collidepoint(pygame.mouse.get_pos()):
        color = COLOR_ROW_HOVER

    pygame.draw.rect(screen, color, rect, border_radius=3)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=3)

    font = pygame.font.SysFont("consolas", 13)
    text = font.render(label, True, COLOR_TEXT)
    screen.blit(
        text,
        (
            rect.centerx - text.get_width() // 2,
            rect.centery - text.get_height() // 2,
        ),
    )

    button = {"rect": rect}
    button.update(action_data)
    return button
