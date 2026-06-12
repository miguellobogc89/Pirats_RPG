CROP_DATABASE = {
    "corn": {
        "name": "Maíz",
        "days_per_stage": [1, 2, 2],
        "harvest_item": "corn",
        "seed_item": "corn_seed",
        "max_dry_days": 2,
        "requires_water_to_grow": True,
    }
}


def get_crop_data(crop_id):
    return CROP_DATABASE.get(crop_id)