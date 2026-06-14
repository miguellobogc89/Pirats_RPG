from game.scenes.scene_runtime import load_object_definitions


def load_npcs_from_scene(scene_data):
    if scene_data is None:
        return []

    object_definitions = load_object_definitions()
    tile_size = scene_data.get("tile_size", 32)
    npcs = []

    for object_data in scene_data.get("objects", []):
        object_type = object_data.get("type")
        object_definition = object_definitions.get(object_type, {})

        if not is_npc_object(object_data, object_definition):
            continue

        npc = build_npc(object_data, object_definition, tile_size)

        if npc is not None:
            npcs.append(npc)

    return npcs


def is_npc_object(object_data, object_definition):
    return (
        object_data.get("type") == "npc"
        or object_definition.get("type") == "npc"
    )


def build_npc(object_data, object_definition, tile_size):
    cell = object_data.get("cell")

    if not isinstance(cell, list) or len(cell) < 2:
        return None

    footprint = object_definition.get("footprint", [1, 1])
    visual_size = object_definition.get("visual_size", footprint)
    world_x = cell[0] * tile_size + footprint[0] * tile_size / 2
    world_y = cell[1] * tile_size + footprint[1] * tile_size / 2
    npc_id = object_data.get("id", f"npc_{cell[0]}_{cell[1]}")

    return {
        "id": npc_id,
        "name": object_data.get("name", object_definition.get("name", npc_id)),
        "position": {
            "x": world_x,
            "y": world_y,
        },
        "dialogue_id": object_data.get(
            "dialogue_id",
            object_definition.get("dialogue_id"),
        ),
        "portrait_path": object_data.get(
            "portrait_path",
            object_definition.get("portrait_path"),
        ),
        "sprite": object_data.get("sprite", object_definition.get("sprite")),
        "radius": max(18, int(max(visual_size) * tile_size / 2)),
        "cell": cell,
    }
