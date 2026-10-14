"""Engine-independent chapter dialogue catalogue (shared JSON with Unity)."""
import json
from pathlib import Path

CATALOGUE = Path(__file__).resolve().parents[2] / "data" / "dialogues" / "chapter_01.json"


def get_chapter_dialogue(dialogue_id, **values):
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    entry = data["dialogues"].get(dialogue_id)
    if entry is None:
        raise KeyError("Dialogo desconocido: " + dialogue_id)
    return entry["speaker"], [line.format(**values) for line in entry["lines"]]
