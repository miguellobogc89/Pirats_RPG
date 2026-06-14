INVENTORY_ROWS = 2
INVENTORY_COLUMNS = 8
HOTBAR_ROW = 0


def ensure_inventory_state(state):
    if "inventory" not in state:
        state["inventory"] = {}

    state["inventory"]["rows"] = INVENTORY_ROWS
    state["inventory"]["columns"] = INVENTORY_COLUMNS

    state["inventory"]["active_hotbar_index"] = clamp_hotbar_index(
        state["inventory"].get("active_hotbar_index", 0)
    )

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

    if not isinstance(state["inventory"].get("grid"), list):
        store_migration_overflow(
            state,
            "inventory_migration_overflow",
            state["inventory"].get("grid"),
            "invalid_inventory_grid",
        )
        state["inventory"]["grid"] = []

    normalize_inventory_grid(state["inventory"]["grid"], state)
    state["inventory"]["rows"] = INVENTORY_ROWS
    state["inventory"]["columns"] = INVENTORY_COLUMNS


def clamp_hotbar_index(index):
    if not isinstance(index, int):
        return 0

    return max(0, min(INVENTORY_COLUMNS - 1, index))


def normalize_inventory_grid(grid, state=None):
    ensure_grid_size(grid)
    hidden_slots = trim_grid_to_contract(grid, INVENTORY_ROWS, INVENTORY_COLUMNS)

    for hidden_slot in hidden_slots:
        place_or_store_migration_slot(
            grid,
            hidden_slot,
            state,
            "inventory_migration_overflow",
            "inventory_hidden_slot",
        )

    for row_index in range(INVENTORY_ROWS):
        row = grid[row_index]

        for column_index in range(INVENTORY_COLUMNS):
            slot = row[column_index]

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
                    store_migration_overflow(
                        state,
                        "inventory_migration_overflow",
                        {
                            "item_id": slot["item_id"],
                            "amount": overflow_amount,
                        },
                        "inventory_stack_overflow",
                    )


def trim_grid_to_contract(grid, rows, columns):
    hidden_slots = []

    for row_index in range(rows):
        row = grid[row_index]

        if len(row) > columns:
            hidden_slots.extend(slot for slot in row[columns:] if slot is not None)
            del row[columns:]

    if len(grid) > rows:
        for row in grid[rows:]:
            hidden_slots.extend(slot for slot in row if slot is not None)

        del grid[rows:]

    return hidden_slots


def place_or_store_migration_slot(grid, slot, state, overflow_key, reason):
    from game.inventory.slot_model import create_stack
    from game.data.item_database import get_item_max_stack

    if not isinstance(slot, dict):
        store_migration_overflow(state, overflow_key, slot, reason)
        return

    item_id = slot.get("item_id")
    amount = slot.get("amount", 0)
    max_stack = get_item_max_stack(item_id)

    if max_stack <= 0 or amount <= 0:
        store_migration_overflow(state, overflow_key, slot, reason)
        return

    remaining_amount = amount

    for row in grid:
        for column_index, current_slot in enumerate(row):
            if current_slot is not None:
                continue

            stack_amount = min(max_stack, remaining_amount)
            row[column_index] = create_stack(item_id, stack_amount)
            remaining_amount -= stack_amount

            if remaining_amount <= 0:
                return

    store_migration_overflow(
        state,
        overflow_key,
        {
            "item_id": item_id,
            "amount": remaining_amount,
        },
        reason,
    )


def store_migration_overflow(state, key, slot, reason):
    if state is None:
        return

    state.setdefault(key, []).append({
        "reason": reason,
        "slot": slot,
    })
    record_migration_warning(
        state,
        f"{key}: no se pudo migrar todo el contenido ({reason}).",
    )


def record_migration_warning(state, message):
    warnings = state.setdefault("migration_warnings", [])

    if message not in warnings:
        warnings.append(message)


def ensure_grid_size(grid):
    while len(grid) < INVENTORY_ROWS:
        grid.append([])

    for row_index in range(INVENTORY_ROWS):
        while len(grid[row_index]) < INVENTORY_COLUMNS:
            grid[row_index].append(None)


def normalize_stack(slot):
    from game.inventory.slot_model import create_stack
    from game.data.item_database import get_item_max_stack

    if not isinstance(slot, dict):
        return None

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

    for row_index in range(INVENTORY_ROWS):
        row = grid[row_index]

        for column_index in range(INVENTORY_COLUMNS):
            slot = row[column_index]

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

    for row in grid[:INVENTORY_ROWS]:
        for column_index, slot in enumerate(row[:INVENTORY_COLUMNS]):
            if row is source_row and column_index == source_column_index:
                continue

            if slot is None:
                free_slots += 1

    return free_slots * max_stack >= amount
