def generate_area_id(prefix, items):
    return f"{prefix}_{len(items) + 1:03d}"


def ensure_area_lists(scene_data):
    if "spawns" not in scene_data:
        scene_data["spawns"] = []

    if "exits" not in scene_data:
        scene_data["exits"] = []

    normalize_area_list(scene_data["spawns"], "spawn")
    normalize_area_list(scene_data["exits"], "exit")


def normalize_area_list(items, prefix):
    for area_data in items:
        if "cells" not in area_data:
            if "cell" in area_data:
                area_data["cells"] = [area_data["cell"]]
                del area_data["cell"]
            else:
                area_data["cells"] = []

        if "id" not in area_data:
            area_data["id"] = generate_area_id(prefix, items)

        if "name" not in area_data:
            area_data["name"] = area_data["id"]

        if prefix == "spawn":
            if "spawn_cell" not in area_data:
                if len(area_data["cells"]) > 0:
                    area_data["spawn_cell"] = area_data["cells"][0]
                else:
                    area_data["spawn_cell"] = None

        if prefix == "exit":
            if "target_links" not in area_data:
                area_data["target_links"] = []


def cells_are_adjacent(cell_a, cell_b):
    distance_x = abs(cell_a[0] - cell_b[0])
    distance_y = abs(cell_a[1] - cell_b[1])

    return distance_x + distance_y == 1


def area_touches_cell(area_data, cell):
    for area_cell in area_data.get("cells", []):
        if cells_are_adjacent(area_cell, cell):
            return True

    return False


def get_area_at_cell(items, cell):
    for area_data in items:
        if cell in area_data.get("cells", []):
            return area_data

    return None


def get_area_by_id(scene_data, area_type, area_id):
    ensure_area_lists(scene_data)

    for area_data in scene_data[area_type]:
        if area_data["id"] == area_id:
            return area_data

    return None


def get_spawn_at_cell(scene_data, cell):
    ensure_area_lists(scene_data)
    return get_area_at_cell(scene_data["spawns"], cell)


def get_exit_at_cell(scene_data, cell):
    ensure_area_lists(scene_data)
    return get_area_at_cell(scene_data["exits"], cell)


def merge_areas(items, target_area, source_area):
    for cell in source_area.get("cells", []):
        if cell not in target_area["cells"]:
            target_area["cells"].append(cell)

    items.remove(source_area)


def add_area_cell(scene_data, area_type, prefix, cell):
    ensure_area_lists(scene_data)

    items = scene_data[area_type]

    if get_area_at_cell(items, cell) is not None:
        return False

    adjacent_areas = []

    for area_data in items:
        if area_touches_cell(area_data, cell):
            adjacent_areas.append(area_data)

    if len(adjacent_areas) == 0:
        area_id = generate_area_id(prefix, items)

        area_data = {
            "id": area_id,
            "name": area_id,
            "cells": [cell],
        }

        if area_type == "spawns":
            area_data["spawn_cell"] = cell

        if area_type == "exits":
            area_data["target_links"] = []

        items.append(area_data)
        return True

    target_area = adjacent_areas[0]
    target_area["cells"].append(cell)

    for index in range(1, len(adjacent_areas)):
        merge_areas(items, target_area, adjacent_areas[index])

    return True


def remove_area_cell(scene_data, area_type, cell):
    ensure_area_lists(scene_data)

    items = scene_data[area_type]
    area_data = get_area_at_cell(items, cell)

    if area_data is None:
        return False

    area_data["cells"].remove(cell)

    if area_type == "spawns":
        if area_data.get("spawn_cell") == cell:
            if len(area_data["cells"]) > 0:
                area_data["spawn_cell"] = area_data["cells"][0]
            else:
                area_data["spawn_cell"] = None

    if len(area_data["cells"]) == 0:
        items.remove(area_data)

    return True


def add_spawn_cell(scene_data, cell):
    return add_area_cell(scene_data, "spawns", "spawn", cell)


def remove_spawn_cell(scene_data, cell):
    return remove_area_cell(scene_data, "spawns", cell)


def add_exit_cell(scene_data, cell):
    return add_area_cell(scene_data, "exits", "exit", cell)


def remove_exit_cell(scene_data, cell):
    return remove_area_cell(scene_data, "exits", cell)


def rename_area(scene_data, area_type, area_id, new_name):
    area_data = get_area_by_id(scene_data, area_type, area_id)

    if area_data is None:
        return False

    clean_name = new_name.strip()

    if clean_name == "":
        return False

    area_data["name"] = clean_name
    return True


def set_exit_target(scene_data, exit_id, target_scene_id, target_spawn_id):
    exit_data = get_area_by_id(scene_data, "exits", exit_id)

    if exit_data is None:
        return False

    exit_data["target_links"] = [{
        "target_scene_id": target_scene_id,
        "target_spawn_id": target_spawn_id,
    }]

    return True