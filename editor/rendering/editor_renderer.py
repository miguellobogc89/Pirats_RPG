import pygame

from editor.editor_ui import PANEL_WIDTH
from editor.terrain.terrain_renderer import draw_editor_terrain
from game.world.object_sprite_layout import (
    get_object_footprint_rect,
    get_object_sprite_rect,
)


def get_sprite_draw_position(cell, object_definition, sprite, camera):
    tile_size = camera.get_tile_size()
    sprite_size = object_definition.get("sprite_size")

    if sprite_size is None:
        sprite_size = [sprite.get_width(), sprite.get_height()]

    sprite_rect = get_object_sprite_rect(
        cell,
        object_definition.get("footprint", [1, 1]),
        [sprite_size[0] * camera.zoom, sprite_size[1] * camera.zoom],
        [
            object_definition.get("sprite_offset", [0, 0])[0] * camera.zoom,
            object_definition.get("sprite_offset", [0, 0])[1] * camera.zoom,
        ],
        tile_size=tile_size,
        camera_offset=(camera.x, camera.y),
    )
    return sprite_rect.topleft


def draw_object_footprint(screen, cell, footprint, color, camera):
    tile_size = camera.get_tile_size()

    rect = get_object_footprint_rect(
        cell,
        footprint,
        tile_size=tile_size,
        camera_offset=(camera.x, camera.y),
    )

    pygame.draw.rect(screen, color, rect, 2)


def draw_scene_objects(
    screen,
    scene_data,
    object_definitions,
    sprites,
    camera,
    selected_scene_object_id=None,
):
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
            (245, 220, 90) if object_data.get("id") == selected_scene_object_id else (30, 80, 30),
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

        if object_data.get("id") == selected_scene_object_id:
            draw_object_footprint(
                screen,
                cell,
                object_definition["footprint"],
                (255, 255, 255),
                camera,
            )


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

    start_x = int(camera.x // tile_size) - 2
    end_x = int((camera.x + screen.get_width()) // tile_size) + 2

    start_y = int(camera.y // tile_size) - 2
    end_y = int((camera.y + screen.get_height()) // tile_size) + 2

    for grid_x in range(start_x, end_x + 1):
        x = grid_x * tile_size - camera.x

        pygame.draw.line(
            screen,
            (45, 65, 45),
            (x, 0),
            (x, map_height * tile_size - camera.y),
        )

    for grid_y in range(start_y, end_y + 1):
        y = grid_y * tile_size - camera.y

        pygame.draw.line(
            screen,
            (45, 65, 45),
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


def draw_spawn_cells(screen, scene_data, camera):
    tile_size = camera.get_tile_size()

    for spawn_data in scene_data.get("spawns", []):
        for cell in spawn_data.get("cells", []):
            rect = pygame.Rect(
                cell[0] * tile_size - camera.x,
                cell[1] * tile_size - camera.y,
                tile_size,
                tile_size,
            )

            pygame.draw.rect(screen, (80, 220, 120), rect, 3)

        spawn_cell = spawn_data.get("spawn_cell")

        if spawn_cell is not None:
            center_x = spawn_cell[0] * tile_size - camera.x + tile_size // 2
            center_y = spawn_cell[1] * tile_size - camera.y + tile_size // 2

            pygame.draw.circle(
                screen,
                (120, 255, 160),
                (int(center_x), int(center_y)),
                max(4, tile_size // 5),
            )


def draw_exit_cells(screen, scene_data, camera):
    tile_size = camera.get_tile_size()

    for exit_data in scene_data.get("exits", []):
        for cell in exit_data.get("cells", []):
            rect = pygame.Rect(
                cell[0] * tile_size - camera.x,
                cell[1] * tile_size - camera.y,
                tile_size,
                tile_size,
            )

            pygame.draw.rect(screen, (240, 190, 70), rect, 3)


def get_area_at_mouse(screen, scene_data, camera):
    mouse_pos = pygame.mouse.get_pos()

    if mouse_pos[0] >= screen.get_width() - PANEL_WIDTH:
        return None

    cell = camera.screen_to_cell(mouse_pos)

    for spawn_data in scene_data.get("spawns", []):
        if cell in spawn_data.get("cells", []):
            return spawn_data

    for exit_data in scene_data.get("exits", []):
        if cell in exit_data.get("cells", []):
            return exit_data

    return None


def draw_area_tooltip(screen, scene_data, camera):
    area_data = get_area_at_mouse(screen, scene_data, camera)

    if area_data is None:
        return

    label = area_data.get("name", area_data.get("id", "area"))
    font = pygame.font.SysFont("consolas", 14)
    text = font.render(label, True, (245, 245, 235))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    padding = 6
    rect = pygame.Rect(
        mouse_x + 14,
        mouse_y + 14,
        text.get_width() + padding * 2,
        text.get_height() + padding * 2,
    )

    if rect.right > screen.get_width():
        rect.x = mouse_x - rect.width - 14

    if rect.bottom > screen.get_height():
        rect.y = mouse_y - rect.height - 14

    pygame.draw.rect(screen, (28, 30, 34), rect)
    pygame.draw.rect(screen, (110, 116, 126), rect, 1)
    screen.blit(text, (rect.x + padding, rect.y + padding))


def draw_editor_scene(
    screen,
    scene_data,
    object_definitions,
    sprites,
    camera,
    selected_scene_object_id=None,
):
    map_width = scene_data["width"]
    map_height = scene_data["height"]

    draw_editor_terrain(screen, scene_data, camera)
    draw_grid(screen, map_width, map_height, camera)
    draw_collision_cells(screen, scene_data, camera)
    draw_spawn_cells(screen, scene_data, camera)
    draw_exit_cells(screen, scene_data, camera)

    draw_scene_objects(
        screen,
        scene_data,
        object_definitions,
        sprites,
        camera,
        selected_scene_object_id,
    )
    draw_area_tooltip(screen, scene_data, camera)
