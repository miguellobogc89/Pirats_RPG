"""Chapter-one transition adapter: all doors are declared in data/scenes."""
import json
from functools import lru_cache
from pathlib import Path

TRANSITIONS_PATH = Path(__file__).resolve().parents[2] / "data" / "scenes" / "chapter_01_transitions.json"
VILLAGE_LAYOUT_PATH = Path(__file__).resolve().parents[2] / "data" / "chapter_layouts" / "pueblo.json"


@lru_cache(maxsize=1)
def village_layout():
    """Mapa transitable del pueblo. Se lee del disco una sola vez."""
    return json.loads(VILLAGE_LAYOUT_PATH.read_text(encoding="utf-8"))


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
    if not chapter_exit_active(app.state, scene_id, target):
        # Inactive exits are handled by explicit scene interaction, not proximity.
        return False
    if target in ("brumazul_casa_almarin", "brumazul_taller_almarin"):
        from game.story.chapter_01_quest_manager import ensure_chapter_quests
        if ensure_chapter_quests(app.state)["la_ultima_madriguera"] != "complete":
            app.add_log("Necesitas las llaves que te entregará el anciano.")
            return False
    if target == "brumazul_madriguera_artesana":
        from game.inventory.inventory_manager import get_item_quantity
        from game.data.item_database import ITEM_DATABASE
        from game.story.chapter_01_quest_manager import ensure_chapter_quests
        from game.story_events.story_event_manager import dispatch_story_event
        armed = any(item.get("type") == "weapon" and get_item_quantity(app.state, item_id) > 0 for item_id, item in ITEM_DATABASE.items())
        quests = ensure_chapter_quests(app.state)
        if not armed:
            app.add_log("Necesitas conseguir un arma antes de entrar en el nido.")
            return False
        if quests["cuando_callan_las_campanas"] == "get_weapon":
            dispatch_story_event(app, "weapon_acquired", {"object_id": "player"})
    if not app.scene_manager.change_scene(target, payload={"target_position": list(spawn)}):
        return False
    app.dispatch_scene_entered_event()
    return True


def can_walk_chapter_area(scene_id, x, y, layout=None):
    """Collision against walkable paths and building footprints (world pixels)."""
    layout = layout or {}
    if scene_id == "brumazul_pueblo":
        layout = village_layout()
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


def recover_chapter_position(state, scene_id, scene_data):
    """Repair invalid legacy save coordinates without resetting quest or inventory."""
    if not scene_id.startswith("brumazul_"):
        return False
    player = state.get("player")
    if not isinstance(player, dict):
        return False
    x, y = player.get("x"), player.get("y")
    layout = (scene_data or {}).get("chapter_layout", {})
    if scene_id == "brumazul_pueblo":
        layout = village_layout()
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        if can_walk_chapter_area(scene_id, x, y, layout):
            width = layout.get("width", (scene_data or {}).get("width", 50) * (scene_data or {}).get("tile_size", 16))
            height = layout.get("height", (scene_data or {}).get("height", 50) * (scene_data or {}).get("tile_size", 16))
            if 0 <= x <= width and 0 <= y <= height:
                return False
    # Prefer a safe, scene-specific default; never touch saved mission progress.
    spawn = (scene_data or {}).get("player_spawn", {})
    sx, sy = spawn.get("x", 0), spawn.get("y", 0)
    if not can_walk_chapter_area(scene_id, sx, sy, layout):
        paths = layout.get("walkable", [])
        if paths:
            rx, ry, rw, rh = paths[0]
            sx, sy = rx + rw / 2, ry + rh / 2
    player["x"], player["y"] = sx, sy
    return True


def chapter_exit_active(state, scene_id, target):
    """Shared exit-state rule. The prologue beach starts closed; saves can unlock exits."""
    key = f"{scene_id}:{target}"
    overrides = state.get("chapter_exit_states", {})
    if key in overrides:
        return bool(overrides[key])
    return scene_id != "brumazul_playa"


def set_chapter_exit_active(state, scene_id, target, active):
    """Persist a chapter exit unlock without changing the transition table."""
    state.setdefault("chapter_exit_states", {})[f"{scene_id}:{target}"] = bool(active)
