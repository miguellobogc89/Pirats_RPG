"""Regression checks for chapter-one event-driven quest progression."""
import unittest
from game.story.chapter_01_quest_manager import apply_chapter_quest_event, ensure_chapter_quests


class ChapterQuestProgressionTests(unittest.TestCase):
    def test_farm_progression_requires_each_event_in_order(self):
        state = {"quests": {"un_techo_propio": "complete"}}
        quests = ensure_chapter_quests(state)
        self.assertEqual(quests["la_ultima_madriguera"], "ready")
        apply_chapter_quest_event(state, "object_interacted", {"object_id": "ambushes_cleared"})
        self.assertEqual(quests["la_ultima_madriguera"], "ready")
        for event, payload, expected in (
            ("npc_talked", {"npc_id": "anciano_granja"}, "hunt"),
            ("object_interacted", {"object_id": "ambushes_cleared"}, "boss"),
            ("object_interacted", {"object_id": "farm_boss_defeated"}, "approach"),
            ("npc_talked", {"npc_id": "anciano_granja"}, "complete"),
        ):
            apply_chapter_quest_event(state, event, payload)
            self.assertEqual(quests["la_ultima_madriguera"], expected)

    def test_rat_progression_requires_weapon_and_boss(self):
        state = {"quests": {"el_hierro_que_canta": "artisan_explained"}}
        quests = ensure_chapter_quests(state)
        apply_chapter_quest_event(state, "rat_nest_offered", {"object_id": "sylvarin"})
        self.assertEqual(quests["cuando_callan_las_campanas"], "get_weapon")
        apply_chapter_quest_event(state, "weapon_acquired", {"object_id": "player"})
        self.assertEqual(quests["cuando_callan_las_campanas"], "offered")
        apply_chapter_quest_event(state, "object_interacted", {"object_id": "rat_nest_cleared"})
        self.assertEqual(quests["cuando_callan_las_campanas"], "cleared")
        apply_chapter_quest_event(state, "npc_talked", {"npc_id": "sylvarin"})
        self.assertEqual(quests["cuando_callan_las_campanas"], "completed")


if __name__ == "__main__":
    unittest.main()
