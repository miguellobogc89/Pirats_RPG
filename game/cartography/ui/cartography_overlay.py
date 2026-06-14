import pygame

from game.cartography.data.world_map import WORLD_MAP
from game.cartography.expedition_setup import create_expedition_setup
from game.cartography.ship_storage_transfer import is_item_allowed_in_ship_storage
from game.data.item_database import get_item_data
from game.inventory.inventory_manager import get_inventory_grid
from game.ui.ui_components import (
    PARCHMENT_LIGHT,
    TEXT_DARK,
    TEXT_DISABLED,
    WOOD_DARK,
    draw_button,
    draw_button_text,
    draw_content_panel,
    draw_label_value,
    draw_panel,
    draw_progress_bar,
    draw_window,
)


GRID_COLS = 5
GRID_ROWS = 4
WINDOW_PADDING = 20
MAP_SIZE = (560, 400)
INFO_WIDTH = 250
TRANSFER_ROW_HEIGHT = 24
TRANSFER_LIST_WIDTH = 224
TRANSFER_LIST_ROWS = 6


def draw_cartography_overlay(app):
    ui_state = app.cartography_ui_state
    ui_state.clear_hitboxes()

    window_rect = pygame.Rect(40, 40, 880, 560)
    draw_window(
        app.screen,
        window_rect,
        "MAPA CARTOGRAFICO",
        app.font,
        app.big_font,
    )

    content_x = window_rect.x + WINDOW_PADDING
    content_y = window_rect.y + 60
    map_rect = pygame.Rect(content_x, content_y, MAP_SIZE[0], MAP_SIZE[1])
    info_content_rect = pygame.Rect(
        map_rect.right + 28,
        content_y + 6,
        INFO_WIDTH,
        306,
    )

    selected_region = draw_map_panel(app, map_rect)
    draw_region_panel(app, selected_region, info_content_rect)
    draw_pending_rewards_action(app, window_rect)
    draw_cartography_footer(app, window_rect)

    if ui_state.modal_open:
        draw_expedition_modal(app)

    if ui_state.reward_modal_open:
        draw_rewards_modal(app)


def draw_map_panel(app, map_rect):
    map_inner = draw_content_panel(app.screen, map_rect, padding=10)
    pygame.draw.rect(app.screen, PARCHMENT_LIGHT, map_inner)
    pygame.draw.rect(app.screen, WOOD_DARK, map_inner, 2)

    cell_w = map_inner.width // GRID_COLS
    cell_h = map_inner.height // GRID_ROWS

    ui_state = app.cartography_ui_state

    if ui_state.selected_region_id is None:
        ui_state.selected_region_id = app.cartography_manager.active_anchor_region_id

    selected_region = None
    map_view = app.cartography_manager.get_map_view_data(WORLD_MAP)

    for row, row_data in enumerate(map_view):
        for col, region in enumerate(row_data):
            x = map_inner.x + col * cell_w
            y = map_inner.y + row * cell_h
            cell_rect = pygame.Rect(x, y, cell_w, cell_h)

            pygame.draw.rect(app.screen, (102, 90, 68), cell_rect, 1)

            if region is None:
                continue

            region_id = region["id"]
            ui_state.region_cells[region_id] = cell_rect

            if region_id == ui_state.selected_region_id:
                selected_region = region

            draw_region_cell(app, region_id, region, cell_rect)

    return selected_region


def draw_region_cell(app, region_id, region, cell_rect):
    inner_rect = cell_rect.inflate(-4, -4)

    if region["hidden"]:
        pygame.draw.rect(app.screen, (58, 49, 39), inner_rect)
        app.draw_text("???", inner_rect.x + 8, inner_rect.y + 8, TEXT_DISABLED, app.small_font)
        return

    color = (213, 196, 145)

    if region["state"] == "settled":
        color = (170, 205, 145)

    pygame.draw.rect(app.screen, color, inner_rect)
    pygame.draw.rect(app.screen, WOOD_DARK, inner_rect, 2)

    if region_id == app.cartography_ui_state.selected_region_id:
        pygame.draw.rect(app.screen, (255, 220, 100), cell_rect, 3)

    app.draw_text(region["name"], inner_rect.x + 8, inner_rect.y + 8, TEXT_DARK, app.small_font)


def draw_region_panel(app, selected_region, content_rect):
    inner = draw_content_panel(app.screen, content_rect, padding=14)
    ui_state = app.cartography_ui_state

    app.draw_text("REGION", inner.x, inner.y, TEXT_DISABLED, app.small_font)

    if selected_region is None:
        app.draw_text("Selecciona una region.", inner.x, inner.y + 34, TEXT_DARK, app.font)
        return

    app.draw_text(selected_region["name"], inner.x, inner.y + 34, TEXT_DARK, app.font)

    draw_label_value(
        app.screen,
        app.small_font,
        "Estado",
        selected_region["state"],
        inner.x,
        inner.y + 78,
    )

    draw_label_value(
        app.screen,
        app.small_font,
        "Visitas",
        selected_region["visits"],
        inner.x,
        inner.y + 104,
    )

    app.draw_text("Cartografia", inner.x, inner.y + 134, TEXT_DISABLED, app.small_font)
    draw_progress_bar(
        app.screen,
        pygame.Rect(inner.x, inner.y + 156, inner.width, 12),
        selected_region["cartography_percent"],
        100,
        (119, 146, 88),
        background_color=(70, 48, 34),
        border_color=WOOD_DARK,
    )
    app.draw_text(
        f"{selected_region['cartography_percent']}%",
        inner.x,
        inner.y + 174,
        TEXT_DARK,
        app.small_font,
    )

    if app.cartography_manager.active_expedition is not None:
        draw_active_expedition_status(app, inner)
        return

    button_rect = pygame.Rect(inner.x, inner.bottom - 42, inner.width, 38)
    draw_button(app.screen, button_rect)
    draw_button_text(app.screen, app.font, "Nueva expedicion", button_rect)
    ui_state.expedition_button = button_rect


def draw_active_expedition_status(app, inner):
    expedition = app.cartography_manager.active_expedition
    region = app.cartography_manager.get_region_view_data(expedition.get("region_id"))
    region_name = expedition.get("region_id")

    if region is not None:
        region_name = region["name"]

    total_days = expedition.get("total_days", 0)
    remaining_days = expedition.get("remaining_days", 0)
    elapsed_days = total_days - remaining_days

    if elapsed_days < 0:
        elapsed_days = 0

    app.draw_text("EXPEDICION EN CURSO", inner.x, inner.y + 210, TEXT_DISABLED, app.small_font)
    draw_label_value(
        app.screen,
        app.small_font,
        "Destino",
        region_name,
        inner.x,
        inner.y + 236,
    )
    draw_label_value(
        app.screen,
        app.small_font,
        "Dias restantes",
        remaining_days,
        inner.x,
        inner.y + 262,
    )

    draw_label_value(
        app.screen,
        app.small_font,
        "Progreso",
        f"{elapsed_days}/{total_days} dias",
        inner.x,
        inner.y + 288,
    )

    draw_progress_bar(
        app.screen,
        pygame.Rect(inner.x, inner.y + 314, inner.width, 12),
        elapsed_days,
        total_days,
        (119, 146, 88),
        background_color=(70, 48, 34),
        border_color=WOOD_DARK,
    )

    disabled_rect = pygame.Rect(inner.x, inner.bottom - 42, inner.width, 38)
    draw_button(app.screen, disabled_rect, enabled=False)
    draw_button_text(app.screen, app.font, "Expedicion en curso", disabled_rect, enabled=False)


def draw_pending_rewards_action(app, window_rect):
    if not app.cartography_manager.has_pending_expedition_results():
        return

    rewards_rect = pygame.Rect(window_rect.right - 172, window_rect.bottom - 86, 140, 38)
    draw_button(app.screen, rewards_rect)
    draw_button_text(app.screen, app.font, "Reclamar", rewards_rect)
    app.cartography_ui_state.rewards_button = rewards_rect


def draw_reward_line(app, item_id, amount, x, y):
    item_data = get_item_data(item_id)
    item_name = item_id

    if item_data is not None:
        item_name = item_data["name"]

    app.draw_text(f"{item_name}: x{amount}", x, y, TEXT_DARK, app.small_font)


def draw_rewards_modal(app):
    modal_content = pygame.Rect(245, 170, 430, 260)
    modal_rect = modal_content.inflate(34, 58)
    pending_results = app.cartography_manager.get_pending_expedition_results()

    draw_panel(app.screen, modal_rect)

    if not pending_results:
        return

    app.draw_text("RECOMPENSAS", modal_content.x, modal_rect.y + 18, TEXT_DARK, app.font)

    rewards_y = modal_content.y
    reward_lines = get_pending_reward_lines(app, pending_results)

    if not reward_lines:
        app.draw_text("No hay recompensas pendientes.", modal_content.x, rewards_y, TEXT_DISABLED, app.small_font)
    else:
        for index, line in enumerate(reward_lines[:8]):
            color = TEXT_DISABLED if line["type"] == "region" else TEXT_DARK
            app.draw_text(line["text"], modal_content.x, rewards_y + index * 24, color, app.small_font)

    app.draw_text(
        "Pendiente de reclamacion.",
        modal_content.x,
        modal_content.bottom - 76,
        TEXT_DISABLED,
        app.small_font,
    )

    close_rect = pygame.Rect(modal_content.right - 100, modal_content.bottom - 42, 100, 38)
    draw_button(app.screen, close_rect)
    draw_button_text(app.screen, app.font, "Cerrar", close_rect)
    app.cartography_ui_state.rewards_close_button = close_rect


def get_pending_reward_lines(app, pending_results):
    lines = []

    for pending_result in pending_results:
        region = app.cartography_manager.get_region_view_data(pending_result.get("region_id"))
        region_name = pending_result.get("region_id")

        if region is not None:
            region_name = region["name"]

        lines.append({
            "type": "region",
            "text": region_name,
        })

        rewards = pending_result.get("rewards", {})

        if not rewards:
            lines.append({
                "type": "reward",
                "text": "Sin recompensas registradas.",
            })
            continue

        for item_id in sorted(rewards):
            lines.append({
                "type": "reward",
                "text": get_reward_text(item_id, rewards[item_id]),
            })

    return lines


def get_reward_text(item_id, amount):
    item_data = get_item_data(item_id)
    item_name = item_id

    if item_data is not None:
        item_name = item_data["name"]

    return f"  {item_name}: x{amount}"


def draw_cartography_footer(app, window_rect):
    footer_y = window_rect.bottom - 38
    active_anchor = app.cartography_manager.get_region_view_data(
        app.cartography_manager.active_anchor_region_id
    )
    anchor_name = "Desconocido"

    if active_anchor is not None:
        anchor_name = active_anchor["name"]

    app.draw_text(f"Puerto actual: {anchor_name}", window_rect.x + 22, footer_y, TEXT_DARK, app.small_font)
    app.draw_text(
        f"Cartografia global: {app.cartography_manager.get_global_cartography_percent()}%",
        window_rect.x + 300,
        footer_y,
        TEXT_DARK,
        app.small_font,
    )
    app.draw_text("ESC cerrar", window_rect.right - 110, footer_y, TEXT_DARK, app.small_font)


def draw_expedition_modal(app):
    modal_content = pygame.Rect(170, 120, 620, 430)
    modal_rect = modal_content.inflate(34, 58)

    draw_panel(app.screen, modal_rect)

    ui_state = app.cartography_ui_state
    selected_region = app.cartography_manager.get_region_view_data(ui_state.selected_region_id)

    if selected_region is None:
        return

    expedition_setup = create_expedition_setup(
        selected_region["id"],
        app.expedition_manager,
        app.cartography_manager.ship_storage,
        state=app.state,
    )
    ui_state.expedition_setup = expedition_setup

    if not expedition_setup.cost:
        return

    app.draw_text("PREPARAR EXPEDICION", modal_content.x, modal_rect.y + 18, TEXT_DARK, app.font)
    app.draw_text(f"Destino: {selected_region['name']}", modal_content.x, modal_content.y, TEXT_DARK)

    draw_label_value(
        app.screen,
        app.small_font,
        "Dias",
        expedition_setup.cost["days"],
        modal_content.x,
        modal_content.y + 36,
    )

    draw_label_value(
        app.screen,
        app.small_font,
        "Peligro",
        expedition_setup.cost["risk"],
        modal_content.x,
        modal_content.y + 62,
    )

    draw_travel_requirements(app, expedition_setup, modal_content.x, modal_content.y + 88)

    cargo_y = modal_content.y + 166
    ship_storage = app.cartography_manager.ship_storage
    app.draw_text("BODEGA DE PREPARACION", modal_content.x, cargo_y, TEXT_DARK, app.font)
    app.draw_text(
        f"Bodega: {expedition_setup.capacity_used}/{ship_storage.max_slots}",
        modal_content.x + 178,
        cargo_y + 4,
        TEXT_DISABLED,
        app.small_font,
    )

    transfer_y = cargo_y + 34
    draw_transfer_lists(app, modal_content.x, transfer_y, expedition_setup.required_items)

    app.draw_text(
        get_expedition_setup_status_text(expedition_setup),
        modal_content.x,
        modal_content.bottom - 76,
        TEXT_DARK if expedition_setup.can_launch else TEXT_DISABLED,
        app.small_font,
    )

    cancel_rect = pygame.Rect(modal_content.right - 218, modal_content.bottom - 42, 100, 38)
    launch_rect = pygame.Rect(modal_content.right - 106, modal_content.bottom - 42, 100, 38)

    draw_button(app.screen, cancel_rect)
    draw_button_text(app.screen, app.font, "Cancelar", cancel_rect)

    draw_button(app.screen, launch_rect)
    draw_button_text(app.screen, app.font, "Zarpar", launch_rect)

    ui_state.cancel_button = cancel_rect
    ui_state.launch_button = launch_rect


def get_expedition_setup_status_text(expedition_setup):
    if expedition_setup.can_launch:
        return "Listo para zarpar"

    if "not_enough_gold" in expedition_setup.validation_errors:
        return "No puedes zarpar: falta oro"

    if "not_enough_required_items" in expedition_setup.validation_errors:
        return "No puedes zarpar: faltan items en bodega"

    if not expedition_setup.validation_errors:
        return "Preparacion incompleta"

    return "Error: " + expedition_setup.validation_errors[0]


def draw_travel_requirements(app, expedition_setup, x, y):
    app.draw_text("REQUISITOS DEL VIAJE", x, y, TEXT_DISABLED, app.small_font)
    draw_requirement_line(
        app,
        "Oro",
        expedition_setup.gold_available,
        expedition_setup.gold_required,
        x,
        y + 22,
    )

    item_y = y + 44

    for index, item_id in enumerate(sorted(expedition_setup.required_items)):
        required_amount = expedition_setup.required_items[item_id]
        assigned_amount = expedition_setup.assigned_items.get(item_id, 0)
        item_data = get_item_data(item_id)
        item_name = item_id

        if item_data is not None:
            item_name = item_data["name"]

        draw_requirement_line(
            app,
            item_name,
            assigned_amount,
            required_amount,
            x,
            item_y + index * 22,
        )


def draw_requirement_line(app, label, current_amount, required_amount, x, y):
    color = TEXT_DARK if current_amount >= required_amount else TEXT_DISABLED

    app.draw_text(
        f"{label}: {current_amount}/{required_amount}",
        x,
        y,
        color,
        app.small_font,
    )


def draw_transfer_lists(app, x, y, required_items):
    storage_x = x + TRANSFER_LIST_WIDTH + 34

    app.draw_text("INVENTARIO TRANSFERIBLE", x, y, TEXT_DISABLED, app.small_font)
    app.draw_text("BODEGA PARA REQUISITOS", storage_x, y, TEXT_DISABLED, app.small_font)

    draw_inventory_transfer_list(app, x, y + 22, required_items)
    draw_storage_transfer_list(app, storage_x, y + 22, required_items)


def draw_inventory_transfer_list(app, x, y, required_items):
    items = get_transferable_inventory_items(app.state, required_items)
    ui_state = app.cartography_ui_state

    if not items:
        app.draw_text("Sin carga transferible", x, y, TEXT_DISABLED, app.small_font)
        return

    for index, item in enumerate(items[:TRANSFER_LIST_ROWS]):
        row_rect = pygame.Rect(
            x,
            y + index * TRANSFER_ROW_HEIGHT,
            TRANSFER_LIST_WIDTH,
            TRANSFER_ROW_HEIGHT - 3,
        )
        draw_transfer_row(app, row_rect, item["item_id"], item["amount"])
        ui_state.inventory_transfer_buttons.append({
            "rect": row_rect,
            "item_id": item["item_id"],
        })


def draw_storage_transfer_list(app, x, y, required_items):
    items = get_transferable_storage_items(app.cartography_manager.ship_storage, required_items)
    ui_state = app.cartography_ui_state

    if not items:
        app.draw_text("Bodega vacia", x, y, TEXT_DISABLED, app.small_font)
        return

    for index, item in enumerate(items[:TRANSFER_LIST_ROWS]):
        row_rect = pygame.Rect(
            x,
            y + index * TRANSFER_ROW_HEIGHT,
            TRANSFER_LIST_WIDTH,
            TRANSFER_ROW_HEIGHT - 3,
        )
        draw_transfer_row(app, row_rect, item["item_id"], item["amount"])
        ui_state.storage_transfer_buttons.append({
            "rect": row_rect,
            "item_id": item["item_id"],
        })


def draw_transfer_row(app, row_rect, item_id, amount):
    item_data = get_item_data(item_id)
    item_name = item_id

    if item_data is not None:
        item_name = item_data["name"]

    pygame.draw.rect(app.screen, PARCHMENT_LIGHT, row_rect, border_radius=4)
    pygame.draw.rect(app.screen, WOOD_DARK, row_rect, 1, border_radius=4)
    app.draw_text(item_name, row_rect.x + 6, row_rect.y + 3, TEXT_DARK, app.small_font)
    app.draw_text(f"x{amount}", row_rect.right - 42, row_rect.y + 3, TEXT_DARK, app.small_font)


def get_transferable_inventory_items(state, required_items):
    totals = {}
    allowed_item_ids = set(required_items)

    for row in get_inventory_grid(state):
        for slot in row:
            if slot is None:
                continue

            item_id = slot["item_id"]

            if item_id not in allowed_item_ids:
                continue

            if not is_item_allowed_in_ship_storage(item_id):
                continue

            totals[item_id] = totals.get(item_id, 0) + slot["amount"]

    return get_sorted_item_amounts(totals)


def get_transferable_storage_items(ship_storage, required_items):
    totals = {}
    allowed_item_ids = set(required_items)

    for item_id, amount in ship_storage.items.items():
        if item_id not in allowed_item_ids:
            continue

        if not is_item_allowed_in_ship_storage(item_id):
            continue

        totals[item_id] = amount

    return get_sorted_item_amounts(totals)


def get_sorted_item_amounts(totals):
    return [
        {
            "item_id": item_id,
            "amount": totals[item_id],
        }
        for item_id in sorted(totals)
    ]
