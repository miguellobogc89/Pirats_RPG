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

        footprint = object_definitions[object_type]["collision"]["footprint"]
        object_cells = get_occupied_cells_for_object(
            object_data["cell"],
            footprint,
        )

        for cell in object_cells:
            if cell not in used_cells:
                used_cells.append(cell)

    return used_cells


def normalize_object_instance(object_data):
    if not isinstance(object_data, dict):
        return None

    object_type = object_data.get("type")
    cell = object_data.get("cell")

    if not object_type:
        return None

    if not isinstance(cell, list) or len(cell) < 2:
        return None

    normalized = dict(object_data)
    normalized["id"] = normalized.get("id") or generate_object_instance_id(
        {"objects": []},
        object_type,
    )
    normalized["type"] = object_type
    normalized["cell"] = [cell[0], cell[1]]

    properties = normalized.get("properties")
    if not isinstance(properties, dict):
        properties = {}

    normalized["properties"] = {
        str(key): str(value)
        for key, value in properties.items()
        if str(key).strip() != ""
    }
    return normalized


def generate_object_instance_id(scene_data, object_type):
    existing_ids = {
        object_data.get("id")
        for object_data in scene_data.get("objects", [])
        if isinstance(object_data, dict)
    }
    index = 1

    while True:
        object_id = f"{object_type}_{index:03d}"

        if object_id not in existing_ids:
            return object_id

        index += 1


def can_place_object(scene_data, object_type, cell, object_definitions):
    if object_type is None:
        return False

    if object_type not in object_definitions:
        return False

    footprint = object_definitions[object_type]["collision"]["footprint"]
    new_object_cells = get_occupied_cells_for_object(cell, footprint)
    used_cells = get_used_object_cells(scene_data, object_definitions)

    for cell_to_check in new_object_cells:
        if cell_to_check in used_cells:
            return False

    return True


def add_object(scene_data, object_type, cell, object_definitions):
    if not can_place_object(scene_data, object_type, cell, object_definitions):
        return False

    object_id = generate_object_instance_id(scene_data, object_type)

    scene_data["objects"].append({
        "id": object_id,
        "type": object_type,
        "cell": cell,
        "properties": {},
    })

    return True


def get_object_at_cell(scene_data, cell, object_definitions):
    for object_data in reversed(scene_data.get("objects", [])):
        object_type = object_data.get("type")

        if object_type not in object_definitions:
            continue

        footprint = object_definitions[object_type]["collision"]["footprint"]
        occupied_cells = get_occupied_cells_for_object(
            object_data.get("cell", [0, 0]),
            footprint,
        )

        if cell in occupied_cells:
            return object_data

    return None


def get_object_by_id(scene_data, object_id):
    for object_data in scene_data.get("objects", []):
        if object_data.get("id") == object_id:
            return object_data

    return None


def ensure_object_properties(object_data):
    if object_data is None:
        return {}

    properties = object_data.get("properties")

    if not isinstance(properties, dict):
        properties = {}
        object_data["properties"] = properties

    return properties


def add_object_property(object_data):
    properties = ensure_object_properties(object_data)
    index = 1

    while True:
        key = f"property_{index}"

        if key not in properties:
            properties[key] = ""
            return key

        index += 1


def remove_object_property(object_data, key):
    properties = ensure_object_properties(object_data)

    if key not in properties:
        return False

    properties.pop(key)
    return True


def rename_object_property(object_data, old_key, new_key):
    properties = ensure_object_properties(object_data)
    clean_key = str(new_key).strip()

    if clean_key == "":
        return False

    if old_key == clean_key:
        return True

    if clean_key in properties:
        return False

    rebuilt = {}

    for key, value in properties.items():
        if key == old_key:
            rebuilt[clean_key] = value
        else:
            rebuilt[key] = value

    object_data["properties"] = rebuilt
    return True


def set_object_property_value(object_data, key, value):
    properties = ensure_object_properties(object_data)

    if key not in properties:
        return False

    properties[key] = str(value)
    return True


def remove_object_at_cell(scene_data, cell, object_definitions):
    for object_data in reversed(scene_data["objects"]):
        object_type = object_data["type"]

        if object_type not in object_definitions:
            continue

        footprint = object_definitions[object_type]["collision"]["footprint"]

        occupied_cells = get_occupied_cells_for_object(
            object_data["cell"],
            footprint,
        )

        if cell in occupied_cells:
            scene_data["objects"].remove(object_data)
            return True

    return False

