import json
import re
import shutil
from pathlib import Path

from game.objects.object_normalizer import normalize_object_definition as normalize_schema_object_definition


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OBJECT_DEFINITION_DIR = PROJECT_ROOT / "data" / "objects"
OBJECT_ICON_DIR = PROJECT_ROOT / "assets" / "icons"


def make_object_id(name):
    clean_name = str(name).strip().lower()
    clean_name = re.sub(r"[^a-z0-9]+", "_", clean_name)
    return clean_name.strip("_")


def make_category_id(category):
    category_id = make_object_id(category)
    return category_id or "other"


def load_file_definitions():
    definitions = {}

    if not OBJECT_DEFINITION_DIR.exists():
        return definitions

    for object_path in sorted(OBJECT_DEFINITION_DIR.glob("*.json")):
        with object_path.open("r", encoding="utf-8") as file:
            object_definition = json.load(file)

        if not isinstance(object_definition, dict):
            continue

        object_id = object_definition.get("id", object_path.stem)
        definitions[object_id] = object_definition

    return definitions


def find_duplicate_definition_ids():
    return []


def load_object_definitions(include_metadata=False):
    file_definitions = load_file_definitions()
    definitions = {}

    for object_id, object_definition in file_definitions.items():
        definitions[object_id] = normalize_object_definition(
            object_id,
            object_definition,
            prepare_sprite=False,
        )

    if include_metadata:
        return {
            "definitions": definitions,
            "duplicates": [],
            "legacy_only": [],
            "file_only": sorted(file_definitions),
        }

    return definitions


def list_object_definitions():
    return [
        {
            "id": object_id,
            "name": object_definition.get("name", object_id),
            "category": object_definition.get("category", "other"),
            "definition": object_definition,
        }
        for object_id, object_definition in sorted(load_object_definitions().items())
    ]


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


def normalize_object_definition(object_id, object_definition, prepare_sprite=True):
    normalized = dict(object_definition)
    category_id = make_category_id(normalized.get("category", "other"))
    normalized["id"] = object_id
    normalized["category"] = category_id

    visual = dict(normalized.get("visual", {}))

    if prepare_sprite:
        visual["sprite"] = prepare_sprite_path(
            object_id,
            category_id,
            visual.get("sprite", ""),
        )
    else:
        visual["sprite"] = str(visual.get("sprite", "")).replace("\\", "/")

    normalized["visual"] = visual
    normalized = normalize_schema_object_definition(normalized, object_id)
    return normalized


def save_object_definition(
    object_id,
    object_definition,
    save_as=False,
    original_object_id=None,
):
    object_id = str(object_id).strip()

    if object_id == "":
        return False, "El ID del objeto esta vacio", None, None

    object_definitions = load_object_definitions()

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

    with object_path.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2, ensure_ascii=False)

    return True, f"Objeto guardado: {object_id}", object_id, normalized


def delete_object_definition(object_id):
    object_id = str(object_id).strip()

    if object_id == "":
        return False, "No hay objeto seleccionado"

    object_definitions = load_object_definitions()

    if object_id not in object_definitions:
        return False, "El objeto no existe"

    object_path = OBJECT_DEFINITION_DIR / f"{object_id}.json"

    if object_path.exists():
        object_path.unlink()

    return True, f"Objeto eliminado: {object_id}"
