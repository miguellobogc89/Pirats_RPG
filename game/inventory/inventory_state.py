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
                None,
                None,
                None,
            ],
            [None, None, None, None, None, None, None, None],
        ]