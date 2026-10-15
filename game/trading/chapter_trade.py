"""Chapter merchant UI and atomic buy/sell transactions."""
import pygame
from game.data.item_database import get_item_data
from game.inventory.inventory_state import ensure_inventory_state
from game.inventory.item_transactions import receive, spend, quantity

SHOPS = {
    "herrero": {"name": "HERRERO", "greeting": "El hierro no espera. ¿Buscas algo o vienes a charlar?", "items": [("iron_ingot", 22), ("copper_ingot", 12), ("iron_ore", 9), ("iron_sword", 95)]},
    "botica": {"name": "BOTICARIA", "greeting": "Tengo remedios para casi todo. ¿Qué necesitas?", "items": [("small_health_potion", 28), ("apple", 6), ("carrot", 5)]},
    "herbolario": {"name": "HERBOLARIO", "greeting": "Cada semilla es una promesa. ¿Quieres ver mi cosecha?", "items": [("corn_seed", 8), ("wheat_seed", 6), ("pumpkin_seed", 13)]},
    "sylvarin": {"name": "SYLVARIN", "greeting": "Bienvenido al taller. ¿Buscas artesanía o una conversación?", "items": [("rope", 11), ("leather", 17), ("wood", 4)]},
}
SELL_FACTOR = 0.5
RECT = pygame.Rect(75, 50, 810, 540)


def available_items(shop_id):
    return [(item, price) for item, price in SHOPS[shop_id]["items"] if get_item_data(item)]


def sell_price(item_id):
    prices = [price for shop in SHOPS.values() for item, price in shop["items"] if item == item_id]
    return max(1, int((prices[0] if prices else 10) * SELL_FACTOR))


def execute(state, action):
    if not action:
        return False, "Selecciona un objeto."
    kind, item_id, amount = action
    if kind == "buy":
        price = next((price for item, price in available_items(amount) if item == item_id), None)
        if price is None:
            return False, "Artículo no disponible."
        gold = state.setdefault("resources", {}).get("gold", 0)
        if gold < price:
            return False, "No tienes suficiente oro."
        if not receive(state, item_id, 1):
            return False, "Inventario lleno."
        state["resources"]["gold"] = gold - price
        return True, "Compra realizada."
    if kind == "sell":
        if quantity(state, item_id) < 1 or not spend(state, item_id, 1):
            return False, "Ya no tienes ese objeto."
        state.setdefault("resources", {})["gold"] = state["resources"].get("gold", 0) + sell_price(item_id)
        return True, "Venta realizada."
    return False, "Operación no válida."


def inventory_stacks(state):
    ensure_inventory_state(state)
    return [(slot["item_id"], slot["amount"]) for row in state["inventory"]["grid"] for slot in row if slot]


def draw(scene):
    app = scene.app
    screen = app.screen
    font, small = app.font, app.small_font
    def text(value, x, y, font=small):
        screen.blit(font.render(str(value), True, (65, 65, 65)), (x, y))
    def frame(rect, fill=(250, 250, 250)):
        pygame.draw.rect(screen, fill, rect)
        pygame.draw.rect(screen, (125, 125, 125), rect, 2)
    frame(RECT)
    shop = SHOPS[scene.shop_id]
    text(shop["name"] + "  |  ORO: " + str(app.state.get("resources", {}).get("gold", 0)), 98, 65, font)
    frame(pygame.Rect(95, 104, 265, 245))  # Portrait intentionally empty.
    frame(pygame.Rect(95, 365, 265, 196))
    scene.shop_hitboxes = []
    for label, y, key in (("ACEPTAR", 402, "accept"), ("SALIR", 479, "exit")):
        rect = pygame.Rect(132, y, 190, 59)
        frame(rect)
        text(label, rect.x + 55, rect.y + 19, font)
        scene.shop_hitboxes.append((rect, key, None))
    text("COMPRAR", 390, 86)
    frame(pygame.Rect(375, 104, 485, 275))
    items = available_items(scene.shop_id)
    for i, (item, price) in enumerate(items[:5]):
        rect = pygame.Rect(387, 114 + i * 51, 461, 46)
        selected = scene.shop_selection == ("buy", item, scene.shop_id)
        frame(rect, (220, 220, 220) if selected else (250, 250, 250))
        data = get_item_data(item)
        text(data.get("icon", "?"), rect.x + 12, rect.y + 12, font)
        text(data["name"], rect.x + 50, rect.y + 13)
        text(str(price) + " oro", rect.right - 105, rect.y + 13)
        scene.shop_hitboxes.append((rect, "buy", item))
    text("VENDER  (clic para seleccionar)", 390, 390)
    frame(pygame.Rect(375, 410, 485, 151))
    for i, (item, count) in enumerate(inventory_stacks(app.state)[scene.shop_page * 8:scene.shop_page * 8 + 8]):
        col, row = i % 4, i // 4
        rect = pygame.Rect(387 + col * 115, 421 + row * 65, 107, 58)
        selected = scene.shop_selection == ("sell", item, None)
        frame(rect, (220, 220, 220) if selected else (250, 250, 250))
        text(get_item_data(item)["name"][:11], rect.x + 5, rect.y + 7)
        text(str(count) + " / " + str(sell_price(item)), rect.x + 5, rect.y + 31)
        scene.shop_hitboxes.append((rect, "sell", item))
    text("Rueda: más objetos | ENTER: aceptar | ESC: salir", 390, 570)


def handle_event(scene, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            scene.shop_id = None
            scene.shop_selection = None
        elif event.key == pygame.K_RETURN:
            confirm(scene)
        return True
    if event.type == pygame.MOUSEWHEEL:
        count = len(inventory_stacks(scene.app.state))
        scene.shop_page = max(0, min(max(0, (count - 1) // 8), scene.shop_page - event.y))
        return True
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for rect, kind, item in scene.shop_hitboxes:
            if not rect.collidepoint(event.pos):
                continue
            if kind == "exit":
                scene.shop_id = None
                scene.shop_selection = None
            elif kind == "accept":
                confirm(scene)
            elif kind == "buy":
                scene.shop_selection = ("buy", item, scene.shop_id)
            elif kind == "sell":
                scene.shop_selection = ("sell", item, None)
            break
        return True
    return True


def confirm(scene):
    success, message = execute(scene.app.state, scene.shop_selection)
    scene.app.add_log(message)
    if success:
        scene.autosave()
        scene.shop_selection = None
