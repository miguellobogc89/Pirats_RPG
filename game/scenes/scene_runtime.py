import json
from pathlib import Path

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OBJECT_DEFINITIONS_PATH = PROJECT_ROOT / "data" / "object_definitions.json"

GAMEPLAY_OBJECT_DEFAULTS = {
    "tree": {
        "name": "Arbol",
        "type": "tree",
        "icon": "T",
        "required_tool": "axe",
        "energy_cost": 2,
        "hp": 3,
        "drops": {
            "on_hit": [],
            "on_destroy": [
                {"item_id": "wood", "amount": [4, 8], "chance": 100},
            ],
        },
    },
    "bush": {
        "name": "Arbusto",
        "type": "bush",
        "icon": "B",
        "required_tool": None,
        "energy_cost": 1,
        "hp": 1,
        "drops": {
            "on_hit": [],
            "on_destroy": [
                {"item_id": "food", "amount": [2, 5], "chance": 100},
            ],
        },
    },
    "small_rock": {
        "name": "Roca",
        "type": "rock",
        "icon": "R",
        "required_tool": "pickaxe",
        "energy_cost": 3,
        "hp": 3,
        "drops": {
            "on_hit": [
                {"item_id": "stone", "amount": [1, 2], "chance": 45},
            ],
            "on_destroy": [
                {"item_id": "stone", "amount": [3, 5], "chance": 100},
            ],
        },
    },
    "big_rock": {
        "name": "Roca",
        "type": "rock",
        "icon": "R",
        "required_tool": "pickaxe",
        "energy_cost": 3,
        "hp": 4,
        "drops": {
            "on_hit": [
                {"item_id": "stone", "amount": [1, 2], "chance": 45},
            ],
            "on_destroy": [
                {"item_id": "stone", "amount": [4, 7], "chance": 100},
                {"item_id": "iron", "amount": [1, 3], "chance": 60},
                {"item_id": "carbon", "amount": [1, 2], "chance": 35},
            ],
        },
    },
    "house": {
        "name": "Casa",
        "type": "house",
        "icon": "H",
        "required_tool": None,
        "energy_cost": 0,
        "hp": 1,
    },
    "dock": {
        "name": "Muelle",
        "type": "dock",
        "icon": "D",
        "required_tool": None,
        "energy_cost": 0,
        "hp": 1,
    },
    "ship": {
        "name": "Barco",
        "type": "ship",
        "icon": "S",
        "required_tool": None,
        "energy_cost": 0,
        "hp": 1,
    },
    "bed": {
        "name": "Cama",
        "type": "bed",
        "icon": "B",
        "required_tool": None,
        "energy_cost": 0,
        "hp": 1,
    },
    "stash": {
        "name": "Cofre",
        "type": "stash",
        "icon": "C",
        "required_tool": None,
        "energy_cost": 0,
        "hp": 1,
    },
}


def load_object_definitions():
    if not OBJECT_DEFINITIONS_PATH.exists():
        return {}

    with OBJECT_DEFINITIONS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_scene_world_objects(scene_data):
    object_definitions = load_object_definitions()
    scene_objects = []

    for object_data in scene_data.get("objects", []):
        object_type = object_data.get("type")
        object_definition = object_definitions.get(object_type, {})
        cell = object_data.get("cell", [0, 0])

        scene_object = build_scene_world_object(
            object_data,
            object_definition,
            scene_data.get("tile_size", 16),
        )

        if scene_object is None:
            continue

        scene_objects.append(scene_object)

    return scene_objects


def build_scene_world_object(object_data, object_definition, scene_tile_size):
    cell = object_data.get("cell")

    if not isinstance(cell, list) or len(cell) < 2:
        return None

    object_type = object_data.get("type", "object")
    defaults = GAMEPLAY_OBJECT_DEFAULTS.get(object_type, {})
    footprint = object_definition.get("footprint", [1, 1])
    visual_size = object_definition.get("visual_size", footprint)
    world_x = cell[0] * scene_tile_size + footprint[0] * scene_tile_size / 2
    world_y = cell[1] * scene_tile_size + footprint[1] * scene_tile_size / 2
    radius = max(16, int(max(visual_size) * scene_tile_size / 2))
    hp = defaults.get("hp", 1)

    return {
        "id": object_data.get("id", f"{object_type}_{cell[0]}_{cell[1]}"),
        "name": object_data.get("name", defaults.get("name", object_type)),
        "type": defaults.get("type", object_type),
        "source_type": object_type,
        "x": world_x,
        "y": world_y,
        "radius": radius,
        "icon": defaults.get("icon", "?"),
        "sprite": object_definition.get("sprite"),
        "footprint": footprint,
        "scene_cell": cell,
        "scene_tile_size": scene_tile_size,
        "hp": object_data.get("hp", hp),
        "max_hp": object_data.get("max_hp", hp),
        "required_tool": defaults.get("required_tool"),
        "energy_cost": defaults.get("energy_cost", 0),
        "drops": defaults.get("drops", {"on_hit": [], "on_destroy": []}),
    }


def build_scene_collision_rects(scene_data, scene_objects):
    tile_size = scene_data.get("tile_size", 16)
    collision_rects = []

    for collision in scene_data.get("collisions", []):
        rect = collision_to_rect(collision, tile_size)

        if rect is not None:
            collision_rects.append(rect)

    object_definitions = load_object_definitions()

    for scene_object in scene_objects:
        object_definition = object_definitions.get(scene_object.get("source_type"), {})

        if not object_definition.get("solid", False):
            continue

        cell = scene_object.get("scene_cell")
        footprint = scene_object.get("footprint", [1, 1])

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
