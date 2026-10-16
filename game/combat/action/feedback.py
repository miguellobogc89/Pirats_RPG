"""Presentacion Pygame de eventos de combate. No contiene reglas de daño.

Se puede sustituir por un adaptador de VFX en Unity sin cambiar engine.py.
"""
from dataclasses import dataclass
import math
import random
import pygame


@dataclass
class FloatingText:
    x: float
    y: float
    text: str
    color: tuple
    lifetime: float = 0.78
    age: float = 0


@dataclass
class Spark:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    color: tuple
    age: float = 0


class CombatFeedback:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.numbers = []
        self.sparks = []
        self.flashes = {}
        self.hitstop = 0.0
        self.shake = 0.0
        self.shake_time = 0.0
        self.slashes = []
        self.messages = []
        self.elapsed = 0.0

    def handle(self, event, world):
        if event.kind == "hit":
            target = world.fighters[event.target]
            player_hit = target.team == "player"
            color = (255, 113, 104) if player_hit else (255, 228, 127)
            self.numbers.append(FloatingText(event.x + self.rng.uniform(-9, 9),
                                             event.y - target.radius - 13,
                                             "-" + str(event.amount), color))
            self.flashes[event.target] = (0.14, (255, 96, 86) if player_hit else (255, 255, 239))
            self.hitstop = max(self.hitstop, event.duration)
            self.shake = max(self.shake, 6.5 * event.intensity)
            self.shake_time = max(self.shake_time, 0.16)
            self._burst(event.x, event.y, 13 + event.amount * 2, color)
        elif event.kind == "dash":
            self._burst(event.x, event.y, 12, (110, 225, 226), speed=95)
        elif event.kind == "shoot":
            self._burst(event.x, event.y, 8, (125, 202, 255), speed=85)
        elif event.kind == "death":
            self._burst(event.x, event.y, 23, (242, 143, 103))
            self.shake = max(self.shake, 9)
            self.shake_time = max(self.shake_time, 0.24)
        elif event.kind == "attack":
            actor = world.fighters[event.actor]
            self.slashes.append([actor.id, 0.15, 0.15])
        elif event.kind == "miss":
            self._burst(event.x, event.y, 3, (142, 164, 161), speed=45)
        elif event.kind == "blocked":
            self.numbers.append(FloatingText(event.x, event.y - 22, "INVULNERABLE",
                                             (171, 215, 235), lifetime=0.5))
            self._burst(event.x, event.y, 6, (164, 212, 245), speed=65)
        elif event.kind == "stun":
            self.messages.append([event.actor, "ATURDIDO", 0.28])
        elif event.kind == "aggro":
            self.messages.append([event.actor, "!", 0.65])

    def _burst(self, x, y, count, color, speed=165):
        for _ in range(count):
            angle = self.rng.uniform(0, math.tau)
            magnitude = self.rng.uniform(speed * 0.25, speed)
            self.sparks.append(Spark(x, y, math.cos(angle) * magnitude,
                                     math.sin(angle) * magnitude,
                                     self.rng.uniform(0.16, 0.48), color))

    def update(self, dt):
        """Los efectos siguen avanzando durante el hitstop (tiempo real)."""
        self.elapsed += dt
        self.hitstop = max(0, self.hitstop - dt)
        self.shake_time = max(0, self.shake_time - dt)
        if self.shake_time == 0:
            self.shake = 0
        for number in self.numbers:
            number.age += dt
            number.y -= dt * 40
        self.numbers = [n for n in self.numbers if n.age < n.lifetime]
        for spark in self.sparks:
            spark.age += dt
            spark.x += spark.vx * dt
            spark.y += spark.vy * dt
            spark.vx *= max(0, 1 - 4 * dt)
            spark.vy *= max(0, 1 - 4 * dt)
        self.sparks = [s for s in self.sparks if s.age < s.lifetime]
        for actor_id, (remaining, color) in list(self.flashes.items()):
            remaining -= dt
            if remaining <= 0:
                del self.flashes[actor_id]
            else:
                self.flashes[actor_id] = (remaining, color)
        for slash in self.slashes:
            slash[1] -= dt
        self.slashes = [s for s in self.slashes if s[1] > 0]
        for message in self.messages:
            message[2] -= dt
        self.messages = [m for m in self.messages if m[2] > 0]

    def offset(self):
        if not self.shake_time:
            return 0, 0
        scale = self.shake * min(1, self.shake_time / 0.12)
        return self.rng.randint(-round(scale), round(scale)), self.rng.randint(-round(scale), round(scale))

    def fighter_color(self, fighter, base):
        if fighter.id in self.flashes:
            return self.flashes[fighter.id][1]
        if fighter.invulnerability > 0 and int(self.elapsed * 15) % 2 == 0:
            return tuple(min(255, round(c * 0.55 + 100)) for c in base)
        return base

    def draw(self, surface, world, small_font, big_font):
        for slash in self.slashes:
            actor = world.fighters.get(slash[0])
            if actor is None:
                continue
            fraction = slash[1] / slash[2]
            direction = math.atan2(actor.facing_y, actor.facing_x)
            reach = actor.radius + actor.reach * 0.72
            center = (round(actor.x), round(actor.y))
            start = direction - 0.9 + (1 - fraction) * 0.4
            points = [(round(actor.x + math.cos(start + i * 0.12) * reach),
                       round(actor.y + math.sin(start + i * 0.12) * reach))
                      for i in range(13)]
            if len(points) > 1:
                pygame.draw.lines(surface, (244, 225, 164), False, points, max(1, round(4 * fraction)))
        for spark in self.sparks:
            fraction = 1 - spark.age / spark.lifetime
            pygame.draw.circle(surface, spark.color, (round(spark.x), round(spark.y)),
                               max(1, round(3 * fraction)))
        for number in self.numbers:
            text = big_font.render(number.text, True, number.color)
            surface.blit(text, (round(number.x - text.get_width() / 2), round(number.y)))
        for actor_id, message, _ in self.messages:
            fighter = world.fighters.get(actor_id)
            if fighter and fighter.alive:
                text = small_font.render(message, True, (253, 206, 116))
                surface.blit(text, (round(fighter.x - text.get_width() / 2),
                                    round(fighter.y - fighter.radius - 35)))
