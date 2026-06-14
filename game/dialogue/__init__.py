from game.dialogue.dialogue_manager import (
    handle_dialogue_event,
    is_dialogue_active,
    start_dialogue,
    update_dialogue,
)
from game.dialogue.dialogue_renderer import draw_dialogue


__all__ = [
    "draw_dialogue",
    "handle_dialogue_event",
    "is_dialogue_active",
    "start_dialogue",
    "update_dialogue",
]
