import pygame

from editor.object_editor.object_definition_repository import list_object_definitions
from editor.ui.widgets.editor_button import draw_editor_button
from editor.ui.widgets.list_dialog import (
    draw_list_dialog,
    draw_list_row_background,
    draw_row_text,
)


def draw_open_object_dialog(screen, object_definitions, scroll_y=0):
    if object_definitions is None:
        source_items = list_object_definitions()
    else:
        source_items = [
            {
                "id": object_id,
                "name": object_data.get("name", object_id),
                "category": object_data.get("category", "other"),
            }
            for object_id, object_data in sorted(object_definitions.items())
        ]

    items = [
        {
            "object_id": item["id"],
            "name": item.get("name", item["id"]),
            "category": item.get("category", "other"),
        }
        for item in source_items
    ]

    return draw_list_dialog(
        screen,
        "Abrir objeto",
        items,
        draw_object_row,
        "No hay objetos guardados.",
        "open_object_cancel",
        width=620,
        height=420,
        row_height=34,
        scroll_y=scroll_y,
    )


def draw_object_row(screen, row, item):
    draw_list_row_background(screen, row)

    open_rect = pygame.Rect(row.right - 150, row.y + 5, 66, 24)
    delete_rect = pygame.Rect(row.right - 76, row.y + 5, 66, 24)
    text_right = open_rect.x - 10

    label = f"{item['name']}  ({item['object_id']})  [{item['category']}]"
    clip = pygame.Rect(row.x + 8, row.y, max(20, text_right - row.x - 8), row.h)
    previous_clip = screen.get_clip()
    screen.set_clip(clip)
    draw_row_text(screen, label, row.x + 8, row.y + 9)
    screen.set_clip(previous_clip)

    open_button = draw_editor_button(
        screen,
        open_rect,
        "Abrir",
        "open_object_select",
        compact=True,
    )
    open_button["object_id"] = item["object_id"]

    delete_button = draw_editor_button(
        screen,
        delete_rect,
        "Eliminar",
        "open_object_delete",
        compact=True,
        danger=True,
    )
    delete_button["object_id"] = item["object_id"]

    return [open_button, delete_button]

