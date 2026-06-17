from editor.ui.widgets.list_dialog import (
    draw_list_dialog,
    draw_list_row_background,
    draw_row_text,
)


def draw_open_scene_dialog(screen, saved_scenes, scroll_y=0):
    return draw_list_dialog(
        screen,
        "Abrir escena",
        saved_scenes,
        draw_scene_row,
        "No hay escenas guardadas.",
        "open_scene_cancel",
        width=520,
        height=360,
        row_height=30,
        scroll_y=scroll_y,
    )


def draw_scene_row(screen, row, scene_info):
    draw_list_row_background(screen, row)
    label = f"{scene_info['name']}  ({scene_info['id']})"
    draw_row_text(screen, label, row.x + 8, row.y + 7)
    return [
        {
            "rect": row.copy(),
            "action": "open_scene_select",
            "scene_id": scene_info["id"],
        }
    ]

