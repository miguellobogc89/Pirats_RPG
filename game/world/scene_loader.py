import json
from pathlib import Path
import pygame

from game.scenes.scene_loader import load_scene_data


OBJECT_DEFINITIONS_PATH = "data/object_definitions.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_scene(scene_id):
    object_definitions = load_json(OBJECT_DEFINITIONS_PATH)
    scene_data = load_scene_data(scene_id)

    return {
        "scene": scene_data,
        "object_definitions": object_definitions,
    }


def load_object_sprite(object_definition, tile_size):
    sprite_path = object_definition["sprite"]
    if not Path(sprite_path).exists():
        return None

    visual_width = object_definition["visual_size"][0] * tile_size
    visual_height = object_definition["visual_size"][1] * tile_size

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
