"""Prototipo aislado: encuentro nocturno en la playa. Ejecutar: python prototype_beach.py"""
import math
import random
from pathlib import Path
import pygame

CELL = 40
COLS, ROWS = 20, 20
WIDTH, HEIGHT = CELL * COLS, CELL * ROWS
VIEW_WIDTH, VIEW_HEIGHT = 720, 520
FPS = 60
CORRIDOR_LEFT = WIDTH // 2 - CELL * 1.5
CORRIDOR_RIGHT = WIDTH // 2 + CELL * 1.5
CORRIDOR_TOP = 0
CORRIDOR_BOTTOM = CELL * 10
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
        self.screen = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT))
        self.world_surface = pygame.Surface((WIDTH, HEIGHT))
        pygame.display.set_caption("Pirats RPG | Prueba de persecucion nocturna")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 19)
        self.small = pygame.font.SysFont("consolas", 15)
        self.reset(0)

    def reset(self, mode):
        self.mode = mode
        self.player = pygame.Vector2(CELL * 10, CELL * 17)
        self.boss = pygame.Vector2(CELL * 15, CELL * 16)
        self.hp = 100
        self.boss_hp = 999
        self.attack_timer = 0
        self.boss_timer = 0
        self.boss_charge = 0
        self.invulnerability_timer = 0
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
        self.boss_activation_range = CELL * 4
        self.in_corridor = False
        self.gate_reached = False
        self.boss_in_corridor = False
        self.messages = ["Algo se mueve entre las sombras..."]
        self.random = random.Random(17)
        self.fade_timer = 0

    def enter_inn(self):
        """Primer nodo de progresion: la derrota nocturna lleva a la posada."""
        self.state = "inn"
        self.hp = 100
        self.player = pygame.Vector2(WIDTH / 2, HEIGHT / 2 + CELL)
        self.elder = pygame.Vector2(WIDTH / 2 + CELL * 2, HEIGHT / 2)
        self.fade_timer = 1.4
        self.messages = ["Amanece en la posada de Brumazul.", "Un anciano espera junto a tu cama."]

    def say(self, message):
        self.messages.append(message)
        self.messages = self.messages[-3:]

    def attack(self, mouse):
        if self.state != "play" or self.attack_timer > 0 or self.stun_timer > 0:
            return
        self.attack_timer = 0.42
        target = pygame.Vector2(mouse) - self.camera_offset()
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
        self.invulnerability_timer = max(0, self.invulnerability_timer - dt)
        self.boss_attack_flash = max(0, self.boss_attack_flash - dt)
        if self.state == "intro":
            self.intro_timer -= dt
            if self.intro_timer <= 0:
                self.state = "play"
                self.say("La criatura te ha visto.")
            return
        if self.state == "inn":
            self.fade_timer = max(0, self.fade_timer - dt)
            keys = pygame.key.get_pressed()
            movement = pygame.Vector2(
                int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
            )
            if movement.length_squared():
                self.player += movement.normalize() * 220 * dt
            self.player.x = clamp(self.player.x, CELL * 5.5, CELL * 14.5)
            self.player.y = clamp(self.player.y, CELL * 5.5, CELL * 14.5)
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
        # Pasillo estrecho: los laterales son paredes reales.
        if self.player.y < CORRIDOR_BOTTOM + CELL / 2:
            self.player.x = clamp(self.player.x, CORRIDOR_LEFT + CELL / 2,
                                  CORRIDOR_RIGHT - CELL / 2)
            self.in_corridor = True
            if self.player.y <= CELL / 2 and not self.gate_reached:
                self.gate_reached = True
                self.say("La puerta esta cerrada. No hay salida.")
        else:
            self.in_corridor = False
        if not self.boss_awake:
            if distance(self.player, self.boss) <= self.boss_activation_range:
                self.boss_awake = True
                self.say("La criatura despierta y comienza a perseguirte.")
            else:
                return
        boss_speed = (42, 27, 27)[self.mode]
        boss_range = (77, 92, 68)[self.mode]
        # En el pasillo actua como portero: iguala la X del jugador
        # mientras avanza lentamente hacia la puerta para cerrarle el paso.
        if self.in_corridor or self.boss.y < CORRIDOR_BOTTOM:
            self.boss_in_corridor = True
        if self.boss_charge > 0:
            self.boss_charge = max(0, self.boss_charge - dt)
            if self.boss_charge == 0:
                self.boss_timer = 1.6
                self.boss_attack_flash = 0.24
                if distance(self.boss, self.player) < boss_range:
                    self.damage(20, self.boss)
        else:
            if self.boss_in_corridor:
                target_x = clamp(self.player.x, CORRIDOR_LEFT + CELL,
                                 CORRIDOR_RIGHT - CELL)
                shift = target_x - self.boss.x
                self.boss.x += clamp(shift, -boss_speed * 1.6 * dt,
                                     boss_speed * 1.6 * dt)
                if self.boss.y > self.player.y:
                    self.boss.y -= min(self.boss.y - self.player.y, boss_speed * dt)
                elif self.boss.y < self.player.y:
                    self.boss.y += min(self.player.y - self.boss.y, boss_speed * dt)
            else:
                move_towards(self.boss, self.player, boss_speed, dt)
            if distance(self.boss, self.player) < boss_range and self.boss_timer <= 0:
                self.boss_charge = 0.5
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
        if self.state != "play" or self.invulnerability_timer > 0:
            return
        self.hp = max(0, self.hp - amount)
        self.hit_flash = 0.55
        self.stun_timer = 1.0
        self.invulnerability_timer = 1.4
        away = self.player - attacker
        if away.length_squared():
            self.knockback = away.normalize() * 480
        self.say(f"Recibes {amount} de dano. Vida: {self.hp}/100")
        if self.hp == 0:
            self.enter_inn()

    def camera_offset(self):
        # Camara centrada en el jugador, independiente de los limites del mapa.
        return pygame.Vector2(VIEW_WIDTH / 2 - self.player.x,
                              VIEW_HEIGHT / 2 - self.player.y)

    def draw_health_bar(self, center_x, top_y, current, maximum, width):
        # Contorno gris y relleno tenue, sin colores intensos.
        x = round(center_x - width / 2)
        y = round(top_y)
        pygame.draw.rect(self.world_surface, (185, 185, 185), (x, y, width, 6), 1)
        fill = max(0, round((width - 2) * current / maximum))
        if fill:
            pygame.draw.rect(self.world_surface, (218, 218, 218), (x + 1, y + 1, fill, 4))

    def draw_inn(self):
        s = self.world_surface
        s.fill((250, 250, 250))
        # Habitacion de posada en el mismo estilo de lineas finas.
        room = pygame.Rect(CELL * 5, CELL * 5, CELL * 10, CELL * 10)
        pygame.draw.rect(s, (245, 245, 245), room)
        for x in range(room.left, room.right + 1, CELL):
            pygame.draw.line(s, (231, 231, 231), (x, room.top), (x, room.bottom), 1)
        for y in range(room.top, room.bottom + 1, CELL):
            pygame.draw.line(s, (231, 231, 231), (room.left, y), (room.right, y), 1)
        pygame.draw.rect(s, (110, 110, 110), room, 2)
        # Cama, mesilla, mesa, sillas y puerta.
        pygame.draw.rect(s, (195, 195, 195), (CELL * 7, CELL * 10, CELL * 2, CELL * 3), 1)
        pygame.draw.rect(s, (215, 215, 215), (CELL * 7 + 5, CELL * 10 + 5, CELL * 2 - 10, CELL - 10), 1)
        pygame.draw.rect(s, (165, 165, 165), (CELL * 9, CELL * 11, CELL, CELL), 1)
        pygame.draw.rect(s, (165, 165, 165), (CELL * 12, CELL * 7, CELL * 2, CELL * 2), 1)
        pygame.draw.line(s, (250, 250, 250), (CELL * 11, room.bottom), (CELL * 13, room.bottom), 5)
        pygame.draw.arc(s, (145, 145, 145), (CELL * 11, room.bottom - CELL * 2, CELL * 2, CELL * 2), math.pi, math.pi * 1.5, 1)
        pygame.draw.circle(s, (110, 110, 110), (round(self.elder.x), round(self.elder.y)), CELL // 2, 2)
        label = self.small.render("ANCIANO", True, INK)
        s.blit(label, (round(self.elder.x) - label.get_width() // 2, round(self.elder.y) - 40))
        pygame.draw.circle(s, (155, 155, 155), (round(self.player.x), round(self.player.y)), CELL // 2, 1)
        self.screen.fill((225, 225, 225))
        offset = self.camera_offset()
        self.screen.blit(s, (round(offset.x), round(offset.y)))
        pygame.draw.rect(self.screen, (255, 255, 255), (4, 4, VIEW_WIDTH - 8, 67))
        self.screen.blit(self.small.render("CAPITULO 1 | BRUMAZUL - POSADA | AMANECER", True, INK), (12, 9))
        self.screen.blit(self.small.render("Despiertas en una cama. Un anciano te observa. WASD mover | Esc salir", True, INK), (12, 30))
        if distance(self.player, self.elder) < CELL * 2:
            self.screen.blit(self.small.render("El anciano: Por fin despiertas... [Dialogo pendiente]", True, INK), (12, 50))
        if self.fade_timer > 0:
            overlay = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(round(255 * min(1, self.fade_timer / 1.4)))
            self.screen.blit(overlay, (0, 0))
        pygame.display.flip()

    def draw(self):
        if self.state == "inn":
            self.draw_inn()
            return
        s = self.world_surface
        s.fill((250, 250, 250))
        # Playa rectangular: 20 x 10 celdas. Solo lineas monocromas.
        for x in range(0, WIDTH + 1, CELL):
            pygame.draw.line(s, (229, 229, 229), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT + 1, CELL):
            pygame.draw.line(s, (229, 229, 229), (0, y), (WIDTH, y), 1)
        # Pasillo vertical de cuatro celdas, con muros y puerta cerrada.
        pygame.draw.rect(s, (238, 238, 238),
                         (round(CORRIDOR_LEFT), 0, round(CORRIDOR_RIGHT - CORRIDOR_LEFT), CORRIDOR_BOTTOM))
        pygame.draw.line(s, (125, 125, 125), (CORRIDOR_LEFT, 0),
                         (CORRIDOR_LEFT, CORRIDOR_BOTTOM), 2)
        pygame.draw.line(s, (125, 125, 125), (CORRIDOR_RIGHT, 0),
                         (CORRIDOR_RIGHT, CORRIDOR_BOTTOM), 2)
        pygame.draw.line(s, (95, 95, 95), (CORRIDOR_LEFT, 4),
                         (CORRIDOR_RIGHT, 4), 3)
        # Jugador: circulo de 1 x 1 celda.
        px, py = round(self.player.x), round(self.player.y)
        if self.stun_timer <= 0 or int(self.stun_timer * 10) % 2 == 0:
            pygame.draw.circle(s, (155, 155, 155), (px, py), CELL//2, 1)
        self.draw_health_bar(px, py - CELL//2 - 13, self.hp, 100, CELL)
        # Enemigo: cuadrado de 2 x 2 celdas.
        bx, by = round(self.boss.x), round(self.boss.y)
        pygame.draw.rect(s, (255, 255, 255),
                         (bx-CELL, by-CELL, CELL*2, CELL*2))
        pygame.draw.rect(s, (155, 155, 155),
                         (bx-CELL, by-CELL, CELL*2, CELL*2), 1)
        self.draw_health_bar(bx, by - CELL - 13, self.boss_hp, 999, CELL * 2)
        if self.boss_charge > 0:
            inset = 10
            pygame.draw.rect(s, (135, 135, 135),
                             (bx-CELL+inset, by-CELL+inset,
                              CELL*2-inset*2, CELL*2-inset*2), 1)
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
        # La escena se desplaza bajo una camara fija sobre el jugador.
        self.screen.fill((225, 225, 225))
        offset = self.camera_offset()
        self.screen.blit(s, (round(offset.x), round(offset.y)))
        hud = self.screen
        pygame.draw.rect(hud, (255, 255, 255), (4, 4, VIEW_WIDTH-8, 45))
        hud.blit(self.small.render(
            f"TEST 20x20 | Jugador 1x1 | Enemigo 2x2 | Variante {self.mode+1}: {MODES[self.mode]}",
            True, INK), (12, 8))
        hud.blit(self.small.render(
            f"HP {self.hp}/100 | {'ATURDIDO' if self.stun_timer > 0 else 'LIBRE'} | WASD | Clic atacar | 1/2/3 | R | Esc salir",
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
