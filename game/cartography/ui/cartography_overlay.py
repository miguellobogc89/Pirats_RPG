import pygame

from game.cartography.data.world_map import WORLD_MAP
from game.cartography.expedition_setup import create_expedition_setup
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
STORAGE_GRID_COLS = 4
STORAGE_SLOT_SIZE = 36
STORAGE_SLOT_GAP = 6


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
    draw_cartography_footer(app, window_rect)

    if ui_state.modal_open:
        draw_expedition_modal(app)


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

    button_rect = pygame.Rect(inner.x, inner.bottom - 42, inner.width, 38)
    draw_button(app.screen, button_rect)
    draw_button_text(app.screen, app.font, "Nueva expedicion", button_rect)
    ui_state.expedition_button = button_rect


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
    modal_content = pygame.Rect(250, 170, 460, 276)
    modal_rect = modal_content.inflate(34, 58)

    draw_panel(app.screen, modal_rect)

    ui_state = app.cartography_ui_state
    selected_region = app.cartography_manager.get_region_view_data(ui_state.selected_region_id)

    if selected_region is None:
        return

    expedition_setup = ui_state.expedition_setup

    if expedition_setup is None or expedition_setup.region_id != selected_region["id"]:
        expedition_setup = create_expedition_setup(
            selected_region["id"],
            app.expedition_manager,
            app.cartography_manager.ship_storage,
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

    draw_label_value(
        app.screen,
        app.small_font,
        "Provisiones",
        f"{expedition_setup.provisions_assigned}/{expedition_setup.provisions_required}",
        modal_content.x,
        modal_content.y + 88,
    )

    cargo_y = modal_content.y + 122
    ship_storage = app.cartography_manager.ship_storage
    app.draw_text("BODEGA", modal_content.x, cargo_y, TEXT_DARK, app.font)
    app.draw_text(
        f"Carga: {expedition_setup.capacity_used}/{ship_storage.max_slots}",
        modal_content.x + 110,
        cargo_y + 4,
        TEXT_DISABLED,
        app.small_font,
    )

    draw_cargo_grid(app, modal_content.x, cargo_y + 36, ship_storage.max_slots)

    app.draw_text(
        "Seleccion de carga pendiente",
        modal_content.x + 196,
        cargo_y + 46,
        TEXT_DISABLED,
        app.small_font,
    )
    app.draw_text(
        get_expedition_setup_status_text(expedition_setup),
        modal_content.x + 196,
        cargo_y + 70,
        TEXT_DARK if expedition_setup.can_launch else TEXT_DISABLED,
        app.small_font,
    )

    cancel_rect = pygame.Rect(modal_content.right - 218, modal_content.bottom - 38, 100, 38)
    launch_rect = pygame.Rect(modal_content.right - 106, modal_content.bottom - 38, 100, 38)

    draw_button(app.screen, cancel_rect)
    draw_button_text(app.screen, app.font, "Cancelar", cancel_rect)

    draw_button(app.screen, launch_rect)
    draw_button_text(app.screen, app.font, "Zarpar", launch_rect)

    ui_state.cancel_button = cancel_rect
    ui_state.launch_button = launch_rect


def get_expedition_setup_status_text(expedition_setup):
    if expedition_setup.can_launch:
        return "Listo para zarpar"

    if not expedition_setup.validation_errors:
        return "Preparacion incompleta"

    return "Error: " + expedition_setup.validation_errors[0]


def draw_cargo_grid(app, x, y, slot_count):
    for slot_index in range(slot_count):
        row = slot_index // STORAGE_GRID_COLS
        col = slot_index % STORAGE_GRID_COLS
        slot_rect = pygame.Rect(
            x + col * (STORAGE_SLOT_SIZE + STORAGE_SLOT_GAP),
            y + row * (STORAGE_SLOT_SIZE + STORAGE_SLOT_GAP),
            STORAGE_SLOT_SIZE,
            STORAGE_SLOT_SIZE,
        )

        pygame.draw.rect(app.screen, PARCHMENT_LIGHT, slot_rect, border_radius=6)
        pygame.draw.rect(app.screen, WOOD_DARK, slot_rect, 2, border_radius=6)
