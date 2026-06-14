import pygame

from editor.ui.editor_menu_bar import MENU_BAR_HEIGHT
from editor.ui.editor_status_bar import STATUS_BAR_HEIGHT
from editor.terrain.terrain_palette import TERRAIN_PALETTE

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


def add_row(buttons, screen, x, y, width, label, action_data, active=False):
    rect = pygame.Rect(x, y, width, ROW_HEIGHT)

    draw_nav_row(
        screen,
        rect,
        label,
        active,
    )

    button_data = {
        "rect": rect,
    }

    button_data.update(action_data)
    buttons.append(button_data)

    return y + ROW_HEIGHT


def draw_editor_side_panel(
    screen,
    mode,
    selected_object_type,
    object_definitions=None,
    selected_area=None,
    selected_terrain_id=None,
    side_panel_scroll_y=0,
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

    previous_clip = screen.get_clip()
    screen.set_clip(panel_rect)

    buttons = []

    x = panel_x + BUTTON_MARGIN
    y = MENU_BAR_HEIGHT + 12 - side_panel_scroll_y
    width = PANEL_WIDTH - BUTTON_MARGIN * 2

    draw_section_title(screen, font, "Insertar objetos", x, y, width)
    y += 28

    for object_type, label in get_object_buttons(object_definitions):
        y = add_row(
            buttons,
            screen,
            x,
            y,
            width,
            label,
            {
                "action": "select_object",
                "object_type": object_type,
            },
            mode == "objects" and object_type == selected_object_type,
        )

    y += 18

    draw_section_title(screen, font, "Terreno", x, y, width)
    y += 28

    for terrain_id, terrain_data in TERRAIN_PALETTE.items():
        terrain_name = terrain_data.get("name", terrain_id)
        y = add_row(
            buttons,
            screen,
            x,
            y,
            width,
            terrain_name,
            {
                "action": "select_terrain",
                "terrain_id": terrain_id,
            },
            mode == "terrain" and terrain_id == selected_terrain_id,
        )

    y += 18

    draw_section_title(screen, font, "Colisiones", x, y, width)
    y += 28

    y = add_row(
        buttons,
        screen,
        x,
        y,
        width,
        "Pintar colisiones",
        {
            "action": "mode_collisions",
        },
        mode == "collisions",
    )

    y += 18

    draw_section_title(screen, font, "Navegación", x, y, width)
    y += 28

    y = add_row(
        buttons,
        screen,
        x,
        y,
        width,
        "Entradas / Spawns",
        {
            "action": "mode_spawns",
        },
        mode == "spawns",
    )

    y = add_row(
        buttons,
        screen,
        x,
        y,
        width,
        "Salidas / Exits",
        {
            "action": "mode_exits",
        },
        mode == "exits",
    )

    y = add_row(
        buttons,
        screen,
        x,
        y,
        width,
        "Relaciones",
        {
            "action": "open_relations_dialog",
        },
        False,
    )

    y += 18

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

        y = add_row(
            buttons,
            screen,
            x,
            y,
            width,
            "Editar nombre",
            {
                "action": "edit_area_name",
            },
            False,
        )

    screen.set_clip(previous_clip)

    content_height = y + side_panel_scroll_y - MENU_BAR_HEIGHT
    visible_height = panel_rect.height

    if content_height > visible_height:
        scrollbar_height = max(30, int(visible_height * visible_height / content_height))
        max_scroll = max(1, content_height - visible_height)
        scrollbar_y = MENU_BAR_HEIGHT + int(
            (visible_height - scrollbar_height) * side_panel_scroll_y / max_scroll
        )

        scrollbar_rect = pygame.Rect(
            panel_rect.right - 6,
            scrollbar_y,
            4,
            scrollbar_height,
        )

        pygame.draw.rect(screen, COLOR_BORDER, scrollbar_rect, border_radius=2)

    return buttons


def get_clicked_panel_action(mouse_pos, buttons):
    for button in buttons:
        if button["rect"].collidepoint(mouse_pos):
            return button

    return None