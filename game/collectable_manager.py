import random

from game.inventory.inventory_manager import add_item
from game.data.item_database import get_item_data


COLLECT_RADIUS = 28


def ensure_collectables_state(state):
    if "collectables" not in state:
        state["collectables"] = []


def spawn_collectables_from_drops(state, drops, origin_x, origin_y):
    ensure_collectables_state(state)

    for drop in drops:
        offset_x = random.randint(-18, 18)
        offset_y = random.randint(-18, 18)

        collectable = {
            "id": f"collectable_{len(state['collectables'])}_{random.randint(1000, 9999)}",
            "item_id": drop["item_id"],
            "amount": drop["amount"],
            "x": origin_x + offset_x,
            "y": origin_y + offset_y,
            "radius": 10,
        }

        state["collectables"].append(collectable)


def update_collectables(app):
    ensure_collectables_state(app.state)

    player = app.state["player"]
    collected = []

    for collectable in app.state["collectables"]:
        dx = collectable["x"] - player["x"]
        dy = collectable["y"] - player["y"]
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > COLLECT_RADIUS:
            continue

        added = add_item(
            app.state,
            collectable["item_id"],
            collectable["amount"],
        )

        if not added:
            app.add_log("Inventario lleno.")
            continue

        item_data = get_item_data(collectable["item_id"])
        item_name = collectable["item_id"]

        if item_data is not None:
            item_name = item_data["name"]

        app.add_log(f"Recoges {item_name} x{collectable['amount']}.")
        app.skill_manager.register_action("collectable_picked")
        collected.append(collectable)

    for collectable in collected:
        app.state["collectables"].remove(collectable)