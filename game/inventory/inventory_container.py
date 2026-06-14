from game.data.item_database import get_item_data, get_item_max_stack
from game.inventory.inventory_state import ensure_inventory_state
from game.inventory.slot_model import can_stack, get_stack_space, is_valid_stack


class InventoryContainer:
    def __init__(self, state):
        self.state = state
        ensure_inventory_state(self.state)

    @property
    def inventory(self):
        return self.state["inventory"]

    @property
    def rows(self):
        return self.inventory["rows"]

    @property
    def columns(self):
        return self.inventory["columns"]

    @property
    def grid(self):
        return self.inventory["grid"]

    def get_slot_count(self):
        return self.rows * self.columns

    def index_to_position(self, index):
        if index < 0 or index >= self.get_slot_count():
            return None

        return index // self.columns, index % self.columns

    def position_to_index(self, row, column):
        if row < 0 or row >= self.rows:
            return None

        if column < 0 or column >= self.columns:
            return None

        return row * self.columns + column

    def get_slot(self, index):
        position = self.index_to_position(index)

        if position is None:
            return None

        row, column = position
        return self.grid[row][column]

    def set_slot(self, index, stack_or_none):
        position = self.index_to_position(index)

        if position is None:
            return False

        if not is_valid_stack(stack_or_none):
            return False

        row, column = position
        self.grid[row][column] = stack_or_none
        return True

    def count_item(self, item_id):
        total = 0

        for row in self.grid:
            for slot in row:
                if slot is None:
                    continue

                if slot["item_id"] == item_id:
                    total += slot["amount"]

        return total

    def can_accept(self, item_id, amount):
        if amount <= 0:
            return False

        if get_item_data(item_id) is None:
            return False

        remaining_amount = amount

        if can_stack(item_id):
            for row in self.grid:
                for slot in row:
                    if slot is None:
                        continue

                    if slot["item_id"] != item_id:
                        continue

                    remaining_amount -= get_stack_space(slot)

                    if remaining_amount <= 0:
                        return True

        max_stack = get_item_max_stack(item_id)

        for row in self.grid:
            for slot in row:
                if slot is None:
                    remaining_amount -= max_stack

                    if remaining_amount <= 0:
                        return True

        return False
