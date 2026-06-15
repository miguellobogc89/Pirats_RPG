from editor.widgets.inspector_panel import GODOT_MUTED
from editor.widgets.modal_dialog import (
    draw_modal_dialog,
    draw_modal_footer_buttons,
    draw_wrapped_text,
)


def draw_unsaved_changes_dialog(screen):
    modal = draw_modal_dialog(
        screen,
        "Cambios sin guardar",
        width=430,
        height=190,
        close_action="dialog_cancel",
    )
    modal_rect = modal["rect"]
    content_rect = modal["content_rect"]

    message_rect = content_rect.copy()
    message_rect.y += 10
    message_rect.h = 72
    draw_wrapped_text(
        screen,
        "Hay cambios sin guardar. ¿Quieres guardarlos antes de continuar?",
        message_rect,
        GODOT_MUTED,
        13,
    )

    buttons = [modal["close_button"]]
    buttons.extend(
        draw_modal_footer_buttons(
            screen,
            modal_rect,
            [
                {"label": "Guardar", "action": "dialog_save"},
                {"label": "No guardar", "action": "dialog_discard"},
                {"label": "Cancelar", "action": "dialog_cancel"},
            ],
            button_width=120,
        )
    )
    return buttons
