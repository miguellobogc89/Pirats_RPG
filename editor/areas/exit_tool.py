def generate_area_id(prefix, items):
    return f"{prefix}_{len(items) + 1:03d}"


def get_spawn_at_cell(scene_data, cell):
    for spawn_data in scene_data["spawns"]:
        if spawn_data["cell"] == cell:
            return spawn_data

    return None


def get_exit_at_cell(scene_data, cell):
    for exit_data in scene_data["exits"]:
        if exit_data["cell"] == cell:
            return exit_data

    return None


def add_spawn_cell(scene_data, cell):
    if get_spawn_at_cell(scene_data, cell) is not None:
        return False

    scene_data["spawns"].append({
        "id": generate_area_id("spawn", scene_data["spawns"]),
        "cell": cell,
    })

    return True


def remove_spawn_cell(scene_data, cell):
    spawn_data = get_spawn_at_cell(scene_data, cell)

    if spawn_data is None:
        return False

    scene_data["spawns"].remove(spawn_data)
    return True


def add_exit_cell(scene_data, cell):
    if get_exit_at_cell(scene_data, cell) is not None:
        return False

    scene_data["exits"].append({
        "id": generate_area_id("exit", scene_data["exits"]),
        "cell": cell,
        "target_scene_id": "",
        "target_spawn_id": "",
    })

    return True


def remove_exit_cell(scene_data, cell):
    exit_data = get_exit_at_cell(scene_data, cell)

    if exit_data is None:
        return False

    scene_data["exits"].remove(exit_data)
    return True