ITEM_DATABASE = {
    "axe": {
        "name": "Hacha",
        "type": "tool",
        "tool_type": "axe",
        "icon": "A",
        "stackable": False,
    },
    "pickaxe": {
        "name": "Pico",
        "type": "tool",
        "tool_type": "pickaxe",
        "icon": "P",
        "stackable": False,
    },
    "fishing_rod": {
        "name": "Caña",
        "type": "tool",
        "tool_type": "fishing_rod",
        "icon": "C",
        "stackable": False,
    },
    "wood": {
        "name": "Madera",
        "type": "resource",
        "icon": "W",
        "stackable": True,
    },
    "iron": {
        "name": "Hierro",
        "type": "resource",
        "icon": "I",
        "stackable": True,
    },
    "carbon": {
        "name": "Carbón",
        "type": "resource",
        "icon": "K",
        "stackable": True,
    },
    "food": {
        "name": "Comida",
        "type": "resource",
        "icon": "F",
        "stackable": True,
    },
}


def get_item_data(item_id):
    return ITEM_DATABASE.get(item_id)