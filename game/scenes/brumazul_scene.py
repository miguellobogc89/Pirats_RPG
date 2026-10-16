"""Brumazul, capitulo 1. Escenas narrativas integradas en Pirats RPG.

El estado del personaje, inventario, recoleccion y menu siguen siendo los del motor.
El prototipo independiente no se modifica.
"""
import math
import json
from pathlib import Path
import pygame

from core.save_manager import save_state
from game.scenes.farm_scene import FarmScene
from game.hud.menu_overlay import draw_menu
from game.hud.stash_overlay import draw_stash_overlay
from game.inventory.hotbar_manager import get_hotbar_slots, get_active_hotbar_index
from game.inventory.item_transactions import receive, spend, spend_bundle, quantity, migrate_chapter_items
from game.world.camera import get_camera_position
from game.data.item_database import get_item_data
from game.dialogue.chapter_dialogues import get_chapter_dialogue, get_chapter_intro, get_chapter_npcs, get_chapter_ui_text
from game.dialogue.chapter_conversation_renderer import draw_chapter_conversation

WIDTH, HEIGHT = 960, 640
WHITE = (250, 250, 249)
PAPER = (245, 245, 244)
PALE = (231, 231, 230)
LIGHT = (208, 208, 207)
LINE = (166, 166, 166)
INK = (105, 105, 105)

# La conversacion tiene indicaciones de escena en vez de lineas pronunciadas.
INTRO = get_chapter_intro()
SCRIPT = [(entry["speaker"], entry["text"]) for entry in INTRO["script"]]
CHOICES = INTRO["choices"]
RESPONSES = INTRO["responses"]
VILLAGE_LAYOUT = json.loads(
    (Path(__file__).resolve().parents[2] / "python_simulator" / "scenes" / "pueblo.json").read_text(encoding="utf-8")
)
VILLAGE_NPCS = [(npc["name"], npc["race"], tuple(npc["position"]), npc["dialogue"]) for npc in get_chapter_npcs("village")]
TAVERN_NPCS = [(npc["name"], npc["race"], tuple(npc["position"]), npc["dialogue"]) for npc in get_chapter_npcs("tavern")]

class BrumazulScene(FarmScene):
    def enter(self):
        self.beach = self.scene_id == "brumazul_playa"
        self.tavern = self.scene_id == "brumazul_taberna"
        self.village = self.scene_id == "brumazul_pueblo"
        self.chapter_area = self.scene_id.startswith("brumazul_") and self.scene_id not in ("brumazul_playa", "brumazul_posada", "brumazul_taberna", "brumazul_pueblo")
        self.area_layout = self.app.scene_data.get("chapter_layout", {}) if self.chapter_area and self.app.scene_data else {}
        self.app.menu_open = False
        self.app.stash_open = False
        from game.story.chapter_01_quest_manager import ensure_chapter_quests
        ensure_chapter_quests(self.app.state)
        migrate_chapter_items(self.app.state)
        if self.scene_id == "brumazul_granja":
            from game.inventory.item_transactions import quantity
            grant_flag = self.app.state.setdefault("farm_tools", {})
            if not grant_flag.get("scythe_granted"):
                if quantity(self.app.state, "scythe") > 0:
                    grant_flag["scythe_granted"] = True
                elif receive(self.app.state, "scythe", 1):
                    grant_flag["scythe_granted"] = True
                else:
                    self.app.add_log("Deja un hueco en el inventario para recibir la segadora.")
        self.app.state.setdefault("brumazul", {})
        self.progress = self.app.state["brumazul"]
        self.boss = pygame.Vector2(490, 560)
        self.boss_awake = False
        self.boss_timer = 0.0
        self.attack_timer = 0.0
        self.boss_hp = 999
        self.index = 0
        self.choice = 0
        self.response = RESPONSES[0]
        self.phase = "free" if self.beach or self.tavern or self.village or self.chapter_area or self.progress.get("intro_finished") else "dialogue"
        self.keeper = pygame.Vector2(480, 395)
        self.elder = pygame.Vector2(470, 625)
        self.show_elder = False
        self.show_keeper = not self.progress.get("intro_finished", False)
        self.fade = 0.0
        self.npc_dialogue = None
        self.npc_dialogue_index = 0
        self.sleep_confirmation = False
        self.shop_id = None
        self.shop_prompt = None
        self.shop_selection = None
        self.shop_hitboxes = []
        self.shop_page = 0
        self.shop_talk_bypass = False
        self.port_departure = False
        self.port_departure_progress = 0.0
        self.door_cooldown = 0.8

        from game.story.chapter_01_encounters import initialize
        initialize(self)
        self.save_elapsed = 0.0
        if self.beach:
            from game.story.beach_monster_combat import BeachMonsterCombat
            p = self.app.state["player"]
            self.beach_combat = BeachMonsterCombat(p["x"], p["y"],
                                                   self.boss.x, self.boss.y)
            self.progress["chapter_started"] = True
            self.seed_collectables()

    def seed_collectables(self):
        from game.collectable_manager import ensure_collectables_state
        ensure_collectables_state(self.app.state)
        if self.progress.get("beach_drops_spawned"):
            return
        item_id = next((i for i in ("wood", "driftwood", "stone") if get_item_data(i)), None)
        if not item_id:
            return
        for i, (x, y) in enumerate(((265, 510), (420, 620), (540, 420))):
            self.app.state["collectables"].append({
                "id": "brumazul_" + str(i), "item_id": item_id,
                "amount": 1, "x": x, "y": y, "radius": 10,
            })
        self.progress["beach_drops_spawned"] = True

    def try_chop_notification_demo_tree(self, mouse_pos):
        """Single test tree: chop with an axe, then collect several wood drops."""
        from game.inventory.hotbar_manager import get_active_tool
        if get_active_tool(self.app.state) != "axe" or self.app.state.get("notification_demo_tree_cut"):
            return False
        player = self.app.state["player"]
        cx, cy = get_camera_position(player["x"], player["y"], WIDTH, HEIGHT,
                                     self.area_layout.get("width", 900), self.area_layout.get("height", 760))
        target = (680, 285)
        if math.dist((mouse_pos[0] + cx, mouse_pos[1] + cy), target) > 43:
            return False
        if math.dist((player["x"], player["y"]), target) > 100:
            self.app.add_log("Acércate al árbol para talarlo.")
            return True
        from game.collectable_manager import spawn_collectables_from_drops
        self.app.state["notification_demo_tree_cut"] = True
        spawn_collectables_from_drops(self.app.state,
                                      [{"item_id": "wood", "amount": 3},
                                       {"item_id": "wood", "amount": 2},
                                       {"item_id": "wood", "amount": 4}], *target)
        self.app.add_log("Árbol talado. Acércate a recoger la madera.", show_notification=False)
        self.autosave()
        return True

    def interact_farm(self, click_position=None):
        """Collect original wood piles and repair each original fence gap."""
        from game.story_events.story_event_manager import dispatch_story_event
        p = self.app.state["player"]
        layout = self.area_layout
        progress = self.app.state.setdefault("farm_repairs", {})
        collected = progress.setdefault("collected_wood", [])
        repaired = progress.setdefault("repaired_fences", [])
        wood = progress.setdefault("wood", 0)
        cx, cy = get_camera_position(p["x"], p["y"], WIDTH, HEIGHT, layout.get("width", 900), layout.get("height", 760))
        clicked = (click_position[0] + cx, click_position[1] + cy) if click_position is not None else None
        for i, position in enumerate(layout.get("wood_piles", [])):
            if i not in collected and (math.dist((p["x"], p["y"]), position) <= 70 or (clicked is not None and math.dist(clicked, position) <= 32)):
                if not receive(self.app.state, "wood", layout.get("wood_per_pile", 5)):
                    return True
                collected.append(i)
                self.npc_dialogue = get_chapter_dialogue("farm_wood_pickup", wood=quantity(self.app.state, "wood"))
                self.autosave()
                return True
        # El porton de reparacion esta dentro de la finca, separado del
        # paso real al pueblo (x=844): interactuar no cambia de escenario.
        gate_marker = (770, 445)
        gate_near = math.dist((p["x"], p["y"]), gate_marker) <= 85
        gate_clicked = clicked is not None and math.dist(clicked, gate_marker) <= 42
        if (gate_clicked or (clicked is None and gate_near)) and self.app.state["quests"]["un_techo_propio"] in ("repair_fence", "inspect_gate", "get_bolt"):
            stage = self.app.state["quests"]["un_techo_propio"]
            if stage in ("repair_fence", "inspect_gate"):
                self.npc_dialogue = get_chapter_dialogue("farm_gate_inspect")
            else:
                wood_cost = layout.get("door_cost", {}).get("wood", 15)
                bolt_cost = layout.get("door_cost", {}).get("metal_bolt", 1)
                bolts = quantity(self.app.state, "metal_bolt")
                if spend_bundle(self.app.state, {"wood": wood_cost, "metal_bolt": bolt_cost}):
                    progress["gate_repaired"] = True
                    dispatch_story_event(self.app, "object_repaired", {"object_id": "farm_gate"})
                    self.npc_dialogue = get_chapter_dialogue("farm_gate_repaired")
                else:
                    self.npc_dialogue = get_chapter_dialogue("farm_gate_requirements", cost=wood_cost, bolt_cost=bolt_cost, wood=quantity(self.app.state, "wood"), bolts=bolts)
            self.autosave()
            return True
        if self.app.state["quests"]["un_techo_propio"] != "repair_fence":
            return False
        for gap in layout.get("fence_gaps", []):
            x, y, w, h = gap["rect"]
            if gap["id"] in repaired:
                continue
            near_player = x - 90 <= p["x"] <= x + w + 90 and y - 90 <= p["y"] <= y + h + 90
            on_click = clicked is not None and x - 25 <= clicked[0] <= x + w + 25 and y - 25 <= clicked[1] <= y + h + 25
            if not (near_player or on_click):
                continue
            cost = gap.get("cost", 10)
            if quantity(self.app.state, "wood") < cost:
                self.npc_dialogue = get_chapter_dialogue("farm_fence_need_wood", cost=cost, wood=quantity(self.app.state, "wood"))
                return True
            if not spend(self.app.state, "wood", cost):
                return True
            repaired.append(gap["id"])
            from game.notifications import notify_quest
            notify_quest(self.app, f"Has arreglado {len(repaired)} de {len(layout['fence_gaps'])} vallas.")
            self.npc_dialogue = get_chapter_dialogue("farm_fence_repaired", done=len(repaired), total=len(layout["fence_gaps"]), wood=quantity(self.app.state, "wood"))
            self.autosave()
            return True
        return False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if self.phase in ("fade", "port_departure", "port_fade", "elder_enters", "keeper_exits", "elder_exits"):
            return True
        if self.phase == "dialogue":
            if event.type == pygame.KEYDOWN and self.index == INTRO["choice_index"]:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.choice = (self.choice - 1) % len(CHOICES)
                    return True
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.choice = (self.choice + 1) % len(CHOICES)
                    return True
            if (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                if self.index == INTRO["choice_index"]:
                    self.response = RESPONSES[self.choice]
                self.index += 1
                self.process_script()
            return True
        if self.shop_id is not None:
            from game.trading.chapter_trade import handle_event as handle_trade_event
            return handle_trade_event(self, event)
        if self.shop_prompt is not None:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_h):
                    self.shop_talk_bypass = True
                    self.shop_prompt = None
                    try:
                        self.talk_to_nearby()
                    finally:
                        self.shop_talk_bypass = False
                elif event.key in (pygame.K_2, pygame.K_c, pygame.K_RETURN):
                    self.shop_id = self.shop_prompt
                    self.shop_prompt = None
                    self.shop_selection = None
                    self.shop_page = 0
                elif event.key in (pygame.K_3, pygame.K_ESCAPE):
                    self.shop_prompt = None
            return True
        if self.sleep_confirmation:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_s, pygame.K_RETURN):
                    self.sleep_confirmation = False
                    self.app.sleep_day()
                    for key in ("health", "energy"):
                        meter = self.app.state.setdefault(key, {})
                        meter["current"] = meter.get("max", 10)
                    self.autosave()
                    self.app.add_log("Has descansado. Son las 06:00. Partida guardada.")
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self.sleep_confirmation = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.sleep_confirmation = False
            return True
        if self.npc_dialogue is not None:
            if (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_ESCAPE)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.npc_dialogue_index += 1
                if self.npc_dialogue_index >= len(self.npc_dialogue[1]):
                    self.npc_dialogue = None
                    self.npc_dialogue_index = 0
                    if self.port_departure:
                        self.phase = "port_departure"
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.app.menu_open and not self.app.stash_open:
            from game.hud.hotbar_widget import hotbar_hit_index
            from game.input.input_manager import select_active_hotbar_slot
            index = hotbar_hit_index(self.app, event.pos)
            if index is not None:
                select_active_hotbar_slot(self.app, index)
                return True
        if self.scene_id in ("brumazul_casa_almarin", "brumazul_taller_almarin") and not self.app.menu_open and not self.app.stash_open and (
            (event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_RETURN))
            or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
        ):
            key = "bed" if self.scene_id == "brumazul_casa_almarin" else "chest"
            position = self.area_layout.get(key)
            player = self.app.state["player"]
            if position and math.dist((player["x"], player["y"]), position) <= 85:
                if self.scene_id == "brumazul_casa_almarin":
                    self.sleep_confirmation = True
                else:
                    from game.inventory.stash_state import ensure_stash_state
                    ensure_stash_state(self.app.state)
                    self.app.slot_ui_state.clear()
                    self.app.stash_open = True
                return True
        # A left-click during an active nearby encounter is an attack, not NPC interaction.
        if self.chapter_area and not self.app.menu_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hasattr(self, "encounter_units"):
            player = self.app.state["player"]
            enemies = self.encounter_units + ([self.encounter_boss] if self.encounter_boss else [])
            if any(math.dist((player["x"], player["y"]), (enemy["x"], enemy["y"])) < 85 for enemy in enemies):
                from game.story.chapter_01_encounters import attack as attack_encounter
                if attack_encounter(self):
                    return True
        if self.scene_id == "brumazul_granja" and not self.app.menu_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.try_chop_notification_demo_tree(event.pos):
                return True
        if self.scene_id == "brumazul_granja" and not self.app.menu_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            from game.inventory.hotbar_manager import get_active_tool
            if get_active_tool(self.app.state) == "hoe":
                from game.input.input_manager import try_remove_placed_with_hoe
                if try_remove_placed_with_hoe(self.app, event.pos):
                    return True
            from game.farming.chapter_farming import interact as interact_farming
            from game.inventory.hotbar_manager import get_active_item_data, get_active_tool
            active_item = get_active_item_data(self.app.state)
            farming_selected = get_active_tool(self.app.state) in ("hoe", "watering_can", "scythe") or (
                active_item is not None and active_item.get("type") == "seed"
            )
            if farming_selected:
                # Farming clicks are tile-specific. Never pass a missed tile click
                # to nearby-object, generic interaction or combat handlers.
                interact_farming(self, event.pos)
                return True
        if (self.tavern or self.village or self.chapter_area) and not self.app.menu_open and ((event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_RETURN)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)):
            if self.scene_id == "brumazul_granja" and self.interact_farm(event.pos if event.type == pygame.MOUSEBUTTONDOWN else None):
                return True
            if self.talk_to_nearby(event.pos if event.type == pygame.MOUSEBUTTONDOWN else None):
                return True
        if self.chapter_area and not self.app.menu_open and ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)):
            from game.story.chapter_01_encounters import attack as attack_encounter
            if attack_encounter(self):
                return True
        if self.beach and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.app.menu_open:
            self.attack(event.pos)
            return True
        return super().handle_event(event)

    def process_script(self):
        if self.index >= len(SCRIPT):
            self.finish_intro()
            return
        cue = SCRIPT[self.index][0]
        if cue == "@elder_enters":
            self.phase = "elder_enters"
            self.show_elder = True
        elif cue == "@innkeeper_exits":
            self.phase = "keeper_exits"
        elif cue == "@elder_exits":
            self.phase = "elder_exits"
        elif cue == "@fade":
            self.phase = "fade"
            self.fade = 0.0
        else:
            self.phase = "dialogue"

    def finish_intro(self):
        self.progress["intro_finished"] = True
        self.progress["mission"] = "las_tierras_de_almarin"
        self.app.state["player"]["x"] = 400
        self.app.state["player"]["y"] = 440
        self.phase = "free"
        self.app.add_log(get_chapter_ui_text("mission_started"))
        self.autosave()

    def autosave(self):
        try:
            save_state(self.app.state)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            self.app.add_log("No se pudo guardar: " + str(error))

    def update(self, dt):
        dt = min(dt, 0.05)
        self.door_cooldown = max(0, self.door_cooldown - dt)
        self.save_elapsed += dt
        if self.save_elapsed >= 2.0:
            self.save_elapsed = 0.0
            self.autosave()
        if self.phase == "port_departure":
            self.port_departure_progress = min(1.0, self.port_departure_progress + dt / 2.5)
            if self.port_departure_progress >= 1.0:
                self.phase = "port_fade"
                self.fade = 0.0
            return
        if self.phase == "port_fade":
            self.fade = min(1.0, self.fade + dt / 1.0)
            if self.fade >= 1.0:
                self.port_departure = False
                self.phase = "free"
                self.fade = 0.0
                self.autosave()
            return
        if self.beach:
            self.app.update_farm_scene(dt)
            if self.app.menu_open or self.app.stash_open:
                return
            self.attack_timer = max(0, self.attack_timer - dt)
            p = self.app.state["player"]
            events, defeated = self.beach_combat.update(dt, p["x"], p["y"])
            self.boss.update(self.beach_combat.monster.x, self.beach_combat.monster.y)
            self.boss_awake = self.beach_combat.monster.awake
            self.boss_hp = self.beach_combat.monster.hp
            for event in events:
                if event.kind == "telegraph" and event.actor == "beach_monster":
                    self.boss_timer = event.duration
            if defeated:
                self.app.state["health"]["current"] = 0
                self.wake_at_inn()
                return
            if not self.door_cooldown and self.phase == "free" and self.npc_dialogue is None:
                from game.scenes.chapter_area_navigation import transition_chapter_scene
                if transition_chapter_scene(self.app, self.scene_id, self.app.state["player"]):
                    self.autosave()
                    return
        elif self.phase == "elder_enters":
            self.elder.y -= 100 * dt
            if self.elder.y <= 465:
                self.elder.y = 465
                self.index += 1
                self.process_script()
        elif self.phase == "keeper_exits":
            self.keeper.y += 110 * dt
            if self.keeper.y >= 620:
                self.show_keeper = False
                self.index += 1
                self.process_script()
        elif self.phase == "elder_exits":
            self.elder.y += 100 * dt
            if self.elder.y >= 625:
                self.show_elder = False
                self.index += 1
                self.process_script()
        elif self.phase == "fade":
            self.fade = min(1.0, self.fade + dt * 0.85)
            if self.fade >= 1:
                self.finish_intro()
        elif self.phase == "free" and self.npc_dialogue is None:
            from game.story.chapter_01_encounters import update as update_encounters
            update_encounters(self, dt)
            p = self.app.state["player"]
            old_position = (p["x"], p["y"])
            self.app.update_farm_scene(dt)
            if self.village or self.chapter_area:
                from game.scenes.chapter_area_navigation import can_walk_chapter_area, find_chapter_exit
                if not can_walk_chapter_area(self.scene_id, p["x"], p["y"], self.area_layout) and not find_chapter_exit(self.scene_id, p["x"], p["y"], self.area_layout):
                    p["x"], p["y"] = old_position
            if self.door_cooldown:
                return
            from game.scenes.chapter_area_navigation import transition_chapter_scene
            if transition_chapter_scene(self.app, self.scene_id, p, self.area_layout):
                self.autosave()

    def wake_at_inn(self):
        self.app.state["health"]["current"] = self.app.state["health"]["max"]
        self.progress["beach_completed"] = True
        self.transition("brumazul_posada", "despertar")
        # Primer punto de control: al reabrir la partida comienza en la posada.
        self.autosave()

    def transition(self, scene_id, spawn_id):
        if self.app.scene_manager.change_scene(scene_id, payload={"target_spawn_id": spawn_id}):
            self.app.dispatch_scene_entered_event()
            self.autosave()

    def attack(self, mouse):
        if self.attack_timer > 0:
            return
        self.attack_timer = 0.42
        p = self.app.state["player"]
        cx, cy = get_camera_position(p["x"], p["y"], WIDTH, HEIGHT, 704 if self.beach else 800, 704 if self.beach else 800)
        direction = pygame.Vector2(mouse[0] + cx - p["x"], mouse[1] + cy - p["y"])
        target = self.boss - pygame.Vector2(p["x"], p["y"])
        if direction.length_squared() and target.length_squared() and target.length() < 105:
            if direction.normalize().dot(target.normalize()) > 0.35:
                self.beach_combat.hit_monster(25)
                self.boss_hp = self.beach_combat.monster.hp

    def talk_to_nearby(self, click_position=None):
        from game.story_events.story_event_manager import dispatch_story_event
        p = self.app.state["player"]
        if not self.shop_talk_bypass:
            if self.village:
                for name, race, pos, dialogue_id in VILLAGE_NPCS:
                    npc_id = {"HERRERO": "herrero", "BOTICA": "botica", "HERBOLARIO": "herbolario"}.get(name)
                    if npc_id and math.dist((p["x"], p["y"]), pos) < 90:
                        self.shop_prompt = npc_id
                        return True
            if self.chapter_area:
                for node in self.area_layout.get("nodes", []):
                    if node["id"] == "sylvarin" and math.dist((p["x"], p["y"]), node["position"]) < node.get("radius", 65):
                        self.shop_prompt = "sylvarin"
                        return True
        if self.tavern and self.app.state["quests"]["un_techo_propio"] in ("find_elder_port", "complete"):
            progress = self.app.state.setdefault("brumazul", {})
            if not progress.get("elder_clue_seen") and math.dist((p["x"], p["y"]), (480, 395)) < 135:
                progress["elder_clue_seen"] = True
                self.npc_dialogue = get_chapter_dialogue("inn_elder_clue")
                self.autosave()
                return True
        if self.scene_id == "brumazul_puerto":
            elder = self.area_layout.get("elder")
            if elder and math.dist((p["x"], p["y"]), elder) < 90:
                stage = self.app.state["quests"]["un_techo_propio"]
                if stage == "find_elder_port":
                    self.npc_dialogue = get_chapter_dialogue("elder_port_followup")
                    if receive(self.app.state, "father_sword", 1, receipt_id="chapter01_father_sword") or "chapter01_father_sword" in self.app.state.get("item_receipts", []):
                        from game.notifications import notify_important
                        notify_important(self.app, "Has recibido la espada del padre.", "Objeto importante")
                        dispatch_story_event(self.app, "npc_talked", {"npc_id": "anciano_puerto"})
                        self.port_departure = True
                        self.port_departure_progress = 0.0
                    else:
                        self.npc_dialogue = get_chapter_dialogue("inventory_full")
                        from game.notifications import notify_important
                        notify_important(self.app, "Tu inventario está lleno. Libera espacio y vuelve a hablar con el personaje.", "Inventario lleno")
                else:
                    self.npc_dialogue = get_chapter_dialogue("elder_port_idle")
                self.autosave()
                return True
        if self.scene_id == "brumazul_granja":
            elder = self.area_layout.get("elder", [690, 365])
            if math.dist((p["x"], p["y"]), elder) < 90:
                stage = self.app.state["quests"]["un_techo_propio"]
                if stage == "complete":
                    from game.story.chapter_01_quest_manager import ensure_chapter_quests
                    quests = ensure_chapter_quests(self.app.state)
                    if quests["la_ultima_madriguera"] == "ready":
                        if quantity(self.app.state, "father_sword") == 0:
                            self.npc_dialogue = get_chapter_dialogue("elder_farm_need_sword")
                        else:
                            dispatch_story_event(self.app, "npc_talked", {"npc_id": "anciano_granja"})
                            self.app.state.setdefault("chapter_encounters", {}).setdefault("farm_ambush", {})["started"] = True
                            self.npc_dialogue = get_chapter_dialogue("elder_farm_ambush")
                        self.autosave()
                        return True
                    if quests["la_ultima_madriguera"] == "approach":
                        dispatch_story_event(self.app, "npc_talked", {"npc_id": "anciano_granja"})
                        self.npc_dialogue = get_chapter_dialogue("elder_farm_deed")
                        self.autosave()
                        return True
                    if quests["la_ultima_madriguera"] in ("hunt", "boss"):
                        self.npc_dialogue = get_chapter_dialogue("elder_farm_guard")
                        return True
                    return False
                if stage == "find_elder_port":
                    return False
                if stage == "find_elder":
                    self.npc_dialogue = get_chapter_dialogue("elder_farm_first")
                    dispatch_story_event(self.app, "npc_talked", {"npc_id": "anciano"})
                elif len(self.app.state.get("farm_repairs", {}).get("repaired_fences", [])) == len(self.area_layout.get("fence_gaps", [])) and self.area_layout.get("fence_gaps"):
                    if stage in ("repair_fence", "inspect_gate"):
                        dispatch_story_event(self.app, "npc_talked", {"npc_id": "anciano"})
                    self.npc_dialogue = get_chapter_dialogue("elder_fences_done")
                else:
                    self.npc_dialogue = get_chapter_dialogue("elder_fences_pending" if stage == "repair_fence" else "elder_farm_other")
                self.autosave()
                return True
        if self.village:
            smith = next((npc for npc in VILLAGE_NPCS if npc[0] == "HERRERO"), None)
            cx, cy = get_camera_position(p["x"], p["y"], WIDTH, HEIGHT, VILLAGE_LAYOUT["width"], VILLAGE_LAYOUT["height"])
            clicked_smith = click_position is not None and math.dist((click_position[0] + cx, click_position[1] + cy), smith[2]) < 48 if smith else False
            if smith and (math.dist((p["x"], p["y"]), smith[2]) < 110 or clicked_smith):
                quests = self.app.state["quests"]
                stage = quests["un_techo_propio"]
                smith_stage = quests["el_hierro_que_canta"]
                progress = self.app.state.setdefault("farm_repairs", {})
                # The bolt is delivered only on this interaction, never by a
                # dialogue event. A completed quest without the bolt is repaired.
                if stage in ("get_bolt", "inspect_gate") and not progress.get("smith_bolt_claimed") and smith_stage == "completed":
                    smith_stage = "artisan_explained"
                    quests["el_hierro_que_canta"] = smith_stage
                if stage not in ("get_bolt", "inspect_gate", "find_elder_port", "complete"):
                    self.npc_dialogue = get_chapter_dialogue("smith_idle")
                elif smith_stage == "not_started":
                    dispatch_story_event(self.app, "npc_talked", {"npc_id": "herrero"})
                    self.npc_dialogue = get_chapter_dialogue("smith_offer")
                elif smith_stage == "investigate":
                    self.npc_dialogue = get_chapter_dialogue("smith_wait_sylvarin")
                elif smith_stage == "artisan_explained" and not progress.get("smith_bolt_claimed"):
                    if receive(self.app.state, "metal_bolt", 1, receipt_id="chapter01_smith_bolt"):
                        from game.notifications import notify_important
                        notify_important(self.app, "Has recibido un cerrojo.", "Objeto de misión")
                        progress["smith_bolt_claimed"] = True
                        quests["el_hierro_que_canta"] = "completed"
                        self.npc_dialogue = get_chapter_dialogue("smith_reward")
                    elif quantity(self.app.state, "metal_bolt") > 0:
                        progress["smith_bolt_claimed"] = True
                        quests["el_hierro_que_canta"] = "completed"
                        self.npc_dialogue = get_chapter_dialogue("smith_reward")
                    elif "chapter01_smith_bolt" in self.app.state.get("item_receipts", []):
                        # A previous buggy save registered the receipt without
                        # leaving the item in the inventory. Retry the grant.
                        self.app.state["item_receipts"].remove("chapter01_smith_bolt")
                        if receive(self.app.state, "metal_bolt", 1, receipt_id="chapter01_smith_bolt"):
                            progress["smith_bolt_claimed"] = True
                            quests["el_hierro_que_canta"] = "completed"
                            self.npc_dialogue = get_chapter_dialogue("smith_reward")
                        else:
                            self.npc_dialogue = get_chapter_dialogue("inventory_full")
                    else:
                        self.npc_dialogue = get_chapter_dialogue("inventory_full")
                elif smith_stage == "completed" or progress.get("smith_bolt_claimed"):
                    if stage in ("get_bolt", "inspect_gate") and quantity(self.app.state, "metal_bolt") == 0:
                        progress["smith_bolt_claimed"] = False
                        self.app.state.setdefault("item_receipts", [])[:] = [r for r in self.app.state.get("item_receipts", []) if r != "chapter01_smith_bolt"]
                        if receive(self.app.state, "metal_bolt", 1, receipt_id="chapter01_smith_bolt"):
                            progress["smith_bolt_claimed"] = True
                            quests["el_hierro_que_canta"] = "completed"
                            self.npc_dialogue = get_chapter_dialogue("smith_reward")
                        else:
                            self.npc_dialogue = get_chapter_dialogue("inventory_full")
                    else:
                        self.npc_dialogue = get_chapter_dialogue("smith_bolt_delivered")
                else:
                    self.npc_dialogue = get_chapter_dialogue("smith_wait_sylvarin")
                self.autosave()
                return True
        if self.chapter_area:
            for node in self.area_layout.get("nodes", []):
                if math.dist((p["x"], p["y"]), node["position"]) < node.get("radius", 65):
                    npc_id = node["id"]
                    if npc_id == "sylvarin":
                        quests = self.app.state["quests"]
                        metal_stage = quests["el_hierro_que_canta"]
                        rat_stage = quests["cuando_callan_las_campanas"]
                        if metal_stage == "investigate":
                            self.npc_dialogue = get_chapter_dialogue("sylvarin_metal_explained")
                            dispatch_story_event(self.app, "npc_talked", {"npc_id": "sylvarin"})
                            dispatch_story_event(self.app, "rat_nest_offered", {"object_id": "sylvarin"})
                            from game.inventory.inventory_manager import get_item_quantity
                            from game.data.item_database import ITEM_DATABASE
                            if any(item.get("type") == "weapon" and get_item_quantity(self.app.state, item_id) > 0 for item_id, item in ITEM_DATABASE.items()):
                                dispatch_story_event(self.app, "weapon_acquired", {"object_id": "player"})
                        elif rat_stage == "get_weapon":
                            self.npc_dialogue = get_chapter_dialogue("sylvarin_need_weapon")
                        elif rat_stage == "not_started":
                            self.npc_dialogue = get_chapter_dialogue("sylvarin_rats_offer")
                            dispatch_story_event(self.app, "npc_talked", {"npc_id": "sylvarin"})
                        elif rat_stage == "cleared":
                            if receive(self.app.state, "sylvarin_boots", 1, receipt_id="chapter01_sylvarin_boots"):
                                dispatch_story_event(self.app, "npc_talked", {"npc_id": "sylvarin"})
                                self.npc_dialogue = get_chapter_dialogue("sylvarin_rats_cleared")
                            else:
                                self.npc_dialogue = get_chapter_dialogue("inventory_full")
                        elif rat_stage == "completed":
                            self.npc_dialogue = get_chapter_dialogue("sylvarin_intro")
                        else:
                            self.npc_dialogue = get_chapter_dialogue("sylvarin_rats_pending")
                    else:
                        self.npc_dialogue = get_chapter_dialogue("generic_villager")
                        dispatch_story_event(self.app, "npc_talked", {"npc_id": npc_id})
                    self.autosave()
                    return True
            return False
        for name, race, pos, dialogue_id in (VILLAGE_NPCS if self.village else TAVERN_NPCS):
            if math.dist((p["x"], p["y"]), pos) < 65:
                self.npc_dialogue = get_chapter_dialogue(dialogue_id)
                dispatch_story_event(self.app, "npc_talked", {"npc_id": name.lower()})
                return True
        return False

    def draw(self):
        s = self.app.screen
        s.fill(WHITE)
        p = self.app.state["player"]
        world_width = self.area_layout.get("width", 800) if self.chapter_area else (1400 if self.village else 800)
        world_height = self.area_layout.get("height", 800) if self.chapter_area else (1050 if self.village else 800)
        cx, cy = get_camera_position(p["x"], p["y"], WIDTH, HEIGHT, world_width, world_height)
        if self.beach:
            pygame.draw.rect(s, PAPER, (0, 0, WIDTH, HEIGHT))
            pygame.draw.rect(s, (239, 239, 239), pygame.Rect(-cx, -cy, 704, 704))
            pygame.draw.rect(s, LINE, pygame.Rect(-cx, -cy, 704, 704), 1)
            from game.world.collision_manager import get_scene_collision_rects
            for collision in get_scene_collision_rects():
                pygame.draw.rect(s, (194, 194, 194), pygame.Rect(collision.x - cx, collision.y - cy, collision.width, collision.height), 1)
            pygame.draw.rect(s, PALE, pygame.Rect(-cx, -cy, 704, 165))
            pygame.draw.line(s, LINE, (-cx, 165 - cy), (704 - cx, 165 - cy), 1)
            # Sin cuadricula: solo limites del mapa y del sendero.
            for x in (350, 450):
                pygame.draw.line(s, LIGHT, (x - cx, -cy), (x - cx, 360 - cy), 1)
            for obj in self.app.state.get("collectables", []):
                if obj.get("id", "").startswith("brumazul_"):
                    pygame.draw.circle(s, LINE, (int(obj["x"] - cx), int(obj["y"] - cy)), 7, 1)
            # The prologue creature uses the shared combat engine, not the
            # old scripted chase. Show its aggro and telegraph states clearly.
            bx, by = int(self.boss.x - cx), int(self.boss.y - cy)
            creature = self.beach_combat.monster
            active = creature.awake
            preparing = creature.windup > 0
            pygame.draw.ellipse(s, (186, 180, 172), (bx - 46, by + 25, 92, 20))
            body = (132, 70, 67) if preparing else ((100, 93, 112) if active else (124, 126, 130))
            pygame.draw.circle(s, body, (bx, by), 39)
            pygame.draw.circle(s, (61, 55, 67), (bx, by), 39, 3)
            for side in (-1, 1):
                pygame.draw.polygon(s, (61, 55, 67), [
                    (bx + side * 24, by - 23),
                    (bx + side * 43, by - 57),
                    (bx + side * 11, by - 35),
                ])
                pygame.draw.circle(s, (238, 212, 154) if active else (225, 225, 220),
                                   (bx + side * 13, by - 7), 8)
                pygame.draw.circle(s, (43, 37, 42), (bx + side * 13, by - 7), 3)
            pygame.draw.arc(s, (43, 37, 42), (bx - 22, by - 1, 44, 35), 3.35, 6.08, 3)
            if preparing:
                # Wind-up warning is visible in the actual game scene.
                pygame.draw.circle(s, (181, 58, 51), (bx, by), 50, 4)
                px, py = self.app.state["player"]["x"], self.app.state["player"]["y"]
                pygame.draw.line(s, (181, 58, 51), (bx, by),
                                 (int(px - cx), int(py - cy)), 3)
                self.label("!", bx - 4, by - 72)
            elif active:
                pygame.draw.circle(s, (165, 113, 78), (bx, by), 47, 2)
                self.label("!", bx - 4, by - 70)
            self.label("PLAYA DE BRUMAZUL  /  NOCHE", 22, 18)
        elif self.tavern:
            self.draw_tavern(cx, cy)
        elif self.scene_id == "brumazul_pueblo":
            self.draw_village(cx, cy)
        elif self.chapter_area:
            self.draw_chapter_area(cx, cy)
            from game.story.chapter_01_encounters import draw as draw_encounters
            draw_encounters(self, cx, cy)
        else:
            self.draw_room(cx, cy)
        # Brumazul uses its own renderer; include constructions and live preview here.
        from game.world.grid_renderer import draw_placed_objects
        draw_placed_objects(s, self.app.state, cx, cy)
        if self.app.placement_mode:
            from game.construction.placement_mode import draw_placement_preview
            draw_placement_preview(self.app)

        if not self.tavern and self.scene_id != "brumazul_pueblo":
            pygame.draw.circle(s, LINE, (int(p["x"] - cx), int(p["y"] - cy)), 13, 1)
            pygame.draw.circle(s, LIGHT, (int(p["x"] - cx), int(p["y"] - cy - 15)), 8, 1)
        else:
            pygame.draw.circle(s, LINE, (int(p["x"] - cx), int(p["y"] - cy)), 13, 1)
        direction = p.get("direction", "down")
        vectors = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        vx, vy = vectors.get(direction, (0, 1))
        center = (int(p["x"] - cx), int(p["y"] - cy - 7))
        tip = (center[0] + vx * 17, center[1] + vy * 17)
        pygame.draw.line(s, (65, 65, 65), center, tip, 3)
        pygame.draw.circle(s, (65, 65, 65), tip, 3)
        from game.hud.hud_renderer import draw_hud
        draw_hud(self.app)
        from game.notifications import draw_notifications
        draw_notifications(self.app)
        if self.app.menu_open:
            draw_menu(self.app)
        if self.app.stash_open:
            draw_stash_overlay(self.app)
        if self.phase == "dialogue":
            who, line = SCRIPT[self.index]
            if who == "@choice":
                self.draw_dialogue(INTRO["player_speaker"], INTRO["question"], CHOICES, self.choice)
            else:
                self.draw_dialogue(who, self.response if self.index == INTRO["response_index"] else line)
        if self.npc_dialogue:
            self.draw_dialogue(self.npc_dialogue[0], self.npc_dialogue[1][self.npc_dialogue_index])
        if self.shop_prompt is not None:
            from game.trading.chapter_trade import SHOPS
            shop = SHOPS[self.shop_prompt]
            self.draw_dialogue(shop["name"], shop["greeting"] + "  [1] Hablar   [2] Comerciar   [3] Salir")
        if self.shop_id is not None:
            from game.trading.chapter_trade import draw as draw_trade
            draw_trade(self)
        if self.sleep_confirmation:
            self.draw_dialogue("DESCANSAR", "¿Quieres dormir hasta las 06:00 del día siguiente? [S / ENTER] Sí   [N / ESC] No")
        if self.phase in ("fade", "port_fade"):
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(WHITE)
            overlay.set_alpha(int(self.fade * 255))
            s.blit(overlay, (0, 0))

    def draw_room(self, cx, cy):
        s = self.app.screen
        room = pygame.Rect(200 - cx, 200 - cy, 400, 400)
        pygame.draw.rect(s, PAPER, room)
        pygame.draw.rect(s, LINE, room, 1)
        pygame.draw.rect(s, LIGHT, (280 - cx, 400 - cy, 80, 120), 1)
        pygame.draw.rect(s, LIGHT, (480 - cx, 280 - cy, 80, 80), 1)
        self.draw_door(430, 595, 110, 10, cx, cy, "SALON")
        if self.show_keeper:
            self.actor("POSADERA", self.keeper, cx, cy)
        if self.show_elder:
            self.actor("ANCIANO", self.elder, cx, cy)
        self.label("POSADA  /  HABITACION", 22, 18)
        if self.phase == "free":
            self.label(get_chapter_ui_text("room_exit_hint"), 24, 43)

    def draw_door(self, x, y, w, h, cx, cy, label=""):
        rect = pygame.Rect(int(x - cx), int(y - cy), int(w), int(max(h, 8)))
        pygame.draw.rect(self.app.screen, PALE, rect)
        pygame.draw.rect(self.app.screen, LINE, rect, 2)
        if label:
            self.label(label, rect.centerx - min(55, len(label) * 3), rect.y - 19)

    def draw_tavern(self, cx, cy):
        s = self.app.screen
        # Salon mas compacto; puertas y transiciones comparten coordenadas.
        pygame.draw.rect(s, PAPER, pygame.Rect(180 - cx, 220 - cy, 440, 400))
        pygame.draw.rect(s, LINE, pygame.Rect(180 - cx, 220 - cy, 440, 400), 2)
        for x, y, w, h in ((225, 270, 85, 55), (460, 440, 95, 65), (395, 320, 85, 55)):
            pygame.draw.rect(s, LIGHT, (x - cx, y - cy, w, h), 1)
        self.draw_door(430, 100, 110, 10, cx, cy, "HABITACION")
        self.draw_door(430, 740, 110, 10, cx, cy, "PUEBLO")
        for name, race, pos, _ in TAVERN_NPCS:
            self.actor(name + " / " + race, pygame.Vector2(pos), cx, cy)
        self.label("POSADA  /  SALON", 22, 18)
        self.label(get_chapter_ui_text("tavern_hint"), 22, 43)

    def draw_chapter_area(self, cx, cy):
        layout = self.area_layout
        screen = self.app.screen
        for x, y, w, h in layout.get("walkable", []):
            pygame.draw.rect(screen, PALE, (x - cx, y - cy, w, h))
        if self.scene_id == "brumazul_granja":
            from game.world.grid_renderer import draw_tilled_cells, draw_watered_cells, draw_crops, draw_wild_bushes, draw_farm_reach_grid
            from game.inventory.hotbar_manager import get_active_tool, get_active_item_data
            active_item = get_active_item_data(self.app.state)
            mode = "eight" if get_active_tool(self.app.state) == "watering_can" or (
                active_item and active_item.get("type") == "seed"
            ) else "cardinal"
            draw_farm_reach_grid(screen, self.app.state["player"], cx, cy, (45, 45, 810, 670), mode)
            draw_tilled_cells(screen, self.app.state, cx, cy)
            draw_watered_cells(screen, self.app.state, cx, cy)
            draw_crops(screen, self.app.state, cx, cy)
            draw_wild_bushes(screen, self.app.state, cx, cy)
        if self.scene_id == "brumazul_granja" and not self.app.state.get("notification_demo_tree_cut"):
            from game.ui.sprite_renderer import draw_sprite_centered
            if draw_sprite_centered(screen, "assets/world/tree.png", 680 - cx, 285 - cy, 76, 110) is None:
                pygame.draw.circle(screen, (86, 119, 73), (int(680 - cx), int(270 - cy)), 31)
                pygame.draw.rect(screen, (117, 81, 52), (672 - cx, 285 - cy, 16, 34))
        buildings = list(layout.get("buildings", []))
        buildings.extend(layout[k] for k in ("house", "workshop") if isinstance(layout.get(k), dict))
        for building in buildings:
            if "rect" not in building:
                continue
            x, y, w, h = building["rect"]
            pygame.draw.rect(screen, PAPER, (x - cx, y - cy, w, h))
            pygame.draw.rect(screen, LINE, (x - cx, y - cy, w, h), 2)
            self.label(building.get("label", ""), x - cx + 5, y - cy + 8)
        for door in layout.get("doors", []) + layout.get("exits", []):
            if "rect" in door:
                x, y, w, h = door["rect"]
                self.draw_door(x, y, w, h, cx, cy, door.get("label", ""))
        for building in buildings:
            if "door" in building:
                door = building["door"]
                if len(door) == 4:
                    self.draw_door(*door, cx, cy, building.get("label", ""))
                elif len(door) == 2:
                    self.draw_door(door[0] - 20, door[1] - 5, 40, 10, cx, cy, building.get("label", ""))
        if self.scene_id == "brumazul_casa_almarin" and "bed" in layout:
            x, y = layout["bed"]
            bed = pygame.Rect(int(x - cx - 27), int(y - cy - 39), 54, 78)
            pygame.draw.rect(screen, (125, 125, 125), bed, border_radius=5)
            pygame.draw.rect(screen, (205, 205, 205), bed.inflate(-8, -8), border_radius=4)
            pygame.draw.rect(screen, (240, 240, 240), (bed.x + 8, bed.y + 7, bed.width - 16, 17), border_radius=4)
            pygame.draw.rect(screen, (160, 160, 160), (bed.x + 7, bed.y + 28, bed.width - 14, bed.height - 37), border_radius=3)
            self.label("CAMA [E]", x - cx - 31, y - cy - 60)
        if self.scene_id == "brumazul_taller_almarin" and "chest" in layout:
            x, y = layout["chest"]
            chest_rect = pygame.Rect(int(x - cx - 24), int(y - cy - 17), 48, 34)
            pygame.draw.rect(screen, (111, 71, 42), chest_rect, border_radius=4)
            pygame.draw.rect(screen, (56, 39, 28), chest_rect, 3, border_radius=4)
            pygame.draw.rect(screen, (192, 152, 75), (int(x - cx - 4), int(y - cy - 14), 8, 28))
            pygame.draw.rect(screen, (222, 185, 98), (int(x - cx - 5), int(y - cy - 3), 10, 9))
            self.label("COFRE [E]", x - cx - 34, y - cy - 43)
        if self.scene_id == "brumazul_granja":
            progress = self.app.state.setdefault("farm_repairs", {})
            collected = progress.get("collected_wood", [])
            repaired = progress.get("repaired_fences", [])
            for i, (x, y) in enumerate(layout.get("wood_piles", [])):
                if i not in collected:
                    pygame.draw.rect(screen, LIGHT, (x - cx - 11, y - cy - 7, 22, 14))
                    self.label("MADERA [E]", x - cx - 32, y - cy - 28)
            for gap in layout.get("fence_gaps", []):
                x, y, w, h = gap["rect"]
                done = gap["id"] in repaired
                pygame.draw.rect(screen, LINE if done else INK, (x - cx, y - cy, w, h), 4 if done else 2)
                if not done:
                    self.label("VALLA ROTA [E]", x - cx - 20, y - cy - 23)
            gate_done = progress.get("gate_repaired", False)
            gate_x, gate_y = 770, 445
            pygame.draw.rect(screen, PALE if not gate_done else LIGHT, (gate_x - cx - 25, gate_y - cy - 13, 50, 26))
            pygame.draw.rect(screen, LINE, (gate_x - cx - 25, gate_y - cy - 13, 50, 26), 2)
            self.label("PORTON REPARADO" if gate_done else "PORTON [E / CLIC]", gate_x - cx - 55, gate_y - cy - 35)
            self.label("MADERA: %d  |  VALLAS: %d/3" % (quantity(self.app.state, "wood"), len(repaired)), 22, 91)
        for node in layout.get("nodes", []):
            x, y = node["position"]
            self.actor(node.get("label", node["id"]), pygame.Vector2(x, y), cx, cy)
        if "elder" in layout and self.scene_id in ("brumazul_granja", "brumazul_puerto"):
            stage = self.app.state["quests"]["un_techo_propio"]
            visible = (self.scene_id == "brumazul_granja" and stage in ("find_elder", "repair_fence", "inspect_gate", "get_bolt", "complete")) or (self.scene_id == "brumazul_puerto" and (stage == "find_elder_port" or self.port_departure))
            if visible:
                elder_position = pygame.Vector2(layout["elder"])
                if self.scene_id == "brumazul_puerto" and self.port_departure:
                    elder_position.y += self.port_departure_progress * 180
                self.actor("ANCIANO [E]", elder_position, cx, cy)
        pygame.draw.rect(screen, LINE, (-cx, -cy, layout.get("width", 800), layout.get("height", 704)), 2)
        self.label(self.scene_id.replace("brumazul_", "").upper(), 22, 18)
        if self.scene_id == "brumazul_granja":
            stage = self.app.state["quests"]["un_techo_propio"]
            objective = {"find_elder": "MISION: Habla con el anciano [E]", "repair_fence": "MISION: Repara las tres vallas", "inspect_gate": "MISION: Examina la puerta de la finca"}.get(stage)
            if objective:
                self.label(objective, 22, 43)

    def draw_village(self, cx, cy):
        s = self.app.screen
        # Chapter-one geometry; shared with the original simulator scene data.
        for x, y, w, h in VILLAGE_LAYOUT["walkable"]:
            pygame.draw.rect(s, PALE, (x - cx, y - cy, w, h))
        for building in VILLAGE_LAYOUT["buildings"]:
            x, y, w, h = building["rect"]
            pygame.draw.rect(s, PAPER, (x - cx, y - cy, w, h))
            pygame.draw.rect(s, LINE, (x - cx, y - cy, w, h), 2)
            self.label(building["label"], x - cx + 8, y - cy + 10)
            dx, dy, dw, dh = building["door"]
            self.draw_door(dx, dy, dw, dh, cx, cy, building.get("label", ""))
        for exit_data in VILLAGE_LAYOUT.get("doors", []):
            x, y, w, h = exit_data["rect"]
            self.draw_door(x, y, w, h, cx, cy, exit_data.get("label", ""))
        for name, race, pos, _ in VILLAGE_NPCS:
            self.actor(name, pygame.Vector2(pos), cx, cy)
        pygame.draw.rect(s, LINE, (-cx, -cy, 1400, 1050), 2)
        self.label("BRUMAZUL  /  PUEBLO", 22, 18)
        self.label(get_chapter_ui_text("village_hint"), 22, 43)

    def actor(self, name, pos, cx, cy):
        x, y = int(pos.x - cx), int(pos.y - cy)
        pygame.draw.circle(self.app.screen, LINE, (x, y), 15, 1)
        self.label(name, x - 35, y - 33)

    def draw_dialogue(self, speaker, message, choices=None, selected=0):
        draw_chapter_conversation(self, speaker, message, choices, selected)

    def label(self, value, x, y):
        self.app.screen.blit(self.app.small_font.render(str(value), True, INK), (int(x), int(y)))
