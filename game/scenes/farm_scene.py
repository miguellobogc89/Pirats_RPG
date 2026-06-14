from game.scenes.base_scene import BaseScene


class FarmScene(BaseScene):
    def handle_event(self, event):
        from game.input.input_manager import handle_event

        return handle_event(self.app, event)

    def update(self, dt):
        self.app.update_farm_scene(dt)

    def draw(self):
        self.app.draw_farm_scene()
