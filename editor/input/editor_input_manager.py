import pygame

from editor.editor_ui import (
    PANEL_WIDTH,
    get_clicked_panel_action,
)

from editor.tools.paint_tool import (
    erase_at_mouse,
    erase_rect,
    paint_at_mouse,
    paint_rect,
)


class EditorInputManager:
    def __init__(self, scene_data, object_definitions, camera, save_scene_callback):
        self.scene_data = scene_data
        self.object_definitions = object_definitions
        self.camera = camera
        self.save_scene_callback = save_scene_callback

        self.mode = "objects"
        self.selected_object_type = None
        self.buttons = []

        self.is_painting = False
        self.is_erasing = False

        self.is_rect_tool_active = False
        self.rect_start_cell = None
        self.rect_end_cell = None
        self.rect_button = None

    def set_buttons(self, buttons):
        self.buttons = buttons

    def is_inside_canvas(self, screen, pos):
        panel_start_x = screen.get_width() - PANEL_WIDTH
        return pos[0] < panel_start_x

    def cancel_current_action(self):
        self.selected_object_type = None
        self.is_painting = False
        self.is_erasing = False
        self.is_rect_tool_active = False
        self.rect_start_cell = None
        self.rect_end_cell = None
        self.rect_button = None
        self.camera.stop_pan()

    def get_rect_preview_data(self):
        if not self.is_rect_tool_active:
            return None

        if self.rect_start_cell is None:
            return None

        if self.rect_end_cell is None:
            return None

        return {
            "start_cell": self.rect_start_cell,
            "end_cell": self.rect_end_cell,
            "button": self.rect_button,
        }

    def handle_panel_action(self, clicked_action):
        if not clicked_action:
            return

        action = clicked_action["action"]

        if action == "save":
            self.save_scene_callback(self.scene_data)

        if action == "zoom_in":
            self.camera.panel_zoom_in()

        if action == "zoom_out":
            self.camera.panel_zoom_out()

        if action == "mode_objects":
            self.mode = "objects"
            self.selected_object_type = None

        if action == "mode_collisions":
            self.mode = "collisions"
            self.selected_object_type = None

        if action == "select_object":
            object_type = clicked_action["object_type"]

            if object_type in self.object_definitions:
                self.mode = "objects"
                self.selected_object_type = object_type

    def start_rect_tool(self, screen, event):
        if not self.is_inside_canvas(screen, event.pos):
            return

        self.rect_start_cell = self.camera.screen_to_cell(event.pos)
        self.rect_end_cell = self.rect_start_cell
        self.rect_button = event.button
        self.is_rect_tool_active = True

    def finish_rect_tool(self):
        if self.rect_start_cell is None:
            self.reset_rect_tool()
            return

        if self.rect_end_cell is None:
            self.reset_rect_tool()
            return

        if self.rect_button == 1:
            paint_rect(
                self.scene_data,
                self.mode,
                self.selected_object_type,
                self.object_definitions,
                self.rect_start_cell,
                self.rect_end_cell,
            )

        if self.rect_button == 3:
            erase_rect(
                self.scene_data,
                self.object_definitions,
                self.rect_start_cell,
                self.rect_end_cell,
            )

        self.reset_rect_tool()

    def reset_rect_tool(self):
        self.is_rect_tool_active = False
        self.rect_start_cell = None
        self.rect_end_cell = None
        self.rect_button = None
        self.is_painting = False
        self.is_erasing = False

    def handle_mouse_button_down(self, screen, event):
        if event.button == 2:
            self.camera.start_pan(event.pos)
            return

        if event.button == 4:
            self.camera.zoom_in()
            return

        if event.button == 5:
            self.camera.zoom_out()
            return

        ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL

        if ctrl_pressed and event.button in [1, 3]:
            self.start_rect_tool(screen, event)
            return

        if event.button == 3:
            if self.is_inside_canvas(screen, event.pos):
                erase_at_mouse(
                    self.scene_data,
                    self.object_definitions,
                    self.camera,
                    event.pos,
                )
                self.is_erasing = True
            return

        clicked_action = get_clicked_panel_action(event.pos, self.buttons)

        if clicked_action:
            self.handle_panel_action(clicked_action)
            return

        if self.is_inside_canvas(screen, event.pos):
            paint_at_mouse(
                self.scene_data,
                self.mode,
                self.selected_object_type,
                self.object_definitions,
                self.camera,
                event.pos,
            )

            self.is_painting = True

    def handle_mouse_button_up(self, event):
        if event.button == 2:
            self.camera.stop_pan()
            return

        if self.is_rect_tool_active and event.button == self.rect_button:
            self.finish_rect_tool()
            return

        if event.button == 1:
            self.is_painting = False

        if event.button == 3:
            self.is_erasing = False

    def handle_mouse_motion(self, screen, event):
        if self.camera.is_panning:
            self.camera.update_pan(event.pos)
            return

        if self.is_rect_tool_active:
            if self.is_inside_canvas(screen, event.pos):
                self.rect_end_cell = self.camera.screen_to_cell(event.pos)
            return

        if self.is_painting:
            if self.is_inside_canvas(screen, event.pos):
                paint_at_mouse(
                    self.scene_data,
                    self.mode,
                    self.selected_object_type,
                    self.object_definitions,
                    self.camera,
                    event.pos,
                )

        if self.is_erasing:
            if self.is_inside_canvas(screen, event.pos):
                erase_at_mouse(
                    self.scene_data,
                    self.object_definitions,
                    self.camera,
                    event.pos,
                )

    def handle_event(self, screen, event):
        if event.type == pygame.QUIT:
            self.save_scene_callback(self.scene_data)
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.cancel_current_action()

            if event.key == pygame.K_s:
                self.save_scene_callback(self.scene_data)

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_button_down(screen, event)

        if event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_button_up(event)

        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(screen, event)

        return True