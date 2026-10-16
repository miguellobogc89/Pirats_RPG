"""Prueba visual independiente. Ejecutar desde la raiz: python -m game.combat.action.demo"""
import math
import pygame
from .engine import CombatWorld, Fighter

W, H = 900, 620
BG = (34, 49, 48)
WHITE = (236, 232, 210)


def make_world():
    world = CombatWorld(width=W, height=H)
    world.add(Fighter("player", "player", 220, 320, hp=12, max_hp=12,
                      radius=16, speed=205, damage=2, reach=62, attack_cooldown=0.36))
    world.add(Fighter("rat_1", "enemy", 520, 200, hp=3, max_hp=3, radius=13, speed=95))
    world.add(Fighter("rat_2", "enemy", 620, 440, hp=3, max_hp=3, radius=13, speed=95))
    world.add(Fighter("farm_boss", "enemy", 740, 300, hp=12, max_hp=12,
                      radius=27, speed=58, damage=3, reach=35, attack_cooldown=1.4))
    return world


def run():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Pirats RPG - Nuevo combate de accion (prueba aislada)")
    font = pygame.font.SysFont("consolas", 20)
    small = pygame.font.SysFont("consolas", 15)
    clock = pygame.time.Clock()
    world = make_world()
    log = []
    running = True
    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        player = world.fighters["player"]
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                world = make_world()
                log = []
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and player.alive:
                mx, my = event.pos
                world.attack("player", (mx - player.x, my - player.y))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and player.alive:
                world.attack("player")
        keys = pygame.key.get_pressed()
        if player.alive:
            world.move("player", int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                       int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]), dt)
            world.update(dt)
        for event in world.consume_events():
            if event.kind in ("hit", "death", "aggro"):
                log.append(f"{event.kind.upper()}: {event.actor} -> {event.target} {event.amount}")
                log = log[-5:]
        screen.fill(BG)
        for x in range(0, W, 40):
            pygame.draw.line(screen, (43, 59, 57), (x, 0), (x, H))
        for y in range(0, H, 40):
            pygame.draw.line(screen, (43, 59, 57), (0, y), (W, y))
        for fighter in world.fighters.values():
            if not fighter.alive:
                continue
            color = (79, 176, 166) if fighter.team == "player" else (176, 97, 78)
            if fighter.id == "farm_boss":
                color = (178, 116, 153)
            if fighter.invulnerability > 0:
                color = (235, 216, 151)
            pygame.draw.circle(screen, color, (round(fighter.x), round(fighter.y)), round(fighter.radius))
            pygame.draw.line(screen, WHITE, (fighter.x, fighter.y),
                             (fighter.x + fighter.facing_x * 23, fighter.y + fighter.facing_y * 23), 3)
            if fighter.windup > 0:
                pygame.draw.circle(screen, (240, 150, 105), (round(fighter.x), round(fighter.y)),
                                   round(fighter.reach + fighter.radius), 2)
            bar = pygame.Rect(fighter.x - 26, fighter.y - fighter.radius - 17, 52, 6)
            pygame.draw.rect(screen, (75, 55, 55), bar)
            pygame.draw.rect(screen, (107, 201, 116),
                             (bar.x, bar.y, round(bar.w * fighter.hp / fighter.max_hp), bar.h))
            screen.blit(small.render(fighter.id, True, WHITE), (fighter.x - 25, fighter.y + fighter.radius + 6))
        screen.blit(font.render("WASD mover | Clic izquierdo atacar hacia cursor | ESPACIO atacar | R reiniciar | ESC salir", True, WHITE), (16, 16))
        screen.blit(font.render(f"VIDA: {player.hp}/{player.max_hp}  |  ENEMIGOS: {sum(f.alive for f in world.fighters.values() if f.team != 'player')}", True, WHITE), (16, 46))
        for i, msg in enumerate(log):
            screen.blit(small.render(msg, True, WHITE), (16, H - 100 + i * 17))
        if not player.alive or not any(f.alive for f in world.fighters.values() if f.team != "player"):
            msg = "DERROTA - Pulsa R" if not player.alive else "VICTORIA - Pulsa R"
            screen.blit(font.render(msg, True, (248, 217, 130)), (W // 2 - 100, 95))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    run()
