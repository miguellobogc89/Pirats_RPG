REGION_DATABASE = {
    "home_port": {
        "id": "home_port",
        "name": "Puerto inicial",
        "description": "Punto de partida del jugador.",
        "connections": ["calm_waters"],
        "base_days": 0,
        "danger": 0,
        "resource_table": {},
        "has_port": True,
    },

    "calm_waters": {
        "id": "calm_waters",
        "name": "Aguas tranquilas",
        "description": "Primeras aguas seguras alrededor del puerto.",
        "connections": ["home_port", "driftwood_coast", "misty_reef"],
        "base_days": 1,
        "danger": 1,
        "resource_table": {
            "driftwood": [2, 5],
            "sea_fiber": [1, 3],
        },
        "has_port": False,
    },

    "driftwood_coast": {
        "id": "driftwood_coast",
        "name": "Costa de madera flotante",
        "description": "Zona rica en madera marina.",
        "connections": ["calm_waters", "old_lighthouse"],
        "base_days": 2,
        "danger": 2,
        "resource_table": {
            "driftwood": [4, 8],
            "salt_stone": [1, 2],
        },
        "has_port": False,
    },

    "misty_reef": {
        "id": "misty_reef",
        "name": "Arrecife nebuloso",
        "description": "Arrecife difícil de cartografiar.",
        "connections": ["calm_waters", "coral_banks"],
        "base_days": 2,
        "danger": 3,
        "resource_table": {
            "coral_fragment": [2, 5],
            "sea_fiber": [2, 4],
        },
        "has_port": False,
    },

    "old_lighthouse": {
        "id": "old_lighthouse",
        "name": "Faro abandonado",
        "description": "Antiguo punto de anclaje restaurable.",
        "connections": ["driftwood_coast", "iron_shoals"],
        "base_days": 3,
        "danger": 3,
        "resource_table": {
            "old_mechanism": [1, 1],
            "salt_stone": [2, 4],
        },
        "has_port": True,
    },

    "coral_banks": {
        "id": "coral_banks",
        "name": "Bancos de coral",
        "description": "Zona con materiales exclusivos para crafting avanzado.",
        "connections": ["misty_reef", "iron_shoals"],
        "base_days": 3,
        "danger": 4,
        "resource_table": {
            "coral_fragment": [5, 9],
            "black_pearl": [0, 1],
        },
        "has_port": False,
    },

    "iron_shoals": {
        "id": "iron_shoals",
        "name": "Bajíos de hierro",
        "description": "Zona peligrosa con minerales marinos.",
        "connections": ["old_lighthouse", "coral_banks"],
        "base_days": 4,
        "danger": 5,
        "resource_table": {
            "marine_iron": [2, 5],
            "salt_stone": [3, 6],
        },
        "has_port": False,
    },
}
