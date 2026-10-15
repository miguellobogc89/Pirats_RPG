import sys
import pygame

from game.cartography.ui.cartography_input import handle_cartography_event
from game.dialogue import handle_dialogue_event, is_dialogue_active
from game.hud.menu_overlay import get_menu_tab_at_position, get_menu_tabs
from game.inventory.hotbar_manager import (
    get_active_item_data,
    get_active_item_id,
    get_active_tool,
    get_active_hotbar_index,
    set_active_hotbar_index,
)
from game.inventory.inventory_state import INVENTORY_COLUMNS, INVENTORY_ROWS
from game.inventory.stash_state import STASH_COLUMNS, STASH_ROWS, ensure_stash_state
from game.inventory.slot_ui_state import SlotReference, copy_stack
from game.inventory.slot_operations import merge_stacks
from game.data.item_database import get_item_data
from game.world.camera import get_camera_position
from game.world.world_config import WORLD_WIDTH, WORLD_HEIGHT
from game.debug.debug_reload import restart_game_with_current_state


NUMBER_KEYS = [
    pygame.K_1,
    pygame.K_2,
    pygame.K_3,
    pygame.K_4,
    pygame.K_5,
    pygame.K_6,
    pygame.K_7,
    pygame.K_8,
]


def handle_events(app):
    for event in pygame.event.get():
        handle_event(app, event)


def handle_event(app, event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F9:
            if not prepare_slot_drag_for_persistent_action(app, "reiniciar"):
                return True

            restart_game_with_current_state(app.state)
            return True

    if is_dialogue_active(app):
        return handle_dialogue_event(app, event)

    if app.combat_manager.is_active():
        app.combat_manager.handle_event(event)
        return True

    if app.cartography_menu_open:
        return handle_cartography_event(app, event)

    if app.stash_open:
        handle_stash_event(app, event)
        return True

    if event.type == pygame.MOUSEWHEEL and app.menu_open and app.menu_tab == "journal":
        from game.hud.menu_overlay import journal_visible_missions, journal_objectives
        category = getattr(app, "mission_category", "main")
        expanded = getattr(app, "mission_expanded", None)
        height = sum(45 + (len(journal_objectives(m["id"])) * 25 + 8 if expanded == m["id"] else 0) for m in journal_visible_missions(app, category))
        app.mission_scroll = max(0, min(max(0, height - 155), getattr(app, "mission_scroll", 0) - event.y * 35))
        return True

    if event.type == pygame.MOUSEWHEEL and app.menu_open and app.menu_tab == "recipes":
        from game.hud.recipe_catalogue import scroll_recipes
        scroll_recipes(app, event.y)
        return True

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            if app.menu_open:
                if app.menu_tab == "recipes":
                    from game.hud.recipe_catalogue import click_recipe
                    if click_recipe(app, event.pos):
                        return True
                if handle_menu_action_click(app, event.pos):
                    return True

                if app.menu_tab == "inventory":
                    if handle_equipment_slot_click(app, event.pos):
                        return True
                    if handle_inventory_slot_click(app, event.pos):
                        return True

                    if app.slot_ui_state.is_dragging:
                        if not cancel_inventory_drag(app):
                            app.add_log("Coloca el item en una casilla libre.")
                        return True

                clicked_tab = get_menu_tab_at_position(event.pos[0], event.pos[1])

                if clicked_tab is not None:
                    app.menu_tab = clicked_tab
                    return True
            else:
                if app.placement_mode:
                    from game.construction.placement_mode import place_at_mouse
                    place_at_mouse(app, event.pos)
                elif get_active_tool(app.state) == "hoe" and try_remove_placed_with_hoe(app, event.pos):
                    pass
                else:
                    handle_game_key(app, pygame.K_e)
                return True

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            if app.placement_mode and not app.menu_open:
                from game.construction.placement_mode import stop_placement
                stop_placement(app)
                return True
            if app.menu_open and app.slot_ui_state.is_dragging:
                if not cancel_inventory_drag(app):
                    app.add_log("Coloca el item antes de cerrar el inventario.")
                return True

            app.menu_open = not app.menu_open
            return True

        if app.menu_open:
            handle_menu_key(app, event.key)
            return True

        handle_game_key(app, event.key)
        return True

    return False


def handle_menu_action_click(app, pos):
    for hitbox in getattr(app, "menu_action_hitboxes", []):
        if not hitbox["rect"].collidepoint(pos):
            continue

        action = hitbox.get("action")

        if action == "mission_category":
            app.mission_category = hitbox["category"]
            app.mission_selected = None
            app.mission_scroll = 0
            return True
        if action == "mission_expand":
            mission_id = hitbox["mission_id"]
            app.mission_expanded = None if getattr(app, "mission_expanded", None) == mission_id else mission_id
            app.mission_selected = mission_id
            app.mission_scroll = 0
            return True
        if action == "mission_select":
            app.mission_selected = hitbox["mission_id"]
            return True
        if action == "mission_replay":
            from game.story.mission_replay import replay_mission
            replay_mission(app, hitbox["mission_id"])
            return True

        if action == "return_to_main_menu":
            app.return_to_main_menu()
            return True

    return False


def handle_menu_key(app, key):
    if app.slot_ui_state.is_dragging:
        return

    if key == pygame.K_TAB:
        cycle_active_hotbar_slot(app)
        return

    if key in NUMBER_KEYS:
        select_active_hotbar_slot(app, NUMBER_KEYS.index(key))
        return

    tabs = get_menu_tabs()

    if app.menu_tab not in tabs:
        app.menu_tab = "inventory"

    current_index = tabs.index(app.menu_tab)

    if key == pygame.K_RIGHT:
        app.menu_tab = tabs[(current_index + 1) % len(tabs)]

    elif key == pygame.K_LEFT:
        app.menu_tab = tabs[(current_index - 1) % len(tabs)]


def handle_stash_event(app, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            if app.slot_ui_state.is_dragging:
                if not cancel_slot_drag(app):
                    app.add_log("Coloca el item antes de cerrar el cofre.")
                return

            from core.save_manager import save_state
            save_state(app.state)
            app.slot_ui_state.clear()
            app.stash_open = False
            return

        if event.key == pygame.K_TAB:
            cycle_active_hotbar_slot(app)
            return

        if event.key in NUMBER_KEYS:
            select_active_hotbar_slot(app, NUMBER_KEYS.index(event.key))

        return

    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return

    if handle_stash_slot_click(app, event.pos):
        return

    if app.slot_ui_state.is_dragging:
        if not cancel_slot_drag(app):
            app.add_log("Coloca el item en una casilla libre.")


def handle_stash_slot_click(app, position):
    slot_hitbox = get_slot_hitbox_at_position(app, position)

    if slot_hitbox is None:
        return False

    return handle_container_slot_click(app, slot_hitbox)


def get_slot_hitbox_at_position(app, position):
    for slot_hitbox in getattr(app, "stash_slot_hitboxes", []):
        if slot_hitbox["rect"].collidepoint(position):
            return slot_hitbox

    for slot_hitbox in getattr(app, "inventory_slot_hitboxes", []):
        if slot_hitbox["rect"].collidepoint(position):
            return slot_hitbox

    return None


def handle_container_slot_click(app, slot_hitbox):
    slot_ui_state = app.slot_ui_state
    grid = get_slot_container_grid(app, slot_hitbox["container_id"])
    columns = get_slot_container_columns(slot_hitbox["container_id"])
    row = slot_hitbox["row"]
    column = slot_hitbox["column"]
    ensure_grid_position(grid, row, column)
    slot_stack = grid[row][column]

    if not slot_ui_state.is_dragging:
        if is_inventory_hotbar_slot(slot_hitbox):
            active_index = get_active_hotbar_index(app.state)
            select_active_hotbar_slot(app, column)

            if column != active_index:
                return True

        if slot_stack is None:
            return True

        slot_ui_state.selected_slot = SlotReference(
            slot_hitbox["container_id"],
            slot_hitbox["index"],
        )
        slot_ui_state.start_drag(
            SlotReference(slot_hitbox["container_id"], slot_hitbox["index"]),
            slot_stack,
        )
        grid[row][column] = None
        return True

    dragged_stack = copy_stack(slot_ui_state.dragged_stack)

    if slot_stack is None:
        grid[row][column] = dragged_stack
        select_hotbar_if_target_is_hotbar(app, slot_hitbox)
        slot_ui_state.selected_slot = SlotReference(
            slot_hitbox["container_id"],
            slot_hitbox["index"],
        )
        slot_ui_state.cancel_drag()
        return True

    if dragged_stack["item_id"] == slot_stack["item_id"]:
        merge_result = merge_stacks(dragged_stack, slot_stack)

        if merge_result["success"]:
            grid[row][column] = merge_result["target_stack"]
            select_hotbar_if_target_is_hotbar(app, slot_hitbox)
            slot_ui_state.selected_slot = SlotReference(
                slot_hitbox["container_id"],
                slot_hitbox["index"],
            )

            if merge_result["source_stack"] is None:
                slot_ui_state.cancel_drag()
            else:
                slot_ui_state.dragged_stack = copy_stack(merge_result["source_stack"])
                slot_ui_state.is_dragging = True

            return True

    grid[row][column] = dragged_stack
    select_hotbar_if_target_is_hotbar(app, slot_hitbox)
    slot_ui_state.dragged_stack = copy_stack(slot_stack)
    slot_ui_state.selected_slot = SlotReference(
        slot_hitbox["container_id"],
        slot_hitbox["index"],
    )
    slot_ui_state.is_dragging = True
    return True


def get_slot_container_grid(app, container_id):
    if container_id == "stash":
        ensure_stash_state(app.state)
        return app.state["stash"]["grid"]

    return app.state["inventory"]["grid"]


def get_slot_container_columns(container_id):
    if container_id == "stash":
        return STASH_COLUMNS

    return INVENTORY_COLUMNS


def get_slot_container_rows(container_id):
    if container_id == "stash":
        return STASH_ROWS

    return INVENTORY_ROWS



def handle_equipment_slot_click(app, position):
    from game.inventory.equipment_state import ensure_equipment_state, armor_slot, EQUIPMENT_SLOTS
    equipment = ensure_equipment_state(app.state)
    for hitbox in getattr(app, "equipment_slot_hitboxes", []):
        if not hitbox["rect"].collidepoint(position):
            continue
        name = hitbox["slot"]
        existing = equipment[name]
        ui = app.slot_ui_state
        if not ui.is_dragging:
            if existing is not None:
                ui.start_drag(SlotReference("equipment", EQUIPMENT_SLOTS.index(name)), existing)
                equipment[name] = None
            return True
        dragged = copy_stack(ui.dragged_stack)
        if armor_slot(dragged["item_id"]) != name:
            app.add_log("Esta pieza no encaja en esa casilla.")
            return True
        equipment[name] = dragged
        if existing is None:
            ui.cancel_drag()
        else:
            ui.dragged_stack = copy_stack(existing)
            ui.is_dragging = True
        return True
    return False

def handle_inventory_slot_click(app, position):
    slot_hitbox = get_inventory_slot_hitbox_at_position(app, position)

    if slot_hitbox is None:
        return False

    slot_ui_state = app.slot_ui_state
    grid = app.state["inventory"]["grid"]
    row = slot_hitbox["row"]
    column = slot_hitbox["column"]
    ensure_inventory_grid_position(grid, row, column)
    slot_stack = grid[row][column]

    if not slot_ui_state.is_dragging:
        if row == 0:
            active_index = get_active_hotbar_index(app.state)
            select_active_hotbar_slot(app, column)

            if column != active_index:
                return True

        if slot_stack is None:
            return True

        slot_ui_state.selected_slot = SlotReference("inventory", slot_hitbox["index"])
        slot_ui_state.start_drag(
            SlotReference("inventory", slot_hitbox["index"]),
            slot_stack,
        )
        grid[row][column] = None
        return True

    dragged_stack = copy_stack(slot_ui_state.dragged_stack)

    if slot_stack is None:
        grid[row][column] = dragged_stack
        if row == 0:
            select_active_hotbar_slot(app, column)
        slot_ui_state.selected_slot = SlotReference("inventory", slot_hitbox["index"])
        slot_ui_state.cancel_drag()
        return True

    if dragged_stack["item_id"] == slot_stack["item_id"]:
        merge_result = merge_stacks(dragged_stack, slot_stack)

        if merge_result["success"]:
            grid[row][column] = merge_result["target_stack"]
            if row == 0:
                select_active_hotbar_slot(app, column)
            slot_ui_state.selected_slot = SlotReference("inventory", slot_hitbox["index"])

            if merge_result["source_stack"] is None:
                slot_ui_state.cancel_drag()
            else:
                slot_ui_state.dragged_stack = copy_stack(merge_result["source_stack"])
                slot_ui_state.is_dragging = True

            return True

    grid[row][column] = dragged_stack
    if row == 0:
        select_active_hotbar_slot(app, column)
    slot_ui_state.dragged_stack = copy_stack(slot_stack)
    slot_ui_state.selected_slot = SlotReference("inventory", slot_hitbox["index"])
    slot_ui_state.is_dragging = True
    return True


def get_inventory_slot_hitbox_at_position(app, position):
    for slot_hitbox in getattr(app, "inventory_slot_hitboxes", []):
        if slot_hitbox["rect"].collidepoint(position):
            return slot_hitbox

    return None


def cancel_inventory_drag(app):
    return cancel_slot_drag(app)


def cancel_slot_drag(app):
    slot_ui_state = app.slot_ui_state

    if not slot_ui_state.is_dragging or slot_ui_state.dragged_stack is None:
        slot_ui_state.cancel_drag()
        return True

    if slot_ui_state.drag_origin is None:
        return False

    if slot_ui_state.drag_origin.container_id == "equipment":
        from game.inventory.equipment_state import ensure_equipment_state, EQUIPMENT_SLOTS
        equipment = ensure_equipment_state(app.state)
        name = EQUIPMENT_SLOTS[slot_ui_state.drag_origin.index]
        if equipment[name] is not None:
            return False
        equipment[name] = copy_stack(slot_ui_state.dragged_stack)
        slot_ui_state.cancel_drag()
        return True

    if slot_ui_state.drag_origin.container_id not in ("inventory", "stash"):
        return False

    container_id = slot_ui_state.drag_origin.container_id
    grid = get_slot_container_grid(app, container_id)
    columns = get_slot_container_columns(container_id)
    rows = get_slot_container_rows(container_id)
    row = slot_ui_state.drag_origin.index // columns
    column = slot_ui_state.drag_origin.index % columns

    if row < 0 or row >= rows:
        return False

    ensure_grid_position(grid, row, column)

    if grid[row][column] is not None:
        return False

    grid[row][column] = copy_stack(slot_ui_state.dragged_stack)
    slot_ui_state.cancel_drag()
    return True


def prepare_slot_drag_for_persistent_action(app, action_name):
    if not app.slot_ui_state.is_dragging:
        return True

    if cancel_slot_drag(app):
        return True

    app.add_log(
        f"No se puede {action_name}: coloca el item en una casilla libre primero."
    )
    return False


def ensure_inventory_grid_position(grid, row, column):
    ensure_grid_position(grid, row, column)


def ensure_grid_position(grid, row, column):
    while len(grid) <= row:
        grid.append([])

    while len(grid[row]) <= column:
        grid[row].append(None)


def is_inventory_hotbar_slot(slot_hitbox):
    return (
        slot_hitbox["container_id"] == "inventory"
        and slot_hitbox["row"] == 0
    )


def select_hotbar_if_target_is_hotbar(app, slot_hitbox):
    if is_inventory_hotbar_slot(slot_hitbox):
        select_active_hotbar_slot(app, slot_hitbox["column"])


def cycle_active_hotbar_slot(app):
    current_index = get_active_hotbar_index(app.state)
    select_active_hotbar_slot(app, (current_index + 1) % INVENTORY_COLUMNS)


def select_active_hotbar_slot(app, index):
    if not set_active_hotbar_index(app.state, index):
        return False

    app.placement_mode = False
    app.placement_item_id = None

    item = get_active_item_data(app.state)

    if item is not None and item.get("type") == "placeable":
        app.placement_mode = True
        app.placement_item_id = get_active_item_id(app.state)

    return True


def handle_game_key(app, key):
    if key == pygame.K_h:
        change_app_scene(app, "player_house")
        return

    if key == pygame.K_g:
        change_app_scene(app, "farm")
        return
    if key == pygame.K_c:
        app.combat_manager.start_test_combat()
        return
    if key == pygame.K_TAB:
        cycle_active_hotbar_slot(app)
        return

    if key in NUMBER_KEYS:
        index = NUMBER_KEYS.index(key)
        select_active_hotbar_slot(app, index)

        return

    if key == pygame.K_RETURN or key == pygame.K_e:
        handle_interaction_key(app)


def handle_interaction_key(app):
    if app.placement_mode:
        from game.construction.placement_mode import place_at_mouse
        place_at_mouse(app, pygame.mouse.get_pos())
        return

    if app.nearby_object is not None:
        if app.nearby_object["type"] in ("bed", "dock", "stash"):
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


def change_app_scene(app, scene_id, payload=None):
    scene_manager = getattr(app, "scene_manager", None)

    if scene_manager is not None:
        scene_manager.change_scene(scene_id, payload=payload)
        return

    from game.scenes.scene_manager import change_scene

    change_scene(app.state, scene_id, payload=payload)


def try_remove_placed_with_hoe(app, mouse_pos):
    """Remove an adjacent placed item with the hoe; allow own cell to recover traps."""
    from game.world.grid_manager import world_to_grid
    from game.construction.construction_manager import remove_placed_object
    player = app.state["player"]
    camera_x, camera_y = get_camera_position(
        player["x"], player["y"], app.screen.get_width(), app.screen.get_height(),
        app.get_scene_world_width(), app.get_scene_world_height())
    gx, gy = world_to_grid(mouse_pos[0] + camera_x, mouse_pos[1] + camera_y)
    px, py = world_to_grid(player["x"], player["y"] + 6)
    if abs(gx - px) + abs(gy - py) > 1:
        return False
    result = remove_placed_object(app.state, gx, gy)
    if result == "removed":
        app.add_log("Objeto recuperado con la azada.")
        return True
    if result == "inventory_full":
        app.add_log("Inventario lleno: libera un hueco para recogerlo.")
        return True
    return False
