from game.data.item_database import get_item_data, get_item_max_stack
from game.inventory.slot_model import can_stack, get_stack_space, is_valid_stack


class ShipStorageContainer:
    def __init__(self, ship_storage):
        self.ship_storage = ship_storage

    def get_slot_count(self):
        return self.ship_storage.max_slots

    def get_ordered_item_ids(self):
        return sorted(self.ship_storage.items)

    def is_valid_index(self, index):
        return index >= 0 and index < self.get_slot_count()

    def get_slot(self, index):
        if not self.is_valid_index(index):
            return None

        item_ids = self.get_ordered_item_ids()

        if index >= len(item_ids):
            return None

        item_id = item_ids[index]
        return {
            "item_id": item_id,
            "amount": self.ship_storage.items[item_id],
        }

    def set_slot(self, index, stack_or_none):
        if not self.is_valid_index(index):
            return False

        if not is_valid_stack(stack_or_none):
            return False

        item_ids = self.get_ordered_item_ids()
        current_item_id = None

        if index < len(item_ids):
            current_item_id = item_ids[index]

        if stack_or_none is None:
            if current_item_id is not None:
                del self.ship_storage.items[current_item_id]

            return True

        item_id = stack_or_none["item_id"]

        if item_id in self.ship_storage.items and item_id != current_item_id:
            return False

        if current_item_id is None and len(item_ids) >= self.get_slot_count():
            return False

        if current_item_id is not None and current_item_id != item_id:
            del self.ship_storage.items[current_item_id]

        self.ship_storage.items[item_id] = stack_or_none["amount"]
        return True

    def count_item(self, item_id):
        return self.ship_storage.items.get(item_id, 0)

    def can_accept(self, item_id, amount):
        if amount <= 0:
            return False

        if get_item_data(item_id) is None:
            return False

        remaining_amount = amount
        current_amount = self.ship_storage.items.get(item_id, 0)

        if current_amount > 0:
            if not can_stack(item_id):
                return False

            remaining_amount -= get_stack_space({
                "item_id": item_id,
                "amount": current_amount,
            })
            return remaining_amount <= 0

        if len(self.ship_storage.items) >= self.get_slot_count():
            return False

        return amount <= get_item_max_stack(item_id)
