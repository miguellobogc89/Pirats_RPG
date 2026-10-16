"""Pruebas del encuentro de playa sin Pygame ni guardados."""
import unittest

from game.story.beach_monster_combat import BeachMonsterCombat


class BeachMonsterCombatTests(unittest.TestCase):
    def test_monster_uses_existing_combat_brain(self):
        encounter = BeachMonsterCombat(490, 430)
        events, defeated = encounter.update(0.3, 490, 430)
        self.assertTrue(encounter.monster.awake)
        self.assertFalse(defeated)
        self.assertTrue(any(event.kind == "aggro" for event in events))

    def test_monster_does_not_know_player_outside_aggro_range(self):
        encounter = BeachMonsterCombat(100, 100)
        start = (encounter.monster.x, encounter.monster.y)
        encounter.update(0.5, 100, 100)
        self.assertFalse(encounter.monster.awake)
        self.assertEqual(start, (encounter.monster.x, encounter.monster.y))

    def test_existing_telegraph_and_hit_lead_to_scripted_defeat(self):
        encounter = BeachMonsterCombat(490, 500)
        events = []
        defeated = False
        for _ in range(50):
            new_events, defeated = encounter.update(0.05, 490, 500)
            events.extend(event.kind for event in new_events)
            if defeated:
                break
        self.assertIn("telegraph", events)
        self.assertIn("hit", events)
        self.assertTrue(defeated)

    def test_prologue_monster_cannot_be_killed(self):
        encounter = BeachMonsterCombat(490, 430)
        encounter.hit_monster(10000)
        self.assertEqual(encounter.monster.hp, 1)
        self.assertTrue(encounter.monster.alive)


if __name__ == "__main__":
    unittest.main()
