import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"


def load_json(name):
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(name, data):
    path = DATA_DIR / name
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def load_game_data():
    return {
        "resources": load_json("resources.json"),
        "actions": load_json("actions.json"),
        "routes": load_json("routes.json"),
        "upgrades": load_json("upgrades.json"),
        "config": load_json("game_config.json"),
        "zones": load_json("zones.json"),
    }
