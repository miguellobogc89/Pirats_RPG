import pygame

from editor.modules.database_editor.database_framework import DatabaseCategory
from editor.modules.database_editor.database_theme import (
    BG,
    BORDER,
    ERROR,
    MUTED,
    PANEL,
    SUCCESS,
    TEXT,
)
from editor.modules.database_editor.database_views import (
    CategoryNavigator,
    MasterDetailView,
)
from editor.modules.database_editor.database_widgets import draw_database_save_button
from editor.modules.database_editor.object_provider import ObjectDefinitionsProvider


class DatabaseEditorModule:
    def __init__(self):
        self.categories = create_database_categories()
        self.selected_category_id = "objects"
        self.category_nav = CategoryNavigator()
        self.master_detail_views = {
            category.id: MasterDetailView()
            for category in self.categories
            if category.is_active()
        }
        self.edit_state = None
        self.dropdown_state = None
        self.status_message = "Click en un valor para editar. Enter confirma. Ctrl+S guarda."
        self.status_color = MUTED
        self.save_button_rect = None

    def handle_event(self, screen, event):
        if event.type == pygame.KEYDOWN:
            return self.handle_key(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.handle_click(event.pos)

            if event.button in (4, 5):
                amount = -42 if event.button == 4 else 42
                return self.handle_scroll(event.pos, amount)

        return True

    def handle_key(self, event):
        if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.save_selected_record()
            return True

        if self.edit_state is None:
            return True

        if event.key == pygame.K_ESCAPE:
            self.edit_state = None
            self.set_status("Edicion cancelada.", MUTED)
            return True

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.commit_edit()
            return True

        if event.key == pygame.K_BACKSPACE:
            self.edit_state["text"] = self.edit_state["text"][:-1]
            return True

        if event.unicode:
            self.edit_state["text"] += event.unicode

        return True

    def handle_click(self, pos):
        if self.save_button_rect and self.save_button_rect.collidepoint(pos):
            self.save_selected_record()
            return True

        category_id = self.category_nav.handle_click(pos)
        if category_id is not None:
            self.edit_state = None
            self.dropdown_state = None
            self.selected_category_id = category_id
            return True

        view = self.get_active_master_detail_view()
        if view is not None:
            action = view.handle_click(pos)
            self.handle_view_action(action)
            return True

        return True

    def handle_view_action(self, action):
        if not action:
            self.dropdown_state = None
            return

        if action["type"] == "record":
            self.edit_state = None
            self.dropdown_state = None
            return

        if action["type"] == "field_picklist_open":
            row = action["row"]
            self.edit_state = None
            self.dropdown_state = {
                "record_id": action["record_id"],
                "path": row.get("path"),
            }
            self.set_status("Selecciona una opcion de la lista.", MUTED)
            return

        if action["type"] == "field_picklist_select":
            category = self.get_selected_category()
            success, message = category.update_record_field(
                action["record_id"],
                action["row"].get("path"),
                action.get("value"),
            )
            self.dropdown_state = None
            self.set_status(message, SUCCESS if success else ERROR)
            return

        if action["type"] == "field":
            row = action["row"]

            if not row.get("editable"):
                return

            self.edit_state = {
                "record_id": action["record_id"],
                "path": row.get("path"),
                "text": str(row.get("value", "")),
            }
            self.dropdown_state = None
            self.set_status("Editando campo. Enter confirma, Esc cancela.", MUTED)
            return

        if action["type"] == "field_toggle":
            row = action["row"]

            if not row.get("editable"):
                return

            category = self.get_selected_category()
            new_value = "false" if row.get("raw_value") else "true"
            success, message = category.update_record_field(
                action["record_id"],
                row.get("path"),
                new_value,
            )
            self.set_status(message, SUCCESS if success else ERROR)

    def commit_edit(self):
        category = self.get_selected_category()

        if self.edit_state is None:
            return

        success, message = category.update_record_field(
            self.edit_state["record_id"],
            self.edit_state["path"],
            self.edit_state["text"],
        )

        if success:
            self.edit_state = None
            self.set_status(message, SUCCESS)
        else:
            self.set_status(message, ERROR)

    def save_selected_record(self):
        if self.edit_state is not None:
            self.commit_edit()

            if self.edit_state is not None:
                return

        category = self.get_selected_category()
        view = self.get_active_master_detail_view()

        if view is None or view.selected_record_id is None:
            return

        success, message = category.save_record(view.selected_record_id)
        self.set_status(message, SUCCESS if success else ERROR)

    def set_status(self, message, color):
        self.status_message = message
        self.status_color = color

    def handle_scroll(self, pos, amount):
        view = self.get_active_master_detail_view()
        if view is not None:
            return view.handle_scroll(pos, amount)

        return True

    def get_selected_category(self):
        for category in self.categories:
            if category.id == self.selected_category_id:
                return category

        return self.categories[0]

    def get_active_master_detail_view(self):
        return self.master_detail_views.get(self.selected_category_id)

    def draw(self, screen):
        screen.fill(BG)

        font_title = pygame.font.SysFont("consolas", 24, bold=True)
        font_body = pygame.font.SysFont("consolas", 15)
        font_label = pygame.font.SysFont("consolas", 16, bold=True)

        rect = pygame.Rect(32, 64, screen.get_width() - 64, screen.get_height() - 96)
        pygame.draw.rect(screen, PANEL, rect, border_radius=6)
        pygame.draw.rect(screen, BORDER, rect, 1, border_radius=6)

        title = font_title.render("Database Editor", True, TEXT)
        screen.blit(title, (rect.x + 28, rect.y + 28))

        subtitle = font_body.render(
            "Placeholder para bases de datos editables del proyecto.",
            True,
            MUTED,
        )
        screen.blit(subtitle, (rect.x + 28, rect.y + 64))

        content_rect = pygame.Rect(rect.x + 28, rect.y + 112, rect.width - 56, rect.height - 140)
        category_rect = pygame.Rect(content_rect.x, content_rect.y, 260, content_rect.height)
        detail_rect = pygame.Rect(category_rect.right + 24, content_rect.y, content_rect.width - 284, content_rect.height)

        self.category_nav.draw(
            screen,
            category_rect,
            self.categories,
            self.selected_category_id,
            font_label,
            font_body,
        )
        self.draw_selected_category(screen, detail_rect, font_label, font_body)
        self.draw_status(screen, rect, font_body)
        self.draw_save_action(screen, font_body)

    def draw_selected_category(self, screen, rect, font_label, font_body):
        category = self.get_selected_category()
        view = self.master_detail_views.get(category.id)

        if view is not None:
            view.draw(
                screen,
                rect,
                category.label,
                category.get_records(),
                font_label,
                font_body,
                self.edit_state,
                self.dropdown_state,
            )
            return

        title = font_label.render(category.label, True, TEXT)
        screen.blit(title, (rect.x, rect.y))

        message = font_body.render("Categoria prevista. Sin funcionalidad activa todavia.", True, MUTED)
        screen.blit(message, (rect.x, rect.y + 34))

    def draw_status(self, screen, rect, font_body):
        status = font_body.render(self.status_message, True, self.status_color)
        screen.blit(status, (rect.x + 28, rect.bottom - 30))

    def draw_save_action(self, screen, font_body):
        view = self.get_active_master_detail_view()
        category = self.get_selected_category()
        can_save = (
            view is not None
            and view.selected_record_id is not None
            and category.is_record_dirty(view.selected_record_id)
        )

        if not can_save:
            self.save_button_rect = None
            return

        anchor_rect = view.detail_rect
        if anchor_rect is None:
            self.save_button_rect = None
            return

        button_width = 110
        button_height = 28
        self.save_button_rect = pygame.Rect(
            anchor_rect.right - button_width - 16,
            anchor_rect.y + 12,
            button_width,
            button_height,
        )
        draw_database_save_button(screen, self.save_button_rect, enabled=True)


def create_database_categories():
    return [
        DatabaseCategory("objects", "Objects", provider=ObjectDefinitionsProvider()),
        DatabaseCategory("items", "Items", planned=True),
        DatabaseCategory("crops", "Crops", planned=True),
        DatabaseCategory("enemies", "Enemies", planned=True),
        DatabaseCategory("recipes", "Recipes", planned=True),
        DatabaseCategory("cartography", "Cartography", planned=True),
        DatabaseCategory("skills", "Skills", planned=True),
    ]
