from game.inventory.inventory_state import (
    normalize_stack,
    place_or_store_migration_slot,
    store_migration_overflow,
    trim_grid_to_contract,
)


STASH_ROWS = 3
STASH_COLUMNS = 8


def create_default_stash_state():
    return {
        "rows": STASH_ROWS,
        "columns": STASH_COLUMNS,
        "grid": create_empty_stash_grid(),
    }


def create_empty_stash_grid():
    return [
        [None for _ in range(STASH_COLUMNS)]
        for _ in range(STASH_ROWS)
    ]


def ensure_stash_state(state):
    if "stash" not in state or not isinstance(state.get("stash"), dict):
        state["stash"] = create_default_stash_state()

    stash = state["stash"]
    stash["rows"] = STASH_ROWS
    stash["columns"] = STASH_COLUMNS

    if "grid" not in stash or not isinstance(stash.get("grid"), list):
        if "grid" in stash:
            store_migration_overflow(
                state,
                "stash_migration_overflow",
                stash.get("grid"),
                "invalid_stash_grid",
            )

        stash["grid"] = create_empty_stash_grid()

    normalize_stash_grid(stash["grid"], state)
    stash["rows"] = STASH_ROWS
    stash["columns"] = STASH_COLUMNS


def normalize_stash_grid(grid, state=None):
    ensure_stash_grid_size(grid, STASH_ROWS, STASH_COLUMNS)
    hidden_slots = trim_grid_to_contract(grid, STASH_ROWS, STASH_COLUMNS)

    for hidden_slot in hidden_slots:
        place_or_store_migration_slot(
            grid,
            hidden_slot,
            state,
            "stash_migration_overflow",
            "stash_hidden_slot",
        )

    for row_index in range(STASH_ROWS):
        row = grid[row_index]

        for column_index in range(STASH_COLUMNS):
            slot = row[column_index]

            if slot is None:
                continue

            normalized_stack = normalize_stack(slot)

            if normalized_stack is None:
                row[column_index] = None
                continue

            row[column_index] = normalized_stack
            overflow_amount = slot.get("amount", 0) - normalized_stack["amount"]

            if overflow_amount <= 0:
                continue

            if can_distribute_stash_overflow(grid, slot["item_id"], overflow_amount, row, column_index):
                distribute_stash_overflow(grid, slot["item_id"], overflow_amount)
            else:
                store_migration_overflow(
                    state,
                    "stash_migration_overflow",
                    {
                        "item_id": slot["item_id"],
                        "amount": overflow_amount,
                    },
                    "stash_stack_overflow",
                )


def ensure_stash_grid_size(grid, rows, columns):
    while len(grid) < rows:
        grid.append([])

    for row_index in range(rows):
        while len(grid[row_index]) < columns:
            grid[row_index].append(None)


def can_distribute_stash_overflow(grid, item_id, amount, source_row, source_column_index):
    from game.data.item_database import get_item_max_stack

    max_stack = get_item_max_stack(item_id)
    free_slots = 0

    for row in grid[:STASH_ROWS]:
        for column_index, slot in enumerate(row[:STASH_COLUMNS]):
            if row is source_row and column_index == source_column_index:
                continue

            if slot is None:
                free_slots += 1

    return free_slots * max_stack >= amount


def distribute_stash_overflow(grid, item_id, amount):
    from game.inventory.slot_model import create_stack
    from game.data.item_database import get_item_max_stack

    max_stack = get_item_max_stack(item_id)
    remaining_amount = amount

    for row_index in range(STASH_ROWS):
        row = grid[row_index]

        for column_index in range(STASH_COLUMNS):
            if row[column_index] is not None:
                continue

            stack_amount = min(max_stack, remaining_amount)
            row[column_index] = create_stack(item_id, stack_amount)
            remaining_amount -= stack_amount

            if remaining_amount <= 0:
                return True

    return False
