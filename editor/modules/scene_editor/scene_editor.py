from game.world.grid_manager import TILE_SIZE

from editor.editor_assets import (
    load_editor_sprites,
    load_object_definitions,
)
from editor.editor_camera import EditorCamera
from editor.input.editor_input_manager import EditorInputManager
from editor.modules.scene_editor.scene_editor_renderer import draw_scene_editor
from editor.scene_editor_serializer import (
    DEFAULT_SCENE_ID,
    load_scene_for_editor,
    save_scene_for_game,
)


class SceneEditorModule:
    def __init__(self):
        self.scene_data = load_scene_for_editor(DEFAULT_SCENE_ID)
        self.object_definitions = load_object_definitions()
        self.sprites = load_editor_sprites(self.object_definitions, TILE_SIZE)
        self.camera = EditorCamera()
        self.input_manager = EditorInputManager(
            self.scene_data,
            self.object_definitions,
            self.camera,
            save_scene_for_game,
        )

    def handle_event(self, screen, event):
        return self.input_manager.handle_event(screen, event)

    def refresh_object_definitions_if_needed(self):
        if not self.input_manager.object_definitions_changed:
            return

        self.object_definitions.clear()
        self.object_definitions.update(load_object_definitions())
        self.sprites.clear()
        self.sprites.update(load_editor_sprites(self.object_definitions, TILE_SIZE))
        self.input_manager.object_definitions_changed = False

    def draw(self, screen):
        self.refresh_object_definitions_if_needed()
        draw_scene_editor(
            screen,
            self.scene_data,
            self.object_definitions,
            self.sprites,
            self.camera,
            self.input_manager,
        )

