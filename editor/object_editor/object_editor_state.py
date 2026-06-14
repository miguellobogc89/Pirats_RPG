class ObjectEditorState:
    def __init__(self):
        self.object_id = ""
        self.name = ""
        self.sprite = ""
        self.footprint = [1, 1]
        self.sprite_offset = [0, 0]
        self.solid = True
        self.object_type = "object"
        self.status_message = ""

    def to_definition(self):
        data = {
            "sprite": self.sprite,
            "footprint": self.footprint,
            "sprite_offset": self.sprite_offset,
            "solid": self.solid,
        }

        if self.name != "":
            data["name"] = self.name

        if self.object_type != "object":
            data["type"] = self.object_type

        return data

    def load_from_definition(self, object_id, definition):
        self.object_id = object_id
        self.name = definition.get("name", "")
        self.sprite = definition.get("sprite", "")
        self.footprint = list(definition.get("footprint", [1, 1]))
        self.sprite_offset = list(definition.get("sprite_offset", [0, 0]))
        self.solid = bool(definition.get("solid", True))
        self.object_type = definition.get("type", "object")