import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OBJECT_DEFINITIONS_PATH = PROJECT_ROOT / "data" / "object_definitions.json"


def load_object_definitions_file():
    if not OBJECT_DEFINITIONS_PATH.exists():
        return {}

    with open(OBJECT_DEFINITIONS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_object_definition(object_id, object_definition):
    object_id = object_id.strip()

    if object_id == "":
        return False, "El ID del objeto está vacío"

    object_definitions = load_object_definitions_file()
    object_definitions[object_id] = object_definition

    with open(OBJECT_DEFINITIONS_PATH, "w", encoding="utf-8") as file:
        json.dump(object_definitions, file, indent=2, ensure_ascii=False)

    return True, f"Objeto guardado: {object_id}"