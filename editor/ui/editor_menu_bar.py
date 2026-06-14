import pygame

MENU_BAR_HEIGHT = 34

COLOR_BAR = (24, 26, 30)
COLOR_DROPDOWN = (32, 35, 40)
COLOR_HOVER = (55, 59, 66)
COLOR_BORDER = (95, 100, 110)
COLOR_TEXT = (230, 230, 230)


def draw_menu_label(screen, rect, label):
    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, COLOR_HOVER, rect)

    font = pygame.font.SysFont("consolas", 15)
    text = font.render(label, True, COLOR_TEXT)

    screen.blit(
        text,
        (
            rect.x + 10,
            rect.y + (rect.height - text.get_height()) // 2,
        ),
    )


def draw_dropdown_item(screen, rect, label):
    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, COLOR_HOVER, rect)

    font = pygame.font.SysFont("consolas", 15)
    text = font.render(label, True, COLOR_TEXT)

    screen.blit(
        text,
        (
            rect.x + 12,
            rect.y + (rect.height - text.get_height()) // 2,
        ),
    )


def draw_dropdown(screen, x, items):
    y = MENU_BAR_HEIGHT
    width = 190
    item_height = 28

    dropdown_rect = pygame.Rect(
        x,
        y,
        width,
        item_height * len(items),
    )

    pygame.draw.rect(screen, COLOR_DROPDOWN, dropdown_rect)
    pygame.draw.rect(screen, COLOR_BORDER, dropdown_rect, 1)

    buttons = []

    for index, item in enumerate(items):
        label = item[0]
        action = item[1]

        rect = pygame.Rect(
            x,
            y + index * item_height,
            width,
            item_height,
        )

        draw_dropdown_item(screen, rect, label)

        if index > 0:
            pygame.draw.line(
                screen,
                COLOR_BORDER,
                (x, rect.y),
                (x + width, rect.y),
            )

        buttons.append({
            "rect": rect,
            "action": action,
        })

    return buttons


def draw_file_dropdown(screen):
    items = [
        ("Nuevo", "file_new"),
        ("Abrir...", "file_open"),
        ("Guardar", "file_save"),
        ("Guardar como...", "file_save_as"),
        ("Abrir carpeta", "file_open_folder"),
        ("Salir", "file_exit"),
    ]

    return draw_dropdown(screen, 8, items)


def draw_objects_dropdown(screen):
    items = [
        ("Nuevo objeto", "object_new"),
        ("Abrir objeto...", "object_open"),
        ("Guardar objeto", "object_save"),
        ("Guardar objeto como...", "object_save_as"),
    ]

    return draw_dropdown(screen, 164, items)


def draw_editor_menu_bar(screen, active_menu=None):
    pygame.draw.rect(
        screen,
        COLOR_BAR,
        (0, 0, screen.get_width(), MENU_BAR_HEIGHT),
    )

    pygame.draw.line(
        screen,
        COLOR_BORDER,
        (0, MENU_BAR_HEIGHT),
        (screen.get_width(), MENU_BAR_HEIGHT),
    )

    buttons = []

    x = 8
    y = 0
    height = MENU_BAR_HEIGHT

    menu_items = [
        ("Archivo", "menu_file", 82),
        ("Editar", "menu_edit", 74),
        ("Objetos", "menu_objects", 82),
        ("Ajustes", "menu_settings", 86),
    ]

    for label, action, width in menu_items:
        rect = pygame.Rect(x, y, width, height)

        draw_menu_label(screen, rect, label)

        buttons.append({
            "rect": rect,
            "action": action,
        })

        separator_x = rect.right

        pygame.draw.line(
            screen,
            COLOR_BORDER,
            (separator_x, 6),
            (separator_x, MENU_BAR_HEIGHT - 6),
        )

        x += width

    if active_menu == "file":
        buttons.extend(draw_file_dropdown(screen))

    if active_menu == "objects":
        buttons.extend(draw_objects_dropdown(screen))

    return buttons