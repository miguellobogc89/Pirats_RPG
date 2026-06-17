import pygame

from editor.ui.widgets.checkbox import draw_checkbox
from editor.ui.widgets.floating_dropdown import draw_dropdown_field
from editor.ui.widgets.inspector_panel import (
    GODOT_DANGER,
    GODOT_MUTED,
    GODOT_PANEL,
    GODOT_TEXT,
    draw_text,
)
from editor.ui.widgets.text_input import draw_text_input
from game.objects.object_schema import FUNCTIONAL_TYPES, INTERACTION_MODES


REQUIRED_TOOL_OPTIONS = ["none", "axe", "pickaxe", "sword"]

FIELD_LABELS = {
    "npc_id": "NPC ID",
    "dialogue_id": "Dialogue ID",
    "portrait_path": "Portrait",
    "interaction_id": "Interaction ID",
    "required_item": "Item requerido",
    "hp": "HP",
    "energy_cost": "Energia",
    "item_id": "Item ID",
    "quantity": "Cantidad",
    "trigger_id": "Trigger ID",
    "target_event": "Evento",
    "once": "Una vez",
    "container_id": "Container ID",
    "capacity": "Capacidad",
    "locked": "Bloqueado",
    "required_key": "Llave",
    "door_id": "Door ID",
}

TEXT_FIELDS_BY_TYPE = {
    "npc": ["npc_id", "dialogue_id", "portrait_path"],
    "interactable": ["interaction_id", "required_item"],
    "destructible": ["hp", "energy_cost"],
    "pickup": ["item_id", "quantity"],
    "trigger": ["trigger_id", "target_event"],
    "container": ["container_id", "capacity", "required_key"],
    "door": ["door_id", "required_key", "interaction_id"],
}

BOOL_FIELDS_BY_TYPE = {
    "trigger": ["once"],
    "container": ["locked"],
    "door": ["locked"],
}


def draw_functional_type_form(screen, state, x, y, width):
    buttons = []
    floating_dropdown_requests = []
    row_h = 28

    row = pygame.Rect(x, y, width, row_h)
    dropdown_buttons, anchor_rect = draw_dropdown_field(
        screen,
        row,
        "Functional Type",
        state.functional_type,
        "object_functional_type_dropdown",
    )
    buttons.extend(dropdown_buttons)
    floating_dropdown_requests.append({
        "id": "functional_type",
        "anchor_rect": anchor_rect,
        "options": list(FUNCTIONAL_TYPES),
        "selected_value": state.functional_type,
        "select_action": "object_functional_type_select",
        "option_key": "functional_type",
    })
    y += row_h

    functional_type = state.functional_type

    if functional_type == "decorative":
        y = draw_hint(screen, x, y, width, "Sin comportamiento adicional.")

    if functional_type == "interactable":
        y, mode_buttons, mode_floaters = draw_interaction_mode_row(screen, state, x, y, width)
        buttons.extend(mode_buttons)
        floating_dropdown_requests.extend(mode_floaters)

    if functional_type == "destructible":
        y, tool_buttons, tool_floaters = draw_required_tool_row(screen, state, x, y, width)
        buttons.extend(tool_buttons)
        floating_dropdown_requests.extend(tool_floaters)

    for field_name in TEXT_FIELDS_BY_TYPE.get(functional_type, []):
        y, field_buttons = draw_dynamic_text_row(screen, state, x, y, width, field_name)
        buttons.extend(field_buttons)

    for field_name in BOOL_FIELDS_BY_TYPE.get(functional_type, []):
        y, field_buttons = draw_dynamic_bool_row(screen, state, x, y, width, field_name)
        buttons.extend(field_buttons)

    y = draw_validation_warnings(screen, state, x, y, width)
    return y, buttons, floating_dropdown_requests


def draw_interaction_mode_row(screen, state, x, y, width):
    row = pygame.Rect(x, y, width, 28)
    buttons, anchor_rect = draw_dropdown_field(
        screen,
        row,
        "Interaction",
        state.interaction_mode,
        "object_interaction_mode_dropdown",
    )
    return y + 28, buttons, [{
        "id": "interaction_mode",
        "anchor_rect": anchor_rect,
        "options": list(INTERACTION_MODES),
        "selected_value": state.interaction_mode,
        "select_action": "object_interaction_mode_select",
        "option_key": "interaction_mode",
    }]


def draw_required_tool_row(screen, state, x, y, width):
    selected_tool = state.required_tool or "none"
    row = pygame.Rect(x, y, width, 28)
    buttons, anchor_rect = draw_dropdown_field(
        screen,
        row,
        "Herramienta",
        selected_tool,
        "object_required_tool_dropdown",
    )
    return y + 28, buttons, [{
        "id": "required_tool",
        "anchor_rect": anchor_rect,
        "options": REQUIRED_TOOL_OPTIONS,
        "selected_value": selected_tool,
        "select_action": "object_required_tool_select",
        "option_key": "required_tool",
    }]


def draw_dynamic_text_row(screen, state, x, y, width, field_name):
    row = pygame.Rect(x, y, width, 28)
    value = str(state.get_dynamic_field(field_name))
    button = draw_text_input(
        screen,
        row,
        FIELD_LABELS.get(field_name, field_name),
        value,
        "object_focus_dynamic_field",
        focused=state.selected_field == field_name,
        cursor_index=getattr(state, "text_cursor", None),
        selection_range=getattr(state, "text_selection", None),
    )
    button["field_name"] = field_name
    buttons = [
        button
    ]
    return y + 28, buttons


def draw_dynamic_bool_row(screen, state, x, y, width, field_name):
    row = pygame.Rect(x, y, width, 28)
    buttons = [
        draw_checkbox(
            screen,
            row,
            FIELD_LABELS.get(field_name, field_name),
            bool(state.get_dynamic_field(field_name)),
            "object_toggle_dynamic_bool",
        )
    ]
    buttons[0]["field_name"] = field_name
    return y + 28, buttons


def draw_hint(screen, x, y, width, message):
    row = pygame.Rect(x, y, width, 28)
    pygame.draw.rect(screen, GODOT_PANEL, row)
    draw_text(screen, message, row.x + 8, row.y + 7, GODOT_MUTED, 12)
    return y + 28


def draw_warning(screen, x, y, width, message):
    row = pygame.Rect(x, y, width, 34)
    pygame.draw.rect(screen, GODOT_PANEL, row)
    draw_text(screen, message, row.x + 8, row.y + 9, GODOT_DANGER, 12)
    return y + 34


def draw_validation_warnings(screen, state, x, y, width):
    state.refresh_validation()
    warnings = list(getattr(state, "validation_warnings", []))[:3]

    for warning in warnings:
        row = pygame.Rect(x, y, width, 28)
        pygame.draw.rect(screen, GODOT_PANEL, row)
        draw_text(screen, warning.message, row.x + 8, row.y + 7, GODOT_MUTED, 11)
        y += 28

    errors = list(getattr(state, "validation_errors", []))[:2]

    for error in errors:
        row = pygame.Rect(x, y, width, 28)
        pygame.draw.rect(screen, GODOT_PANEL, row)
        draw_text(screen, error.message, row.x + 8, row.y + 7, GODOT_DANGER, 11)
        y += 28

    return y

