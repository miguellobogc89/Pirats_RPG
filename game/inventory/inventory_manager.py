from game.inventory.inventory_state import ensure_inventory_state
from game.data.item_database import get_item_data


def get_inventory_grid(state):
    ensure_inventory_state(state)
    return state["inventory"]["grid"]


def get_inventory_capacity(state):
    ensure_inventory_state(state)
    return state["inventory"]["rows"] * state["inventory"]["columns"]


def has_item(state, item_id):
    grid = get_inventory_grid(state)

    for row in grid:
        for slot in row:
            if slot is None:
                continue

            if slot["item_id"] == item_id:
                return True

    return False


def add_item(state, item_id, amount=1):
    ensure_inventory_state(state)

    item_data = get_item_data(item_id)

    if item_data is None:
        return False

    grid = state["inventory"]["grid"]

    if item_data.get("stackable", True):
        for row in grid:
            for slot in row:
                if slot is None:
                    continue

                if slot["item_id"] == item_id:
                    slot["amount"] += amount
                    return True

    for row in grid:
        for index, slot in enumerate(row):
            if slot is None:
                row[index] = {
                    "item_id": item_id,
                    "amount": amount,
                }
                return True

    return False

def remove_item(state, item_id, amount=1):
    grid = get_inventory_grid(state)

    for row in grid:
        for index, slot in enumerate(row):
            if slot is None:
                continue

            if slot["item_id"] != item_id:
                continue

            if slot["amount"] < amount:
                return False

            slot["amount"] -= amount

            if slot["amount"] <= 0:
                row[index] = None

            return True

    return False