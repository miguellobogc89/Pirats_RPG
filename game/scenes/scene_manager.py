import pygame

from game.scenes.farm_scene import FarmScene
from game.scenes.scene_loader import load_scene_data, scene_exists


DEFAULT_SCENE_ID = "farm"


def ensure_scene_state(state):
    if "current_scene" not in state:
        state["current_scene"] = DEFAULT_SCENE_ID


def get_current_scene_id(state):
    ensure_scene_state(state)
    return state["current_scene"]


def get_current_scene_data(state):
    scene_id = get_current_scene_id(state)
    return load_scene_data(scene_id)


def change_scene(state, scene_id, payload=None):
    if not scene_exists(scene_id):
        return False

    apply_scene_state(state, scene_id, payload)
    return True


def apply_scene_state(state, scene_id, payload=None):
    scene_data = load_scene_data(scene_id)
    spawn = resolve_scene_spawn(scene_data, payload)

    state["current_scene"] = scene_id
    state["player"]["x"] = spawn["x"]
    state["player"]["y"] = spawn["y"]

    if payload:
        state["last_scene_payload"] = payload


def resolve_scene_spawn(scene_data, payload=None):
    if payload is None:
        return scene_data["player_spawn"]

    target_spawn_id = payload.get("target_spawn_id")

    if target_spawn_id is None:
        return scene_data["player_spawn"]

    for spawn_data in scene_data.get("spawns", []):
        if spawn_data.get("id") != target_spawn_id:
            continue

        spawn_cell = spawn_data.get("spawn_cell")

        if not isinstance(spawn_cell, list) or len(spawn_cell) < 2:
            return scene_data["player_spawn"]

        tile_size = scene_data.get("tile_size", 32)

        return {
            "x": spawn_cell[0] * tile_size + tile_size // 2,
            "y": spawn_cell[1] * tile_size + tile_size // 2,
        }

    return scene_data["player_spawn"]


class SceneManager:
    def __init__(self, app):
        self.app = app
        self.scene_stack = []

    @property
    def current_scene(self):
        if not self.scene_stack:
            return None

        return self.scene_stack[-1]

    def load_from_state(self):
        scene_id = get_current_scene_id(self.app.state)

        if not scene_exists(scene_id):
            scene_id = DEFAULT_SCENE_ID
            self.app.state["current_scene"] = scene_id

        self.notify_scene_data_changed(scene_id)
        scene = self.create_scene(scene_id)
        self.scene_stack = [scene]
        scene.enter()
        return scene

    def create_scene(
        self,
        scene_id,
        payload=None,
        is_overlay=False,
        blocks_lower_input=True,
        blocks_lower_update=True,
    ):
        if not scene_exists(scene_id):
            return None

        scene_class = self.get_scene_class(scene_id)
        return scene_class(
            self.app,
            scene_id,
            payload=payload,
            is_overlay=is_overlay,
            blocks_lower_input=blocks_lower_input,
            blocks_lower_update=blocks_lower_update,
        )

    def get_scene_class(self, scene_id):
        return FarmScene

    def change_scene(self, scene_id, payload=None):
        if not scene_exists(scene_id):
            return False

        if self.current_scene is not None:
            self.current_scene.exit()

        apply_scene_state(self.app.state, scene_id, payload)
        self.notify_scene_data_changed(scene_id)
        scene = self.create_scene(scene_id, payload=payload)
        self.scene_stack = [scene]
        scene.enter()
        return True

    def push_scene(
        self,
        scene_id,
        payload=None,
        is_overlay=True,
        blocks_lower_input=True,
        blocks_lower_update=True,
    ):
        scene = self.create_scene(
            scene_id,
            payload=payload,
            is_overlay=is_overlay,
            blocks_lower_input=blocks_lower_input,
            blocks_lower_update=blocks_lower_update,
        )

        if scene is None:
            return False

        if self.current_scene is not None:
            self.current_scene.pause()

        if not is_overlay:
            apply_scene_state(self.app.state, scene_id, payload)
            self.notify_scene_data_changed(scene_id)

        self.scene_stack.append(scene)
        scene.enter()
        return True

    def pop_scene(self, payload=None):
        if len(self.scene_stack) <= 1:
            return False

        scene = self.scene_stack.pop()
        scene.exit()

        current_scene = self.current_scene

        if current_scene is not None:
            if not current_scene.is_overlay:
                self.app.state["current_scene"] = current_scene.scene_id

            current_scene.resume(payload=payload)

        return True

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event):
        for scene in reversed(self.scene_stack):
            handled = scene.handle_event(event)

            if handled or scene.blocks_lower_input:
                return handled

        return False

    def update(self, dt):
        start_index = 0

        for index in range(len(self.scene_stack) - 1, -1, -1):
            if self.scene_stack[index].blocks_lower_update:
                start_index = index
                break

        for scene in self.scene_stack[start_index:]:
            scene.update(dt)

    def draw(self):
        for scene in self.scene_stack:
            scene.draw()

    def notify_scene_data_changed(self, scene_id):
        if hasattr(self.app, "load_scene_runtime"):
            self.app.load_scene_runtime(scene_id)
