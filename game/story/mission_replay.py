"""Developer mission replay checkpoints, defined in JSON. Keeps player inventory."""
import json
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[2] / "data/missions/chapter_01_replay.json"


def replay_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def replay_mission(app, mission_id):
    from game.story.chapter_01_quest_manager import QUESTS, ensure_chapter_quests
    from core.save_manager import save_state
    config = replay_config()
    mission = next((m for m in config["missions"] if m["id"] == mission_id), None)
    if mission is None:
        return False
    state = app.state
    quests = ensure_chapter_quests(state)
    for quest_id in mission["reset_quests"]:
        quests[quest_id] = QUESTS[quest_id]["initial"]
    if mission.get("reset_farm"):
        state["farm_repairs"] = {}
        state.setdefault("brumazul", {}).pop("elder_clue_seen", None)
    if mission_id == "la_ultima_madriguera":
        state.setdefault("brumazul", {}).pop("farm_boss_defeated", None)
    if mission_id in ("el_hierro_que_canta", "cuando_callan_las_campanas"):
        # Make the replayed side quest reachable without replaying the farm.
        if quests["un_techo_propio"] in ("find_elder", "repair_fence"):
            quests["un_techo_propio"] = "get_bolt"
    if mission_id == "cuando_callan_las_campanas" and quests["el_hierro_que_canta"] == "not_started":
        quests["el_hierro_que_canta"] = "artisan_explained"
    state.setdefault("mission_replays", {})[mission_id] = state.get("mission_replays", {}).get(mission_id, 0) + 1
    state["player"]["x"], state["player"]["y"] = config["neutral_position"]
    state["current_scene"] = config["neutral_scene"]
    app.menu_open = False
    app.menu_action_hitboxes = []
    app.scene_manager.change_scene(config["neutral_scene"], payload={"target_position": config["neutral_position"]})
    save_state(state)
    app.add_log("Reinicio de prueba: " + mission["title"])
    return True
