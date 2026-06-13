import random


def generate_region_rewards(region_data):
    rewards = {}

    resource_table = region_data.get("resource_table", {})

    for resource_id, amount_range in resource_table.items():
        min_amount = amount_range[0]
        max_amount = amount_range[1]
        amount = random.randint(min_amount, max_amount)

        if amount > 0:
            rewards[resource_id] = amount

    chest_roll = random.randint(1, 100)

    if chest_roll >= 85:
        rewards["sealed_crate"] = rewards.get("sealed_crate", 0) + 1

    return rewards
