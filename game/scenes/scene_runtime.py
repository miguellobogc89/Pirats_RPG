from pathlib import Path

import pygame

from game.data.object_definition_repository import (
    load_object_definitions as load_repository_object_definitions,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_object_definitions():
    return load_repository_object_definitions()


def build_scene_world_objects(scene_data):
    object_definitions = load_object_definitions()
    scene_objects = []

    for object_data in scene_data.get("objects", []):
        object_type = object_data.get("type")
        object_definition = object_definitions.get(object_type)

        if object_definition is None:
            continue

        if object_definition["functional_type"] == "npc":
            continue

        scene_object = build_scene_world_object(
            object_data,
            object_definition,
            scene_data.get("tile_size", 16),
        )

        if scene_object is not None:
            scene_objects.append(scene_object)

    return scene_objects


def build_scene_world_object(object_data, object_definition, scene_tile_size):
    cell = object_data.get("cell")

    if not isinstance(cell, list) or len(cell) < 2:
        return None

    object_type = object_data.get("type", "object")
    visual = object_definition["visual"]
    collision = object_definition["collision"]
    functional_type = object_definition["functional_type"]
    functional_data = dict(object_definition.get(functional_type, {}))
    footprint = collision["footprint"]
    visual_size = get_visual_size(visual, footprint, scene_tile_size)
    world_x = cell[0] * scene_tile_size + footprint[0] * scene_tile_size / 2
    world_y = cell[1] * scene_tile_size + footprint[1] * scene_tile_size / 2
    radius = max(16, int(max(visual_size) * scene_tile_size / 2))
    hp = get_runtime_hp(functional_type, functional_data, object_data)

    return {
        "id": object_data.get("id", f"{object_type}_{cell[0]}_{cell[1]}"),
        "name": object_data.get("name", object_definition.get("name", object_type)),
        "type": object_type,
        "functional_type": functional_type,
        "functional_data": functional_data,
        "properties": dict(object_data.get("properties", {})),
        "x": world_x,
        "y": world_y,
        "radius": radius,
        "sprite": visual["sprite"],
        "sprite_offset": visual["sprite_offset"],
        "sprite_size": visual["sprite_size"],
        "footprint": footprint,
        "solid": collision["solid"],
        "scene_cell": cell,
        "scene_tile_size": scene_tile_size,
        "hp": hp,
        "max_hp": hp,
    }


def get_visual_size(visual, footprint, scene_tile_size):
    visual_size = visual.get("visual_size")

    if visual_size is not None:
        return visual_size

    sprite_size = visual.get("sprite_size")

    if sprite_size is not None:
        return [
            max(1, sprite_size[0] / scene_tile_size),
            max(1, sprite_size[1] / scene_tile_size),
        ]

    return footprint


def get_runtime_hp(functional_type, functional_data, object_data):
    if functional_type != "destructible":
        return 1

    hp = object_data.get("hp", functional_data.get("hp", 1))

    try:
        return max(1, int(hp))
    except (TypeError, ValueError):
        return 1


def build_scene_collision_rects(scene_data, scene_objects):
    tile_size = scene_data.get("tile_size", 16)
    collision_rects = []

    for collision in scene_data.get("collisions", []):
        rect = collision_to_rect(collision, tile_size)

        if rect is not None:
            collision_rects.append(rect)

    for scene_object in scene_objects:
        if not scene_object_is_solid(scene_object):
            continue

        cell = scene_object.get("scene_cell")
        footprint = scene_object.get("footprint")

        if not isinstance(cell, list) or len(cell) < 2:
            continue

        collision_rects.append(
            pygame.Rect(
                cell[0] * tile_size,
                cell[1] * tile_size,
                footprint[0] * tile_size,
                footprint[1] * tile_size,
            )
        )

    return collision_rects


def scene_object_is_solid(scene_object):
    return bool(scene_object.get("solid", False))


def collision_to_rect(collision, tile_size):
    if isinstance(collision, list) and len(collision) >= 2:
        return pygame.Rect(
            collision[0] * tile_size,
            collision[1] * tile_size,
            tile_size,
            tile_size,
        )

    if isinstance(collision, dict):
        return pygame.Rect(
            collision.get("x", 0),
            collision.get("y", 0),
            collision.get("w", tile_size),
            collision.get("h", tile_size),
        )

    return None
