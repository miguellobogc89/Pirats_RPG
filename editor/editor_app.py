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

from scene_editor_serializer import (
    DEFAULT_SCENE_ID,
    load_scene_for_editor,
    save_scene_for_game,
)


def load_scene(scene_id=DEFAULT_SCENE_ID):
    return load_scene_for_editor(scene_id)


def save_scene(scene_data):
    save_scene_for_game(scene_data)


def add_object(scene_data, object_type, cell):
    if object_type is None:
        return

    object_id = f"{object_type}_{len(scene_data['objects']) + 1:03d}"

    scene_data["objects"].append({
        "id": object_id,
        "type": object_type,
        "cell": cell,
    })


def add_collision_cell(scene_data, cell):
    if cell not in scene_data["collisions"]:
        scene_data["collisions"].append(cell)


def get_sprite_draw_position(cell, object_definition, sprite, camera):
    tile_size = camera.get_tile_size()

    footprint_width = object_definition["footprint"][0] * tile_size
    footprint_height = object_definition["footprint"][1] * tile_size

    anchor = object_definition.get("footprint_anchor", [0.5, 1.0])

    footprint_x = cell[0] * tile_size - camera.x
    footprint_y = cell[1] * tile_size - camera.y

    footprint_center_x = footprint_x + footprint_width / 2
    footprint_bottom_y = footprint_y + footprint_height

    anchor_x = sprite.get_width() * anchor[0]
    anchor_y = sprite.get_height() * anchor[1]

    return (
        int(footprint_center_x - anchor_x),
        int(footprint_bottom_y - anchor_y),
    )


def draw_object_footprint(screen, cell, footprint, color, camera):
    tile_size = camera.get_tile_size()

    rect = pygame.Rect(
        cell[0] * tile_size - camera.x,
        cell[1] * tile_size - camera.y,
        footprint[0] * tile_size,
        footprint[1] * tile_size,
    )

    pygame.draw.rect(screen, color, rect, 2)


def draw_scene_objects(screen, scene_data, object_definitions, sprites, camera):
    for object_data in scene_data["objects"]:
        object_type = object_data["type"]

        if object_type not in object_definitions:
            continue

        object_definition = object_definitions[object_type]
        cell = object_data["cell"]

        draw_object_footprint(
            screen,
            cell,
            object_definition["footprint"],
            (30, 80, 30),
            camera,
        )

        if object_type in sprites:
            sprite = pygame.transform.scale_by(
                sprites[object_type],
                camera.zoom,
            )

            draw_pos = get_sprite_draw_position(
                cell,
                object_definition,
                sprite,
                camera,
            )

            screen.blit(sprite, draw_pos)


def draw_collision_cells(screen, scene_data, camera):
    tile_size = camera.get_tile_size()

    for cell in scene_data["collisions"]:
        rect = pygame.Rect(
            cell[0] * tile_size - camera.x,
            cell[1] * tile_size - camera.y,
            tile_size,
            tile_size,
        )

        pygame.draw.rect(screen, (180, 60, 60), rect, 2)


def draw_preview(screen, selected_object_type, object_definitions, sprites, camera):
    if selected_object_type is None:
        return

    if selected_object_type not in object_definitions:
        return

    mouse_pos = pygame.mouse.get_pos()
    panel_start_x = screen.get_width() - PANEL_WIDTH

    if mouse_pos[0] >= panel_start_x:
        return

    cell = camera.screen_to_cell(mouse_pos)
    object_definition = object_definitions[selected_object_type]

    draw_object_footprint(
        screen,
        cell,
        object_definition["footprint"],
        (80, 180, 255),
        camera,
    )

    if selected_object_type in sprites:
        preview_sprite = pygame.transform.scale_by(
            sprites[selected_object_type],
            camera.zoom,
        )

        preview_sprite.set_alpha(140)

        draw_pos = get_sprite_draw_position(
            cell,
            object_definition,
            preview_sprite,
            camera,
        )

        screen.blit(preview_sprite, draw_pos)


def draw_grid(screen, map_width, map_height, camera):
    tile_size = camera.get_tile_size()

    start_x = max(0, int(camera.x // tile_size))
    end_x = min(
        map_width,
        int((camera.x + screen.get_width()) // tile_size) + 2,
    )

    start_y = max(0, int(camera.y // tile_size))
    end_y = min(
        map_height,
        int((camera.y + screen.get_height()) // tile_size) + 2,
    )

    for grid_x in range(start_x, end_x + 1):
        x = grid_x * tile_size - camera.x

        pygame.draw.line(
            screen,
            (100, 140, 90),
            (x, 0),
            (x, map_height * tile_size - camera.y),
        )

    for grid_y in range(start_y, end_y + 1):
        y = grid_y * tile_size - camera.y

        pygame.draw.line(
            screen,
            (100, 140, 90),
            (0, y),
            (map_width * tile_size - camera.x, y),
        )


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


def paint_at_mouse(scene_data, mode, selected_object_type, object_definitions, camera, mouse_pos):
    cell = camera.screen_to_cell(mouse_pos)

    if mode == "objects" and selected_object_type:
        add_object(
            scene_data,
            selected_object_type,
            cell,
        )

    if mode == "collisions":
        add_collision_cell(scene_data, cell)


def main():
    pygame.init()

    scene_data = load_scene()
    object_definitions = load_object_definitions()

    map_width = scene_data["width"]
    map_height = scene_data["height"]

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

                clicked_action = get_clicked_panel_action(event.pos, buttons)

                if clicked_action:
                    action = clicked_action["action"]

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
                else:
                    is_painting = False

            if event.type == pygame.MOUSEMOTION:
                if camera.is_panning:
                    camera.update_pan(event.pos)
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

        draw_grid(screen, map_width, map_height, camera)

        draw_collision_cells(screen, scene_data, camera)

        draw_scene_objects(
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