import json
from pathlib import Path

import pygame

from editor_assets import (
    load_editor_sprites,
    load_object_definitions,
)

from editor_ui import (
    PANEL_WIDTH,
    draw_editor_panel,
    get_clicked_panel_action,
)


TILE_SIZE = 16

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENE_PATH = PROJECT_ROOT / "data" / "scenes" / "farm.json"


def load_scene():
    with open(SCENE_PATH, "r", encoding="utf-8") as file:
        scene_data = json.load(file)

    if "collision_cells" not in scene_data:
        scene_data["collision_cells"] = []

    return scene_data


def save_scene(scene_data):
    with open(SCENE_PATH, "w", encoding="utf-8") as file:
        json.dump(scene_data, file, indent=2)


def add_object(scene_data, object_type, cell):
    object_id = f"{object_type}_{len(scene_data['objects']) + 1:03d}"

    scene_data["objects"].append({
        "id": object_id,
        "type": object_type,
        "cell": cell,
    })


def add_collision_cell(scene_data, cell):
    if cell not in scene_data["collision_cells"]:
        scene_data["collision_cells"].append(cell)


def get_scaled_tile_size(zoom):
    return int(TILE_SIZE * zoom)


def screen_to_cell(pos, zoom):
    tile_size = get_scaled_tile_size(zoom)

    return [
        pos[0] // tile_size,
        pos[1] // tile_size,
    ]


def get_sprite_draw_position(cell, object_definition, sprite, zoom):
    tile_size = get_scaled_tile_size(zoom)

    footprint_width = object_definition["footprint"][0] * tile_size
    footprint_height = object_definition["footprint"][1] * tile_size

    anchor = object_definition.get("footprint_anchor", [0.5, 1.0])

    footprint_x = cell[0] * tile_size
    footprint_y = cell[1] * tile_size

    footprint_center_x = footprint_x + footprint_width / 2
    footprint_bottom_y = footprint_y + footprint_height

    anchor_x = sprite.get_width() * anchor[0]
    anchor_y = sprite.get_height() * anchor[1]

    return (
        int(footprint_center_x - anchor_x),
        int(footprint_bottom_y - anchor_y),
    )


def draw_object_footprint(screen, cell, footprint, color, zoom):
    tile_size = get_scaled_tile_size(zoom)

    rect = pygame.Rect(
        cell[0] * tile_size,
        cell[1] * tile_size,
        footprint[0] * tile_size,
        footprint[1] * tile_size,
    )

    pygame.draw.rect(screen, color, rect, 2)


def draw_scene_objects(screen, scene_data, object_definitions, sprites, zoom):
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
            zoom,
        )

        if object_type in sprites:
            sprite = pygame.transform.scale_by(
                sprites[object_type],
                zoom,
            )

            draw_pos = get_sprite_draw_position(
                cell,
                object_definition,
                sprite,
                zoom,
            )

            screen.blit(sprite, draw_pos)


def draw_collision_cells(screen, scene_data, zoom):
    tile_size = get_scaled_tile_size(zoom)

    for cell in scene_data["collision_cells"]:
        rect = pygame.Rect(
            cell[0] * tile_size,
            cell[1] * tile_size,
            tile_size,
            tile_size,
        )

        pygame.draw.rect(screen, (180, 60, 60), rect, 2)


def draw_preview(screen, selected_object_type, object_definitions, sprites, zoom):
    if selected_object_type is None:
        return

    if selected_object_type not in object_definitions:
        return

    mouse_pos = pygame.mouse.get_pos()
    panel_start_x = screen.get_width() - PANEL_WIDTH

    if mouse_pos[0] >= panel_start_x:
        return

    cell = screen_to_cell(mouse_pos, zoom)
    object_definition = object_definitions[selected_object_type]

    draw_object_footprint(
        screen,
        cell,
        object_definition["footprint"],
        (80, 180, 255),
        zoom,
    )

    if selected_object_type in sprites:
        preview_sprite = pygame.transform.scale_by(
            sprites[selected_object_type],
            zoom,
        )

        preview_sprite.set_alpha(140)

        draw_pos = get_sprite_draw_position(
            cell,
            object_definition,
            preview_sprite,
            zoom,
        )

        screen.blit(preview_sprite, draw_pos)


def draw_grid(screen, map_width, map_height, zoom):
    tile_size = get_scaled_tile_size(zoom)

    for x in range(0, map_width * tile_size, tile_size):
        pygame.draw.line(
            screen,
            (100, 140, 90),
            (x, 0),
            (x, map_height * tile_size),
        )

    for y in range(0, map_height * tile_size, tile_size):
        pygame.draw.line(
            screen,
            (100, 140, 90),
            (0, y),
            (map_width * tile_size, y),
        )


def main():
    pygame.init()

    scene_data = load_scene()
    object_definitions = load_object_definitions()

    map_width = scene_data["map_size"][0]
    map_height = scene_data["map_size"][1]

    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("RPG Scene Editor")

    sprites = load_editor_sprites(object_definitions, TILE_SIZE)

    clock = pygame.time.Clock()

    mode = "objects"
    selected_object_type = None
    buttons = []
    zoom = 1.0

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

                if event.key == pygame.K_s:
                    save_scene(scene_data)

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_action = get_clicked_panel_action(event.pos, buttons)

                if clicked_action:
                    action = clicked_action["action"]

                    if action == "mode_objects":
                        mode = "objects"

                    if action == "mode_collisions":
                        mode = "collisions"
                        selected_object_type = None

                    if action == "select_object":
                        mode = "objects"
                        selected_object_type = clicked_action["object_type"]

                    if action == "zoom_in":
                        zoom += 0.25

                    if action == "zoom_out":
                        zoom -= 0.25

                        if zoom < 0.5:
                            zoom = 0.5

                else:
                    panel_start_x = screen.get_width() - PANEL_WIDTH

                    if event.pos[0] < panel_start_x:
                        cell = screen_to_cell(event.pos, zoom)

                        if mode == "objects" and selected_object_type:
                            add_object(
                                scene_data,
                                selected_object_type,
                                cell,
                            )
                            is_painting = True

                        if mode == "collisions":
                            add_collision_cell(scene_data, cell)
                            is_painting = True

            if event.type == pygame.MOUSEBUTTONUP:
                is_painting = False

            if event.type == pygame.MOUSEMOTION and is_painting:
                panel_start_x = screen.get_width() - PANEL_WIDTH

                if event.pos[0] < panel_start_x:
                    cell = screen_to_cell(event.pos, zoom)

                    if mode == "objects" and selected_object_type:
                        add_object(
                            scene_data,
                            selected_object_type,
                            cell,
                        )

                    if mode == "collisions":
                        add_collision_cell(scene_data, cell)

        draw_grid(screen, map_width, map_height, zoom)

        draw_collision_cells(screen, scene_data, zoom)

        draw_scene_objects(
            screen,
            scene_data,
            object_definitions,
            sprites,
            zoom,
        )

        draw_preview(
            screen,
            selected_object_type,
            object_definitions,
            sprites,
            zoom,
        )

        buttons = draw_editor_panel(
            screen,
            mode,
            selected_object_type,
            zoom,
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()