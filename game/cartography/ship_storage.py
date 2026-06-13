DEFAULT_SHIP_STORAGE_SLOTS = 16


class ShipStorage:
    def __init__(self, max_slots=DEFAULT_SHIP_STORAGE_SLOTS):
        self.max_slots = max_slots
        self.items = {}

    def get_used_slots(self):
        return len(self.items.keys())

    def get_item_amount(self, item_id):
        return self.items.get(item_id, 0)

    def get_items_snapshot(self):
        return [
            {
                "item_id": item_id,
                "amount": amount,
            }
            for item_id, amount in self.items.items()
        ]

    def has_space_for_item(self, item_id):
        if item_id in self.items:
            return True

        if self.get_used_slots() < self.max_slots:
            return True

        return False

    def add_item(self, item_id, amount):
        if amount <= 0:
            return False

        if not self.has_space_for_item(item_id):
            return False

        current_amount = self.items.get(item_id, 0)
        self.items[item_id] = current_amount + amount
        return True

    def remove_item(self, item_id, amount):
        if item_id not in self.items:
            return False

        if self.items[item_id] < amount:
            return False

        self.items[item_id] -= amount

        if self.items[item_id] <= 0:
            del self.items[item_id]

        return True

    def has_items(self, requirements):
        for item_id, required_amount in requirements.items():
            current_amount = self.items.get(item_id, 0)

            if current_amount < required_amount:
                return False

        return True

    def get_save_data(self):
        return {
            "max_slots": self.max_slots,
            "items": self.items,
        }

    def load_from_data(self, data):
        if not data:
            return

        self.max_slots = data.get("max_slots", self.max_slots)
        self.items = data.get("items", self.items)
