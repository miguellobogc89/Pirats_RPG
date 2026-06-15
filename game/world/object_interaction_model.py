INTERACTION_MODES = [
    "none",
    "inspect",
    "talk",
    "pickup",
    "use",
    "open",
    "repair",
    "trigger",
]

REQUIRED_TOOLS = [
    None,
    "axe",
    "pickaxe",
    "sword",
]

LEGACY_DESTRUCTIBLE_TYPES = {
    "tree",
    "rock",
    "small_rock",
    "big_rock",
    "bush",
    "resource",
}


def normalize_interaction_mode(data):
    interaction_mode = data.get("interaction_mode")

    if interaction_mode in INTERACTION_MODES:
        return interaction_mode

    pickup_mode = data.get("pickup_mode")

    if pickup_mode in ("collectable", "pickable"):
        return "pickup"

    if pickup_mode == "interactable":
        return "use"

    if data.get("interactable") is True:
        return "use"

    return "none"


def normalize_required_tool(data):
    required_tool = data.get("required_tool")

    if required_tool in REQUIRED_TOOLS:
        return required_tool

    if required_tool in ("", "none", "null"):
        return None

    return None


def parse_bool(value, default=False):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        clean_value = value.strip().lower()

        if clean_value in ("true", "1", "yes", "y", "si", "sí"):
            return True

        if clean_value in ("false", "0", "no", "n", "none", "null", ""):
            return False

    if value is None:
        return default

    return bool(value)


def infer_legacy_destructible(data, object_id=None):
    object_type = data.get("type", object_id)
    source_type = data.get("source_type", object_id)
    category = data.get("category")

    if object_type in LEGACY_DESTRUCTIBLE_TYPES:
        return True

    if source_type in LEGACY_DESTRUCTIBLE_TYPES:
        return True

    if category in LEGACY_DESTRUCTIBLE_TYPES:
        return True

    if data.get("required_tool") in ("axe", "pickaxe"):
        return True

    return False


def normalize_object_interaction(data, object_id=None):
    normalized = dict(data)
    normalized["interaction_mode"] = normalize_interaction_mode(normalized)

    if "destructible" in normalized:
        normalized["destructible"] = parse_bool(normalized.get("destructible"))
    else:
        normalized["destructible"] = infer_legacy_destructible(
            normalized,
            object_id=object_id,
        )

    if not normalized["destructible"]:
        normalized["required_tool"] = normalize_required_tool(normalized)
    else:
        normalized["required_tool"] = normalize_required_tool(normalized)

    return normalized
