from dataclasses import dataclass

from game.objects.object_schema import (
    FUNCTIONAL_TYPES,
    INTERACTION_MODES,
    LEGACY_ROOT_FIELDS,
    ROOT_FIELDS,
    get_functional_block_name,
)


@dataclass(frozen=True)
class ObjectValidationIssue:
    severity: str
    object_id: str
    message: str
    field: str | None = None


def validate_object_definition(object_definition, object_id=None):
    errors = []
    warnings = []

    if not isinstance(object_definition, dict):
        return [
            ObjectValidationIssue(
                "error",
                object_id or "<unknown>",
                "Object definition must be a JSON object.",
            )
        ], []

    current_id = str(object_definition.get("id") or object_id or "").strip()

    if current_id == "":
        errors.append(make_error(object_id or "<unknown>", "id is required.", "id"))

    for field_name in object_definition:
        if field_name in LEGACY_ROOT_FIELDS:
            errors.append(
                make_error(
                    current_id or object_id or "<unknown>",
                    f"Legacy root field is not allowed: {field_name}.",
                    field_name,
                )
            )
            continue

        if field_name not in ROOT_FIELDS:
            errors.append(
                make_error(
                    current_id or object_id or "<unknown>",
                    f"Unknown root field: {field_name}.",
                    field_name,
                )
            )

    functional_type = object_definition.get("functional_type")

    if functional_type not in FUNCTIONAL_TYPES:
        errors.append(
            make_error(
                current_id or object_id or "<unknown>",
                f"functional_type is required and must be one of: {', '.join(FUNCTIONAL_TYPES)}.",
                "functional_type",
            )
        )

    validate_visual(object_definition.get("visual"), current_id, errors)
    validate_collision(object_definition.get("collision"), current_id, errors)

    block_name = get_functional_block_name(functional_type)

    if block_name is not None:
        validate_functional_block(
            block_name,
            object_definition.get(block_name),
            current_id,
            errors,
        )

    for other_block in ("npc", "interactable", "destructible", "pickup", "trigger", "container", "door"):
        if other_block == block_name:
            continue

        if other_block in object_definition:
            errors.append(
                make_error(
                    current_id or object_id or "<unknown>",
                    f"Functional block {other_block} does not match functional_type {functional_type}.",
                    other_block,
                )
            )

    return errors, warnings


def validate_visual(visual, object_id, errors):
    if not isinstance(visual, dict):
        errors.append(make_error(object_id, "visual block is required.", "visual"))
        return

    if "sprite" not in visual:
        errors.append(make_error(object_id, "visual.sprite is required.", "visual.sprite"))

    if not is_valid_pair(visual.get("sprite_offset"), positive=False):
        errors.append(make_error(object_id, "visual.sprite_offset must be a two-value list.", "visual.sprite_offset"))

    if visual.get("sprite_size") is not None and not is_valid_pair(visual.get("sprite_size")):
        errors.append(make_error(object_id, "visual.sprite_size must be null or a positive two-value list.", "visual.sprite_size"))

    if visual.get("visual_size") is not None and not is_valid_pair(visual.get("visual_size")):
        errors.append(make_error(object_id, "visual.visual_size must be null or a positive two-value list.", "visual.visual_size"))


def validate_collision(collision, object_id, errors):
    if not isinstance(collision, dict):
        errors.append(make_error(object_id, "collision block is required.", "collision"))
        return

    if not is_valid_pair(collision.get("footprint")):
        errors.append(make_error(object_id, "collision.footprint must be a positive two-value list.", "collision.footprint"))

    if "solid" not in collision or not isinstance(collision.get("solid"), bool):
        errors.append(make_error(object_id, "collision.solid must be a boolean.", "collision.solid"))

    interaction_points = collision.get("interaction_points")
    if not isinstance(interaction_points, list):
        errors.append(make_error(object_id, "collision.interaction_points must be a list.", "collision.interaction_points"))


def validate_functional_block(block_name, block_data, object_id, errors):
    if not isinstance(block_data, dict):
        errors.append(make_error(object_id, f"{block_name} block is required.", block_name))
        return

    if block_name == "interactable":
        interaction_mode = block_data.get("interaction_mode")
        if interaction_mode not in INTERACTION_MODES:
            errors.append(make_error(object_id, "interactable.interaction_mode is invalid.", "interactable.interaction_mode"))

    if block_name == "destructible":
        if not isinstance(block_data.get("hp"), int) or block_data.get("hp") <= 0:
            errors.append(make_error(object_id, "destructible.hp must be a positive integer.", "destructible.hp"))

        if not isinstance(block_data.get("energy_cost"), int) or block_data.get("energy_cost") < 0:
            errors.append(make_error(object_id, "destructible.energy_cost must be zero or greater.", "destructible.energy_cost"))

        if not isinstance(block_data.get("drops"), list):
            errors.append(make_error(object_id, "destructible.drops must be a list.", "destructible.drops"))

    if block_name == "pickup":
        if not isinstance(block_data.get("quantity"), int) or block_data.get("quantity") <= 0:
            errors.append(make_error(object_id, "pickup.quantity must be a positive integer.", "pickup.quantity"))

    if block_name == "container":
        if not isinstance(block_data.get("capacity"), int) or block_data.get("capacity") <= 0:
            errors.append(make_error(object_id, "container.capacity must be a positive integer.", "container.capacity"))

        if not isinstance(block_data.get("locked"), bool):
            errors.append(make_error(object_id, "container.locked must be a boolean.", "container.locked"))

    if block_name == "door":
        if not isinstance(block_data.get("locked"), bool):
            errors.append(make_error(object_id, "door.locked must be a boolean.", "door.locked"))

    if block_name == "trigger":
        if not isinstance(block_data.get("once"), bool):
            errors.append(make_error(object_id, "trigger.once must be a boolean.", "trigger.once"))


def is_valid_pair(value, positive=True):
    if not isinstance(value, list) or len(value) < 2:
        return False

    for item in value[:2]:
        if not isinstance(item, (int, float)):
            return False

        if positive and item <= 0:
            return False

    return True


def make_error(object_id, message, field=None):
    return ObjectValidationIssue("error", object_id or "<unknown>", message, field)

