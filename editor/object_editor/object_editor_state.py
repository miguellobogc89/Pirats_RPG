from game.world.object_interaction_model import normalize_object_interaction


class ObjectEditorState:
    def __init__(self):
        self.object_id = ""
        self.name = ""
        self.sprite = ""
        self.source_sprite_path = ""
        self.footprint = [1, 1]
        self.footprint_preview_offset = [0, 0]
        self.sprite_offset = [0, 0]
        self.sprite_size = None
        self.solid = True
        self.stackable = False
        self.interaction_mode = "none"
        self.destructible = False
        self.required_tool = None
        self.interaction_points = []
        self.category = "Other"
        self.object_type = "object"
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
        self.category_dropdown_open = False
        self.interaction_mode_dropdown_open = False
        self.required_tool_dropdown_open = False

    def to_definition(self):
        data = {
            "name": self.name,
            "category": self.category.lower(),
            "sprite": self.sprite,
            "footprint": self.footprint,
            "sprite_offset": self.sprite_offset,
            "sprite_size": self.sprite_size,
            "solid": self.solid,
            "stackable": self.stackable,
            "interaction_mode": self.interaction_mode,
            "destructible": self.destructible,
            "required_tool": self.required_tool,
            "interaction_points": self.interaction_points,
        }

        if self.object_type != "object":
            data["type"] = self.object_type

        return data

    def load_from_definition(self, object_id, definition):
        self.object_id = object_id
        self.original_object_id = object_id
        self.name = definition.get("name", "")
        self.sprite = definition.get("sprite", "")
        self.source_sprite_path = self.sprite
        self.footprint = list(definition.get("footprint", [1, 1]))
        self.footprint_preview_offset = [0, 0]
        self.sprite_offset = list(definition.get("sprite_offset", [0, 0]))
        self.sprite_size = definition.get("sprite_size")
        self.solid = bool(definition.get("solid", True))
        self.stackable = bool(definition.get("stackable", False))
        normalized_interaction = normalize_object_interaction(definition, object_id)
        self.interaction_mode = normalized_interaction["interaction_mode"]
        self.destructible = normalized_interaction["destructible"]
        self.required_tool = normalized_interaction["required_tool"]
        self.interaction_points = [
            list(point)
            for point in definition.get("interaction_points", [])
            if isinstance(point, list) and len(point) >= 2
        ]
        self.category = definition.get("category", "Other")
        self.object_type = definition.get("type", "object")

    def apply_interaction_rules(self):
        if not self.destructible and self.required_tool in ("axe", "pickaxe", "sword"):
            return
