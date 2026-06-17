import ast

from editor.editor_assets import load_object_definitions
from editor.object_editor.object_definition_repository import save_object_definition
from editor.modules.database_editor.database_framework import DatabaseRecord
from game.objects.object_schema import FUNCTIONAL_TYPES, INTERACTION_MODES, REQUIRED_TOOLS


class ObjectDefinitionsProvider:
    def __init__(self):
        self.definitions = load_object_definitions()
        self.dirty_record_ids = set()

    def get_records(self):
        records = []
        category_options = get_category_options(self.definitions)

        for object_id, definition in sorted(self.definitions.items()):
            records.append(
                build_object_record(
                    object_id,
                    definition,
                    category_options,
                    dirty=object_id in self.dirty_record_ids,
                )
            )

        return records

    def is_record_dirty(self, record_id):
        return record_id in self.dirty_record_ids

    def update_record_field(self, record_id, path, text_value):
        definition = self.definitions.get(record_id)

        if definition is None:
            return False, "Objeto no encontrado."

        if not path:
            return False, "Campo no editable."

        current_value = get_nested_value(definition, path)

        try:
            parsed_value = parse_text_value(text_value, current_value)
        except ValueError as error:
            return False, str(error)

        set_nested_value(definition, path, parsed_value)
        self.dirty_record_ids.add(record_id)
        return True, "Campo actualizado."

    def save_record(self, record_id):
        definition = self.definitions.get(record_id)

        if definition is None:
            return False, "Objeto no encontrado."

        success, message, saved_id, normalized = save_object_definition(
            record_id,
            definition,
            save_as=False,
            original_object_id=record_id,
        )

        if success and saved_id:
            self.definitions = load_object_definitions()
            self.dirty_record_ids.discard(record_id)
            self.dirty_record_ids.discard(saved_id)

        return success, message


def build_object_record(object_id, definition, category_options, dirty=False):
    name = definition.get("name", object_id)
    functional_type = definition.get("functional_type", "unknown")
    category = definition.get("category", "other")
    collision = definition.get("collision", {})
    visual = definition.get("visual", {})
    footprint = collision.get("footprint", definition.get("footprint", [1, 1]))
    solid = collision.get("solid", definition.get("solid", False))

    summary_parts = [
        f"type: {functional_type}",
        f"category: {category}",
        f"footprint: {format_pair(footprint)}",
        f"solid: {solid}",
    ]

    relevant = get_relevant_definition_info(definition)
    if relevant:
        summary_parts.append(relevant)

    return DatabaseRecord(
        object_id,
        f"{object_id}  |  {name}",
        summary_parts,
        build_definition_detail_rows(object_id, definition, category_options),
        flags={
            "missing_sprite": not bool(visual.get("sprite")),
            "dirty": dirty,
        },
    )


def format_pair(value):
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return f"{value[0]}x{value[1]}"

    return "1x1"


def build_definition_detail_rows(object_id, definition, category_options):
    rows = []

    add_section(rows, "General")
    add_field(rows, "id", object_id, editable=False)
    add_field(rows, "name", definition.get("name", ""), ("name",))
    add_field(rows, "category", definition.get("category", ""), ("category",), options=category_options)
    add_field(rows, "functional_type", definition.get("functional_type", ""), ("functional_type",), options=FUNCTIONAL_TYPES)

    visual = definition.get("visual", {})
    if isinstance(visual, dict):
        add_section(rows, "Visual")
        add_field(rows, "sprite", visual.get("sprite", ""), ("visual", "sprite"))
        add_field(rows, "sprite_offset", visual.get("sprite_offset"), ("visual", "sprite_offset"))
        add_field(rows, "sprite_size", visual.get("sprite_size"), ("visual", "sprite_size"))
        add_field(rows, "visual_size", visual.get("visual_size"), ("visual", "visual_size"))

    collision = definition.get("collision", {})
    if isinstance(collision, dict):
        add_section(rows, "Collision")
        add_field(rows, "footprint", collision.get("footprint"), ("collision", "footprint"))
        add_field(rows, "footprint_anchor", collision.get("footprint_anchor"), ("collision", "footprint_anchor"), options=("center", "bottom", "top"))
        add_field(rows, "solid", collision.get("solid"), ("collision", "solid"))
        add_field(rows, "interaction_points", collision.get("interaction_points"), ("collision", "interaction_points"))

    functional_type = definition.get("functional_type")
    functional_data = definition.get(functional_type)
    if isinstance(functional_data, dict):
        add_section(rows, functional_type.title())
        for key, value in functional_data.items():
            add_field(
                rows,
                key,
                value,
                (functional_type, key),
                options=get_field_options(functional_type, key),
            )

    extra_keys = [
        key
        for key in sorted(definition)
        if key
        not in {
            "id",
            "name",
            "category",
            "functional_type",
            "visual",
            "collision",
            functional_type,
        }
    ]

    if extra_keys:
        add_section(rows, "Extra")
        for key in extra_keys:
            add_field(rows, key, definition.get(key), (key,))

    return rows


def add_section(rows, label):
    rows.append({
        "type": "section",
        "label": label,
    })


def add_field(rows, label, value, path=None, editable=True, options=None):
    rows.append({
        "type": "field",
        "label": label,
        "value": format_value(value),
        "raw_value": value,
        "path": path,
        "editable": editable and path is not None,
        "options": normalize_options(options),
    })


def format_value(value):
    if value is None:
        return "None"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(format_value(item) for item in value) + "]"

    if isinstance(value, dict):
        parts = [
            f"{key}: {format_value(item)}"
            for key, item in value.items()
        ]
        return "{" + ", ".join(parts) + "}"

    return str(value)


def normalize_options(options):
    if not options:
        return []

    return [
        format_value(option)
        for option in options
    ]


def get_category_options(definitions):
    categories = {
        str(definition.get("category", "other"))
        for definition in definitions.values()
    }
    categories.add("other")
    return tuple(sorted(categories))


def get_field_options(functional_type, key):
    if key == "interaction_mode":
        return INTERACTION_MODES

    if key == "required_tool":
        return REQUIRED_TOOLS

    if key == "locked":
        return ("true", "false")

    if key == "once":
        return ("true", "false")

    return ()


def get_nested_value(data, path):
    value = data

    for key in path:
        if not isinstance(value, dict):
            return None

        value = value.get(key)

    return value


def set_nested_value(data, path, value):
    target = data

    for key in path[:-1]:
        if not isinstance(target.get(key), dict):
            target[key] = {}

        target = target[key]

    target[path[-1]] = value


def parse_text_value(text_value, current_value):
    text_value = str(text_value).strip()

    if isinstance(current_value, bool):
        lowered = text_value.lower()

        if lowered in ("true", "1", "yes", "si", "sÃ­"):
            return True

        if lowered in ("false", "0", "no"):
            return False

        raise ValueError("Usa true o false.")

    if current_value is None:
        if text_value.lower() in ("none", "null", ""):
            return None

        return text_value

    if isinstance(current_value, int) and not isinstance(current_value, bool):
        try:
            return int(text_value)
        except ValueError as error:
            raise ValueError("Valor entero invalido.") from error

    if isinstance(current_value, float):
        try:
            return float(text_value)
        except ValueError as error:
            raise ValueError("Valor numerico invalido.") from error

    if isinstance(current_value, (list, dict)):
        try:
            value = ast.literal_eval(text_value)
        except (SyntaxError, ValueError) as error:
            raise ValueError("Usa sintaxis Python/JSON valida para listas o diccionarios.") from error

        if not isinstance(value, type(current_value)):
            raise ValueError("El tipo del valor no coincide con el campo original.")

        return value

    return text_value


def get_relevant_definition_info(definition):
    functional_type = definition.get("functional_type")

    if functional_type == "destructible":
        data = definition.get("destructible", {})
        return f"hp: {data.get('hp', 1)} tool: {data.get('required_tool')}"

    if functional_type == "interactable":
        data = definition.get("interactable", {})
        return f"mode: {data.get('interaction_mode', 'inspect')}"

    if functional_type == "pickup":
        data = definition.get("pickup", {})
        return f"item: {data.get('item_id', '')} qty: {data.get('quantity', 1)}"

    if functional_type == "npc":
        data = definition.get("npc", {})
        return f"npc: {data.get('npc_id', '')} dialogue: {data.get('dialogue_id', '')}"

    return ""

