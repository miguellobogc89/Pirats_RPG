GENDER_OPTIONS = ["male", "female", "neutral"]
INITIAL_SCENE_ID = "intro_port"
INITIAL_SPAWN_ID = "spawn_001"
FALLBACK_SCENE_ID = "farm"


def create_character_creation_state():
    return {
        "name": "",
        "gender": "neutral",
        "selected_field": "name",
        "button_rects": {},
        "message": "",
    }
