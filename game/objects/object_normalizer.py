from copy import deepcopy

from game.objects.object_schema import (
    DEFAULT_COLLISION,
    DEFAULT_VISUAL,
    FUNCTIONAL_BLOCK_DEFAULTS,
    ROOT_FIELDS,
    get_functional_block_name,
    is_valid_functional_type,
)


def normalize_object_definition(object_definition, object_id=None):
    """Normalize the definitive object schema.

    This function does not infer or preserve legacy root fields. It expects the
    new block-based model and only fills safe defaults inside that model.
    """

    if not isinstance(object_definition, dict):
        object_definition = {}

    normalized = {
        key: deepcopy(value)
        for key, value in object_definition.items()
        if key in ROOT_FIELDS
    }

    normalized["id"] = str(normalized.get("id") or object_id or "").strip()
    normalized["name"] = str(normalized.get("name") or normalized["id"] or "Object")
    normalized["category"] = str(normalized.get("category") or "other").strip().lower()

    functional_type = normalized.get("functional_type")
    if not is_valid_functional_type(functional_type):
        functional_type = "decorative"
    normalized["functional_type"] = functional_type

    normalized["visual"] = normalize_visual(normalized.get("visual"))
    normalized["collision"] = normalize_collision(normalized.get("collision"))

    block_name = get_functional_block_name(functional_type)
    if block_name is not None:
        normalized[block_name] = normalize_functional_block(
            block_name,
            normalized.get(block_name),
        )

    return normalized


def normalize_visual(visual):
    normalized = deepcopy(DEFAULT_VISUAL)

    if isinstance(visual, dict):
        normalized.update({
            key: deepcopy(value)
            for key, value in visual.items()
            if key in normalized
        })

    normalized["sprite"] = str(normalized.get("sprite") or "").replace("\\", "/")
    normalized["sprite_offset"] = normalize_pair(normalized.get("sprite_offset"), [0, 0], positive=False)
    normalized["sprite_size"] = normalize_optional_pair(normalized.get("sprite_size"))
    normalized["visual_size"] = normalize_optional_pair(normalized.get("visual_size"))
    return normalized


def normalize_collision(collision):
    normalized = deepcopy(DEFAULT_COLLISION)

    if isinstance(collision, dict):
        normalized.update({
            key: deepcopy(value)
            for key, value in collision.items()
            if key in normalized
        })

    normalized["footprint"] = normalize_pair(normalized.get("footprint"), [1, 1])
    normalized["footprint_anchor"] = normalize_anchor(normalized.get("footprint_anchor"))
    normalized["solid"] = bool(normalized.get("solid", True))
    normalized["interaction_points"] = normalize_interaction_points(
        normalized.get("interaction_points"),
    )
    return normalized


def normalize_functional_block(block_name, block_data):
    normalized = deepcopy(FUNCTIONAL_BLOCK_DEFAULTS[block_name])

    if isinstance(block_data, dict):
        normalized.update({
            key: deepcopy(value)
            for key, value in block_data.items()
            if key in normalized
        })

    if block_name == "destructible":
        normalized["hp"] = normalize_int(normalized.get("hp"), 1, minimum=1)
        normalized["energy_cost"] = normalize_int(normalized.get("energy_cost"), 0, minimum=0)
        normalized["drops"] = normalized.get("drops") if isinstance(normalized.get("drops"), list) else []

    if block_name == "pickup":
        normalized["quantity"] = normalize_int(normalized.get("quantity"), 1, minimum=1)

    if block_name == "trigger":
        normalized["once"] = bool(normalized.get("once", False))

    if block_name == "container":
        normalized["capacity"] = normalize_int(normalized.get("capacity"), 16, minimum=1)
        normalized["locked"] = bool(normalized.get("locked", False))

    if block_name == "door":
        normalized["locked"] = bool(normalized.get("locked", False))

    return normalized


def normalize_pair(value, fallback, positive=True):
    if not isinstance(value, list) or len(value) < 2:
        return list(fallback)

    pair = [value[0], value[1]]

    for index, item in enumerate(pair):
        if not isinstance(item, (int, float)):
            return list(fallback)

        if positive and item <= 0:
            return list(fallback)

        pair[index] = int(item) if float(item).is_integer() else item

    return pair


def normalize_optional_pair(value):
    if value is None:
        return None

    return normalize_pair(value, [1, 1])


def normalize_anchor(value):
    if isinstance(value, str) and value.strip():
        return value.strip()

    if isinstance(value, list) and len(value) >= 2:
        return [value[0], value[1]]

    return "center"


def normalize_interaction_points(value):
    if not isinstance(value, list):
        return []

    points = []

    for point in value:
        if not isinstance(point, list) or len(point) < 2:
            continue

        points.append([point[0], point[1]])

    return points


def normalize_int(value, fallback, minimum=None):
    try:
        normalized = int(value)
    except (TypeError, ValueError):
        normalized = fallback

    if minimum is not None:
        normalized = max(minimum, normalized)

    return normalized

