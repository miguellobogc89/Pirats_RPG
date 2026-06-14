import pygame

from editor.ui.editor_menu_bar import MENU_BAR_HEIGHT
from editor.ui.editor_status_bar import STATUS_BAR_HEIGHT

PANEL_WIDTH = 260
ROW_HEIGHT = 30
BUTTON_MARGIN = 8

COLOR_PANEL = (38, 41, 46)
COLOR_ROW_HOVER = (55, 59, 66)
COLOR_ROW_ACTIVE = (86, 120, 92)
COLOR_BORDER = (95, 100, 110)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_MUTED = (165, 170, 178)

NON_PLACEABLE_OBJECT_TYPES = {"player"}


def draw_text(screen, font, text, x, y, color=COLOR_TEXT):
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))


def draw_nav_row(screen, rect, label, active=False):
    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, COLOR_ROW_HOVER, rect)

    if active:
        pygame.draw.rect(screen, COLOR_ROW_ACTIVE, rect)

    font = pygame.font.SysFont("consolas", 15)
    text = font.render(label, True, COLOR_TEXT)

    screen.blit(
        text,
        (
            rect.x + 10,
            rect.y + (rect.height - text.get_height()) // 2,
        ),
    )

    pygame.draw.line(
        screen,
        COLOR_BORDER,
        (rect.x, rect.bottom),
        (rect.right, rect.bottom),
    )


def get_object_buttons(object_definitions=None):
    if not object_definitions:
        return []

    return [
        (object_type, object_type.replace("_", " ").title())
        for object_type in sorted(object_definitions)
        if object_type not in NON_PLACEABLE_OBJECT_TYPES
    ]


def draw_section_title(screen, font, text, x, y, width):
    draw_text(screen, font, text.upper(), x, y, COLOR_TEXT_MUTED)

    pygame.draw.line(
        screen,
        COLOR_BORDER,
        (x, y + 22),
        (x + width, y + 22),
    )


def draw_editor_side_panel(
    screen,
    mode,
    selected_object_type,
    object_definitions=None,
    selected_area=None,
):
    font = pygame.font.SysFont("consolas", 14)

    screen_width = screen.get_width()
    panel_x = screen_width - PANEL_WIDTH

    panel_rect = pygame.Rect(
        panel_x,
        MENU_BAR_HEIGHT,
        PANEL_WIDTH,
        screen.get_height() - MENU_BAR_HEIGHT - STATUS_BAR_HEIGHT,
    )

    pygame.draw.rect(screen, COLOR_PANEL, panel_rect)

    pygame.draw.line(
        screen,
        COLOR_BORDER,
        (panel_x, MENU_BAR_HEIGHT),
        (panel_x, screen.get_height() - STATUS_BAR_HEIGHT),
    )

    buttons = []

    x = panel_x + BUTTON_MARGIN
    y = MENU_BAR_HEIGHT + 12
    width = PANEL_WIDTH - BUTTON_MARGIN * 2

    draw_section_title(screen, font, "Insertar objetos", x, y, width)
    y += 28

    for object_type, label in get_object_buttons(object_definitions):
        rect = pygame.Rect(x, y, width, ROW_HEIGHT)

        draw_nav_row(
            screen,
            rect,
            label,
            mode == "objects" and object_type == selected_object_type,
        )

        buttons.append({
            "rect": rect,
            "action": "select_object",
            "object_type": object_type,
        })

        y += ROW_HEIGHT

    y += 18

    draw_section_title(screen, font, "Colisiones", x, y, width)
    y += 28

    collision_rect = pygame.Rect(x, y, width, ROW_HEIGHT)

    draw_nav_row(
        screen,
        collision_rect,
        "Pintar colisiones",
        mode == "collisions",
    )

    buttons.append({
        "rect": collision_rect,
        "action": "mode_collisions",
    })

    y += ROW_HEIGHT + 18

    draw_section_title(screen, font, "Navegación", x, y, width)
    y += 28

    spawn_rect = pygame.Rect(x, y, width, ROW_HEIGHT)

    draw_nav_row(
        screen,
        spawn_rect,
        "Entradas / Spawns",
        mode == "spawns",
    )

    buttons.append({
        "rect": spawn_rect,
        "action": "mode_spawns",
    })

    y += ROW_HEIGHT

    exit_rect = pygame.Rect(x, y, width, ROW_HEIGHT)

    draw_nav_row(
        screen,
        exit_rect,
        "Salidas / Exits",
        mode == "exits",
    )

    buttons.append({
        "rect": exit_rect,
        "action": "mode_exits",
    })

    y += ROW_HEIGHT

    relations_rect = pygame.Rect(x, y, width, ROW_HEIGHT)

    draw_nav_row(
        screen,
        relations_rect,
        "Relaciones",
        False,
    )

    buttons.append({
        "rect": relations_rect,
        "action": "open_relations_dialog",
    })

    y += ROW_HEIGHT + 18

    draw_section_title(screen, font, "Área activa", x, y, width)
    y += 28

    if selected_area is None:

        draw_text(
            screen,
            font,
            "Sin área seleccionada",
            x,
            y,
            COLOR_TEXT_MUTED,
        )

        y += 24

    else:

        draw_text(
            screen,
            font,
            f"ID: {selected_area.get('id', '-')}",
            x,
            y,
            COLOR_TEXT_MUTED,
        )

        y += 20

        draw_text(
            screen,
            font,
            f"Nombre: {selected_area.get('name', '-')}",
            x,
            y,
            COLOR_TEXT_MUTED,
        )

        y += 24

        edit_rect = pygame.Rect(
            x,
            y,
            width,
            ROW_HEIGHT,
        )

        draw_nav_row(
            screen,
            edit_rect,
            "Editar nombre",
            False,
        )

        buttons.append({
            "rect": edit_rect,
            "action": "edit_area_name",
        })

        y += ROW_HEIGHT

    y += 18

    draw_section_title(screen, font, "Terreno", x, y, width)
    y += 28

    terrain_rect = pygame.Rect(
        x,
        y,
        width,
        ROW_HEIGHT,
    )

    draw_nav_row(
        screen,
        terrain_rect,
        "Grass",
        False,
    )

    buttons.append({
        "rect": terrain_rect,
        "action": "terrain_grass",
    })

    return buttons


def get_clicked_panel_action(mouse_pos, buttons):
    for button in buttons:
        if button["rect"].collidepoint(mouse_pos):
            return button

    return None