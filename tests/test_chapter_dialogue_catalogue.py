"""Guard against broken chapter dialogue references and inline spoken dialogue."""
import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "game" / "scenes" / "brumazul_scene.py"
CATALOGUE = ROOT / "data" / "dialogues" / "chapter_01.json"


class ChapterDialogueAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
        cls.source = SCENE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_all_static_dialogue_ids_exist(self):
        dialogues = self.catalogue["dialogues"]
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "get_chapter_dialogue" or not node.args:
                continue
            for part in ast.walk(node.args[0]):
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                    self.assertIn(part.value, dialogues, f"Unknown dialogue ID at line {node.lineno}")

    def test_all_npc_dialogues_exist(self):
        dialogues = self.catalogue["dialogues"]
        for area, npcs in self.catalogue["npcs"].items():
            for npc in npcs:
                self.assertIn(npc["dialogue"], dialogues, f"{area}: {npc['id']}")

    def test_dialogues_have_speaker_and_lines(self):
        for key, value in self.catalogue["dialogues"].items():
            with self.subTest(dialogue=key):
                self.assertTrue(value.get("speaker"))
                self.assertTrue(value.get("lines"))
                self.assertTrue(all(isinstance(line, str) and line for line in value["lines"]))

    def test_no_inline_spoken_dialogue_in_scene(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "draw_dialogue":
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            self.fail(f"Inline dialogue text at line {node.lineno}")
        self.assertNotRegex(self.source, r'(?m)^\s*self\.npc_dialogue\s*=\s*\(\s*["\']')

    def test_npc_dialogue_advances_one_line_at_a_time(self):
        self.assertIn("self.npc_dialogue_index += 1", self.source)
        self.assertIn("self.npc_dialogue[1][self.npc_dialogue_index]", self.source)
        self.assertNotIn('"  ".join(self.npc_dialogue[1])', self.source)

    def test_chapter_quest_conversations_do_not_cascade(self):
        from game.story.chapter_01_quest_manager import apply_chapter_quest_event
        state = {"quests": {
            "un_techo_propio": "get_bolt",
            "el_hierro_que_canta": "investigate",
            "cuando_callan_las_campanas": "not_started",
            "la_ultima_madriguera": "ready",
        }}
        result = apply_chapter_quest_event(state, "npc_talked", {"npc_id": "sylvarin"})
        self.assertEqual([entry["quest_id"] for entry in result], ["el_hierro_que_canta"])
        self.assertEqual(state["quests"]["cuando_callan_las_campanas"], "not_started")
        result = apply_chapter_quest_event(state, "npc_talked", {"npc_id": "sylvarin"})
        self.assertEqual([entry["quest_id"] for entry in result], ["cuando_callan_las_campanas"])

    def test_reward_dialogue_has_matching_inventory_transaction(self):
        self.assertIn('receive(self.app.state, "metal_bolt"', self.source)
        self.assertIn('receive(self.app.state, "sylvarin_boots"', self.source)

    def test_narrative_hints_are_catalogued(self):
        for key in ("mission_started", "room_exit_hint", "tavern_hint", "village_hint"):
            self.assertIn(key, self.catalogue["ui_text"])
        self.assertIn("get_chapter_ui_text", self.source)

    def test_intro_is_data_driven(self):
        intro = self.catalogue["intro"]
        self.assertTrue(intro["script"])
        self.assertEqual(len(intro["choices"]), len(intro["responses"]))
        self.assertLess(intro["choice_index"], len(intro["script"]))
        self.assertLess(intro["response_index"], len(intro["script"]))


if __name__ == "__main__":
    unittest.main()
