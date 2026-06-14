import pygame

from game.main_menu.main_menu_state import MAIN_MENU_OPTIONS
from game.ui.ui_components import (
    TEXT_DARK,
    TEXT_DISABLED,
    draw_button_text,
    draw_panel,
)


BUTTON_WIDTH = 260
BUTTON_HEIGHT = 46
BUTTON_GAP = 14


def draw_main_menu(app):
    draw_background(app)

    if app.main_menu_state.get("show_options"):
        draw_options(app)
        return

    if app.main_menu_state.get("show_load_game"):
        draw_load_game(app)
        return

    title = app.big_font.render("Pirats RPG", True, app.WHITE)
    app.screen.blit(
        title,
        (
            (app.screen.get_width() - title.get_width()) // 2,
            118,
        ),
    )

    app.main_menu_state["button_rects"] = draw_menu_buttons(app)
    draw_menu_message(app)


def draw_background(app):
    app.screen.fill((62, 93, 82))
    overlay = pygame.Surface((app.screen.get_width(), app.screen.get_height()))
    overlay.set_alpha(80)
    overlay.fill((30, 45, 42))
    app.screen.blit(overlay, (0, 0))


def draw_menu_buttons(app):
    rects = []
    x = (app.screen.get_width() - BUTTON_WIDTH) // 2
    y = 240

    for index, (_, label) in enumerate(MAIN_MENU_OPTIONS):
        rect = pygame.Rect(
            x,
            y + index * (BUTTON_HEIGHT + BUTTON_GAP),
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )
        selected = index == app.main_menu_state["selected_index"]
        hovered = index == app.main_menu_state.get("hovered_index")
        draw_menu_button(app, rect, label, selected or hovered)
        rects.append(rect)

    return rects


def draw_menu_button(app, rect, label, selected):
    draw_panel(app.screen, rect)

    if selected:
        pygame.draw.rect(
            app.screen,
            (250, 248, 235),
            rect.inflate(-8, -8),
            2,
            border_radius=6,
        )

    draw_button_text(app.screen, app.font, label, rect, enabled=True)


def draw_menu_message(app):
    message = app.main_menu_state.get("message")

    if not message:
        return

    surface = app.font.render(message, True, (250, 230, 170))
    app.screen.blit(
        surface,
        (
            (app.screen.get_width() - surface.get_width()) // 2,
            515,
        ),
    )


def draw_options(app):
    title = app.big_font.render("Opciones", True, app.WHITE)
    app.screen.blit(
        title,
        (
            (app.screen.get_width() - title.get_width()) // 2,
            170,
        ),
    )

    panel_rect = pygame.Rect(
        (app.screen.get_width() - 420) // 2,
        250,
        420,
        130,
    )
    draw_panel(app.screen, panel_rect)

    text = app.font.render("Opciones proximamente", True, TEXT_DARK)
    app.screen.blit(
        text,
        (
            panel_rect.x + (panel_rect.width - text.get_width()) // 2,
            panel_rect.y + 42,
        ),
    )

    hint = app.small_font.render("Escape para volver", True, TEXT_DISABLED)
    app.screen.blit(
        hint,
        (
            panel_rect.x + (panel_rect.width - hint.get_width()) // 2,
            panel_rect.bottom - 34,
        ),
    )


def draw_load_game(app):
    title = app.big_font.render("Cargar partida", True, app.WHITE)
    app.screen.blit(
        title,
        (
            (app.screen.get_width() - title.get_width()) // 2,
            150,
        ),
    )

    panel_rect = pygame.Rect(
        (app.screen.get_width() - 520) // 2,
        220,
        520,
        240,
    )
    draw_panel(app.screen, panel_rect)
    saved_games = app.main_menu_state.get("saved_games", [])
    app.main_menu_state["load_button_rects"] = []

    if not saved_games:
        text = app.font.render("No hay partidas guardadas", True, TEXT_DARK)
        app.screen.blit(
            text,
            (
                panel_rect.x + (panel_rect.width - text.get_width()) // 2,
                panel_rect.y + 82,
            ),
        )
    else:
        y = panel_rect.y + 34

        for index, saved_game in enumerate(saved_games):
            rect = pygame.Rect(panel_rect.x + 42, y, panel_rect.width - 84, 42)
            selected = index == app.main_menu_state.get("load_selected_index")
            hovered = index == app.main_menu_state.get("load_hovered_index")
            draw_menu_button(app, rect, saved_game["label"], selected or hovered)
            app.main_menu_state["load_button_rects"].append(rect)
            y += 54

    hint = app.small_font.render("Enter/click cargar | Escape volver", True, TEXT_DISABLED)
    app.screen.blit(
        hint,
        (
            panel_rect.x + (panel_rect.width - hint.get_width()) // 2,
            panel_rect.bottom - 34,
        ),
    )
