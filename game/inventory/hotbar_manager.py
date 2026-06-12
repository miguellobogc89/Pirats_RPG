from game.inventory.inventory_state import (
    HOTBAR_ROW,
    INVENTORY_COLUMNS,
    ensure_inventory_state,
)
from game.data.item_database import get_item_data


def get_hotbar_slots(state):
    ensure_inventory_state(state)
    return state["inventory"]["grid"][HOTBAR_ROW]


def get_active_hotbar_index(state):
    ensure_inventory_state(state)
    return state["inventory"]["active_hotbar_index"]


def set_active_hotbar_index(state, index):
    ensure_inventory_state(state)

    if index < 0 or index >= INVENTORY_COLUMNS:
        return False

    state["inventory"]["active_hotbar_index"] = index
    return True


def get_active_slot(state):
    slots = get_hotbar_slots(state)
    active_index = get_active_hotbar_index(state)
    return slots[active_index]


def get_active_item_id(state):
    slot = get_active_slot(state)

    if slot is None:
        return None

    return slot["item_id"]


def get_active_item_data(state):
    item_id = get_active_item_id(state)

    if item_id is None:
        return None

    return get_item_data(item_id)


def get_active_tool(state):
    item_data = get_active_item_data(state)

    if item_data is None:
        return None

    if item_data.get("type") != "tool":
        return None

    return item_data.get("tool_type")