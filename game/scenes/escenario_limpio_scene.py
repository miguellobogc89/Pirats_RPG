"""Escenario de prueba aislado: sin renderer de granja ni sprites heredados."""
import pygame
from game.scenes.farm_scene import FarmScene
from game.world.camera import get_camera_position
from game.world.collision_manager import get_scene_collision_rects

WORLD_W, WORLD_H = 640, 512
BACKGROUND = (252, 252, 252)
GROUND = (242, 242, 242)
OUTLINE = (175, 175, 175)
COLLISION = (155, 155, 155)


class EscenarioLimpioScene(FarmScene):
    def update(self, dt):
        self.app.update_farm_scene(dt)

    def draw(self):
        screen = self.app.screen
        sw, sh = screen.get_size()
        player = self.app.state["player"]
        cx, cy = get_camera_position(player["x"], player["y"], sw, sh, WORLD_W, WORLD_H)
        # Mapa menor que la pantalla: centrado, sin escala ni tiles visibles.
        cx = -(sw - WORLD_W) / 2
        cy = -(sh - WORLD_H) / 2
        screen.fill(BACKGROUND)
        world = pygame.Rect(round(-cx), round(-cy), WORLD_W, WORLD_H)
        pygame.draw.rect(screen, GROUND, world)
        pygame.draw.rect(screen, OUTLINE, world, 1)
        for collision in get_scene_collision_rects():
            box = pygame.Rect(round(collision.x - cx), round(collision.y - cy), collision.width, collision.height)
            pygame.draw.rect(screen, COLLISION, box, 1)
        px, py = round(player["x"] - cx), round(player["y"] - cy)
        pygame.draw.circle(screen, (110, 110, 110), (px, py), 11, 1)
        pygame.draw.circle(screen, (150, 150, 150), (px, py - 15), 7, 1)
        health = self.app.state.get("health", {})
        maximum = max(1, health.get("max", 10))
        current = max(0, health.get("current", maximum))
        pygame.draw.rect(screen, OUTLINE, (18, 20, 155, 7), 1)
        pygame.draw.rect(screen, (210, 210, 210), (19, 21, round(153 * current / maximum), 5))
        if self.app.menu_open:
            from game.hud.menu_overlay import draw_menu
            draw_menu(self.app)
