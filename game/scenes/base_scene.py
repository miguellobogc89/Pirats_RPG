class BaseScene:
    def __init__(
        self,
        app,
        scene_id,
        payload=None,
        is_overlay=False,
        blocks_lower_input=True,
        blocks_lower_update=True,
    ):
        self.app = app
        self.scene_id = scene_id
        self.payload = payload or {}
        self.is_overlay = is_overlay
        self.blocks_lower_input = blocks_lower_input
        self.blocks_lower_update = blocks_lower_update

    def enter(self):
        pass

    def exit(self):
        pass

    def pause(self):
        pass

    def resume(self, payload=None):
        pass

    def handle_event(self, event):
        return False

    def update(self, dt):
        pass

    def draw(self):
        pass
