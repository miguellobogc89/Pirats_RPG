import random

from game.inventory.hotbar_manager import get_active_tool
from game.world_objects import WORLD_OBJECTS
from core.save_manager import save_state


def get_nearby_object(state, game_data, interaction_range):
    player = state["player"]
    closest_object = None
    closest_distance = interaction_range

    for world_object in WORLD_OBJECTS:
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

    if world_object["type"] == "dock":
        app.menu_open = True
        app.menu_tab = "routes"
        return
    
    if world_object["type"] == "bed":
        app.sleep_day()
        save_state(app.state)
        app.add_log("Has dormido y la partida se ha guardado.")
        return

    interact_with_resource_object(app, world_object)


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

    reward_on_hit = world_object.get("reward_on_hit", {})
    apply_reward(app.state, reward_on_hit)

    app.add_log(f"Golpeas {world_object['name']}. Energía -{energy_cost}.")

    if world_object["hp"] <= 0:
        reward_on_destroy = world_object.get("reward_on_destroy", {})
        gained_text = apply_reward(app.state, reward_on_destroy)

        app.add_log(f"{world_object['name']} destruido.")

        if gained_text:
            app.add_log(f"Obtienes {gained_text}.")

        WORLD_OBJECTS.remove(world_object)
        app.nearby_object = None


def apply_reward(state, reward_data):
    gained_parts = []

    for resource, value in reward_data.items():
        amount = roll_reward_amount(value)
        state["resources"][resource] = state["resources"].get(resource, 0) + amount
        gained_parts.append(f"{resource} x{amount}")

    return ", ".join(gained_parts)


def roll_reward_amount(value):
    if isinstance(value, list):
        minimum = value[0]
        maximum = value[1]
        return random.randint(minimum, maximum)

    return value