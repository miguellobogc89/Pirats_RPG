"""Prueba aislada 3.1: guardia, vision y cajas. Sin modificar la arena de combate."""
import math
import pygame
from .engine import CombatWorld, Fighter
from .components import StealthConfig
from .stealth import Obstacle, can_see

W, H = 900, 620
BG = (31, 45, 45)
WHITE = (232, 231, 214)


def make_world():
    world = CombatWorld(width=W, height=H)
    world.obstacles = [
        Obstacle(320, 170, 95, 110),
        Obstacle(440, 350, 125, 85),
        Obstacle(655, 190, 75, 105),
    ]
    world.add(Fighter("player", "player", 120, 310, hp=12, max_hp=12,
                      radius=15, speed=205, damage=2, reach=62))
    world.add(Fighter("guard", "enemy", 565, 220, hp=8, max_hp=8,
                      speed=78, walk_speed=48, chase_speed=110, radius=15, reach=36, damage=1,
                      facing_x=0, facing_y=1,
                      stealth=StealthConfig(),
                      patrol_points=((565, 220), (565, 490), (760, 490), (760, 120), (565, 120))))
    return world


def run():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Pirats RPG | Fase 3.1: sigilo y vision")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    small = pygame.font.SysFont("consolas", 15)
    world = make_world()
    debug = True
    running = True
    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                world = make_world()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                debug = not debug
        player, guard = world.fighters["player"], world.fighters["guard"]
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        world.move("player", dx, dy, dt)
        world.update(dt)
        screen.fill(BG)
        for x in range(0, W, 40):
            pygame.draw.line(screen, (42, 58, 57), (x, 0), (x, H))
        for y in range(0, H, 40):
            pygame.draw.line(screen, (42, 58, 57), (0, y), (W, y))
        if debug and guard.alive:
            cone = pygame.Surface((W, H), pygame.SRCALPHA)
            angle = math.atan2(guard.facing_y, guard.facing_x)
            half = math.radians(guard.vision_angle) / 2
            points = [(guard.x, guard.y)]
            for i in range(45):
                a = angle - half + 2 * half * i / 44
                points.append((guard.x + math.cos(a) * guard.vision_range,
                               guard.y + math.sin(a) * guard.vision_range))
            pygame.draw.polygon(cone, (220, 83, 72, 72) if guard.awake else (237, 204, 90, 64), points)
            # La vision efectiva se calcula en el motor, nunca a partir del dibujo.
            screen.blit(cone, (0, 0))
        for box in world.obstacles:
            rect = pygame.Rect(box.x, box.y, box.width, box.height)
            pygame.draw.rect(screen, (110, 88, 67), rect, border_radius=5)
            pygame.draw.rect(screen, (176, 147, 104), rect, 3, border_radius=5)
            pygame.draw.line(screen, (147, 119, 82), rect.topleft, rect.bottomright, 2)
        for actor in (player, guard):
            if not actor.alive:
                continue
            color = (87, 196, 179) if actor.team == "player" else (222, 100, 85)
            if actor.team == "enemy" and actor.surprise_remaining > 0:
                # Vibracion visual local, sin alterar coordenadas de fisica/IA.
                elapsed = 0.32 - actor.surprise_remaining
                jitter = round(math.sin(elapsed * 95) * 4 * min(1, actor.surprise_remaining / 0.08))
                px, py = round(actor.x) + jitter, round(actor.y)
                pygame.draw.circle(screen, (255, 221, 116), (px, py), round(actor.radius + 5), 2)
                exclamation = font.render("!", True, (255, 225, 120))
                screen.blit(exclamation, (px - exclamation.get_width() // 2, py - 49))
            else:
                px, py = round(actor.x), round(actor.y)
            pygame.draw.circle(screen, color, (px, py), round(actor.radius))
            if actor.team == "enemy" and actor.alert_state in ("confused", "search_ended"):
                symbol = "?" if actor.alert_state == "confused" else "..."
                bubble = font.render(symbol, True, (37, 43, 47))
                bw, bh = bubble.get_width() + 18, bubble.get_height() + 10
                rect = pygame.Rect(round(actor.x - bw / 2), round(actor.y - 61), bw, bh)
                pygame.draw.rect(screen, (247, 240, 215), rect, border_radius=9)
                pygame.draw.polygon(screen, (247, 240, 215),
                                    [(round(actor.x - 5), rect.bottom - 1),
                                     (round(actor.x + 5), rect.bottom - 1),
                                     (round(actor.x), rect.bottom + 7)])
                screen.blit(bubble, (rect.x + 9, rect.y + 5))
            pygame.draw.line(screen, WHITE, (actor.x, actor.y),
                             (actor.x + actor.facing_x * 24, actor.y + actor.facing_y * 24), 3)
        pygame.draw.rect(screen, (22, 32, 32), (0, 0, W, 84))
        screen.blit(font.render("WASD: moverse | F1: vision | R: reiniciar | ESC: salir", True, WHITE), (16, 11))
        visible = can_see(guard, player, world.obstacles) if guard.alive and player.alive else False
        status = ("SORPRENDIDO" if guard.surprise_remaining > 0 else
                  "CONFUNDIDO" if guard.alert_state == "confused" else
                  "SIN PISTAS" if guard.alert_state == "search_ended" else
                  "BUSCANDO" if guard.alert_state == "search" else "PERSIGUIENDO") if guard.awake else "CAMINANDO"
        info = f"GUARDIA: {status} | VISIBLE: {'SI' if visible else 'NO'} | DETECCION: {guard.detection / guard.detection_time:.0%} | VIDA: {player.hp}"
        screen.blit(small.render(info, True, (245, 205, 125)), (16, 47))
        if debug and guard.last_seen is not None:
            lx, ly = guard.last_seen
            pygame.draw.circle(screen, (255, 198, 90), (round(lx), round(ly)), 9, 2)
            pygame.draw.line(screen, (255, 198, 90), (lx - 13, ly), (lx + 13, ly), 1)
            pygame.draw.line(screen, (255, 198, 90), (lx, ly - 13), (lx, ly + 13), 1)
        if debug and guard.alert_state == "search":
            for px, py in guard.search_points:
                pygame.draw.circle(screen, (112, 168, 224), (round(px), round(py)), 3)
            for px, py in guard.searched_points:
                pygame.draw.circle(screen, (90, 110, 112), (round(px), round(py)), 3)
            if guard.search_goal:
                pygame.draw.circle(screen, (245, 210, 111), tuple(map(round, guard.search_goal)), 8, 2)
        if guard.awake:
            screen.blit(font.render("BUSQUEDA: barriendo zonas" if guard.alert_state == "search"
                                    else "ALERTA: persecucion rapida", True, (255, 148, 119)), (220, H - 40))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    run()
