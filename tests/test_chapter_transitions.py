"""Regression checks for the single chapter-one transition engine."""
import json
import unittest
from pathlib import Path

from game.scenes.chapter_area_navigation import chapter_transitions, find_chapter_exit

ROOT = Path(__file__).resolve().parents[1]


class ChapterTransitionsAudit(unittest.TestCase):
    def test_all_destinations_exist_and_spawns_are_safe(self):
        links = chapter_transitions()
        self.assertGreaterEqual(len(links), 20)
        for link in links:
            with self.subTest(source=link["from"], destination=link["to"]):
                for key in ("from", "to"):
                    self.assertTrue((ROOT / "data" / "scenes" / (link[key] + ".json")).is_file())
                self.assertEqual(len(link["rect"]), 4)
                self.assertEqual(len(link["spawn"]), 2)
                self.assertGreater(link["rect"][2], 0)
                self.assertGreater(link["rect"][3], 0)
                x, y = link["spawn"]
                for reverse in links:
                    if reverse["from"] != link["to"]:
                        continue
                    rx, ry, rw, rh = reverse["rect"]
                    self.assertFalse(rx <= x <= rx + rw and ry <= y <= ry + rh,
                                     f"Spawn from {link['from']} to {link['to']} overlaps exit to {reverse['to']}")
                legacy_name = link["to"].replace("brumazul_", "")
                legacy_name = {"taberna": "salon_posada", "posada": "habitacion_posada"}.get(legacy_name, legacy_name)
                source = ROOT / "python_simulator" / "scenes" / (legacy_name + ".json")
                if source.exists():
                    scene = json.loads(source.read_text(encoding="utf-8"))
                    walkable = scene.get("walkable")
                    if walkable:
                        self.assertTrue(any(a <= x <= a+w and b <= y <= b+h for a,b,w,h in walkable),
                                        f"Spawn outside walkable area: {link}")

    def test_every_exit_resolves_to_declared_destination(self):
        for link in chapter_transitions():
            x, y, w, h = link["rect"]
            found = find_chapter_exit(link["from"], x+w/2, y+h/2)
            self.assertEqual(found, (link["to"], tuple(link["spawn"])), link)

    def test_invalid_saved_village_position_recovers_without_losing_progress(self):
        from game.scenes.chapter_area_navigation import recover_chapter_position, can_walk_chapter_area
        from game.scenes.scene_loader import load_scene_data
        state = {"player": {"x": 485, "y": 145}, "quests": {"un_techo_propio": "find_elder_port"},
                 "inventory": {"wood": 10}}
        fixed = recover_chapter_position(state, "brumazul_pueblo", load_scene_data("brumazul_pueblo"))
        self.assertTrue(fixed)
        self.assertTrue(can_walk_chapter_area("brumazul_pueblo", state["player"]["x"], state["player"]["y"]))
        self.assertEqual(state["quests"]["un_techo_propio"], "find_elder_port")
        self.assertEqual(state["inventory"]["wood"], 10)
        self.assertFalse(recover_chapter_position(state, "brumazul_pueblo", load_scene_data("brumazul_pueblo")))

    def test_inn_round_trip(self):
        for a,b in [("brumazul_pueblo","brumazul_taberna"),
                    ("brumazul_taberna","brumazul_posada"),
                    ("brumazul_posada","brumazul_taberna"),
                    ("brumazul_taberna","brumazul_pueblo")]:
            self.assertTrue(any(link["from"] == a and link["to"] == b for link in chapter_transitions()))

    def test_no_duplicate_source_trigger(self):
        links = chapter_transitions()
        for i, a in enumerate(links):
            ax, ay, aw, ah = a["rect"]
            for b in links[i+1:]:
                if a["from"] != b["from"]:
                    continue
                bx, by, bw, bh = b["rect"]
                self.assertFalse(max(ax,bx)<min(ax+aw,bx+bw) and max(ay,by)<min(ay+ah,by+bh),
                                 f"Overlapping triggers: {a} and {b}")


if __name__ == "__main__":
    unittest.main()
