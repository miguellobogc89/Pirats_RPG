from game.inventory.inventory_state import normalize_stack


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

    if "rows" not in stash:
        stash["rows"] = STASH_ROWS

    if "columns" not in stash:
        stash["columns"] = STASH_COLUMNS

    if "grid" not in stash or not isinstance(stash.get("grid"), list):
        stash["grid"] = create_empty_stash_grid()

    normalize_stash_grid(stash["grid"], stash["rows"], stash["columns"])


def normalize_stash_grid(grid, rows, columns):
    ensure_stash_grid_size(grid, rows, columns)

    for row_index in range(rows):
        row = grid[row_index]

        for column_index in range(columns):
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
                distribute_stash_overflow(grid, slot["item_id"], overflow_amount, rows, columns)
            else:
                row[column_index] = slot


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

    for row in grid:
        for column_index, slot in enumerate(row):
            if row is source_row and column_index == source_column_index:
                continue

            if slot is None:
                free_slots += 1

    return free_slots * max_stack >= amount


def distribute_stash_overflow(grid, item_id, amount, rows, columns):
    from game.inventory.slot_model import create_stack
    from game.data.item_database import get_item_max_stack

    max_stack = get_item_max_stack(item_id)
    remaining_amount = amount

    for row_index in range(rows):
        row = grid[row_index]

        for column_index in range(columns):
            if row[column_index] is not None:
                continue

            stack_amount = min(max_stack, remaining_amount)
            row[column_index] = create_stack(item_id, stack_amount)
            remaining_amount -= stack_amount

            if remaining_amount <= 0:
                return True

    return False
