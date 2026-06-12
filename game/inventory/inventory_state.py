DEFAULT_INVENTORY_CAPACITY = 24


def ensure_inventory_state(state):
    if "inventory" not in state:
        state["inventory"] = {}

    if "capacity" not in state["inventory"]:
        state["inventory"]["capacity"] = DEFAULT_INVENTORY_CAPACITY

    if "items" not in state["inventory"]:
        state["inventory"]["items"] = {
            "axe": 1,
            "pickaxe": 1,
            "fishing_rod": 1,
        }