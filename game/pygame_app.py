import sys
import pygame
from game.world_objects import WORLD_OBJECTS
from game.hud.hud_renderer import draw_hud
from game.ui_renderer import draw_log
from game.world.world_renderer import draw_world_background
from game.world.camera import get_camera_position
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.inventory.hotbar_state import HOTBAR_SIZE, ensure_hotbar_state
from game.inventory.inventory_manager import has_item
from game.inventory.item_database import get_item_data


def get_hotbar_slots(state):
    ensure_hotbar_state(state)
    return state["hotbar"]["slots"]


def get_active_hotbar_index(state):
    ensure_hotbar_state(state)
    return state["hotbar"]["active_index"]


def set_active_hotbar_index(state, index):
    ensure_hotbar_state(state)

    if index < 0 or index >= HOTBAR_SIZE:
        return False

    state["hotbar"]["active_index"] = index
    return True


def get_active_item_id(state):
    slots = get_hotbar_slots(state)
    active_index = get_active_hotbar_index(state)

    return slots[active_index]


def get_active_item_data(state):
    active_item_id = get_active_item_id(state)

    if active_item_id is None:
        return None

    return get_item_data(active_item_id)


def get_active_tool(state):
    item_data = get_active_item_data(state)

    if item_data is None:
        return None

    if item_data.get("type") != "tool":
        return None

    return item_data.get("tool_type")


def assign_item_to_hotbar(state, index, item_id):
    ensure_hotbar_state(state)

    if index < 0 or index >= HOTBAR_SIZE:
        return False

    if item_id is not None and not has_item(state, item_id):
        return False

    state["hotbar"]["slots"][index] = item_id
    return True
from core.rules_engine import (
    advance_day,
    build_upgrade,
    continue_and_risk,
    secure_return,
    start_trip,
)
from core.save_manager import save_state

from game.player_controller import update_player_movement
from game.interaction_manager import get_nearby_object, interact_with_nearby_object

WIDTH = 960
HEIGHT = 640
FPS = 60

PANEL = (238, 230, 204)
DARK = (48, 55, 43)
ACCENT = (119, 146, 88)
WARN = (151, 76, 60)
WHITE = (250, 248, 235)


class PygameApp:
    def __init__(self, state, game_data):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maritime RPG Prototype v4")
        self.clock = pygame.time.Clock()

        self.state = state
        self.game_data = game_data

        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 28, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)

        self.nearby_object = None
        self.player_speed = 180
        self.interaction_range = 45

        self.menu_open = False
        self.menu_tab = "inventory"
        self.hud_visible = True

        self.log = list(state.get("log", []))[-7:]

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.menu_open:
                    interact_with_nearby_object(self)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu_open = not self.menu_open

                elif self.menu_open:
                    self.handle_menu_key(event.key)

                else:
                    self.handle_game_key(event.key)

    def handle_game_key(self, key):
        if key == pygame.K_1:
            set_active_hotbar_index(self.state, 0)
            item = get_active_item_data(self.state)
            self.add_log(f"Equipado: {item['name']}")
            return

        if key == pygame.K_2:
            set_active_hotbar_index(self.state, 1)
            item = get_active_item_data(self.state)
            self.add_log(f"Equipado: {item['name']}")
            return

        if key == pygame.K_3:
            set_active_hotbar_index(self.state, 2)
            item = get_active_item_data(self.state)
            self.add_log(f"Equipado: {item['name']}")
            return
        
        if key == pygame.K_RETURN or key == pygame.K_e:
            interact_with_nearby_object(self)


    def handle_menu_key(self, key):
        tabs = ["inventory", "routes", "upgrades", "plants", "recipes", "options"]
        current_index = tabs.index(self.menu_tab)

        if key == pygame.K_RIGHT:
            self.menu_tab = tabs[(current_index + 1) % len(tabs)]

        elif key == pygame.K_LEFT:
            self.menu_tab = tabs[(current_index - 1) % len(tabs)]



    def update(self, dt):
        if self.menu_open:
            return

        update_player_movement(self.state, self.player_speed, dt)

        self.nearby_object = get_nearby_object(
            self.state,
            self.game_data,
            self.interaction_range
        )

    def sleep_day(self):
        messages = advance_day(self.state, self.game_data)

        for message in messages:
            self.add_log(message)

    def add_log(self, message):
        self.log.append(message)
        self.log = self.log[-7:]
        self.state["log"] = self.log

    def draw(self):
        draw_world_background(self.screen)

        self.draw_map()
        draw_log(self)

        if self.hud_visible:
            draw_hud(self)

        if self.menu_open and self.hud_visible:
            self.draw_menu()

        pygame.display.flip()



    def draw_map(self):
        player = self.state["player"]

        camera_x, camera_y = get_camera_position(
            player["x"],
            player["y"],
            WIDTH,
            HEIGHT,
            WORLD_WIDTH,
            WORLD_HEIGHT,
        )

        for world_object in WORLD_OBJECTS:
            x = int(world_object["x"] - camera_x)
            y = int(world_object["y"] - camera_y)
            selected = self.nearby_object is not None and world_object["id"] == self.nearby_object["id"]

            radius = world_object["radius"] + 7 if selected else world_object["radius"]
            color = WHITE if selected else PANEL

            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, DARK, (x, y), radius, 3)

            icon = world_object["icon"]

            icon = world_object["icon"]

            if world_object["type"] == "tree" and "hp" in world_object and "max_hp" in world_object:
                hp_percent = world_object["hp"] / world_object["max_hp"]

                if hp_percent >= 1:
                    icon = "T"
                elif hp_percent >= 0.5:
                    icon = "t"
                else:
                    icon = "|"

            self.draw_text(icon, x - 6, y - 10, DARK, self.big_font)
            self.draw_text(world_object["name"], x - 34, y + radius + 8, DARK, self.small_font)

            if selected:
                self.draw_text("E", x - 5, y - radius - 28, WARN, self.big_font)

        player = self.state["player"]
        px = int(player["x"] - camera_x)
        py = int(player["y"] - camera_y)

        pygame.draw.circle(self.screen, DARK, (px, py), 13)
        pygame.draw.circle(self.screen, WHITE, (px, py - 18), 9)

        if self.nearby_object is None:
            self.draw_text(
                "WASD/Flechas: moverse | E/Enter: interactuar",
                80,
                530,
                DARK
            )
        else:
            self.draw_text(
                f"Cerca: {self.nearby_object['name']} | E/Enter interactuar",
                80,
                530,
                DARK
            )

        self.draw_ship_panel()

    def draw_ship_panel(self):
        ship = self.state["ship"]

        pygame.draw.rect(self.screen, PANEL, (710, 120, 220, 260), border_radius=8)
        pygame.draw.rect(self.screen, DARK, (710, 120, 220, 260), 3, border_radius=8)

        self.draw_text("BARCO", 730, 140, DARK, self.big_font)

        if ship["status"] == "available":
            self.draw_text("Disponible", 730, 185, DARK)
            return

        route = self.game_data["routes"][ship["route"]]

        self.draw_text(route["name"], 730, 185, DARK)
        self.draw_text(f"Dias: {ship['days_left']}", 730, 215, DARK)
        self.draw_text(f"Exito: {ship['success_rate']}%", 730, 245, DARK)

        if ship.get("pending_event") == "arrival_decision":
            self.draw_text("DECISION!", 730, 285, WARN, self.big_font)
            self.draw_text("ESC > Rutas", 730, 325, DARK)

    def draw_log(self):
        pygame.draw.rect(self.screen, PANEL, (60, 555, 870, 70), border_radius=8)
        pygame.draw.rect(self.screen, DARK, (60, 555, 870, 70), 2, border_radius=8)

        last_messages = self.log[-3:]

        for index, message in enumerate(last_messages):
            self.draw_text(message[:105], 76, 568 + index * 18, DARK, self.small_font)

    def draw_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, PANEL, (90, 95, 780, 450), border_radius=10)
        pygame.draw.rect(self.screen, DARK, (90, 95, 780, 450), 3, border_radius=10)

        tabs = ["inventory", "routes", "upgrades", "plants", "recipes", "options"]

        labels = {
            "inventory": "Inventario",
            "routes": "Rutas",
            "upgrades": "Mejoras",
            "plants": "Plantas",
            "recipes": "Recetas",
            "options": "Opciones",
        }

        for index, tab in enumerate(tabs):
            x = 115 + index * 120
            color = WHITE if tab == self.menu_tab else (220, 210, 180)

            pygame.draw.rect(self.screen, color, (x, 115, 105, 34), border_radius=5)
            pygame.draw.rect(self.screen, DARK, (x, 115, 105, 34), 2, border_radius=5)

            self.draw_text(labels[tab], x + 8, 124, DARK, self.small_font)

        if self.menu_tab == "inventory":
            self.draw_inventory_tab()

        elif self.menu_tab == "routes":
            self.draw_routes_tab()

        elif self.menu_tab == "upgrades":
            self.draw_upgrades_tab()

        else:
            self.draw_text("Pendiente de prototipar.", 130, 190, DARK)

        self.draw_text("ESC cerrar | LEFT/RIGHT tabs | S guardar", 130, 510, DARK, self.small_font)

    def draw_inventory_tab(self):
        resources = self.state["resources"]
        x0 = 130
        y0 = 180
        cell_w = 165
        cell_h = 70

        for index, item in enumerate(self.game_data["resources"].items()):
            key, data = item
            row = index // 4
            col = index % 4

            x = x0 + col * cell_w
            y = y0 + row * cell_h

            pygame.draw.rect(self.screen, WHITE, (x, y, 145, 54), border_radius=6)
            pygame.draw.rect(self.screen, DARK, (x, y, 145, 54), 2, border_radius=6)

            amount = resources.get(key, 0)

            self.draw_text(f"{data['icon']} {data['name']}", x + 10, y + 8, DARK, self.small_font)
            self.draw_text(f"x{amount}", x + 10, y + 30, DARK)

    def draw_routes_tab(self):
        y = 180
        ship = self.state["ship"]

        if ship.get("pending_event") == "arrival_decision":
            self.draw_text("Decision de expedicion pendiente:", 130, y, WARN)
            self.draw_text("A = asegurar botin | R = arriesgar", 130, y + 30, DARK)

            keys = pygame.key.get_pressed()

            if keys[pygame.K_a]:
                self.add_log(secure_return(self.state, self.game_data))
                self.menu_open = False

            elif keys[pygame.K_r]:
                self.add_log(continue_and_risk(self.state, self.game_data))
                self.menu_open = False

            return

        self.draw_text("Pulsa 1/2/3 para enviar el barco.", 130, y, DARK)
        y += 35

        route_keys = list(self.game_data["routes"].keys())
        keys = pygame.key.get_pressed()

        for index, route_key in enumerate(route_keys):
            route = self.game_data["routes"][route_key]

            self.draw_text(
                f"{index + 1}. {route['name']} - {route['duration']} dias - coste {route['cost']}",
                130,
                y,
                DARK,
                self.small_font
            )
            y += 42

            if keys[pygame.K_1 + index]:
                self.add_log(start_trip(self.state, self.game_data, route_key))
                self.menu_open = False

    def draw_upgrades_tab(self):
        self.draw_text("Pulsa 1/2/3 para construir mejora.", 130, 180, DARK)

        y = 220
        upgrade_keys = list(self.game_data["upgrades"].keys())
        keys = pygame.key.get_pressed()

        for index, upgrade_key in enumerate(upgrade_keys):
            upgrade = self.game_data["upgrades"][upgrade_key]
            owned = self.state["upgrades"].get(upgrade_key, False)
            status = "OK" if owned else "Pendiente"

            self.draw_text(
                f"{index + 1}. {upgrade['name']} - {status} - coste {upgrade['cost']}",
                130,
                y,
                DARK,
                self.small_font
            )
            y += 42

            if keys[pygame.K_1 + index]:
                self.add_log(build_upgrade(self.state, self.game_data, upgrade_key))
                self.menu_open = False

    def draw_text(self, text, x, y, color, font=None):
        if font is None:
            font = self.font

        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))