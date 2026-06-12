import pygame

from core.rules_engine import build_upgrade, continue_and_risk, secure_return, start_trip
from game.inventory.hotbar_manager import get_active_item_data
from game.data.item_database import get_item_data
from game.data.recipe_database import get_all_recipes
from game.crafting.crafting_manager import can_craft, craft_item


def draw_menu(app):
    overlay = pygame.Surface((app.screen.get_width(), app.screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    app.screen.blit(overlay, (0, 0))

    pygame.draw.rect(app.screen, app.PANEL, (90, 95, 780, 450), border_radius=10)
    pygame.draw.rect(app.screen, app.DARK, (90, 95, 780, 450), 3, border_radius=10)

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

        color = (220, 210, 180)
        if tab == app.menu_tab:
            color = app.WHITE

        pygame.draw.rect(app.screen, color, (x, 115, 105, 34), border_radius=5)
        pygame.draw.rect(app.screen, app.DARK, (x, 115, 105, 34), 2, border_radius=5)

        app.draw_text(labels[tab], x + 8, 124, app.DARK, app.small_font)

    if app.menu_tab == "inventory":
        draw_inventory_tab(app)

    elif app.menu_tab == "routes":
        draw_routes_tab(app)

    elif app.menu_tab == "upgrades":
        draw_upgrades_tab(app)

    elif app.menu_tab == "recipes":
        draw_recipes_tab(app)

    else:
        app.draw_text("Pendiente de prototipar.", 130, 190, app.DARK)

    app.draw_text("ESC cerrar | LEFT/RIGHT tabs", 130, 510, app.DARK, app.small_font)


def draw_inventory_tab(app):
    inventory = app.state.get("inventory", {})
    grid = inventory.get("grid", [])

    x0 = 130
    y0 = 185
    cell_size = 58
    gap = 10

    for row_index, row in enumerate(grid):
        for column_index, slot in enumerate(row):
            x = x0 + column_index * (cell_size + gap)
            y = y0 + row_index * (cell_size + gap)

            pygame.draw.rect(app.screen, app.WHITE, (x, y, cell_size, cell_size), border_radius=6)
            pygame.draw.rect(app.screen, app.DARK, (x, y, cell_size, cell_size), 2, border_radius=6)

            if slot is None:
                continue

            item_id = slot["item_id"]
            amount = slot["amount"]

            item = get_item_data(item_id)

            if item is None:
                continue

            app.draw_text(item["icon"], x + 22, y + 10, app.DARK, app.big_font)

            if amount > 1:
                app.draw_text(str(amount), x + 38, y + 38, app.DARK, app.small_font)

    app.draw_text("Fila superior = hotbar", x0, y0 + 150, app.DARK, app.small_font)


def draw_routes_tab(app):
    y = 180
    ship = app.state["ship"]

    if ship.get("pending_event") == "arrival_decision":
        app.draw_text("Decision de expedicion pendiente:", 130, y, app.WARN)
        app.draw_text("A = asegurar botin | R = arriesgar", 130, y + 30, app.DARK)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            app.add_log(secure_return(app.state, app.game_data))
            app.menu_open = False

        elif keys[pygame.K_r]:
            app.add_log(continue_and_risk(app.state, app.game_data))
            app.menu_open = False

        return

    app.draw_text("Pulsa 1/2/3 para enviar el barco.", 130, y, app.DARK)
    y += 35

    route_keys = list(app.game_data["routes"].keys())
    keys = pygame.key.get_pressed()

    for index, route_key in enumerate(route_keys):
        route = app.game_data["routes"][route_key]

        app.draw_text(
            f"{index + 1}. {route['name']} - {route['duration']} dias - coste {route['cost']}",
            130,
            y,
            app.DARK,
            app.small_font,
        )
        y += 42

        if keys[pygame.K_1 + index]:
            app.add_log(start_trip(app.state, app.game_data, route_key))
            app.menu_open = False


def draw_upgrades_tab(app):
    app.draw_text("Pulsa 1/2/3 para construir mejora.", 130, 180, app.DARK)

    y = 220
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
            130,
            y,
            app.DARK,
            app.small_font,
        )
        y += 42

        if keys[pygame.K_1 + index]:
            app.add_log(build_upgrade(app.state, app.game_data, upgrade_key))
            app.menu_open = False

def draw_recipes_tab(app):
            app.draw_text("Pulsa 1 para fabricar.", 130, 180, app.DARK)

            recipes = get_all_recipes()
            recipe_keys = list(recipes.keys())
            keys = pygame.key.get_pressed()

            y = 220

            for index, recipe_id in enumerate(recipe_keys):
                recipe = recipes[recipe_id]
                craftable = can_craft(app.state, recipe_id)

                status = "OK"
                if not craftable:
                    status = "Faltan recursos"

                app.draw_text(
                    f"{index + 1}. {recipe['name']} - {status}",
                    130,
                    y,
                    app.DARK,
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
                    160,
                    y + 20,
                    app.DARK,
                    app.small_font,
                )

                if keys[pygame.K_1 + index]:
                    result = craft_item(app.state, recipe_id)

                    if result == "crafted":
                        app.add_log(f"Fabricado: {recipe['name']}")
                    else:
                        app.add_log("No tienes recursos suficientes.")

                y += 58