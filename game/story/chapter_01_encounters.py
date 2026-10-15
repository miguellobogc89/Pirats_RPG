"""Persistent proximity encounters for the chapter-one farm and rat nest."""
import math

ENCOUNTERS = {
    "brumazul_granja": ("farm_ambush", "ambushes", "farm_boss", "final_boss"),
    "brumazul_madriguera_artesana": ("rat_nest", "rats", "rat_boss", "nest"),
}


def initialize(scene):
    data = ENCOUNTERS.get(scene.scene_id)
    if not data:
        return
    key, positions_key, boss_key, boss_position_key = data
    state = scene.app.state.setdefault("chapter_encounters", {}).setdefault(key, {})
    scene.encounter_state = state
    scene.encounter_units = [
        {"id": str(i), "x": float(x), "y": float(y), "hp": state.get("unit_hp", {}).get(str(i), 3 if key == "farm_ambush" else 2), "max_hp": 3 if key == "farm_ambush" else 2,
         "awake": False, "cooldown": 0.0}
        for i, (x, y) in enumerate(scene.area_layout.get(positions_key, []))
        if str(i) not in state.get("defeated", [])
    ]
    scene.encounter_boss = None
    scene.encounter_attack_cooldown = 0.0
    scene.encounter_damage_cooldown = 0.0
    scene.encounter_boss_position = scene.area_layout.get(boss_position_key, [445, 355])
    if state.get("boss_spawned") and not state.get("boss_defeated"):
        spawn_boss(scene)


def spawn_boss(scene):
    x, y = scene.encounter_boss_position
    scene.encounter_boss = {"id": "boss", "x": float(x), "y": float(y),
                            "hp": scene.encounter_state.get("boss_hp", 12), "max_hp": 12, "awake": True, "cooldown": 0.0}
    scene.encounter_state["boss_spawned"] = True
    scene.encounter_state["boss_hp"] = scene.encounter_boss["hp"]


def update(scene, dt):
    if not hasattr(scene, "encounter_units") or scene.app.menu_open or scene.npc_dialogue is not None:
        return
    if scene.scene_id == "brumazul_granja" and not scene.encounter_state.get("started"):
        return
    scene.encounter_attack_cooldown = max(0.0, scene.encounter_attack_cooldown - dt)
    scene.encounter_damage_cooldown = max(0.0, scene.encounter_damage_cooldown - dt)
    player = scene.app.state["player"]
    for enemy in scene.encounter_units + ([scene.encounter_boss] if scene.encounter_boss else []):
        distance = math.dist((player["x"], player["y"]), (enemy["x"], enemy["y"]))
        if distance < 170:
            enemy["awake"] = True
        if not enemy["awake"]:
            continue
        if distance > 32:
            step = min(distance - 32, (62 if enemy["id"] == "boss" else 82) * dt)
            enemy["x"] += (player["x"] - enemy["x"]) / distance * step
            enemy["y"] += (player["y"] - enemy["y"]) / distance * step
        if distance < 39 and scene.encounter_damage_cooldown <= 0:
            health = scene.app.state.get("health", {})
            health["current"] = max(0, health.get("current", health.get("max", 10)) - (3 if enemy["id"] == "boss" else 1))
            scene.encounter_damage_cooldown = 1.2
            scene.app.add_log("Una criatura te ha atacado.")
    if not scene.encounter_units and not scene.encounter_state.get("boss_spawned") and not scene.encounter_state.get("boss_defeated"):
        if scene.scene_id == "brumazul_granja":
            from game.story_events.story_event_manager import dispatch_story_event
            dispatch_story_event(scene.app, "object_interacted", {"object_id": "ambushes_cleared"})
        spawn_boss(scene)
        scene.app.add_log("La maleza se agita... ¡aparece una criatura enorme!")


def attack(scene):
    if not hasattr(scene, "encounter_units") or scene.encounter_attack_cooldown > 0:
        return False
    if scene.scene_id == "brumazul_granja" and not scene.encounter_state.get("started"):
        return False
    from game.inventory.inventory_manager import get_item_quantity
    from game.data.item_database import ITEM_DATABASE
    if not any(item.get("type") == "weapon" and get_item_quantity(scene.app.state, item_id) for item_id, item in ITEM_DATABASE.items()):
        scene.app.add_log("Necesitas un arma para luchar.")
        return True
    player = scene.app.state["player"]
    enemies = scene.encounter_units + ([scene.encounter_boss] if scene.encounter_boss else [])
    from game.world.action_range import can_interact_point
    targets = [e for e in enemies if can_interact_point(player, e["x"], e["y"])]
    if not targets:
        return False
    enemy = min(targets, key=lambda e: math.dist((player["x"], player["y"]), (e["x"], e["y"])))
    enemy["awake"] = True
    enemy["hp"] -= 1
    if enemy["id"] == "boss":
        scene.encounter_state["boss_hp"] = max(0, enemy["hp"])
    else:
        scene.encounter_state.setdefault("unit_hp", {})[enemy["id"]] = max(0, enemy["hp"])
    scene.autosave()
    scene.encounter_attack_cooldown = 0.4
    if enemy["hp"] <= 0:
        if enemy["id"] == "boss":
            scene.encounter_boss = None
            scene.encounter_state["boss_defeated"] = True
            scene.encounter_state.pop("boss_hp", None)
            from game.story_events.story_event_manager import dispatch_story_event
            if scene.scene_id == "brumazul_granja":
                dispatch_story_event(scene.app, "object_interacted", {"object_id": "farm_boss_defeated"})
            else:
                dispatch_story_event(scene.app, "object_interacted", {"object_id": "rat_nest_cleared"})
            scene.app.add_log("¡Has derrotado al jefe!")
        else:
            scene.encounter_units.remove(enemy)
            scene.encounter_state.get("unit_hp", {}).pop(enemy["id"], None)
            scene.encounter_state.setdefault("defeated", []).append(enemy["id"])
            scene.app.add_log("Criatura derrotada.")
        scene.autosave()
    return True


def draw(scene, cx, cy):
    if not hasattr(scene, "encounter_units"):
        return
    import pygame
    for enemy in scene.encounter_units + ([scene.encounter_boss] if scene.encounter_boss else []):
        if scene.scene_id == "brumazul_granja" and not scene.encounter_state.get("started"):
            continue
        x, y = int(enemy["x"] - cx), int(enemy["y"] - cy)
        boss = enemy["id"] == "boss"
        radius = 23 if boss else 12
        pygame.draw.circle(scene.app.screen, (112, 58, 56) if enemy["awake"] else (75, 111, 65), (x, y), radius)
        pygame.draw.circle(scene.app.screen, (42, 39, 36), (x, y), radius, 2)
        scene.label("JEFE" if boss else ("CRIATURA" if enemy["awake"] else "MALEZA"), x - 25, y - radius - 32)
        bar_width = 62 if boss else 42
        left, top = x - bar_width // 2, y - radius - 13
        pygame.draw.rect(scene.app.screen, (57, 45, 45), (left, top, bar_width, 7))
        pygame.draw.rect(scene.app.screen, (192, 77, 67), (left + 1, top + 1, round((bar_width - 2) * max(0, enemy["hp"]) / enemy["max_hp"]), 5))
        scene.label(str(enemy["hp"]) + "/" + str(enemy["max_hp"]), left + bar_width + 4, top - 4)
