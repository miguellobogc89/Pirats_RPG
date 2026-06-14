def generate_area_id(prefix, items):
    return f"{prefix}_{len(items) + 1:03d}"


def ensure_area_lists(scene_data):
    if "spawns" not in scene_data:
        scene_data["spawns"] = []

    if "exits" not in scene_data:
        scene_data["exits"] = []


def get_area_at_cell(items, cell):
    for area_data in items:
        if cell in area_data.get("cells", []):
            return area_data

    return None


def get_spawn_at_cell(scene_data, cell):
    ensure_area_lists(scene_data)
    return get_area_at_cell(scene_data["spawns"], cell)


def get_exit_at_cell(scene_data, cell):
    ensure_area_lists(scene_data)
    return get_area_at_cell(scene_data["exits"], cell)


def get_or_create_active_spawn(scene_data):
    ensure_area_lists(scene_data)

    if len(scene_data["spawns"]) == 0:
        scene_data["spawns"].append({
            "id": generate_area_id("spawn", scene_data["spawns"]),
            "name": "New Spawn",
            "cells": [],
            "spawn_cell": None,
        })

    return scene_data["spawns"][-1]


def get_or_create_active_exit(scene_data):
    ensure_area_lists(scene_data)

    if len(scene_data["exits"]) == 0:
        scene_data["exits"].append({
            "id": generate_area_id("exit", scene_data["exits"]),
            "name": "New Exit",
            "cells": [],
            "target_scene_id": "",
            "target_spawn_id": "",
        })

    return scene_data["exits"][-1]


def add_spawn_cell(scene_data, cell):
    if get_spawn_at_cell(scene_data, cell) is not None:
        return False

    spawn_data = get_or_create_active_spawn(scene_data)

    spawn_data["cells"].append(cell)

    if spawn_data.get("spawn_cell") is None:
        spawn_data["spawn_cell"] = cell

    return True


def remove_spawn_cell(scene_data, cell):
    spawn_data = get_spawn_at_cell(scene_data, cell)

    if spawn_data is None:
        return False

    spawn_data["cells"].remove(cell)

    if spawn_data.get("spawn_cell") == cell:
        if len(spawn_data["cells"]) > 0:
            spawn_data["spawn_cell"] = spawn_data["cells"][0]
        else:
            spawn_data["spawn_cell"] = None

    if len(spawn_data["cells"]) == 0:
        scene_data["spawns"].remove(spawn_data)

    return True


def add_exit_cell(scene_data, cell):
    if get_exit_at_cell(scene_data, cell) is not None:
        return False

    exit_data = get_or_create_active_exit(scene_data)

    exit_data["cells"].append(cell)

    return True


def remove_exit_cell(scene_data, cell):
    exit_data = get_exit_at_cell(scene_data, cell)

    if exit_data is None:
        return False

    exit_data["cells"].remove(cell)

    if len(exit_data["cells"]) == 0:
        scene_data["exits"].remove(exit_data)

    return True