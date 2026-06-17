from editor.dialogs.area_name_dialog import draw_area_name_dialog
from editor.dialogs.confirm_dialog import draw_confirm_dialog
from editor.dialogs.open_object_dialog import draw_open_object_dialog
from editor.dialogs.open_scene_dialog import draw_open_scene_dialog
from editor.dialogs.relations_dialog import draw_relations_dialog
from editor.dialogs.save_as_dialog import draw_save_as_dialog
from editor.dialogs.unsaved_changes_dialog import draw_unsaved_changes_dialog
from editor.editor_ui import draw_editor_side_panel
from editor.object_editor.object_editor_dialog import draw_object_editor_dialog
from editor.rendering.editor_renderer import (
    draw_editor_scene,
    draw_preview,
    draw_rect_tool_preview,
)
from editor.ui.editor_menu_bar import draw_editor_menu_bar
from editor.ui.editor_status_bar import draw_editor_status_bar


def draw_scene_editor(
    screen,
    scene_data,
    object_definitions,
    sprites,
    camera,
    input_manager,
):
    screen.fill((30, 34, 38))

    draw_editor_scene(
        screen,
        scene_data,
        object_definitions,
        sprites,
        camera,
        input_manager.selected_scene_object_id,
    )

    draw_preview(
        screen,
        input_manager.selected_object_type,
        object_definitions,
        sprites,
        camera,
    )

    draw_rect_tool_preview(
        screen,
        input_manager.get_rect_preview_data(),
        camera,
    )

    menu_buttons = draw_editor_menu_bar(
        screen,
        input_manager.active_menu,
    )

    side_panel_result = draw_editor_side_panel(
        screen,
        input_manager.mode,
        input_manager.selected_object_type,
        object_definitions,
        input_manager.get_selected_area(),
        input_manager.selected_terrain_id,
        input_manager.side_panel_scroll_y,
        input_manager.side_panel_sections,
        input_manager.get_selected_scene_object(),
        input_manager.get_property_edit_view(),
    )
    side_buttons = side_panel_result["buttons"]
    input_manager.side_panel_max_scroll = side_panel_result["max_scroll"]

    input_manager.set_buttons(menu_buttons + side_buttons)

    draw_editor_status_bar(
        screen,
        scene_data,
        object_definitions,
        camera,
        input_manager.mode,
        input_manager.selected_object_type,
        input_manager.status_message,
    )

    draw_scene_dialogs(screen, object_definitions, input_manager)


def draw_scene_dialogs(screen, object_definitions, input_manager):
    if input_manager.show_unsaved_dialog:
        dialog_buttons = draw_unsaved_changes_dialog(screen)
        input_manager.set_dialog_buttons(dialog_buttons)

    if input_manager.show_save_as_dialog:
        dialog_buttons = draw_save_as_dialog(
            screen,
            input_manager.save_as_text,
        )
        input_manager.set_dialog_buttons(dialog_buttons)

    if input_manager.show_open_scene_dialog:
        dialog_result = draw_open_scene_dialog(
            screen,
            input_manager.saved_scenes,
            input_manager.open_scene_dialog_scroll_y,
        )
        dialog_buttons = dialog_result["buttons"]
        input_manager.open_scene_dialog_max_scroll = dialog_result["max_scroll"]
        input_manager.set_dialog_buttons(dialog_buttons)

    if input_manager.show_open_object_dialog:
        dialog_result = draw_open_object_dialog(
            screen,
            object_definitions,
            input_manager.open_object_dialog_scroll_y,
        )
        dialog_buttons = dialog_result["buttons"]
        input_manager.open_object_dialog_max_scroll = dialog_result["max_scroll"]
        input_manager.set_dialog_buttons(dialog_buttons)

    if input_manager.show_area_name_dialog:
        dialog_buttons = draw_area_name_dialog(
            screen,
            "Editar area",
            input_manager.area_name_text,
        )
        input_manager.set_dialog_buttons(dialog_buttons)

    if input_manager.show_relations_dialog:
        dialog_buttons = draw_relations_dialog(
            screen,
            input_manager.relation_exits,
            input_manager.relation_targets,
            input_manager.selected_relation_exit_key,
            input_manager.selected_relation_target_keys,
        )
        input_manager.set_dialog_buttons(dialog_buttons)

    if input_manager.show_area_name_dialog and input_manager.show_relations_dialog:
        dialog_buttons = draw_area_name_dialog(
            screen,
            "Editar area",
            input_manager.area_name_text,
        )
        input_manager.set_dialog_buttons(dialog_buttons)

    if input_manager.show_object_delete_confirm:
        dialog_buttons = draw_confirm_dialog(
            screen,
            "Eliminar objeto",
            f"Seguro que quieres eliminar '{input_manager.selected_object_type}'?",
            "object_delete_confirm",
            "object_delete_cancel",
        )
        input_manager.set_dialog_buttons(dialog_buttons)

    if input_manager.show_object_editor:
        object_editor_result = draw_object_editor_dialog(
            screen,
            input_manager.object_editor_state,
            input_manager.object_editor_sprite,
            object_definitions,
        )

        input_manager.object_editor_preview_layout = object_editor_result["preview_layout"]
        input_manager.set_dialog_buttons(object_editor_result["buttons"])
