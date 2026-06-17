from editor.areas.collision_tool import (
    add_collision_cell,
    remove_collision_cell,
)

from editor.areas.exit_tool import (
    add_exit_cell,
    add_spawn_cell,
    remove_exit_cell,
    remove_spawn_cell,
)

from editor.scene.scene_operations import (
    add_object,
    remove_object_at_cell,
)

from editor.terrain.terrain_tool import (
    paint_terrain_cell,
    erase_terrain_cell,
)


def get_cell_rect(start_cell, end_cell):
    min_x = min(start_cell[0], end_cell[0])
    max_x = max(start_cell[0], end_cell[0])
    min_y = min(start_cell[1], end_cell[1])
    max_y = max(start_cell[1], end_cell[1])

    return min_x, min_y, max_x, max_y


def paint_at_mouse(
    scene_data,
    mode,
    selected_object_type,
    selected_terrain_id,
    object_definitions,
    camera,
    mouse_pos,
):
    cell = camera.screen_to_cell(mouse_pos)

    return paint_at_cell(
        scene_data,
        mode,
        selected_object_type,
        selected_terrain_id,
        object_definitions,
        cell,
    )


def paint_at_cell(
    scene_data,
    mode,
    selected_object_type,
    selected_terrain_id,
    object_definitions,
    cell,
):
    if mode == "objects" and selected_object_type:
        return add_object(
            scene_data,
            selected_object_type,
            cell,
            object_definitions,
        )

    if mode == "collisions":
        return add_collision_cell(scene_data, cell)

    if mode == "spawns":
        return add_spawn_cell(scene_data, cell)

    if mode == "exits":
        return add_exit_cell(scene_data, cell)

    if mode == "terrain" and selected_terrain_id:
        return paint_terrain_cell(scene_data, cell, selected_terrain_id)

    return False


def erase_at_mouse(scene_data, mode, object_definitions, camera, mouse_pos):
    cell = camera.screen_to_cell(mouse_pos)

    return erase_at_cell(
        scene_data,
        mode,
        object_definitions,
        cell,
    )


def erase_at_cell(scene_data, mode, object_definitions, cell):
    if mode == "collisions":
        return remove_collision_cell(scene_data, cell)

    if mode == "spawns":
        return remove_spawn_cell(scene_data, cell)

    if mode == "exits":
        return remove_exit_cell(scene_data, cell)

    if mode == "terrain":
        return erase_terrain_cell(scene_data, cell)

    return remove_object_at_cell(
        scene_data,
        cell,
        object_definitions,
    )


def paint_rect(
    scene_data,
    mode,
    selected_object_type,
    selected_terrain_id,
    object_definitions,
    start_cell,
    end_cell,
):
    changed = False
    min_x, min_y, max_x, max_y = get_cell_rect(start_cell, end_cell)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            cell_changed = paint_at_cell(
                scene_data,
                mode,
                selected_object_type,
                selected_terrain_id,
                object_definitions,
                [x, y],
            )

            if cell_changed:
                changed = True

    return changed


def erase_rect(scene_data, mode, object_definitions, start_cell, end_cell):
    changed = False
    min_x, min_y, max_x, max_y = get_cell_rect(start_cell, end_cell)

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            cell_changed = erase_at_cell(
                scene_data,
                mode,
                object_definitions,
                [x, y],
            )

            if cell_changed:
                changed = True

    return changed
