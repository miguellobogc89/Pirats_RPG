"""Chapter-one transition adapter: all doors are declared in data/scenes."""
import json
from functools import lru_cache
from pathlib import Path

TRANSITIONS_PATH = Path(__file__).resolve().parents[2] / "data" / "scenes" / "chapter_01_transitions.json"


@lru_cache(maxsize=1)
def chapter_transitions():
    return json.loads(TRANSITIONS_PATH.read_text(encoding="utf-8"))["transitions"]


def find_chapter_exit(scene_id, x, y, layout=None):
    """Return destination and safe arrival point from the shared transition table."""
    for link in chapter_transitions():
        if link["from"] != scene_id:
            continue
        rx, ry, rw, rh = link["rect"]
        if rx <= x <= rx + rw and ry <= y <= ry + rh:
            return link["to"], tuple(link["spawn"])
    return None


def transition_chapter_scene(app, scene_id, player, layout=None):
    """Single chapter transition entry point; scene and spawn change atomically."""
    destination = find_chapter_exit(scene_id, player["x"], player["y"], layout)
    if destination is None:
        return False
    target, spawn = destination
    if not app.scene_manager.change_scene(target, payload={"target_position": list(spawn)}):
        return False
    app.dispatch_scene_entered_event()
    return True


def can_walk_chapter_area(scene_id, x, y, layout=None):
    """Collision against walkable paths and building footprints (world pixels)."""
    layout = layout or {}
    if scene_id == "brumazul_pueblo":
        from pathlib import Path
        import json
        path = Path(__file__).resolve().parents[2] / "data" / "scenes" / "brumazul_pueblo.json"
        # The village walkable map is shared with the chapter-one source until migrated.
        source = Path(__file__).resolve().parents[2] / "python_simulator" / "scenes" / "pueblo.json"
        layout = json.loads(source.read_text(encoding="utf-8"))
    paths = layout.get("walkable", [])
    if not paths:
        return True
    inside = any(rx <= x <= rx + rw and ry <= y <= ry + rh for rx, ry, rw, rh in paths)
    if not inside:
        return False
    for building in layout.get("buildings", []):
        rx, ry, rw, rh = building["rect"]
        if rx <= x <= rx + rw and ry <= y <= ry + rh:
            return False
    for key in ("house", "workshop"):
        building = layout.get(key)
        if building and "rect" in building:
            rx, ry, rw, rh = building["rect"]
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return False
    return True
