from editor.widgets.inspector_panel import GODOT_TEXT
from editor.widgets.modal_dialog import (
    draw_modal_dialog,
    draw_modal_footer_buttons,
    draw_wrapped_text,
)


def draw_confirm_dialog(screen, title, message, confirm_action, cancel_action):
    modal = draw_modal_dialog(
        screen,
        title,
        width=460,
        height=190,
        close_action=cancel_action,
    )
    modal_rect = modal["rect"]
    content_rect = modal["content_rect"]

    message_rect = content_rect.copy()
    message_rect.y += 8
    message_rect.h = 82
    draw_wrapped_text(screen, message, message_rect, GODOT_TEXT, 13)

    buttons = [modal["close_button"]]
    buttons.extend(
        draw_modal_footer_buttons(
            screen,
            modal_rect,
            [
                {"label": "Eliminar", "action": confirm_action, "danger": True},
                {"label": "Cancelar", "action": cancel_action},
            ],
            button_width=92,
        )
    )
    return buttons
