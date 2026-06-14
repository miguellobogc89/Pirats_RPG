from game.notifications import notify
from game.story.story_database import (
    INTRO_CHAPTER_ID,
    INTRO_STEPS,
    get_next_intro_step,
    get_story_step_label,
)
from game.story.story_state import ensure_story_state


def get_current_story_step(state):
    story_state = ensure_story_state(state)
    return story_state["step"]


def set_story_step(state, step_id, app=None):
    if step_id not in INTRO_STEPS:
        return False

    story_state = ensure_story_state(state)
    story_state["chapter"] = INTRO_CHAPTER_ID
    story_state["step"] = step_id
    notify_story_step(app, step_id)
    return True


def advance_story_step(state, app=None):
    current_step = get_current_story_step(state)
    next_step = get_next_intro_step(current_step)

    if next_step == current_step:
        return False

    return set_story_step(state, next_step, app=app)


def notify_story_step(app, step_id):
    if app is None:
        return

    notify(
        app,
        f"Nuevo objetivo: {get_story_step_label(step_id)}",
        notification_type="center",
    )
