"""Prototipo aislado: encuentro nocturno en la playa. Ejecutar: python prototype_beach.py"""
import math
import random
from pathlib import Path
import pygame

CELL = 40
COLS, ROWS = 20, 10
WIDTH, HEIGHT = CELL * COLS, CELL * ROWS
FPS = 60
ROOT = Path(__file__).resolve().parent
SAND = (245, 245, 245)
SEA = (226, 226, 226)
INK = (20, 20, 20)
MODES = ["Rapida y alcance", "Lenta y alcance", "Lenta con esbirros"]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def move_towards(a, b, speed, dt):
    delta = b - a
    if delta.length_squared() > 0:
        a += delta.normalize() * min(delta.length(), speed * dt)


class BeachTest:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pirats RPG | Prueba de persecucion nocturna")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 19)
        self.small = pygame.font.SysFont("consolas", 15)
        self.reset(0)

    def reset(self, mode):
        self.mode = mode
        self.player = pygame.Vector2(CELL * 2.5, CELL * 5.5)
        self.boss = pygame.Vector2(CELL * 17, CELL * 5)
        self.hp = 100
        self.boss_hp = 999
        self.attack_timer = 0
        self.boss_timer = 0
        self.hit_flash = 0
        self.boss_attack_flash = 0
        self.knockback = pygame.Vector2()
        self.stun_timer = 0
        self.minions = []
        self.spawn_timer = 2.5
        self.elapsed = 0
        self.state = "play"
        self.intro_timer = 0
        self.boss_awake = False
        self.messages = ["Algo se mueve entre las sombras..."]
        self.random = random.Random(17)

    def say(self, message):
        self.messages.append(message)
        self.messages = self.messages[-3:]

    def attack(self, mouse):
        if self.state != "play" or self.attack_timer > 0 or self.stun_timer > 0:
            return
        self.attack_timer = 0.42
        target = pygame.Vector2(mouse)
        delta = target - self.player
        if delta.length_squared() == 0:
            return
        direction = delta.normalize()
        # Distancia al borde del cuerpo 2x2, no al centro.
        closest = pygame.Vector2(
            clamp(self.player.x, self.boss.x - CELL, self.boss.x + CELL),
            clamp(self.player.y, self.boss.y - CELL, self.boss.y + CELL),
        )
        towards = closest - self.player
        if towards.length() <= 76 and (
            towards.length_squared() == 0 or direction.dot(towards.normalize()) > 0.35
        ):
            self.boss_hp = max(0, self.boss_hp - 25)
            self.say("Golpeas a la criatura. (-25)")
            return
        for m in self.minions[:]:
            towards = m - self.player
            if towards.length() < 68 and towards.length_squared() > 0 and direction.dot(towards.normalize()) > 0.35:
                self.minions.remove(m)
                self.say("Has derribado a un esbirro.")
                return

    def update(self, dt):
        dt = min(dt, 0.05)
        self.attack_timer = max(0, self.attack_timer - dt)
        self.boss_timer = max(0, self.boss_timer - dt)
        self.hit_flash = max(0, self.hit_flash - dt)
        self.stun_timer = max(0, self.stun_timer - dt)
        self.boss_attack_flash = max(0, self.boss_attack_flash - dt)
        if self.state == "intro":
            self.intro_timer -= dt
            if self.intro_timer <= 0:
                self.state = "play"
                self.say("La criatura te ha visto.")
            return
        if self.state != "play":
            return
        self.elapsed += dt
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if movement.length_squared() and self.stun_timer <= 0:
            self.player += movement.normalize() * 220 * dt
        self.player += self.knockback * dt
        self.knockback *= max(0, 1 - 5 * dt)
        self.player.x = clamp(self.player.x, CELL / 2, WIDTH - CELL / 2)
        self.player.y = clamp(self.player.y, CELL / 2, HEIGHT - CELL / 2)
        boss_speed = (75, 48, 48)[self.mode]
        boss_range = (77, 92, 68)[self.mode]
        move_towards(self.boss, self.player, boss_speed, dt)
        if distance(self.boss, self.player) < boss_range and self.boss_timer <= 0:
            self.boss_attack_flash = 0.24
            self.damage(48, self.boss)
            self.boss_timer = 1.15
        if self.mode == 2:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0 and len(self.minions) < 5:
                offset = pygame.Vector2(self.random.randint(-65, 65), self.random.randint(-65, 65))
                self.minions.append(self.boss + offset)
                self.spawn_timer = 2.4
            for m in self.minions:
                move_towards(m, self.player, 205, dt)
                if distance(m, self.player) < 25 and self.hit_flash <= 0:
                    self.damage(15, m)

    def damage(self, amount, attacker):
        if self.state != "play":
            return
        self.hp = max(0, self.hp - amount)
        self.hit_flash = 0.55
        self.stun_timer = 1.5
        away = self.player - attacker
        if away.length_squared():
            self.knockback = away.normalize() * 480
        self.say(f"Recibes {amount} de dano. Vida: {self.hp}/100")
        if self.hp == 0:
            self.reset(self.mode)
            self.say("Derrota: reaparicion inmediata en el inicio.")

    def draw_health_bar(self, center_x, top_y, current, maximum, width):
        # Contorno gris y relleno tenue, sin colores intensos.
        x = round(center_x - width / 2)
        y = round(top_y)
        pygame.draw.rect(self.screen, (185, 185, 185), (x, y, width, 6), 1)
        fill = max(0, round((width - 2) * current / maximum))
        if fill:
            pygame.draw.rect(self.screen, (218, 218, 218), (x + 1, y + 1, fill, 4))

    def draw(self):
        s = self.screen
        s.fill((250, 250, 250))
        # Playa rectangular: 20 x 10 celdas. Solo lineas monocromas.
        for x in range(0, WIDTH + 1, CELL):
            pygame.draw.line(s, (229, 229, 229), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT + 1, CELL):
            pygame.draw.line(s, (229, 229, 229), (0, y), (WIDTH, y), 1)
        # Jugador: capsula de 1 x 1 celda.
        px, py = round(self.player.x), round(self.player.y)
        pygame.draw.circle(s, (155, 155, 155), (px, py), CELL//2, 1)
        self.draw_health_bar(px, py - CELL//2 - 13, self.hp, 100, CELL)
        # Enemigo: cuadrado de 2 x 2 celdas.
        bx, by = round(self.boss.x), round(self.boss.y)
        pygame.draw.rect(s, (255, 255, 255),
                         (bx-CELL, by-CELL, CELL*2, CELL*2))
        pygame.draw.rect(s, (155, 155, 155),
                         (bx-CELL, by-CELL, CELL*2, CELL*2), 1)
        self.draw_health_bar(bx, by - CELL - 13, self.boss_hp, 999, CELL * 2)
        if self.boss_attack_flash > 0:
            pygame.draw.circle(s, (145, 145, 145), (bx, by),
                               round((77, 92, 68)[self.mode]), 1)
        for m in self.minions:
            pygame.draw.circle(s, (60, 60, 60),
                               (round(m.x), round(m.y)), CELL//4, 2)
        if self.attack_timer > 0.24:
            pygame.draw.circle(s, (155, 155, 155), (px, py), 55, 1)
        if self.hit_flash > 0:
            pygame.draw.rect(s, (30, 30, 30), (0, 0, WIDTH, HEIGHT), 5)
        pygame.draw.rect(s, (255, 255, 255), (4, 4, WIDTH-8, 45))
        s.blit(self.small.render(
            f"TEST 20x10 | Jugador 1x1 | Enemigo 2x2 | Variante {self.mode+1}: {MODES[self.mode]}",
            True, INK), (12, 8))
        s.blit(self.small.render(
            f"HP {self.hp}/100 | {'ATURDIDO' if self.stun_timer > 0 else 'LIBRE'} | WASD mover | Clic golpear | 1/2/3 variantes | R reiniciar",
            True, INK), (12, 28))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset(self.mode)
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.reset(event.key - pygame.K_1)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.attack(event.pos)
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    BeachTest().run()
