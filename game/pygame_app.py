import sys
import pygame

from core.rules_engine import (
    advance_day,
)
from game.hud.hud_renderer import draw_hud
from game.time.time_manager import update_time, reset_time_to_wake_up
from game.interaction_manager import get_nearby_object, interact_with_nearby_object

from game.inventory.hotbar_manager import (
    get_active_item_data,
    get_active_item_id,
    get_active_tool,
    set_active_hotbar_index,
)
from game.world.grid_manager import TILE_SIZE, world_to_grid, grid_to_world
from game.cartography.cartography_manager import CartographyManager
from game.cartography.expedition_manager import ExpeditionManager
from game.cartography.cartography_validator import (
    format_validation_issue,
    validate_cartography_data,
)
from game.player_controller import update_player_movement
from game.skills.skill_manager import SkillManager
from game.ui_renderer import draw_log
from game.world.camera import get_camera_position
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.world.world_renderer import draw_world_background
from game.world_objects import WORLD_OBJECTS
from game.collectable_manager import update_collectables
from game.cartography.ui.cartography_overlay import draw_cartography_overlay
from game.cartography.ui.cartography_ui_state import CartographyUIState
from game.data.item_database import get_item_data
from game.ui.sprite_renderer import draw_item_sprite, draw_sprite_centered
from game.farming.farming_manager import advance_farming_day
from game.input.input_manager import handle_events
from game.bestiary.bestiary_manager import BestiaryManager
from game.combat.combat_manager import CombatManager
from game.hud.menu_overlay import draw_menu, get_menu_tab_at_position
from game.ui.ui_theme import create_game_fonts
from game.world.grid_renderer import (
    draw_world_grid,
    draw_tilled_cells,
    draw_watered_cells,
    draw_crops,
    draw_placed_objects,
    draw_occupied_cells_debug,
    draw_collision_debug,
)


WORLD_OBJECT_SPRITES = {
    "tree": "assets/world/object_tree.png",
    "rock": "assets/world/rock.png",
    "bush": "assets/world/object_bush.png",
    "fishing_spot": "assets/world/fishing_spot.png",
    "dock": "assets/world/dock.png",
    "ship": "assets/world/ship.png",
    "bed": "assets/world/bed.png",
}

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
        pygame.display.set_caption("Pirats RPG - RELOAD TEST")
        self.clock = pygame.time.Clock()

        self.state = state
        self.game_data = game_data

        self.cartography_manager = CartographyManager()
        self.cartography_manager.load_from_data(
            self.state["cartography"]
        )
        self.state["cartography"] = self.cartography_manager.get_save_data()
        self.expedition_manager = ExpeditionManager(self.cartography_manager)
        self.cartography_ui_state = CartographyUIState()

        self.skill_manager = SkillManager(self.state)

        self.bestiary_manager = BestiaryManager(self.state)
        self.combat_manager = CombatManager(self)

        self.placement_mode = False
        self.placement_item_id = None

        fonts = create_game_fonts()

        self.font = fonts["normal"]
        self.big_font = fonts["title"]
        self.small_font = fonts["small"]

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
        self.cartography_menu_open = False
        self.menu_tab = "inventory"
        self.hud_visible = True

        self.log = list(state.get("log", []))[-7:]
        self.run_cartography_validation_debug()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            handle_events(self)
            self.update(dt)
            self.draw()



    def update(self, dt):
        if self.combat_manager.is_active():
            self.combat_manager.update(dt)
            return
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
        reset_time_to_wake_up(self.state)

        dead_crops = advance_farming_day(self.state)

        for crop in dead_crops:
            self.add_log("Una planta se ha secado.")

        for message in messages:
            self.add_log(message)

    def add_log(self, message):
        self.log.append(message)
        self.log = self.log[-7:]
        self.state["log"] = self.log

    def run_cartography_validation_debug(self):
        config = self.game_data.get("config", {})

        if not self.state.get("debug") and not config.get("debug_cartography_validation"):
            return

        issues = validate_cartography_data()

        for issue in issues:
            print("[cartography validation]", format_validation_issue(issue))

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
        draw_placed_objects(self.screen,self.state,camera_x,camera_y)
        draw_occupied_cells_debug(self.screen,self.state,camera_x,camera_y)
        draw_collision_debug(self.screen, camera_x, camera_y)

        self.draw_map()

        if self.hud_visible:
            draw_hud(self)

        if self.menu_open and self.hud_visible:
            draw_menu(self)

        if self.cartography_menu_open:
            draw_cartography_overlay(self)

        if self.combat_manager.is_active():
            self.combat_manager.draw()
        
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

            sprite_path = world_object.get("sprite")

            if sprite_path is None:
                sprite_path = WORLD_OBJECT_SPRITES.get(world_object["type"])

            if sprite_path is not None:
                sprite_size = radius * 2 + 18
                sprite_rect = draw_sprite_centered(
                    self.screen,
                    sprite_path,
                    x,
                    y,
                    sprite_size,
                    sprite_size,
                )

                if selected:
                    pygame.draw.rect(self.screen, WARN, sprite_rect.inflate(8, 8), 2, border_radius=6)
            else:
                self.draw_text(world_object["icon"], x - 6, y - 10, DARK, self.big_font)

            self.draw_text(world_object["name"], x - 34, y + radius + 8, DARK, self.small_font)

            if selected:
                self.draw_text("E", x - 5, y - radius - 28, WARN, self.big_font)

        for collectable in self.state.get("collectables", []):
            x = int(collectable["x"] - camera_x)
            y = int(collectable["y"] - camera_y)

            item_data = get_item_data(collectable["item_id"])

            if item_data is not None:
                draw_item_sprite(
                    self.screen,
                    item_data,
                    pygame.Rect(x - 14, y - 14, 28, 28),
                    padding=0,
                )
        px = int(player["x"] - camera_x)
        py = int(player["y"] - camera_y)

        pygame.draw.circle(self.screen, DARK, (px, py), 13)
        pygame.draw.circle(self.screen, WHITE, (px, py - 18), 9)

        from game.world.grid_manager import TILE_SIZE, world_to_grid, grid_to_world

        foot_x = player["x"]
        foot_y = player["y"] + 6

        foot_grid_x, foot_grid_y = world_to_grid(foot_x, foot_y)
        foot_world_x, foot_world_y = grid_to_world(foot_grid_x, foot_grid_y)

        foot_screen_x = int(foot_world_x - camera_x)
        foot_screen_y = int(foot_world_y - camera_y)

        foot_rect = pygame.Rect(
            foot_screen_x,
            foot_screen_y,
            TILE_SIZE,
            TILE_SIZE,
        )

        pygame.draw.rect(self.screen, (220, 80, 80), foot_rect, 2)

        direction = player.get("direction", "down")

        if direction == "up":
            pygame.draw.circle(self.screen, WARN, (px, py - 18), 4)

        elif direction == "down":
            pygame.draw.circle(self.screen, WARN, (px, py + 18), 4)

        elif direction == "left":
            pygame.draw.circle(self.screen, WARN, (px - 18, py), 4)

        elif direction == "right":
            pygame.draw.circle(self.screen, WARN, (px + 18, py), 4)


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
                draw_item_sprite(self.screen, item_data, preview_rect, padding=3)

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
