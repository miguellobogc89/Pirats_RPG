"""Headless crafting engine: recipes + inventory + optional context -> result."""
from game.data.recipe_database import get_recipe_data
from game.inventory.item_transactions import quantity, exchange
from game.inventory.inventory_manager import can_add_item, get_inventory_grid
from copy import deepcopy


def check_requirements(state, recipe, context=None):
    """Future-proof recipe requirements. No station/skill requirement by default."""
    context = context or {}
    requirements = recipe.get("requirements", {})
    station = requirements.get("station")
    if station and station not in context.get("stations", []):
        return "missing_station"
    for skill_id, minimum in requirements.get("skills", {}).items():
        if state.get("skills", {}).get(skill_id, {}).get("level", 0) < minimum:
            return "missing_skill"
    return None


def check_craft(state, recipe_id, context=None):
    recipe = get_recipe_data(recipe_id)
    if recipe is None:
        return "recipe_not_found"
    if check_requirements(state, recipe, context):
        return check_requirements(state, recipe, context)
    ingredients = recipe.get("ingredients", {})
    if any(quantity(state, item_id) < amount for item_id, amount in ingredients.items()):
        return "missing_resources"
    # Preflight output capacity on a copy AFTER spending the ingredients.
    from game.inventory.item_transactions import spend, can_receive
    simulation = {"inventory": deepcopy(state["inventory"])} if "inventory" in state else {}
    if any(not spend(simulation, item_id, amount) for item_id, amount in ingredients.items()):
        return "missing_resources"
    if not can_receive(simulation, recipe["result_item"], recipe["result_amount"]):
        return "inventory_full"
    return "ready"


def can_craft(state, recipe_id, context=None):
    return check_craft(state, recipe_id, context) == "ready"


def craft_item(state, recipe_id, skill_manager=None, context=None):
    status = check_craft(state, recipe_id, context)
    if status != "ready":
        return {"status": status, "skill_result": None}
    recipe = get_recipe_data(recipe_id)
    if not exchange(state, recipe["ingredients"], {recipe["result_item"]: recipe["result_amount"]}):
        return {"status": "inventory_full", "skill_result": None}
    skill_result = skill_manager.register_action("item_crafted") if skill_manager else None
    return {"status": "crafted", "skill_result": skill_result,
            "item_id": recipe["result_item"], "amount": recipe["result_amount"]}


def get_item_quantity(state, item_id):
    """Compatibility for callers using the original June API."""
    return quantity(state, item_id)
