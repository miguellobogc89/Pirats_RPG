import json
from pathlib import Path

from game.scenes.scene_database import SCENE_DATABASE
from game.world.grid_manager import TILE_SIZE


SCENES_DIR = Path(__file__).resolve().parents[2] / "data" / "scenes"
DEFAULT_SCENE_WIDTH = 80
DEFAULT_SCENE_HEIGHT = 60
DEFAULT_TILE_SIZE = TILE_SIZE


def scene_exists(scene_id):
    return scene_id in SCENE_DATABASE or get_scene_path(scene_id).exists()


def get_scene_path(scene_id):
    return SCENES_DIR / f"{scene_id}.json"


def load_scene_data(scene_id):
    if get_scene_path(scene_id).exists():
        raw_scene = load_scene_file(scene_id)
    else:
        raw_scene = SCENE_DATABASE.get(scene_id)

    if raw_scene is None:
        return None

    return normalize_scene_data(raw_scene, fallback_scene_id=scene_id)


def load_scene_file(scene_id):
    with get_scene_path(scene_id).open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_scene_data(raw_scene, fallback_scene_id=None):
    scene_id = raw_scene.get("id", fallback_scene_id)
    tile_size = raw_scene.get("tile_size", DEFAULT_TILE_SIZE)
    width, height = normalize_scene_size(raw_scene)

    return {
        "id": scene_id,
        "name": raw_scene.get("name", scene_id),
        "width": width,
        "height": height,
        "tile_size": tile_size,
        "player_spawn": normalize_player_spawn(raw_scene, tile_size),
        "objects": normalize_objects(raw_scene),
        "collisions": normalize_collisions(raw_scene),
        "spawns": normalize_spawns(raw_scene),
        "exits": normalize_exits(raw_scene),
    }


def normalize_scene_size(raw_scene):
    if "width" in raw_scene and "height" in raw_scene:
        return raw_scene["width"], raw_scene["height"]

    map_size = raw_scene.get("map_size")

    if isinstance(map_size, list) and len(map_size) >= 2:
        return map_size[0], map_size[1]

    return DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT


def normalize_player_spawn(raw_scene, tile_size):
    player_spawn = raw_scene.get("player_spawn")

    if isinstance(player_spawn, dict):
        return {
            "x": player_spawn.get("x", 0),
            "y": player_spawn.get("y", 0),
        }

    legacy_spawn = raw_scene.get("spawn")

    if isinstance(legacy_spawn, list) and len(legacy_spawn) >= 2:
        return {
            "x": legacy_spawn[0] * tile_size,
            "y": legacy_spawn[1] * tile_size,
        }

    return {
        "x": 0,
        "y": 0,
    }


def normalize_list_field(raw_scene, field_name):
    value = raw_scene.get(field_name, [])

    if isinstance(value, list):
        return value

    return []


def normalize_objects(raw_scene):
    normalized_objects = []

    for object_data in normalize_list_field(raw_scene, "objects"):
        if not isinstance(object_data, dict):
            continue

        object_type = object_data.get("type")
        cell = object_data.get("cell")

        if not object_type:
            continue

        if not isinstance(cell, list) or len(cell) < 2:
            continue

        properties = object_data.get("properties")
        if not isinstance(properties, dict):
            properties = {}

        normalized_object = dict(object_data)
        normalized_object["id"] = normalized_object.get(
            "id",
            f"{object_type}_{cell[0]}_{cell[1]}",
        )
        normalized_object["type"] = object_type
        normalized_object["definition_id"] = normalized_object.get(
            "definition_id",
            object_type,
        )
        normalized_object["cell"] = [cell[0], cell[1]]
        normalized_object["properties"] = {
            str(key): str(value)
            for key, value in properties.items()
            if str(key).strip() != ""
        }
        normalized_objects.append(normalized_object)

    return normalized_objects


def normalize_collisions(raw_scene):
    collisions = raw_scene.get("collisions")

    if isinstance(collisions, list):
        return collisions

    legacy_collision_cells = raw_scene.get("collision_cells")

    if isinstance(legacy_collision_cells, list):
        return legacy_collision_cells

    return []


def normalize_spawns(raw_scene):
    spawns = []

    for spawn_data in normalize_list_field(raw_scene, "spawns"):
        if not isinstance(spawn_data, dict):
            continue

        cells = normalize_cells(spawn_data)
        spawn_cell = spawn_data.get("spawn_cell")

        if spawn_cell not in cells:
            if cells:
                spawn_cell = cells[0]
            else:
                spawn_cell = None

        spawns.append({
            "id": spawn_data.get("id", "spawn"),
            "name": spawn_data.get("name", spawn_data.get("id", "spawn")),
            "cells": cells,
            "spawn_cell": spawn_cell,
        })

    return spawns


def normalize_exits(raw_scene):
    exits = []

    for exit_data in normalize_list_field(raw_scene, "exits"):
        if not isinstance(exit_data, dict):
            continue

        exits.append({
            "id": exit_data.get("id", "exit"),
            "name": exit_data.get("name", exit_data.get("id", "exit")),
            "cells": normalize_cells(exit_data),
            "target_links": normalize_target_links(exit_data),
        })

    return exits


def normalize_cells(area_data):
    cells = area_data.get("cells")

    if not isinstance(cells, list):
        legacy_cell = area_data.get("cell")

        if isinstance(legacy_cell, list) and len(legacy_cell) >= 2:
            cells = [legacy_cell]
        else:
            cells = []

    normalized_cells = []

    for cell in cells:
        if not isinstance(cell, list) or len(cell) < 2:
            continue

        normalized_cell = [cell[0], cell[1]]

        if normalized_cell not in normalized_cells:
            normalized_cells.append(normalized_cell)

    return normalized_cells


def normalize_target_links(exit_data):
    links = []

    if isinstance(exit_data.get("target_links"), list):
        links.extend(exit_data["target_links"])

    legacy_scene_id = exit_data.get("target_scene_id")
    legacy_spawn_id = exit_data.get("target_spawn_id")

    if legacy_scene_id and legacy_spawn_id:
        links.append({
            "target_scene_id": legacy_scene_id,
            "target_spawn_id": legacy_spawn_id,
        })

    normalized_links = []
    seen = set()

    for link in links:
        if not isinstance(link, dict):
            continue

        target_scene_id = link.get("target_scene_id")
        target_spawn_id = link.get("target_spawn_id")

        if not target_scene_id or not target_spawn_id:
            continue

        key = (target_scene_id, target_spawn_id)

        if key in seen:
            continue

        seen.add(key)
        normalized_links.append({
            "target_scene_id": target_scene_id,
            "target_spawn_id": target_spawn_id,
        })

    return normalized_links
