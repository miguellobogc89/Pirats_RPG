import json
from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OBJECT_DEFINITIONS_PATH = PROJECT_ROOT / "data" / "object_definitions.json"
OBJECT_DEFINITION_DIR = PROJECT_ROOT / "data" / "objects"


def load_object_definitions():
    object_definitions = {}

    if OBJECT_DEFINITIONS_PATH.exists():
        with open(OBJECT_DEFINITIONS_PATH, "r", encoding="utf-8") as file:
            object_definitions.update(json.load(file))

    if OBJECT_DEFINITION_DIR.exists():
        for object_path in sorted(OBJECT_DEFINITION_DIR.glob("*.json")):
            with open(object_path, "r", encoding="utf-8") as file:
                object_definition = json.load(file)

            object_id = object_definition.get("id", object_path.stem)
            object_definitions[object_id] = object_definition

    return object_definitions


def load_object_sprite(object_definition, tile_size):
    if not object_definition.get("sprite"):
        return None

    sprite_path = PROJECT_ROOT / object_definition["sprite"]

    try:
        image = pygame.image.load(sprite_path).convert_alpha()
    except pygame.error:
        return None

    if "visual_size" in object_definition:
        visual_width = object_definition["visual_size"][0] * tile_size
        visual_height = object_definition["visual_size"][1] * tile_size
    elif "sprite_size" in object_definition and object_definition["sprite_size"]:
        visual_width = object_definition["sprite_size"][0]
        visual_height = object_definition["sprite_size"][1]
    else:
        return image

    original_width = image.get_width()
    original_height = image.get_height()

    scale_x = visual_width / original_width
    scale_y = visual_height / original_height

    scale = min(scale_x, scale_y)

    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    image = pygame.transform.scale(image, (new_width, new_height))

    return image


def load_editor_sprites(object_definitions, tile_size):
    sprites = {}

    for object_type, object_definition in object_definitions.items():
        sprite_path = PROJECT_ROOT / object_definition["sprite"]

        if not sprite_path.exists():
            continue

        sprite = load_object_sprite(
            object_definition,
            tile_size,
        )

        if sprite is not None:
            sprites[object_type] = sprite

    return sprites
