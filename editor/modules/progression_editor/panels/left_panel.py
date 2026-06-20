import pygame

from editor.ui.widgets.editor_button import draw_editor_button
from editor.modules.progression_editor.progression_theme import CARD, CARD_ACTIVE, BORDER, TEXT, MUTED, ACCENT


class ProgressionLeftPanel:
    def __init__(self):
        self.chapter_buttons = []
        self.new_chapter_button = None

    def handle_click(self, pos):
        if self.new_chapter_button and self.new_chapter_button["rect"].collidepoint(pos):
            return {"type": "new_chapter"}

        for button in self.chapter_buttons:
            if button["rect"].collidepoint(pos):
                return {"type": "select_chapter", "chapter_id": button["chapter_id"]}

        return None

    def draw(self, screen, rect, chapters, selected_chapter_id):
        font_title = pygame.font.SysFont("consolas", 16, bold=True)
        font_body = pygame.font.SysFont("consolas", 14)

        pygame.draw.rect(screen, CARD, rect, border_radius=5)
        pygame.draw.rect(screen, BORDER, rect, 1, border_radius=5)

        screen.blit(font_title.render("Capitulos", True, TEXT), (rect.x + 14, rect.y + 12))

        self.new_chapter_button = draw_editor_button(
            screen,
            pygame.Rect(rect.x + 14, rect.y + 42, rect.width - 28, 30),
            "+ Nuevo capitulo",
            "new_chapter",
            compact=True,
        )

        self.chapter_buttons = []
        y = rect.y + 88

        for chapter in chapters:
            row = pygame.Rect(rect.x + 10, y, rect.width - 20, 52)
            color = CARD_ACTIVE if chapter["id"] == selected_chapter_id else CARD

            pygame.draw.rect(screen, color, row, border_radius=5)
            pygame.draw.rect(screen, BORDER, row, 1, border_radius=5)
            pygame.draw.rect(screen, ACCENT, pygame.Rect(row.x + 10, row.y + 10, 5, row.height - 20), border_radius=2)

            screen.blit(font_title.render(chapter["name"], True, TEXT), (row.x + 24, row.y + 8))
            screen.blit(font_body.render(f'{len(chapter["nodes"])} elementos', True, MUTED), (row.x + 24, row.y + 30))

            self.chapter_buttons.append({"rect": row, "chapter_id": chapter["id"]})
            y += 60