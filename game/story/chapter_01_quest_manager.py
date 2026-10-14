"""Chapter-one quest progress driven by the modular event bus, not Pygame.

Quest events are additive: original intro events continue to work.
This module never grants items or claims an encounter was completed.
"""

QUESTS = {
    "un_techo_propio": {
        "initial": "find_elder",
        "transitions": {
            "find_elder": ("npc_talked", "anciano", "repair_fence"),
            "repair_fence": ("npc_talked", "anciano", "get_bolt"),
            "inspect_gate": ("npc_talked", "anciano", "get_bolt"),
            "get_bolt": ("object_repaired", "farm_gate", "find_elder_port"),
            "find_elder_port": ("npc_talked", "anciano_puerto", "complete"),
        },
    },
    "el_hierro_que_canta": {
        "initial": "not_started",
        "transitions": {
            "not_started": ("npc_talked", "herrero", "investigate"),
            "investigate": ("npc_talked", "sylvarin", "artisan_explained"),
            "artisan_explained": ("npc_talked", "herrero", "completed"),
        },
    },
    "cuando_callan_las_campanas": {
        "initial": "not_started",
        "transitions": {
            "not_started": ("npc_talked", "sylvarin", "get_weapon"),
            "get_weapon": ("weapon_acquired", "player", "offered"),
            "offered": ("object_interacted", "rat_nest_cleared", "cleared"),
            "cleared": ("npc_talked", "sylvarin", "completed"),
        },
    },
    "la_ultima_madriguera": {
        "initial": "ready",
        "transitions": {
            "ready": ("npc_talked", "anciano_granja", "hunt"),
            "hunt": ("object_interacted", "ambushes_cleared", "boss"),
            "boss": ("object_interacted", "farm_boss_defeated", "approach"),
            "approach": ("npc_talked", "anciano_granja", "complete"),
        },
    },
}


def ensure_chapter_quests(state):
    quests = state.setdefault("quests", {})
    if not isinstance(quests, dict):
        quests = {}
        state["quests"] = quests
    for quest_id, definition in QUESTS.items():
        quests.setdefault(quest_id, definition["initial"])
    return quests


def apply_chapter_quest_event(state, event_type, payload=None):
    """Return actual transitions; never infer objectives from merely opening a UI."""
    payload = payload or {}
    quests = ensure_chapter_quests(state)
    results = []
    previous = dict(quests)
    for quest_id, definition in QUESTS.items():
        current = previous[quest_id]
        transition = definition["transitions"].get(current)
        if transition is None:
            continue
        required_event, required_target, next_stage = transition
        target = payload.get("npc_id") if event_type == "npc_talked" else ("player" if event_type == "weapon_acquired" else payload.get("object_id"))
        if event_type != required_event or target != required_target:
            continue
        if quest_id == "el_hierro_que_canta" and current == "not_started" and previous["un_techo_propio"] not in ("inspect_gate", "get_bolt", "find_elder_port", "complete"):
            continue
        if quest_id == "cuando_callan_las_campanas" and current == "not_started" and previous["el_hierro_que_canta"] not in ("artisan_explained", "completed"):
            continue
        quests[quest_id] = next_stage
        results.append({"quest_id": quest_id, "from": current, "to": next_stage})
    return results
