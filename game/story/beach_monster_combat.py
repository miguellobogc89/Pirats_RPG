"""Beach prologue adapter: sleeping monster, stones, and shared combat AI."""
import math

from game.combat.action.engine import CombatWorld, Fighter
from game.combat.action.components import StealthConfig
from game.combat.action.ground_throw import GroundThrow
from game.combat.action.stealth import Obstacle, segment_hits_rect


class BeachMonsterCombat:
    REQUIRED_HITS = 3

    def __init__(self, player_x, player_y, monster_x=490, monster_y=560,
                 obstacles=()):
        self.world = CombatWorld(width=704, height=704)
        self.world.obstacles = [
            Obstacle(float(box.x), float(box.y), float(box.width), float(box.height))
            for box in obstacles
        ]
        self.player = self.world.add(Fighter(
            "beach_player", "player", player_x, player_y,
            hp=1, max_hp=1, radius=14, brain_enabled=False,
        ))
        self.monster = self.world.add(Fighter(
            "beach_monster", "monster", monster_x, monster_y,
            hp=999, max_hp=999, radius=40, speed=42,
            damage=1, reach=62, aggro_radius=160,
            attack_cooldown=1.2, brain_enabled=False,
            stealth=StealthConfig(),
        ))
        self.monster.facing_x, self.monster.facing_y = 0, 1
        self.throwing = GroundThrow()
        self.stone_hits = 0
        self.sleep_reaction = 0.0
        self.last_stone_event = ""
        self.impact_effects = []

    def update(self, dt, player_x, player_y):
        self.player.x, self.player.y = player_x, player_y
        old_positions = [(stone, stone.x, stone.y) for stone in self.throwing.projectiles]
        self.throwing.tick(dt)
        self.last_stone_event = ""
        for stone, old_x, old_y in old_positions:
            if stone not in self.throwing.projectiles:
                continue
            if any(segment_hits_rect(old_x, old_y, stone.x, stone.y, box)
                   for box in self.world.obstacles):
                self.throwing.projectiles.remove(stone)
                self.last_stone_event = "obstacle"
                continue
            dx, dy = stone.x - old_x, stone.y - old_y
            den = dx * dx + dy * dy
            t = max(0, min(1, ((self.monster.x - old_x) * dx +
                                (self.monster.y - old_y) * dy) / den)) if den else 0
            closest = (old_x + t * dx, old_y + t * dy)
            if math.dist(closest, (self.monster.x, self.monster.y)) <= self.monster.radius + 6:
                self.throwing.projectiles.remove(stone)
                if self.stone_hits < self.REQUIRED_HITS:
                    self.stone_hits += 1
                    self.sleep_reaction = 0.9
                    self.last_stone_event = "woken" if self.stone_hits == self.REQUIRED_HITS else "hit"
                    if self.stone_hits == self.REQUIRED_HITS:
                        self.monster.brain_enabled = True
                        self.monster.awake = True
                        self.monster.alert_state = "surprised"
                        self.monster.surprise_remaining = 0.8
                        self.monster.last_seen = (player_x, player_y)
                        self.world.events.append(
                            __import__("game.combat.action.engine", fromlist=["CombatEvent"]).CombatEvent(
                                "aggro", self.monster.id, self.player.id,
                                x=self.monster.x, y=self.monster.y, duration=0.8))
                else:
                    self.last_stone_event = "hit"
        self.sleep_reaction = max(0, self.sleep_reaction - dt)
        self.world.update(dt)
        events = self.world.consume_events()
        return events, not self.player.alive

    def hit_monster(self, damage=25):
        # Story boss cannot be killed before the scripted defeat.
        self.monster.hp = max(1, self.monster.hp - damage)
        return True
