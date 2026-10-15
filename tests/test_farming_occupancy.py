import unittest

from game.world.occupancy import blocks_movement, blocks_farming, movement_multiplier
from game.scenes.scene_state import get_current_scene_state
from game.world.grid_manager import TILE_SIZE


class OccupancyTests(unittest.TestCase):
    def setUp(self):
        self.state = {"current_scene": "brumazul_granja", "scene_states": {}}

    def test_bush_slows_without_blocking(self):
        get_current_scene_state(self.state)["wild_bushes"].append([4, 5])
        self.assertFalse(blocks_movement(self.state, 4, 5))
        self.assertTrue(blocks_farming(self.state, 4, 5))
        self.assertAlmostEqual(movement_multiplier(self.state, 4.5 * TILE_SIZE, 5.5 * TILE_SIZE), 0.6)

    def test_tree_rock_and_item_block(self):
        tree = {"type": "tree", "grid_x": 3, "grid_y": 4}
        rock = {"type": "rock", "grid_x": 7, "grid_y": 8}
        self.assertTrue(blocks_movement(self.state, 3, 4, [tree, rock]))
        self.assertTrue(blocks_movement(self.state, 7, 8, [tree, rock]))
        self.state["collectables"] = [{"item_id": "wood", "x": 9.5 * TILE_SIZE, "y": 9.5 * TILE_SIZE}]
        self.assertTrue(blocks_movement(self.state, 9, 9))


if __name__ == "__main__":
    unittest.main()
