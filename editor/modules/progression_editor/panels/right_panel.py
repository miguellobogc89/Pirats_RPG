import pygame

from editor.modules.progression_editor.progression_theme import CARD, CARD_ACTIVE, BORDER, TEXT, MUTED, ACCENT


class ProgressionRightPanel:
    def __init__(self):
        self.tool_buttons = []

    def handle_click(self, pos):
        for button in self.tool_buttons:
            if button["rect"].collidepoint(pos):
                return {"type": "select_tool", "tool_id": button["tool_id"]}

        return None

    def draw(self, screen, rect, selected_tool_id):
        font_title = pygame.font.SysFont("consolas", 16, bold=True)
        font_body = pygame.font.SysFont("consolas", 14)

        pygame.draw.rect(screen, CARD, rect, border_radius=5)
        pygame.draw.rect(screen, BORDER, rect, 1, border_radius=5)

        screen.blit(font_title.render("Insertar", True, TEXT), (rect.x + 14, rect.y + 12))
        screen.blit(font_body.render("Selecciona y pulsa en el lienzo.", True, MUTED), (rect.x + 14, rect.y + 38))

        tools = [
            {"id": "signal", "label": "Signal", "description": "Evento que dispara algo"},
            {"id": "action", "label": "Action", "description": "Resultado o cambio"},
        ]

        self.tool_buttons = []
        y = rect.y + 78

        for tool in tools:
            row = pygame.Rect(rect.x + 10, y, rect.width - 20, 58)
            color = CARD_ACTIVE if tool["id"] == selected_tool_id else CARD

            pygame.draw.rect(screen, color, row, border_radius=5)
            pygame.draw.rect(screen, BORDER, row, 1, border_radius=5)
            pygame.draw.rect(screen, ACCENT, pygame.Rect(row.x + 10, row.y + 10, 5, row.height - 20), border_radius=2)

            screen.blit(font_title.render(tool["label"], True, TEXT), (row.x + 24, row.y + 8))
            screen.blit(font_body.render(tool["description"], True, MUTED), (row.x + 24, row.y + 32))

            self.tool_buttons.append({"rect": row, "tool_id": tool["id"]})
            y += 68