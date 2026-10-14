"""Persistent equipped armor slots, independent of inventory stacks."""
EQUIPMENT_SLOTS = ("head", "torso", "gloves", "pants", "boots")


def ensure_equipment_state(state):
    equipment = state.setdefault("equipment", {})
    for slot in EQUIPMENT_SLOTS:
        equipment.setdefault(slot, None)
    return equipment


def armor_slot(item_id):
    from game.data.item_database import get_item_data
    data = get_item_data(item_id) or {}
    if data.get("type") != "armor":
        return None
    name = item_id.lower()
    if "boot" in name:
        return "boots"
    if "glove" in name:
        return "gloves"
    if "pant" in name or "legging" in name:
        return "pants"
    if "chestplate" in name or "tunic" in name or "armor" in name:
        return "torso"
    if "helmet" in name or "hat" in name or "hood" in name:
        return "head"
    return None
