import sys

import pygame

from core.game_state import normalize_state
from core.save_manager import list_saved_games, load_saved_state
from game.main_menu.main_menu_state import MAIN_MENU_OPTIONS
from game.notifications import notify


def handle_main_menu_event(app, event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    if app.main_menu_state.get("show_options"):
        return handle_options_event(app, event)

    if app.main_menu_state.get("show_load_game"):
        return handle_load_game_event(app, event)

    if event.type == pygame.MOUSEMOTION:
        update_hover(app, event.pos)
        return True

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        clicked_index = get_button_index_at_pos(app, event.pos)

        if clicked_index is not None:
            app.main_menu_state["selected_index"] = clicked_index
            activate_selected_option(app)

        return True

    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_UP, pygame.K_w):
            move_selection(app, -1)
            return True

        if event.key in (pygame.K_DOWN, pygame.K_s):
            move_selection(app, 1)
            return True

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            activate_selected_option(app)
            return True

    return True


def handle_options_event(app, event):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        app.main_menu_state["show_options"] = False
        app.main_menu_state["message"] = ""
        return True

    return True


def handle_load_game_event(app, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            app.main_menu_state["show_load_game"] = False
            app.main_menu_state["message"] = ""
            return True

        if event.key in (pygame.K_UP, pygame.K_w):
            move_load_selection(app, -1)
            return True

        if event.key in (pygame.K_DOWN, pygame.K_s):
            move_load_selection(app, 1)
            return True

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            load_selected_game(app)
            return True

    if event.type == pygame.MOUSEMOTION:
        update_load_hover(app, event.pos)
        return True

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        clicked_index = get_load_button_index_at_pos(app, event.pos)

        if clicked_index is not None:
            app.main_menu_state["load_selected_index"] = clicked_index
            load_selected_game(app)

        return True

    return True


def update_hover(app, pos):
    app.main_menu_state["hovered_index"] = get_button_index_at_pos(app, pos)

    if app.main_menu_state["hovered_index"] is not None:
        app.main_menu_state["selected_index"] = app.main_menu_state["hovered_index"]


def get_button_index_at_pos(app, pos):
    for index, rect in enumerate(app.main_menu_state.get("button_rects", [])):
        if rect.collidepoint(pos):
            return index

    return None


def move_selection(app, direction):
    count = len(MAIN_MENU_OPTIONS)
    current_index = app.main_menu_state["selected_index"]
    app.main_menu_state["selected_index"] = (current_index + direction) % count


def activate_selected_option(app):
    option_id = MAIN_MENU_OPTIONS[app.main_menu_state["selected_index"]][0]

    if option_id == "new_game":
        app.open_character_creation()
        return

    if option_id == "load_game":
        open_load_game(app)
        return

    if option_id == "options":
        app.main_menu_state["show_options"] = True
        app.main_menu_state["message"] = ""
        return

    if option_id == "quit":
        pygame.quit()
        sys.exit()


def open_load_game(app):
    saved_games = list_saved_games()
    app.main_menu_state["saved_games"] = saved_games
    app.main_menu_state["load_selected_index"] = 0
    app.main_menu_state["load_hovered_index"] = None
    app.main_menu_state["show_load_game"] = True

    if not saved_games:
        app.main_menu_state["message"] = "No hay partida guardada"
        notify(app, "No hay partida guardada", notification_type="corner")


def move_load_selection(app, direction):
    saved_games = app.main_menu_state.get("saved_games", [])

    if not saved_games:
        return

    count = len(saved_games)
    current_index = app.main_menu_state.get("load_selected_index", 0)
    app.main_menu_state["load_selected_index"] = (current_index + direction) % count


def update_load_hover(app, pos):
    hovered_index = get_load_button_index_at_pos(app, pos)
    app.main_menu_state["load_hovered_index"] = hovered_index

    if hovered_index is not None:
        app.main_menu_state["load_selected_index"] = hovered_index


def get_load_button_index_at_pos(app, pos):
    for index, rect in enumerate(app.main_menu_state.get("load_button_rects", [])):
        if rect.collidepoint(pos):
            return index

    return None


def load_selected_game(app):
    saved_games = app.main_menu_state.get("saved_games", [])

    if not saved_games:
        app.main_menu_state["message"] = "No hay partida guardada"
        notify(app, "No hay partida guardada", notification_type="corner")
        return

    selected_index = app.main_menu_state.get("load_selected_index", 0)

    if selected_index < 0 or selected_index >= len(saved_games):
        selected_index = 0

    continue_game(app, saved_games[selected_index]["id"])


def continue_game(app, save_slot_id):
    saved_state = load_saved_state(save_slot_id)

    if saved_state is None:
        app.main_menu_state["message"] = "No hay partida guardada"
        notify(app, "No hay partida guardada", notification_type="corner")
        return

    app.load_game_state(
        normalize_state(saved_state, app.game_data),
        dispatch_scene_entered=True,
    )
    app.mode = "game"
