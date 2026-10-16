"""Motor de combate de accion sin dependencias de Pygame ni de escenas."""
from dataclasses import dataclass, field
import math


@dataclass
class Fighter:
    id: str
    team: str
    x: float
    y: float
    hp: int = 10
    max_hp: int = 10
    radius: float = 14
    speed: float = 85
    damage: int = 1
    reach: float = 42
    attack_cooldown: float = 0.65
    aggro_radius: float = 180
    invulnerability: float = 0
    stun: float = 0
    cooldown: float = 0
    facing_x: float = 1
    facing_y: float = 0
    awake: bool = False
    windup: float = 0
    attack_target: str = ""
    knockback_x: float = 0
    knockback_y: float = 0

    @property
    def alive(self):
        return self.hp > 0


@dataclass
class CombatEvent:
    kind: str
    actor: str
    target: str = ""
    amount: int = 0


@dataclass
class CombatWorld:
    fighters: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    width: float = 800
    height: float = 600

    def add(self, fighter):
        if fighter.id in self.fighters:
            raise ValueError("Fighter ID duplicado: " + fighter.id)
        self.fighters[fighter.id] = fighter
        return fighter

    def consume_events(self):
        events, self.events = self.events, []
        return events

    def move(self, actor_id, dx, dy, dt):
        actor = self.fighters[actor_id]
        if not actor.alive or actor.stun > 0:
            return
        length = math.hypot(dx, dy)
        if length:
            dx, dy = dx / length, dy / length
            actor.facing_x, actor.facing_y = dx, dy
            actor.x = min(self.width - actor.radius, max(actor.radius, actor.x + dx * actor.speed * dt))
            actor.y = min(self.height - actor.radius, max(actor.radius, actor.y + dy * actor.speed * dt))

    def attack(self, actor_id, direction=None):
        actor = self.fighters[actor_id]
        if not actor.alive or actor.cooldown > 0 or actor.stun > 0:
            return False
        if direction is not None:
            dx, dy = direction
            magnitude = math.hypot(dx, dy)
            if magnitude:
                actor.facing_x, actor.facing_y = dx / magnitude, dy / magnitude
        actor.cooldown = actor.attack_cooldown
        self.events.append(CombatEvent("attack", actor.id))
        targets = []
        for target in self.fighters.values():
            if target.team == actor.team or not target.alive or target.id == actor.id:
                continue
            dx, dy = target.x - actor.x, target.y - actor.y
            distance = math.hypot(dx, dy)
            if distance > actor.reach + target.radius:
                continue
            if distance and (dx * actor.facing_x + dy * actor.facing_y) / distance < 0.35:
                continue
            targets.append((distance, target))
        if targets:
            target = min(targets, key=lambda item: item[0])[1]
            self.damage(actor.id, target.id, actor.damage)
        return True

    def damage(self, source_id, target_id, amount):
        source, target = self.fighters[source_id], self.fighters[target_id]
        if not source.alive or not target.alive or target.invulnerability > 0:
            return False
        amount = max(0, int(amount))
        if amount == 0:
            return False
        target.hp = max(0, target.hp - amount)
        target.invulnerability = 0.45
        target.stun = 0.16
        dx, dy = target.x - source.x, target.y - source.y
        distance = math.hypot(dx, dy)
        if distance:
            target.knockback_x, target.knockback_y = dx / distance * 115, dy / distance * 115
        self.events.append(CombatEvent("hit", source_id, target_id, amount))
        if not target.alive:
            target.windup = 0
            self.events.append(CombatEvent("death", source_id, target_id))
        return True

    def update(self, dt):
        if dt < 0:
            raise ValueError("dt no puede ser negativo")
        # Limitar el salto de simulacion evita atravesar objetivos por un frame lento.
        remaining = dt
        while remaining > 0:
            step = min(remaining, 0.05)
            self._step(step)
            remaining -= step

    def _step(self, dt):
        for actor in self.fighters.values():
            actor.cooldown = max(0, actor.cooldown - dt)
            actor.invulnerability = max(0, actor.invulnerability - dt)
            actor.stun = max(0, actor.stun - dt)
            if actor.alive:
                actor.x = min(self.width - actor.radius, max(actor.radius, actor.x + actor.knockback_x * dt))
                actor.y = min(self.height - actor.radius, max(actor.radius, actor.y + actor.knockback_y * dt))
            actor.knockback_x *= max(0, 1 - 8 * dt)
            actor.knockback_y *= max(0, 1 - 8 * dt)
        for actor in list(self.fighters.values()):
            if not actor.alive or actor.team == "player":
                continue
            targets = [f for f in self.fighters.values() if f.alive and f.team != actor.team]
            if not targets:
                continue
            target = min(targets, key=lambda f: math.hypot(f.x - actor.x, f.y - actor.y))
            dx, dy = target.x - actor.x, target.y - actor.y
            distance = math.hypot(dx, dy)
            if distance <= actor.aggro_radius and not actor.awake:
                actor.awake = True
                self.events.append(CombatEvent("aggro", actor.id, target.id))
            if not actor.awake:
                continue
            if actor.windup > 0:
                actor.windup = max(0, actor.windup - dt)
                if actor.windup == 0 and target.alive:
                    if math.hypot(target.x - actor.x, target.y - actor.y) <= actor.reach + target.radius:
                        self.damage(actor.id, target.id, actor.damage)
                continue
            if actor.stun > 0:
                continue
            if distance > 0:
                actor.facing_x, actor.facing_y = dx / distance, dy / distance
            if distance <= actor.reach + target.radius:
                if actor.cooldown == 0:
                    actor.cooldown = actor.attack_cooldown
                    actor.windup = 0.22
                    self.events.append(CombatEvent("telegraph", actor.id, target.id))
            elif distance > 0:
                self.move(actor.id, dx, dy, dt)
