INVENTORY_ROWS = 2
INVENTORY_COLUMNS = 8
HOTBAR_ROW = 0


def ensure_inventory_state(state):
    if "inventory" not in state:
        state["inventory"] = {}

    if "rows" not in state["inventory"]:
        state["inventory"]["rows"] = INVENTORY_ROWS

    if "columns" not in state["inventory"]:
        state["inventory"]["columns"] = INVENTORY_COLUMNS

    if "active_hotbar_index" not in state["inventory"]:
        state["inventory"]["active_hotbar_index"] = 0

    if "grid" not in state["inventory"]:
        state["inventory"]["grid"] = [
            [
                {"item_id": "axe", "amount": 1},
                {"item_id": "pickaxe", "amount": 1},
                {"item_id": "campfire", "amount": 1},
                {"item_id": "hoe", "amount": 1},
                {"item_id": "corn_seed", "amount": 10},
                {"item_id": "watering_can", "amount": 1},
                {"item_id": "rope", "amount": 100},
                None,
            ],
            [
                {"item_id": "wood", "amount": 100},
                {"item_id": "rope", "amount": 100},
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        ]

    normalize_inventory_grid(state["inventory"]["grid"])


def normalize_inventory_grid(grid):
    ensure_grid_size(grid)

    for row_index, row in enumerate(grid):
        for column_index, slot in enumerate(list(row)):
            if slot is None:
                continue

            normalized_stack = normalize_stack(slot)

            if normalized_stack is None:
                row[column_index] = None
                continue

            row[column_index] = normalized_stack
            overflow_amount = slot.get("amount", 0) - normalized_stack["amount"]

            if overflow_amount > 0:
                if can_distribute_stack_overflow(grid, slot["item_id"], overflow_amount, column_index, row):
                    distribute_stack_overflow(grid, slot["item_id"], overflow_amount)
                else:
                    row[column_index] = slot


def ensure_grid_size(grid):
    while len(grid) < INVENTORY_ROWS:
        grid.append([])

    for row_index in range(INVENTORY_ROWS):
        while len(grid[row_index]) < INVENTORY_COLUMNS:
            grid[row_index].append(None)


def normalize_stack(slot):
    from game.inventory.slot_model import create_stack
    from game.data.item_database import get_item_max_stack

    item_id = slot.get("item_id")
    amount = slot.get("amount", 0)
    max_stack = get_item_max_stack(item_id)

    if max_stack <= 0:
        return None

    return create_stack(item_id, min(amount, max_stack))


def distribute_stack_overflow(grid, item_id, amount):
    from game.inventory.slot_model import create_stack
    from game.data.item_database import get_item_max_stack

    max_stack = get_item_max_stack(item_id)
    remaining_amount = amount

    for row in grid:
        for column_index, slot in enumerate(row):
            if slot is not None:
                continue

            stack_amount = min(max_stack, remaining_amount)
            row[column_index] = create_stack(item_id, stack_amount)
            remaining_amount -= stack_amount

            if remaining_amount <= 0:
                return True

    return False


def can_distribute_stack_overflow(grid, item_id, amount, source_column_index, source_row):
    from game.data.item_database import get_item_max_stack

    max_stack = get_item_max_stack(item_id)
    free_slots = 0

    for row in grid:
        for column_index, slot in enumerate(row):
            if row is source_row and column_index == source_column_index:
                continue

            if slot is None:
                free_slots += 1

    return free_slots * max_stack >= amount
