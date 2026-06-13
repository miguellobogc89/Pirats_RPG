import sys
import pygame

from game.cartography.ui.cartography_input import handle_cartography_event
from game.hud.menu_overlay import get_menu_tab_at_position, get_menu_tabs
from game.inventory.hotbar_manager import (
    get_active_item_data,
    get_active_item_id,
    get_active_tool,
    set_active_hotbar_index,
)
from game.data.item_database import get_item_data
from game.world.camera import get_camera_position
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.debug.debug_reload import restart_game_with_current_state


def handle_events(app):
    for event in pygame.event.get():
        print("[DEBUG EVENT]", event)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if app.combat_manager.is_active():
            app.combat_manager.handle_event(event)
            continue

        if app.cartography_menu_open:
            handle_cartography_event(app, event)
            continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if app.menu_open:
                    clicked_tab = get_menu_tab_at_position(event.pos[0], event.pos[1])

                    if clicked_tab is not None:
                        app.menu_tab = clicked_tab
                else:
                    handle_game_key(app, pygame.K_e)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F9:
                        restart_game_with_current_state(app.state)
                        return

                    if event.key == pygame.K_ESCAPE:
                        app.menu_open = not app.menu_open

            elif app.menu_open:
                handle_menu_key(app, event.key)

            else:
                handle_game_key(app, event.key)

def handle_menu_key(app, key):
    tabs = get_menu_tabs()

    if app.menu_tab not in tabs:
        app.menu_tab = "inventory"

    current_index = tabs.index(app.menu_tab)

    if key == pygame.K_RIGHT:
        app.menu_tab = tabs[(current_index + 1) % len(tabs)]

    elif key == pygame.K_LEFT:
        app.menu_tab = tabs[(current_index - 1) % len(tabs)]


def handle_game_key(app, key):
    if key == pygame.K_c:
        app.combat_manager.start_test_combat()
        return
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
        set_active_hotbar_index(app.state, index)

        app.placement_mode = False
        app.placement_item_id = None

        item = get_active_item_data(app.state)

        if item is not None and item.get("type") == "placeable":
            app.placement_mode = True
            app.placement_item_id = get_active_item_id(app.state)
        else:
            app.placement_mode = False
            app.placement_item_id = None

        return

    if key == pygame.K_RETURN or key == pygame.K_e:
        handle_interaction_key(app)


def handle_interaction_key(app):
    if app.placement_mode and app.placement_item_id is not None:
        from game.construction.construction_manager import place_object
        from game.inventory.inventory_manager import remove_item
        from game.world.grid_manager import world_to_grid

        item_data = get_item_data(app.placement_item_id)
        footprint = item_data.get("footprint", [1, 1])

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player = app.state["player"]

        camera_x, camera_y = get_camera_position(
            player["x"],
            player["y"],
            app.screen.get_width(),
            app.screen.get_height(),
            WORLD_WIDTH,
            WORLD_HEIGHT,
        )

        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y

        grid_x, grid_y = world_to_grid(world_mouse_x, world_mouse_y)

        placed = place_object(
            app.state,
            app.placement_item_id,
            grid_x,
            grid_y,
            footprint[0],
            footprint[1],
        )

        if not placed:
            return

        removed = remove_item(app.state, app.placement_item_id, 1)

        if removed:
            app.skill_manager.register_action("object_placed")

        app.placement_mode = False
        app.placement_item_id = None
        return

    if app.nearby_object is not None:
        if app.nearby_object["type"] == "bed" or app.nearby_object["type"] == "dock":
            from game.interaction_manager import interact_with_nearby_object
            interact_with_nearby_object(app)
            return

    from game.farming.farming_manager import harvest_crop
    from game.inventory.inventory_manager import add_item

    harvest_result = harvest_crop(
        app.state,
        app.state["player"]["x"],
        app.state["player"]["y"],
    )

    if harvest_result["status"] == "harvested":
        added = add_item(
            app.state,
            harvest_result["item_id"],
            harvest_result["amount"],
        )

        if added:
            app.skill_manager.register_action("crop_harvested")

        return

    if harvest_result["status"] == "removed_dead":
        return

    active_item = get_active_item_data(app.state)
    active_tool = get_active_tool(app.state)

    if active_item is not None and active_item.get("type") == "placeable":
        app.placement_mode = True
        app.placement_item_id = get_active_item_id(app.state)
        return

    if active_tool == "hoe":
        from game.farming.farming_manager import till_cell

        till_cell(
            app.state,
            app.state["player"]["x"],
            app.state["player"]["y"],
        )
        return

    if active_tool == "watering_can":
        from game.farming.farming_manager import water_cell

        water_cell(
            app.state,
            app.state["player"]["x"],
            app.state["player"]["y"],
        )
        return

    if active_item is not None and active_item.get("type") == "seed":
        from game.farming.farming_manager import plant_crop
        from game.inventory.inventory_manager import remove_item

        result = plant_crop(
            app.state,
            app.state["player"]["x"],
            app.state["player"]["y"],
            active_item["crop_id"],
        )

        if result == "not_tilled":
            return

        if result == "occupied":
            return

        active_item_id = get_active_item_id(app.state)
        remove_item(app.state, active_item_id, 1)
        return

    from game.interaction_manager import interact_with_nearby_object
    interact_with_nearby_object(app)
