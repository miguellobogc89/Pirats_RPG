"""Laboratorio visual de combate. Ejecutar: py -3.12 -m game.combat.action.demo"""
import pygame
from .engine import CombatWorld, Fighter
from .feedback import CombatFeedback

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
    pygame.display.set_caption("Pirats RPG - Laboratorio de combate | Fase 2")
    font = pygame.font.SysFont("consolas", 19)
    small = pygame.font.SysFont("consolas", 15)
    large = pygame.font.SysFont("consolas", 26, bold=True)
    clock = pygame.time.Clock()
    world = make_world()
    feedback = CombatFeedback()
    log = []
    running = True
    melee_down_at = None
    while running:
        dt = min(clock.tick(60) / 1000, 0.05)
        player = world.fighters["player"]
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                world = make_world()
                feedback = CombatFeedback()
                log = []
                player = world.fighters["player"]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                melee_down_at = pygame.time.get_ticks()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if melee_down_at is not None and player.alive and feedback.hitstop == 0:
                    mx, my = event.pos
                    charged = pygame.time.get_ticks() - melee_down_at >= 550
                    world.attack("player", (mx - player.x, my - player.y), charged=charged)
                melee_down_at = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and player.alive and feedback.hitstop == 0:
                mx, my = event.pos
                world.shoot("player", (mx - player.x, my - player.y))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and player.alive and feedback.hitstop == 0:
                pressed = pygame.key.get_pressed()
                dx = int(pressed[pygame.K_d] or pressed[pygame.K_RIGHT]) - int(pressed[pygame.K_a] or pressed[pygame.K_LEFT])
                dy = int(pressed[pygame.K_s] or pressed[pygame.K_DOWN]) - int(pressed[pygame.K_w] or pressed[pygame.K_UP])
                world.dash("player", (dx, dy) if dx or dy else None)
        keys = pygame.key.get_pressed()
        if player.alive and feedback.hitstop <= 0:
            world.move("player", int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                       int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]), dt)
            world.update(dt)
        for event in world.consume_events():
            feedback.handle(event, world)
            if event.kind in ("hit", "death", "aggro", "blocked"):
                log.append(f"{event.kind.upper()}: {event.actor} -> {event.target} {event.amount}")
                log = log[-5:]
        feedback.update(dt)
        # La escena se renderiza en coordenadas del mundo y se desplaza como
        # conjunto: la interfaz y el texto de HUD permanecen fijos.
        scene = pygame.Surface((W, H))
        scene.fill(BG)
        for x in range(0, W, 40):
            pygame.draw.line(scene, (43, 59, 57), (x, 0), (x, H))
        for y in range(0, H, 40):
            pygame.draw.line(scene, (43, 59, 57), (0, y), (W, y))
        for projectile in world.projectiles:
            pygame.draw.circle(scene, (125, 202, 255), (round(projectile.x), round(projectile.y)), round(projectile.radius))
            pygame.draw.circle(scene, (217, 243, 255), (round(projectile.x), round(projectile.y)), 2)
        for fighter in world.fighters.values():
            if not fighter.alive:
                continue
            color = (79, 176, 166) if fighter.team == "player" else (176, 97, 78)
            if fighter.id == "farm_boss":
                color = (178, 116, 153)
            color = feedback.fighter_color(fighter, color)
            pygame.draw.circle(scene, color, (round(fighter.x), round(fighter.y)), round(fighter.radius))
            pygame.draw.line(scene, WHITE, (fighter.x, fighter.y),
                             (fighter.x + fighter.facing_x * 23, fighter.y + fighter.facing_y * 23), 3)
            if fighter.windup > 0:
                pygame.draw.circle(scene, (240, 150, 105), (round(fighter.x), round(fighter.y)),
                                   round(fighter.reach + fighter.radius), 2)
            if fighter.stun > 0:
                pygame.draw.circle(scene, (255, 216, 125), (round(fighter.x), round(fighter.y)),
                                   round(fighter.radius + 6), 2)
            if fighter.invulnerability > 0:
                pygame.draw.arc(scene, (158, 214, 231),
                                (fighter.x - fighter.radius - 7, fighter.y - fighter.radius - 7,
                                 2 * (fighter.radius + 7), 2 * (fighter.radius + 7)),
                                0.2, 4.6, 2)
            bar = pygame.Rect(fighter.x - 26, fighter.y - fighter.radius - 17, 52, 6)
            pygame.draw.rect(scene, (75, 55, 55), bar)
            pygame.draw.rect(scene, (107, 201, 116),
                             (bar.x, bar.y, round(bar.w * fighter.hp / fighter.max_hp), bar.h))
            scene.blit(small.render(fighter.id, True, WHITE),
                       (fighter.x - 25, fighter.y + fighter.radius + 6))
        feedback.draw(scene, world, small, large)
        screen.fill(BG)
        screen.blit(scene, feedback.offset())
        pygame.draw.rect(screen, (24, 36, 35), (0, 0, W, 80))
        screen.blit(font.render("WASD | Izq sable (mantener=cargar) | Dcho proyectil | ESPACIO dash | R reiniciar", True, WHITE), (16, 12))
        screen.blit(font.render(f"VIDA: {player.hp}/{player.max_hp} | ENERGIA: {round(player.stamina)}/{round(player.max_stamina)} | COMBO: {player.combo_step if player.combo_timer else 0} | ENEMIGOS: {sum(f.alive for f in world.fighters.values() if f.team != 'player')}", True, WHITE), (16, 43))
        for i, msg in enumerate(log):
            screen.blit(small.render(msg, True, WHITE), (16, H - 100 + i * 17))
        if not player.alive or not any(f.alive for f in world.fighters.values() if f.team != "player"):
            msg = "DERROTA - Pulsa R" if not player.alive else "VICTORIA - Pulsa R"
            screen.blit(font.render(msg, True, (248, 217, 130)), (W // 2 - 100, 95))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    run()
