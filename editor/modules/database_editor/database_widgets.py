import pygame

from editor.ui.widgets.checkbox import draw_checkbox
from editor.ui.widgets.editor_button import draw_editor_button
from editor.ui.widgets.floating_dropdown import draw_dropdown_field, draw_floating_dropdown
from editor.ui.widgets.text_input import draw_text_input


def draw_database_field(screen, rect, row, edit_state=None, record_id=None, dropdown_state=None):
    action = {
        "type": "field",
        "row": row,
    }

    if not row.get("editable"):
        return draw_clipped_text_input(
            screen,
            rect,
            row["label"],
            row.get("value", ""),
            action,
            focused=False,
            readonly=True,
        )

    raw_value = row.get("raw_value")

    if isinstance(raw_value, bool):
        return draw_clipped_checkbox(
            screen,
            rect,
            row["label"],
            raw_value,
            {
                "type": "field_toggle",
                "row": row,
            },
        )

    options = row.get("options", [])

    if options:
        return draw_database_picklist(
            screen,
            rect,
            row,
            record_id,
            dropdown_state,
        )

    is_editing = (
        edit_state is not None
        and edit_state.get("record_id") == record_id
        and edit_state.get("path") == row.get("path")
    )

    value = row.get("value", "")
    if is_editing:
        value = edit_state.get("text")

    return draw_clipped_text_input(
        screen,
        rect,
        row["label"],
        value,
        action,
        focused=is_editing,
        readonly=False,
        cursor_index=len(str(value)) if is_editing else None,
    )


def draw_database_save_button(screen, rect, enabled=True):
    return draw_editor_button(
        screen,
        rect,
        "Guardar",
        "database_save",
        compact=True,
        disabled=not enabled,
    )


def draw_database_discard_button(screen, rect, enabled=True):
    return draw_editor_button(
        screen,
        rect,
        "Descartar",
        "database_discard",
        compact=True,
        disabled=not enabled,
    )


def draw_database_picklist(screen, rect, row, record_id, dropdown_state=None):
    is_open = (
        dropdown_state is not None
        and dropdown_state.get("record_id") == record_id
        and dropdown_state.get("path") == row.get("path")
    )

    previous_clip = screen.get_clip()
    buttons, field_rect = draw_dropdown_field(
        screen,
        rect,
        row["label"],
        row.get("value", ""),
        {
            "type": "field_picklist_open",
            "row": row,
        },
    )
    screen.set_clip(previous_clip)

    return {
        "rect": field_rect,
        "action": buttons[0]["action"],
        "dropdown_request": {
            "open": is_open,
            "anchor_rect": field_rect,
            "row": row,
            "record_id": record_id,
            "options": row.get("options", []),
            "selected_value": row.get("value", ""),
        },
    }


def draw_database_picklist_dropdown(screen, request):
    if not request or not request.get("open"):
        return []

    result = draw_floating_dropdown(
        screen,
        request["anchor_rect"],
        request["options"],
        request.get("selected_value", ""),
        "database_picklist_select",
        "value",
        allow_new=False,
    )

    buttons = []
    for button in result["buttons"]:
        action = dict(button)
        action["action"] = {
            "type": "field_picklist_select",
            "record_id": request["record_id"],
            "row": request["row"],
            "value": button.get("value"),
        }
        buttons.append({
            "rect": button["rect"],
            "action": action["action"],
        })

    return buttons


def draw_clipped_text_input(*args, **kwargs):
    screen = args[0]
    previous_clip = screen.get_clip()
    result = draw_text_input(*args, **kwargs)
    screen.set_clip(previous_clip)
    return result


def draw_clipped_checkbox(*args, **kwargs):
    screen = args[0]
    previous_clip = screen.get_clip()
    result = draw_checkbox(*args, **kwargs)
    screen.set_clip(previous_clip)
    return result
