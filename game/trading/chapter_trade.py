"""Chapter merchant UI and atomic buy/sell transactions."""
import pygame
from game.data.item_database import get_item_data
from game.inventory.inventory_state import ensure_inventory_state
from game.inventory.item_transactions import receive, spend, quantity
from game.inventory.inventory_manager import can_add_item
from game.ui.sprite_renderer import draw_item_sprite

SHOPS = {
    "herrero": {"name": "HERRERO", "greeting": "El hierro no espera. ¿Buscas algo o vienes a charlar?", "items": [("iron_ingot", 22), ("copper_ingot", 12), ("iron_ore", 9), ("iron_sword", 95)]},
    "botica": {"name": "BOTICARIA", "greeting": "Tengo remedios para casi todo. ¿Qué necesitas?", "items": [("small_health_potion", 28), ("apple", 6), ("carrot", 5)]},
    "herbolario": {"name": "HERBOLARIO", "greeting": "Cada semilla es una promesa. ¿Quieres ver mi cosecha?", "items": [("corn_seed", 8), ("wheat_seed", 6), ("pumpkin_seed", 13)]},
    "sylvarin": {"name": "SYLVARIN", "greeting": "Bienvenido al taller. ¿Buscas artesanía o una conversación?", "items": [("rope", 11), ("leather", 17), ("wood", 4)]},
}
SELL_FACTOR = 0.5
SELL_PRICE_OVERRIDES = {"corn": 25}
RECT = pygame.Rect(75, 50, 810, 540)


def available_items(shop_id):
    return [(item, price) for item, price in SHOPS[shop_id]["items"] if get_item_data(item)]


def sell_price(item_id):
    if item_id in SELL_PRICE_OVERRIDES:
        return SELL_PRICE_OVERRIDES[item_id]
    prices = [price for shop in SHOPS.values() for item, price in shop["items"] if item == item_id]
    return max(1, int((prices[0] if prices else 10) * SELL_FACTOR))


def execute(state, action, count=1):
    """Commit one validated bulk trade without partial inventory or gold changes."""
    if not action or not isinstance(count, int) or count < 1:
        return False, "Selecciona una cantidad válida."
    kind, item_id, shop_id = action
    if kind == "buy":
        price = next((price for item, price in available_items(shop_id) if item == item_id), None)
        if price is None:
            return False, "Artículo no disponible."
        total = price * count
        resources = state.setdefault("resources", {})
        if resources.get("gold", 0) < total:
            return False, "No tienes suficiente oro."
        if not can_add_item(state, item_id, count):
            return False, "No hay espacio suficiente en el inventario."
        if not receive(state, item_id, count):
            return False, "No se pudo completar la compra."
        resources["gold"] -= total
        return True, "Compra realizada."
    if kind == "sell":
        if quantity(state, item_id) < count:
            return False, "No tienes esa cantidad de objetos."
        if not spend(state, item_id, count):
            return False, "No se pudo completar la venta."
        resources = state.setdefault("resources", {})
        resources["gold"] = resources.get("gold", 0) + sell_price(item_id) * count
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
        if draw_item_sprite(screen, data, pygame.Rect(rect.x + 7, rect.y + 5, 35, 35), padding=2) is None:
            text(data.get("icon", "?"), rect.x + 12, rect.y + 12, font)
        text(data["name"], rect.x + 50, rect.y + 13)
        text(str(price) + " oro", rect.right - 105, rect.y + 13)
        scene.shop_hitboxes.append((rect, "buy", item))
    text("VENDER  (clic para seleccionar)", 390, 390)
    frame(pygame.Rect(375, 410, 485, 151))
    for i, (item, count) in enumerate(inventory_stacks(app.state)[scene.shop_page * 14:scene.shop_page * 14 + 14]):
        col, row = i % 7, i // 7
        rect = pygame.Rect(385 + col * 67, 421 + row * 65, 62, 58)
        selected = scene.shop_selection == ("sell", item, None)
        frame(rect, (220, 220, 220) if selected else (250, 250, 250))
        data = get_item_data(item)
        if draw_item_sprite(screen, data, pygame.Rect(rect.x + 4, rect.y + 3, 29, 29), padding=1) is None:
            text(data.get("icon", "?"), rect.x + 8, rect.y + 7)
        text(data["name"][:8], rect.x + 4, rect.y + 34)
        text(str(count) + "/" + str(sell_price(item)), rect.x + 32, rect.y + 8)
        scene.shop_hitboxes.append((rect, "sell", item))
    text("Rueda: más objetos | ESC: salir", 390, 570)
    if scene.shop_selection is not None:
        draw_confirmation(scene)


def draw_confirmation(scene):
    app = scene.app
    screen = app.screen
    kind, item_id, shop_id = scene.shop_selection
    item = get_item_data(item_id) or {}
    price = (next((price for product, price in available_items(shop_id) if product == item_id), 0)
             if kind == "buy" else sell_price(item_id))
    count = getattr(scene, "shop_quantity", 1)
    panel = pygame.Rect(215, 164, 530, 300)
    pygame.draw.rect(screen, (245, 245, 245), panel)
    pygame.draw.rect(screen, (75, 75, 75), panel, 3)
    font, small = app.font, app.small_font
    def label(value, x, y, use_font=small):
        screen.blit(use_font.render(str(value), True, (45, 45, 45)), (x, y))
    label(item.get("name", item_id), 240, 187, font)
    description = item.get("description") or ("Objeto de tipo " + item.get("type", "general") + ".")
    label(description[:66], 240, 224)
    if kind == "sell":
        label("Disponibles: " + str(quantity(app.state, item_id)), 240, 251)
    label("Precio unidad: " + str(price) + " oro", 240, 278)
    label("Cantidad:", 240, 316)
    scene.shop_modal_hitboxes = []
    for x, sign in ((423, "-"), (543, "+")):
        rect = pygame.Rect(x, 306, 45, 42)
        pygame.draw.rect(screen, (222, 222, 222), rect)
        pygame.draw.rect(screen, (100, 100, 100), rect, 2)
        label(sign, x + 15, 313, font)
        scene.shop_modal_hitboxes.append((rect, "decrease" if sign == "-" else "increase"))
    label(str(count), 497, 313, font)
    label("Total: " + str(price * count) + " oro", 240, 362, font)
    if getattr(scene, "shop_error", None):
        label(scene.shop_error, 455, 369)
    for x, title, action in ((240, "COMPRAR" if kind == "buy" else "VENDER", "confirm"),
                             (510, "CANCELAR", "cancel")):
        rect = pygame.Rect(x, 400, 205, 44)
        pygame.draw.rect(screen, (224, 224, 224), rect)
        pygame.draw.rect(screen, (100, 100, 100), rect, 2)
        label(title, x + 29, 410)
        scene.shop_modal_hitboxes.append((rect, action))


def change_quantity(scene, step):
    if scene.shop_selection is None:
        return
    kind, item_id, shop_id = scene.shop_selection
    limit = quantity(scene.app.state, item_id) if kind == "sell" else 99
    scene.shop_quantity = max(1, min(max(1, limit), getattr(scene, "shop_quantity", 1) + step))


def handle_event(scene, event):
    if scene.shop_selection is not None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                scene.shop_selection = None
            elif event.key == pygame.K_RETURN:
                confirm(scene)
            elif event.key in (pygame.K_RIGHT, pygame.K_UP, pygame.K_PLUS, pygame.K_EQUALS):
                change_quantity(scene, 1)
            elif event.key in (pygame.K_LEFT, pygame.K_DOWN, pygame.K_MINUS):
                change_quantity(scene, -1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, action in getattr(scene, "shop_modal_hitboxes", []):
                if rect.collidepoint(event.pos):
                    if action == "increase":
                        change_quantity(scene, 1)
                    elif action == "decrease":
                        change_quantity(scene, -1)
                    elif action == "cancel":
                        scene.shop_selection = None
                    elif action == "confirm":
                        confirm(scene)
                    break
        return True
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            scene.shop_id = None
        return True
    if event.type == pygame.MOUSEWHEEL:
        count = len(inventory_stacks(scene.app.state))
        scene.shop_page = max(0, min(max(0, (count - 1) // 14), scene.shop_page - event.y))
        return True
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for rect, kind, item in scene.shop_hitboxes:
            if not rect.collidepoint(event.pos):
                continue
            if kind == "exit":
                scene.shop_id = None
            elif kind in ("buy", "sell"):
                scene.shop_selection = (kind, item, scene.shop_id if kind == "buy" else None)
                scene.shop_quantity = 1
                scene.shop_error = None
            elif kind == "accept":
                scene.app.add_log("Selecciona un objeto para comprar o vender.")
            break
        return True
    return True


def confirm(scene):
    success, message = execute(scene.app.state, scene.shop_selection, getattr(scene, "shop_quantity", 1))
    scene.app.add_log(message)
    if not success:
        scene.shop_error = "No tienes suficiente dinero." if message == "No tienes suficiente oro." else message
        return
    scene.shop_error = None
    if success:
        scene.autosave()
        scene.shop_selection = None
        scene.shop_quantity = 1
