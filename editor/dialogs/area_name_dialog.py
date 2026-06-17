import pygame

from editor.ui.widgets.modal_dialog import (
    draw_modal_dialog,
    draw_modal_footer_buttons,
    draw_modal_label,
    draw_modal_text_input,
)


def draw_area_name_dialog(screen, title, text_value):
    modal = draw_modal_dialog(
        screen,
        title,
        width=430,
        height=210,
        close_action="area_name_cancel",
    )
    modal_rect = modal["rect"]
    content_rect = modal["content_rect"]

    draw_modal_label(screen, "Nombre:", content_rect.x + 12, content_rect.y + 20)
    input_rect = pygame.Rect(
        content_rect.x + 12,
        content_rect.y + 48,
        content_rect.w - 24,
        32,
    )
    draw_modal_text_input(screen, input_rect, text_value)

    buttons = [modal["close_button"]]
    buttons.extend(
        draw_modal_footer_buttons(
            screen,
            modal_rect,
            [
                {"label": "Guardar", "action": "area_name_confirm"},
                {"label": "Cancelar", "action": "area_name_cancel"},
            ],
            button_width=120,
        )
    )
    return buttons

