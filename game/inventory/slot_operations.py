from game.inventory.slot_model import (
    can_merge_stacks,
    create_stack,
    get_stack_space,
    is_valid_stack,
)


def success(source_stack=None, target_stack=None, moved_amount=0):
    return {
        "success": True,
        "source_stack": copy_stack(source_stack),
        "target_stack": copy_stack(target_stack),
        "moved_amount": moved_amount,
    }


def failure(reason, source_stack=None, target_stack=None):
    return {
        "success": False,
        "reason": reason,
        "source_stack": copy_stack(source_stack),
        "target_stack": copy_stack(target_stack),
        "moved_amount": 0,
    }


def copy_stack(stack):
    if stack is None:
        return None

    return {
        "item_id": stack["item_id"],
        "amount": stack["amount"],
    }


def can_combine_stacks(source_stack, target_stack):
    if not is_valid_stack(source_stack) or not is_valid_stack(target_stack):
        return False

    if source_stack is None or target_stack is None:
        return False

    if not can_merge_stacks(source_stack, target_stack):
        return False

    return get_stack_space(target_stack) > 0


def merge_stacks(source_stack, target_stack):
    if source_stack is None:
        return failure("empty_source", source_stack, target_stack)

    if target_stack is None:
        return failure("empty_target", source_stack, target_stack)

    if not is_valid_stack(source_stack):
        return failure("invalid_source_stack", source_stack, target_stack)

    if not is_valid_stack(target_stack):
        return failure("invalid_target_stack", source_stack, target_stack)

    if not can_merge_stacks(source_stack, target_stack):
        return failure("incompatible_stacks", source_stack, target_stack)

    stack_space = get_stack_space(target_stack)

    if stack_space <= 0:
        return failure("target_stack_full", source_stack, target_stack)

    moved_amount = min(source_stack["amount"], stack_space)
    new_target_amount = target_stack["amount"] + moved_amount
    new_source_amount = source_stack["amount"] - moved_amount
    new_source_stack = None

    if new_source_amount > 0:
        new_source_stack = create_stack(source_stack["item_id"], new_source_amount)

    new_target_stack = create_stack(target_stack["item_id"], new_target_amount)
    return success(new_source_stack, new_target_stack, moved_amount)


def swap_slots(source_stack, target_stack):
    if not is_valid_stack(source_stack):
        return failure("invalid_source_stack", source_stack, target_stack)

    if not is_valid_stack(target_stack):
        return failure("invalid_target_stack", source_stack, target_stack)

    return success(target_stack, source_stack, 0)


def move_amount(source_stack, target_stack, amount):
    if amount <= 0:
        return failure("invalid_amount", source_stack, target_stack)

    if source_stack is None:
        return failure("empty_source", source_stack, target_stack)

    if not is_valid_stack(source_stack):
        return failure("invalid_source_stack", source_stack, target_stack)

    if target_stack is not None and not is_valid_stack(target_stack):
        return failure("invalid_target_stack", source_stack, target_stack)

    if source_stack["amount"] < amount:
        return failure("not_enough_source_amount", source_stack, target_stack)

    if target_stack is None:
        moved_stack = create_stack(source_stack["item_id"], amount)

        if moved_stack is None:
            return failure("amount_exceeds_max_stack", source_stack, target_stack)

        remaining_amount = source_stack["amount"] - amount
        remaining_stack = None

        if remaining_amount > 0:
            remaining_stack = create_stack(source_stack["item_id"], remaining_amount)

        return success(remaining_stack, moved_stack, amount)

    if not can_merge_stacks(source_stack, target_stack):
        return failure("incompatible_stacks", source_stack, target_stack)

    stack_space = get_stack_space(target_stack)

    if stack_space < amount:
        return failure("not_enough_target_space", source_stack, target_stack)

    new_target_stack = create_stack(
        target_stack["item_id"],
        target_stack["amount"] + amount,
    )
    remaining_amount = source_stack["amount"] - amount
    remaining_stack = None

    if remaining_amount > 0:
        remaining_stack = create_stack(source_stack["item_id"], remaining_amount)

    return success(remaining_stack, new_target_stack, amount)


def split_stack(source_stack, amount):
    if amount <= 0:
        return failure("invalid_amount", source_stack, None)

    if source_stack is None:
        return failure("empty_source", source_stack, None)

    if not is_valid_stack(source_stack):
        return failure("invalid_source_stack", source_stack, None)

    if source_stack["amount"] <= amount:
        return failure("not_enough_source_amount", source_stack, None)

    split_off_stack = create_stack(source_stack["item_id"], amount)

    if split_off_stack is None:
        return failure("invalid_split_amount", source_stack, None)

    remaining_stack = create_stack(
        source_stack["item_id"],
        source_stack["amount"] - amount,
    )
    return success(remaining_stack, split_off_stack, amount)
