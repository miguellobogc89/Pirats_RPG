from editor.scene.scene_operations import (
    add_collision_cell,
    add_object,
)


def paint_at_mouse(scene_data, mode, selected_object_type, camera, mouse_pos):
    cell = camera.screen_to_cell(mouse_pos)

    if mode == "objects" and selected_object_type:
        add_object(
            scene_data,
            selected_object_type,
            cell,
        )

    if mode == "collisions":
        add_collision_cell(scene_data, cell)