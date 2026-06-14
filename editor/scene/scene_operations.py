def get_occupied_cells_for_object(cell, footprint):
    occupied_cells = []

    for offset_x in range(footprint[0]):
        for offset_y in range(footprint[1]):
            occupied_cells.append([
                cell[0] + offset_x,
                cell[1] + offset_y,
            ])

    return occupied_cells


def get_used_object_cells(scene_data, object_definitions):
    used_cells = []

    for object_data in scene_data["objects"]:
        object_type = object_data["type"]

        if object_type not in object_definitions:
            continue

        footprint = object_definitions[object_type]["footprint"]
        object_cells = get_occupied_cells_for_object(
            object_data["cell"],
            footprint,
        )

        for cell in object_cells:
            if cell not in used_cells:
                used_cells.append(cell)

    return used_cells


def can_place_object(scene_data, object_type, cell, object_definitions):
    if object_type is None:
        return False

    if object_type not in object_definitions:
        return False

    footprint = object_definitions[object_type]["footprint"]
    new_object_cells = get_occupied_cells_for_object(cell, footprint)
    used_cells = get_used_object_cells(scene_data, object_definitions)

    for cell_to_check in new_object_cells:
        if cell_to_check in used_cells:
            return False

    return True


def add_object(scene_data, object_type, cell, object_definitions):
    if not can_place_object(scene_data, object_type, cell, object_definitions):
        return False

    object_id = f"{object_type}_{len(scene_data['objects']) + 1:03d}"

    scene_data["objects"].append({
        "id": object_id,
        "type": object_type,
        "cell": cell,
    })

    return True


def remove_object_at_cell(scene_data, cell, object_definitions):
    for object_data in reversed(scene_data["objects"]):
        object_type = object_data["type"]

        if object_type not in object_definitions:
            continue

        footprint = object_definitions[object_type]["footprint"]

        occupied_cells = get_occupied_cells_for_object(
            object_data["cell"],
            footprint,
        )

        if cell in occupied_cells:
            scene_data["objects"].remove(object_data)
            return True

    return False