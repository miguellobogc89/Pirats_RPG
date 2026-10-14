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

    def test_intro_is_data_driven(self):
        intro = self.catalogue["intro"]
        self.assertTrue(intro["script"])
        self.assertEqual(len(intro["choices"]), len(intro["responses"]))
        self.assertLess(intro["choice_index"], len(intro["script"]))
        self.assertLess(intro["response_index"], len(intro["script"]))


if __name__ == "__main__":
    unittest.main()
