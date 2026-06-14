import pygame
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game.world.grid_manager import TILE_SIZE

from editor.editor_assets import (
    load_editor_sprites,
    load_object_definitions,
)

from editor.editor_camera import EditorCamera
from editor.dialogs.unsaved_changes_dialog import draw_unsaved_changes_dialog
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
    save_scene_for_game(scene_data)


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
        )

        input_manager.set_buttons(menu_buttons + side_buttons)

        draw_editor_status_bar(
            screen,
            scene_data,
            object_definitions,
            camera,
            input_manager.mode,
            input_manager.selected_object_type,
        )


        if input_manager.show_unsaved_dialog:
            dialog_buttons = draw_unsaved_changes_dialog(screen)
            input_manager.set_dialog_buttons(dialog_buttons)
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()