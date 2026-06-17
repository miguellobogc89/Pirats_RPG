import pygame

from editor.modules.database_editor.database_editor import DatabaseEditorModule
from editor.modules.progression_editor.progression_editor import ProgressionEditorModule
from editor.modules.scene_editor.scene_editor import SceneEditorModule


EDITOR_MIN_WIDTH = 1100
EDITOR_MIN_HEIGHT = 720
EDITOR_DEFAULT_WIDTH = 1440
EDITOR_DEFAULT_HEIGHT = 900
FPS = 60

NAV_ACTIVE = (64, 92, 132)
NAV_IDLE = (38, 42, 48)
NAV_BORDER = (112, 118, 130)
NAV_TEXT = (238, 238, 238)


class EditorShell:
    def __init__(self):
        pygame.init()

        self.editor_width = EDITOR_DEFAULT_WIDTH
        self.editor_height = EDITOR_DEFAULT_HEIGHT
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode(
            (self.editor_width, self.editor_height),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption("RPG Editor")
        self.clock = pygame.time.Clock()

        self.modules = {
            "scene": SceneEditorModule(),
            "database": DatabaseEditorModule(),
            "progression": ProgressionEditorModule(),
        }
        self.active_module_id = "scene"
        self.nav_buttons = []

    def get_active_module(self):
        return self.modules[self.active_module_id]

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (self.editor_width, self.editor_height),
                pygame.RESIZABLE,
            )

    def resize_window(self, width, height):
        self.editor_width = max(EDITOR_MIN_WIDTH, width)
        self.editor_height = max(EDITOR_MIN_HEIGHT, height)
        self.screen = pygame.display.set_mode(
            (self.editor_width, self.editor_height),
            pygame.RESIZABLE,
        )

    def handle_shell_click(self, pos):
        for button in self.nav_buttons:
            if button["rect"].collidepoint(pos):
                self.active_module_id = button["module_id"]
                return True

        return False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            self.toggle_fullscreen()
            return True

        if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
            self.resize_window(event.w, event.h)
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_shell_click(event.pos):
                return True

        result = self.get_active_module().handle_event(self.screen, event)

        if result == "toggle_fullscreen":
            self.toggle_fullscreen()
            return True

        return result is not False

    def draw_navigation(self):
        labels = [
            ("scene", "Scene"),
            ("database", "Database"),
            ("progression", "Progression"),
        ]
        font = pygame.font.SysFont("consolas", 14, bold=True)
        height = 28
        gap = 8
        widths = {
            "scene": 82,
            "database": 108,
            "progression": 126,
        }
        total_width = sum(widths[module_id] for module_id, _ in labels) + gap
        x = max(260, self.screen.get_width() - total_width - 128)
        y = 3

        self.nav_buttons = []

        for module_id, label in labels:
            width = widths[module_id]
            rect = pygame.Rect(x, y, width, height)
            color = NAV_ACTIVE if module_id == self.active_module_id else NAV_IDLE

            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            pygame.draw.rect(self.screen, NAV_BORDER, rect, 1, border_radius=4)

            text = font.render(label, True, NAV_TEXT)
            self.screen.blit(
                text,
                (
                    rect.x + (rect.width - text.get_width()) // 2,
                    rect.y + (rect.height - text.get_height()) // 2,
                ),
            )

            self.nav_buttons.append({
                "rect": rect,
                "module_id": module_id,
            })
            x += width + gap

    def draw(self):
        self.get_active_module().draw(self.screen)
        self.draw_navigation()
        pygame.display.flip()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                running = self.handle_event(event)

                if not running:
                    break

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    EditorShell().run()
