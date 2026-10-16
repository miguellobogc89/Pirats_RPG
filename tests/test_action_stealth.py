"""Pruebas de la microfase 3.1, sin Pygame."""
import unittest
from game.combat.action.engine import CombatWorld, Fighter
from game.combat.action.stealth import Obstacle, can_see, line_of_sight


class StealthTests(unittest.TestCase):
    def setUp(self):
        self.world = CombatWorld(width=700, height=500, perception_enabled=True)
        self.guard = self.world.add(Fighter("guard", "enemy", 350, 200, speed=0,
                                            facing_x=-1, facing_y=0,
                                            vision_range=250, vision_angle=90,
                                            patrol_points=((350, 200),)))
        self.hero = self.world.add(Fighter("hero", "player", 170, 200))

    def test_forward_visible_and_behind_hidden(self):
        self.assertTrue(can_see(self.guard, self.hero, []))
        self.hero.x = 530
        self.assertFalse(can_see(self.guard, self.hero, []))

    def test_wall_blocks_vision(self):
        wall = Obstacle(245, 160, 45, 85)
        self.assertFalse(line_of_sight(350, 200, 170, 200, [wall]))
        self.assertFalse(can_see(self.guard, self.hero, [wall]) if self.hero.x == 170 else
                         can_see(self.guard, Fighter("target", "player", 170, 200), [wall]))

    def test_detection_requires_time_and_cover_breaks_progress(self):
        self.world.update(0.15)
        self.assertFalse(self.guard.awake)
        self.world.obstacles.append(Obstacle(245, 160, 45, 85))
        self.world.update(0.4)
        self.assertFalse(self.guard.awake)
        self.assertEqual(self.guard.detection, 0)
        self.world.obstacles.clear()
        self.world.update(0.3)
        self.assertTrue(self.guard.awake)
        self.assertEqual(self.guard.alert_state, "alert")

    def test_collision_blocks_movement_and_dash(self):
        self.world.obstacles.append(Obstacle(195, 150, 50, 100))
        self.world.move("hero", 1, 0, 0.1)
        self.assertLessEqual(self.hero.x, 195 - self.hero.radius)
        self.world.dash("hero", (1, 0))
        self.world.update(0.2)
        self.assertLessEqual(self.hero.x, 195 - self.hero.radius)

    def test_patrol_moves_between_points(self):
        self.guard.speed = 60
        self.guard.patrol_points = ((350, 200), (350, 300))
        self.world.obstacles.append(Obstacle(245, 160, 45, 85))
        self.world.update(1)
        self.assertGreater(self.guard.y, 200)
        self.assertFalse(self.guard.awake)

    def test_guard_routes_around_obstacle(self):
        self.guard.awake = True
        self.guard.last_seen = (self.hero.x, self.hero.y)
        self.world.obstacles.append(Obstacle(245, 160, 45, 85))
        self.world.update(1.5)
        self.assertNotAlmostEqual(self.guard.y, 200)
        self.assertEqual(self.guard.alert_state, "search")

    def test_hidden_player_does_not_update_last_seen(self):
        self.guard.awake = True
        self.guard.last_seen = (170, 200)
        self.world.obstacles.append(Obstacle(245, 160, 45, 85))
        self.hero.x, self.hero.y = 120, 250
        self.world.update(0.2)
        self.assertEqual(self.guard.last_seen, (170, 200))

    def test_search_continues_after_reaching_last_seen(self):
        self.guard.awake = True
        self.guard.last_seen = (170, 200)
        self.world.obstacles.append(Obstacle(245, 160, 45, 85))
        self.world.update(4)
        self.assertEqual(self.guard.alert_state, "search")
        self.assertTrue(self.guard.search_points or self.guard.searched_points or self.guard.search_goal)

    def test_chase_speed_exceeds_walk(self):
        self.assertGreaterEqual(self.guard.chase_speed, 2 * self.guard.walk_speed)


if __name__ == "__main__":
    unittest.main()
