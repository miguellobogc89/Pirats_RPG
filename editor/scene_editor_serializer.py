import json
from pathlib import Path

from game.world.grid_manager import TILE_SIZE


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENES_DIR = PROJECT_ROOT / "data" / "scenes"
DEFAULT_SCENE_ID = "farm"
DEFAULT_SCENE_WIDTH = 80
DEFAULT_SCENE_HEIGHT = 60
DEFAULT_TILE_SIZE = TILE_SIZE


def get_scene_path(scene_id):
    return SCENES_DIR / f"{scene_id}.json"


def load_scene_for_editor(scene_id=DEFAULT_SCENE_ID):
    scene_path = get_scene_path(scene_id)

    if scene_path.exists():
        with scene_path.open("r", encoding="utf-8") as file:
            raw_scene = json.load(file)
    else:
        raw_scene = {
            "id": scene_id,
            "name": scene_id,
        }

    return normalize_scene_for_editor(raw_scene, fallback_scene_id=scene_id)


def save_scene_for_game(scene_data):
    normalized_scene = normalize_scene_for_game(scene_data)
    scene_path = get_scene_path(normalized_scene["id"])
    scene_path.parent.mkdir(parents=True, exist_ok=True)

    with scene_path.open("w", encoding="utf-8") as file:
        json.dump(normalized_scene, file, indent=2, ensure_ascii=False)

    return scene_path


def normalize_scene_for_editor(raw_scene, fallback_scene_id=DEFAULT_SCENE_ID):
    return normalize_scene(raw_scene, fallback_scene_id)


def normalize_scene_for_game(scene_data):
    return normalize_scene(scene_data, scene_data.get("id", DEFAULT_SCENE_ID))


def normalize_scene(raw_scene, fallback_scene_id):
    scene_id = raw_scene.get("id", fallback_scene_id)
    width, height = normalize_scene_size(raw_scene)

    return {
        "id": scene_id,
        "name": raw_scene.get("name", scene_id),
        "width": width,
        "height": height,
        "tile_size": DEFAULT_TILE_SIZE,
        "player_spawn": normalize_player_spawn(raw_scene),
        "objects": normalize_list(raw_scene.get("objects")),
        "collisions": normalize_collisions(raw_scene),
        "exits": normalize_list(raw_scene.get("exits")),
    }


def normalize_scene_size(raw_scene):
    if "width" in raw_scene and "height" in raw_scene:
        return raw_scene["width"], raw_scene["height"]

    map_size = raw_scene.get("map_size")

    if isinstance(map_size, list) and len(map_size) >= 2:
        return map_size[0], map_size[1]

    return DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT


def normalize_player_spawn(raw_scene):
    player_spawn = raw_scene.get("player_spawn")

    if isinstance(player_spawn, dict):
        return {
            "x": player_spawn.get("x", 0),
            "y": player_spawn.get("y", 0),
        }

    spawn = raw_scene.get("spawn")
    tile_size = raw_scene.get("tile_size", DEFAULT_TILE_SIZE)

    if isinstance(spawn, list) and len(spawn) >= 2:
        return {
            "x": spawn[0] * tile_size,
            "y": spawn[1] * tile_size,
        }

    return {
        "x": 0,
        "y": 0,
    }


def normalize_collisions(raw_scene):
    collisions = raw_scene.get("collisions")

    if isinstance(collisions, list):
        return collisions

    return normalize_list(raw_scene.get("collision_cells"))


def normalize_list(value):
    if isinstance(value, list):
        return value

    return []
