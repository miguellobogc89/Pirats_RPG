from game.data.item_database import get_item_data
from game.inventory.inventory_manager import (
    add_item,
    can_add_item,
    get_item_quantity,
    remove_item_quantity,
)
from game.inventory.inventory_state import ensure_inventory_state
from game.cartography.ship_storage import ShipStorage


ALLOWED_SHIP_STORAGE_ITEM_TYPES = {
    "resource",
    "crop",
    "currency",
}


def move_inventory_to_ship_storage(state, ship_storage, item_id, amount):
    validation_error = validate_transfer_request(item_id, amount)

    if validation_error is not None:
        return failure(validation_error)

    if not is_item_allowed_in_ship_storage(item_id):
        return failure("item_type_not_allowed")

    if get_item_quantity(state, item_id) < amount:
        return failure("not_enough_inventory_items")

    if not ship_storage.has_space_for_item(item_id):
        return failure("ship_storage_full")

    if not remove_item_quantity(state, item_id, amount):
        return failure("inventory_remove_failed")

    if ship_storage.add_item(item_id, amount):
        return success(item_id, amount)

    add_item(state, item_id, amount)
    return failure("ship_storage_add_failed")


def move_ship_storage_to_inventory(state, ship_storage, item_id, amount):
    validation_error = validate_transfer_request(item_id, amount)

    if validation_error is not None:
        return failure(validation_error)

    if not is_item_allowed_in_ship_storage(item_id):
        return failure("item_type_not_allowed")

    if ship_storage.get_item_amount(item_id) < amount:
        return failure("not_enough_ship_storage_items")

    if not can_add_item(state, item_id, amount):
        return failure("inventory_full")

    if not ship_storage.remove_item(item_id, amount):
        return failure("ship_storage_remove_failed")

    if add_item(state, item_id, amount):
        return success(item_id, amount)

    ship_storage.add_item(item_id, amount)
    return failure("inventory_add_failed")


def validate_transfer_request(item_id, amount):
    if get_item_data(item_id) is None:
        return "item_not_found"

    if amount <= 0:
        return "invalid_amount"

    return None


def is_item_allowed_in_ship_storage(item_id):
    item_data = get_item_data(item_id)

    if item_data is None:
        return False

    return item_data.get("type") in ALLOWED_SHIP_STORAGE_ITEM_TYPES


def success(item_id, amount):
    return {
        "success": True,
        "item_id": item_id,
        "amount": amount,
    }


def failure(reason):
    return {
        "success": False,
        "reason": reason,
    }


def run_smoke_test():
    state = {}
    ensure_inventory_state(state)
    add_item(state, "wood", 5)

    ship_storage = ShipStorage(max_slots=2)

    to_storage_result = move_inventory_to_ship_storage(
        state,
        ship_storage,
        "wood",
        3,
    )
    back_to_inventory_result = move_ship_storage_to_inventory(
        state,
        ship_storage,
        "wood",
        2,
    )

    return {
        "to_storage": to_storage_result,
        "back_to_inventory": back_to_inventory_result,
        "inventory_wood": get_item_quantity(state, "wood"),
        "storage_wood": ship_storage.get_item_amount("wood"),
    }


if __name__ == "__main__":
    print(run_smoke_test())
