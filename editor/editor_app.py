import pygame
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game.world.grid_manager import TILE_SIZE

from editor.dialogs.open_scene_dialog import draw_open_scene_dialog
from editor.dialogs.open_object_dialog import draw_open_object_dialog
from editor.dialogs.save_as_dialog import draw_save_as_dialog
from editor.dialogs.unsaved_changes_dialog import draw_unsaved_changes_dialog
from editor.dialogs.area_name_dialog import draw_area_name_dialog
from editor.dialogs.confirm_dialog import draw_confirm_dialog
from editor.dialogs.relations_dialog import draw_relations_dialog
from editor.object_editor.object_editor_dialog import draw_object_editor_dialog

from editor.editor_assets import (
    load_editor_sprites,
    load_object_definitions,
)

from editor.editor_camera import EditorCamera

from editor.editor_ui import draw_editor_side_panel

from editor.input.editor_input_manager import EditorInputManager

from editor.rendering.editor_renderer import (
    draw_editor_scene,
    draw_preview,
    draw_rect_tool_preview,
)

from editor.scene_editor_serializer import (
    DEFAULT_SCENE_ID,
    load_scene_for_editor,
    save_scene_for_game,
)

from editor.ui.editor_menu_bar import draw_editor_menu_bar
from editor.ui.editor_status_bar import draw_editor_status_bar


def load_scene(scene_id=DEFAULT_SCENE_ID):
    return load_scene_for_editor(scene_id)


def save_scene(scene_data):
    return save_scene_for_game(scene_data)


def main():
    pygame.init()

    scene_data = load_scene()
    object_definitions = load_object_definitions()

    editor_width = 1440
    editor_height = 900
    is_fullscreen = False
    screen = pygame.display.set_mode((editor_width, editor_height), pygame.RESIZABLE)
    pygame.display.set_caption("RPG Scene Editor")

    sprites = load_editor_sprites(object_definitions, TILE_SIZE)

    clock = pygame.time.Clock()
    camera = EditorCamera()

    input_manager = EditorInputManager(
        scene_data,
        object_definitions,
        camera,
        save_scene,
    )

    running = True

    def toggle_fullscreen():
        nonlocal screen, is_fullscreen
        is_fullscreen = not is_fullscreen
        if is_fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((editor_width, editor_height), pygame.RESIZABLE)

    while running:
        screen.fill((30, 34, 38))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                continue

            if event.type == pygame.VIDEORESIZE and not is_fullscreen:
                editor_width = max(1100, event.w)
                editor_height = max(720, event.h)
                screen = pygame.display.set_mode((editor_width, editor_height), pygame.RESIZABLE)
                continue

            running = input_manager.handle_event(screen, event)

            if running == "toggle_fullscreen":
                toggle_fullscreen()
                running = True

            if not running:
                break

        if input_manager.object_definitions_changed:
            object_definitions.clear()
            object_definitions.update(load_object_definitions())
            sprites.clear()
            sprites.update(load_editor_sprites(object_definitions, TILE_SIZE))
            input_manager.object_definitions_changed = False

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
            dialog_buttons = draw_open_scene_dialog(
                screen,
                input_manager.saved_scenes,
            )
            input_manager.set_dialog_buttons(dialog_buttons)

        if input_manager.show_open_object_dialog:
            dialog_buttons = draw_open_object_dialog(
                screen,
                object_definitions,
            )
            input_manager.set_dialog_buttons(dialog_buttons)

        if input_manager.show_area_name_dialog:
            dialog_buttons = draw_area_name_dialog(
                screen,
                "Editar área",
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

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
