import unittest
from unittest.mock import patch

from game.crafting.crafting_manager import craft_item, check_craft, can_craft
from game.inventory.inventory_manager import add_item, get_item_quantity, get_inventory_grid
from game.inventory.item_transactions import exchange, can_receive


class CraftingEngineTests(unittest.TestCase):
    def setUp(self):
        self.state = {}

    def test_missing_resources_do_not_mutate_inventory(self):
        self.assertEqual(craft_item(self.state, "campfire")["status"], "missing_resources")
        self.assertEqual(get_item_quantity(self.state, "campfire"), 0)

    def test_craft_consumes_split_stacks_and_delivers(self):
        add_item(self.state, "wood", 10)
        add_item(self.state, "stone", 5)
        self.assertTrue(can_craft(self.state, "campfire"))
        self.assertEqual(craft_item(self.state, "campfire")["status"], "crafted")
        self.assertEqual(get_item_quantity(self.state, "wood"), 0)
        self.assertEqual(get_item_quantity(self.state, "stone"), 0)
        self.assertEqual(get_item_quantity(self.state, "campfire"), 1)

    def test_atomic_exchange_rolls_back_on_invalid_output(self):
        add_item(self.state, "wood", 10)
        self.assertFalse(exchange(self.state, {"wood": 10}, {"unknown_item": 1}))
        self.assertEqual(get_item_quantity(self.state, "wood"), 10)

    def test_station_and_skill_requirements(self):
        from game.crafting.crafting_manager import check_requirements
        recipe = {"requirements": {"station": "forge", "skills": {"crafting": 3}}}
        self.assertEqual(check_requirements(self.state, recipe), "missing_station")
        self.assertEqual(check_requirements(self.state, recipe, {"stations": ["forge"]}), "missing_skill")
        self.state["skills"] = {"crafting": {"level": 3}}
        self.assertIsNone(check_requirements(self.state, recipe, {"stations": ["forge"]}))


if __name__ == "__main__":
    unittest.main()
