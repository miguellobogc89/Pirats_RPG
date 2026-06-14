import pygame

from game.dialogue.dialogue_loader import load_dialogue
from game.notifications import notify


ADVANCE_KEYS = {
    pygame.K_RETURN,
    pygame.K_KP_ENTER,
    pygame.K_e,
    pygame.K_SPACE,
}


def start_dialogue(app, dialogue_id, speaker_name=None, portrait_path=None):
    dialogue = load_dialogue(dialogue_id)

    if dialogue is None or not dialogue["lines"]:
        notify(app, "No hay dialogo disponible.", notification_type="corner")
        return False

    app._dialogue = {
        "active": True,
        "dialogue_id": dialogue["id"],
        "speaker_name": speaker_name or dialogue.get("speaker_name"),
        "portrait_path": portrait_path or dialogue.get("portrait_path"),
        "lines": dialogue["lines"],
        "line_index": 0,
    }
    return True


def handle_dialogue_event(app, event):
    if not is_dialogue_active(app):
        return False

    if event.type == pygame.KEYDOWN and event.key in ADVANCE_KEYS:
        advance_dialogue(app)
        return True

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        advance_dialogue(app)
        return True

    return True


def update_dialogue(app, dt):
    return None


def draw_current_dialogue_text(app):
    dialogue_state = get_dialogue_state(app)

    if dialogue_state is None:
        return ""

    line_index = dialogue_state.get("line_index", 0)
    lines = dialogue_state.get("lines", [])

    if line_index < 0 or line_index >= len(lines):
        return ""

    return lines[line_index]


def advance_dialogue(app):
    dialogue_state = get_dialogue_state(app)

    if dialogue_state is None:
        return

    dialogue_state["line_index"] += 1

    if dialogue_state["line_index"] >= len(dialogue_state["lines"]):
        close_dialogue(app)


def close_dialogue(app):
    app._dialogue = {
        "active": False,
        "dialogue_id": None,
        "speaker_name": None,
        "portrait_path": None,
        "lines": [],
        "line_index": 0,
    }


def is_dialogue_active(app):
    dialogue_state = get_dialogue_state(app)
    return bool(dialogue_state and dialogue_state.get("active"))


def get_dialogue_state(app):
    return getattr(app, "_dialogue", None)
