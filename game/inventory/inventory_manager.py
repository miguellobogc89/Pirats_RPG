from game.inventory.inventory_state import ensure_inventory_state
from game.data.item_database import get_item_data, get_item_max_stack
from game.inventory.slot_model import can_stack, create_stack, get_stack_space


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
    remaining_amount = amount

    if can_stack(item_id):
        for row in grid:
            for slot in row:
                if slot is None:
                    continue

                if slot["item_id"] != item_id:
                    continue

                remaining_amount -= get_stack_space(slot)

                if remaining_amount <= 0:
                    return True

    max_stack = get_item_max_stack(item_id)
    for row in grid:
        for slot in row:
            if slot is None:
                remaining_amount -= max_stack

                if remaining_amount <= 0:
                    return True

    return False


def add_item(state, item_id, amount=1):
    ensure_inventory_state(state)

    if amount <= 0:
        return False

    item_data = get_item_data(item_id)

    if item_data is None:
        return False

    if not can_add_item(state, item_id, amount):
        return False

    grid = state["inventory"]["grid"]
    remaining_amount = amount

    if can_stack(item_id):
        for row in grid:
            for slot in row:
                if slot is None:
                    continue

                if slot["item_id"] != item_id:
                    continue

                amount_to_add = min(get_stack_space(slot), remaining_amount)

                if amount_to_add <= 0:
                    continue

                slot["amount"] += amount_to_add
                remaining_amount -= amount_to_add

                if remaining_amount <= 0:
                    return True

    max_stack = get_item_max_stack(item_id)
    for row in grid:
        for index, slot in enumerate(row):
            if slot is None:
                amount_to_add = min(max_stack, remaining_amount)
                row[index] = create_stack(item_id, amount_to_add)
                remaining_amount -= amount_to_add

                if remaining_amount <= 0:
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
