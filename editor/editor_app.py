import pygame
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game.world.grid_manager import TILE_SIZE

from editor_assets import (
    load_editor_sprites,
    load_object_definitions,
)

from editor_camera import EditorCamera

from editor_ui import (
    PANEL_WIDTH,
    draw_editor_panel,
    get_clicked_panel_action,
)

from rendering.editor_renderer import (
    draw_editor_scene,
    draw_preview,
)

from scene_editor_serializer import (
    DEFAULT_SCENE_ID,
    load_scene_for_editor,
    save_scene_for_game,
)

from editor.tools.paint_tool import (
    erase_at_mouse,
    erase_rect,
    paint_at_mouse,
    paint_rect,
)


def load_scene(scene_id=DEFAULT_SCENE_ID):
    return load_scene_for_editor(scene_id)


def save_scene(scene_data):
    save_scene_for_game(scene_data)


def is_inside_canvas(screen, pos):
    panel_start_x = screen.get_width() - PANEL_WIDTH

    return pos[0] < panel_start_x


def handle_panel_action(clicked_action, object_definitions):
    if not clicked_action:
        return None

    action = clicked_action["action"]

    if action == "mode_objects":
        return {
            "mode": "objects",
            "selected_object_type": None,
        }

    if action == "mode_collisions":
        return {
            "mode": "collisions",
            "selected_object_type": None,
        }

    if action == "select_object":
        object_type = clicked_action["object_type"]

        if object_type in object_definitions:
            return {
                "mode": "objects",
                "selected_object_type": object_type,
            }

    return None


def main():
    pygame.init()

    scene_data = load_scene()
    object_definitions = load_object_definitions()

    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("RPG Scene Editor")

    sprites = load_editor_sprites(object_definitions, TILE_SIZE)

    clock = pygame.time.Clock()
    camera = EditorCamera()

    mode = "objects"
    selected_object_type = None
    buttons = []

    is_painting = False
    running = True

    while running:
        screen.fill((80, 120, 70))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_scene(scene_data)
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    selected_object_type = None
                    is_painting = False
                    camera.stop_pan()

                if event.key == pygame.K_s:
                    save_scene(scene_data)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    camera.start_pan(event.pos)
                    continue

                if event.button == 4:
                    camera.zoom_in()
                    continue

                if event.button == 5:
                    camera.zoom_out()
                    continue

                if event.button == 3:
                    if is_inside_canvas(screen, event.pos):
                        erase_at_mouse(
                            scene_data,
                            object_definitions,
                            camera,
                            event.pos,
                        )
                    continue

                ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL

                if event.button == 1 and ctrl_pressed:
                    if is_inside_canvas(screen, event.pos):
                        rect_start_cell = camera.screen_to_cell(event.pos)
                        rect_end_cell = rect_start_cell
                        rect_button = 1
                        is_rect_tool_active = True
                    continue

                if event.button == 3 and ctrl_pressed:
                    if is_inside_canvas(screen, event.pos):
                        rect_start_cell = camera.screen_to_cell(event.pos)
                        rect_end_cell = rect_start_cell
                        rect_button = 3
                        is_rect_tool_active = True
                    continue

                if event.button == 3:
                    if is_inside_canvas(screen, event.pos):
                        erase_at_mouse(
                            scene_data,
                            object_definitions,
                            camera,
                            event.pos,
                        )
                        is_erasing = True
                    continue

                clicked_action = get_clicked_panel_action(event.pos, buttons)

                if clicked_action:
                    action = clicked_action["action"]

                    if action == "save":
                        save_scene(scene_data)

                    if action == "zoom_in":
                        camera.panel_zoom_in()

                    if action == "zoom_out":
                        camera.panel_zoom_out()

                    panel_result = handle_panel_action(
                        clicked_action,
                        object_definitions,
                    )

                    if panel_result is not None:
                        mode = panel_result["mode"]
                        selected_object_type = panel_result["selected_object_type"]

                else:
                    if is_inside_canvas(screen, event.pos):
                        paint_at_mouse(
                            scene_data,
                            mode,
                            selected_object_type,
                            object_definitions,
                            camera,
                            event.pos,
                        )

                        is_painting = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    camera.stop_pan()

                if is_rect_tool_active:
                    if rect_start_cell is not None and rect_end_cell is not None:
                        if rect_button == 1:
                            paint_rect(
                                scene_data,
                                mode,
                                selected_object_type,
                                object_definitions,
                                rect_start_cell,
                                rect_end_cell,
                            )

                        if rect_button == 3:
                            erase_rect(
                                scene_data,
                                object_definitions,
                                rect_start_cell,
                                rect_end_cell,
                            )

                    is_rect_tool_active = False
                    rect_start_cell = None
                    rect_end_cell = None
                    rect_button = None
                    is_painting = False
                    is_erasing = False

                else:
                    is_painting = False
                    is_erasing = False

            if event.type == pygame.MOUSEMOTION:
                if camera.is_panning:
                    camera.update_pan(event.pos)
                    continue

                if is_rect_tool_active:
                    if is_inside_canvas(screen, event.pos):
                        rect_end_cell = camera.screen_to_cell(event.pos)
                    continue

                if is_painting:
                    if is_inside_canvas(screen, event.pos):
                        paint_at_mouse(
                            scene_data,
                            mode,
                            selected_object_type,
                            object_definitions,
                            camera,
                            event.pos,
                        )

                if is_erasing:
                    if is_inside_canvas(screen, event.pos):
                        erase_at_mouse(
                            scene_data,
                            object_definitions,
                            camera,
                            event.pos,
                        )

        draw_editor_scene(
            screen,
            scene_data,
            object_definitions,
            sprites,
            camera,
        )

        draw_preview(
            screen,
            selected_object_type,
            object_definitions,
            sprites,
            camera,
        )

        buttons = draw_editor_panel(
            screen,
            mode,
            selected_object_type,
            camera.zoom,
            object_definitions,
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()