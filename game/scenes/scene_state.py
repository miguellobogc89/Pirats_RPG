DEFAULT_SCENE_STATE = {
    "removed_objects": [],
    "placed_objects": [],
    "modified_objects": {},
    "object_states": {},
    "tilled_cells": [],
    "watered_cells": [],
    "crops": [],
}


def create_default_scene_state():
    return {
        "removed_objects": [],
        "placed_objects": [],
        "modified_objects": {},
        "object_states": {},
        "tilled_cells": [],
        "watered_cells": [],
        "crops": [],
    }


def ensure_scene_states(state):
    if "scene_states" not in state or not isinstance(state.get("scene_states"), dict):
        state["scene_states"] = {}

    current_scene = state.get("current_scene", "farm")
    ensure_scene_state_entry(state, current_scene)
    migrate_legacy_world_state_to_scene(state, current_scene)


def ensure_scene_state_entry(state, scene_id):
    scene_states = state.setdefault("scene_states", {})

    if scene_id not in scene_states or not isinstance(scene_states.get(scene_id), dict):
        scene_states[scene_id] = create_default_scene_state()

    scene_state = scene_states[scene_id]

    for key, value in DEFAULT_SCENE_STATE.items():
        if key not in scene_state:
            scene_state[key] = value.copy() if isinstance(value, (list, dict)) else value

    normalize_object_states(scene_state)
    return scene_state


def get_current_scene_state(state):
    scene_id = state.get("current_scene", "farm")
    return ensure_scene_state_entry(state, scene_id)


def migrate_legacy_world_state_to_scene(state, scene_id):
    scene_state = ensure_scene_state_entry(state, scene_id)

    if scene_state.get("_legacy_migrated"):
        return

    farming = state.get("farming")

    if isinstance(farming, dict):
        copy_list_if_empty(scene_state, "tilled_cells", farming.get("tilled_cells"))
        copy_list_if_empty(scene_state, "watered_cells", farming.get("watered_cells"))
        copy_list_if_empty(scene_state, "crops", farming.get("crops"))

    construction = state.get("construction")

    if isinstance(construction, dict):
        copy_list_if_empty(scene_state, "placed_objects", construction.get("placed_objects"))

    if not scene_state["placed_objects"]:
        copy_list_if_empty(scene_state, "placed_objects", state.get("placed_objects"))

    removed_objects = state.get("destroyed_world_objects", state.get("destroyed_objects"))
    copy_list_if_empty(scene_state, "removed_objects", removed_objects)
    migrate_legacy_object_lists_to_object_states(scene_state)

    scene_state["_legacy_migrated"] = True


def normalize_object_states(scene_state):
    if not isinstance(scene_state.get("object_states"), dict):
        scene_state["object_states"] = {}

    migrate_legacy_object_lists_to_object_states(scene_state)


def migrate_legacy_object_lists_to_object_states(scene_state):
    object_states = scene_state.setdefault("object_states", {})

    removed_objects = scene_state.get("removed_objects", [])
    if isinstance(removed_objects, list):
        for object_id in removed_objects:
            if not object_id:
                continue

            object_state = ensure_object_state_entry(scene_state, object_id)
            object_state["removed"] = True

    modified_objects = scene_state.get("modified_objects", {})
    if isinstance(modified_objects, dict):
        for object_id, modified_data in modified_objects.items():
            if not object_id or not isinstance(modified_data, dict):
                continue

            object_state = ensure_object_state_entry(scene_state, object_id)

            for key, value in modified_data.items():
                state_key = "current_hp" if key == "hp" else key
                object_state[state_key] = copy_scene_value(value)

    for object_id, object_state in list(object_states.items()):
        if not isinstance(object_state, dict):
            object_states[object_id] = {}


def ensure_object_state_entry(scene_state, object_id):
    object_states = scene_state.setdefault("object_states", {})
    object_id = str(object_id)

    if not isinstance(object_states.get(object_id), dict):
        object_states[object_id] = {}

    return object_states[object_id]


def get_object_state(state, object_id, scene_id=None):
    if scene_id is None:
        scene_id = state.get("current_scene", "farm")

    scene_state = ensure_scene_state_entry(state, scene_id)
    object_states = scene_state.setdefault("object_states", {})
    object_state = object_states.get(str(object_id))

    if isinstance(object_state, dict):
        return object_state

    return {}


def update_object_state(state, object_id, values, scene_id=None):
    if scene_id is None:
        scene_id = state.get("current_scene", "farm")

    scene_state = ensure_scene_state_entry(state, scene_id)
    object_state = ensure_object_state_entry(scene_state, object_id)

    for key, value in values.items():
        object_state[key] = copy_scene_value(value)

    sync_object_state_to_legacy(scene_state, object_id, object_state)
    return object_state


def mark_object_removed(state, object_id, scene_id=None):
    object_state = update_object_state(
        state,
        object_id,
        {"removed": True},
        scene_id=scene_id,
    )

    scene_state = ensure_scene_state_entry(
        state,
        scene_id or state.get("current_scene", "farm"),
    )

    if object_id not in scene_state["removed_objects"]:
        scene_state["removed_objects"].append(object_id)

    return object_state


def sync_object_state_to_legacy(scene_state, object_id, object_state):
    if object_state.get("removed"):
        if object_id not in scene_state["removed_objects"]:
            scene_state["removed_objects"].append(object_id)
        return

    legacy_patch = {}

    for key, value in object_state.items():
        if key == "removed":
            continue

        legacy_key = "hp" if key == "current_hp" else key
        legacy_patch[legacy_key] = copy_scene_value(value)

    if legacy_patch:
        scene_state.setdefault("modified_objects", {})[object_id] = legacy_patch


def copy_list_if_empty(scene_state, key, value):
    if scene_state.get(key):
        return

    if isinstance(value, list):
        scene_state[key] = [copy_scene_value(item) for item in value]


def copy_scene_value(value):
    if isinstance(value, dict):
        return value.copy()

    if isinstance(value, list):
        return list(value)

    if isinstance(value, tuple):
        return list(value)

    return value
