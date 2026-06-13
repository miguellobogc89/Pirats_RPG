from game.scenes.scene_database import SCENE_DATABASE


def ensure_scene_state(state):
    if "current_scene" not in state:
        state["current_scene"] = "farm"


def get_current_scene_id(state):
    ensure_scene_state(state)

    return state["current_scene"]


def get_current_scene_data(state):
    scene_id = get_current_scene_id(state)

    return SCENE_DATABASE.get(scene_id)


def change_scene(state, scene_id):
    if scene_id not in SCENE_DATABASE:
        return False

    scene_data = SCENE_DATABASE[scene_id]
    spawn = scene_data["player_spawn"]

    state["current_scene"] = scene_id
    state["player"]["x"] = spawn["x"]
    state["player"]["y"] = spawn["y"]

    return True