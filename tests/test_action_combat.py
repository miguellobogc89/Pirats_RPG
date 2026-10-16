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


if __name__ == "__main__":
    unittest.main()
