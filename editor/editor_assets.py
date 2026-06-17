from pathlib import Path

import pygame

from editor.object_editor.object_definition_repository import (
    load_object_definitions,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_object_sprite(object_definition, tile_size):
    visual = object_definition.get("visual", {})

    if not visual.get("sprite"):
        return None

    sprite_path = PROJECT_ROOT / visual["sprite"]

    try:
        image = pygame.image.load(sprite_path).convert_alpha()
    except pygame.error:
        return None

    if visual.get("visual_size"):
        visual_width = visual["visual_size"][0] * tile_size
        visual_height = visual["visual_size"][1] * tile_size
    elif visual.get("sprite_size"):
        visual_width = visual["sprite_size"][0]
        visual_height = visual["sprite_size"][1]
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
        visual = object_definition.get("visual", {})
        sprite_path = PROJECT_ROOT / visual.get("sprite", "")

        if not sprite_path.exists():
            continue

        sprite = load_object_sprite(
            object_definition,
            tile_size,
        )

        if sprite is not None:
            sprites[object_type] = sprite

    return sprites

