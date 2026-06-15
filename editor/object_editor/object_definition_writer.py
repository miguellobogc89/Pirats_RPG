import json
import re
import shutil
from pathlib import Path

from game.world.object_interaction_model import normalize_object_interaction


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OBJECT_DEFINITIONS_PATH = PROJECT_ROOT / "data" / "object_definitions.json"
OBJECT_DEFINITION_DIR = PROJECT_ROOT / "data" / "objects"
OBJECT_ICON_DIR = PROJECT_ROOT / "assets" / "icons"


def make_object_id(name):
    clean_name = name.strip().lower()
    clean_name = re.sub(r"[^a-z0-9]+", "_", clean_name)
    return clean_name.strip("_")


def make_category_id(category):
    category_id = make_object_id(category)

    if category_id == "":
        return "other"

    return category_id


def load_object_definitions_file():
    object_definitions = {}

    if OBJECT_DEFINITIONS_PATH.exists():
        with open(OBJECT_DEFINITIONS_PATH, "r", encoding="utf-8") as file:
            object_definitions.update(json.load(file))

    if OBJECT_DEFINITION_DIR.exists():
        for object_path in sorted(OBJECT_DEFINITION_DIR.glob("*.json")):
            with open(object_path, "r", encoding="utf-8") as file:
                object_definition = json.load(file)

            object_id = object_definition.get("id", object_path.stem)
            object_definitions[object_id] = object_definition

    return object_definitions


def get_unique_object_id(base_object_id, object_definitions):
    object_id = base_object_id
    index = 2

    while object_id in object_definitions:
        object_id = f"{base_object_id}_{index}"
        index += 1

    return object_id


def prepare_sprite_path(object_id, category_id, source_sprite_path):
    if not source_sprite_path:
        return ""

    source_path = Path(source_sprite_path)

    if not source_path.is_absolute():
        source_path = PROJECT_ROOT / source_path

    if not source_path.exists():
        return str(source_sprite_path).replace("\\", "/")

    target_dir = OBJECT_ICON_DIR / category_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{object_id}.png"

    if source_path.resolve() != target_path.resolve():
        shutil.copy2(source_path, target_path)

    return target_path.relative_to(PROJECT_ROOT).as_posix()


def normalize_object_definition(object_id, object_definition):
    normalized = dict(object_definition)
    category_id = make_category_id(normalized.get("category", "other"))
    normalized["id"] = object_id
    normalized["category"] = category_id
    normalized["sprite"] = prepare_sprite_path(
        object_id,
        category_id,
        normalized.get("sprite", ""),
    )
    normalized["footprint"] = list(normalized.get("footprint", [1, 1]))
    normalized["sprite_offset"] = list(normalized.get("sprite_offset", [0, 0]))
    normalized["solid"] = bool(normalized.get("solid", True))
    normalized["stackable"] = bool(normalized.get("stackable", False))
    normalized.update(normalize_object_interaction(normalized, object_id))
    normalized.pop("pickup_mode", None)
    normalized.pop("pickable_interactable", None)
    return normalized


def save_object_definition(
    object_id,
    object_definition,
    save_as=False,
    original_object_id=None,
):
    object_id = object_id.strip()

    if object_id == "":
        return False, "El ID del objeto esta vacio", None, None

    object_definitions = load_object_definitions_file()

    if save_as and object_id in object_definitions:
        object_id = get_unique_object_id(f"{object_id}_copy", object_definitions)

    if (
        not save_as
        and object_id in object_definitions
        and object_id != original_object_id
    ):
        return False, "Ya existe un objeto con ese ID", None, None

    normalized = normalize_object_definition(object_id, object_definition)

    OBJECT_DEFINITION_DIR.mkdir(parents=True, exist_ok=True)
    object_path = OBJECT_DEFINITION_DIR / f"{object_id}.json"

    with open(object_path, "w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2, ensure_ascii=False)

    object_definitions[object_id] = normalized

    with open(OBJECT_DEFINITIONS_PATH, "w", encoding="utf-8") as file:
        json.dump(object_definitions, file, indent=2, ensure_ascii=False)

    return True, f"Objeto guardado: {object_id}", object_id, normalized


def delete_object_definition(object_id):
    object_id = object_id.strip()

    if object_id == "":
        return False, "No hay objeto seleccionado"

    object_definitions = load_object_definitions_file()

    if object_id not in object_definitions:
        return False, "El objeto no existe"

    object_definitions.pop(object_id, None)

    object_path = OBJECT_DEFINITION_DIR / f"{object_id}.json"

    if object_path.exists():
        object_path.unlink()

    with open(OBJECT_DEFINITIONS_PATH, "w", encoding="utf-8") as file:
        json.dump(object_definitions, file, indent=2, ensure_ascii=False)

    return True, f"Objeto eliminado: {object_id}"
