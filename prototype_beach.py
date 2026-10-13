"""Prototipo aislado: encuentro nocturno en la playa. Ejecutar: python prototype_beach.py"""
import math
import random
from pathlib import Path
import pygame

WIDTH, HEIGHT = 1000, 650
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
        self.player = pygame.Vector2(190, 355)
        self.boss = pygame.Vector2(800, 335)
        self.hp = 100
        self.boss_hp = 999
        self.attack_timer = 0
        self.boss_timer = 0
        self.hit_flash = 0
        self.knockback = pygame.Vector2()
        self.minions = []
        self.spawn_timer = 2.5
        self.elapsed = 0
        self.state = "intro"
        self.intro_timer = 2.5
        self.boss_awake = False
        self.messages = ["Algo se mueve entre las sombras..."]
        self.random = random.Random(17)

    def say(self, message):
        self.messages.append(message)
        self.messages = self.messages[-3:]

    def attack(self, mouse):
        if self.state != "play" or self.attack_timer > 0:
            return
        self.attack_timer = 0.42
        target = pygame.Vector2(mouse)
        delta = target - self.player
        if delta.length_squared() == 0:
            return
        direction = delta.normalize()
        towards = self.boss - self.player
        if towards.length() <= 76 and towards.length_squared() > 0 and direction.dot(towards.normalize()) > 0.35:
            self.boss_hp -= 1
            self.say("Golpeas a la criatura. Apenas reacciona. (-1)")
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
        if movement.length_squared():
            self.player += movement.normalize() * 220 * dt
        self.player += self.knockback * dt
        self.knockback *= max(0, 1 - 9 * dt)
        self.player.x = clamp(self.player.x, 52, WIDTH - 48)
        self.player.y = clamp(self.player.y, 152, HEIGHT - 53)
        boss_speed = (165, 105, 105)[self.mode]
        boss_range = (77, 92, 68)[self.mode]
        move_towards(self.boss, self.player, boss_speed, dt)
        if distance(self.boss, self.player) < boss_range and self.boss_timer <= 0:
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
        away = self.player - attacker
        if away.length_squared():
            self.knockback = away.normalize() * 140
        self.say(f"Recibes {amount} de dano. Vida: {self.hp}/100")
        if self.hp == 0:
            self.state = "dead"
            self.say("La criatura te deja sin sentido...")

    def draw(self):
        s = self.screen
        s.fill((248, 248, 248))
        # Plano abstracto de pruebas: geometria monocroma, sin texturas ni sprites.
        pygame.draw.rect(s, (232, 232, 232), (0, 75, WIDTH, 75))
        pygame.draw.line(s, (65, 65, 65), (0, 150), (WIDTH, 150), 2)
        pygame.draw.polygon(s, (220, 220, 220),
                            [(WIDTH-150, 150), (WIDTH, 150), (WIDTH, HEIGHT-75),
                             (WIDTH-115, HEIGHT-75), (WIDTH-185, 455)])
        pygame.draw.lines(s, (80, 80, 80), False,
                          [(WIDTH-150, 150), (WIDTH-185, 455),
                           (WIDTH-115, HEIGHT-75)], 2)
        # El protagonista es una capsula vertical.
        px, py = round(self.player.x), round(self.player.y)
        pygame.draw.rect(s, (35, 35, 35), (px-12, py-22, 24, 44), border_radius=12)
        pygame.draw.circle(s, (255, 255, 255), (px, py-8), 3)
        # La criatura es un circulo grande con contorno, no un personaje.
        bx, by = round(self.boss.x), round(self.boss.y)
        pygame.draw.circle(s, (35, 35, 35), (bx, by), 32, 3)
        pygame.draw.circle(s, (35, 35, 35), (bx, by), 8)
        for m in self.minions:
            pygame.draw.circle(s, (95, 95, 95), (round(m.x), round(m.y)), 12, 2)
        if self.attack_timer > 0.24 and self.state == "play":
            pygame.draw.circle(s, (110, 110, 110), (px, py), 55, 2)
        if self.hit_flash > 0:
            pygame.draw.rect(s, (40, 40, 40), (0, 0, WIDTH, HEIGHT), 5)
        pygame.draw.rect(s, (245, 245, 245), (0, 0, WIDTH, 75))
        pygame.draw.line(s, (50, 50, 50), (0, 74), (WIDTH, 74), 1)
        s.blit(self.font.render("TEST / PERSECUCION", True, INK), (20, 10))
        s.blit(self.small.render(f"Variante {self.mode+1}: {MODES[self.mode]}   |   1/2/3 cambiar   R reiniciar", True, INK), (20, 40))
        pygame.draw.rect(s, (255, 255, 255), (WIDTH-250, 19, 212, 22))
        pygame.draw.rect(s, (40, 40, 40), (WIDTH-250, 19, 212, 22), 1)
        pygame.draw.rect(s, (50, 50, 50), (WIDTH-247, 22, int(206*self.hp/100), 16))
        s.blit(self.small.render(f"HP {self.hp}/100", True, INK), (WIDTH-245, 45))
        pygame.draw.rect(s, (245, 245, 245), (0, HEIGHT-75, WIDTH, 75))
        pygame.draw.line(s, (50, 50, 50), (0, HEIGHT-75), (WIDTH, HEIGHT-75), 1)
        for i, message in enumerate(self.messages[-2:]):
            s.blit(self.small.render(message, True, INK), (20, HEIGHT-67+i*22))
        s.blit(self.small.render("WASD / flechas: mover | Clic: golpe | ESC: salir", True, INK), (WIDTH-485, HEIGHT-25))
        if self.state in ("intro", "dead"):
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 218))
            s.blit(overlay, (0, 0))
            lines = (["SE DETECTA UNA PRESENCIA", "La persecucion comienza..."] if self.state == "intro" else
                     ["FIN DE LA PRUEBA", "El jugador ha sido derrotado.",
                      "R: repetir  |  1/2/3: cambiar variante"])
            for i, line in enumerate(lines):
                img = self.font.render(line, True, (25, 25, 25))
                s.blit(img, img.get_rect(center=(WIDTH//2, HEIGHT//2+i*34)))
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
