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
}


def get_recipe_data(recipe_id):
    return RECIPE_DATABASE.get(recipe_id)


def get_all_recipes():
    return RECIPE_DATABASE