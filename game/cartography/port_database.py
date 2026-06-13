PORT_DATABASE = {
    "home_port": {
        "id": "home_port",
        "region_id": "home_port",
        "name": "Puerto inicial",
        "is_starting_port": True,
        "requirements": {},
    },

    "old_lighthouse_port": {
        "id": "old_lighthouse_port",
        "region_id": "old_lighthouse",
        "name": "Faro abandonado",
        "is_starting_port": False,
        "requirements": {
            "driftwood": 20,
            "salt_stone": 8,
            "old_mechanism": 1,
        },
    },
}
