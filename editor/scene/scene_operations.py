def add_object(scene_data, object_type, cell):
    if object_type is None:
        return

    object_id = f"{object_type}_{len(scene_data['objects']) + 1:03d}"

    scene_data["objects"].append({
        "id": object_id,
        "type": object_type,
        "cell": cell,
    })


def add_collision_cell(scene_data, cell):
    if cell not in scene_data["collisions"]:
        scene_data["collisions"].append(cell)