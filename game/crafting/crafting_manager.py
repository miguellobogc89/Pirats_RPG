from game.data.recipe_database import get_recipe_data
from game.inventory.inventory_manager import has_item, add_item, remove_item


def can_craft(state, recipe_id):
    recipe = get_recipe_data(recipe_id)

    if recipe is None:
        return False

    ingredients = recipe["ingredients"]

    for item_id, amount_required in ingredients.items():
        quantity = get_item_quantity(state, item_id)

        if quantity < amount_required:
            return False

    return True


def craft_item(state, recipe_id):
    recipe = get_recipe_data(recipe_id)

    if recipe is None:
        return "recipe_not_found"

    if not can_craft(state, recipe_id):
        return "missing_resources"

    ingredients = recipe["ingredients"]

    for item_id, amount_required in ingredients.items():
        remove_item(state, item_id, amount_required)

    add_item(
        state,
        recipe["result_item"],
        recipe["result_amount"],
    )

    return "crafted"


def get_item_quantity(state, item_id):
    inventory = state["inventory"]["grid"]

    total = 0

    for row in inventory:
        for slot in row:
            if slot is None:
                continue

            if slot["item_id"] == item_id:
                total += slot["amount"]

    return total