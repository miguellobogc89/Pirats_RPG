from game.story.story_database import INTRO_CHAPTER_ID, INTRO_STEPS


def create_default_story_state():
    return {
        "chapter": INTRO_CHAPTER_ID,
        "step": INTRO_STEPS[0],
    }


def ensure_story_state(state):
    if not isinstance(state.get("story"), dict):
        state["story"] = create_default_story_state()

    if "chapter" not in state["story"]:
        state["story"]["chapter"] = INTRO_CHAPTER_ID

    if "step" not in state["story"]:
        state["story"]["step"] = INTRO_STEPS[0]

    if state["story"]["step"] not in INTRO_STEPS:
        state["story"]["step"] = INTRO_STEPS[0]

    return state["story"]
