import pygame


BG = (30, 34, 38)
PANEL = (38, 42, 48)
BORDER = (90, 96, 108)
TEXT = (232, 232, 232)
MUTED = (158, 166, 178)


class ProgressionEditorModule:
    def handle_event(self, screen, event):
        return True

    def draw(self, screen):
        screen.fill(BG)

        font_title = pygame.font.SysFont("consolas", 24, bold=True)
        font_body = pygame.font.SysFont("consolas", 15)

        rect = pygame.Rect(32, 64, screen.get_width() - 64, screen.get_height() - 96)
        pygame.draw.rect(screen, PANEL, rect, border_radius=6)
        pygame.draw.rect(screen, BORDER, rect, 1, border_radius=6)

        title = font_title.render("Progression Editor", True, TEXT)
        screen.blit(title, (rect.x + 28, rect.y + 28))

        lines = [
            "Placeholder preparado para capitulos, hitos, condiciones y efectos.",
            "Sin funcionalidad activa en este bloque.",
        ]

        y = rect.y + 78
        for line in lines:
            text = font_body.render(line, True, MUTED)
            screen.blit(text, (rect.x + 28, y))
            y += 26

