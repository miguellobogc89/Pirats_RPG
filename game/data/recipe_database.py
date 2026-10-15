RECIPE_DATABASE = {
    "campfire": {
        "name": "Hoguera",
        "ingredients": {
            "wood": 10,
            "stone": 5,
        },
        "result_item": "campfire",
        "result_amount": 1,
    },
    "wooden_chest": {"name": "Caja de madera", "ingredients": {"wood": 20, "stone": 2}, "result_item": "wooden_chest", "result_amount": 1},
    "wood_floor": {"name": "Suelo de madera", "ingredients": {"wood": 4}, "result_item": "wood_floor", "result_amount": 1},
    "wooden_fence": {"name": "Valla de madera", "ingredients": {"wood": 6, "rope": 2}, "result_item": "wooden_fence", "result_amount": 1},
}


def get_recipe_data(recipe_id):
    return RECIPE_DATABASE.get(recipe_id)


def get_all_recipes():
    return RECIPE_DATABASE