from pathlib import Path
import pygame

from game.data.object_definition_repository import load_object_definitions
from game.scenes.scene_loader import load_scene_data


def load_scene(scene_id):
    object_definitions = load_object_definitions()
    scene_data = load_scene_data(scene_id)

    return {
        "scene": scene_data,
        "object_definitions": object_definitions,
    }


def load_object_sprite(object_definition, tile_size):
    visual = object_definition["visual"]
    sprite_path = visual["sprite"]
    if not Path(sprite_path).exists():
        return None

    visual_size = visual.get("visual_size")

    if visual_size is not None:
        visual_width = visual_size[0] * tile_size
        visual_height = visual_size[1] * tile_size
    elif visual.get("sprite_size") is not None:
        visual_width = visual["sprite_size"][0]
        visual_height = visual["sprite_size"][1]
    else:
        visual_width = object_definition["collision"]["footprint"][0] * tile_size
        visual_height = object_definition["collision"]["footprint"][1] * tile_size

    try:
        image = pygame.image.load(sprite_path).convert_alpha()
    except pygame.error:
        return None

    image = pygame.transform.scale(image, (visual_width, visual_height))

    return image


def build_scene_objects(scene_data, object_definitions):
    tile_size = scene_data["tile_size"]
    built_objects = []

    for object_data in scene_data["objects"]:
        object_type = object_data["type"]
        object_definition = object_definitions[object_type]

        sprite = load_object_sprite(object_definition, tile_size)

        cell_x = object_data["cell"][0]
        cell_y = object_data["cell"][1]

        pixel_x = cell_x * tile_size
        pixel_y = cell_y * tile_size

        built_objects.append({
            "id": object_data["id"],
            "type": object_type,
            "cell": object_data["cell"],
            "position": [pixel_x, pixel_y],
            "sprite": sprite,
            "definition": object_definition,
        })

    return built_objects
