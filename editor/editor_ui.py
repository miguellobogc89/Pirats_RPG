import pygame

from editor.ui.editor_menu_bar import MENU_BAR_HEIGHT
from editor.ui.editor_status_bar import STATUS_BAR_HEIGHT
from editor.terrain.terrain_palette import TERRAIN_PALETTE
from editor.ui.widgets.section import draw_section_header


PANEL_WIDTH = 320
ROW_HEIGHT = 30
BUTTON_MARGIN = 8

COLOR_PANEL = (38, 41, 46)
COLOR_ROW_HOVER = (55, 59, 66)
COLOR_ROW_ACTIVE = (86, 120, 92)
COLOR_BORDER = (95, 100, 110)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_MUTED = (165, 170, 178)
COLOR_FIELD = (29, 32, 38)
COLOR_FIELD_FOCUS = (74, 109, 160)
COLOR_DANGER = (116, 56, 59)

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
    screen.blit(text, (rect.x + 10, rect.y + (rect.height - text.get_height()) // 2))
    pygame.draw.line(screen, COLOR_BORDER, (rect.x, rect.bottom), (rect.right, rect.bottom))


def draw_small_button(screen, rect, label, action_data, danger=False):
    mouse_pos = pygame.mouse.get_pos()
    color = COLOR_DANGER if danger else (58, 64, 74)

    if rect.collidepoint(mouse_pos):
        color = (72, 80, 92)

    pygame.draw.rect(screen, color, rect, border_radius=3)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=3)

    font = pygame.font.SysFont("segoeui", 12)
    surface = font.render(str(label), True, COLOR_TEXT)
    screen.blit(
        surface,
        (
            rect.centerx - surface.get_width() // 2,
            rect.centery - surface.get_height() // 2,
        ),
    )

    button_data = {"rect": rect}
    button_data.update(action_data)
    return button_data


def draw_property_input(screen, rect, value, focused=False):
    pygame.draw.rect(screen, COLOR_FIELD, rect, border_radius=2)
    border_color = COLOR_FIELD_FOCUS if focused else COLOR_BORDER
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=2)

    font = pygame.font.SysFont("consolas", 12)
    text = str(value)
    text_surface = font.render(text, True, COLOR_TEXT)
    clip = rect.inflate(-8, -4)
    previous_clip = screen.get_clip()
    screen.set_clip(clip)
    screen.blit(text_surface, (rect.x + 4, rect.y + 5))
    screen.set_clip(previous_clip)


def get_object_buttons(object_definitions=None):
    if not object_definitions:
        return []

    return [
        (object_type, object_type.replace("_", " ").title())
        for object_type in sorted(object_definitions)
        if object_type not in NON_PLACEABLE_OBJECT_TYPES
    ]


def add_row(buttons, screen, x, y, width, label, action_data, active=False):
    rect = pygame.Rect(x, y, width, ROW_HEIGHT)
    draw_nav_row(screen, rect, label, active)

    button_data = {"rect": rect}
    button_data.update(action_data)
    buttons.append(button_data)
    return y + ROW_HEIGHT


def add_section(buttons, screen, x, y, width, title, section_id, section_state):
    expanded = section_state.get(section_id, True)
    rect = pygame.Rect(x, y, width, 28)
    buttons.append(
        draw_section_header(
            screen,
            rect,
            title,
            expanded,
            "toggle_side_section",
            section_id,
        )
    )
    return y + 28


def draw_editor_side_panel(
    screen,
    mode,
    selected_object_type,
    object_definitions=None,
    selected_area=None,
    selected_terrain_id=None,
    side_panel_scroll_y=0,
    section_state=None,
    selected_scene_object=None,
    property_edit=None,
):
    section_state = section_state or {}
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

    y = add_section(buttons, screen, x, y, width, "Objetos", "objects", section_state)
    if section_state.get("objects", True):
        y = add_row(buttons, screen, x, y, width, "+ Nuevo objeto", {"action": "object_new"})

        if selected_object_type is not None:
            y = add_row(
                buttons,
                screen,
                x,
                y,
                width,
                "Editar seleccionado",
                {"action": "object_edit_selected"},
            )
            y = add_row(
                buttons,
                screen,
                x,
                y,
                width,
                "Eliminar seleccionado",
                {"action": "object_delete_selected"},
            )

        y += 10
        for object_type, label in get_object_buttons(object_definitions):
            y = add_row(
                buttons,
                screen,
                x,
                y,
                width,
                label,
                {"action": "select_object", "object_type": object_type},
                mode == "objects" and object_type == selected_object_type,
            )

    y += 18
    y = add_section(
        buttons,
        screen,
        x,
        y,
        width,
        "Objeto seleccionado",
        "object_instance",
        section_state,
    )
    if section_state.get("object_instance", True):
        if selected_scene_object is None:
            draw_text(screen, font, "Sin objeto seleccionado", x, y + 6, COLOR_TEXT_MUTED)
            y += 30
            draw_text(
                screen,
                font,
                "Esc cancela herramienta; click en objeto para editar.",
                x,
                y + 2,
                COLOR_TEXT_MUTED,
            )
            y += 34
        else:
            draw_text(screen, font, f"ID: {selected_scene_object.get('id', '-')}", x, y, COLOR_TEXT_MUTED)
            y += 20
            draw_text(screen, font, f"Tipo: {selected_scene_object.get('type', '-')}", x, y, COLOR_TEXT_MUTED)
            y += 20
            draw_text(screen, font, f"Celda: {selected_scene_object.get('cell', '-')}", x, y, COLOR_TEXT_MUTED)
            y += 28
            y = add_row(
                buttons,
                screen,
                x,
                y,
                width,
                "+ AÃ±adir propiedad",
                {"action": "instance_property_add"},
            )
            y += 6

            properties = selected_scene_object.get("properties", {})
            if not isinstance(properties, dict):
                properties = {}

            if not properties:
                draw_text(screen, font, "Sin propiedades", x, y + 6, COLOR_TEXT_MUTED)
                y += 30
            else:
                key_width = int(width * 0.42)
                value_width = width - key_width - 38

                for property_key, property_value in properties.items():
                    edit_key = (
                        property_edit
                        and property_edit.get("kind") == "key"
                        and property_edit.get("property_key") == property_key
                    )
                    edit_value = (
                        property_edit
                        and property_edit.get("kind") == "value"
                        and property_edit.get("property_key") == property_key
                    )

                    key_value = property_key
                    value_value = property_value

                    if edit_key:
                        key_value = property_edit.get("text", property_key)

                    if edit_value:
                        value_value = property_edit.get("text", property_value)

                    key_rect = pygame.Rect(x, y, key_width, 26)
                    value_rect = pygame.Rect(x + key_width + 6, y, value_width, 26)
                    delete_rect = pygame.Rect(value_rect.right + 6, y, 26, 26)

                    draw_property_input(screen, key_rect, key_value, edit_key)
                    draw_property_input(screen, value_rect, value_value, edit_value)
                    buttons.append({
                        "rect": key_rect,
                        "action": "instance_property_focus_key",
                        "property_key": property_key,
                    })
                    buttons.append({
                        "rect": value_rect,
                        "action": "instance_property_focus_value",
                        "property_key": property_key,
                    })
                    buttons.append(
                        draw_small_button(
                            screen,
                            delete_rect,
                            "X",
                            {
                                "action": "instance_property_delete",
                                "property_key": property_key,
                            },
                            danger=True,
                        )
                    )
                    y += 30

    y += 18
    y = add_section(buttons, screen, x, y, width, "Terreno", "terrain", section_state)
    if section_state.get("terrain", True):
        for terrain_id, terrain_data in TERRAIN_PALETTE.items():
            terrain_name = terrain_data.get("name", terrain_id)
            y = add_row(
                buttons,
                screen,
                x,
                y,
                width,
                terrain_name,
                {"action": "select_terrain", "terrain_id": terrain_id},
                mode == "terrain" and terrain_id == selected_terrain_id,
            )

    y += 18
    y = add_section(buttons, screen, x, y, width, "Colisiones", "collisions", section_state)
    if section_state.get("collisions", True):
        y = add_row(
            buttons,
            screen,
            x,
            y,
            width,
            "Pintar colisiones",
            {"action": "mode_collisions"},
            mode == "collisions",
        )

    y += 18
    y = add_section(buttons, screen, x, y, width, "Navegacion", "navigation", section_state)
    if section_state.get("navigation", True):
        y = add_row(
            buttons,
            screen,
            x,
            y,
            width,
            "Entradas / Spawns",
            {"action": "mode_spawns"},
            mode == "spawns",
        )
        y = add_row(
            buttons,
            screen,
            x,
            y,
            width,
            "Salidas / Exits",
            {"action": "mode_exits"},
            mode == "exits",
        )
        y = add_row(buttons, screen, x, y, width, "Relaciones", {"action": "open_relations_dialog"})

    y += 18
    y = add_section(buttons, screen, x, y, width, "Area activa", "active_area", section_state)
    if section_state.get("active_area", True):
        if selected_area is None:
            draw_text(screen, font, "Sin area seleccionada", x, y + 6, COLOR_TEXT_MUTED)
            y += 30
        else:
            draw_text(screen, font, f"ID: {selected_area.get('id', '-')}", x, y, COLOR_TEXT_MUTED)
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
            y = add_row(buttons, screen, x, y, width, "Editar nombre", {"action": "edit_area_name"})

    screen.set_clip(previous_clip)

    content_height = y + side_panel_scroll_y - MENU_BAR_HEIGHT
    visible_height = panel_rect.height
    max_scroll = max(0, content_height - visible_height)

    if content_height > visible_height:
        scrollbar_height = max(30, int(visible_height * visible_height / content_height))
        scrollbar_y = MENU_BAR_HEIGHT + int(
            (visible_height - scrollbar_height) * side_panel_scroll_y / max(1, max_scroll)
        )
        scrollbar_rect = pygame.Rect(panel_rect.right - 6, scrollbar_y, 4, scrollbar_height)
        pygame.draw.rect(screen, COLOR_BORDER, scrollbar_rect, border_radius=2)

    return {
        "buttons": buttons,
        "max_scroll": max_scroll,
    }


def get_clicked_panel_action(mouse_pos, buttons):
    for button in buttons:
        if button["rect"].collidepoint(mouse_pos):
            return button

    return None

