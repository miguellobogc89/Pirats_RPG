"""Motor de combate de accion independiente de Pygame y de las escenas.

Las reglas emiten eventos con posiciones y duraciones. Los adaptadores visuales
(Pygame, Unity) deciden como representarlos.
"""
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
    stamina: float = 100
    max_stamina: float = 100
    ranged_cooldown: float = 0
    dash_cooldown: float = 0
    dash_remaining: float = 0
    dash_x: float = 0
    dash_y: float = 0
    combo_step: int = 0
    combo_timer: float = 0

    @property
    def alive(self):
        return self.hp > 0


@dataclass
class CombatEvent:
    kind: str
    actor: str
    target: str = ""
    amount: int = 0
    x: float = 0
    y: float = 0
    duration: float = 0
    intensity: float = 0


@dataclass
class Projectile:
    owner: str
    team: str
    x: float
    y: float
    vx: float
    vy: float
    damage: int = 1
    radius: float = 6
    lifetime: float = 1.4


@dataclass
class CombatWorld:
    fighters: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    projectiles: list = field(default_factory=list)
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

    def dash(self, actor_id, direction=None):
        actor = self.fighters[actor_id]
        if not actor.alive or actor.stun > 0 or actor.dash_cooldown > 0 or actor.dash_remaining > 0 or actor.stamina < 24:
            return False
        dx, dy = direction if direction is not None else (actor.facing_x, actor.facing_y)
        length = math.hypot(dx, dy)
        if length < 1e-8:
            dx, dy, length = actor.facing_x, actor.facing_y, 1
        actor.dash_x, actor.dash_y = dx / length, dy / length
        actor.facing_x, actor.facing_y = actor.dash_x, actor.dash_y
        actor.dash_remaining = 0.17
        actor.dash_cooldown = 0.72
        actor.invulnerability = max(actor.invulnerability, 0.19)
        actor.stamina -= 24
        self.events.append(CombatEvent("dash", actor.id, x=actor.x, y=actor.y, duration=0.17))
        return True

    def shoot(self, actor_id, direction=None):
        actor = self.fighters[actor_id]
        if not actor.alive or actor.stun > 0 or actor.dash_remaining > 0 or actor.ranged_cooldown > 0 or actor.stamina < 12:
            return False
        dx, dy = direction if direction is not None else (actor.facing_x, actor.facing_y)
        length = math.hypot(dx, dy)
        if length < 1e-8:
            return False
        dx, dy = dx / length, dy / length
        actor.facing_x, actor.facing_y = dx, dy
        actor.ranged_cooldown = 0.75
        actor.stamina -= 12
        px, py = actor.x + dx * (actor.radius + 9), actor.y + dy * (actor.radius + 9)
        self.projectiles.append(Projectile(actor.id, actor.team, px, py, dx * 390, dy * 390))
        self.events.append(CombatEvent("shoot", actor.id, x=px, y=py))
        return True

    def attack(self, actor_id, direction=None, charged=False):
        actor = self.fighters[actor_id]
        if not actor.alive or actor.cooldown > 0 or actor.stun > 0 or actor.dash_remaining > 0:
            return False
        if direction is not None:
            dx, dy = direction
            magnitude = math.hypot(dx, dy)
            if magnitude:
                actor.facing_x, actor.facing_y = dx / magnitude, dy / magnitude
        if charged and actor.stamina < 28:
            return False
        if charged:
            actor.stamina -= 28
            actor.combo_step = 0
            actor.combo_timer = 0
            damage = actor.damage * 3
            reach = actor.reach * 1.3
            actor.cooldown = 0.85
        else:
            actor.combo_step = actor.combo_step % 3 + 1 if actor.combo_timer > 0 else 1
            actor.combo_timer = 1.0
            damage = actor.damage + (1 if actor.combo_step == 3 else 0)
            reach = actor.reach * (1.15 if actor.combo_step == 3 else 1)
            actor.cooldown = max(0.48, actor.attack_cooldown)
        self.events.append(CombatEvent("attack", actor.id, amount=actor.combo_step,
                                       x=actor.x, y=actor.y, duration=0.18 if charged else 0.12,
                                       intensity=2 if charged else 1))
        targets = []
        for target in self.fighters.values():
            if target.team == actor.team or not target.alive or target.id == actor.id:
                continue
            dx, dy = target.x - actor.x, target.y - actor.y
            distance = math.hypot(dx, dy)
            if distance > reach + target.radius:
                continue
            if distance and (dx * actor.facing_x + dy * actor.facing_y) / distance < 0.35:
                continue
            targets.append((distance, target))
        if targets:
            target = min(targets, key=lambda item: item[0])[1]
            if not self.damage(actor.id, target.id, damage):
                self.events.append(CombatEvent("blocked", actor.id, target.id,
                                               x=target.x, y=target.y,
                                               duration=0.22))
        else:
            self.events.append(CombatEvent("miss", actor.id, x=actor.x + actor.facing_x * reach,
                                           y=actor.y + actor.facing_y * reach,
                                           duration=0.18))
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
        target.stun = 0.16 if target.alive else 0
        dx, dy = target.x - source.x, target.y - source.y
        distance = math.hypot(dx, dy)
        if distance:
            target.knockback_x, target.knockback_y = dx / distance * 115, dy / distance * 115
        else:
            target.knockback_x, target.knockback_y = source.facing_x * 115, source.facing_y * 115
        # Los eventos describen el impacto sin depender de Pygame ni del framerate.
        self.events.append(CombatEvent("hit", source_id, target_id, amount,
                                       target.x, target.y, 0.11, min(1.8, 0.65 + amount * 0.14)))
        self.events.append(CombatEvent("invulnerability", target.id, duration=0.45,
                                       x=target.x, y=target.y))
        if target.alive:
            self.events.append(CombatEvent("stun", target.id, duration=target.stun,
                                           x=target.x, y=target.y))
        else:
            target.windup = 0
            self.events.append(CombatEvent("death", source_id, target_id,
                                           x=target.x, y=target.y, intensity=1.4))
        return True

    def update(self, dt):
        if dt < 0:
            raise ValueError("dt no puede ser negativo")
        remaining = dt
        while remaining > 0:
            step = min(remaining, 0.05)
            self._step(step)
            remaining -= step

    def _step(self, dt):
        for actor in self.fighters.values():
            actor.cooldown = max(0, actor.cooldown - dt)
            actor.ranged_cooldown = max(0, actor.ranged_cooldown - dt)
            actor.dash_cooldown = max(0, actor.dash_cooldown - dt)
            actor.combo_timer = max(0, actor.combo_timer - dt)
            actor.stamina = min(actor.max_stamina, actor.stamina + 19 * dt)
            if actor.dash_remaining > 0 and actor.alive:
                duration = min(dt, actor.dash_remaining)
                actor.x = min(self.width - actor.radius, max(actor.radius, actor.x + actor.dash_x * 650 * duration))
                actor.y = min(self.height - actor.radius, max(actor.radius, actor.y + actor.dash_y * 650 * duration))
                actor.dash_remaining = max(0, actor.dash_remaining - dt)
            actor.invulnerability = max(0, actor.invulnerability - dt)
            actor.stun = max(0, actor.stun - dt)
            if actor.alive:
                actor.x = min(self.width - actor.radius, max(actor.radius, actor.x + actor.knockback_x * dt))
                actor.y = min(self.height - actor.radius, max(actor.radius, actor.y + actor.knockback_y * dt))
            actor.knockback_x *= max(0, 1 - 8 * dt)
            actor.knockback_y *= max(0, 1 - 8 * dt)
        for projectile in self.projectiles[:]:
            old_x, old_y = projectile.x, projectile.y
            projectile.x += projectile.vx * dt
            projectile.y += projectile.vy * dt
            projectile.lifetime -= dt
            struck = False
            for target in self.fighters.values():
                if not target.alive or target.team == projectile.team:
                    continue
                vx, vy = projectile.x - old_x, projectile.y - old_y
                denominator = vx * vx + vy * vy
                fraction = max(0, min(1, ((target.x - old_x) * vx + (target.y - old_y) * vy) / denominator)) if denominator else 0
                cx, cy = old_x + vx * fraction, old_y + vy * fraction
                if math.hypot(target.x - cx, target.y - cy) <= target.radius + projectile.radius:
                    if not self.damage(projectile.owner, target.id, projectile.damage):
                        self.events.append(CombatEvent("blocked", projectile.owner, target.id, x=target.x, y=target.y))
                    struck = True
                    break
            if struck or projectile.lifetime <= 0 or not (0 <= projectile.x <= self.width and 0 <= projectile.y <= self.height):
                self.projectiles.remove(projectile)
                if not struck:
                    self.events.append(CombatEvent("projectile_end", projectile.owner, x=projectile.x, y=projectile.y))
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
                self.events.append(CombatEvent("aggro", actor.id, target.id,
                                               x=actor.x, y=actor.y))
            if not actor.awake:
                continue
            if actor.windup > 0:
                actor.windup = max(0, actor.windup - dt)
                if actor.windup == 0 and target.alive:
                    if math.hypot(target.x - actor.x, target.y - actor.y) <= actor.reach + target.radius:
                        if not self.damage(actor.id, target.id, actor.damage):
                            self.events.append(CombatEvent("blocked", actor.id, target.id,
                                                           x=target.x, y=target.y,
                                                           duration=0.22))
                    else:
                        self.events.append(CombatEvent("miss", actor.id,
                                                       x=actor.x + actor.facing_x * actor.reach,
                                                       y=actor.y + actor.facing_y * actor.reach,
                                                       duration=0.18))
                continue
            if actor.stun > 0 or actor.dash_remaining > 0:
                continue
            if distance > 0:
                actor.facing_x, actor.facing_y = dx / distance, dy / distance
            if distance <= actor.reach + target.radius:
                if actor.cooldown == 0:
                    actor.cooldown = actor.attack_cooldown
                    actor.windup = 0.22
                    self.events.append(CombatEvent("telegraph", actor.id, target.id,
                                                   x=actor.x, y=actor.y, duration=0.22))
            elif distance > 0:
                self.move(actor.id, dx, dy, dt)
