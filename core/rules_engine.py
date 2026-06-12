import random

WINDS = ["north", "south", "east", "west", "calm"]


def current_season(state, game_data):
    return game_data["config"]["seasons"][state["season_index"]]


def can_pay(state, cost):
    for resource, amount in cost.items():
        if state["resources"].get(resource, 0) < amount:
            return False
    return True


def pay_cost(state, cost):
    for resource, amount in cost.items():
        state["resources"][resource] = state["resources"].get(resource, 0) - amount


def add_reward(state, reward):
    for resource, amount in reward.items():
        state["resources"][resource] = state["resources"].get(resource, 0) + amount


def has_requirements(state, requirements):
    for upgrade_key, required_value in requirements.items():
        if state["upgrades"].get(upgrade_key) != required_value:
            return False
    return True


def calculate_success(route, wind):
    success = route["base_success"]

    if wind == route["direction"]:
        success += 15
    elif wind != "calm":
        success -= 10

    return max(10, min(100, success))


def perform_action(state, game_data, action_key):
    action = game_data["actions"].get(action_key)
    if action is None:
        return "Accion no encontrada."

    energy_cost = action["energy_cost"]
    if state["energy"]["current"] < energy_cost:
        return "No tienes energia suficiente."

    state["energy"]["current"] -= energy_cost
    rewards = {}

    for resource, value_range in action["reward"].items():
        amount = random.randint(value_range[0], value_range[1])
        rewards[resource] = amount

    add_reward(state, rewards)

    reward_text = format_reward(rewards, game_data)
    return f"{action['message']} Obtenido: {reward_text}. Energia -{energy_cost}."


def start_trip(state, game_data, route_key):
    route = game_data["routes"].get(route_key)
    if route is None:
        return "Ruta no encontrada."

    if state["ship"]["status"] != "available":
        return "El barco no esta disponible."

    season = current_season(state, game_data)
    if season in route["season_block"]:
        return "Esta ruta esta bloqueada en esta estacion."

    if not has_requirements(state, route["requires"]):
        return "Falta una mejora para esta ruta."

    if not can_pay(state, route["cost"]):
        return "No tienes suministros suficientes."

    pay_cost(state, route["cost"])
    success = calculate_success(route, state["wind"])

    state["ship"] = {
        "status": "traveling",
        "days_left": route["duration"],
        "route": route_key,
        "success_rate": success,
        "pending_event": None,
        "secured_reward": {},
    }

    return f"El barco zarpa hacia {route['name']}. Exito estimado: {success}%."


def advance_day(state, game_data):
    messages = []
    config = game_data["config"]

    state["day"] += 1
    if state["day"] > config["season_days"]:
        state["day"] = 1
        state["season_index"] = (state["season_index"] + 1) % len(config["seasons"])
        messages.append(f"Cambia la estacion: {current_season(state, game_data)}.")

    state["energy"]["current"] = state["energy"]["max"]
    state["wind"] = random.choice(WINDS)
    messages.append("Duermes y recuperas energia.")

    ship = state["ship"]
    if ship["status"] == "traveling":
        ship["days_left"] -= 1
        route = game_data["routes"][ship["route"]]

        if ship["days_left"] <= 0:
            ship["pending_event"] = "arrival_decision"
            ship["secured_reward"] = route["safe_reward"].copy()
            messages.append(f"El barco llega a {route['name']}. Puedes asegurar botin o arriesgar.")
        else:
            messages.append(f"El barco sigue navegando. Faltan {ship['days_left']} dias.")

    return messages


def secure_return(state, game_data):
    ship = state["ship"]
    if ship.get("pending_event") != "arrival_decision":
        return "No hay decision pendiente."

    reward = ship["secured_reward"]
    add_reward(state, reward)
    route_name = game_data["routes"][ship["route"]]["name"]
    reset_ship(state)
    return f"El barco vuelve desde {route_name}. Botin asegurado: {format_reward(reward, game_data)}."


def continue_and_risk(state, game_data):
    ship = state["ship"]
    if ship.get("pending_event") != "arrival_decision":
        return "No hay decision pendiente."

    route = game_data["routes"][ship["route"]]
    roll = random.randint(1, 100)

    if roll <= ship["success_rate"]:
        reward = route["risk_reward"]
        add_reward(state, reward)
        result = f"Riesgo exitoso. Botin grande: {format_reward(reward, game_data)}."
    else:
        reward = {}
        for resource, amount in route["safe_reward"].items():
            reward[resource] = max(1, amount // 2)
        add_reward(state, reward)
        result = f"La expedicion sale mal. Botin reducido: {format_reward(reward, game_data)}."

    reset_ship(state)
    return result


def build_upgrade(state, game_data, upgrade_key):
    upgrade = game_data["upgrades"].get(upgrade_key)
    if upgrade is None:
        return "Mejora no encontrada."

    if state["upgrades"].get(upgrade_key):
        return "Ya tienes esta mejora."

    if not can_pay(state, upgrade["cost"]):
        return "No tienes recursos suficientes."

    pay_cost(state, upgrade["cost"])
    state["upgrades"][upgrade_key] = True
    return f"Mejora construida: {upgrade['name']}."


def reset_ship(state):
    state["ship"] = {
        "status": "available",
        "days_left": 0,
        "route": None,
        "success_rate": 0,
        "pending_event": None,
        "secured_reward": {},
    }


def format_reward(reward, game_data):
    parts = []
    for resource, amount in reward.items():
        resource_data = game_data["resources"].get(resource, {"name": resource, "icon": resource})
        parts.append(f"{resource_data['icon']} {amount}")
    return " | ".join(parts)
