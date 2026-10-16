"""Beach prologue tests: one stone in hand, pickup odds, sleeping boss."""
import random
import unittest

from game.combat.action.ground_throw import GroundThrow
from game.story.beach_monster_combat import BeachMonsterCombat
from game.combat.action.stealth import Obstacle


class GroundThrowTests(unittest.TestCase):
    def test_one_held_stone_without_inventory(self):
        mechanic = GroundThrow(random.Random(0))
        self.assertEqual(mechanic.pickup(350, 560), "picked")
        self.assertEqual(mechanic.pickup(350, 560), "already_held")
        self.assertTrue(mechanic.start_charge())
        mechanic.tick(1.2)
        self.assertEqual(mechanic.charge, 1)
        self.assertTrue(mechanic.throw(350, 560, 490, 560))
        self.assertFalse(mechanic.held)
        self.assertEqual(len(mechanic.projectiles), 1)
        self.assertEqual(mechanic.pickup(350, 560), "empty")

    def test_rocky_pickup_is_guaranteed_and_cells_deplete(self):
        mechanic = GroundThrow(random.Random(0))
        mechanic.first_pickup = False
        self.assertEqual(mechanic.pickup(90, 400), "picked")
        mechanic.held = False
        self.assertEqual(mechanic.pickup(90, 400), "picked")
        self.assertEqual(mechanic.pickup(180, 400), "already_held")

    def test_sand_pity_after_three_failed_attempts(self):
        mechanic = GroundThrow(random.Random(0))
        mechanic.first_pickup = False
        for _ in range(3):
            self.assertEqual(mechanic.pickup(350, 560), "empty")
        self.assertEqual(mechanic.pickup(350, 560), "picked")


class BeachMonsterTests(unittest.TestCase):
    def test_monster_stays_dormant_until_three_hits(self):
        encounter = BeachMonsterCombat(350, 560)
        for _ in range(10):
            encounter.update(0.05, 350, 560)
        self.assertFalse(encounter.monster.awake)
        self.assertFalse(encounter.monster.brain_enabled)
        for i in range(3):
            encounter.throwing.held = True
            encounter.throwing.start_charge()
            encounter.throwing.tick(1.2)
            encounter.throwing.throw(350, 560, 400, 255)
            for _ in range(18):
                encounter.update(0.05, 350, 560)
            self.assertEqual(encounter.stone_hits, i + 1)
        self.assertTrue(encounter.monster.awake)
        self.assertTrue(encounter.monster.brain_enabled)
        encounter.throwing.held = True
        encounter.throwing.start_charge()
        encounter.throwing.tick(1.2)
        encounter.throwing.throw(350, 560, encounter.monster.x, encounter.monster.y)
        for _ in range(18):
            encounter.update(0.05, 350, 560)
        self.assertEqual(encounter.stone_hits, 3)

    def test_monster_obstacles_passed_to_world(self):
        box = Obstacle(390, 510, 40, 40)
        encounter = BeachMonsterCombat(350, 560, obstacles=[box])
        self.assertEqual(len(encounter.world.obstacles), 1)
        self.assertEqual(encounter.world.obstacles[0], box)

    def test_stone_stops_on_obstacle(self):
        box = Obstacle(360, 430, 50, 30)
        encounter = BeachMonsterCombat(350, 560, obstacles=[box])
        encounter.throwing.held = True
        encounter.throwing.start_charge()
        encounter.throwing.tick(1.2)
        encounter.throwing.throw(350, 560, 490, 560)
        for _ in range(12):
            encounter.update(0.05, 350, 560)
        self.assertEqual(encounter.stone_hits, 0)


if __name__ == "__main__":
    unittest.main()
