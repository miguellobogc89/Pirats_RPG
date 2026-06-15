FUNCTIONAL_TYPES = (
    "decorative",
    "npc",
    "interactable",
    "destructible",
    "pickup",
    "trigger",
    "container",
    "door",
)

INTERACTION_MODES = (
    "inspect",
    "talk",
    "use",
    "open",
    "repair",
)

REQUIRED_TOOLS = (
    None,
    "axe",
    "pickaxe",
    "sword",
)

ROOT_FIELDS = frozenset(
    {
        "id",
        "name",
        "category",
        "functional_type",
        "visual",
        "collision",
        "npc",
        "interactable",
        "destructible",
        "pickup",
        "trigger",
        "container",
        "door",
    }
)

FUNCTIONAL_BLOCKS = frozenset(
    {
        "npc",
        "interactable",
        "destructible",
        "pickup",
        "trigger",
        "container",
        "door",
    }
)

LEGACY_ROOT_FIELDS = frozenset(
    {
        "type",
        "sprite",
        "sprite_offset",
        "sprite_size",
        "visual_size",
        "footprint",
        "footprint_anchor",
        "solid",
        "interaction_points",
        "interaction_mode",
        "pickup_mode",
        "pickable_interactable",
        "required_tool",
        "dialogue_id",
        "target_scene",
        "stackable",
        "hp",
        "max_hp",
        "energy_cost",
        "drops",
        "properties",
    }
)

DEFAULT_VISUAL = {
    "sprite": "",
    "sprite_offset": [0, 0],
    "sprite_size": None,
    "visual_size": None,
}

DEFAULT_COLLISION = {
    "footprint": [1, 1],
    "footprint_anchor": "center",
    "solid": True,
    "interaction_points": [],
}

FUNCTIONAL_BLOCK_DEFAULTS = {
    "decorative": {},
    "npc": {
        "npc_id": "",
        "dialogue_id": "",
        "portrait_path": "",
    },
    "interactable": {
        "interaction_mode": "inspect",
        "interaction_id": "",
        "required_item": "",
    },
    "destructible": {
        "hp": 1,
        "required_tool": None,
        "energy_cost": 0,
        "drops": [],
    },
    "pickup": {
        "item_id": "",
        "quantity": 1,
    },
    "trigger": {
        "trigger_id": "",
        "target_event": "",
        "once": False,
    },
    "container": {
        "container_id": "",
        "capacity": 16,
        "locked": False,
        "required_key": "",
    },
    "door": {
        "door_id": "",
        "locked": False,
        "required_key": "",
        "interaction_id": "",
    },
}


def is_valid_functional_type(functional_type):
    return functional_type in FUNCTIONAL_TYPES


def get_functional_block_name(functional_type):
    if functional_type in FUNCTIONAL_BLOCKS:
        return functional_type

    return None
