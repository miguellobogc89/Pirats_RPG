"""Prototipo visual independiente: combate, cinematicas y transiciones."""
import json
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parent
SAVE = ROOT / "save.json"
SHARED_DATA = ROOT.parent / "game_data" / "chapter_01.json"
W, H = 960, 640
INK, LINE = (95,95,95), (170,170,170)

def read(name):
    return json.loads((ROOT / "scenes" / (name + ".json")).read_text(encoding="utf-8"))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W,H))
        pygame.display.set_caption("Pirates - Simulador")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 23)
        self.story = read("posada_guion")
        self.chapter = json.loads(SHARED_DATA.read_text(encoding="utf-8"))
        try:
            saved = json.loads(SAVE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            saved = {}
        self.mission = saved.get("mission", "las_tierras_de_almarin" if saved.get("intro_finished") else None)
        self.mission_stage = saved.get("mission_stage", "find_elder")
        self.wood = saved.get("wood", [])
        self.wood_count = saved.get("wood_count", 0)
        self.repaired_fences = saved.get("repaired_fences", [])
        self.elder_met = saved.get("elder_met", False)
        self.elder_after_fence = saved.get("elder_after_fence", False)
        self.gate_inspected = saved.get("gate_inspected", False)
        self.gate_repaired = saved.get("gate_repaired", saved.get("mission_stage") == "gate_repaired")
        self.journal_open = False
        self.menu_tab = "inventario"
        self.smith_quest = saved.get("smith_quest", "not_started")
        self.rat_quest = saved.get("rat_quest", "not_started")
        self.metal_bolt = saved.get("metal_bolt", 0)
        self.sylvarin_boots = saved.get("sylvarin_boots", False)
        self.rat_reward_claimed = saved.get("rat_reward_claimed", False)
        self.fathers_sword = saved.get("fathers_sword", False)
        self.elder_clue = saved.get("elder_clue", False)
        self.port_meeting = saved.get("port_meeting", False)
        self.farm_state = saved.get("farm_state", "ready")
        self.farm_kills = saved.get("farm_kills", [])
        self.farm_boss_hp = saved.get("farm_boss_hp", 160)
        self.house_key = saved.get("house_key", False)
        self.tools_collected = saved.get("tools_collected", False)
        self.prologue_finished = saved.get("prologue_finished", False)
        self.farm_fade = 0
        self.farm_elder_approach = False
        self.time_of_day = saved.get("time_of_day", "day" if saved.get("intro_finished",False) else "night")
        self.cinematic_kind = None
        self.current_node = None
        self.modal = None
        self.modal_actions = []
        self.modal_selection = 0
        self.cinematic_lines = []
        self.cinematic_index = 0
        self.elder_walk = False
        self.elder_visible = True
        self.notice = ""
        self.notice_timer = 0
        self.farm_dialogue = None
        start_scene = saved.get("scene", "playa")
        if self.house_key and not self.prologue_finished and start_scene == "pueblo":
            start_scene = "granja"
        self.enter(start_scene, saved.get("intro_finished", False), [440, 400] if start_scene == "granja" and saved.get("scene") == "pueblo" and self.house_key else None)

    def enter(self, name, finished=False, spawn=None):
        self.name, self.data = name, read(name)
        if name == "puerto" and self.gate_repaired and not self.port_meeting:
            self.mission_stage = "find_elder_port"
        self.player = pygame.Vector2(spawn if spawn is not None else self.data["spawn"])
        self.facing = pygame.Vector2(0,-1)
        self.hp, self.invulnerable, self.stun = 100, 0, 0
        self.attack_cooldown, self.attack_flash = 0, 0
        self.boss = pygame.Vector2(self.data["enemy"]["spawn"]) if "enemy" in self.data and not (name == "playa" and self.time_of_day == "day") else None
        self.rats = []
        self.rat_nest_hp = 0
        self.rat_hit_timer = 0
        self.farm_creatures = []
        self.farm_big = None
        self.farm_hit_timer = 0
        if name == "granja" and self.farm_state == "hunt":
            self.farm_creatures = [{"id":i,"pos":pygame.Vector2(p),"hp":40,"revealed":False} for i,p in enumerate(self.data["ambushes"]) if i not in self.farm_kills]
            if not self.farm_creatures:
                self.farm_state = "boss"
        if name == "granja" and self.farm_state == "boss":
            self.farm_big = pygame.Vector2(self.data["final_boss"])
        if name == "madriguera_artesana" and self.rat_quest != "completed":
            self.rats = [{"pos":pygame.Vector2(p),"hp":40,"cooldown":0} for p in self.data["rats"]]
            self.rat_nest_hp = 80
        self.boss_hp = self.data["enemy"]["hp"] if self.boss else 0
        self.boss_state, self.boss_timer = "idle", .8
        self.charge = pygame.Vector2()
        self.boss_stun = 0
        self.step, self.choice, self.cue_timer = 0, 0, 0
        self.keeper = pygame.Vector2(480,395)
        self.elder = pygame.Vector2(470,625)
        if name == "granja":
            self.elder = pygame.Vector2(self.data["elder"])
            self.elder_visible = not self.house_key and ((not self.elder_after_fence) or (self.port_meeting and self.farm_state in ("ready","approach")))
            if self.farm_state == "approach":
                self.elder.update(755,365)
                self.farm_elder_approach = True
            if not self.elder_met:
                self.elder.update(550,365)
                self.elder_walk = True
        self.show_keeper, self.show_elder = True, False
        self.phase = "free" if name == "playa" or finished else "dialogue"
        self.response = ""
        self.fade = 0

    def save(self, finished=False):
        SAVE.write_text(json.dumps({
            "scene": self.name, "intro_finished": finished,
            "mission": self.mission, "mission_stage": self.mission_stage,
            "wood": self.wood, "wood_count": self.wood_count,
            "smith_quest": self.smith_quest, "rat_quest": self.rat_quest,
            "metal_bolt": self.metal_bolt,
            "sylvarin_boots": self.sylvarin_boots, "rat_reward_claimed": self.rat_reward_claimed,
            "fathers_sword": self.fathers_sword, "elder_clue": self.elder_clue,
            "port_meeting": self.port_meeting, "time_of_day": self.time_of_day,
            "farm_state": self.farm_state, "farm_kills": self.farm_kills,
            "farm_boss_hp": self.farm_boss_hp, "house_key": self.house_key,
            "tools_collected": self.tools_collected, "prologue_finished": self.prologue_finished,
            "repaired_fences": self.repaired_fences, "elder_met": self.elder_met,
            "elder_after_fence": self.elder_after_fence, "gate_inspected": self.gate_inspected,
            "gate_repaired": self.gate_repaired
        }), encoding="utf-8")

    def advance(self):
        if self.phase != "dialogue":
            return
        if self.step == 10:
            self.response = self.story["responses"][self.choice]
        self.step += 1
        self.process_cue()

    def process_cue(self):
        if self.step >= len(self.story["script"]):
            self.finish()
            return
        cue = self.story["script"][self.step][0]
        phases = {"@elder_enters":"elder_enters","@innkeeper_exits":"keeper_exits","@elder_exits":"elder_exits","@fade":"fade"}
        self.phase = phases.get(cue,"dialogue")
        self.cue_timer = 0
        if cue == "@elder_enters":
            self.show_elder = True

    def finish(self):
        self.phase = "free"
        self.mission = "las_tierras_de_almarin"
        self.mission_stage = "find_elder"
        self.notice = "NUEVA MISION: LAS TIERRAS DE ALMARIN - Busca al anciano en la finca"
        self.notice_timer = 6
        self.player.update(400,440)
        self.show_keeper = False
        self.show_elder = False
        self.time_of_day = "day"
        self.save(True)

    def open_modal(self, lines, actions=None):
        self.modal = list(lines)
        self.modal_actions = actions or [("Continuar", "close")]
        self.modal_selection = 0

    def modal_action(self, action):
        if action.startswith("node:"):
            self.node_action(action)
            return
        if action == "close":
            if self.cinematic_lines and self.cinematic_index + 1 < len(self.cinematic_lines):
                self.cinematic_index += 1
                self.open_modal([self.cinematic_lines[self.cinematic_index]])
            else:
                if self.cinematic_lines:
                    self.cinematic_lines = []
                    self.cinematic_index = 0
                    if self.cinematic_kind == "farm_final":
                        self.house_key = True
                        self.farm_state = "complete"
                        self.mission_stage = "complete"
                        self.cinematic_kind = None
                        self.notice = "LLAVE DE ALMARIN - CASA Y TALLER ABIERTOS"
                        self.notice_timer = 7
                    elif self.cinematic_kind == "port_elder":
                        self.port_meeting = True
                        self.fathers_sword = True
                        self.mission = "la_ultima_madriguera"
                        self.mission_stage = "prepare"
                        self.notice = "M2 COMPLETADA - ESPADA DE ALMARIN RECIBIDA"
                        self.notice_timer = 6
                        self.cinematic_kind = None
                    elif not self.elder_met:
                        self.elder_met = True
                        self.mission = "un_techo_propio"
                        self.mission_stage = "repair_fence"
                        self.notice = "M1 COMPLETADA - M2: UN TECHO PROPIO"
                        self.notice_timer = 4
                    elif not self.elder_after_fence and self.name == "granja" and len(self.repaired_fences) == len(self.data["fence_gaps"]):
                        self.elder_after_fence = True
                        self.mission_stage = "inspect_gate"
                        self.elder_visible = False
                    self.save(True)
                self.modal = None
            return
        if action == "take_tools":
            self.tools_collected = True
            self.save(True)
            self.open_modal(["Has recogido hacha, azada, pico, guadana y regadera.",
                             "Las cinco herramientas son tuyas permanentemente."])
            return
        if action == "sleep":
            self.prologue_finished = True
            self.time_of_day = "day"
            self.mission_stage = "chapter_1"
            self.transition("casa_almarin", [400, 535])
            self.notice = "PROLOGO COMPLETADO - CAPITULO 1"
            self.notice_timer = 8
            self.open_modal(["Amanece sobre la granja de Almarin.",
                             "Comienza tu nueva vida en la granja."])
            return
        if action == "farm_yes":
            self.modal = None
            self.farm_state = "hunt"
            self.farm_kills = []
            self.farm_boss_hp = 160
            self.farm_creatures = [{"id":i,"pos":pygame.Vector2(p),"hp":40,"revealed":False} for i,p in enumerate(self.data["ambushes"])]
            self.time_of_day = "night"
            self.elder_visible = False
            self.mission_stage = "ambush"
            self.notice = "INVESTIGA LOS MOVIMIENTOS ENTRE LA MALEZA"
            self.notice_timer = 6
            self.save(True)
            return
        if action.startswith("fence:"):
            fence_id = action.split(":",1)[1]
            if fence_id not in self.repaired_fences and self.wood_count >= self.chapter["quests"]["un_techo_propio"]["requirements"]["fence_wood"]:
                self.wood_count -= self.chapter["quests"]["un_techo_propio"]["requirements"]["fence_wood"]
                self.repaired_fences.append(fence_id)
                self.mission_stage = "talk_elder" if len(self.repaired_fences) == len(self.data["fence_gaps"]) else "repair_fence"
                self.notice = "VALLA REPARADA (%d/%d)" % (len(self.repaired_fences),len(self.data["fence_gaps"]))
                self.notice_timer = 3
                self.save(True)
            self.modal = None
        elif action == "repair_gate":
            requirements = self.chapter["quests"]["un_techo_propio"]["requirements"]
            wood_cost = requirements["door_wood"]
            bolt_cost = requirements["door_metal_bolt"]
            if (self.elder_after_fence and len(self.repaired_fences) == len(self.data["fence_gaps"])
                    and not self.gate_repaired and self.wood_count >= wood_cost
                    and self.metal_bolt >= bolt_cost):
                self.wood_count -= wood_cost
                self.metal_bolt -= bolt_cost
                self.gate_repaired = True
                self.mission_stage = "gate_repaired"
                self.mission_stage = "find_elder_inn"
                self.notice = "NUEVO OBJETIVO: HABLA CON EL ANCIANO EN LA POSADA"
                self.notice_timer = 5
                self.save(True)
            self.modal = None
        elif action == "gate":
            self.gate_inspected = True
            self.mission_stage = "get_bolt"
            self.open_modal(["Para construir la puerta necesitas 15 de madera y un cerrojo de metal.",
                             "Nuevo objetivo: consigue 15 de madera y 1 cerrojo metalico."],
                            [("Cerrar","close")])
            self.save(True)

    def meet_elder_at_port(self):
        if self.port_meeting:
            return
        if not self.gate_repaired:
            self.open_modal(["ANCIANO: Aun queda trabajo por hacer en la finca. Nos veremos cuando hayas asegurado la entrada."])
            return
        self.cinematic_kind = "port_elder"
        self.cinematic_lines = self.chapter["dialogues"]["port_elder_intro"]
        self.cinematic_index = 0
        self.open_modal([self.cinematic_lines[0]])

    def interact_at(self, world):
        if self.name != "granja" or self.phase != "free" or self.modal:
            return
        if self.player.distance_to(world) > 95:
            return
        if self.port_meeting and self.farm_state == "ready" and world.distance_to(self.elder) < 70 and self.player.distance_to(self.elder) < 115:
            self.open_modal(["ANCIANO: Las criaturas salen de la maleza al caer la noche.",
                             "ANCIANO: Esta es tu oportunidad para acabar con ellas. Estas preparado?"],
                            [("Si, estoy listo","farm_yes"),("Todavia no","close")])
            return
        if self.port_meeting and self.farm_state == "approach" and not self.farm_elder_approach and world.distance_to(self.elder) < 70 and self.player.distance_to(self.elder) < 115:
            self.cinematic_kind = "farm_final"
            self.cinematic_lines = self.chapter["dialogues"]["farm_final"]
            self.cinematic_index = 0
            self.open_modal([self.cinematic_lines[0]])
            return
        if self.elder_visible and self.player.distance_to(self.elder) < 80 and world.distance_to(self.elder) < 50:
            if not self.elder_met:
                self.begin_elder_intro()
            elif self.mission_stage == "talk_elder":
                self.begin_elder_fence_end()
            return
        for building_key in ("house", "workshop"):
            building = self.data.get(building_key)
            if building and pygame.Vector2(building["door"]).distance_to(world) < 48:
                if self.house_key:
                    self.transition("casa_almarin" if building_key == "house" else "taller_almarin", [400, 535])
                else:
                    self.open_modal(["La puerta esta cerrada. El anciano conserva la llave."])
                return
        for i,position in enumerate(self.data["wood_piles"]):
            if i not in self.wood and world.distance_to(pygame.Vector2(position)) < 28:
                self.wood.append(i)
                self.wood_count += self.data.get("wood_per_pile",5)
                self.notice = "RAMAS RECOGIDAS: +5 MADERA (TOTAL %d)" % self.wood_count
                self.notice_timer = 3
                self.save(True)
                return
        if not self.elder_met:
            return
        for gap in self.data["fence_gaps"]:
            x,y,w,h = gap["rect"]
            if gap["id"] not in self.repaired_fences and x-15 <= world.x <= x+w+15 and y-15 <= world.y <= y+h+15:
                if self.wood_count >= gap["cost"]:
                    self.open_modal(["Reparar este tramo requiere 10 de madera. Tienes %d." % self.wood_count],
                                    [("Reparar","fence:"+gap["id"]),("Salir","close")])
                else:
                    self.open_modal(["Reparar este tramo requiere 10 de madera. Tienes %d." % self.wood_count],
                                    [("Salir","close")])
                return
        gate = pygame.Vector2(self.data["gate"]["position"])
        if self.elder_after_fence and world.distance_to(gate) < 55:
            if self.gate_repaired:
                self.open_modal(["La puerta ya esta reparada y asegurada."])
                return
            requirements = self.chapter["quests"]["un_techo_propio"]["requirements"]
            wood_cost = requirements["door_wood"]
            bolt_cost = requirements["door_metal_bolt"]
            if self.wood_count >= wood_cost and self.metal_bolt >= bolt_cost:
                self.open_modal(["Puerta: %d madera y %d cerrojo. Dispones de ambos materiales." % (wood_cost,bolt_cost)],
                                [("Reparar","repair_gate"),("Salir","close")])
            else:
                self.open_modal(["Puerta: necesitas %d madera y %d cerrojo." % (wood_cost,bolt_cost),
                                 "Tienes: %d madera y %d cerrojo." % (self.wood_count,self.metal_bolt)],
                                [("Nuevo objetivo","gate"),("Salir","close")])

    def click_world(self, world):
        if self.name in ("casa_almarin", "taller_almarin"):
            if self.player.distance_to(world) > 115:
                return
            if world.distance_to(pygame.Vector2(400, 125)) < 65:
                destination = "taller_almarin" if self.name == "casa_almarin" else "casa_almarin"
                self.transition(destination, [400, 175])
            elif world.distance_to(pygame.Vector2(self.data["exit"])) < 55:
                self.transition("granja", [260, 310] if self.name == "casa_almarin" else [465, 310])
            elif self.name == "casa_almarin" and world.distance_to(pygame.Vector2(self.data["bed"])) < 65:
                if self.prologue_finished:
                    self.open_modal(["Ya ha amanecido. Puedes descansar aqui."])
                else:
                    self.open_modal(["Quieres dormir hasta manana?"], [("Dormir", "sleep"), ("Todavia no", "close")])
            elif self.name == "taller_almarin":
                if world.distance_to(pygame.Vector2(self.data["chest"])) < 65:
                    if self.tools_collected:
                        self.open_modal(["El baul esta vacio. Ya tienes las herramientas."])
                    else:
                        self.open_modal(["Baul: hacha, azada, pico, guadana y regadera."], [("Recoger todo", "take_tools"), ("Cerrar", "close")])
                elif world.distance_to(pygame.Vector2(self.data["map_table"])) < 65:
                    self.open_modal(["Mapas antiguos cubren la mesa.",
                                     "Las runas estan escritas en una lengua que aun no comprendes."])
            return
        if self.name == "granja":
            self.interact_at(world)
            return
        if self.name not in ("pueblo", "taller_sylvarin", "puerto", "salon_posada"):
            return
        if self.name == "puerto" and not self.port_meeting:
            elder = pygame.Vector2(self.data["elder"])
            if elder.distance_to(world) < 60 and elder.distance_to(self.player) < 115:
                self.meet_elder_at_port()
                return
        if self.name == "salon_posada" and self.gate_repaired and not self.elder_clue:
            if pygame.Vector2(480,395).distance_to(world) < 95 and self.player.distance_to(pygame.Vector2(480,395)) < 135:
                self.elder_clue = True
                self.mission_stage = "find_elder_port"
                self.save(True)
                self.open_modal(self.chapter["dialogues"]["inn_elder_clue"])
                return
        for node in self.data.get("nodes", []):
            pos = pygame.Vector2(node["position"])
            if pos.distance_to(world) < node.get("radius", 45) and pos.distance_to(self.player) < 110:
                self.current_node = node["id"]
                self.open_node_menu()
                return
        if self.name == "taller_sylvarin":
            door = pygame.Vector2(675,260)
            if world.distance_to(door) < 65 and self.player.distance_to(door) < 120:
                self.transition("madriguera_artesana",[125,330])

    def open_node_menu(self):
        npc = self.chapter["npcs"][self.current_node]
        self.open_modal([npc["label"]+": Que necesitas?"],
                        [(name,"node:"+name.lower()) for name in npc["options"]])

    def node_action(self, action):
        choice = action.split(":",1)[1]
        if choice == "salir":
            self.modal = None
        elif choice == "hablar":
            if self.current_node == "herrero":
                if self.smith_quest == "artisan_explained":
                    self.smith_quest = "completed"
                    self.metal_bolt += 1
                    self.save(True)
                    self.open_modal(["HERRERO: Ahora comprendo. Eran campanas contra las ratas.",
                                     "HERRERO: Toma el cerrojo que necesitabas."])
                    return
                if self.gate_inspected and self.smith_quest == "not_started":
                    self.smith_quest = "investigate"
                    self.save(True)
            if self.current_node == "sylvarin":
                if self.rat_quest == "cleared" and not self.rat_reward_claimed:
                    self.rat_quest = "completed"
                    self.rat_reward_claimed = True
                    self.sylvarin_boots = True
                    self.save(True)
                    self.open_modal(["SYLVARIN: Ya no se oyen las criaturas. Has recuperado mi taller.",
                                     "SYLVARIN: Toma estas botas de cuero, las hice yo misma. +2 defensa.",
                                     "SYLVARIN: A partir de ahora tambien comerciare contigo materiales organicos."])
                    return
                if self.smith_quest == "investigate":
                    self.smith_quest = "artisan_explained"
                if self.rat_quest == "not_started":
                    self.rat_quest = "offered"
                self.save(True)
            npc = self.chapter["npcs"][self.current_node]
            self.open_modal(npc["dialogues"]["intro"])
        elif choice == "entrar":
            self.modal = None
            self.transition("salon_posada",[485,710])
        elif choice == "comerciar":
            self.open_modal(["Comercio pendiente de implementar."])

    def begin_elder_intro(self):
        self.elder_walk = False
        self.cinematic_lines = self.chapter["dialogues"]["farm_intro"]
        self.cinematic_index = 0
        self.open_modal([self.cinematic_lines[0]])

    def begin_elder_fence_end(self):
        self.cinematic_lines = self.chapter["dialogues"]["farm_fence_end"]
        self.cinematic_index = 0
        self.open_modal([self.cinematic_lines[0]])

    def attack(self):
        if self.attack_cooldown > 0:
            return
        if self.name == "granja" and self.farm_state in ("hunt","boss"):
            self.attack_cooldown, self.attack_flash = .38, .14
            if self.farm_state == "hunt":
                for creature in self.farm_creatures:
                    delta = creature["pos"]-self.player
                    if creature["revealed"] and creature["hp"] > 0 and 0 < delta.length() < 92 and self.facing.dot(delta.normalize()) > .1:
                        creature["hp"] = max(0,creature["hp"]-20)
                        if creature["hp"] == 0 and creature["id"] not in self.farm_kills:
                            self.farm_kills.append(creature["id"])
                            self.save(True)
                if len(self.farm_kills) == len(self.data["ambushes"]):
                    self.farm_state = "boss"
                    self.farm_big = pygame.Vector2(self.data["final_boss"])
                    self.mission_stage = "boss"
                    self.notice = "ALGO MUCHO MAS GRANDE SE MUEVE EN LA OSCURIDAD"
                    self.notice_timer = 6
                    self.save(True)
            elif self.farm_big is not None:
                delta = self.farm_big-self.player
                if 0 < delta.length() < 100 and self.facing.dot(delta.normalize()) > .1:
                    self.farm_boss_hp = max(0,self.farm_boss_hp-20)
                    if self.farm_boss_hp == 0:
                        self.farm_state = "fade"
                        self.farm_fade = 0
                        self.mission_stage = "complete"
                        self.save(True)
                    else:
                        self.save(True)
            return
        if self.name == "madriguera_artesana":
            if not self.fathers_sword:
                self.notice = "NECESITAS UN ARMA PARA LUCHAR"
                self.notice_timer = 2
                return
            self.attack_cooldown, self.attack_flash = .38, .14
            for rat in self.rats:
                delta = rat["pos"]-self.player
                if rat["hp"] > 0 and 0 < delta.length() < 92 and self.facing.dot(delta.normalize()) > .1:
                    rat["hp"] = max(0,rat["hp"]-20)
            nest = pygame.Vector2(self.data["nest"])-self.player
            if self.rat_nest_hp > 0 and 0 < nest.length() < 100 and self.facing.dot(nest.normalize()) > .1:
                self.rat_nest_hp = max(0,self.rat_nest_hp-20)
            if self.rat_nest_hp == 0 and all(r["hp"] == 0 for r in self.rats):
                self.rat_quest = "cleared"
                self.notice = "ALMACEN DESPEJADO - VUELVE CON SYLVARIN"
                self.notice_timer = 6
                self.save(True)
            return
        if self.boss is None or self.boss_hp <= 0:
            return
        self.attack_cooldown, self.attack_flash = .38, .14
        delta = self.boss-self.player
        if 0 < delta.length() < 92 and self.facing.dot(delta.normalize()) > .25:
            self.boss_hp = max(0,self.boss_hp-20)
            self.boss_stun = .55
            self.boss_state = "stunned"
            self.boss += delta.normalize()*25

    def walkable(self, point):
        """Test a circle-sized player against configured walkable regions."""
        radius = 12
        regions = self.data.get("walkable", [])
        if regions:
            # Centre must lie in a corridor; four cardinal samples prevent wall clipping.
            samples = ((0,0),(-radius,0),(radius,0),(0,-radius),(0,radius))
            for dx,dy in samples:
                if not any(x <= point.x+dx <= x+w and y <= point.y+dy <= y+h
                           for x,y,w,h in regions):
                    return False
            if self.name == "granja":
                for gap in self.data["fence_gaps"]:
                    if gap["id"] not in self.repaired_fences:
                        continue
                    # A repaired fence closes the opening; the perimeter is already bounded.
                x,y,w,h = self.data["gate"]["barrier"]
                if x-radius < point.x < x+w+radius and y-radius < point.y < y+h+radius:
                    return False
            if self.name == "granja":
                for key in ("house","workshop"):
                    building = self.data.get(key)
                    if building:
                        x,y,w,h = building["rect"]
                        if x-radius < point.x < x+w+radius and y-radius < point.y < y+h+radius:
                            return False
            if self.name == "pueblo":
                for building in self.data.get("buildings", []):
                    x,y,w,h = building["rect"]
                    if x-radius < point.x < x+w+radius and y-radius < point.y < y+h+radius:
                        return False
            return True
        if self.name in ("casa_almarin", "taller_almarin"):
            return 117 <= point.x <= 683 and 117 <= point.y <= 558
        if self.name == "habitacion_posada":
            return 216 <= point.x <= 584 and 216 <= point.y <= 584
        return 16 <= point.x <= 688 and 16 <= point.y <= 688

    def transition(self, name, spawn):
        self.enter(name, True, spawn)
        self.save(True)

    def update(self, dt):
        dt = min(dt,.05)
        self.attack_cooldown = max(0,self.attack_cooldown-dt)
        self.attack_flash = max(0,self.attack_flash-dt)
        self.invulnerable = max(0,self.invulnerable-dt)
        self.stun = max(0,self.stun-dt)
        self.boss_stun = max(0,self.boss_stun-dt)
        self.boss_timer -= dt
        if self.name == "granja" and self.elder_walk and self.modal is None:
            direction = self.player - self.elder
            if direction.length() > 65:
                self.elder += direction.normalize()*100*dt
            else:
                self.begin_elder_intro()
        if self.name == "granja" and self.farm_state == "fade":
            self.farm_fade = min(1,self.farm_fade+dt*1.4)
            if self.farm_fade >= 1:
                self.farm_state = "approach"
                self.time_of_day = "day"
                self.player.update(445,410)
                self.elder.update(755,365)
                self.elder_visible = True
                self.farm_elder_approach = True
                self.save(True)
        if self.name == "granja" and self.farm_state == "approach" and self.farm_elder_approach and not self.modal:
            direction = self.player-self.elder
            if direction.length() > 65:
                self.elder += direction.normalize()*110*dt
            else:
                self.farm_elder_approach = False
                self.cinematic_kind = "farm_final"
                self.cinematic_lines = self.chapter["dialogues"]["farm_final"]
                self.cinematic_index = 0
                self.open_modal([self.cinematic_lines[0]])
        if self.name == "granja" and self.farm_state in ("hunt","boss") and not self.modal and not self.journal_open:
            self.farm_hit_timer = max(0,self.farm_hit_timer-dt)
            if self.farm_state == "hunt":
                for creature in self.farm_creatures:
                    if creature["hp"] <= 0:
                        continue
                    delta = self.player-creature["pos"]
                    distance = delta.length()
                    if distance < 100:
                        creature["revealed"] = True
                    if creature["revealed"] and 26 < distance < 220:
                        creature["pos"] += delta.normalize()*85*dt
                    elif creature["revealed"] and distance <= 26 and self.farm_hit_timer <= 0 and self.invulnerable <= 0:
                        self.hp -= 8 if self.sylvarin_boots else 11
                        self.invulnerable = .7
                        self.farm_hit_timer = .85
            elif self.farm_big is not None:
                delta = self.player-self.farm_big
                distance = delta.length()
                if 44 < distance < 420:
                    self.farm_big += delta.normalize()*72*dt
                elif distance <= 44 and self.farm_hit_timer <= 0 and self.invulnerable <= 0:
                    self.hp -= 14 if self.sylvarin_boots else 18
                    self.invulnerable = .9
                    self.farm_hit_timer = 1.1
            if self.hp <= 0:
                self.farm_state = "ready"
                self.farm_kills = []
                self.farm_boss_hp = 160
                self.time_of_day = "day"
                self.transition("habitacion_posada",[320,256])
                return
        self.notice_timer = max(0, self.notice_timer-dt)
        if self.phase in ("elder_enters","keeper_exits","elder_exits"):
            who = self.elder if self.phase != "keeper_exits" else self.keeper
            speed = -100 if self.phase == "elder_enters" else 110
            who.y += speed*dt
            target = 465 if self.phase == "elder_enters" else 620 if self.phase == "keeper_exits" else 625
            if (speed < 0 and who.y <= target) or (speed > 0 and who.y >= target):
                who.y = target
                if self.phase == "keeper_exits": self.show_keeper = False
                if self.phase == "elder_exits": self.show_elder = False
                self.step += 1
                self.process_cue()
        elif self.phase == "fade":
            self.fade = min(1,self.fade+dt*.85)
            if self.fade >= 1: self.finish()
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(int(keys[pygame.K_d] or keys[pygame.K_RIGHT])-int(keys[pygame.K_a] or keys[pygame.K_LEFT]),int(keys[pygame.K_s] or keys[pygame.K_DOWN])-int(keys[pygame.K_w] or keys[pygame.K_UP]))
        if self.phase == "free" and self.modal is None and not self.journal_open and not self.elder_walk and self.stun <= 0 and move.length_squared():
            self.facing = move.normalize()
            delta = self.facing * 185 * dt
            # Resolve separately on each axis to allow sliding along walls.
            for axis in ("x", "y"):
                trial = self.player.copy()
                setattr(trial, axis, getattr(trial, axis)+getattr(delta, axis))
                if self.walkable(trial):
                    self.player = trial
        if self.phase == "free" and self.modal is None and not self.journal_open:
            if self.name == "playa" and self.time_of_day == "day":
                if self.player.y <= 30 and 350 < self.player.x < 450 and move.y < 0:
                    self.transition("pueblo",[495,930])
                    return
                if self.player.x >= 675 and 390 < self.player.y < 490 and move.x > 0:
                    self.transition("puerto",[75,440])
                    return
            if self.name in ("casa_almarin", "taller_almarin") and self.player.y >= 545 and 345 < self.player.x < 455 and move.y > 0:
                self.transition("granja", [260, 310] if self.name == "casa_almarin" else [465, 310])
                return
            if self.name == "habitacion_posada" and self.player.y >= 575 and 430 < self.player.x < 540 and move.y > 0:
                self.transition("salon_posada", [480,180])
                return
            if self.name == "salon_posada":
                if self.player.y <= 119 and 430 < self.player.x < 540 and move.y < 0:
                    self.transition("habitacion_posada", [485,560])
                    return
                if self.player.y >= 730 and 430 < self.player.x < 540 and move.y > 0:
                    self.transition("pueblo", [1060,410])
                    return
            if self.name == "taller_sylvarin":
                if self.player.y >= 560 and 345 < self.player.x < 455 and move.y > 0:
                    self.transition("pueblo",[1255,455])
                    return
                if self.player.x >= 635 and 200 < self.player.y < 330 and move.x > 0:
                    self.transition("madriguera_artesana",[125,330])
                    return
                    return
            if self.name == "madriguera_artesana":
                if self.player.x <= 105 and 275 < self.player.y < 385 and move.x < 0:
                    self.transition("taller_sylvarin",[605,260])
                    return
            if self.name == "puerto":
                if self.player.y <= 32 and 350 < self.player.x < 450 and move.y < 0:
                    self.transition("pueblo",[650,925])
                    return
                if self.player.x <= 32 and 390 < self.player.y < 490 and move.x < 0:
                    if self.time_of_day == "day":
                        self.transition("playa",[650,440])
                    else:
                        self.open_modal(["El paso a la playa permanece cerrado durante la noche."])
                    return
            if self.name == "pueblo":
                if 1225 < self.player.x < 1290 and 425 <= self.player.y <= 465 and move.y < 0:
                    self.transition("taller_sylvarin",[400,555])
                    return
                if 1040 < self.player.x < 1110 and self.player.y <= 265 and move.y < 0:
                    self.transition("salon_posada", [485,710])
                    return
                if 580 < self.player.x < 720 and self.player.y >= 990 and move.y > 0:
                    self.transition("puerto", [400,145])
                    return
                if 450 < self.player.x < 540 and self.player.y >= 990 and move.y > 0:
                    if self.time_of_day == "day":
                        self.transition("playa",[400,55])
                    else:
                        self.open_modal(["El acceso a la playa esta cerrado de noche."])
                    return
                if self.player.x <= 125 and 410 < self.player.y < 500 and move.x < 0:
                    self.transition("granja", [680,320])
                    return
            if self.name == "granja" and self.farm_state not in ("hunt","boss","fade") and self.player.x >= 740 and 270 < self.player.y < 370 and move.x > 0:
                self.transition("pueblo", [140,455])
                return
        if self.name == "madriguera_artesana" and self.rat_quest != "completed":
            self.rat_hit_timer = max(0,self.rat_hit_timer-dt)
            if self.fathers_sword and self.rat_quest != "cleared" and self.modal is None and not self.journal_open:
                for rat in self.rats:
                    if rat["hp"] <= 0:
                        continue
                    delta = self.player-rat["pos"]
                    if delta.length() > 27 and delta.length() < 260:
                        rat["pos"] += delta.normalize()*65*dt
                    elif delta.length() <= 27 and self.rat_hit_timer <= 0 and self.invulnerable <= 0:
                        self.hp -= 6 if self.sylvarin_boots else 8
                        self.invulnerable = .65
                        self.rat_hit_timer = .75
                if self.hp <= 0:
                    self.transition("habitacion_posada",[320,256])
                    return
        if self.boss is None or self.boss_hp <= 0: return
        delta = self.player-self.boss
        distance = delta.length()
        if self.boss_stun > 0: self.boss_state = "stunned"
        elif self.boss_state == "stunned":
            self.boss_state,self.boss_timer = "idle",.5
        elif self.boss_state == "idle":
            if 80 < distance < 360: self.boss += delta.normalize()*45*dt
            if self.boss_timer <= 0 and 0 < distance < 340:
                self.boss_state,self.boss_timer,self.charge = "windup",.85,delta.normalize()
        elif self.boss_state == "windup" and self.boss_timer <= 0:
            self.boss_state,self.boss_timer = "charge",.38
        elif self.boss_state == "charge":
            self.boss += self.charge*440*dt
            if self.boss_timer <= 0: self.boss_state,self.boss_timer = "recovery",1
        elif self.boss_state == "recovery" and self.boss_timer <= 0:
            self.boss_state,self.boss_timer = "idle",.45
        self.boss.x = max(26,min(678,self.boss.x))
        self.boss.y = max(26,min(678,self.boss.y))
        if self.boss_state == "charge" and self.boss.distance_to(self.player) < 36 and self.invulnerable <= 0:
            self.hp -= 30
            self.invulnerable,self.stun = 1,.45
        if self.hp <= 0:
            self.enter("habitacion_posada")
            self.save(False)

    def label(self,text,x,y):
        self.screen.blit(self.font.render(text,True,INK),(int(x),int(y)))

    def draw(self):
        s = self.screen
        s.fill((255,255,255))
        cx = max(0,min(self.data["width"]-W,self.player.x-W/2)) if self.data["width"]>W else (self.data["width"]-W)/2
        cy = max(0,min(self.data["height"]-H,self.player.y-H/2)) if self.data["height"]>H else (self.data["height"]-H)/2
        if self.name == "playa":
            pygame.draw.rect(s,(240,240,240),(-cx,-cy,704,704))
            pygame.draw.rect(s,LINE,(-cx,-cy,704,704),1)
            pygame.draw.rect(s,(231,231,231),(-cx,-cy,704,165))
            for x in (350,450): pygame.draw.line(s,LINE,(x-cx,-cy),(x-cx,360-cy),1)
            self.label("PLAYA DE BRUMAZUL / "+self.time_of_day.upper(),22,18)
        elif self.name in ("casa_almarin", "taller_almarin"):
            pygame.draw.rect(s,LINE,(105-cx,105-cy,590,465),1)
            pygame.draw.line(s,(255,255,255),(355-cx,105-cy),(445-cx,105-cy),3)
            self.label("IR AL " + ("TALLER" if self.name == "casa_almarin" else "CASA") + " [CLIC]",325-cx,125-cy)
            pygame.draw.line(s,(255,255,255),(345-cx,570-cy),(455-cx,570-cy),3)
            self.label("SALIDA A LA GRANJA",345-cx,520-cy)
            if self.name == "casa_almarin":
                pygame.draw.rect(s,LINE,(180-cx,180-cy,130,105),1)
                self.label("CAMA [CLIC]",193-cx,150-cy)
                self.label("CASA DE ALMARIN",22,18)
            else:
                pygame.draw.rect(s,LINE,(205-cx,220-cy,120,75),1)
                self.label("BAUL [CLIC]",210-cx,185-cy)
                pygame.draw.rect(s,LINE,(475-cx,215-cy,135,85),1)
                self.label("MAPAS [CLIC]",478-cx,180-cy)
                self.label("TALLER DE ALMARIN",22,18)
        elif self.name == "habitacion_posada":
            pygame.draw.rect(s,(245,245,244),(200-cx,200-cy,400,400))
            pygame.draw.rect(s,LINE,(200-cx,200-cy,400,400),1)
            pygame.draw.rect(s,LINE,(280-cx,400-cy,80,120),1)
            pygame.draw.rect(s,LINE,(480-cx,280-cy,80,80),1)
            pygame.draw.line(s,(255,255,255),(430-cx,600-cy),(540-cx,600-cy),5)
            if self.show_keeper: self.actor("POSADERA",self.keeper,cx,cy)
            if self.show_elder: self.actor("ANCIANO",self.elder,cx,cy)
            self.label("POSADA / HABITACION",22,18)
        elif self.name == "salon_posada":
            pygame.draw.rect(s,(245,245,244),(100-cx,100-cy,600,650))
            pygame.draw.rect(s,LINE,(100-cx,100-cy,600,650),2)
            pygame.draw.line(s,(255,255,255),(430-cx,100-cy),(540-cx,100-cy),6)
            pygame.draw.line(s,(255,255,255),(430-cx,750-cy),(540-cx,750-cy),6)
            self.label("HABITACION",435-cx,125-cy)
            self.label("SALIDA AL PUEBLO",430-cx,720-cy)
            if self.gate_repaired and not self.elder_clue:
                self.actor("POSADERA [CLIC]",pygame.Vector2(480,395),cx,cy)
            self.label("POSADA / SALON",22,18)
        elif self.name == "puerto":
            for x,y,w,h in self.data["walkable"]:
                pygame.draw.rect(s,(245,245,244),(x-cx,y-cy,w,h))
                pygame.draw.rect(s,LINE,(x-cx,y-cy,w,h),2)
            pygame.draw.rect(s,(228,228,228),(210-cx,270-cy,440,100))
            self.label("PUERTO DE BRUMAZUL / "+self.time_of_day.upper(),22,18)
            self.label("MAR",260-cx,305-cy)
            self.label("PUEBLO",360-cx,80-cy)
            self.label("PLAYA / SOLO DE DIA",35-cx,360-cy)
            if not self.port_meeting:
                self.actor("ANCIANO [CLIC]",pygame.Vector2(self.data["elder"]),cx,cy)
            for node in self.data.get("nodes",[]):
                px,py = node["position"]
                self.actor(node["label"],pygame.Vector2(px,py),cx,cy)
        elif self.name == "pueblo":
            for x,y,w,h in self.data["walkable"]:
                pygame.draw.rect(s,(245,245,244),(x-cx,y-cy,w,h))
                pygame.draw.rect(s,LINE,(x-cx,y-cy,w,h),2)
            for building in self.data["buildings"]:
                x,y,w,h = building["rect"]
                pygame.draw.rect(s,(231,231,231),(x-cx,y-cy,w,h))
                pygame.draw.rect(s,INK,(x-cx,y-cy,w,h),2)
                dx,dy,dw,dh = building["door"]
                pygame.draw.line(s,(255,255,255),(dx-cx,dy-cy),(dx+dw-cx,dy-cy),7)
                self.label(building["label"],x-cx+45,y-cy+60)
            for door in self.data["doors"]:
                x,y,w,h = door["rect"]
                self.label(door["label"],x-cx,y-cy-24)
            for node in self.data.get("nodes", []):
                px,py = node["position"]
                pygame.draw.circle(s,INK,(int(px-cx),int(py-cy)),5,1)
                self.label(node["label"]+" [CLIC]",px-cx-35,py-cy-28)
            self.label("BRUMAZUL / PUEBLO",22,18)
        elif self.name == "madriguera_artesana":
            pygame.draw.rect(s,(245,245,244),(75-cx,75-cy,650,510))
            pygame.draw.rect(s,LINE,(75-cx,75-cy,650,510),2)
            self.label("ALMACEN DE SYLVARIN",22,18)
            if self.rat_quest != "completed":
                for rat in self.rats:
                    if rat["hp"] > 0:
                        pygame.draw.circle(s,INK,(int(rat["pos"].x-cx),int(rat["pos"].y-cy)),12,2)
                        self.label(str(rat["hp"])+" PV",rat["pos"].x-cx-20,rat["pos"].y-cy-35)
                if self.rat_nest_hp > 0:
                    nx,ny = self.data["nest"]
                    pygame.draw.circle(s,INK,(int(nx-cx),int(ny-cy)),35,2)
                    self.label("GUARIDA: %d PV" % self.rat_nest_hp,nx-cx-55,ny-cy-48)
            else:
                self.label("ALMACEN DESPEJADO",260-cx,310-cy)
            self.label("VOLVER AL TALLER",95-cx,245-cy)
        elif self.name == "taller_sylvarin":
            pygame.draw.rect(s,(245,245,244),(75-cx,75-cy,650,510))
            pygame.draw.rect(s,LINE,(75-cx,75-cy,650,510),2)
            self.label("TALLER DE SYLVARIN",22,18)
            self.actor("SYLVARIN",pygame.Vector2(390,255),cx,cy)
            pygame.draw.rect(s,INK,(650-cx,215-cy,50,90),2)
            self.label("ALMACEN DE RATAS",560-cx,180-cy)
            self.label("SALIDA AL PUEBLO",345-cx,540-cy)
        elif self.name == "granja":
            pygame.draw.rect(s,(245,245,244),(40-cx,40-cy,720,560))
            pygame.draw.rect(s,LINE,(40-cx,40-cy,720,560),2)
            self.label("GRANJA",22,18)
            self.label("SALIDA AL PUEBLO",600-cx,260-cy)
            self.label("MADERA: %d" % self.wood_count,22,44)
            gx,gy,gw,gh = self.data["gate"]["barrier"]
            pygame.draw.rect(s,LINE,(gx-cx,gy-cy,gw,gh),2)
            if not self.gate_repaired:
                self.label("PUERTA ROTA [CLIC]",gx-cx-25,gy-cy-27)
            else:
                self.label("PUERTA REPARADA",gx-cx-25,gy-cy-27)
            for gap in self.data["fence_gaps"]:
                x,y,w,h = gap["rect"]
                if gap["id"] not in self.repaired_fences:
                    pygame.draw.rect(s,(255,255,255),(x-cx,y-cy,w,h))
                    pygame.draw.rect(s,INK,(x-cx,y-cy,w,h),1)
                    self.label("VALLA ROTA",x-cx,y-cy-23)
                else:
                    pygame.draw.rect(s,INK,(x-cx,y-cy,w,h),2)
            for building_key in ("house", "workshop"):
                building = self.data.get(building_key)
                if not building:
                    continue
                bx,by,bw,bh = building["rect"]
                # Marcadores esquematicos: solo contorno, sin volumen ni tejado.
                pygame.draw.rect(s,INK,(bx-cx,by-cy,bw,bh),1)
                dx,dy = building["door"]
                pygame.draw.line(s,INK,(dx-cx-17,dy-cy),(dx-cx+17,dy-cy),1)
                self.label(building["label"],bx-cx+12,by-cy+18)
                self.label("CERRADO [CLIC]" if not self.house_key else "ENTRAR [CLIC]",dx-cx-67,dy-cy+9)
            if self.farm_state in ("hunt","boss","fade"):
                for i,(wx,wy) in enumerate(self.data["ambushes"]):
                    for j in range(9):
                        ox = ((i*37+j*19)%85)-42
                        oy = ((i*29+j*23)%70)-35
                        pygame.draw.line(s,(92,117,83),(wx+ox-cx,wy+oy-cy),(wx+ox+5-cx,wy+oy-13-cy),3)
                shadow = pygame.Surface((W,H),pygame.SRCALPHA)
                shadow.fill((14,23,29,210))
                torch = pygame.Vector2(self.player.x-cx,self.player.y-cy)
                pygame.draw.circle(shadow,(0,0,0,0),(int(torch.x),int(torch.y)),115)
                pygame.draw.circle(shadow,(14,23,29,75),(int(torch.x),int(torch.y)),170,55)
                s.blit(shadow,(0,0))
                pygame.draw.circle(s,(245,178,75),(int(torch.x+14),int(torch.y-12)),7)
                for creature in self.farm_creatures:
                    if creature["hp"] <= 0:
                        continue
                    ex,ey = creature["pos"].x-cx,creature["pos"].y-cy
                    if creature["revealed"]:
                        pygame.draw.circle(s,(140,88,68),(int(ex),int(ey)),13)
                        pygame.draw.circle(s,(242,213,120),(int(ex-4),int(ey-3)),2)
                        pygame.draw.circle(s,(242,213,120),(int(ex+4),int(ey-3)),2)
                        pygame.draw.rect(s,(205,90,75),(ex-15,ey-24,30*creature["hp"]/40,4))
                    elif self.player.distance_to(creature["pos"]) < 180:
                        pygame.draw.circle(s,(242,213,120),(int(ex-4),int(ey)),2)
                        pygame.draw.circle(s,(242,213,120),(int(ex+4),int(ey)),2)
                if self.farm_big is not None and self.farm_state == "boss":
                    ex,ey = self.farm_big.x-cx,self.farm_big.y-cy
                    pygame.draw.circle(s,(95,66,80),(int(ex),int(ey)),34)
                    pygame.draw.circle(s,(235,177,93),(int(ex-12),int(ey-6)),5)
                    pygame.draw.circle(s,(235,177,93),(int(ex+12),int(ey-6)),5)
                    pygame.draw.rect(s,(190,70,65),(ex-35,ey-51,70*self.farm_boss_hp/160,6))
                self.label("NOCHE / ANTORCHA - CRIATURAS: %d/%d" % (len(self.farm_kills),len(self.data["ambushes"])),22,94)
            if self.elder_visible: self.actor("ANCIANO",self.elder,cx,cy)
            for i,position in enumerate(self.data["wood_piles"]):
                if i not in self.wood:
                    px,py = position
                    pygame.draw.rect(s,INK,(px-cx-10,py-cy-7,20,14),1)
                    self.label("RAMAS [CLIC]",px-cx-34,py-cy-30)
        if self.boss is not None and self.boss_hp > 0:
            bx,by = int(self.boss.x-cx),int(self.boss.y-cy)
            pygame.draw.circle(s,INK,(bx,by),24,1)
            if self.boss_state == "windup":
                end = self.boss+self.charge*170
                pygame.draw.line(s,LINE,(bx,by),(int(end.x-cx),int(end.y-cy)),1)
            pygame.draw.rect(s,LINE,(bx-26,by-40,52,4),1)
            pygame.draw.rect(s,INK,(bx-25,by-39,int(50*self.boss_hp/self.data["enemy"]["hp"]),2))
        center = self.player-pygame.Vector2(cx,cy)
        side = pygame.Vector2(-self.facing.y,self.facing.x)
        points = [center+self.facing*16,center-self.facing*12+side*10,center-self.facing*12-side*10]
        pygame.draw.polygon(s,INK,points,1)
        pygame.draw.rect(s,LINE,(24,67,152,7),1)
        pygame.draw.rect(s,INK,(25,68,int(150*self.hp/100),5))
        if self.journal_open:
            pygame.draw.rect(s,(250,250,250),(120,65,720,510))
            pygame.draw.rect(s,INK,(120,65,720,510),2)
            self.label("PERSONAJE  /  TAB PARA CERRAR",145,88)
            for name,x in (("inventario",150),("misiones",330)):
                active = self.menu_tab == name
                pygame.draw.rect(s,(225,225,225) if active else (245,245,245),(x,110,170,42))
                pygame.draw.rect(s,INK,(x,110,170,42),2 if active else 1)
                self.label(name.upper(),x+23,122)
            pygame.draw.line(s,LINE,(145,165),(815,165),1)
            if self.menu_tab == "inventario":
                self.label("INVENTARIO  /  OBJETOS EN TU PODER",150,183)
                items = [
                    ("wood",self.wood_count),
                    ("metal_bolt",self.metal_bolt),
                    ("fathers_sword",int(self.fathers_sword)),
                    ("sylvarin_boots",int(self.sylvarin_boots)),
                    ("house_key",int(self.house_key)),
                ]
                if self.tools_collected:
                    items.extend((tool, 1) for tool in ("axe","hoe","pickaxe","scythe","watering_can"))
                visible = [(item,qty) for item,qty in items if qty > 0]
                # Cuadricula visual fija de 16 huecos; el estado de las misiones
                # sigue siendo la fuente de verdad hasta migrar los objetos.
                for i in range(16):
                    x,y = 155+(i%4)*164,215+(i//4)*74
                    pygame.draw.rect(s,(255,255,255),(x,y,150,66))
                    pygame.draw.rect(s,LINE,(x,y,150,66),1)
                    if i < len(visible):
                        item,qty = visible[i]
                        title = {"axe":"Hacha","hoe":"Azada","pickaxe":"Pico","scythe":"Guadana","watering_can":"Regadera"}.get(item,self.chapter["items"].get(item,{}).get("title",item))
                        self.label(str(title)[:19],x+7,y+10)
                        self.label("x%d" % qty,x+7,y+37)
                if not visible:
                    self.label("No tienes objetos todavia.",160,530)
            else:
                self.label("MISIONES PRINCIPALES",150,182)
                self.label("M1  LAS TIERRAS DE ALMARIN",155,220)
                self.label("Completada" if self.elder_met else "Busca al anciano en la finca",175,247)
                if self.elder_met:
                    self.label("M2  UN TECHO PROPIO",155,285)
                    if self.port_meeting:
                        objective = "COMPLETADA - Espada de Almarin recibida"
                    elif self.gate_repaired:
                        objective = "Busca al anciano en el puerto" if self.elder_clue else "Habla con el anciano en la posada"
                    elif not self.elder_after_fence:
                        objective = ("Repara la valla: %d/%d tramos" % (len(self.repaired_fences),len(self.data.get("fence_gaps",[])))) if self.mission_stage == "repair_fence" else "Habla con el anciano en la entrada"
                    elif not self.gate_inspected:
                        objective = "Examina la puerta de la finca"
                    else:
                        objective = "Puerta: %d/15 madera, %d/1 cerrojo" % (min(self.wood_count,15),min(self.metal_bolt,1))
                    self.label(objective,175,313)
                if self.port_meeting:
                    self.label("M3  LA ULTIMA MADRIGUERA",155,342)
                    self.label({"ready":"Habla con el anciano en la verja de la finca", "hunt":"Investiga la maleza: %d/%d" % (len(self.farm_kills),len(self.data.get("ambushes",[]))), "boss":"Derrota a la criatura mayor", "fade":"Victoria", "approach":"Habla con el anciano", "complete":"COMPLETADA - Llave recibida"}.get(self.farm_state,"Recupera la finca"),175,364)
                self.label("MISIONES SECUNDARIAS",150,392)
                if self.smith_quest != "not_started":
                    self.label("S1  EL HIERRO QUE CANTA",155,420)
                    status = {"investigate":"Investiga a Sylvarin","artisan_explained":"Vuelve con el herrero","completed":"Completada"}
                    self.label(status.get(self.smith_quest,"En curso"),175,442)
                if self.rat_quest != "not_started":
                    self.label("S2  CUANDO CALLAN LAS CAMPANAS",155,482)
                    self.label("Completada" if self.rat_quest == "completed" else ("Vuelve con Sylvarin" if self.rat_quest == "cleared" else "Despeja el almacen de la artesana"),175,505)
            pygame.display.flip()
            return
        if False and self.mission:
            objectives = {"find_elder":"Busca al anciano en la finca",
                          "collect_wood":"Recoge madera (%d/3)" % len(self.wood),
                          "repair_gate":"Repara la puerta de la finca",
                          "gate_repaired":"Entra en la finca"}
            self.label("MISION: LAS TIERRAS DE ALMARIN",24,93)
            self.label(objectives.get(self.mission_stage,""),24,117)
        if self.notice_timer > 0:
            pygame.draw.rect(s,(255,255,255),(20,145,650,35))
            pygame.draw.rect(s,LINE,(20,145,650,35),1)
            self.label(self.notice,30,155)
        if self.modal:
            pygame.draw.rect(s,(255,255,255),(35,430,890,165))
            pygame.draw.rect(s,LINE,(35,430,890,165),2)
            for i,line in enumerate(self.modal[:3]):
                self.label(line[:105],55,450+i*24)
            for i,(label,action) in enumerate(self.modal_actions):
                self.label(("> " if i == self.modal_selection else "  ")+label,55+i*300,540)
            self.label("CLIC / ENTER",790,575)
        if self.farm_dialogue:
            pygame.draw.rect(s,(255,255,255),(35,450,890,140))
            pygame.draw.rect(s,LINE,(35,450,890,140),1)
            self.label(self.farm_dialogue,55,490)
            self.label("E / ENTER PARA CERRAR",700,565)
        if self.phase == "dialogue":
            who,line = self.story["script"][self.step]
            if self.step == 10:
                who,line = "TU","¿Que fue lo que viste?"
            if self.step == 11: line = self.response
            pygame.draw.rect(s,(255,255,255),(35,450,890,140))
            pygame.draw.rect(s,LINE,(35,450,890,140),1)
            self.label(who,55,467)
            if self.step == 10:
                for i,option in enumerate(self.story["choices"]):
                    self.label(("> " if i == self.choice else "  ")+option,58,493+i*25)
            else:
                words,linebuf,y = line.split(),"",495
                for word in words:
                    trial = (linebuf+" "+word).strip()
                    if self.font.size(trial)[0]>820 and linebuf:
                        self.label(linebuf,58,y)
                        linebuf,y = word,y+22
                    else: linebuf=trial
                if linebuf: self.label(linebuf,58,y)
            self.label("ENTER / ESPACIO",785,565)
        if self.phase == "fade":
            overlay = pygame.Surface((W,H))
            overlay.fill((255,255,255))
            overlay.set_alpha(int(self.fade*255))
            s.blit(overlay,(0,0))
        if self.name == "granja" and self.farm_state == "fade":
            overlay = pygame.Surface((W,H))
            overlay.fill((0,0,0))
            overlay.set_alpha(int(self.farm_fade*255))
            s.blit(overlay,(0,0))
        pygame.display.flip()

    def actor(self,name,pos,cx,cy):
        pygame.draw.circle(self.screen,LINE,(int(pos.x-cx),int(pos.y-cy)),15,1)
        self.label(name,pos.x-cx-35,pos.y-cy-33)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running=False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.journal_open = not self.journal_open
                        continue
                    if self.journal_open:
                        if event.key in (pygame.K_LEFT,pygame.K_RIGHT):
                            self.menu_tab = "misiones" if self.menu_tab == "inventario" else "inventario"
                        elif event.key == pygame.K_1:
                            self.menu_tab = "inventario"
                        elif event.key == pygame.K_2:
                            self.menu_tab = "misiones"
                        continue
                    if self.modal:
                        if event.key in (pygame.K_LEFT,pygame.K_a,pygame.K_UP):
                            self.modal_selection = (self.modal_selection-1)%len(self.modal_actions)
                        elif event.key in (pygame.K_RIGHT,pygame.K_d,pygame.K_DOWN):
                            self.modal_selection = (self.modal_selection+1)%len(self.modal_actions)
                        elif event.key in (pygame.K_RETURN,pygame.K_SPACE):
                            self.modal_action(self.modal_actions[self.modal_selection][1])
                        continue
                    if self.phase == "dialogue":
                        if self.step == 10 and event.key in (pygame.K_UP,pygame.K_w): self.choice=(self.choice-1)%3
                        elif self.step == 10 and event.key in (pygame.K_DOWN,pygame.K_s): self.choice=(self.choice+1)%3
                        elif event.key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_e): self.advance()
                    elif self.phase == "free" and event.key in (pygame.K_SPACE,pygame.K_f): self.attack()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.journal_open:
                        x,y = event.pos
                        if 110 <= y <= 152:
                            if 150 <= x <= 320:
                                self.menu_tab = "inventario"
                            elif 330 <= x <= 500:
                                self.menu_tab = "misiones"
                        continue
                    if self.modal:
                        x,y = event.pos
                        if y >= 515:
                            idx = min(len(self.modal_actions)-1,max(0,int((x-55)//300)))
                            self.modal_action(self.modal_actions[idx][1])
                        else:
                            self.modal_action(self.modal_actions[self.modal_selection][1])
                    elif self.phase == "dialogue":
                        self.advance()
                    elif self.name == "granja" and self.farm_state in ("hunt","boss"):
                        cx = max(0,min(self.data["width"]-W,self.player.x-W/2)) if self.data["width"]>W else (self.data["width"]-W)/2
                        cy = max(0,min(self.data["height"]-H,self.player.y-H/2)) if self.data["height"]>H else (self.data["height"]-H)/2
                        aim = pygame.Vector2(event.pos)+pygame.Vector2(cx,cy)-self.player
                        if aim.length_squared() > 0:
                            self.facing = aim.normalize()
                        self.attack()
                    elif self.name in ("granja","pueblo","taller_sylvarin","puerto","salon_posada","casa_almarin","taller_almarin"):
                        cx = max(0,min(self.data["width"]-W,self.player.x-W/2)) if self.data["width"]>W else (self.data["width"]-W)/2
                        cy = max(0,min(self.data["height"]-H,self.player.y-H/2)) if self.data["height"]>H else (self.data["height"]-H)/2
                        self.click_world(pygame.Vector2(event.pos)+pygame.Vector2(cx,cy))
                    elif self.phase == "free":
                        self.attack()
            self.update(self.clock.tick(60)/1000)
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    Game().run()
