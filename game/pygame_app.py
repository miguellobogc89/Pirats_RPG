import sys
import pygame

from core.rules_engine import (
    advance_day,
)
from game.hud.hud_renderer import draw_hud
from game.time_manager import update_time
from game.interaction_manager import get_nearby_object, interact_with_nearby_object

from game.inventory.hotbar_manager import (
    get_active_item_data,
    get_active_item_id,
    get_active_tool,
    set_active_hotbar_index,
)
from game.world.grid_manager import TILE_SIZE, world_to_grid, grid_to_world
from game.player_controller import update_player_movement
from game.ui_renderer import draw_log
from game.world.camera import get_camera_position
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.world.world_renderer import draw_world_background
from game.world_objects import WORLD_OBJECTS
from game.hud.menu_overlay import draw_menu
from game.collectable_manager import update_collectables
from game.data.item_database import get_item_data
from game.farming.farming_manager import advance_farming_day
from game.world.grid_renderer import (
    draw_world_grid,
    draw_tilled_cells,
    draw_watered_cells,
    draw_crops,
)

WIDTH = 960
HEIGHT = 640
FPS = 60

PANEL = (238, 230, 204)
DARK = (48, 55, 43)
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

        self.placement_mode = False
        self.placement_item_id = None

        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 28, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)

        self.player_sprite = pygame.image.load(
            "assets/player/player_idle.png"
        ).convert_alpha()

        self.PANEL = PANEL
        self.DARK = DARK
        self.WARN = WARN
        self.WHITE = WHITE

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
                    self.handle_game_key(pygame.K_e)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu_open = not self.menu_open
                elif self.menu_open:
                    self.handle_menu_key(event.key)
                else:
                    self.handle_game_key(event.key)

    def handle_game_key(self, key):
        number_keys = [
            pygame.K_1,
            pygame.K_2,
            pygame.K_3,
            pygame.K_4,
            pygame.K_5,
            pygame.K_6,
            pygame.K_7,
            pygame.K_8,
        ]

        if key in number_keys:
            index = number_keys.index(key)
            set_active_hotbar_index(self.state, index)

            item = get_active_item_data(self.state)

            if item is None:
                self.add_log(f"Slot {index + 1} vacío.")
            else:
                self.add_log(f"Equipado: {item['name']}")

            return

        if key == pygame.K_RETURN or key == pygame.K_e:
            if self.nearby_object is not None:
                if self.nearby_object["type"] == "bed" or self.nearby_object["type"] == "dock":
                    interact_with_nearby_object(self)
                    return
                

            from game.farming.farming_manager import harvest_crop
            from game.inventory.inventory_manager import add_item

            harvest_result = harvest_crop(
                self.state,
                self.state["player"]["x"],
                self.state["player"]["y"],
            )

            if harvest_result["status"] == "harvested":
                added = add_item(
                    self.state,
                    harvest_result["item_id"],
                    harvest_result["amount"],
                )

                if added:
                    self.add_log(f"Cosechas {harvest_result['item_id']} x{harvest_result['amount']}.")
                else:
                    self.add_log("Inventario lleno.")

                return

            if harvest_result["status"] == "removed_dead":
                self.add_log("Has retirado una planta seca.")
                return
            active_item = get_active_item_data(self.state)
            active_tool = get_active_tool(self.state)

            if active_item is not None and active_item.get("type") == "placeable":
                self.placement_mode = True
                self.placement_item_id = get_active_item_id(self.state)
                self.add_log(f"Colocando: {active_item['name']}")
                return

            if active_tool == "hoe":
                from game.farming.farming_manager import till_cell

                tilled = till_cell(
                    self.state,
                    self.state["player"]["x"],
                    self.state["player"]["y"],
                )

                if tilled:
                    self.add_log("Has arado la tierra.")
                else:
                    self.add_log("Esta celda ya está arada.")

                return

            if active_tool == "watering_can":
                from game.farming.farming_manager import water_cell

                result = water_cell(
                    self.state,
                    self.state["player"]["x"],
                    self.state["player"]["y"],
                )

                if result == "not_tilled":
                    self.add_log("Solo puedes regar tierra arada.")
                    return

                if result == "already_watered":
                    self.add_log("Esta celda ya está regada.")
                    return

                self.add_log("Has regado la tierra.")
                return

            if active_item is not None and active_item.get("type") == "seed":
                from game.farming.farming_manager import plant_crop
                from game.inventory.inventory_manager import remove_item

                result = plant_crop(
                    self.state,
                    self.state["player"]["x"],
                    self.state["player"]["y"],
                    active_item["crop_id"],
                )

                if result == "not_tilled":
                    self.add_log("Primero tienes que arar la tierra.")
                    return

                if result == "occupied":
                    self.add_log("Ya hay algo plantado aquí.")
                    return

                active_item_id = get_active_item_id(self.state)
                removed = remove_item(self.state, active_item_id, 1)

                if not removed:
                    self.add_log("No tienes semillas suficientes.")
                    return

                self.add_log("Has plantado una semilla.")
                return

            interact_with_nearby_object(self)

    def handle_menu_key(self, key):
        tabs = ["inventory", "routes", "upgrades", "plants", "recipes", "options"]
        current_index = tabs.index(self.menu_tab)

        if key == pygame.K_RIGHT:
            self.menu_tab = tabs[(current_index + 1) % len(tabs)]

        elif key == pygame.K_LEFT:
            self.menu_tab = tabs[(current_index - 1) % len(tabs)]

    def update(self, dt):
        update_time(self.state, dt)

        if self.menu_open:
            return

        update_player_movement(self.state, self.player_speed, dt)
        update_collectables(self)

        self.nearby_object = get_nearby_object(
            self.state,
            self.game_data,
            self.interaction_range,
        )

    def sleep_day(self):
        messages = advance_day(self.state, self.game_data)

        dead_crops = advance_farming_day(self.state)

        for crop in dead_crops:
            self.add_log("Una planta se ha secado.")

        for message in messages:
            self.add_log(message)

    def add_log(self, message):
        self.log.append(message)
        self.log = self.log[-7:]
        self.state["log"] = self.log

    def draw(self):
        player = self.state["player"]

        camera_x, camera_y = get_camera_position(
            player["x"],
            player["y"],
            WIDTH,
            HEIGHT,
            WORLD_WIDTH,
            WORLD_HEIGHT,
        )

        draw_world_background(self.screen, camera_x, camera_y)
        draw_tilled_cells(self.screen, self.state, camera_x, camera_y)
        draw_watered_cells(self.screen, self.state, camera_x, camera_y)
        draw_crops(self.screen, self.state, camera_x, camera_y)
        draw_world_grid(self.screen, camera_x, camera_y)

        self.draw_map()

        if self.hud_visible:
            draw_hud(self)

        if self.menu_open and self.hud_visible:
            draw_menu(self)

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
        draw_world_grid(self.screen, camera_x, camera_y)

        destroyed_objects = self.state.get("destroyed_world_objects", [])

        for world_object in WORLD_OBJECTS:

            if world_object["id"] in destroyed_objects:
                continue

            x = int(world_object["x"] - camera_x)
            y = int(world_object["y"] - camera_y)
            selected = self.nearby_object is not None and world_object["id"] == self.nearby_object["id"]

            radius = world_object["radius"]
            if selected:
                radius += 7

            color = PANEL
            if selected:
                color = WHITE

            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, DARK, (x, y), radius, 3)

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

        for collectable in self.state.get("collectables", []):
            x = int(collectable["x"] - camera_x)
            y = int(collectable["y"] - camera_y)

            item_data = get_item_data(collectable["item_id"])

            pygame.draw.circle(self.screen, WHITE, (x, y), collectable["radius"])
            pygame.draw.circle(self.screen, DARK, (x, y), collectable["radius"], 2)

            if item_data is not None:
                self.draw_text(item_data["icon"], x - 5, y - 10, DARK, self.small_font)
        px = int(player["x"] - camera_x)
        py = int(player["y"] - camera_y)

        pygame.draw.circle(self.screen, DARK, (px, py), 13)
        pygame.draw.circle(self.screen, WHITE, (px, py - 18), 9)


        if self.placement_mode and self.placement_item_id is not None:
            item_data = get_item_data(self.placement_item_id)

            if item_data is not None:
                footprint = item_data.get("footprint", [1, 1])
                width = footprint[0]
                height = footprint[1]

                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mouse_x = mouse_x + camera_x
                world_mouse_y = mouse_y + camera_y

                grid_x, grid_y = world_to_grid(world_mouse_x, world_mouse_y)
                world_x, world_y = grid_to_world(grid_x, grid_y)

                screen_x = int(world_x - camera_x)
                screen_y = int(world_y - camera_y)

                preview_rect = pygame.Rect(
                    screen_x,
                    screen_y,
                    width * TILE_SIZE,
                    height * TILE_SIZE,
                )

                pygame.draw.rect(self.screen, (240, 220, 80), preview_rect, 2)
                self.draw_text(
                    item_data["icon"],
                    screen_x + 10,
                    screen_y + 6,
                    DARK,
                    self.big_font,
                )

        if self.nearby_object is None:
            self.draw_text("WASD/Flechas: moverse | E/Enter: interactuar", 80, 530, DARK)
        else:
            self.draw_text(f"Cerca: {self.nearby_object['name']} | E/Enter interactuar", 80, 530, DARK)


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

    def draw_text(self, text, x, y, color, font=None):
        if font is None:
            font = self.font

        surface = font.render(str(text), True, color)
        self.screen.blit(surface, (x, y))