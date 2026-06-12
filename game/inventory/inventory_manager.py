from game.inventory.inventory_state import ensure_inventory_state
from game.inventory.item_database import get_item_data


def get_inventory_items(state):
    ensure_inventory_state(state)
    return state["inventory"]["items"]


def get_inventory_capacity(state):
    ensure_inventory_state(state)
    return state["inventory"]["capacity"]


def has_item(state, item_id):
    items = get_inventory_items(state)
    return items.get(item_id, 0) > 0


def add_item(state, item_id, amount):
    ensure_inventory_state(state)

    item_data = get_item_data(item_id)

    if item_data is None:
        return False

    current_amount = state["inventory"]["items"].get(item_id, 0)

    if not item_data.get("stackable", True) and current_amount > 0:
        return False

    state["inventory"]["items"][item_id] = current_amount + amount
    return True


def remove_item(state, item_id, amount):
    ensure_inventory_state(state)

    current_amount = state["inventory"]["items"].get(item_id, 0)

    if current_amount < amount:
        return False

    new_amount = current_amount - amount

    if new_amount <= 0:
        del state["inventory"]["items"][item_id]
    else:
        state["inventory"]["items"][item_id] = new_amount

    return True