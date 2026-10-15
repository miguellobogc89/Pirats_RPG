import unittest
from unittest.mock import patch

from game.farming.farming_manager import advance_farming_day
from game.farming.crop_manager import plant_crop, get_crop_at_cell, is_crop_ready
from game.farming.soil_manager import till_cell
from game.scenes.scene_state import get_current_scene_state
from game.world.grid_manager import TILE_SIZE


def center(x, y):
    return (x + 0.5) * TILE_SIZE, (y + 0.5) * TILE_SIZE


class FarmingLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.state = {"current_scene": "brumazul_granja", "scene_states": {}, "player": {"x": 0, "y": 0}}

    def test_tilling_occupied_ground_fails(self):
        get_current_scene_state(self.state)["wild_bushes"].append([2, 2])
        self.assertFalse(till_cell(self.state, *center(2, 2)))
        self.state["collectables"] = [{"item_id": "stone", "x": center(3, 3)[0], "y": center(3, 3)[1]}]
        self.assertFalse(till_cell(self.state, *center(3, 3)))
        self.assertTrue(till_cell(self.state, *center(4, 4)))

    def test_growth_drought_and_dead_crop(self):
        scene = get_current_scene_state(self.state)
        scene["tilled_cells"].append([5, 5])
        self.assertEqual(plant_crop(self.state, *center(5, 5), "corn"), "planted")
        scene["watered_cells"].append([5, 5])
        with patch("game.farming.farming_manager.random.random", return_value=1.0):
            advance_farming_day(self.state, "brumazul_granja")
            crop = get_crop_at_cell(self.state, 5, 5)
            self.assertEqual(crop["stage"], 1)
            advance_farming_day(self.state, "brumazul_granja")
            advance_farming_day(self.state, "brumazul_granja")
            self.assertTrue(crop["dead"])
            self.assertFalse(is_crop_ready(crop))

    def test_scene_isolation(self):
        get_current_scene_state(self.state)["wild_bushes"].append([4, 5])
        self.state["current_scene"] = "brumazul_pueblo"
        self.assertNotIn([4, 5], get_current_scene_state(self.state)["wild_bushes"])


if __name__ == "__main__":
    unittest.main()
