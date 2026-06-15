import os
import pygame
import subprocess
import sys
from pathlib import Path

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
from editor.scene.scene_operations import (
    add_object_property,
    get_object_at_cell,
    get_object_by_id,
    remove_object_property,
    rename_object_property,
    set_object_property_value,
)
from editor.object_editor.object_definition_writer import (
    delete_object_definition,
    save_object_definition,
)
from editor.widgets.text_edit_state import (
    TextEditState,
    copy_to_clipboard,
    paste_from_clipboard,
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
        self.show_open_object_dialog = False
        self.saved_scenes = []

        self.status_message = ""

        self.is_painting = False
        self.is_erasing = False

        self.object_editor_preview_layout = None
        self.object_editor_drag_mode = None
        self.object_editor_drag_handle = None
        self.is_dragging_object_sprite = False
        self.object_sprite_drag_offset = [0, 0]
        self.object_editor_drag_start_pos = [0, 0]
        self.object_editor_drag_start_size = [0, 0]
        self.object_editor_drag_start_offset = [0, 0]
        self.object_editor_drag_start_footprint = [1, 1]
        self.object_editor_drag_start_footprint_offset = [0, 0]
        self.is_panning_object_preview = False
        self.object_preview_pan_start_pos = [0, 0]
        self.object_preview_pan_start = [0, 0]

        self.is_rect_tool_active = False
        self.rect_start_cell = None
        self.rect_end_cell = None
        self.rect_button = None

        self.selected_terrain_id = "grass"
        self.side_panel_scroll_y = 0
        self.side_panel_max_scroll = 0
        self.side_panel_sections = {
            "objects": True,
            "object_instance": True,
            "terrain": True,
            "collisions": True,
            "navigation": True,
            "active_area": True,
        }
        self.selected_scene_object_id = None
        self.property_edit = None

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
        self.object_definitions_changed = False
        self.show_object_delete_confirm = False
        self.object_editor_inspector_scroll_y = 0
        self.text_edit_state = TextEditState()
        self.last_mouse_clicks = 1
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
        self.show_open_object_dialog = False
        self.show_unsaved_dialog = False
        self.show_area_name_dialog = False
        self.show_relations_dialog = False

        current_name = self.scene_data.get("name", "")

        if current_name == "New Scene":
            current_name = ""

        self.save_as_text = current_name
        self.text_edit_state.set_text(self.save_as_text)

    def open_open_scene_dialog(self):
        self.active_menu = None
        self.saved_scenes = list_saved_scenes()
        self.show_open_scene_dialog = True
        self.show_open_object_dialog = False
        self.show_save_as_dialog = False
        self.show_unsaved_dialog = False
        self.show_area_name_dialog = False
        self.show_relations_dialog = False

    def open_open_object_dialog(self):
        self.active_menu = None
        self.show_open_object_dialog = True
        self.show_open_scene_dialog = False
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
        if self.show_object_delete_confirm:
            return True
        if self.show_unsaved_dialog:
            return True

        if self.show_save_as_dialog:
            return True

        if self.show_open_scene_dialog:
            return True

        if self.show_open_object_dialog:
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

        if self.side_panel_scroll_y > self.side_panel_max_scroll:
            self.side_panel_scroll_y = self.side_panel_max_scroll

    def cancel_current_action(self):
        self.selected_object_type = None
        self.selected_scene_object_id = None
        self.property_edit = None
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
        self.selected_scene_object_id = None
        self.property_edit = None
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
        self.selected_scene_object_id = None
        self.property_edit = None
        self.selected_area_type = None
        self.selected_area_id = None
        self.mode = "objects"
        self.mark_saved()
        self.set_status(f"Escena abierta: {loaded_scene['name']}")

    def open_object_editor(self, object_id=None):
        from editor.object_editor.object_editor_state import ObjectEditorState

        self.active_menu = None
        self.show_object_editor = True
        self.show_object_delete_confirm = False
        self.object_editor_state = ObjectEditorState()
        self.object_editor_sprite = None
        self.object_editor_inspector_scroll_y = 0

        if object_id is None:
            self.text_edit_state.set_text("")
            return

        definition = self.object_definitions.get(object_id)

        if definition is None:
            self.set_status("No se pudo abrir el objeto")
            return

        self.object_editor_state.load_from_definition(object_id, definition)
        self.text_edit_state.set_text(self.object_editor_state.name)

        if self.object_editor_state.sprite:
            sprite, error_message = self.load_object_editor_png(
                self.object_editor_state.sprite
            )

            if sprite is None:
                self.set_status(error_message)
            else:
                self.object_editor_sprite = sprite

    def confirm_object_delete(self):
        success, message = delete_object_definition(self.selected_object_type)
        self.show_object_delete_confirm = False
        self.set_status(message)

        if not success:
            return

        self.object_definitions.pop(self.selected_object_type, None)
        self.selected_object_type = None
        self.object_definitions_changed = True

    def scroll_object_editor_inspector(self, button):
        if self.object_editor_preview_layout is None:
            return

        inspector_rect = self.object_editor_preview_layout.get("inspector_rect")

        if inspector_rect is None:
            return

        if not inspector_rect.collidepoint(pygame.mouse.get_pos()):
            return

        if button == 4:
            self.object_editor_state.inspector_scroll_y = max(
                0,
                self.object_editor_state.inspector_scroll_y - 60,
            )
        elif button == 5:
            self.object_editor_state.inspector_scroll_y = min(
                self.object_editor_state.inspector_max_scroll,
                self.object_editor_state.inspector_scroll_y + 60,
            )

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

        if action is None:
            return None

        if action == "open_scene_cancel":
            self.show_open_scene_dialog = False
            return None

        if action == "open_scene_select":
            self.show_open_scene_dialog = False
            self.load_scene(clicked_action["scene_id"])
            return None

        return None

    def handle_open_object_dialog_action(self, clicked_action):
        action = clicked_action["action"]

        if action == "open_object_cancel":
            self.show_open_object_dialog = False
            return None

        if action == "open_object_select":
            self.show_open_object_dialog = False
            self.selected_object_type = clicked_action["object_id"]
            self.open_object_editor(clicked_action["object_id"])
            return None

        if action == "open_object_delete":
            self.show_open_object_dialog = False
            self.selected_object_type = clicked_action["object_id"]
            self.show_object_delete_confirm = True
            return None

        return None

    def handle_dialog_click(self, event):
        clicked_action = get_clicked_panel_action(event.pos, self.dialog_buttons)

        if not clicked_action:
            return None

        if self.show_object_editor:
            return self.handle_panel_action(clicked_action)

        if self.show_object_delete_confirm:
            return self.handle_panel_action(clicked_action)

        if self.show_unsaved_dialog:
            return self.handle_unsaved_dialog_action(clicked_action["action"])

        if self.show_save_as_dialog:
            return self.handle_save_as_dialog_action(clicked_action["action"])

        if self.show_open_scene_dialog:
            return self.handle_open_scene_dialog_action(clicked_action)

        if self.show_open_object_dialog:
            return self.handle_open_object_dialog_action(clicked_action)

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

        self.handle_text_edit_input(event, max_length=48)
        self.save_as_text = self.text_edit_state.text

    def focus_instance_property(self, property_key, kind):
        selected_object = self.get_selected_scene_object()

        if selected_object is None:
            return

        properties = selected_object.get("properties", {})

        if property_key not in properties:
            return

        if kind == "key":
            text_value = property_key
        else:
            text_value = properties[property_key]

        self.property_edit = {
            "object_id": selected_object.get("id"),
            "property_key": property_key,
            "kind": kind,
        }
        self.text_edit_state.set_text(str(text_value))

    def get_property_edit_view(self):
        if self.property_edit is None:
            return None

        view = dict(self.property_edit)
        view["text"] = self.text_edit_state.text
        return view

    def handle_instance_property_text_input(self, event):
        if self.property_edit is None:
            return False

        if event.key == pygame.K_ESCAPE:
            self.property_edit = None
            return True

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.commit_instance_property_edit()
            self.property_edit = None
            return True

        changed = self.handle_text_edit_input(event, max_length=64)

        if not changed:
            return True

        self.commit_instance_property_edit(live=True)
        return True

    def commit_instance_property_edit(self, live=False):
        if self.property_edit is None:
            return False

        selected_object = self.get_selected_scene_object()

        if selected_object is None:
            self.property_edit = None
            return False

        kind = self.property_edit.get("kind")
        property_key = self.property_edit.get("property_key")
        text_value = self.text_edit_state.text

        if kind == "value":
            changed = set_object_property_value(
                selected_object,
                property_key,
                text_value,
            )

            if changed:
                self.mark_dirty()

            return changed

        if kind == "key":
            if text_value.strip() == "":
                if not live:
                    self.set_status("La clave no puede estar vacia")
                return False

            changed = rename_object_property(
                selected_object,
                property_key,
                text_value,
            )

            if changed:
                self.property_edit["property_key"] = text_value.strip()
                self.mark_dirty()
                return True

            if not live:
                self.set_status("Ya existe una propiedad con esa clave")

        return False

    def handle_object_editor_text_input(self, event):
        if event.key == pygame.K_ESCAPE:
            if self.object_editor_state.selected_field is not None:
                self.object_editor_state.selected_field = None
                return

            self.show_object_editor = False
            self.stop_object_sprite_drag()
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.object_editor_state.selected_field = None
            return

        if self.object_editor_state.selected_field != "name":
            return

        self.handle_text_edit_input(event, max_length=48)
        self.object_editor_state.name = self.text_edit_state.text
        self.sync_object_editor_text_visual_state()

    def sync_object_editor_text_visual_state(self):
        if self.object_editor_state is None:
            return

        self.object_editor_state.text_cursor = self.text_edit_state.cursor
        self.object_editor_state.text_selection = self.text_edit_state.get_selection_range()

    def handle_text_edit_input(self, event, max_length=64):
        mods = pygame.key.get_mods()
        ctrl = bool(mods & pygame.KMOD_CTRL)
        shift = bool(mods & pygame.KMOD_SHIFT)

        if ctrl and event.key == pygame.K_a:
            self.text_edit_state.select_all()
            return True

        if ctrl and event.key == pygame.K_c:
            copy_to_clipboard(self.text_edit_state.selected_text())
            return True

        if ctrl and event.key == pygame.K_x:
            copy_to_clipboard(self.text_edit_state.selected_text())
            self.text_edit_state.replace_selection("")
            return True

        if ctrl and event.key == pygame.K_v:
            self.text_edit_state.insert_text(paste_from_clipboard(), max_length=max_length)
            return True

        if event.key == pygame.K_LEFT:
            self.text_edit_state.move_cursor(-1, selecting=shift, word=ctrl)
            return True

        if event.key == pygame.K_RIGHT:
            self.text_edit_state.move_cursor(1, selecting=shift, word=ctrl)
            return True

        if event.key == pygame.K_HOME:
            if shift and self.text_edit_state.selection_anchor is None:
                self.text_edit_state.selection_anchor = self.text_edit_state.cursor
            self.text_edit_state.cursor = 0
            if not shift:
                self.text_edit_state.clear_selection()
            return True

        if event.key == pygame.K_END:
            if shift and self.text_edit_state.selection_anchor is None:
                self.text_edit_state.selection_anchor = self.text_edit_state.cursor
            self.text_edit_state.cursor = len(self.text_edit_state.text)
            if not shift:
                self.text_edit_state.clear_selection()
            return True

        if event.key == pygame.K_BACKSPACE:
            self.text_edit_state.backspace()
            return True

        if event.key == pygame.K_DELETE:
            self.text_edit_state.delete()
            return True

        if event.unicode:
            self.text_edit_state.insert_text(event.unicode, max_length=max_length)
            return True

        return False

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

        if action == "window_close":
            return self.request_protected_action("exit")

        if action == "window_minimize":
            pygame.display.iconify()
            return None

        if action == "window_toggle_fullscreen":
            return "toggle_fullscreen"

        if action == "toggle_side_section":
            section_id = clicked_action["section_id"]
            self.side_panel_sections[section_id] = not self.side_panel_sections.get(section_id, True)
            self.scroll_side_panel(0)
            return None

        if action == "instance_property_add":
            selected_object = self.get_selected_scene_object()

            if selected_object is not None:
                new_key = add_object_property(selected_object)
                self.focus_instance_property(new_key, "value")
                self.mark_dirty()

            return None

        if action == "instance_property_delete":
            selected_object = self.get_selected_scene_object()

            if selected_object is not None and remove_object_property(
                selected_object,
                clicked_action.get("property_key"),
            ):
                self.property_edit = None
                self.mark_dirty()

            return None

        if action == "instance_property_focus_key":
            self.focus_instance_property(clicked_action.get("property_key"), "key")
            return None

        if action == "instance_property_focus_value":
            self.focus_instance_property(clicked_action.get("property_key"), "value")
            return None

        if action == "object_new":
            self.open_object_editor()
            return None

        if action == "object_edit_selected":
            if self.selected_object_type is not None:
                self.open_object_editor(self.selected_object_type)
            return None

        if action == "object_delete_selected":
            if self.selected_object_type is not None:
                self.show_object_delete_confirm = True
                self.active_menu = None
            return None

        if action == "object_delete_cancel":
            self.show_object_delete_confirm = False
            return None

        if action == "object_delete_confirm":
            self.confirm_object_delete()
            return None

        if action == "object_cancel":
            self.show_object_editor = False
            self.stop_object_sprite_drag()
            return None

        if action == "object_confirm_save":
            self.save_object_editor_definition(save_as=False)
            return None

        if action == "object_confirm_save_as":
            self.save_object_editor_definition(save_as=True)
            return None

        if action == "object_focus_name":
            self.object_editor_state.selected_field = "name"
            self.text_edit_state.set_text(self.object_editor_state.name)
            if self.last_mouse_clicks >= 2:
                self.text_edit_state.select_all()
            self.sync_object_editor_text_visual_state()
            return None

        if action == "object_focus_id":
            self.object_editor_state.selected_field = None
            return None

        if action == "object_toggle_group":
            group = clicked_action["group"]
            is_open = self.object_editor_state.open_groups.get(group, True)
            self.object_editor_state.open_groups[group] = not is_open
            return None

        if action == "object_toggle_solid":
            self.object_editor_state.solid = not self.object_editor_state.solid
            return None

        if action == "object_toggle_stackable":
            self.object_editor_state.stackable = not self.object_editor_state.stackable
            return None

        if action == "object_interaction_mode_dropdown":
            self.object_editor_state.interaction_mode_dropdown_open = not getattr(
                self.object_editor_state,
                "interaction_mode_dropdown_open",
                False,
            )
            return None

        if action == "object_interaction_mode_select":
            self.object_editor_state.interaction_mode = clicked_action["interaction_mode"]
            self.object_editor_state.interaction_mode_dropdown_open = False
            return None

        if action == "object_toggle_destructible":
            self.object_editor_state.destructible = not self.object_editor_state.destructible
            return None

        if action == "object_required_tool_dropdown":
            self.object_editor_state.required_tool_dropdown_open = not getattr(
                self.object_editor_state,
                "required_tool_dropdown_open",
                False,
            )
            return None

        if action == "object_required_tool_select":
            required_tool = clicked_action["required_tool"]
            self.object_editor_state.required_tool = None if required_tool == "none" else required_tool
            self.object_editor_state.required_tool_dropdown_open = False
            return None

        if action == "object_category_dropdown":
            self.object_editor_state.category_dropdown_open = not self.object_editor_state.category_dropdown_open
            return None

        if action == "object_category_select":
            self.object_editor_state.category = clicked_action["category"]
            self.object_editor_state.category_dropdown_open = False
            return None

        if action == "object_category_new":
            self.object_editor_state.category_dropdown_open = False
            self.set_status("Nueva categoria pendiente de persistencia")
            return None

        if action == "object_add_interaction_point":
            self.object_editor_state.interaction_points.append([0, 0])
            self.object_editor_state.selected_element = "interaction_point"
            return None

        if action == "object_clear_interaction_points":
            self.object_editor_state.interaction_points = []
            return None

        if action == "object_clear_sprite":
            self.object_editor_sprite = None
            self.object_editor_state.sprite = ""
            self.object_editor_state.sprite_size = None
            self.object_editor_state.sprite_offset = [0, 0]
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

            sprite, error_message = self.load_object_editor_png(source_path)

            if sprite is None:
                self.set_status(error_message)
                self.object_editor_state.status_message = error_message
                return None

            self.object_editor_sprite = sprite
            self.object_editor_state.sprite = source_path
            self.object_editor_state.source_sprite_path = source_path
            self.object_editor_state.sprite_size = [
                self.object_editor_sprite.get_width(),
                self.object_editor_sprite.get_height(),
            ]
            self.set_status(f"PNG cargado: {Path(source_path).name}")

            return None


        if action == "object_footprint_w_minus":
            if self.object_editor_state.footprint[0] > 1:
                self.object_editor_state.footprint[0] -= 1
            return None

        if action == "object_footprint_w_plus":
            self.object_editor_state.footprint[0] += 1
            return None

        if action == "object_footprint_h_minus":
            if self.object_editor_state.footprint[1] > 1:
                self.object_editor_state.footprint[1] -= 1
            return None

        if action == "object_footprint_h_plus":
            self.object_editor_state.footprint[1] += 1
            return None

        if action == "object_open":
            self.active_menu = None
            self.open_open_object_dialog()
            return None

        if action == "object_save":
            self.active_menu = None
            self.save_object_editor_definition(save_as=False)
            return None

        if action == "object_save_as":
            self.active_menu = None
            self.save_object_editor_definition(save_as=True)
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
            self.selected_scene_object_id = None
            self.property_edit = None
            return None

        if action == "mode_spawns":
            self.mode = "spawns"
            self.selected_object_type = None
            self.selected_scene_object_id = None
            self.property_edit = None
            return None

        if action == "mode_exits":
            self.mode = "exits"
            self.selected_object_type = None
            self.selected_scene_object_id = None
            self.property_edit = None
            return None

        if action == "select_object":
            object_type = clicked_action["object_type"]

            if object_type in self.object_definitions:
                self.mode = "objects"
                self.selected_object_type = object_type
                self.selected_scene_object_id = None
                self.property_edit = None

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
            self.selected_scene_object_id = None
            self.property_edit = None
            return None

        if action == "select_terrain":
            self.mode = "terrain"
            self.selected_object_type = None
            self.selected_scene_object_id = None
            self.property_edit = None
            self.selected_terrain_id = clicked_action["terrain_id"]
            return None



        return None

    def load_object_editor_png(self, source_path):
        path = Path(source_path)

        if not path.is_absolute():
            project_root = Path(__file__).resolve().parents[2]
            path = project_root / path

        if not path.exists():
            return None, "No se encontro el PNG seleccionado"

        try:
            image = pygame.image.load(str(path))
        except pygame.error as error:
            return None, f"No se pudo cargar el PNG: {error}"

        if pygame.display.get_surface() is None:
            return image, None

        try:
            return image.convert_alpha(), None
        except pygame.error:
            try:
                return image.convert(), None
            except pygame.error as error:
                return None, f"No se pudo convertir el PNG: {error}"

    def save_object_editor_definition(self, save_as=False):
        state = self.object_editor_state

        if state is None:
            return

        success, message, object_id, object_definition = save_object_definition(
            state.object_id,
            state.to_definition(),
            save_as=save_as,
            original_object_id=state.original_object_id,
        )

        state.status_message = message
        self.set_status(message)

        if not success:
            return

        state.object_id = object_id
        state.original_object_id = object_id
        state.sprite = object_definition.get("sprite", "")
        state.source_sprite_path = state.sprite
        state.category = object_definition.get("category", state.category)
        self.object_definitions[object_id] = object_definition
        self.selected_object_type = object_id
        self.mode = "objects"
        self.object_definitions_changed = True
        self.mark_dirty()

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

        preview_rect = self.object_editor_preview_layout.get("preview_rect")
        sprite_rect = self.object_editor_preview_layout.get("sprite_rect")
        footprint_rect = self.object_editor_preview_layout.get("footprint_rect")

        if preview_rect is None or not preview_rect.collidepoint(event.pos):
            return False

        if self.object_editor_state.selected_element == "sprite":
            sprite_handles = self.object_editor_preview_layout.get("sprite_handles", {})

            for handle_name, handle_rect in sprite_handles.items():
                if not handle_rect.collidepoint(event.pos):
                    continue

                self.object_editor_drag_mode = "sprite_resize"
                self.object_editor_drag_handle = handle_name
                self.object_editor_drag_start_pos = list(event.pos)
                self.object_editor_drag_start_size = list(
                    self.object_editor_state.sprite_size or [16, 16]
                )
                self.object_editor_drag_start_offset = list(
                    self.object_editor_state.sprite_offset
                )
                self.is_dragging_object_sprite = True
                return True

        if self.object_editor_state.selected_element == "footprint":
            footprint_handles = self.object_editor_preview_layout.get("footprint_handles", {})

            for handle_name, handle_rect in footprint_handles.items():
                if not handle_rect.collidepoint(event.pos):
                    continue

                self.object_editor_drag_mode = "footprint_resize"
                self.object_editor_drag_handle = handle_name
                self.object_editor_drag_start_pos = list(event.pos)
                self.object_editor_drag_start_footprint = list(
                    self.object_editor_state.footprint
                )
                self.object_editor_drag_start_footprint_offset = list(
                    self.object_editor_state.footprint_preview_offset
                )
                self.is_dragging_object_sprite = True
                return True

        if sprite_rect is not None and sprite_rect.collidepoint(event.pos):
            self.object_editor_state.selected_element = "sprite"
            self.object_editor_state.selected_field = None
            self.is_dragging_object_sprite = True
            self.object_editor_drag_mode = "sprite_move"
            self.object_editor_drag_handle = None

            self.object_sprite_drag_offset = [
                event.pos[0] - sprite_rect.x,
                event.pos[1] - sprite_rect.y,
            ]

            return True

        if footprint_rect is not None and footprint_rect.collidepoint(event.pos):
            self.object_editor_state.selected_element = "footprint"
            self.object_editor_state.selected_field = None
            return True

        self.object_editor_state.selected_element = None
        self.object_editor_state.selected_field = None

        return True

    def start_object_preview_pan(self, event):
        if self.object_editor_preview_layout is None:
            return False

        preview_rect = self.object_editor_preview_layout.get("preview_rect")

        if preview_rect is None or not preview_rect.collidepoint(event.pos):
            return False

        self.is_panning_object_preview = True
        self.object_preview_pan_start_pos = list(event.pos)
        self.object_preview_pan_start = list(self.object_editor_state.preview_pan)
        return True

    def update_object_preview_pan(self, event):
        if not self.is_panning_object_preview:
            return

        delta_x = event.pos[0] - self.object_preview_pan_start_pos[0]
        delta_y = event.pos[1] - self.object_preview_pan_start_pos[1]
        self.object_editor_state.preview_pan = [
            self.object_preview_pan_start[0] + delta_x,
            self.object_preview_pan_start[1] + delta_y,
        ]

    def zoom_object_preview(self, event):
        if self.object_editor_preview_layout is None:
            return False

        preview_rect = self.object_editor_preview_layout.get("preview_rect")

        if preview_rect is None or not preview_rect.collidepoint(event.pos):
            return False

        if event.button == 4:
            self.object_editor_state.preview_zoom = min(
                4.0,
                self.object_editor_state.preview_zoom * 1.1,
            )
        elif event.button == 5:
            self.object_editor_state.preview_zoom = max(
                0.25,
                self.object_editor_state.preview_zoom / 1.1,
            )

        return True


    def update_object_sprite_drag(self, event):
        if not self.is_dragging_object_sprite:
            return

        if self.object_editor_preview_layout is None:
            return

        if self.object_editor_drag_mode == "sprite_resize":
            self.update_object_sprite_resize(event)
            return

        if self.object_editor_drag_mode == "footprint_resize":
            self.update_object_footprint_resize(event)
            return

        anchor_pos = self.object_editor_preview_layout.get("anchor_pos")

        if anchor_pos is None:
            return

        new_sprite_x = event.pos[0] - self.object_sprite_drag_offset[0]
        new_sprite_y = event.pos[1] - self.object_sprite_drag_offset[1]
        zoom = self.object_editor_state.preview_zoom

        self.object_editor_state.sprite_offset = [
            int((new_sprite_x - anchor_pos[0]) / zoom),
            int((new_sprite_y - anchor_pos[1]) / zoom),
        ]

    def update_object_sprite_resize(self, event):
        zoom = self.object_editor_state.preview_zoom
        delta_x = (event.pos[0] - self.object_editor_drag_start_pos[0]) / zoom
        delta_y = (event.pos[1] - self.object_editor_drag_start_pos[1]) / zoom
        start_w = self.object_editor_drag_start_size[0]
        start_h = self.object_editor_drag_start_size[1]
        start_offset_x = self.object_editor_drag_start_offset[0]
        start_offset_y = self.object_editor_drag_start_offset[1]
        handle = self.object_editor_drag_handle

        new_w = start_w
        new_h = start_h
        new_offset_x = start_offset_x
        new_offset_y = start_offset_y

        if "e" in handle:
            new_w = start_w + delta_x
        if "w" in handle:
            new_w = start_w - delta_x
            if new_w < 8:
                delta_x = start_w - 8
                new_w = 8
            new_offset_x = start_offset_x + delta_x
        if "s" in handle:
            new_h = start_h + delta_y
        if "n" in handle:
            new_h = start_h - delta_y
            if new_h < 8:
                delta_y = start_h - 8
                new_h = 8
            new_offset_y = start_offset_y + delta_y

        self.object_editor_state.sprite_size = [
            max(8, int(new_w)),
            max(8, int(new_h)),
        ]
        self.object_editor_state.sprite_offset = [
            int(new_offset_x),
            int(new_offset_y),
        ]

    def update_object_footprint_resize(self, event):
        tile_size = self.object_editor_preview_layout.get("tile_size", 32)
        delta_x = event.pos[0] - self.object_editor_drag_start_pos[0]
        delta_y = event.pos[1] - self.object_editor_drag_start_pos[1]
        start_w = self.object_editor_drag_start_footprint[0]
        start_h = self.object_editor_drag_start_footprint[1]
        start_offset_x = self.object_editor_drag_start_footprint_offset[0]
        start_offset_y = self.object_editor_drag_start_footprint_offset[1]
        handle = self.object_editor_drag_handle

        new_w = start_w
        new_h = start_h
        new_offset_x = start_offset_x
        new_offset_y = start_offset_y

        if "e" in handle:
            new_w = start_w + round(delta_x / tile_size)
        if "w" in handle:
            delta_cells = round(delta_x / tile_size)
            new_w = start_w - delta_cells
            if new_w < 1:
                delta_cells = start_w - 1
                new_w = 1
            new_offset_x = start_offset_x + delta_cells * tile_size
        if "s" in handle:
            new_h = start_h + round(delta_y / tile_size)
        if "n" in handle:
            delta_cells = round(delta_y / tile_size)
            new_h = start_h - delta_cells
            if new_h < 1:
                delta_cells = start_h - 1
                new_h = 1
            new_offset_y = start_offset_y + delta_cells * tile_size

        self.object_editor_state.footprint = [
            max(1, int(new_w)),
            max(1, int(new_h)),
        ]
        self.object_editor_state.footprint_preview_offset = [
            int(new_offset_x),
            int(new_offset_y),
        ]


    def stop_object_sprite_drag(self):
        self.is_dragging_object_sprite = False
        self.object_editor_drag_mode = None
        self.object_editor_drag_handle = None
        self.is_panning_object_preview = False


    def handle_mouse_button_down(self, screen, event):
        self.last_mouse_clicks = getattr(event, "clicks", 1)

        if self.show_object_editor:
            if event.button in (4, 5):
                if self.zoom_object_preview(event):
                    return None
                self.scroll_object_editor_inspector(event.button)
                return None

            if event.button == 2:
                self.start_object_preview_pan(event)
                return None

            if event.button == 1:
                space_pressed = pygame.key.get_pressed()[pygame.K_SPACE]
                if space_pressed and self.start_object_preview_pan(event):
                    return None

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
                self.scroll_side_panel(-60)
                return None

            self.camera.zoom_in()
            return None

        if event.button == 5:
            if self.is_inside_side_panel(screen, event.pos):
                self.scroll_side_panel(60)
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
                    self.selected_scene_object_id = None
                    self.property_edit = None

                self.selected_area_type = None
                self.selected_area_id = None

            return None

        clicked_action = get_clicked_panel_action(event.pos, self.buttons)

        if clicked_action:
            return self.handle_panel_action(clicked_action)

        if self.is_inside_canvas(screen, event.pos):
            if self.mode == "objects" and self.selected_object_type is None:
                self.select_scene_object_at_cell(self.camera.screen_to_cell(event.pos))
                return None

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
                cell = self.camera.screen_to_cell(event.pos)
                if self.mode == "objects":
                    self.select_scene_object_at_cell(cell)
                else:
                    self.select_area_at_cell(cell)

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
            self.update_object_preview_pan(event)
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
                    cell = self.camera.screen_to_cell(event.pos)
                    if self.mode == "objects":
                        self.select_scene_object_at_cell(cell)
                    else:
                        self.select_area_at_cell(cell)

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
            if self.show_object_editor:
                self.handle_object_editor_text_input(event)
                return True

            if self.show_object_delete_confirm:
                if event.key == pygame.K_ESCAPE:
                    self.show_object_delete_confirm = False
                return True

            if self.show_area_name_dialog:
                self.handle_area_name_text_input(event)
                return True

            if self.show_save_as_dialog:
                self.handle_save_as_text_input(event)
                return True

            if (
                self.show_unsaved_dialog
                or self.show_open_scene_dialog
                or self.show_open_object_dialog
                or self.show_relations_dialog
            ):
                if event.key == pygame.K_ESCAPE:
                    self.show_unsaved_dialog = False
                    self.show_open_scene_dialog = False
                    self.show_open_object_dialog = False
                    self.show_relations_dialog = False
                    self.pending_protected_action = None
                return True

            if self.property_edit is not None:
                self.handle_instance_property_text_input(event)
                return True

            if event.key == pygame.K_ESCAPE:
                self.cancel_current_action()

            if event.key == pygame.K_s:
                self.save_current_scene()

        if event.type == pygame.MOUSEBUTTONDOWN:
            result = self.handle_mouse_button_down(screen, event)

            if result == "exit":
                return False

            if result == "toggle_fullscreen":
                return result

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

    def get_selected_scene_object(self):
        if self.selected_scene_object_id is None:
            return None

        return get_object_by_id(
            self.scene_data,
            self.selected_scene_object_id,
        )

    def select_scene_object_at_cell(self, cell):
        object_data = get_object_at_cell(
            self.scene_data,
            cell,
            self.object_definitions,
        )

        self.property_edit = None
        self.selected_area_type = None
        self.selected_area_id = None

        if object_data is None:
            self.selected_scene_object_id = None
            self.set_status("Sin objeto seleccionado")
            return False

        if not isinstance(object_data.get("properties"), dict):
            object_data["properties"] = {}
            self.mark_dirty()

        self.selected_scene_object_id = object_data.get("id")
        self.set_status(f"Objeto seleccionado: {self.selected_scene_object_id}")
        return True

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
        self.text_edit_state.set_text(self.area_name_text)
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
        self.text_edit_state.set_text(self.area_name_text)
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

        self.handle_text_edit_input(event, max_length=48)
        self.area_name_text = self.text_edit_state.text

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
