import os
import pygame
import subprocess
import sys

from editor.areas.exit_tool import (
    get_area_by_id,
    get_exit_at_cell,
    get_spawn_at_cell,
    rename_area,
    set_exit_targets,
)

from editor.editor_ui import (
    PANEL_WIDTH,
    get_clicked_panel_action,
)

from editor.scene_editor_serializer import (
    SCENES_DIR,
    create_empty_scene_data,
    list_saved_scenes,
    load_scene_for_editor,
    save_scene_as_for_game,
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

        self.active_menu = None

        self.mode = "objects"
        self.selected_object_type = None
        self.buttons = []
        self.dialog_buttons = []

        self.has_unsaved_changes = False
        self.pending_protected_action = None
        self.show_unsaved_dialog = False

        self.show_save_as_dialog = False
        self.save_as_text = ""

        self.show_open_scene_dialog = False
        self.saved_scenes = []

        self.status_message = ""

        self.is_painting = False
        self.is_erasing = False

        self.object_editor_preview_layout = None
        self.is_dragging_object_sprite = False
        self.object_sprite_drag_offset = [0, 0]

        self.is_rect_tool_active = False
        self.rect_start_cell = None
        self.rect_end_cell = None
        self.rect_button = None

        self.selected_terrain_id = "grass"
        self.side_panel_scroll_y = 0

        self.selected_area_type = None
        self.selected_area_id = None

        self.show_area_name_dialog = False
        self.area_name_text = ""
        self.relation_name_edit_scene_id = None
        self.relation_name_edit_area_type = None
        self.relation_name_edit_area_id = None

        self.show_relations_dialog = False
        self.show_object_editor = False
        self.object_editor_buttons = []
        self.object_editor_state = None
        self.object_editor_sprite = None
        self.relation_exits = []
        self.relation_targets = []
        self.selected_relation_exit_key = None
        self.selected_relation_exit_scene_id = None
        self.selected_relation_exit_id = None
        self.selected_relation_target_keys = []

    def set_buttons(self, buttons):
        self.buttons = buttons

    def set_dialog_buttons(self, buttons):
        self.dialog_buttons = buttons

    def mark_dirty(self):
        self.has_unsaved_changes = True

    def mark_saved(self):
        self.has_unsaved_changes = False

    def set_status(self, message):
        self.status_message = message

    def save_current_scene(self):
        if self.scene_data.get("id") == "new_scene":
            self.open_save_as_dialog()
            return None

        path = self.save_scene_callback(self.scene_data)
        self.mark_saved()
        self.set_status(f"Escena guardada: {path.name}")
        return path

    def save_current_scene_as(self, scene_name):
        clean_name = scene_name.strip()

        if clean_name == "":
            return None

        path = save_scene_as_for_game(self.scene_data, clean_name)
        self.mark_saved()
        self.set_status(f"Escena guardada como: {path.name}")
        return path

    def open_save_as_dialog(self):
        self.active_menu = None
        self.show_save_as_dialog = True
        self.show_open_scene_dialog = False
        self.show_unsaved_dialog = False
        self.show_area_name_dialog = False
        self.show_relations_dialog = False

        current_name = self.scene_data.get("name", "")

        if current_name == "New Scene":
            current_name = ""

        self.save_as_text = current_name

    def open_open_scene_dialog(self):
        self.active_menu = None
        self.saved_scenes = list_saved_scenes()
        self.show_open_scene_dialog = True
        self.show_save_as_dialog = False
        self.show_unsaved_dialog = False
        self.show_area_name_dialog = False
        self.show_relations_dialog = False

    def open_scenes_folder(self):
        SCENES_DIR.mkdir(parents=True, exist_ok=True)

        if sys.platform.startswith("win"):
            os.startfile(SCENES_DIR)
            return

        if sys.platform == "darwin":
            subprocess.Popen(["open", str(SCENES_DIR)])
            return

        subprocess.Popen(["xdg-open", str(SCENES_DIR)])

    def is_dialog_open(self):
        if self.show_object_editor:
            return True
        if self.show_unsaved_dialog:
            return True

        if self.show_save_as_dialog:
            return True

        if self.show_open_scene_dialog:
            return True

        if self.show_area_name_dialog:
            return True

        if self.show_relations_dialog:
            return True

        return False

    def is_inside_canvas(self, screen, pos):
        panel_start_x = screen.get_width() - PANEL_WIDTH
        return pos[0] < panel_start_x

    def is_inside_side_panel(self, screen, pos):
        panel_start_x = screen.get_width() - PANEL_WIDTH

        if pos[0] < panel_start_x:
            return False

        return True


    def scroll_side_panel(self, amount):
        self.side_panel_scroll_y += amount

        if self.side_panel_scroll_y < 0:
            self.side_panel_scroll_y = 0

        max_scroll = 1000

        if self.side_panel_scroll_y > max_scroll:
            self.side_panel_scroll_y = max_scroll

    def cancel_current_action(self):
        self.selected_object_type = None
        self.is_painting = False
        self.is_erasing = False
        self.is_rect_tool_active = False
        self.rect_start_cell = None
        self.rect_end_cell = None
        self.rect_button = None
        self.camera.stop_pan()

    def request_protected_action(self, action):
        self.active_menu = None

        if self.has_unsaved_changes:
            self.pending_protected_action = action
            self.show_unsaved_dialog = True
            return None

        return self.execute_protected_action(action)

    def execute_protected_action(self, action):
        if action == "exit":
            return "exit"

        if action == "new_scene":
            self.create_new_scene()
            return None

        if action == "open_scene":
            self.open_open_scene_dialog()
            return None

        return None

    def create_new_scene(self):
        self.scene_data.clear()
        self.scene_data.update(create_empty_scene_data())

        self.camera.x = 0
        self.camera.y = 0
        self.selected_object_type = None
        self.selected_area_type = None
        self.selected_area_id = None
        self.mode = "objects"
        self.mark_dirty()
        self.set_status("Nueva escena creada")

    def load_scene(self, scene_id):
        loaded_scene = load_scene_for_editor(scene_id)

        self.scene_data.clear()
        self.scene_data.update(loaded_scene)

        self.camera.x = 0
        self.camera.y = 0
        self.selected_object_type = None
        self.selected_area_type = None
        self.selected_area_id = None
        self.mode = "objects"
        self.mark_saved()
        self.set_status(f"Escena abierta: {loaded_scene['name']}")

    def handle_unsaved_dialog_action(self, action):
        if action == "dialog_cancel":
            self.show_unsaved_dialog = False
            self.pending_protected_action = None
            return None

        if action == "dialog_save":
            save_result = self.save_current_scene()

            if save_result is None and self.show_save_as_dialog:
                self.show_unsaved_dialog = False
                return None

            action_to_execute = self.pending_protected_action
            self.show_unsaved_dialog = False
            self.pending_protected_action = None

            return self.execute_protected_action(action_to_execute)

        if action == "dialog_discard":
            action_to_execute = self.pending_protected_action
            self.show_unsaved_dialog = False
            self.pending_protected_action = None
            self.mark_saved()

            return self.execute_protected_action(action_to_execute)

        return None

    def handle_save_as_dialog_action(self, action):
        if action == "save_as_cancel":
            self.show_save_as_dialog = False
            return None

        if action == "save_as_confirm":
            path = self.save_current_scene_as(self.save_as_text)

            if path is not None:
                self.show_save_as_dialog = False

                if self.pending_protected_action is not None:
                    action_to_execute = self.pending_protected_action
                    self.pending_protected_action = None
                    return self.execute_protected_action(action_to_execute)

            return None

        return None

    def handle_open_scene_dialog_action(self, clicked_action):
        action = clicked_action["action"]

        if action == "open_scene_cancel":
            self.show_open_scene_dialog = False
            return None

        if action == "open_scene_select":
            self.show_open_scene_dialog = False
            self.load_scene(clicked_action["scene_id"])
            return None

        return None

    def handle_dialog_click(self, event):
        clicked_action = get_clicked_panel_action(event.pos, self.dialog_buttons)

        if not clicked_action:
            return None

        if self.show_unsaved_dialog:
            return self.handle_unsaved_dialog_action(clicked_action["action"])

        if self.show_save_as_dialog:
            return self.handle_save_as_dialog_action(clicked_action["action"])

        if self.show_open_scene_dialog:
            return self.handle_open_scene_dialog_action(clicked_action)

        if self.show_area_name_dialog:
            return self.handle_area_name_dialog_action(clicked_action["action"])

        if self.show_relations_dialog:
            return self.handle_relations_dialog_action(clicked_action)

        return None

    def handle_save_as_text_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.show_save_as_dialog = False
            return

        if event.key == pygame.K_RETURN:
            self.handle_save_as_dialog_action("save_as_confirm")
            return

        if event.key == pygame.K_BACKSPACE:
            self.save_as_text = self.save_as_text[:-1]
            return

        if event.unicode:
            self.save_as_text += event.unicode

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
            return None

        action = clicked_action["action"]

        if action == "menu_file":
            if self.active_menu == "file":
                self.active_menu = None
            else:
                self.active_menu = "file"
            return None

        if action == "menu_edit":
            self.active_menu = None
            return None

        if action == "menu_objects":
            if self.active_menu == "objects":
                self.active_menu = None
            else:
                self.active_menu = "objects"
            return None

        if action == "menu_settings":
            self.active_menu = None
            return None

        if action == "file_new":
            return self.request_protected_action("new_scene")

        if action == "file_open":
            return self.request_protected_action("open_scene")

        if action == "file_save":
            self.save_current_scene()
            self.active_menu = None
            return None

        if action == "file_save_as":
            self.open_save_as_dialog()
            return None

        if action == "file_open_folder":
            self.active_menu = None
            self.open_scenes_folder()
            return None

        if action == "file_exit":
            return self.request_protected_action("exit")

        if action == "object_new":
            from editor.object_editor.object_editor_state import ObjectEditorState

            self.active_menu = None
            self.show_object_editor = True
            self.object_editor_state = ObjectEditorState()
            self.object_editor_sprite = None

            return None
        if action == "object_cancel":
            self.show_object_editor = False
            return None

        if action == "object_confirm_save":
            self.set_status("Guardar objeto pendiente")
            return None

        if action == "object_load_png":
            from tkinter import Tk, filedialog

            root = Tk()
            root.withdraw()

            source_path = filedialog.askopenfilename(
                title="Seleccionar PNG",
                filetypes=[("PNG files", "*.png")],
            )

            root.destroy()

            if source_path == "":
                self.set_status("Carga de PNG cancelada")
                return None

            try:
                self.object_editor_sprite = pygame.image.load(source_path).convert_alpha()
                self.object_editor_state.sprite = source_path
                self.set_status(f"PNG cargado: {source_path}")
            except pygame.error:
                self.set_status("No se pudo cargar el PNG")

            return None

        if action == "object_open":
            self.active_menu = None
            self.set_status("Abrir objeto")
            return None

        if action == "object_save":
            self.active_menu = None
            self.set_status("Guardar objeto")
            return None

        if action == "object_save_as":
            self.active_menu = None
            self.set_status("Guardar objeto como")
            return None

        if action == "zoom_in":
            self.camera.panel_zoom_in()
            return None

        if action == "zoom_out":
            self.camera.panel_zoom_out()
            return None

        if action == "mode_objects":
            self.mode = "objects"
            self.selected_object_type = None
            return None

        if action == "mode_collisions":
            self.mode = "collisions"
            self.selected_object_type = None
            return None

        if action == "mode_spawns":
            self.mode = "spawns"
            self.selected_object_type = None
            return None

        if action == "mode_exits":
            self.mode = "exits"
            self.selected_object_type = None
            return None

        if action == "select_object":
            object_type = clicked_action["object_type"]

            if object_type in self.object_definitions:
                self.mode = "objects"
                self.selected_object_type = object_type

            return None

        if action == "edit_area_name":
            self.open_area_name_dialog()
            return None

        if action == "open_relations_dialog":
            self.open_relations_dialog()
            return None

        if action == "mode_terrain":
            self.mode = "terrain"
            self.selected_object_type = None
            return None

        if action == "select_terrain":
            self.mode = "terrain"
            self.selected_object_type = None
            self.selected_terrain_id = clicked_action["terrain_id"]
            return None



        return None

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

        changed = False

        if self.rect_button == 1:
            changed = paint_rect(
                self.scene_data,
                self.mode,
                self.selected_object_type,
                self.selected_terrain_id,
                self.object_definitions,
                self.rect_start_cell,
                self.rect_end_cell,
            )

        if self.rect_button == 3:
            changed = erase_rect(
                self.scene_data,
                self.mode,
                self.object_definitions,
                self.rect_start_cell,
                self.rect_end_cell,
            )

        if changed:
            self.mark_dirty()
            self.select_area_at_cell(self.rect_start_cell)

        self.reset_rect_tool()

    def reset_rect_tool(self):
        self.is_rect_tool_active = False
        self.rect_start_cell = None
        self.rect_end_cell = None
        self.rect_button = None
        self.is_painting = False
        self.is_erasing = False

    def start_object_sprite_drag(self, event):
        if self.object_editor_preview_layout is None:
            return False

        sprite_rect = self.object_editor_preview_layout.get("sprite_rect")

        if sprite_rect is None:
            return False

        if not sprite_rect.collidepoint(event.pos):
            return False

        self.is_dragging_object_sprite = True

        self.object_sprite_drag_offset = [
            event.pos[0] - sprite_rect.x,
            event.pos[1] - sprite_rect.y,
        ]

        return True


    def update_object_sprite_drag(self, event):
        if not self.is_dragging_object_sprite:
            return

        if self.object_editor_preview_layout is None:
            return

        anchor_pos = self.object_editor_preview_layout.get("anchor_pos")

        if anchor_pos is None:
            return

        new_sprite_x = event.pos[0] - self.object_sprite_drag_offset[0]
        new_sprite_y = event.pos[1] - self.object_sprite_drag_offset[1]

        self.object_editor_state.sprite_offset = [
            new_sprite_x - anchor_pos[0],
            new_sprite_y - anchor_pos[1],
        ]


    def stop_object_sprite_drag(self):
        self.is_dragging_object_sprite = False


    def handle_mouse_button_down(self, screen, event):

        if self.show_object_editor:
            if event.button == 1:
                if self.start_object_sprite_drag(event):
                    return None

            return self.handle_dialog_click(event)

        if self.is_dialog_open():
            return self.handle_dialog_click(event)

        if event.button == 2:
            self.camera.start_pan(event.pos)
            return None

        if event.button == 4:
            if self.is_inside_side_panel(screen, event.pos):
                self.scroll_side_panel(-40)
                return None

            self.camera.zoom_in()
            return None

        if event.button == 5:
            if self.is_inside_side_panel(screen, event.pos):
                self.scroll_side_panel(40)
                return None

            self.camera.zoom_out()
            return None

        ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL

        if ctrl_pressed and event.button in [1, 3]:
            self.start_rect_tool(screen, event)
            return None

        if event.button == 3:
            if self.is_inside_canvas(screen, event.pos):
                changed = erase_at_mouse(
                    self.scene_data,
                    self.mode,
                    self.object_definitions,
                    self.camera,
                    event.pos,
                )

                self.is_erasing = True

                if changed:
                    self.mark_dirty()

                self.selected_area_type = None
                self.selected_area_id = None

            return None

        clicked_action = get_clicked_panel_action(event.pos, self.buttons)

        if clicked_action:
            return self.handle_panel_action(clicked_action)

        if self.is_inside_canvas(screen, event.pos):
            changed = paint_at_mouse(
                self.scene_data,
                self.mode,
                self.selected_object_type,
                self.selected_terrain_id,
                self.object_definitions,
                self.camera,
                event.pos,
            )
            self.is_painting = True

            if changed:
                self.mark_dirty()
                self.select_area_at_cell(self.camera.screen_to_cell(event.pos))

        return None

    def handle_mouse_button_up(self, event):
        if self.show_object_editor:
            self.stop_object_sprite_drag()
            return

        if self.is_dialog_open():
            return

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
        if self.show_object_editor:
            self.update_object_sprite_drag(event)
            return
        if self.is_dialog_open():
            return

        if self.camera.is_panning:
            self.camera.update_pan(event.pos)
            return

        if self.is_rect_tool_active:
            if self.is_inside_canvas(screen, event.pos):
                self.rect_end_cell = self.camera.screen_to_cell(event.pos)
            return

        if self.is_painting:
            if self.is_inside_canvas(screen, event.pos):
                changed = paint_at_mouse(
                    self.scene_data,
                    self.mode,
                    self.selected_object_type,
                    self.selected_terrain_id,
                    self.object_definitions,
                    self.camera,
                    event.pos,
                )

                if changed:
                    self.mark_dirty()
                    self.select_area_at_cell(self.camera.screen_to_cell(event.pos))

        if self.is_erasing:
            if self.is_inside_canvas(screen, event.pos):
                changed = erase_at_mouse(
                    self.scene_data,
                    self.mode,
                    self.object_definitions,
                    self.camera,
                    event.pos,
                )

                if changed:
                    self.mark_dirty()

    def handle_event(self, screen, event):
        if event.type == pygame.QUIT:
            result = self.request_protected_action("exit")

            if result == "exit":
                return False

            return True

        if event.type == pygame.KEYDOWN:
            if self.show_area_name_dialog:
                self.handle_area_name_text_input(event)
                return True

            if self.show_save_as_dialog:
                self.handle_save_as_text_input(event)
                return True

            if self.show_unsaved_dialog or self.show_open_scene_dialog or self.show_relations_dialog:
                if event.key == pygame.K_ESCAPE:
                    self.show_unsaved_dialog = False
                    self.show_open_scene_dialog = False
                    self.show_relations_dialog = False
                    self.pending_protected_action = None
                return True

            if event.key == pygame.K_ESCAPE:
                self.cancel_current_action()

            if event.key == pygame.K_s:
                self.save_current_scene()

        if event.type == pygame.MOUSEBUTTONDOWN:
            result = self.handle_mouse_button_down(screen, event)

            if result == "exit":
                return False

        if event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_button_up(event)

        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(screen, event)

        return True

    def get_selected_area(self):
        if self.selected_area_type is None:
            return None

        if self.selected_area_id is None:
            return None

        return get_area_by_id(
            self.scene_data,
            self.selected_area_type,
            self.selected_area_id,
        )

    def select_area_at_cell(self, cell):
        if self.mode == "spawns":
            spawn_data = get_spawn_at_cell(self.scene_data, cell)

            if spawn_data is not None:
                self.selected_area_type = "spawns"
                self.selected_area_id = spawn_data["id"]

            return

        if self.mode == "exits":
            exit_data = get_exit_at_cell(self.scene_data, cell)

            if exit_data is not None:
                self.selected_area_type = "exits"
                self.selected_area_id = exit_data["id"]

            return

    def open_area_name_dialog(self):
        selected_area = self.get_selected_area()

        if selected_area is None:
            return

        self.clear_relation_name_edit()
        self.area_name_text = selected_area.get("name", "")
        self.show_area_name_dialog = True

    def handle_area_name_dialog_action(self, action):
        if action == "area_name_cancel":
            self.show_area_name_dialog = False
            self.clear_relation_name_edit()
            return None

        if action == "area_name_confirm":
            if self.relation_name_edit_scene_id is not None:
                return self.confirm_relation_name_edit()

            renamed = rename_area(
                self.scene_data,
                self.selected_area_type,
                self.selected_area_id,
                self.area_name_text,
            )

            if renamed:
                self.mark_dirty()
                self.set_status("Nombre de área actualizado")

            self.show_area_name_dialog = False
            return None

        return None

    def clear_relation_name_edit(self):
        self.relation_name_edit_scene_id = None
        self.relation_name_edit_area_type = None
        self.relation_name_edit_area_id = None

    def open_relation_name_dialog(self, scene_id, area_type, area_id):
        scene_data = self.get_scene_for_relation_edit(scene_id)
        area_data = get_area_by_id(scene_data, area_type, area_id)

        if area_data is None:
            return

        self.relation_name_edit_scene_id = scene_id
        self.relation_name_edit_area_type = area_type
        self.relation_name_edit_area_id = area_id
        self.area_name_text = area_data.get("name", area_data.get("id", ""))
        self.show_area_name_dialog = True

    def confirm_relation_name_edit(self):
        scene_data = self.get_scene_for_relation_edit(
            self.relation_name_edit_scene_id
        )
        renamed = rename_area(
            scene_data,
            self.relation_name_edit_area_type,
            self.relation_name_edit_area_id,
            self.area_name_text,
        )

        if renamed:
            self.save_scene_callback(scene_data)

            if scene_data is self.scene_data:
                self.mark_saved()

            self.relation_exits = self.build_relation_exits()
            self.relation_targets = self.build_relation_targets()
            self.set_status("Nombre de relacion actualizado")

        self.show_area_name_dialog = False
        self.clear_relation_name_edit()
        return None

    def handle_area_name_text_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.show_area_name_dialog = False
            return

        if event.key == pygame.K_RETURN:
            self.handle_area_name_dialog_action("area_name_confirm")
            return

        if event.key == pygame.K_BACKSPACE:
            self.area_name_text = self.area_name_text[:-1]
            return

        if event.unicode:
            self.area_name_text += event.unicode

    def build_relation_exits(self):
        exits = []

        saved_scenes = list_saved_scenes()

        for scene_info in saved_scenes:
            loaded_scene = self.get_scene_for_relation_edit(scene_info["id"])

            for exit_data in loaded_scene.get("exits", []):
                exit_key = f"{loaded_scene['id']}::{exit_data['id']}"

                exits.append({
                    "exit_key": exit_key,
                    "scene_id": loaded_scene["id"],
                    "scene_name": loaded_scene["name"],
                    "exit_id": exit_data["id"],
                    "exit_name": exit_data.get("name", exit_data["id"]),
                    "target_links": exit_data.get("target_links", []),
                })

        return exits

    def build_relation_targets(self):
        targets = []

        saved_scenes = list_saved_scenes()

        for scene_info in saved_scenes:
            loaded_scene = self.get_scene_for_relation_edit(scene_info["id"])

            for spawn_data in loaded_scene.get("spawns", []):
                target_key = f"{loaded_scene['id']}::{spawn_data['id']}"

                targets.append({
                    "target_key": target_key,
                    "scene_id": loaded_scene["id"],
                    "scene_name": loaded_scene["name"],
                    "spawn_id": spawn_data["id"],
                    "spawn_name": spawn_data.get("name", spawn_data["id"]),
                })

        return targets

    def get_scene_for_relation_edit(self, scene_id):
        if self.scene_data.get("id") == scene_id:
            return self.scene_data

        return load_scene_for_editor(scene_id)

    def open_relations_dialog(self):
        self.relation_exits = self.build_relation_exits()
        self.relation_targets = self.build_relation_targets()

        self.selected_relation_exit_key = None
        self.selected_relation_exit_scene_id = None
        self.selected_relation_exit_id = None
        self.selected_relation_target_keys = []

        if len(self.relation_exits) > 0:
            first_exit = self.relation_exits[0]

            self.selected_relation_exit_key = first_exit["exit_key"]
            self.selected_relation_exit_scene_id = first_exit["scene_id"]
            self.selected_relation_exit_id = first_exit["exit_id"]

            for link in first_exit.get("target_links", []):
                target_key = (
                    f"{link.get('target_scene_id', '')}::"
                    f"{link.get('target_spawn_id', '')}"
                )

                self.selected_relation_target_keys.append(target_key)

        self.show_relations_dialog = True

    def get_selected_relation_exit_data(self):
        for exit_data in self.relation_exits:
            if exit_data["exit_key"] == self.selected_relation_exit_key:
                return exit_data

        return None

    def handle_relations_dialog_action(self, clicked_action):
        action = clicked_action["action"]

        if action == "relation_cancel":
            self.show_relations_dialog = False
            return None

        if action == "relation_select_exit":
            self.selected_relation_exit_key = clicked_action["exit_key"]
            self.selected_relation_exit_scene_id = clicked_action["scene_id"]
            self.selected_relation_exit_id = clicked_action["exit_id"]
            self.selected_relation_target_keys = []

            selected_exit = self.get_selected_relation_exit_data()

            if selected_exit is not None:
                for link in selected_exit.get("target_links", []):
                    target_key = (
                        f"{link.get('target_scene_id', '')}::"
                        f"{link.get('target_spawn_id', '')}"
                    )

                    self.selected_relation_target_keys.append(target_key)

            return None

        if action == "relation_toggle_target":
            target_key = clicked_action["target_key"]

            if target_key in self.selected_relation_target_keys:
                self.selected_relation_target_keys.remove(target_key)
            else:
                self.selected_relation_target_keys.append(target_key)

            return None

        if action == "relation_rename_exit":
            self.open_relation_name_dialog(
                clicked_action["scene_id"],
                "exits",
                clicked_action["area_id"],
            )
            return None

        if action == "relation_rename_spawn":
            self.open_relation_name_dialog(
                clicked_action["scene_id"],
                "spawns",
                clicked_action["area_id"],
            )
            return None

        if action == "relation_confirm":
            if self.selected_relation_exit_scene_id is None:
                return None

            if self.selected_relation_exit_id is None:
                return None

            target_links = []

            for target_key in self.selected_relation_target_keys:
                parts = target_key.split("::")

                if len(parts) != 2:
                    continue

                target_links.append({
                    "target_scene_id": parts[0],
                    "target_spawn_id": parts[1],
                })

            loaded_scene = self.get_scene_for_relation_edit(
                self.selected_relation_exit_scene_id
            )

            linked = set_exit_targets(
                loaded_scene,
                self.selected_relation_exit_id,
                target_links,
            )

            if linked:
                self.save_scene_callback(loaded_scene)

                if loaded_scene is self.scene_data:
                    self.mark_saved()

                self.set_status("Relaciones guardadas")
                self.relation_exits = self.build_relation_exits()
                self.show_relations_dialog = False

            return None

        return None
