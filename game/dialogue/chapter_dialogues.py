"""Chapter dialogue data adapter. No gameplay text lives in scene controllers."""
import json
from functools import lru_cache
from pathlib import Path

CATALOGUE = Path(__file__).resolve().parents[2] / "data" / "dialogues" / "chapter_01.json"


@lru_cache(maxsize=1)
def load_chapter_dialogues():
    return json.loads(CATALOGUE.read_text(encoding="utf-8"))


def get_chapter_dialogue(dialogue_id, **values):
    entry = load_chapter_dialogues()["dialogues"][dialogue_id]
    return entry["speaker"], [line.format(**values) for line in entry["lines"]]


def get_chapter_intro():
    return load_chapter_dialogues()["intro"]


def get_chapter_npcs(area):
    return load_chapter_dialogues()["npcs"].get(area, [])


def get_chapter_ui_text(text_id, **values):
    return load_chapter_dialogues()["ui_text"][text_id].format(**values)
