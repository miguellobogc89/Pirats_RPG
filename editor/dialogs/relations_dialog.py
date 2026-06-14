import pygame

COLOR_OVERLAY = (0, 0, 0)
COLOR_DIALOG = (38, 41, 46)
COLOR_HEADER = (24, 26, 30)
COLOR_BORDER = (95, 100, 110)
COLOR_ROW_HOVER = (55, 59, 66)
COLOR_ROW_ACTIVE = (86, 120, 92)
COLOR_BUTTON = (55, 59, 66)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_MUTED = (165, 170, 178)


def draw_row(screen, rect, label, active):
    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, COLOR_ROW_HOVER, rect)

    if active:
        pygame.draw.rect(screen, COLOR_ROW_ACTIVE, rect)

    pygame.draw.line(screen, COLOR_BORDER, (rect.x, rect.bottom), (rect.right, rect.bottom))

    font = pygame.font.SysFont("consolas", 14)
    text = font.render(label, True, COLOR_TEXT)
    screen.blit(text, (rect.x + 8, rect.y + 7))


def draw_button(screen, rect, label):
    mouse_pos = pygame.mouse.get_pos()

    color = COLOR_BUTTON
    if rect.collidepoint(mouse_pos):
        color = COLOR_ROW_HOVER

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


def draw_relations_dialog(
    screen,
    scene_data,
    relation_targets,
    selected_exit_id,
    selected_target_key,
):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(120)
    overlay.fill(COLOR_OVERLAY)
    screen.blit(overlay, (0, 0))

    dialog_width = 760
    dialog_height = 460
    dialog_x = (screen.get_width() - dialog_width) // 2
    dialog_y = (screen.get_height() - dialog_height) // 2

    pygame.draw.rect(screen, COLOR_DIALOG, (dialog_x, dialog_y, dialog_width, dialog_height))
    pygame.draw.rect(screen, COLOR_BORDER, (dialog_x, dialog_y, dialog_width, dialog_height), 1)

    pygame.draw.rect(screen, COLOR_HEADER, (dialog_x, dialog_y, dialog_width, 38))

    title_font = pygame.font.SysFont("consolas", 17, bold=True)
    font = pygame.font.SysFont("consolas", 14)

    screen.blit(title_font.render("Relaciones de escena", True, COLOR_TEXT), (dialog_x + 14, dialog_y + 10))

    left_x = dialog_x + 20
    right_x = dialog_x + 390
    list_y = dialog_y + 72
    col_w = 330
    row_h = 30

    screen.blit(font.render("Salidas de esta escena", True, COLOR_TEXT_MUTED), (left_x, dialog_y + 50))
    screen.blit(font.render("Entradas disponibles", True, COLOR_TEXT_MUTED), (right_x, dialog_y + 50))

    buttons = []

    exits = scene_data.get("exits", [])

    for index, exit_data in enumerate(exits):
        rect = pygame.Rect(left_x, list_y + index * row_h, col_w, row_h)

        if rect.bottom > dialog_y + dialog_height - 66:
            break

        active = exit_data["id"] == selected_exit_id
        label = f"{exit_data.get('name', exit_data['id'])} ({exit_data['id']})"

        draw_row(screen, rect, label, active)

        buttons.append({
            "rect": rect,
            "action": "relation_select_exit",
            "exit_id": exit_data["id"],
        })

    for index, target_data in enumerate(relation_targets):
        rect = pygame.Rect(right_x, list_y + index * row_h, col_w, row_h)

        if rect.bottom > dialog_y + dialog_height - 66:
            break

        target_key = f"{target_data['scene_id']}::{target_data['spawn_id']}"
        active = target_key == selected_target_key

        label = (
            f"{target_data['scene_name']} / "
            f"{target_data['spawn_name']} ({target_data['spawn_id']})"
        )

        draw_row(screen, rect, label, active)

        buttons.append({
            "rect": rect,
            "action": "relation_select_target",
            "target_key": target_key,
            "target_scene_id": target_data["scene_id"],
            "target_spawn_id": target_data["spawn_id"],
        })

    confirm_rect = pygame.Rect(dialog_x + dialog_width - 280, dialog_y + dialog_height - 44, 120, 30)
    cancel_rect = pygame.Rect(dialog_x + dialog_width - 146, dialog_y + dialog_height - 44, 120, 30)

    draw_button(screen, confirm_rect, "Vincular")
    draw_button(screen, cancel_rect, "Cerrar")

    buttons.append({
        "rect": confirm_rect,
        "action": "relation_confirm",
    })

    buttons.append({
        "rect": cancel_rect,
        "action": "relation_cancel",
    })

    return buttons