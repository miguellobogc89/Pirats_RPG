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
    "hoe": {
        "name": "Azada",
        "type": "tool",
        "tool_type": "hoe",
        "icon": "H",
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
    "stone": {
        "name": "Piedra",
        "type": "resource",
        "icon": "S",
        "stackable": True,
    },
    "gold": {
        "name": "Oro",
        "type": "currency",
        "icon": "G",
        "stackable": True,
    },
    "corn_seed": {
    "name": "Semilla de maíz",
    "type": "seed",
    "crop_id": "corn",
    "icon": "s",
    "stackable": True,
},
"corn": {
    "name": "Maíz",
    "type": "crop",
    "icon": "M",
    "stackable": True,
},
"watering_can": {
    "name": "Regadera",
    "type": "tool",
    "tool_type": "watering_can",
    "icon": "R",
    "stackable": False,
},
"campfire": {
    "name": "Hoguera",
    "type": "placeable",
    "icon": "O",
    "stackable": True,
},
"wood_floor": {
    "name": "Suelo madera",
    "type": "placeable",
    "icon": "=",
    "stackable": True,
},
"campfire": {
    "name": "Hoguera",
    "type": "placeable",
    "icon": "O",
    "stackable": True,
    "footprint": [2, 2]
},
}


def get_item_data(item_id):
    return ITEM_DATABASE.get(item_id)