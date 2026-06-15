import re
from pathlib import Path

import pygame

from editor.object_editor.object_preview_renderer import draw_object_preview
from editor.widgets.checkbox import draw_checkbox
from editor.widgets.dropdown import draw_dropdown
from editor.widgets.editor_button import draw_editor_button
from editor.widgets.inspector_panel import (
    GODOT_BG,
    GODOT_BORDER,
    GODOT_DANGER,
    GODOT_MUTED,
    GODOT_PANEL,
    GODOT_TEXT,
    draw_inspector_panel,
    draw_text,
)
from editor.widgets.modal_dialog import draw_modal_dialog
from editor.widgets.property_group import draw_property_group
from editor.widgets.text_input import draw_text_input
from game.world.object_interaction_model import INTERACTION_MODES


COLOR_OVERLAY = (0, 0, 0)
COLOR_MODAL = (29, 31, 36)
COLOR_PREVIEW_PANEL = (24, 26, 31)

DEFAULT_CATEGORIES = [
    "Tree",
    "Rock",
    "Decoration",
    "Building",
    "Furniture",
    "Resource",
    "Other",
]
REQUIRED_TOOL_OPTIONS = ["none", "axe", "pickaxe", "sword"]


def make_object_id(name):
    clean_name = name.strip().lower()
    clean_name = re.sub(r"[^a-z0-9]+", "_", clean_name)
    clean_name = clean_name.strip("_")
    return clean_name


def get_sprite_label(sprite_path):
    if not sprite_path:
        return ""

    return Path(sprite_path).name


def draw_object_editor_dialog(screen, state, sprite=None, object_definitions=None):
    object_definitions = object_definitions or {}
    sync_generated_id(state, object_definitions)

    modal = draw_modal_dialog(screen, "Object Editor")
    content_rect = modal["content_rect"]
    padding = 10

    inspector_w = max(280, int(content_rect.w * 0.3))
    preview_w = content_rect.w - inspector_w - padding

    preview_panel = pygame.Rect(
        content_rect.x,
        content_rect.y,
        preview_w,
        content_rect.h,
    )
    inspector_rect = pygame.Rect(
        preview_panel.right + padding,
        content_rect.y,
        inspector_w,
        content_rect.h,
    )

    pygame.draw.rect(screen, COLOR_PREVIEW_PANEL, preview_panel, border_radius=3)
    pygame.draw.rect(screen, GODOT_BORDER, preview_panel, 1, border_radius=3)
    draw_text(screen, "Preview", preview_panel.x + 10, preview_panel.y + 8, GODOT_MUTED, 12, True)

    preview_layout = draw_object_preview(
        screen,
        preview_panel.inflate(-18, -50).move(0, 18),
        state,
        sprite,
        32,
    )
    preview_layout["inspector_rect"] = inspector_rect

    buttons = [modal["close_button"]]
    buttons.extend(
        draw_inspector(
            screen,
            inspector_rect,
            state,
            object_definitions,
            scroll_y=getattr(state, "inspector_scroll_y", 0),
        )
    )

    return {
        "buttons": buttons,
        "preview_layout": preview_layout,
        "inspector_rect": inspector_rect,
    }


def sync_generated_id(state, object_definitions):
    generated_id = make_object_id(state.name)

    if generated_id:
        state.object_id = generated_id

    state.id_is_duplicate = (
        bool(state.object_id)
        and state.object_id in object_definitions
        and state.object_id != getattr(state, "original_object_id", None)
    )


def draw_inspector(screen, rect, state, object_definitions, scroll_y=0):
    buttons = []
    y = draw_inspector_panel(screen, rect)
    clip_rect = pygame.Rect(rect.x, y, rect.w, rect.h - 112)
    previous_clip = screen.get_clip()
    screen.set_clip(clip_rect)
    inner_x = rect.x + 1
    inner_w = rect.w - 2
    y -= scroll_y

    content_start_y = y

    y, group_buttons = draw_general_group(screen, state, inner_x, y, inner_w)
    buttons.extend(group_buttons)

    y, group_buttons = draw_rendering_group(screen, state, inner_x, y, inner_w)
    buttons.extend(group_buttons)

    y, group_buttons = draw_collision_group(screen, state, inner_x, y, inner_w)
    buttons.extend(group_buttons)

    y, group_buttons = draw_inventory_group(screen, state, inner_x, y, inner_w)
    buttons.extend(group_buttons)

    y, group_buttons = draw_behaviour_group(screen, state, inner_x, y, inner_w)
    buttons.extend(group_buttons)

    y, group_buttons = draw_interaction_points_group(screen, state, inner_x, y, inner_w)
    buttons.extend(group_buttons)

    screen.set_clip(previous_clip)
    content_height = y + scroll_y - content_start_y
    visible_height = clip_rect.height
    state.inspector_max_scroll = max(0, content_height - visible_height)

    if state.inspector_scroll_y > state.inspector_max_scroll:
        state.inspector_scroll_y = state.inspector_max_scroll

    footer_y = rect.bottom - 104
    pygame.draw.rect(screen, GODOT_BG, pygame.Rect(inner_x, footer_y - 10, inner_w, 114))
    save_rect = pygame.Rect(rect.x + 10, footer_y, rect.w - 20, 26)
    save_as_rect = pygame.Rect(rect.x + 10, footer_y + 32, rect.w - 20, 26)
    cancel_rect = pygame.Rect(rect.x + 10, footer_y + 64, rect.w - 20, 26)
    buttons.append(draw_editor_button(screen, save_rect, "Guardar", "object_confirm_save", compact=True))
    buttons.append(draw_editor_button(screen, save_as_rect, "Guardar como...", "object_confirm_save_as", compact=True))
    buttons.append(draw_editor_button(screen, cancel_rect, "Cancelar", "object_cancel", compact=True))

    if getattr(state, "id_is_duplicate", False):
        draw_text(screen, "ID duplicado: se resolvera al guardar", rect.x + 10, footer_y - 25, GODOT_DANGER, 12)
    elif state.status_message:
        draw_text(screen, state.status_message, rect.x + 10, footer_y - 25, GODOT_MUTED, 12)

    return buttons


def draw_group_header(screen, title, expanded, x, y, width):
    rect = pygame.Rect(x, y, width, 26)
    return rect, draw_property_group(screen, rect, title, expanded)


def draw_general_group(screen, state, x, y, width):
    buttons = []
    expanded = state.open_groups.get("General", True)
    header_rect, button = draw_group_header(screen, "General", expanded, x, y, width)
    buttons.append(button)
    y = header_rect.bottom

    if not expanded:
        return y, buttons

    row_h = 28
    row = pygame.Rect(x, y, width, row_h)
    buttons.append(
        draw_text_input(
            screen,
            row,
            "Nombre",
            state.name,
            "object_focus_name",
            focused=state.selected_field == "name",
            cursor_index=getattr(state, "text_cursor", None),
            selection_range=getattr(state, "text_selection", None),
        )
    )
    y += row_h

    row = pygame.Rect(x, y, width, row_h)
    buttons.append(
        draw_text_input(
            screen,
            row,
            "ID",
            state.object_id or "(auto)",
            "object_focus_id",
            readonly=True,
        )
    )
    y += row_h

    row = pygame.Rect(x, y, width, row_h)
    dropdown_buttons = draw_dropdown(
        screen,
        row,
        "Categoria",
        state.category,
        DEFAULT_CATEGORIES,
        "object_category_dropdown",
        expanded=state.category_dropdown_open,
    )
    buttons.extend(dropdown_buttons)
    y += row_h

    if state.category_dropdown_open:
        y += 24 * (len(DEFAULT_CATEGORIES) + 1)

    return y, buttons


def draw_rendering_group(screen, state, x, y, width):
    buttons = []
    expanded = state.open_groups.get("Rendering", True)
    header_rect, button = draw_group_header(screen, "Rendering", expanded, x, y, width)
    buttons.append(button)
    y = header_rect.bottom

    if not expanded:
        return y, buttons

    row_h = 30
    row = pygame.Rect(x, y, width, row_h)
    pygame.draw.rect(screen, GODOT_PANEL, row)
    draw_text(screen, "Sprite", row.x + 8, row.y + 8, GODOT_MUTED, 12)

    if state.sprite:
        label_rect = pygame.Rect(row.x + 104, row.y + 3, row.w - 148, row.h - 6)
        clear_rect = pygame.Rect(row.right - 38, row.y + 3, 28, row.h - 6)
        pygame.draw.rect(screen, (28, 30, 35), label_rect, border_radius=2)
        pygame.draw.rect(screen, GODOT_BORDER, label_rect, 1, border_radius=2)
        draw_text(screen, get_sprite_label(state.sprite), label_rect.x + 6, label_rect.y + 5, GODOT_TEXT, 12)
        buttons.append(draw_editor_button(screen, clear_rect, "X", "object_clear_sprite", compact=True, danger=True))
    else:
        load_rect = pygame.Rect(row.x + 104, row.y + 3, row.w - 112, row.h - 6)
        buttons.append(draw_editor_button(screen, load_rect, "Cargar PNG", "object_load_png", compact=True))

    y += row_h

    return y, buttons


def draw_collision_group(screen, state, x, y, width):
    buttons = []
    expanded = state.open_groups.get("Collision", True)
    header_rect, button = draw_group_header(screen, "Collision", expanded, x, y, width)
    buttons.append(button)
    y = header_rect.bottom

    if not expanded:
        return y, buttons

    row = pygame.Rect(x, y, width, 28)
    buttons.append(
        draw_checkbox(
            screen,
            row,
            "Bloquea movimiento",
            state.solid,
            "object_toggle_solid",
            tooltip="Impide que el jugador atraviese este objeto.",
        )
    )
    y += 28

    return y, buttons


def draw_inventory_group(screen, state, x, y, width):
    buttons = []
    expanded = state.open_groups.get("Inventory", True)
    header_rect, button = draw_group_header(screen, "Inventory", expanded, x, y, width)
    buttons.append(button)
    y = header_rect.bottom

    if not expanded:
        return y, buttons

    row = pygame.Rect(x, y, width, 28)
    buttons.append(
        draw_checkbox(
            screen,
            row,
            "Stackeable",
            state.stackable,
            "object_toggle_stackable",
        )
    )
    y += 28
    return y, buttons


def draw_behaviour_group(screen, state, x, y, width):
    buttons = []
    expanded = state.open_groups.get("Behaviour", True)
    header_rect, button = draw_group_header(screen, "Behaviour", expanded, x, y, width)
    buttons.append(button)
    y = header_rect.bottom

    if not expanded:
        return y, buttons

    row_h = 28
    row = pygame.Rect(x, y, width, row_h)
    dropdown_buttons = draw_dropdown(
        screen,
        row,
        "Pickup",
        "Interaction",
        state.interaction_mode,
        INTERACTION_MODES,
        "object_interaction_mode_dropdown",
        expanded=getattr(state, "interaction_mode_dropdown_open", False),
        select_action="object_interaction_mode_select",
        option_key="interaction_mode",
        allow_new=False,
    )
    buttons.extend(dropdown_buttons)
    y += row_h

    if getattr(state, "interaction_mode_dropdown_open", False):
        y += 24 * len(INTERACTION_MODES)

    row = pygame.Rect(x, y, width, 28)
    buttons.append(
        draw_checkbox(
            screen,
            row,
            "Destructible",
            state.destructible,
            "object_toggle_destructible",
        )
    )
    y += 28

    row = pygame.Rect(x, y, width, row_h)
    selected_tool = state.required_tool or "none"
    dropdown_buttons = draw_dropdown(
        screen,
        row,
        "Herramienta",
        selected_tool,
        REQUIRED_TOOL_OPTIONS,
        "object_required_tool_dropdown",
        expanded=getattr(state, "required_tool_dropdown_open", False),
        select_action="object_required_tool_select",
        option_key="required_tool",
        allow_new=False,
    )
    buttons.extend(dropdown_buttons)
    y += row_h

    if getattr(state, "required_tool_dropdown_open", False):
        y += 24 * len(REQUIRED_TOOL_OPTIONS)

    return y, buttons


def draw_interaction_points_group(screen, state, x, y, width):
    buttons = []
    expanded = state.open_groups.get("Interaction Points", True)
    header_rect, button = draw_group_header(screen, "Interaction Points", expanded, x, y, width)
    buttons.append(button)
    y = header_rect.bottom

    if not expanded:
        return y, buttons

    row = pygame.Rect(x, y, width, 28)
    pygame.draw.rect(screen, GODOT_PANEL, row)
    draw_text(
        screen,
        f"Puntos: {len(state.interaction_points)}",
        row.x + 8,
        row.y + 7,
        GODOT_TEXT,
        12,
    )
    y += 28

    add_rect = pygame.Rect(x + 8, y + 4, width - 16, 24)
    buttons.append(draw_editor_button(screen, add_rect, "Anadir punto en origen", "object_add_interaction_point", compact=True))
    y += 32

    clear_rect = pygame.Rect(x + 8, y + 4, width - 16, 24)
    buttons.append(draw_editor_button(screen, clear_rect, "Limpiar puntos", "object_clear_interaction_points", compact=True))
    y += 34

    return y, buttons
