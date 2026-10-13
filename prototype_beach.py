"""Prototipo aislado: encuentro nocturno en la playa. Ejecutar: python prototype_beach.py"""
import math
import random
from pathlib import Path
import pygame

WIDTH, HEIGHT = 1000, 650
FPS = 60
ROOT = Path(__file__).resolve().parent
SAND = (113, 109, 91)
SEA = (29, 65, 85)
INK = (224, 225, 205)
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
        path = ROOT / "assets" / "player" / "player_idle.png"
        self.sprite = None
        if path.exists():
            try:
                self.sprite = pygame.image.load(str(path)).convert_alpha()
                self.sprite = pygame.transform.smoothscale(self.sprite, (40, 48))
            except pygame.error:
                pass
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
        s.fill(SAND)
        pygame.draw.rect(s, SEA, (0, 0, WIDTH, 150))
        for i in range(11):
            x = i * 105
            pygame.draw.arc(s, (73, 106, 117), (x, 124, 125, 54), 0.1, 2.8, 2)
        pygame.draw.polygon(s, (72, 73, 65), [(WIDTH-150, 150), (WIDTH, 150), (WIDTH, HEIGHT), (WIDTH-115, HEIGHT), (WIDTH-185, 455)])
        for i in range(32):
            x = 55 + (i * 163) % 860
            y = 175 + (i * 97) % 420
            pygame.draw.circle(s, (137, 130, 108), (x, y), 3)
        for i in range(9):
            x = 70 + i * 97
            pygame.draw.line(s, (60, 86, 69), (x, 590), (x-6, 571), 3)
            pygame.draw.line(s, (60, 86, 69), (x, 590), (x+7, 575), 3)
        pygame.draw.circle(s, (32, 37, 43), self.boss, 33)
        pygame.draw.circle(s, (71, 79, 77), self.boss, 28)
        for off in (-11, 11):
            pygame.draw.circle(s, (214, 83, 70), (int(self.boss.x + off), int(self.boss.y - 7)), 5)
        for m in self.minions:
            pygame.draw.circle(s, (51, 54, 59), m, 14)
            pygame.draw.circle(s, (220, 104, 86), m + pygame.Vector2(3, -4), 3)
        if self.sprite:
            s.blit(self.sprite, (self.player.x - 20, self.player.y - 39))
        else:
            pygame.draw.circle(s, (95, 175, 180), self.player, 17)
        if self.attack_timer > 0.24 and self.state == "play":
            pygame.draw.circle(s, (245, 215, 142), self.player, 55, 3)
        if self.hit_flash > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((180, 35, 32, int(self.hit_flash * 70)))
            s.blit(overlay, (0, 0))
        pygame.draw.rect(s, (22, 29, 33), (0, 0, WIDTH, 74))
        s.blit(self.font.render("BRUMAZUL | ENCUENTRO NOCTURNO", True, INK), (20, 10))
        s.blit(self.small.render(f"Modo {self.mode+1}: {MODES[self.mode]}   |   1/2/3 cambiar   R reiniciar", True, INK), (20, 40))
        pygame.draw.rect(s, (57, 51, 51), (WIDTH-250, 19, 212, 22))
        pygame.draw.rect(s, (186, 68, 63), (WIDTH-246, 23, int(204 * self.hp / 100), 14))
        s.blit(self.small.render(f"VIDA {self.hp}/100", True, INK), (WIDTH-244, 45))
        pygame.draw.rect(s, (22, 29, 33), (0, HEIGHT-75, WIDTH, 75))
        for i, message in enumerate(self.messages[-2:]):
            s.blit(self.small.render(message, True, INK), (20, HEIGHT-67+i*22))
        s.blit(self.small.render("WASD/flechas mover | Clic izquierdo golpear | ESC salir", True, (170, 186, 183)), (WIDTH-480, HEIGHT-25))
        if self.state in ("intro", "dead"):
            shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shade.fill((8, 12, 20, 150))
            s.blit(shade, (0, 0))
            lines = (["Oyes pasos pesados en la arena...", "No estas solo."] if self.state == "intro" else
                     ["HAS CAIDO", "La criatura te da por muerto.", "Pulsa R para repetir o 1/2/3 para probar otra variante."])
            for i, line in enumerate(lines):
                img = self.font.render(line, True, (248, 235, 212))
                s.blit(img, img.get_rect(center=(WIDTH//2, HEIGHT//2 + i*34)))
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
