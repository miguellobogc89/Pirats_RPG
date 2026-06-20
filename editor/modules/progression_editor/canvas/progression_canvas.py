import pygame

from editor.modules.progression_editor.progression_theme import (
    INNER_PANEL,
    CARD,
    CARD_ACTIVE,
    BORDER,
    GRID_LINE,
    TEXT,
    MUTED,
    ACCENT,
)


class ProgressionCanvas:
    def __init__(self):
        self.rect = None

    def handle_click(self, pos, selected_chapter, selected_tool_id, next_node_number):
        if self.rect is None:
            return None

        if not self.rect.collidepoint(pos):
            return None

        if selected_chapter is None:
            return {"type": "canvas_empty_click"}

        if selected_tool_id is None:
            return {"type": "canvas_missing_tool"}

        cell_size = 32
        local_x = pos[0] - self.rect.x
        local_y = pos[1] - self.rect.y

        grid_x = local_x // cell_size
        grid_y = local_y // cell_size

        return {
            "type": "create_node",
            "node": {
                "id": f"node_{next_node_number}",
                "type": selected_tool_id,
                "name": self.build_node_name(selected_tool_id),
                "grid_pos": [grid_x, grid_y],
            },
        }

    def build_node_name(self, tool_id):
        if tool_id == "signal":
            return "Signal"

        if tool_id == "action":
            return "Action"

        return "Node"

    def draw(self, screen, rect, selected_chapter, selected_tool_id):
        self.rect = rect

        font_body = pygame.font.SysFont("consolas", 15)

        pygame.draw.rect(screen, INNER_PANEL, rect, border_radius=5)
        pygame.draw.rect(screen, BORDER, rect, 1, border_radius=5)

        self.draw_grid(screen, rect)
        self.draw_nodes(screen, rect, selected_chapter, font_body)

        if selected_chapter is None:
            message = "Crea o selecciona un capitulo."
            self.draw_center_message(screen, rect, font_body, message)
            return

        if selected_tool_id is None:
            message = "Selecciona Signal o Action en el panel derecho."
            text = font_body.render(message, True, MUTED)
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.y + 18))

    def draw_grid(self, screen, rect):
        cell_size = 32

        x = rect.x
        while x < rect.right:
            pygame.draw.line(screen, GRID_LINE, (x, rect.y), (x, rect.bottom))
            x += cell_size

        y = rect.y
        while y < rect.bottom:
            pygame.draw.line(screen, GRID_LINE, (rect.x, y), (rect.right, y))
            y += cell_size

    def draw_nodes(self, screen, rect, selected_chapter, font_body):
        if selected_chapter is None:
            return

        cell_size = 32

        for node in selected_chapter["nodes"]:
            grid_pos = node["grid_pos"]

            node_rect = pygame.Rect(
                rect.x + grid_pos[0] * cell_size + 4,
                rect.y + grid_pos[1] * cell_size + 4,
                120,
                44,
            )

            color = CARD_ACTIVE if node["type"] == "signal" else CARD

            pygame.draw.rect(screen, color, node_rect, border_radius=5)
            pygame.draw.rect(screen, BORDER, node_rect, 1, border_radius=5)
            pygame.draw.rect(
                screen,
                ACCENT,
                pygame.Rect(node_rect.x + 8, node_rect.y + 8, 5, node_rect.height - 16),
                border_radius=2,
            )

            label = font_body.render(node["name"], True, TEXT)
            screen.blit(label, (node_rect.x + 22, node_rect.y + 13))

    def draw_center_message(self, screen, rect, font_body, message):
        text = font_body.render(message, True, MUTED)
        screen.blit(
            text,
            (
                rect.centerx - text.get_width() // 2,
                rect.centery - text.get_height() // 2,
            ),
        )