import random

from core.save_manager import save_state
from game.inventory.hotbar_manager import get_active_tool
from game.scenes.scene_state import get_current_scene_state
from game.collectable_manager import spawn_collectables_from_drops
from game.npcs import interact_with_npc
from game.story_events import dispatch_story_event
from game.inventory.inventory_manager import add_item


def get_nearby_object(state, game_data, interaction_range, world_objects=None):
    player = state["player"]
    closest_object = None
    closest_distance = interaction_range

    removed_objects = set(get_current_scene_state(state).get("removed_objects", []))
    destroyed_objects = set(state.get("destroyed_world_objects", []))
    if world_objects is None:
        world_objects = []

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
    if getattr(app, "nearby_npc", None) is not None:
        interact_with_npc(app, app.nearby_npc)
        dispatch_story_event(
            app,
            "npc_talked",
            {
                "npc_id": app.nearby_npc.get("id"),
                "scene_id": app.state.get("current_scene"),
            },
        )
        return

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

    functional_type = world_object.get("functional_type", "decorative")
    functional_data = world_object.get("functional_data", {})

    if functional_type == "pickup":
        pickup_world_object(app, world_object)
        return

    if functional_type == "trigger":
        dispatch_object_interaction_event(app, world_object)
        return

    if functional_type in ("interactable", "container", "door"):
        dispatch_object_interaction_event(app, world_object)
        app.add_log(get_interaction_message(world_object))
        return

    if functional_type == "destructible":
        interact_with_resource_object(app, world_object)
        return

    app.add_log(get_interaction_message(world_object))


def prepare_slot_drag_for_save(app):
    if not app.slot_ui_state.is_dragging:
        return True

    from game.input.input_manager import cancel_slot_drag

    if cancel_slot_drag(app):
        return True

    app.add_log("No se puede guardar: coloca el item en una casilla libre primero.")
    return False


def interact_with_resource_object(app, world_object):
    if world_object.get("functional_type") != "destructible":
        app.add_log(get_interaction_message(world_object))
        return

    destructible_data = world_object.get("functional_data", {})
    required_tool = destructible_data.get("required_tool")

    if required_tool is not None:
        active_tool = get_active_tool(app.state)

        if active_tool != required_tool:
            app.add_log(f"No puedes usar esa herramienta con {world_object['name']}.")
            return

    energy_cost = destructible_data.get("energy_cost", 0)
    current_energy = app.state["energy"]["current"]

    if current_energy < energy_cost:
        app.add_log("No tienes energía suficiente.")
        return

    app.state["energy"]["current"] -= energy_cost
    world_object["hp"] -= 1

    app.add_log(f"Golpeas {world_object['name']}. Energía -{energy_cost}.")

    if world_object["hp"] <= 0:
        destroy_drops = roll_drops(destructible_data.get("drops", []))
        spawn_collectables_from_drops(app.state, destroy_drops, world_object["x"], world_object["y"])

        app.add_log(f"{world_object['name']} destruido.")

        if world_object["type"] in ("rock", "small_rock", "big_rock"):
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

        app.nearby_object = None

        if hasattr(app, "load_scene_runtime"):
            app.load_scene_runtime(app.state.get("current_scene", "farm"))


def get_interaction_message(world_object):
    functional_type = world_object.get("functional_type", "decorative")
    functional_data = world_object.get("functional_data", {})
    name = world_object.get("name", "Objeto")
    interaction_mode = functional_data.get("interaction_mode")

    if functional_type == "destructible":
        return f"{name} se puede romper."

    if functional_type == "pickup":
        return f"Recoges {name}."

    if functional_type == "trigger":
        return ""

    if interaction_mode == "inspect":
        return f"Inspeccionas {name}."

    if interaction_mode == "talk":
        return f"No parece querer hablar ahora."

    if interaction_mode == "open":
        return f"No puedes abrir {name} ahora."

    if interaction_mode == "use":
        return f"Usas {name}."

    if interaction_mode == "repair":
        return f"{name} necesita reparacion."

    if interaction_mode == "trigger":
        return ""

    return f"{name} no se puede destruir."


def dispatch_object_interaction_event(app, world_object):
    functional_data = world_object.get("functional_data", {})
    dispatch_story_event(
        app,
        "object_interacted",
        {
            "scene_id": app.state.get("current_scene"),
            "object_id": world_object.get("id"),
            "functional_type": world_object.get("functional_type"),
            "interaction_mode": functional_data.get("interaction_mode"),
            "interaction_id": functional_data.get(
                "interaction_id",
                world_object.get("properties", {}).get("interaction_id"),
            ),
        },
    )


def pickup_world_object(app, world_object):
    pickup_data = world_object.get("functional_data", {})
    item_id = pickup_data.get("item_id") or world_object.get("type")

    try:
        amount = int(pickup_data.get("quantity", 1))
    except (TypeError, ValueError):
        amount = 1

    if amount <= 0:
        amount = 1

    if not add_item(app.state, item_id, amount):
        app.add_log("Inventario lleno.")
        return

    scene_state = get_current_scene_state(app.state)

    if world_object["id"] not in scene_state["removed_objects"]:
        scene_state["removed_objects"].append(world_object["id"])

    app.add_log(f"Recoges {world_object.get('name', item_id)} x{amount}.")
    dispatch_story_event(
        app,
        "item_collected",
        {
            "item_id": item_id,
            "amount": amount,
            "scene_id": app.state.get("current_scene"),
        },
    )

    if hasattr(app, "load_scene_runtime"):
        app.load_scene_runtime(app.state.get("current_scene", "farm"))


def roll_drops(drops):
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
