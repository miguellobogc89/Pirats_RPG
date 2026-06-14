import pygame

from editor.editor_ui import PANEL_WIDTH


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


def draw_rect_tool_preview(screen, rect_preview_data, camera):
    if rect_preview_data is None:
        return

    start_cell = rect_preview_data["start_cell"]
    end_cell = rect_preview_data["end_cell"]
    button = rect_preview_data["button"]

    min_x = min(start_cell[0], end_cell[0])
    max_x = max(start_cell[0], end_cell[0])
    min_y = min(start_cell[1], end_cell[1])
    max_y = max(start_cell[1], end_cell[1])

    tile_size = camera.get_tile_size()

    rect = pygame.Rect(
        min_x * tile_size - camera.x,
        min_y * tile_size - camera.y,
        (max_x - min_x + 1) * tile_size,
        (max_y - min_y + 1) * tile_size,
    )

    color = (80, 180, 255)

    if button == 3:
        color = (230, 80, 80)

    pygame.draw.rect(screen, color, rect, 3)

def draw_editor_scene(screen, scene_data, object_definitions, sprites, camera):
    map_width = scene_data["width"]
    map_height = scene_data["height"]

    draw_grid(screen, map_width, map_height, camera)
    draw_collision_cells(screen, scene_data, camera)

    draw_scene_objects(
        screen,
        scene_data,
        object_definitions,
        sprites,
        camera,
    )