"""Pruebas sin Pygame: python -m unittest tests.test_action_combat"""
import unittest
from game.combat.action.engine import CombatWorld, Fighter


class ActionCombatTests(unittest.TestCase):
    def setUp(self):
        self.world = CombatWorld(width=500, height=500)
        self.world.add(Fighter("hero", "player", 100, 100, damage=2, reach=60))
        self.world.add(Fighter("rat", "enemy", 135, 100, hp=3, max_hp=3, speed=0, aggro_radius=0))

    def test_attack_direction_and_cooldown(self):
        self.assertTrue(self.world.attack("hero", (-1, 0)))
        self.assertEqual(self.world.fighters["rat"].hp, 3)
        self.assertFalse(self.world.attack("hero", (1, 0)))
        self.world.update(1)
        self.assertTrue(self.world.attack("hero", (1, 0)))
        self.assertEqual(self.world.fighters["rat"].hp, 1)

    def test_damage_invulnerability_and_death(self):
        self.assertTrue(self.world.damage("hero", "rat", 2))
        self.assertFalse(self.world.damage("hero", "rat", 2))
        self.world.update(0.5)
        self.assertTrue(self.world.damage("hero", "rat", 2))
        self.assertFalse(self.world.fighters["rat"].alive)
        self.assertIn("death", [e.kind for e in self.world.consume_events()])

    def test_enemy_chases_and_attacks(self):
        rat = self.world.fighters["rat"]
        rat.speed = 100
        rat.aggro_radius = 200
        rat.reach = 35
        self.world.update(1)
        self.assertLess(self.world.fighters["hero"].hp, 10)

    def test_normalized_movement_and_bounds(self):
        hero = self.world.fighters["hero"]
        self.world.move("hero", 1, 1, 0.5)
        self.assertAlmostEqual(hero.x - 100, hero.y - 100)
        self.world.move("hero", -1, 0, 100)
        self.assertEqual(hero.x, hero.radius)

    def test_hit_emits_portable_feedback_events(self):
        self.assertTrue(self.world.damage("hero", "rat", 2))
        events = self.world.consume_events()
        self.assertEqual([e.kind for e in events], ["hit", "invulnerability", "stun"])
        hit = events[0]
        self.assertEqual((hit.x, hit.y, hit.amount), (135, 100, 2))
        self.assertGreater(hit.duration, 0)
        self.assertGreater(hit.intensity, 0)
        self.assertEqual(events[1].duration, 0.45)
        self.assertEqual(events[2].duration, 0.16)

    def test_miss_and_invulnerable_target_are_distinct(self):
        self.world.attack("hero", (-1, 0))
        self.assertIn("miss", [e.kind for e in self.world.consume_events()])
        self.world.update(1)
        self.world.fighters["rat"].invulnerability = 0.3
        self.world.attack("hero", (1, 0))
        kinds = [e.kind for e in self.world.consume_events()]
        self.assertIn("blocked", kinds)
        self.assertNotIn("hit", kinds)

    def test_stun_prevents_movement_until_expired(self):
        hero = self.world.fighters["hero"]
        hero.stun = 0.16
        self.world.move("hero", 1, 0, 0.1)
        self.assertEqual(hero.x, 100)
        self.world.update(0.2)
        self.world.move("hero", 1, 0, 0.1)
        self.assertGreater(hero.x, 100)

    def test_knockback_moves_target(self):
        rat = self.world.fighters["rat"]
        self.world.damage("hero", "rat", 1)
        self.world.update(0.1)
        self.assertGreater(rat.x, 135)


if __name__ == "__main__":
    unittest.main()
