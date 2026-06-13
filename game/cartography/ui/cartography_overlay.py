import pygame

from game.cartography.data.world_map import WORLD_MAP
from game.cartography.data.region_database import REGION_DATABASE


GRID_COLS = 5
GRID_ROWS = 4


def draw_cartography_overlay(app):

    panel_x = 40
    panel_y = 40
    panel_w = 880
    panel_h = 560

    pygame.draw.rect(
        app.screen,
        app.PANEL,
        (panel_x, panel_y, panel_w, panel_h),
        border_radius=10,
    )

    pygame.draw.rect(
        app.screen,
        app.DARK,
        (panel_x, panel_y, panel_w, panel_h),
        3,
        border_radius=10,
    )

    app.draw_text(
        "MAPA CARTOGRAFICO",
        panel_x + 20,
        panel_y + 15,
        app.DARK,
        app.big_font,
    )

    map_x = panel_x + 20
    map_y = panel_y + 60
    map_w = 560
    map_h = 400

    info_x = map_x + map_w + 20
    info_y = map_y
    info_w = 240
    info_h = 400

    pygame.draw.rect(
        app.screen,
        app.WHITE,
        (map_x, map_y, map_w, map_h),
    )

    pygame.draw.rect(
        app.screen,
        app.DARK,
        (map_x, map_y, map_w, map_h),
        2,
    )

    cell_w = map_w // GRID_COLS
    cell_h = map_h // GRID_ROWS

    regions = REGION_DATABASE

    if not hasattr(app, "cartography_cells"):
        app.cartography_cells = {}

    app.cartography_cells.clear()

    if app.selected_region_id is None:
        app.selected_region_id = "home_port"
        
    selected_region = None

    for row, row_data in enumerate(WORLD_MAP):

        for col, region_id in enumerate(row_data):

            x = map_x + col * cell_w
            y = map_y + row * cell_h

            pygame.draw.rect(
                app.screen,
                (80, 80, 80),
                (x, y, cell_w, cell_h),
                1,
            )

            if region_id is None:
                continue

            region = regions[region_id]
            if region_id == app.selected_region_id:
                selected_region = region

            if region["hidden"]:

                pygame.draw.rect(
                    app.screen,
                    (40, 40, 40),
                    (x + 2, y + 2, cell_w - 4, cell_h - 4),
                )

                app.cartography_cells[region_id] = pygame.Rect(
                    x,
                    y,
                    cell_w,
                    cell_h,
                )

                continue

                app.draw_text(
                    "???",
                    x + 8,
                    y + 8,
                    (120, 120, 120),
                    app.small_font,
                )

            app.cartography_cells[region_id] = pygame.Rect(
                x,
                y,
                cell_w,
                cell_h,
            )

            color = (200, 200, 180)

            if region["state"] == "settled":
                color = (180, 220, 180)

            pygame.draw.rect(
                app.screen,
                color,
                (x + 2, y + 2, cell_w - 4, cell_h - 4),
            )

            pygame.draw.rect(
                app.screen,
                app.DARK,
                (x + 2, y + 2, cell_w - 4, cell_h - 4),
                2,
            )

            if region_id == app.selected_region_id:

                pygame.draw.rect(
                    app.screen,
                    (255, 220, 100),
                    (x, y, cell_w, cell_h),
                    3,
                )

                selected_region = region

            app.draw_text(
                region["name"],
                x + 8,
                y + 8,
                app.DARK,
                app.small_font,
            )
    
    pygame.draw.rect(
        app.screen,
        app.WHITE,
        (info_x, info_y, info_w, info_h),
    )

    pygame.draw.rect(
        app.screen,
        app.DARK,
        (info_x, info_y, info_w, info_h),
        2,
    )

    app.draw_text(
        "REGION",
        info_x + 10,
        info_y + 10,
        app.DARK,
        app.small_font,
    )

    if selected_region is not None:

        app.draw_text(
            selected_region["name"],
            info_x + 10,
            info_y + 40,
            app.DARK,
        )

        app.draw_text(
            f"Estado: {selected_region['state']}",
            info_x + 10,
            info_y + 90,
            app.DARK,
        )

        app.draw_text(
            f"Cartografia: {selected_region['cartography_percent']}%",
            info_x + 10,
            info_y + 120,
            app.DARK,
        )

        app.draw_text(
            f"Visitas: {selected_region['visits']}",
            info_x + 10,
            info_y + 150,
            app.DARK,
        )

        button_rect = pygame.Rect(
            info_x + 20,
            info_y + 320,
            200,
            40,
        )

        pygame.draw.rect(
            app.screen,
            (210, 210, 180),
            button_rect,
        )

        pygame.draw.rect(
            app.screen,
            app.DARK,
            button_rect,
            2,
        )

        app.cartography_expedition_button = button_rect

    pygame.draw.rect(
        app.screen,
        app.DARK,
        (info_x + 20, info_y + 320, 200, 40),
        2,
    )

    app.draw_text(
        "Nueva expedicion",
        info_x + 35,
        info_y + 332,
        app.DARK,
    )

    app.draw_text(
        "Puerto actual: Puerto Inicial",
        panel_x + 20,
        panel_y + 500,
        app.DARK,
        app.small_font,
    )

    app.draw_text(
        "Cartografia global: 3%",
        panel_x + 280,
        panel_y + 500,
        app.DARK,
        app.small_font,
    )

    app.draw_text(
        "ESC cerrar",
        panel_x + 730,
        panel_y + 500,
        app.DARK,
        app.small_font,
    )

    if app.cartography_modal_open:

        modal_w = 500
        modal_h = 380

        modal_x = app.screen.get_width() // 2 - modal_w // 2
        modal_y = app.screen.get_height() // 2 - modal_h // 2

        pygame.draw.rect(
            app.screen,
            app.PANEL,
            (modal_x, modal_y, modal_w, modal_h),
        )

        pygame.draw.rect(
            app.screen,
            app.DARK,
            (modal_x, modal_y, modal_w, modal_h),
            2,
        )

        selected_region = REGION_DATABASE[
            app.selected_region_id
        ]

        app.draw_text(
            "PREPARAR EXPEDICION",
            modal_x + 20,
            modal_y + 20,
            app.DARK,
        )

        app.draw_text(
            f"Destino: {selected_region['name']}",
            modal_x + 20,
            modal_y + 60,
            app.DARK,
        )

        app.draw_text(
            f"Dias: {selected_region['travel_days']}",
            modal_x + 20,
            modal_y + 90,
            app.DARK,
        )

        app.draw_text(
            f"Peligro: {selected_region['danger']}",
            modal_x + 20,
            modal_y + 120,
            app.DARK,
        )

        app.draw_text(
            "BODEGA",
            modal_x + 20,
            modal_y + 170,
            app.DARK,
        )

        grid_x = modal_x + 20
        grid_y = modal_y + 200

        slot_size = 40
        gap = 6

        for row in range(4):

            for col in range(4):

                x = grid_x + col * (slot_size + gap)
                y = grid_y + row * (slot_size + gap)

                pygame.draw.rect(
                    app.screen,
                    app.WHITE,
                    (x, y, slot_size, slot_size),
                )

                pygame.draw.rect(
                    app.screen,
                    app.DARK,
                    (x, y, slot_size, slot_size),
                    2,
                )

        cancel_rect = pygame.Rect(
            modal_x + 260,
            modal_y + 300,
            100,
            40,
        )

        launch_rect = pygame.Rect(
            modal_x + 370,
            modal_y + 300,
            100,
            40,
        )

        pygame.draw.rect(
            app.screen,
            (180, 180, 180),
            cancel_rect,
        )

        pygame.draw.rect(
            app.screen,
            app.DARK,
            cancel_rect,
            2,
        )

        pygame.draw.rect(
            app.screen,
            (180, 220, 180),
            launch_rect,
        )

        pygame.draw.rect(
            app.screen,
            app.DARK,
            launch_rect,
            2,
        )

        app.draw_text(
            "Cancelar",
            cancel_rect.x + 15,
            cancel_rect.y + 12,
            app.DARK,
        )

        app.draw_text(
            "Zarpar",
            launch_rect.x + 22,
            launch_rect.y + 12,
            app.DARK,
        )

        app.cartography_cancel_button = cancel_rect
        app.cartography_launch_button = launch_rect