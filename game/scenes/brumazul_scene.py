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
from game.dialogue.chapter_dialogues import get_chapter_dialogue, get_chapter_intro, get_chapter_npcs
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
        self.door_cooldown = 0.8
        self.save_elapsed = 0.0
        if self.beach:
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
        if (gate_clicked or (clicked is None and gate_near)) and self.app.state["quests"]["un_techo_propio"] in ("inspect_gate", "get_bolt"):
            stage = self.app.state["quests"]["un_techo_propio"]
            if stage == "inspect_gate":
                dispatch_story_event(self.app, "object_interacted", {"object_id": "farm_gate"})
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
            self.npc_dialogue = get_chapter_dialogue("farm_fence_repaired", done=len(repaired), total=len(layout["fence_gaps"]), wood=quantity(self.app.state, "wood"))
            self.autosave()
            if len(repaired) == len(layout["fence_gaps"]):
                dispatch_story_event(self.app, "object_repaired", {"object_id": "fence"})
                self.npc_dialogue = get_chapter_dialogue("farm_fences_complete")
            return True
        return False

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if self.phase == "fade" or self.phase in ("elder_enters", "keeper_exits", "elder_exits"):
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
                if self.index == 10:
                    self.response = RESPONSES[self.choice]
                self.index += 1
                self.process_script()
            return True
        if self.npc_dialogue is not None:
            if (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_ESCAPE)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.npc_dialogue = None
            return True
        if (self.tavern or self.village or self.chapter_area) and not self.app.menu_open and ((event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_RETURN)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)):
            if self.scene_id == "brumazul_granja" and self.interact_farm(event.pos if event.type == pygame.MOUSEBUTTONDOWN else None):
                return True
            if self.talk_to_nearby():
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
        self.app.add_log("MISION: LAS TIERRAS DE ALMARIN - Busca al anciano en la finca")
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
        if self.beach:
            self.app.update_farm_scene(dt)
            if self.app.menu_open or self.app.stash_open:
                return
            self.attack_timer = max(0, self.attack_timer - dt)
            self.boss_timer = max(0, self.boss_timer - dt)
            p = pygame.Vector2(self.app.state["player"]["x"], self.app.state["player"]["y"])
            if not self.boss_awake and p.distance_to(self.boss) <= 160:
                self.boss_awake = True
            if self.boss_awake:
                delta = p - self.boss
                if delta.length_squared():
                    self.boss += delta.normalize() * min(delta.length(), 42 * dt)
                if delta.length() <= 77 and self.boss_timer <= 0:
                    self.app.state["health"]["current"] = 0
                    self.wake_at_inn()
                    return
                self.boss_timer = max(0, self.boss_timer - dt)
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
            p = self.app.state["player"]
            old_position = (p["x"], p["y"])
            self.app.update_farm_scene(dt)
            if self.village or self.chapter_area:
                from game.scenes.chapter_area_navigation import can_walk_chapter_area, find_chapter_exit
                if not can_walk_chapter_area(self.scene_id, p["x"], p["y"], self.area_layout) and not find_chapter_exit(self.scene_id, p["x"], p["y"], self.area_layout):
                    p["x"], p["y"] = old_position
            if self.door_cooldown:
                return
            if self.tavern:
                if p["y"] < 225 and 425 < p["x"] < 550:
                    self.transition("brumazul_posada", "retorno")
                elif p["y"] > 615 and 425 < p["x"] < 550:
                    self.transition("brumazul_pueblo", "entrada")
            elif self.village or self.chapter_area:
                self.update_chapter_exits(p)
            else:
                if p["y"] > 575 and 430 < p["x"] < 540:
                    self.transition("brumazul_taberna", "desde_habitacion")

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
                self.boss_hp = max(0, self.boss_hp - 25)

    def talk_to_nearby(self):
        from game.story_events.story_event_manager import dispatch_story_event
        p = self.app.state["player"]
        if self.scene_id == "brumazul_granja":
            elder = self.area_layout.get("elder", [690, 365])
            if math.dist((p["x"], p["y"]), elder) < 90:
                stage = self.app.state["quests"]["un_techo_propio"]
                if stage == "find_elder":
                    self.npc_dialogue = get_chapter_dialogue("elder_farm_first")
                    dispatch_story_event(self.app, "npc_talked", {"npc_id": "anciano"})
                elif len(self.app.state.get("farm_repairs", {}).get("repaired_fences", [])) == len(self.area_layout.get("fence_gaps", [])) and self.area_layout.get("fence_gaps"):
                    if stage == "repair_fence":
                        dispatch_story_event(self.app, "object_repaired", {"object_id": "fence"})
                    self.npc_dialogue = get_chapter_dialogue("elder_fences_done")
                else:
                    self.npc_dialogue = get_chapter_dialogue("elder_fences_pending" if stage == "repair_fence" else "elder_farm_other")
                return True
        if self.village:
            smith = next((npc for npc in VILLAGE_NPCS if npc[0] == "HERRERO"), None)
            if smith and math.dist((p["x"], p["y"]), smith[2]) < 85:
                quests = self.app.state["quests"]
                stage = quests["un_techo_propio"]
                smith_stage = quests["el_hierro_que_canta"]
                if stage not in ("get_bolt", "inspect_gate", "find_elder_port", "complete"):
                    self.npc_dialogue = get_chapter_dialogue("smith_idle")
                elif smith_stage == "not_started":
                    dispatch_story_event(self.app, "npc_talked", {"npc_id": "herrero"})
                    self.npc_dialogue = get_chapter_dialogue("smith_offer")
                elif smith_stage == "investigate":
                    self.npc_dialogue = get_chapter_dialogue("smith_wait_sylvarin")
                elif smith_stage == "artisan_explained":
                    dispatch_story_event(self.app, "npc_talked", {"npc_id": "herrero"})
                    progress = self.app.state.setdefault("farm_repairs", {})
                    if progress.get("smith_bolt_claimed") or receive(self.app.state, "metal_bolt", 1, receipt_id="chapter01_smith_bolt"):
                        progress["smith_bolt_claimed"] = True
                        self.npc_dialogue = get_chapter_dialogue("smith_reward")
                    else:
                        self.npc_dialogue = get_chapter_dialogue("inventory_full")
                        return True
                else:
                    self.npc_dialogue = get_chapter_dialogue("smith_done")
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
                        elif rat_stage == "not_started":
                            self.npc_dialogue = get_chapter_dialogue("sylvarin_rats_offer")
                            dispatch_story_event(self.app, "npc_talked", {"npc_id": "sylvarin"})
                        elif rat_stage == "cleared":
                            dispatch_story_event(self.app, "npc_talked", {"npc_id": "sylvarin"})
                            self.npc_dialogue = get_chapter_dialogue("sylvarin_rats_cleared")
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
            bx, by = int(self.boss.x - cx), int(self.boss.y - cy)
            pygame.draw.circle(s, INK, (bx, by), 40, 2)
            pygame.draw.circle(s, INK, (bx - 13, by - 9), 6, 2)
            pygame.draw.circle(s, INK, (bx + 13, by - 9), 6, 2)
            pygame.draw.arc(s, LINE, (bx - 28, by - 14, 56, 48), 0.25, 2.85, 2)
            self.label("PLAYA DE BRUMAZUL  /  NOCHE", 22, 18)
        elif self.tavern:
            self.draw_tavern(cx, cy)
        elif self.scene_id == "brumazul_pueblo":
            self.draw_village(cx, cy)
        elif self.chapter_area:
            self.draw_chapter_area(cx, cy)
        else:
            self.draw_room(cx, cy)
        if not self.tavern and self.scene_id != "brumazul_pueblo":
            pygame.draw.circle(s, LINE, (int(p["x"] - cx), int(p["y"] - cy)), 13, 1)
            pygame.draw.circle(s, LIGHT, (int(p["x"] - cx), int(p["y"] - cy - 15)), 8, 1)
        else:
            pygame.draw.circle(s, LINE, (int(p["x"] - cx), int(p["y"] - cy)), 13, 1)
        self.draw_minimal_hud()
        if self.app.menu_open:
            draw_menu(self.app)
        if self.app.stash_open:
            draw_stash_overlay(self.app)
        if self.phase == "dialogue":
            who, line = SCRIPT[self.index]
            if who == "@choice":
                self.draw_dialogue("TU", INTRO["question"], CHOICES, self.choice)
            else:
                self.draw_dialogue(who, self.response if self.index == INTRO["response_index"] else line)
        if self.npc_dialogue:
            self.draw_dialogue(self.npc_dialogue[0], "  ".join(self.npc_dialogue[1]))
        if self.phase == "fade":
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
            self.label("Puerta al salon: abajo", 24, 43)

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
        self.draw_door(425, 215, 125, 12, cx, cy, "HABITACION")
        self.draw_door(425, 610, 125, 12, cx, cy, "PUEBLO")
        for name, race, pos, _ in TAVERN_NPCS:
            self.actor(name + " / " + race, pygame.Vector2(pos), cx, cy)
        self.label("POSADA  /  SALON", 22, 18)
        self.label("E: hablar  |  norte: habitacion  |  sur: pueblo", 22, 43)

    def update_chapter_exits(self, player):
        from game.scenes.chapter_area_navigation import find_chapter_exit
        target = find_chapter_exit(self.scene_id, player["x"], player["y"], self.area_layout)
        if target:
            scene_id, spawn = target
            if self.app.scene_manager.change_scene(scene_id):
                self.app.state["player"].update({"x": spawn[0], "y": spawn[1]})
                self.app.dispatch_scene_entered_event()
                self.autosave()

    def draw_chapter_area(self, cx, cy):
        layout = self.area_layout
        screen = self.app.screen
        for x, y, w, h in layout.get("walkable", []):
            pygame.draw.rect(screen, PALE, (x - cx, y - cy, w, h))
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
        if "elder" in layout and self.scene_id == "brumazul_granja" and self.app.state["quests"]["un_techo_propio"] in ("find_elder", "repair_fence", "inspect_gate", "get_bolt"):
            self.actor("ANCIANO [E]", pygame.Vector2(layout["elder"]), cx, cy)
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
        self.label("E: hablar | Posada, taller, granja, puerto y playa", 22, 43)

    def actor(self, name, pos, cx, cy):
        x, y = int(pos.x - cx), int(pos.y - cy)
        pygame.draw.circle(self.app.screen, LINE, (x, y), 15, 1)
        self.label(name, x - 35, y - 33)

    def draw_minimal_hud(self):
        s = self.app.screen
        hp = self.app.state.get("health", {})
        maximum = max(1, hp.get("max", 10))
        current = max(0, hp.get("current", maximum))
        pygame.draw.rect(s, LIGHT, (24, 67, 152, 7), 1)
        pygame.draw.rect(s, PALE, (25, 68, int(150 * current / maximum), 5))
        slots = get_hotbar_slots(self.app.state)
        selected = get_active_hotbar_index(self.app.state)
        size, gap = 42, 7
        start = (WIDTH - len(slots) * (size + gap) + gap) // 2
        for i, item in enumerate(slots):
            x = start + i * (size + gap)
            pygame.draw.rect(s, LINE if i == selected else LIGHT, (x, HEIGHT - 54, size, size), 1)
            self.label(str(i + 1), x + 3, HEIGHT - 51)
            if item:
                item_id = item.get("item_id", "") if isinstance(item, dict) else str(item)
                data = get_item_data(item_id)
                self.label((data or {}).get("icon", item_id[:1]).upper(), x + 17, HEIGHT - 34)

    def draw_dialogue(self, speaker, message, choices=None, selected=0):
        draw_chapter_conversation(self, speaker, message, choices, selected)

    def label(self, value, x, y):
        self.app.screen.blit(self.app.small_font.render(str(value), True, INK), (int(x), int(y)))
