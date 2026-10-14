"""Single inventory transaction gateway for pickups, rewards, repairs and sales.

No game system should mutate inventory slots or shadow item counters directly.
"""
from game.inventory.inventory_manager import (
    add_item, can_add_item, get_item_quantity, remove_item_quantity,
)


def quantity(state, item_id):
    return get_item_quantity(state, item_id)


def receive(state, item_id, amount=1, *, receipt_id=None):
    if not isinstance(amount, int) or amount <= 0:
        return False
    receipts = state.setdefault("item_receipts", [])
    if receipt_id is not None and receipt_id in receipts:
        return False
    if not can_add_item(state, item_id, amount):
        return False
    if not add_item(state, item_id, amount):
        return False
    if receipt_id is not None:
        receipts.append(receipt_id)
    return True


def spend(state, item_id, amount=1):
    if not isinstance(amount, int) or amount <= 0:
        return False
    return remove_item_quantity(state, item_id, amount)


def spend_bundle(state, costs):
    """Validate all requirements first, then consume. No partial spending."""
    if not costs or any(not isinstance(n, int) or n <= 0 for n in costs.values()):
        return False
    if any(quantity(state, item_id) < n for item_id, n in costs.items()):
        return False
    return all(spend(state, item_id, n) for item_id, n in costs.items())


def migrate_chapter_items(state):
    """One-time migration of legacy farm counters into visible inventory."""
    progress = state.setdefault("farm_repairs", {})
    if progress.get("inventory_migrated"):
        return
    pending = {item: int(progress.get(item, 0)) for item in ("wood", "metal_bolt")}
    for item_id, amount in pending.items():
        if amount > 0 and not receive(state, item_id, amount):
            return
    for item_id in pending:
        progress[item_id] = 0
    progress["inventory_migrated"] = True
