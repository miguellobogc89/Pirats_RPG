from editor.scene.scene_operations import (
    add_collision_cell,
    add_object,
    remove_object_at_cell,
)


def get_cell_rect(start_cell, end_cell):
    min_x = min(start_cell[0], end_cell[0])
    max_x = max(start_cell[0], end_cell[0])
    min_y = min(start_cell[1], end_cell[1])
    max_y = max(start_cell[1], end_cell[1])

    return min_x, min_y, max_x, max_y


def paint_at_mouse(scene_data, mode, selected_object_type, object_definitions, camera, mouse_pos):
    cell = camera.screen_to_cell(mouse_pos)
    paint_at_cell(scene_data, mode, selected_object_type, object_definitions, cell)


def paint_at_cell(scene_data, mode, selected_object_type, object_definitions, cell):
    if mode == "objects" and selected_object_type:
        add_object(
            scene_data,
            selected_object_type,
            cell,
            object_definitions,
        )

    if mode == "collisions":
        add_collision_cell(scene_data, cell)


def erase_at_mouse(scene_data, object_definitions, camera, mouse_pos):
    cell = camera.screen_to_cell(mouse_pos)
    erase_at_cell(scene_data, object_definitions, cell)


def erase_at_cell(scene_data, object_definitions, cell):
    remove_object_at_cell(
        scene_data,
        cell,
        object_definitions,
    )


def paint_rect(scene_data, mode, selected_object_type, object_definitions, start_cell, end_cell):
    min_x, min_y, max_x, max_y = get_cell_rect(start_cell, end_cell)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            paint_at_cell(
                scene_data,
                mode,
                selected_object_type,
                object_definitions,
                [x, y],
            )


def erase_rect(scene_data, object_definitions, start_cell, end_cell):
    min_x, min_y, max_x, max_y = get_cell_rect(start_cell, end_cell)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            erase_at_cell(
                scene_data,
                object_definitions,
                [x, y],
            )