from game.inventory.slot_operations import (
    merge_stacks,
    move_amount,
    swap_slots,
)


def success(operation, source_index, target_index, operation_result):
    return {
        "success": True,
        "operation": operation,
        "source_index": source_index,
        "target_index": target_index,
        "moved_amount": operation_result.get("moved_amount", 0),
        "source_stack": operation_result.get("source_stack"),
        "target_stack": operation_result.get("target_stack"),
    }


def failure(reason, operation, source_index, target_index):
    return {
        "success": False,
        "reason": reason,
        "operation": operation,
        "source_index": source_index,
        "target_index": target_index,
    }


def transfer_amount(source_container, source_index, target_container, target_index, amount):
    source_stack = source_container.get_slot(source_index)
    target_stack = target_container.get_slot(target_index)
    operation_result = move_amount(source_stack, target_stack, amount)

    if not operation_result["success"]:
        return failure(
            operation_result["reason"],
            "move_amount",
            source_index,
            target_index,
        )

    return apply_slot_operation(
        source_container,
        source_index,
        target_container,
        target_index,
        operation_result,
        "move_amount",
    )


def transfer_merge(source_container, source_index, target_container, target_index):
    source_stack = source_container.get_slot(source_index)
    target_stack = target_container.get_slot(target_index)
    operation_result = merge_stacks(source_stack, target_stack)

    if not operation_result["success"]:
        return failure(
            operation_result["reason"],
            "merge",
            source_index,
            target_index,
        )

    return apply_slot_operation(
        source_container,
        source_index,
        target_container,
        target_index,
        operation_result,
        "merge",
    )


def transfer_swap(source_container, source_index, target_container, target_index):
    source_stack = source_container.get_slot(source_index)
    target_stack = target_container.get_slot(target_index)
    operation_result = swap_slots(source_stack, target_stack)

    if not operation_result["success"]:
        return failure(
            operation_result["reason"],
            "swap",
            source_index,
            target_index,
        )

    return apply_slot_operation(
        source_container,
        source_index,
        target_container,
        target_index,
        operation_result,
        "swap",
    )


def transfer_stack(source_container, source_index, target_container, target_index):
    source_stack = source_container.get_slot(source_index)

    if source_stack is None:
        return failure("empty_source", "move_stack", source_index, target_index)

    return transfer_amount(
        source_container,
        source_index,
        target_container,
        target_index,
        source_stack["amount"],
    )


def apply_slot_operation(
    source_container,
    source_index,
    target_container,
    target_index,
    operation_result,
    operation,
):
    original_source_stack = source_container.get_slot(source_index)
    original_target_stack = target_container.get_slot(target_index)

    if not source_container.set_slot(source_index, operation_result["source_stack"]):
        return failure("source_set_failed", operation, source_index, target_index)

    if target_container.set_slot(target_index, operation_result["target_stack"]):
        return success(operation, source_index, target_index, operation_result)

    source_container.set_slot(source_index, original_source_stack)
    target_container.set_slot(target_index, original_target_stack)
    return failure("target_set_failed", operation, source_index, target_index)
