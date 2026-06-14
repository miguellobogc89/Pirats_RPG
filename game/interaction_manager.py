import random

from core.save_manager import save_state
from game.inventory.hotbar_manager import get_active_tool
from game.scenes.scene_state import get_current_scene_state
from game.world_objects import WORLD_OBJECTS
from game.collectable_manager import spawn_collectables_from_drops


def get_nearby_object(state, game_data, interaction_range, world_objects=None):
    player = state["player"]
    closest_object = None
    closest_distance = interaction_range

    removed_objects = set(get_current_scene_state(state).get("removed_objects", []))
    destroyed_objects = set(state.get("destroyed_world_objects", []))
    if world_objects is None:
        world_objects = WORLD_OBJECTS

    for world_object in world_objects:
        if world_object["id"] in removed_objects or world_object["id"] in destroyed_objects:
            continue

        dx = world_object["x"] - player["x"]
        dy = world_object["y"] - player["y"]
        distance = (dx * dx + dy * dy) ** 0.5

        if distance <= closest_distance:
            closest_object = world_object
            closest_distance = distance

    return closest_object


def interact_with_nearby_object(app):
    if app.nearby_object is None:
        app.add_log("No hay nada cerca con lo que interactuar.")
        return

    world_object = app.nearby_object

    if world_object["type"] == "ship":
        app.cartography_menu_open = True
        app.add_log("Abres el mapa cartográfico.")
        return

    if world_object["type"] == "dock":
        app.menu_open = True
        app.menu_tab = "routes"
        return

    if world_object["type"] == "bed":
        if not prepare_slot_drag_for_save(app):
            return

        app.sleep_day()
        save_state(app.state)
        app.add_log("Has dormido y la partida se ha guardado.")
        return

    if world_object["type"] == "stash":
        app.slot_ui_state.cancel_drag()
        app.stash_open = True
        app.menu_open = False
        app.cartography_menu_open = False
        app.add_log("Abres el cofre.")
        return

    interact_with_resource_object(app, world_object)


def prepare_slot_drag_for_save(app):
    if not app.slot_ui_state.is_dragging:
        return True

    from game.input.input_manager import cancel_slot_drag

    if cancel_slot_drag(app):
        return True

    app.add_log("No se puede guardar: coloca el item en una casilla libre primero.")
    return False


def interact_with_resource_object(app, world_object):
    required_tool = world_object.get("required_tool")

    if required_tool is not None:
        active_tool = get_active_tool(app.state)

        if active_tool != required_tool:
            app.add_log(f"No puedes usar esa herramienta con {world_object['name']}.")
            return

    energy_cost = world_object.get("energy_cost", 0)
    current_energy = app.state["energy"]["current"]

    if current_energy < energy_cost:
        app.add_log("No tienes energía suficiente.")
        return

    app.state["energy"]["current"] -= energy_cost
    world_object["hp"] -= 1

    app.add_log(f"Golpeas {world_object['name']}. Energía -{energy_cost}.")

    hit_drops = roll_drops(world_object, "on_hit")
    spawn_collectables_from_drops(app.state, hit_drops, world_object["x"], world_object["y"])

    if world_object["hp"] <= 0:
        destroy_drops = roll_drops(world_object, "on_destroy")
        spawn_collectables_from_drops(app.state, destroy_drops, world_object["x"], world_object["y"])

        app.add_log(f"{world_object['name']} destruido.")

        if world_object["type"] == "rock":
            app.skill_manager.register_action("rock_destroyed")

        if world_object["type"] == "tree":
            app.skill_manager.register_action("tree_destroyed")


        scene_state = get_current_scene_state(app.state)

        if world_object["id"] not in scene_state["removed_objects"]:
            scene_state["removed_objects"].append(world_object["id"])

        if "destroyed_world_objects" not in app.state:
            app.state["destroyed_world_objects"] = []

        if world_object["id"] not in app.state["destroyed_world_objects"]:
            app.state["destroyed_world_objects"].append(world_object["id"])

        if world_object in WORLD_OBJECTS:
            WORLD_OBJECTS.remove(world_object)

        app.nearby_object = None

        if hasattr(app, "load_scene_runtime"):
            app.load_scene_runtime(app.state.get("current_scene", "farm"))


def roll_drops(world_object, drop_moment):
    drops = world_object.get("drops", {}).get(drop_moment, [])
    rolled_drops = []

    for drop in drops:
        chance = drop.get("chance", 100)
        roll = random.randint(1, 100)

        if roll > chance:
            continue

        amount = roll_drop_amount(drop.get("amount", 1))

        if amount <= 0:
            continue

        rolled_drops.append(
            {
                "item_id": drop["item_id"],
                "amount": amount,
            }
        )

    return rolled_drops


def roll_drop_amount(amount_data):
    if isinstance(amount_data, list):
        minimum = amount_data[0]
        maximum = amount_data[1]
        return random.randint(minimum, maximum)

    return amount_data


def add_drops_to_resources(app, drops):
    if not drops:
        return

    if "resources" not in app.state:
        app.state["resources"] = {}

    gained_parts = []

    for drop in drops:
        item_id = drop["item_id"]
        amount = drop["amount"]

        app.state["resources"][item_id] = app.state["resources"].get(item_id, 0) + amount
        gained_parts.append(f"{item_id} x{amount}")

    app.add_log(f"Obtienes {', '.join(gained_parts)}.")
