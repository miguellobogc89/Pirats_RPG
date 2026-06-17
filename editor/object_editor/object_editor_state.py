from copy import deepcopy

from game.objects.object_normalizer import normalize_object_definition
from game.objects.object_schema import FUNCTIONAL_BLOCK_DEFAULTS
from game.objects.object_validator import validate_object_definition


DYNAMIC_FIELD_DEFAULTS = {
    "npc_id": "",
    "dialogue_id": "",
    "portrait_path": "",
    "interaction_id": "",
    "interaction_mode": "inspect",
    "required_item": "",
    "hp": 1,
    "required_tool": None,
    "energy_cost": 0,
    "drops": [],
    "item_id": "",
    "quantity": 1,
    "trigger_id": "",
    "target_event": "",
    "once": False,
    "container_id": "",
    "capacity": 16,
    "locked": False,
    "required_key": "",
    "door_id": "",
}

FUNCTIONAL_TYPE_FIELDS = {
    "decorative": [],
    "npc": ["npc_id", "dialogue_id", "portrait_path"],
    "interactable": ["interaction_mode", "interaction_id", "required_item"],
    "destructible": ["hp", "required_tool", "energy_cost", "drops"],
    "pickup": ["item_id", "quantity"],
    "trigger": ["trigger_id", "target_event", "once"],
    "container": ["container_id", "capacity", "locked", "required_key"],
    "door": ["door_id", "locked", "required_key", "interaction_id"],
}

NUMERIC_DYNAMIC_FIELDS = {"hp", "energy_cost", "quantity", "capacity"}
BOOL_DYNAMIC_FIELDS = {"once", "locked"}


class ObjectEditorState:
    def __init__(self):
        self.object_id = ""
        self.name = ""
        self.sprite = ""
        self.source_sprite_path = ""
        self.footprint = [1, 1]
        self.footprint_preview_offset = [0, 0]
        self.footprint_anchor = "center"
        self.sprite_offset = [0, 0]
        self.sprite_size = None
        self.visual_size = None
        self.solid = True
        self.stackable = False
        self.functional_type = "decorative"
        self.interaction_mode = "inspect"
        self.destructible = False
        self.required_tool = None
        self.interaction_points = []
        self.dynamic_fields = deepcopy(DYNAMIC_FIELD_DEFAULTS)
        self.validation_warnings = []
        self.validation_errors = []
        self.category = "other"
        self.status_message = ""
        self.selected_field = None
        self.text_cursor = 0
        self.text_selection = None
        self.selected_element = None
        self.original_object_id = None
        self.preview_zoom = 1.0
        self.preview_pan = [0, 0]
        self.inspector_scroll_y = 0
        self.inspector_max_scroll = 0
        self.open_groups = {
            "General": True,
            "Rendering": True,
            "Collision": True,
            "Inventory": True,
            "Behaviour": True,
            "Interaction Points": True,
        }
        self.floating_dropdown = None
        self.floating_dropdown_scroll_y = 0
        self.floating_dropdown_max_scroll = 0
        self.floating_dropdown_rect = None

    def to_definition(self):
        data = {
            "id": self.object_id,
            "name": self.name,
            "category": self.category.lower(),
            "functional_type": self.functional_type,
            "visual": {
                "sprite": self.sprite,
                "sprite_offset": self.sprite_offset,
                "sprite_size": self.sprite_size,
                "visual_size": self.visual_size,
            },
            "collision": {
                "footprint": self.footprint,
                "footprint_anchor": self.footprint_anchor,
                "solid": self.solid,
                "interaction_points": self.interaction_points,
            },
        }

        block = self.build_functional_block()

        if block:
            data[self.functional_type] = block

        return data

    def build_functional_block(self):
        if self.functional_type == "decorative":
            return {}

        defaults = FUNCTIONAL_BLOCK_DEFAULTS.get(self.functional_type, {})
        block = {}

        for field_name in defaults:
            block[field_name] = self.get_dynamic_field(field_name)

        return block

    def load_from_definition(self, object_id, definition):
        normalized_definition = normalize_object_definition(definition, object_id)
        visual = normalized_definition["visual"]
        collision = normalized_definition["collision"]

        self.object_id = normalized_definition["id"]
        self.original_object_id = normalized_definition["id"]
        self.name = normalized_definition.get("name", "")
        self.category = normalized_definition.get("category", "other")
        self.functional_type = normalized_definition.get("functional_type", "decorative")
        self.sprite = visual.get("sprite", "")
        self.source_sprite_path = self.sprite
        self.sprite_offset = list(visual.get("sprite_offset", [0, 0]))
        self.sprite_size = visual.get("sprite_size")
        self.visual_size = visual.get("visual_size")
        self.footprint = list(collision.get("footprint", [1, 1]))
        self.footprint_anchor = collision.get("footprint_anchor", "center")
        self.footprint_preview_offset = [0, 0]
        self.solid = bool(collision.get("solid", True))
        self.interaction_points = [
            list(point)
            for point in collision.get("interaction_points", [])
            if isinstance(point, list) and len(point) >= 2
        ]
        self.dynamic_fields = deepcopy(DYNAMIC_FIELD_DEFAULTS)
        self.load_dynamic_fields(normalized_definition)
        self.interaction_mode = self.get_dynamic_field("interaction_mode")
        self.required_tool = self.get_dynamic_field("required_tool")
        self.destructible = self.functional_type == "destructible"
        self.refresh_validation()

    def apply_interaction_rules(self):
        return

    def load_dynamic_fields(self, definition):
        block = definition.get(self.functional_type, {})

        if not isinstance(block, dict):
            block = {}

        for field_name, default_value in DYNAMIC_FIELD_DEFAULTS.items():
            self.dynamic_fields[field_name] = block.get(field_name, default_value)

    def get_dynamic_field(self, field_name):
        value = self.dynamic_fields.get(field_name, DYNAMIC_FIELD_DEFAULTS.get(field_name, ""))

        if field_name in NUMERIC_DYNAMIC_FIELDS:
            try:
                return int(value)
            except (TypeError, ValueError):
                return DYNAMIC_FIELD_DEFAULTS.get(field_name, 0)

        if field_name in BOOL_DYNAMIC_FIELDS:
            return bool(value)

        if field_name == "drops":
            return value if isinstance(value, list) else []

        return value

    def set_dynamic_field(self, field_name, value):
        if field_name in NUMERIC_DYNAMIC_FIELDS:
            self.dynamic_fields[field_name] = value
            return

        if field_name in BOOL_DYNAMIC_FIELDS:
            self.dynamic_fields[field_name] = bool(value)
            return

        self.dynamic_fields[field_name] = value

        if field_name == "interaction_mode":
            self.interaction_mode = value

        if field_name == "required_tool":
            self.required_tool = value

    def toggle_dynamic_bool(self, field_name):
        if field_name not in BOOL_DYNAMIC_FIELDS:
            return

        self.dynamic_fields[field_name] = not bool(self.dynamic_fields.get(field_name, False))

    def refresh_validation(self):
        errors, warnings = validate_object_definition(self.to_definition(), self.object_id)
        self.validation_errors = errors
        self.validation_warnings = warnings


