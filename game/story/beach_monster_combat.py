"""Beach prologue adapter: sleeping monster, stones, and shared combat AI."""
import math

from game.combat.action.engine import CombatWorld, Fighter, CombatEvent
from game.combat.action.components import StealthConfig
from game.combat.action.ground_throw import GroundThrow
from game.combat.action.feedback import CombatFeedback
from game.combat.action.stealth import Obstacle, segment_hits_rect


class BeachMonsterCombat:
    REQUIRED_HITS = 3

    def __init__(self, player_x, player_y, monster_x=400, monster_y=255,
                 obstacles=(), width=704, height=704, stone_field=None):
        self.world = CombatWorld(width=width, height=height)
        self.world.obstacles = [
            Obstacle(float(box.x), float(box.y), float(box.width), float(box.height))
            for box in obstacles
        ]
        self.player = self.world.add(Fighter(
            "beach_player", "player", player_x, player_y,
            hp=6, max_hp=6, radius=14, brain_enabled=False,
        ))
        self.monster = self.world.add(Fighter(
            "beach_monster", "monster", monster_x, monster_y,
            hp=120, max_hp=120, radius=40, speed=42,
            damage=2, reach=62, aggro_radius=160,
            attack_cooldown=1.2, brain_enabled=False,
            stealth=StealthConfig(),
        ))
        self.monster.facing_x, self.monster.facing_y = 0, 1
        self.throwing = GroundThrow()
        if stone_field:
            self.throwing.rocky_rect = tuple(stone_field)
        self.stone_hits = 0
        self.sleep_reaction = 0.0
        self.last_stone_event = ""
        self.feedback = CombatFeedback()

    def player_attack(self, direction):
        if not self.monster.brain_enabled:
            return False
        return self.world.attack(self.player.id, direction)

    def player_dash(self, direction=None):
        return self.world.dash(self.player.id, direction)

    def update(self, dt, player_x, player_y):
        # External movement controls the player; engine knockback is applied back to the scene.
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
                if not self.monster.brain_enabled and self.stone_hits < self.REQUIRED_HITS:
                    self.stone_hits += 1
                    self.sleep_reaction = 0.9
                    self.last_stone_event = "woken" if self.stone_hits == self.REQUIRED_HITS else "hit"
                    if self.stone_hits == self.REQUIRED_HITS:
                        self.monster.brain_enabled = True
                        self.monster.awake = True
                        self.monster.alert_state = "surprised"
                        self.monster.surprise_remaining = 0.8
                        self.monster.last_seen = (player_x, player_y)
                        self.world.events.append(CombatEvent(
                            "aggro", self.monster.id, self.player.id,
                            x=self.monster.x, y=self.monster.y, duration=0.8))
                else:
                    self.world.damage(self.player.id, self.monster.id, 4)
                    self.last_stone_event = "combat_hit"
        self.sleep_reaction = max(0, self.sleep_reaction - dt)
        self.world.update(dt)
        events = self.world.consume_events()
        for event in events:
            self.feedback.handle(event, self.world)
        self.feedback.update(dt)
        return events, not self.player.alive

    def hit_monster(self, damage=25):
        # Story boss cannot be killed before the scripted defeat.
        if not self.monster.brain_enabled:
            return False
        if self.monster.invulnerability > 0:
            return False
        # Reuse combat hit, flash, knockback and damage events.
        if self.monster.hp <= damage:
            damage = max(0, self.monster.hp - 1)
        return self.world.damage(self.player.id, self.monster.id, damage)
