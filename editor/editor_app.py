import pygame
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game.world.grid_manager import TILE_SIZE

from editor.dialogs.open_scene_dialog import draw_open_scene_dialog
from editor.dialogs.save_as_dialog import draw_save_as_dialog
from editor.dialogs.unsaved_changes_dialog import draw_unsaved_changes_dialog
from editor.dialogs.area_name_dialog import draw_area_name_dialog
from editor.dialogs.relations_dialog import draw_relations_dialog

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

    screen = pygame.display.set_mode((1000, 700))
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

    while running:
        screen.fill((80, 120, 70))

        for event in pygame.event.get():
            running = input_manager.handle_event(screen, event)

            if not running:
                break

        draw_editor_scene(
            screen,
            scene_data,
            object_definitions,
            sprites,
            camera,
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

        side_buttons = draw_editor_side_panel(
            screen,
            input_manager.mode,
            input_manager.selected_object_type,
            object_definitions,
            input_manager.get_selected_area(),
        )

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
                scene_data,
                input_manager.relation_targets,
                input_manager.selected_relation_exit_id,
                input_manager.selected_relation_target_key,
            )
            input_manager.set_dialog_buttons(dialog_buttons)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()