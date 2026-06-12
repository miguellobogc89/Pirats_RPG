HOTBAR_SIZE = 8


def ensure_hotbar_state(state):
    if "hotbar" not in state:
        state["hotbar"] = {}

    if "active_index" not in state["hotbar"]:
        state["hotbar"]["active_index"] = 0

    if "slots" not in state["hotbar"]:
        state["hotbar"]["slots"] = [
            "axe",
            "pickaxe",
            "fishing_rod",
            None,
            None,
            None,
            None,
            None,
        ]