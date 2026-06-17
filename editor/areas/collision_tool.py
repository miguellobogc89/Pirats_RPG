def add_collision_cell(scene_data, cell):
    if cell not in scene_data["collisions"]:
        scene_data["collisions"].append(cell)
        return True

    return False


def remove_collision_cell(scene_data, cell):
    if cell in scene_data["collisions"]:
        scene_data["collisions"].remove(cell)
        return True

    return False
