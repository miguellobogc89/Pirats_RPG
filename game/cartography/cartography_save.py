import json
from pathlib import Path


DEFAULT_SAVE_PATH = "save/cartography_save.json"


def load_cartography_save(path=DEFAULT_SAVE_PATH):
    save_path = Path(path)

    if not save_path.exists():
        return {}

    with save_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_cartography_data(data, path=DEFAULT_SAVE_PATH):
    save_path = Path(path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with save_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
