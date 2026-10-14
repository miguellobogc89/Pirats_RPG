"""Pure chapter-one exit resolver. Scene geometry is in modular data/scenes."""
SCENE_IDS = {
    "pueblo": "brumazul_pueblo",
    "puerto": "brumazul_puerto",
    "playa": "brumazul_playa",
    "granja": "brumazul_granja",
    "salon_posada": "brumazul_taberna",
    "habitacion_posada": "brumazul_posada",
    "taller_sylvarin": "brumazul_taller_sylvarin",
    "casa_almarin": "brumazul_casa_almarin",
    "taller_almarin": "brumazul_taller_almarin",
    "madriguera_artesana": "brumazul_madriguera",
}


def find_chapter_exit(scene_id, x, y, layout=None):
    """Resolve every chapter door in one place; arrival points never overlap exits."""
    if scene_id == "brumazul_pueblo":
        if 1035 <= x <= 1115 and 245 <= y <= 270:
            return "brumazul_taberna", (480, 180)
        if 1225 <= x <= 1285 and 425 <= y <= 450:
            return "brumazul_taller_sylvarin", (400, 555)
        if x <= 115 and 410 <= y <= 500:
            return "brumazul_granja", (780, 375)
        if 580 <= x <= 720 and y >= 960:
            return "brumazul_puerto", (400, 145)
        if 450 <= x < 580 and y >= 960:
            return "brumazul_playa", (400, 55)
    if scene_id == "brumazul_taberna":
        if 425 <= x <= 550 and y <= 119:
            return "brumazul_posada", (400, 440)
        if 425 <= x <= 550 and y >= 730:
            return "brumazul_pueblo", (1060, 410)
    if scene_id == "brumazul_posada":
        if 430 <= x <= 540 and y >= 575:
            return "brumazul_taberna", (485, 540)
    if scene_id == "brumazul_granja":
        if x >= 842 and 330 <= y <= 420:
            return "brumazul_pueblo", (145, 455)
        if 255 <= x <= 290 and 275 <= y <= 300:
            return "brumazul_casa_almarin", (400, 480)
        if 450 <= x <= 490 and 275 <= y <= 300:
            return "brumazul_taller_almarin", (400, 480)
    if scene_id == "brumazul_puerto":
        if 350 <= x <= 450 and y <= 45:
            return "brumazul_pueblo", (650, 925)
        if x <= 45 and 390 <= y <= 490:
            return "brumazul_playa", (650, 440)
    if scene_id == "brumazul_casa_almarin" and 350 <= x <= 450 and y >= 545:
        return "brumazul_granja", (275, 310)
    if scene_id == "brumazul_taller_almarin" and 350 <= x <= 450 and y >= 545:
        return "brumazul_granja", (470, 310)
    for exit_data in (layout or {}).get("exits", []):
        rect = exit_data.get("rect")
        target = SCENE_IDS.get(exit_data.get("to"))
        spawn = exit_data.get("spawn")
        if rect and target and spawn and rect[0] <= x <= rect[0] + rect[2] and rect[1] <= y <= rect[1] + rect[3]:
            return target, tuple(spawn)
    return None


def transition_chapter_scene(app, scene_id, player, layout=None):
    """Apply destination and coordinates through the common scene manager."""
    destination = find_chapter_exit(scene_id, player["x"], player["y"], layout)
    if destination is None:
        return False
    target, spawn = destination
    if not app.scene_manager.change_scene(target):
        return False
    app.state["player"].update({"x": spawn[0], "y": spawn[1]})
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
