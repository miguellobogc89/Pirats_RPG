"""Wild vegetation spawning."""
import random

def spawn_wild_bush(state, farming):
    """One bush on an unoccupied, walkable tile of the chapter farm."""
    import json
    from pathlib import Path
    from game.world.grid_manager import TILE_SIZE
    from game.scenes.chapter_area_navigation import can_walk_chapter_area
    path = Path(__file__).resolve().parents[2] / "data" / "scenes" / "brumazul_granja.json"
    layout = json.loads(path.read_text(encoding="utf-8"))["chapter_layout"]
    occupied = {tuple(c) for c in farming["tilled_cells"]}
    occupied.update((c["grid_x"], c["grid_y"]) for c in farming["crops"])
    occupied.update(tuple(c) for c in farming.setdefault("wild_bushes", []))
    for obj in farming.get("placed_objects", []):
        for gx in range(obj["grid_x"], obj["grid_x"] + obj.get("width", 1)):
            for gy in range(obj["grid_y"], obj["grid_y"] + obj.get("height", 1)):
                occupied.add((gx, gy))
    player = state.get("player", {})
    if state.get("current_scene") == "brumazul_granja" and "x" in player:
        occupied.add((int(player["x"] // TILE_SIZE), int(player["y"] // TILE_SIZE)))
    candidates = []
    for gy in range(2, int(layout["height"] // TILE_SIZE) - 1):
        for gx in range(2, int(layout["width"] // TILE_SIZE) - 1):
            if (gx, gy) in occupied:
                continue
            x, y = (gx + .5) * TILE_SIZE, (gy + .5) * TILE_SIZE
            if not can_walk_chapter_area("brumazul_granja", x, y, layout):
                continue
            if any((x - wx)**2 + (y - wy)**2 < 48**2 for wx, wy in layout.get("wood_piles", [])):
                continue
            if any((x - px)**2 + (y - py)**2 < 48**2 for px, py in
                   (layout.get("spawn", [0, 0]), layout.get("gate", {}).get("position", [0, 0]))):
                continue
            candidates.append([gx, gy])
    if candidates:
        farming["wild_bushes"].append(random.choice(candidates))
