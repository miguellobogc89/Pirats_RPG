from editor.terrain.terrain_palette import DEFAULT_TERRAIN_ID


def ensure_terrain_data(scene_data):
    if "terrain" not in scene_data:
        scene_data["terrain"] = {
            "default": DEFAULT_TERRAIN_ID,
            "tiles": [],
        }

    if "default" not in scene_data["terrain"]:
        scene_data["terrain"]["default"] = DEFAULT_TERRAIN_ID

    if "tiles" not in scene_data["terrain"]:
        scene_data["terrain"]["tiles"] = []


def get_terrain_tile(scene_data, cell):
    ensure_terrain_data(scene_data)

    for tile in scene_data["terrain"]["tiles"]:
        if tile.get("cell") == cell:
            return tile

    return None


def paint_terrain_cell(scene_data, cell, terrain_id):
    ensure_terrain_data(scene_data)

    if terrain_id == scene_data["terrain"]["default"]:
        return erase_terrain_cell(scene_data, cell)

    existing_tile = get_terrain_tile(scene_data, cell)

    if existing_tile is not None:
        if existing_tile.get("terrain_id") == terrain_id:
            return False

        existing_tile["terrain_id"] = terrain_id
        return True

    scene_data["terrain"]["tiles"].append({
        "cell": cell,
        "terrain_id": terrain_id,
    })

    return True


def erase_terrain_cell(scene_data, cell):
    ensure_terrain_data(scene_data)

    existing_tile = get_terrain_tile(scene_data, cell)

    if existing_tile is None:
        return False

    scene_data["terrain"]["tiles"].remove(existing_tile)
    return True
