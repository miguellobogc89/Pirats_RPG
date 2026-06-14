import pygame

from core.rules_engine import build_upgrade, continue_and_risk, secure_return, start_trip
from game.inventory.hotbar_manager import get_active_hotbar_index
from game.inventory.inventory_state import INVENTORY_COLUMNS, INVENTORY_ROWS
from game.data.item_database import get_item_data
from game.data.recipe_database import get_all_recipes
from game.crafting.crafting_manager import can_craft, craft_item
from game.skills.skill_database import SKILL_DATABASE
from game.ui.ui_components import (
    TEXT_DARK,
    TEXT_DISABLED,
    draw_button_text,
    draw_content_panel,
    draw_panel,
    draw_progress_bar,
    draw_tab_bar,
    get_tab_rects,
)
from game.ui.slot_renderer import draw_slot


MENU_RECT = pygame.Rect(90, 95, 780, 450)
MENU_CONTENT_RECT = pygame.Rect(120, 166, 720, 318)
TAB_X = 112
TAB_Y = 122


def get_menu_tabs():
    return ["inventory", "routes", "upgrades", "plants", "recipes", "skills", "options"]


def get_menu_tab_at_position(mouse_x, mouse_y):
    tabs = get_menu_tabs()
    labels = get_menu_tab_labels()
    font = pygame.font.SysFont("consolas", 14)
    tab_rects = get_tab_rects(tabs, labels, font, TAB_X, TAB_Y)

    for tab, rect in tab_rects.items():
        if rect.collidepoint(mouse_x, mouse_y):
            return tab

    return None


def get_menu_tab_labels():
    return {
        "inventory": "Invent.",
        "routes": "Rutas",
        "upgrades": "Mejoras",
        "plants": "Plantas",
        "recipes": "Recetas",
        "skills": "Skills",
        "options": "Opciones",
    }


def draw_menu(app):
    overlay = pygame.Surface((app.screen.get_width(), app.screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    app.screen.blit(overlay, (0, 0))

    draw_panel(app.screen, MENU_RECT)

    tabs = get_menu_tabs()
    labels = get_menu_tab_labels()

    draw_tab_bar(
        app.screen,
        tabs,
        labels,
        app.menu_tab,
        app.small_font,
        TAB_X,
        TAB_Y,
    )
    draw_content_panel(app.screen, MENU_CONTENT_RECT, padding=12)
    app.menu_action_hitboxes = []

    if app.menu_tab == "inventory":
        draw_inventory_tab(app)

    elif app.menu_tab == "routes":
        draw_routes_tab(app)

    elif app.menu_tab == "upgrades":
        draw_upgrades_tab(app)

    elif app.menu_tab == "recipes":
        draw_recipes_tab(app)

    elif app.menu_tab == "skills":
        draw_skills_tab(app)

    elif app.menu_tab == "options":
        draw_options_tab(app)

    else:
        app.draw_text("Pendiente de prototipar.", 140, 190, TEXT_DARK)

    app.draw_text("ESC cerrar | LEFT/RIGHT tabs | Click para seleccionar", 130, 510, TEXT_DARK, app.small_font)


def draw_inventory_tab(app):
    inventory = app.state.get("inventory", {})
    grid = inventory.get("grid", [])
    mouse_pos = pygame.mouse.get_pos()
    hovered_slot = None
    app.inventory_slot_hitboxes = []

    active_hotbar_index = get_active_hotbar_index(app.state)
    slot_ui_state = app.slot_ui_state
    rows = INVENTORY_ROWS
    columns = INVENTORY_COLUMNS
    cell_size = 50
    gap = 7
    grid_width = columns * cell_size + (columns - 1) * gap
    x0 = MENU_CONTENT_RECT.x + (MENU_CONTENT_RECT.width - grid_width) // 2
    y0 = 202

    for row_index in range(rows):
        row = []

        if row_index < len(grid):
            row = grid[row_index]

        for column_index in range(columns):
            slot = None

            if column_index < len(row):
                slot = row[column_index]

            x = x0 + column_index * (cell_size + gap)
            y = y0 + row_index * (cell_size + gap)

            slot_rect = pygame.Rect(x, y, cell_size, cell_size)
            hovered = slot_rect.collidepoint(mouse_pos)
            slot_index = row_index * columns + column_index
            slot_hitbox = {
                "rect": slot_rect,
                "row": row_index,
                "column": column_index,
                "index": slot_index,
                "slot": slot,
            }
            app.inventory_slot_hitboxes.append(slot_hitbox)

            if hovered:
                hovered_slot = slot_hitbox

            visible_slot = slot

            if (
                slot_ui_state.is_dragging
                and slot_ui_state.drag_origin is not None
                and slot_ui_state.drag_origin.container_id == "inventory"
                and slot_ui_state.drag_origin.index == slot_index
            ):
                visible_slot = None

            selected = row_index == 0 and column_index == active_hotbar_index
            hotkey_label = None

            if row_index == 0:
                hotkey_label = str(column_index + 1)

            draw_slot(
                app.screen,
                slot_rect,
                visible_slot,
                app.font,
                app.small_font,
                selected=selected,
                hovered=hovered,
                hotkey_label=hotkey_label,
                text_color=TEXT_DARK,
                hotkey_position="top",
            )

    if (
        not slot_ui_state.is_dragging
        and hovered_slot is not None
        and hovered_slot["slot"] is not None
    ):
        draw_inventory_tooltip(app, hovered_slot["slot"], mouse_pos)

    if slot_ui_state.is_dragging and slot_ui_state.dragged_stack is not None:
        draw_dragged_inventory_stack(app, slot_ui_state.dragged_stack, mouse_pos, cell_size)


def draw_inventory_tooltip(app, slot, mouse_pos):
    item_data = get_item_data(slot["item_id"])

    if item_data is None:
        return

    description = item_data.get("description", "Sin descripcion.")
    lines = [
        item_data["name"],
        description,
        f"Cantidad: {slot['amount']}",
        f"Tipo: {item_data.get('type', 'desconocido')}",
        f"ID: {slot['item_id']}",
    ]
    padding = 10
    line_height = 18
    width = max(app.small_font.size(line)[0] for line in lines) + padding * 2
    height = len(lines) * line_height + padding * 2
    tooltip_x = mouse_pos[0] + 14
    tooltip_y = mouse_pos[1] + 14

    if tooltip_x + width > app.screen.get_width():
        tooltip_x = mouse_pos[0] - width - 14

    if tooltip_y + height > app.screen.get_height():
        tooltip_y = mouse_pos[1] - height - 14

    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, width, height)
    draw_panel(app.screen, tooltip_rect)

    text_y = tooltip_rect.y + padding

    for line in lines:
        app.draw_text(line, tooltip_rect.x + padding, text_y, TEXT_DARK, app.small_font)
        text_y += line_height


def draw_dragged_inventory_stack(app, stack, mouse_pos, cell_size):
    drag_rect = pygame.Rect(
        mouse_pos[0] - cell_size // 2,
        mouse_pos[1] - cell_size // 2,
        cell_size,
        cell_size,
    )
    draw_slot(
        app.screen,
        drag_rect,
        stack,
        app.font,
        app.small_font,
        selected=True,
        text_color=TEXT_DARK,
    )


def draw_routes_tab(app):
    y = 186
    ship = app.state["ship"]

    if ship.get("pending_event") == "arrival_decision":
        app.draw_text("Decision de expedicion pendiente:", 140, y, app.WARN)
        app.draw_text("A = asegurar botin | R = arriesgar", 140, y + 30, TEXT_DARK)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            app.add_log(secure_return(app.state, app.game_data))
            app.menu_open = False

        elif keys[pygame.K_r]:
            app.add_log(continue_and_risk(app.state, app.game_data))
            app.menu_open = False

        return

    app.draw_text("Pulsa 1/2/3 para enviar el barco.", 140, y, TEXT_DARK)
    y += 35

    route_keys = list(app.game_data["routes"].keys())
    keys = pygame.key.get_pressed()

    for index, route_key in enumerate(route_keys):
        route = app.game_data["routes"][route_key]

        app.draw_text(
            f"{index + 1}. {route['name']} - {route['duration']} dias - coste {route['cost']}",
            140,
            y,
            TEXT_DARK,
            app.small_font,
        )
        y += 42

        if keys[pygame.K_1 + index]:
            app.add_log(start_trip(app.state, app.game_data, route_key))
            app.menu_open = False


def draw_upgrades_tab(app):
    app.draw_text("Pulsa 1/2/3 para construir mejora.", 140, 186, TEXT_DARK)

    y = 226
    upgrade_keys = list(app.game_data["upgrades"].keys())
    keys = pygame.key.get_pressed()

    for index, upgrade_key in enumerate(upgrade_keys):
        upgrade = app.game_data["upgrades"][upgrade_key]
        owned = app.state["upgrades"].get(upgrade_key, False)

        status = "Pendiente"
        if owned:
            status = "OK"

        app.draw_text(
            f"{index + 1}. {upgrade['name']} - {status} - coste {upgrade['cost']}",
            140,
            y,
            TEXT_DARK,
            app.small_font,
        )
        y += 42

        if keys[pygame.K_1 + index]:
            app.add_log(build_upgrade(app.state, app.game_data, upgrade_key))
            app.menu_open = False


def draw_recipes_tab(app):
    app.draw_text("Pulsa numero para fabricar.", 140, 186, TEXT_DARK)

    recipes = get_all_recipes()
    recipe_keys = list(recipes.keys())
    keys = pygame.key.get_pressed()

    y = 226

    for index, recipe_id in enumerate(recipe_keys):
        recipe = recipes[recipe_id]
        craftable = can_craft(app.state, recipe_id)

        status = "OK"
        if not craftable:
            status = "Faltan recursos"

        app.draw_text(
            f"{index + 1}. {recipe['name']} - {status}",
            140,
            y,
            TEXT_DARK,
            app.small_font,
        )

        ingredient_texts = []

        for item_id, amount in recipe["ingredients"].items():
            item_data = get_item_data(item_id)

            item_name = item_id
            if item_data is not None:
                item_name = item_data["name"]

            ingredient_texts.append(f"{item_name} x{amount}")

        app.draw_text(
            " + ".join(ingredient_texts),
            170,
            y + 20,
            TEXT_DARK,
            app.small_font,
        )

        if keys[pygame.K_1 + index]:
            result = craft_item(
                app.state,
                recipe_id,
                app.skill_manager,
            )

            if result["status"] == "crafted":
                app.add_log(f"Fabricado: {recipe['name']}")

                skill_result = result["skill_result"]

                if skill_result is not None:
                    app.add_log("Artesanía +10 XP")

                    if skill_result["leveled_up"]:
                        app.add_log(f"Artesanía sube a nivel {skill_result['level']}.")
            else:
                app.add_log("No tienes recursos suficientes.")

        y += 58


def draw_skills_tab(app):
    app.draw_text("Habilidades", 140, 186, TEXT_DARK, app.big_font)

    y = 232

    for skill_id, skill_data in SKILL_DATABASE.items():
        skill_state = app.skill_manager.get_skill_state(skill_id)

        if skill_state is None:
            continue

        level = skill_state.get("level", 1)
        xp = skill_state.get("xp", 0)
        total_xp = skill_state.get("total_xp", 0)

        xp_required = app.skill_manager.get_xp_required_for_next_level(level)

        percent = 0
        if xp_required > 0:
            percent = int((xp / xp_required) * 100)

        app.draw_text(
            f"{skill_data['name']} | Nivel {level} | XP {xp}/{xp_required} | Total {total_xp} | {percent}%",
            140,
            y,
            TEXT_DARK,
            app.small_font,
        )

        bar_x = 140
        bar_y = y + 22
        bar_width = 280
        bar_height = 12

        draw_progress_bar(
            app.screen,
            pygame.Rect(bar_x, bar_y, bar_width, bar_height),
            percent,
            100,
            app.WARN,
            background_color=(70, 48, 34),
            border_color=WOOD_DARK,
        )

        y += 48


def draw_options_tab(app):
    app.draw_text("Opciones", 140, 186, TEXT_DARK, app.big_font)
    app.draw_text("Ajustes proximamente.", 140, 226, TEXT_DARK, app.small_font)

    button_rect = pygame.Rect(140, 278, 230, 42)
    draw_panel(app.screen, button_rect)
    draw_button_text(app.screen, app.font, "Salir al menu principal", button_rect, enabled=True)

    app.menu_action_hitboxes.append({
        "rect": button_rect,
        "action": "return_to_main_menu",
    })
