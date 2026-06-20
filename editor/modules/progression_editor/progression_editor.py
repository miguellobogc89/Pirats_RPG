import pygame

from editor.modules.progression_editor.canvas.progression_canvas import ProgressionCanvas
from editor.modules.progression_editor.panels.left_panel import ProgressionLeftPanel
from editor.modules.progression_editor.panels.right_panel import ProgressionRightPanel
from editor.modules.progression_editor.progression_theme import (
    BG,
    PANEL,
    BORDER,
    TEXT,
    MUTED,
)


class ProgressionEditorModule:
    def __init__(self):
        self.left_panel = ProgressionLeftPanel()
        self.right_panel = ProgressionRightPanel()
        self.canvas = ProgressionCanvas()

        self.chapters = []
        self.selected_chapter_id = None
        self.selected_tool_id = None

        self.next_chapter_number = 1
        self.next_node_number = 1

    def handle_event(self, screen, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_click(event.pos)

        return True

    def handle_click(self, pos):
        action = self.left_panel.handle_click(pos)
        if action:
            self.handle_left_action(action)
            return True

        action = self.right_panel.handle_click(pos)
        if action:
            self.handle_right_action(action)
            return True

        chapter = self.get_selected_chapter()

        result = self.canvas.handle_click(
            pos,
            chapter,
            self.selected_tool_id,
            self.next_node_number,
        )

        if result:
            if result["type"] == "create_node":
                chapter["nodes"].append(result["node"])
                self.next_node_number += 1

            return True

        return True

    def handle_left_action(self, action):
        if action["type"] == "new_chapter":
            self.create_chapter()
            return

        if action["type"] == "select_chapter":
            self.selected_chapter_id = action["chapter_id"]

    def handle_right_action(self, action):
        if action["type"] == "select_tool":
            self.selected_tool_id = action["tool_id"]

    def create_chapter(self):
        chapter_id = f"chapter_{self.next_chapter_number}"

        chapter = {
            "id": chapter_id,
            "name": f"Capitulo {self.next_chapter_number}",
            "nodes": [],
        }

        self.chapters.append(chapter)
        self.selected_chapter_id = chapter_id
        self.next_chapter_number += 1

    def get_selected_chapter(self):
        for chapter in self.chapters:
            if chapter["id"] == self.selected_chapter_id:
                return chapter

        return None

    def draw(self, screen):
        screen.fill(BG)

        font_title = pygame.font.SysFont("consolas", 24, bold=True)
        font_body = pygame.font.SysFont("consolas", 15)

        main_rect = pygame.Rect(32, 64, screen.get_width() - 64, screen.get_height() - 96)
        pygame.draw.rect(screen, PANEL, main_rect, border_radius=6)
        pygame.draw.rect(screen, BORDER, main_rect, 1, border_radius=6)

        screen.blit(
            font_title.render("Progression Editor", True, TEXT),
            (main_rect.x + 28, main_rect.y + 24),
        )
        screen.blit(
            font_body.render("Editor visual de capitulos, señales y acciones.", True, MUTED),
            (main_rect.x + 28, main_rect.y + 58),
        )

        content_rect = pygame.Rect(
            main_rect.x + 24,
            main_rect.y + 100,
            main_rect.width - 48,
            main_rect.height - 124,
        )

        left_rect = pygame.Rect(content_rect.x, content_rect.y, 260, content_rect.height)
        right_rect = pygame.Rect(content_rect.right - 260, content_rect.y, 260, content_rect.height)
        canvas_rect = pygame.Rect(
            left_rect.right + 18,
            content_rect.y,
            content_rect.width - left_rect.width - right_rect.width - 36,
            content_rect.height,
        )

        self.left_panel.draw(screen, left_rect, self.chapters, self.selected_chapter_id)

        self.canvas.draw(
            screen,
            canvas_rect,
            self.get_selected_chapter(),
            self.selected_tool_id,
        )

        self.right_panel.draw(screen, right_rect, self.selected_tool_id)