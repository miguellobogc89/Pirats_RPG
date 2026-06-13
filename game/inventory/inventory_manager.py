from game.inventory.inventory_state import ensure_inventory_state
from game.data.item_database import get_item_data


def get_inventory_grid(state):
    ensure_inventory_state(state)
    return state["inventory"]["grid"]


def get_inventory_capacity(state):
    ensure_inventory_state(state)
    return state["inventory"]["rows"] * state["inventory"]["columns"]


def has_item(state, item_id):
    return get_item_quantity(state, item_id) > 0


def get_item_quantity(state, item_id):
    grid = get_inventory_grid(state)
    total = 0

    for row in grid:
        for slot in row:
            if slot is None:
                continue

            if slot["item_id"] == item_id:
                total += slot["amount"]

    return total


def can_add_item(state, item_id, amount=1):
    ensure_inventory_state(state)

    if amount <= 0:
        return False

    item_data = get_item_data(item_id)

    if item_data is None:
        return False

    grid = state["inventory"]["grid"]

    if item_data.get("stackable", True):
        for row in grid:
            for slot in row:
                if slot is not None and slot["item_id"] == item_id:
                    return True

    for row in grid:
        for slot in row:
            if slot is None:
                return True

    return False


def add_item(state, item_id, amount=1):
    ensure_inventory_state(state)

    if amount <= 0:
        return False

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
    if amount <= 0:
        return False

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


def remove_item_quantity(state, item_id, amount=1):
    if amount <= 0:
        return False

    if get_item_quantity(state, item_id) < amount:
        return False

    remaining_amount = amount
    grid = get_inventory_grid(state)

    for row in grid:
        for index, slot in enumerate(row):
            if slot is None:
                continue

            if slot["item_id"] != item_id:
                continue

            amount_to_remove = min(slot["amount"], remaining_amount)
            slot["amount"] -= amount_to_remove
            remaining_amount -= amount_to_remove

            if slot["amount"] <= 0:
                row[index] = None

            if remaining_amount <= 0:
                return True

    return False
