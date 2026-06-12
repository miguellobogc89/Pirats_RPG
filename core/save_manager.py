import json
from pathlib import Path

SAVE_FILE = Path(__file__).resolve().parents[1] / "save.json"


def save_state(state):
    with SAVE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)


def load_saved_state():
    if not SAVE_FILE.exists():
        return None

    with SAVE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)
