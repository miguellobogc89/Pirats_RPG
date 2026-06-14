import json
from pathlib import Path


DIALOGUES_DIR = Path(__file__).resolve().parents[2] / "data" / "dialogues"


def load_dialogue(dialogue_id):
    dialogue_path = DIALOGUES_DIR / f"{dialogue_id}.json"

    if not dialogue_path.exists():
        return None

    with dialogue_path.open("r", encoding="utf-8") as file:
        raw_dialogue = json.load(file)

    return normalize_dialogue(raw_dialogue, dialogue_id)


def normalize_dialogue(raw_dialogue, fallback_dialogue_id):
    lines = raw_dialogue.get("lines")

    if lines is None:
        lines = raw_dialogue.get("text")

    if isinstance(lines, str):
        lines = [lines]

    if not isinstance(lines, list):
        lines = []

    normalized_lines = [
        str(line)
        for line in lines
        if str(line).strip() != ""
    ]

    return {
        "id": raw_dialogue.get("id", fallback_dialogue_id),
        "speaker_name": raw_dialogue.get("speaker_name"),
        "portrait_path": raw_dialogue.get("portrait_path"),
        "lines": normalized_lines,
    }
