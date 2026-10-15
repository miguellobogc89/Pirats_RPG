"""Clickable recipe catalogue, isolated from crafting and inventory rules."""
import math
import pygame

from game.data.recipe_database import get_all_recipes
from game.data.item_database import get_item_data
from game.crafting.crafting_manager import check_craft, craft_item
from game.inventory.item_transactions import quantity
from game.ui.slot_renderer import draw_slot
from game.ui.sprite_renderer import draw_item_sprite
from game.ui.ui_components import TEXT_DARK

GRID = pygame.Rect(145, 201, 260, 254)
DETAIL = pygame.Rect(429, 190, 390, 279)
CELL = 53
GAP = 9
COLS = 4
ROW_HEIGHT = CELL + GAP


def recipe_ids():
    return list(get_all_recipes())


def selected_recipe(app):
    ids = recipe_ids()
    selected = getattr(app, "selected_recipe_id", None)
    if selected not in ids:
        selected = ids[0] if ids else None
        app.selected_recipe_id = selected
    return selected


def scroll_recipes(app, direction):
    rows = math.ceil(len(recipe_ids()) / COLS)
    max_scroll = max(0, rows * ROW_HEIGHT - GRID.height)
    app.recipe_scroll = max(0, min(max_scroll, getattr(app, "recipe_scroll", 0) - direction * ROW_HEIGHT))


def draw_recipes(app):
    recipes = get_all_recipes()
    selected = selected_recipe(app)
    app.draw_text("RECETAS", GRID.x, 180, TEXT_DARK, app.small_font)
    app.draw_text("DETALLES", DETAIL.x, 180, TEXT_DARK, app.small_font)
    app.recipe_hitboxes = []
    scroll = getattr(app, "recipe_scroll", 0)
    screen = app.screen
    previous_clip = screen.get_clip()
    screen.set_clip(GRID)
    for i, recipe_id in enumerate(recipes):
        x = GRID.x + (i % COLS) * ROW_HEIGHT
        y = GRID.y + (i // COLS) * ROW_HEIGHT - scroll
        rect = pygame.Rect(x, y, CELL, CELL)
        if not rect.colliderect(GRID):
            continue
        item_id = recipes[recipe_id]["result_item"]
        draw_slot(screen, rect, {"item_id": item_id, "amount": 1}, app.font, app.small_font,
                  selected=recipe_id == selected, hovered=rect.collidepoint(pygame.mouse.get_pos()),
                  disabled=check_craft(app.state, recipe_id) != "ready", text_color=TEXT_DARK)
        app.recipe_hitboxes.append({"rect": rect.clip(GRID), "recipe_id": recipe_id})
    screen.set_clip(previous_clip)
    if len(recipes) > COLS * 4:
        app.draw_text("Rueda para desplazarte", GRID.x, 462, TEXT_DARK, app.small_font)
    if selected is None:
        app.draw_text("No hay recetas.", DETAIL.x, 235, TEXT_DARK, app.small_font)
        return
    recipe = recipes[selected]
    item = get_item_data(recipe["result_item"]) or {}
    app.draw_text(recipe["name"], DETAIL.x, 198, TEXT_DARK, app.font)
    preview = pygame.Rect(DETAIL.x + 126, 223, 110, 85)
    pygame.draw.rect(screen, (215, 204, 177), preview, border_radius=5)
    if draw_item_sprite(screen, item, preview, padding=9) is None:
        symbol = app.big_font.render(item.get("icon", "?"), True, TEXT_DARK)
        screen.blit(symbol, symbol.get_rect(center=preview.center))
    description = item.get("description") or recipe.get("description") or "Objeto fabricable."
    # Wrap to the detail panel width.
    words = description.split()
    lines, line = [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if app.small_font.size(candidate)[0] > DETAIL.width - 14 and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    for index, text in enumerate(lines[:2]):
        app.draw_text(text, DETAIL.x, 316 + index * 19, TEXT_DARK, app.small_font)
    app.draw_text("Materiales:", DETAIL.x, 355, TEXT_DARK, app.small_font)
    for index, (item_id, amount) in enumerate(recipe["ingredients"].items()):
        data = get_item_data(item_id) or {}
        have = quantity(app.state, item_id)
        color = TEXT_DARK if have >= amount else (155, 66, 52)
        app.draw_text(f"{data.get('name', item_id)}: {have}/{amount}", DETAIL.x + (index % 2) * 187,
                      379 + (index // 2) * 21, color, app.small_font)
    status = check_craft(app.state, selected)
    button = pygame.Rect(DETAIL.x, 422, 175, 38)
    enabled = status == "ready"
    pygame.draw.rect(screen, (89, 111, 77) if enabled else (149, 145, 130), button, border_radius=5)
    label = app.font.render("Fabricar", True, (255, 255, 245))
    screen.blit(label, label.get_rect(center=button.center))
    app.recipe_craft_rect = button
    if not enabled:
        messages = {"missing_resources": "Faltan materiales", "inventory_full": "Inventario lleno",
                    "missing_station": "Falta estacion", "missing_skill": "Falta habilidad"}
        app.draw_text(messages.get(status, status), DETAIL.x + 186, 433, TEXT_DARK, app.small_font)


def click_recipe(app, pos):
    for hitbox in getattr(app, "recipe_hitboxes", []):
        if hitbox["rect"].collidepoint(pos):
            app.selected_recipe_id = hitbox["recipe_id"]
            return True
    if getattr(app, "recipe_craft_rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
        recipe_id = selected_recipe(app)
        if recipe_id:
            result = craft_item(app.state, recipe_id, app.skill_manager)
            if result["status"] == "crafted":
                app.add_log("Fabricado: " + get_all_recipes()[recipe_id]["name"])
                skill = result.get("skill_result")
                if skill and skill.get("leveled_up"):
                    app.add_log("Artesania sube a nivel " + str(skill["level"]))
            else:
                app.add_log("No se puede fabricar: " + result["status"])
        return True
    return False
