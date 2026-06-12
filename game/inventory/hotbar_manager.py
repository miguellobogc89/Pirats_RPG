from game.inventory.hotbar_state import HOTBAR_SIZE, ensure_hotbar_state
from game.inventory.inventory_manager import has_item
from game.inventory.item_database import get_item_data


def get_hotbar_slots(state):
    ensure_hotbar_state(state)
    return state["hotbar"]["slots"]


def get_active_hotbar_index(state):
    ensure_hotbar_state(state)
    return state["hotbar"]["active_index"]


def set_active_hotbar_index(state, index):
    ensure_hotbar_state(state)

    if index < 0 or index >= HOTBAR_SIZE:
        return False

    state["hotbar"]["active_index"] = index
    return True


def get_active_item_id(state):
    slots = get_hotbar_slots(state)
    active_index = get_active_hotbar_index(state)

    return slots[active_index]


def get_active_item_data(state):
    active_item_id = get_active_item_id(state)

    if active_item_id is None:
        return None

    return get_item_data(active_item_id)


def get_active_tool(state):
    item_data = get_active_item_data(state)

    if item_data is None:
        return None

    if item_data.get("type") != "tool":
        return None

    return item_data.get("tool_type")


def assign_item_to_hotbar(state, index, item_id):
    ensure_hotbar_state(state)

    if index < 0 or index >= HOTBAR_SIZE:
        return False

    if item_id is not None and not has_item(state, item_id):
        return False

    state["hotbar"]["slots"][index] = item_id
    return True