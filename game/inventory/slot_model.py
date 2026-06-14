from game.data.item_database import (
    get_item_data,
    get_item_max_stack,
    is_item_stackable,
)


def can_stack(item_id):
    return is_item_stackable(item_id)


def create_stack(item_id, amount):
    if amount <= 0:
        return None

    if get_item_data(item_id) is None:
        return None

    max_stack = get_item_max_stack(item_id)

    if amount > max_stack:
        return None

    return {
        "item_id": item_id,
        "amount": amount,
    }


def can_merge_stacks(source_stack, target_stack):
    if source_stack is None or target_stack is None:
        return False

    if source_stack["item_id"] != target_stack["item_id"]:
        return False

    return can_stack(source_stack["item_id"])


def get_stack_space(stack):
    if stack is None:
        return 0

    max_stack = get_item_max_stack(stack["item_id"])
    return max(0, max_stack - stack["amount"])


def is_valid_stack(stack):
    if stack is None:
        return True

    item_id = stack.get("item_id")
    amount = stack.get("amount", 0)

    if get_item_data(item_id) is None:
        return False

    if amount <= 0:
        return False

    return amount <= get_item_max_stack(item_id)
