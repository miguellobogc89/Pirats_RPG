"""Reusable one-object-in-hand pickup/charge/throw mechanic, no inventory."""
from dataclasses import dataclass
import math
import random


@dataclass
class ThrownObject:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float = 1.2


class GroundThrow:
    CHARGE_SECONDS = 1.2

    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.held = False
        self.charging = False
        self.charge = 0.0
        self.first_pickup = True
        self.failures = {}
        self.depleted = set()
        self.projectiles = []

    @staticmethod
    def terrain(x, y):
        # Beach test layout: visible pebble strip at the west side.
        return "rocky" if 70 <= x <= 230 and 350 <= y <= 465 else "sand"

    def pickup(self, x, y, terrain=None):
        if self.held:
            return "already_held"
        kind = terrain or self.terrain(x, y)
        if kind == "none":
            return "empty"
        cell = (int(x // 70), int(y // 70))
        if kind != "rocky" and cell in self.depleted:
            return "empty"
        if self.first_pickup:
            found = True
        elif kind == "rocky":
            found = True
        else:
            failed = self.failures.get(cell, 0)
            found = failed >= 3 or self.rng.random() < 0.4
        if not found:
            self.failures[cell] = self.failures.get(cell, 0) + 1
            return "empty"
        self.first_pickup = False
        self.held = True
        self.failures[cell] = 0
        # A patch yields one pickup; walking to another patch is necessary.
        if kind != "rocky":
            self.depleted.add(cell)
        return "picked"

    def start_charge(self):
        if not self.held:
            return False
        self.charging = True
        self.charge = 0
        return True

    def tick(self, dt):
        if self.charging:
            self.charge = min(1.0, self.charge + dt / self.CHARGE_SECONDS)
        for stone in self.projectiles[:]:
            stone.x += stone.vx * dt
            stone.y += stone.vy * dt
            stone.lifetime -= dt
            if stone.lifetime <= 0:
                self.projectiles.remove(stone)

    def throw(self, x, y, aim_x, aim_y):
        if not self.charging or not self.held:
            return False
        dx, dy = aim_x - x, aim_y - y
        length = math.hypot(dx, dy)
        if length < 1:
            dx, dy, length = 0, -1, 1
        speed = 150 + self.charge * 340
        self.projectiles.append(ThrownObject(x, y, dx / length * speed,
                                             dy / length * speed,
                                             lifetime=0.48 + self.charge * 0.24))
        self.held = False
        self.charging = False
        self.charge = 0
        return True

    def cancel(self):
        self.charging = False
        self.charge = 0
