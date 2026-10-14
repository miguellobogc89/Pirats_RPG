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
from game.world.camera import get_camera_position
from game.data.item_database import get_item_data

WIDTH, HEIGHT = 960, 640
WHITE = (250, 250, 249)
PAPER = (245, 245, 244)
PALE = (231, 231, 230)
LIGHT = (208, 208, 207)
LINE = (166, 166, 166)
INK = (105, 105, 105)

# La conversacion tiene indicaciones de escena en vez de lineas pronunciadas.
SCRIPT = [
    ("POSADERA", "Vaya, has despertado. Pensabamos que no lo contarias."),
    ("POSADERA", "Un pescador te encontro al amanecer, tendido junto al camino."),
    ("POSADERA", "Llevabas arena en la ropa y no reaccionabas a nada."),
    ("TU", "Recuerdo la playa. Y algo enorme moviendose en la oscuridad."),
    ("POSADERA", "Aqui conocemos las tormentas y las alimañas. Pero aquello..."),
    ("POSADERA", "Hay alguien que lleva horas esperando a que despiertes."),
    ("@elder_enters", ""),
    ("ANCIANO", "Asi que eres el hijo de Almarin Velhart."),
    ("ANCIANO", "He visto muchos naufragos. Pocos llegan vivos desde esa playa."),
    ("ANCIANO", "Dime, ¿que recuerdas exactamente de la criatura?"),
    ("@choice", ""),
    ("ANCIANO", "Lo que describes confirma mis temores."),
    ("POSADERA", "¿Que ocurre? ¿Acaso sabeis que hay ahi fuera?"),
    ("ANCIANO", "Os agradezco que le hayais cuidado. ¿Nos dejaria a solas?"),
    ("POSADERA", "Por supuesto. Os traere algo de comer mas tarde."),
    ("@innkeeper_exits", ""),
    ("TU", "Ahora que estamos solos, ¿que sabes de esa criatura?"),
    ("ANCIANO", "Mas de lo que me gustaria. Y menos de lo necesario."),
    ("ANCIANO", "Hace años comenzaron a aparecer rastros en la costa."),
    ("ANCIANO", "Animales desaparecidos, marcas en la roca, noches sin aves."),
    ("ANCIANO", "Algunos lo atribuyeron a las mareas. Otros dejaron de salir."),
    ("TU", "¿La habias visto antes?"),
    ("ANCIANO", "No con mis propios ojos. Pero reconozco lo que has contado."),
    ("ANCIANO", "Y lo mas extraño de todo es que hayas sobrevivido."),
    ("ANCIANO", "Una criatura de ese tamaño no suele dejar escapar a su presa."),
    ("TU", "Entonces, ¿por que sigo aqui?"),
    ("ANCIANO", "Esa es precisamente la pregunta que no puedo responder."),
    ("ANCIANO", "Y no pienso inventar una respuesta para tranquilizarte."),
    ("TU", "Has dicho que conocias a mi padre."),
    ("ANCIANO", "Almarin Velhart no era un hombre que buscara reconocimiento."),
    ("ANCIANO", "Era paciente, reservado y mas obstinado que cualquier marinero."),
    ("ANCIANO", "Construyo una finca a las afueras. Trabajaba la tierra con sus manos."),
    ("ANCIANO", "Pero tambien tenia un taller. Alli guardaba sus herramientas y notas."),
    ("ANCIANO", "Nunca me explico del todo en que trabajaba durante las noches."),
    ("TU", "¿Que le ocurrio?"),
    ("ANCIANO", "Su historia no cabe en una conversacion junto a una cama."),
    ("ANCIANO", "Y hay cosas que prefiero comprobar antes de contartelas."),
    ("ANCIANO", "La finca sigue en pie, aunque nadie la cuida desde hace tiempo."),
    ("ANCIANO", "Te pertenece por derecho. Tengo documentos que debes ver."),
    ("ANCIANO", "Cuando hayas descansado, ven a la entrada de la finca."),
    ("TU", "¿Y la criatura?"),
    ("ANCIANO", "No vuelvas a la playa de noche. Ni siquiera por curiosidad."),
    ("ANCIANO", "No puedo protegerte de algo que aun no comprendo."),
    ("ANCIANO", "Por ahora descansa. Hablaremos cuando recuperes fuerzas."),
    ("@elder_exits", ""),
    ("@fade", ""),
]
CHOICES = [
    "Era enorme y avanzaba lentamente.",
    "Vi unos ojos brillando entre las sombras.",
    "Parecia conocer el camino al pueblo.",
]
RESPONSES = [
    "Entonces era tan grande como cuentan los viejos relatos...",
    "Esos ojos... esperaba no volver a oir hablar de ellos.",
    "Si buscaba el camino al pueblo, estamos ante algo peor.",
]
VILLAGE_LAYOUT = json.loads(
    (Path(__file__).resolve().parents[2] / "python_simulator" / "scenes" / "pueblo.json").read_text(encoding="utf-8")
)
VILLAGE_NPCS = [
    ("HERRERO", "human", (920, 485), ["Trabajo el hierro. Busca a Sylvarin si necesitas un cerrojo."]),
    ("BOTICA", "human", (1130, 475), ["La botica esta abierta."]),
    ("MERCADER", "human", (910, 300), ["Bienvenido a Brumazul."]),
    ("POSADERA", "human", (1080, 265), ["La posada esta al norte."]),
]

TAVERN_NPCS = [
    ("MARINERA", "human", (370, 450), [
        "La costa parecia tranquila ayer. Esta manana nadie quiere salir a faenar.",
        "No te acerques a la playa cuando caiga la noche.",
    ]),
    ("VIAJERO", "human", (555, 440), [
        "He recorrido tres islas y ninguna posada sirve un caldo como esta.",
        "Si buscas la finca Velhart, pregunta en el camino del pueblo.",
    ]),
]


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

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if self.phase == "fade" or self.phase in ("elder_enters", "keeper_exits", "elder_exits"):
            return True
        if self.phase == "dialogue":
            if event.type == pygame.KEYDOWN and self.index == 10:
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
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_ESCAPE):
                self.npc_dialogue = None
            return True
        if (self.tavern or self.village or self.chapter_area) and not self.app.menu_open and event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_RETURN):
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
                    self.npc_dialogue = ("ANCIANO", [
                        "Has llegado a la finca de Almarin. Ahora es tuya.",
                        "Antes de entrar debemos arreglar las tres vallas rotas.",
                        "Busca madera por la granja y repara los huecos.",
                    ])
                    dispatch_story_event(self.app, "npc_talked", {"npc_id": "anciano"})
                else:
                    self.npc_dialogue = ("ANCIANO", [
                        "Las vallas necesitan reparacion. Revisa los huecos de la finca."
                        if stage == "repair_fence" else "Tenemos que continuar con los trabajos de la finca."
                    ])
                return True
        if self.chapter_area:
            for node in self.area_layout.get("nodes", []):
                if math.dist((p["x"], p["y"]), node["position"]) < node.get("radius", 65):
                    self.npc_dialogue = (node.get("label", node["id"]), [
                        "Bienvenido. Hablemos de lo que ocurre en Brumazul."
                    ])
                    dispatch_story_event(self.app, "npc_talked", {"npc_id": node["id"]})
                    return True
            return False
        for name, race, pos, lines in (VILLAGE_NPCS if self.village else TAVERN_NPCS):
            if math.dist((p["x"], p["y"]), pos) < 65:
                self.npc_dialogue = (name, lines)
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
                self.draw_dialogue("TU", "¿Que fue lo que viste?", CHOICES, self.choice)
            else:
                self.draw_dialogue(who, self.response if self.index == 11 else line)
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
        pygame.draw.rect(self.app.screen, (129, 94, 54), rect)
        pygame.draw.rect(self.app.screen, (75, 57, 40), rect, 2)
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
        for node in layout.get("nodes", []):
            x, y = node["position"]
            self.actor(node.get("label", node["id"]), pygame.Vector2(x, y), cx, cy)
        if "elder" in layout and self.scene_id == "brumazul_granja" and self.app.state["quests"]["un_techo_propio"] in ("find_elder", "repair_fence", "inspect_gate", "get_bolt"):
            self.actor("ANCIANO [E]", pygame.Vector2(layout["elder"]), cx, cy)
        pygame.draw.rect(screen, LINE, (-cx, -cy, layout.get("width", 800), layout.get("height", 704)), 2)
        self.label(self.scene_id.replace("brumazul_", "").upper(), 22, 18)

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
        s = self.app.screen
        rect = pygame.Rect(35, HEIGHT - 190, WIDTH - 70, 140)
        pygame.draw.rect(s, WHITE, rect)
        pygame.draw.rect(s, LIGHT, rect, 1)
        self.label(speaker, 55, HEIGHT - 173)
        if choices:
            for i, choice in enumerate(choices):
                self.label(("> " if i == selected else "  ") + choice, 58, HEIGHT - 147 + i * 25)
        else:
            # Salto de linea por palabras para textos largos.
            words, line, y = message.split(), "", HEIGHT - 144
            for word in words:
                trial = (line + " " + word).strip()
                if self.app.small_font.size(trial)[0] > WIDTH - 125 and line:
                    self.label(line, 58, y)
                    y += 22
                    line = word
                else:
                    line = trial
            if line:
                self.label(line, 58, y)
        self.label("ENTER / ESPACIO", WIDTH - 175, HEIGHT - 73)

    def label(self, value, x, y):
        self.app.screen.blit(self.app.small_font.render(str(value), True, INK), (int(x), int(y)))
