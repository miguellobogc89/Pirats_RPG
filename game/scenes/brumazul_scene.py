"""Capitulo 1: escenas integradas en el motor principal de Pirats RPG.

La logica de inventario, hotbar, movimiento y recoleccion sigue en PygameApp.
prototype_beach.py se conserva como referencia visual y narrativa.
"""
import math
import pygame

from game.scenes.farm_scene import FarmScene
from game.collectable_manager import update_collectables
from game.data.item_database import get_item_data
from game.hud.hud_renderer import draw_hud
from game.hud.menu_overlay import draw_menu
from game.notifications import draw_notifications
from game.world.camera import get_camera_position
from game.pygame_app import WIDTH, HEIGHT

INK = (35, 39, 40)
PAPER = (245, 245, 242)
LINE = (175, 180, 181)

DIALOGUE = [
    ("POSADERA", "Vaya, has despertado. Pensabamos que no lo contarias."),
    ("POSADERA", "Te encontraron al amanecer junto al camino. Apenas respirabas."),
    ("POSADERA", "No quiero asustarte, pero... ¿que ocurrio anoche?"),
    ("TU", "Algo me siguio desde la playa. Era una criatura enorme."),
    ("POSADERA", "En Brumazul hay alimanas, pero nunca habia oido algo asi."),
    ("POSADERA", "Espera. Hay un hombre que lleva horas preguntando por ti."),
    ("ENTRADA", ""),
    ("ANCIANO", "Asi que has sobrevivido. Eso ya es mas de lo que esperaba."),
    ("ANCIANO", "Dicen que viste una criatura cerca del camino de la playa."),
    ("ANCIANO", "Dime una cosa. ¿Que recuerdas de ella?"),
    ("ELECCION", ""),
    ("ANCIANO", "Ya veo..."),
    ("POSADERA", "La conoceis? Habeis palidecido."),
    ("ANCIANO", "No he dicho tal cosa. Mejor no alarmar a los vecinos."),
    ("ANCIANO", "Escuchame bien: no vuelvas a la playa despues del anochecer."),
    ("ANCIANO", "Conoci a tu padre. Almarin Velhart. Hace muchos anos."),
    ("ANCIANO", "Te dejo algo aqui: una finca a las afueras de Brumazul."),
    ("ANCIANO", "Cuando puedas caminar, ven a buscarme a la entrada."),
    ("POSADERA", "Y antes comeras. No pienso recoger otro desmayado del suelo."),
]
CHOICES = [
    "Era enorme y avanzaba lentamente.",
    "Vi sus ojos brillando en la oscuridad.",
    "Parecia conocer el camino al pueblo.",
]
RESPONSES = [
    "Tan grande... (Aprieta los labios, inquieto.)",
    "Esos ojos... (Por un momento parece reconocerlos.)",
    "Ese camino... (Guarda un silencio demasiado largo.)",
]


class BrumazulScene(FarmScene):
    def enter(self):
        self.beach = self.scene_id == "brumazul_playa"
        self.boss = pygame.Vector2(600, 640)
        self.boss_awake = False
        self.boss_timer = 0.0
        self.invulnerable = 0.0
        self.attack_timer = 0.0
        self.boss_hp = 999
        self.entrance_timer = 0.0
        self.elder_y = 640.0
        self.dialogue_index = 0
        self.choice_index = 0
        self.inn_phase = "dialogue"
        self.app.menu_open = False
        self.app.stash_open = False
        self.app.state.setdefault("brumazul", {})
        if self.beach:
            self.app.state["brumazul"]["chapter_started"] = True
            self.seed_collectables()

    def seed_collectables(self):
        """Los objetos se recogen mediante el gestor de recoleccion real."""
        from game.data.item_database import get_item_data
        from game.collectable_manager import ensure_collectables_state
        ensure_collectables_state(self.app.state)
        flag = self.app.state["brumazul"]
        if flag.get("beach_drops_spawned"):
            return
        for item_id in ("wood", "madera", "stone", "piedra"):
            if get_item_data(item_id) is not None:
                for i, (x, y) in enumerate(((315, 575), (485, 725), (560, 560))):
                    self.app.state["collectables"].append({
                        "id": "brumazul_" + item_id + "_" + str(i),
                        "item_id": item_id, "amount": 1, "x": x, "y": y, "radius": 10,
                    })
                flag["beach_drops_spawned"] = True
                break

    def handle_event(self, event):
        if not self.beach and self.inn_phase != "free":
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if self.inn_phase == "dialogue":
                if event.type == pygame.KEYDOWN and self.dialogue_index == 10:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.choice_index = (self.choice_index - 1) % 3
                        return True
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.choice_index = (self.choice_index + 1) % 3
                        return True
                if (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e)) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                    if self.dialogue_index == 10:
                        DIALOGUE[11] = ("ANCIANO", RESPONSES[self.choice_index])
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(DIALOGUE):
                        self.inn_phase = "free"
                        self.app.state["brumazul"]["mission"] = "las_tierras_de_almarin"
                        self.app.add_log("MISION: LAS TIERRAS DE ALMARIN | Busca al anciano en la finca")
                    elif self.dialogue_index == 6:
                        self.inn_phase = "entrance"
                    return True
            return True
        if self.beach and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.app.menu_open:
            self.attack(event.pos)
            return True
        return super().handle_event(event)

    def attack(self, mouse):
        if self.attack_timer > 0:
            return
        self.attack_timer = 0.42
        player = self.app.state["player"]
        px, py = player["x"], player["y"]
        cam_x, cam_y = get_camera_position(px, py, WIDTH, HEIGHT, 800, 800)
        direction = pygame.Vector2(mouse[0] + cam_x - px, mouse[1] + cam_y - py)
        target = self.boss - pygame.Vector2(px, py)
        if direction.length_squared() and target.length() < 105 and target.length_squared() and direction.normalize().dot(target.normalize()) > 0.35:
            self.boss_hp -= 25
            self.app.add_log("Golpeas a la criatura (-25).")

    def update(self, dt):
        dt = min(dt, 0.05)
        if self.beach:
            self.app.update_farm_scene(dt)
            if self.app.menu_open or self.app.stash_open:
                return
            self.attack_timer = max(0, self.attack_timer - dt)
            self.boss_timer = max(0, self.boss_timer - dt)
            self.invulnerable = max(0, self.invulnerable - dt)
            p = pygame.Vector2(self.app.state["player"]["x"], self.app.state["player"]["y"])
            if not self.boss_awake and p.distance_to(self.boss) < 160:
                self.boss_awake = True
                self.app.add_log("La criatura despierta y comienza a perseguirte.")
            if self.boss_awake:
                delta = p - self.boss
                if delta.length_squared():
                    self.boss += delta.normalize() * min(delta.length(), 42 * dt)
                if delta.length() < 77 and self.boss_timer <= 0:
                    self.boss_timer = 1.6
                    if self.invulnerable <= 0:
                        health = self.app.state["health"]
                        health["current"] = max(0, health["current"] - 2)
                        self.invulnerable = 1.4
                        if health["current"] <= 0:
                            self.wake_at_inn()
                self.boss_timer = max(0, self.boss_timer - dt)
        elif self.inn_phase == "entrance":
            self.elder_y -= 100 * dt
            if self.elder_y <= 450:
                self.elder_y = 450
                self.dialogue_index = 7
                self.inn_phase = "dialogue"
        elif self.inn_phase == "free":
            self.app.update_farm_scene(dt)

    def wake_at_inn(self):
        self.app.state["health"]["current"] = self.app.state["health"]["max"]
        self.app.state["brumazul"]["beach_completed"] = True
        self.app.scene_manager.change_scene("brumazul_posada", payload={"target_spawn_id": "despertar"})
        self.app.dispatch_scene_entered_event()

    def draw(self):
        s = self.app.screen
        s.fill(PAPER)
        p = self.app.state["player"]
        cx, cy = get_camera_position(p["x"], p["y"], WIDTH, HEIGHT, 800, 800)
        if self.beach:
            pygame.draw.rect(s, (230, 230, 228), (0, 0, WIDTH, HEIGHT))
            for x in range(0, 800, 40):
                for y in range(0, 800, 40):
                    sx, sy = x - cx, y - cy
                    if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                        pygame.draw.rect(s, LINE, (sx, sy, 40, 40), 1)
            pygame.draw.rect(s, (205, 212, 212), (0 - cx, 0 - cy, 800, 170))
            for obj in self.app.state.get("collectables", []):
                if obj.get("id", "").startswith("brumazul_"):
                    pygame.draw.circle(s, (110, 130, 110), (int(obj["x"] - cx), int(obj["y"] - cy)), 8)
            bx, by = int(self.boss.x - cx), int(self.boss.y - cy)
            pygame.draw.circle(s, INK, (bx, by), 40, 3)
            pygame.draw.circle(s, INK, (bx - 12, by - 8), 5)
            pygame.draw.circle(s, INK, (bx + 12, by - 8), 5)
            self.label("PLAYA DE BRUMAZUL - NOCHE", 20, 16)
        else:
            room = pygame.Rect(200 - cx, 200 - cy, 400, 400)
            pygame.draw.rect(s, (235, 235, 233), room)
            pygame.draw.rect(s, INK, room, 3)
            pygame.draw.rect(s, LINE, (280 - cx, 400 - cy, 80, 120), 2)
            pygame.draw.rect(s, LINE, (480 - cx, 280 - cy, 80, 80), 2)
            pygame.draw.circle(s, INK, (int(480 - cx), int(400 - cy)), 17, 2)
            self.label("POSADERA", int(445 - cx), int(365 - cy))
            if self.dialogue_index >= 7 or self.inn_phase == "entrance":
                pygame.draw.circle(s, INK, (int(470 - cx), int(self.elder_y - cy)), 17, 2)
                self.label("ANCIANO", int(435 - cx), int(self.elder_y - cy - 35))
            self.label("POSADA DE BRUMAZUL - AMANECER", 20, 16)
        pygame.draw.circle(s, INK, (int(p["x"] - cx), int(p["y"] - cy)), 13)
        pygame.draw.circle(s, PAPER, (int(p["x"] - cx), int(p["y"] - cy - 16)), 8)
        if self.app.hud_visible:
            draw_hud(self.app)
        if self.app.menu_open:
            draw_menu(self.app)
        if self.app.stash_open:
            from game.hud.stash_overlay import draw_stash_overlay
            draw_stash_overlay(self.app)
        if not self.beach and self.inn_phase == "dialogue":
            pygame.draw.rect(s, (252, 251, 247), (30, HEIGHT - 190, WIDTH - 60, 145))
            pygame.draw.rect(s, INK, (30, HEIGHT - 190, WIDTH - 60, 145), 2)
            who, line = DIALOGUE[self.dialogue_index]
            self.label(who, 50, HEIGHT - 174)
            if who == "ELECCION":
                for i, choice in enumerate(CHOICES):
                    self.label(("> " if i == self.choice_index else "  ") + choice, 55, HEIGHT - 150 + i * 26)
            else:
                self.label(line, 50, HEIGHT - 140)
                self.label("ENTER / ESPACIO para continuar", 50, HEIGHT - 76)
        if not self.beach and self.inn_phase == "free":
            self.label("MISION: LAS TIERRAS DE ALMARIN", 30, HEIGHT - 65)
        draw_notifications(self.app)

    def label(self, value, x, y):
        self.app.screen.blit(self.app.small_font.render(value, True, INK), (x, y))
