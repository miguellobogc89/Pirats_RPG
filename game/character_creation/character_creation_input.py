import sys

import pygame

from core.game_state import create_new_game_state
from core.save_manager import get_available_save_slot_id
from game.character_creation.character_creation_state import (
    FALLBACK_SCENE_ID,
    GENDER_OPTIONS,
    INITIAL_SCENE_ID,
    INITIAL_SPAWN_ID,
)
from game.scenes.scene_loader import scene_exists


def handle_character_creation_event(app, event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        return handle_click(app, event.pos)

    if event.type == pygame.KEYDOWN:
        return handle_key(app, event)

    return True


def handle_click(app, pos):
    rects = app.character_creation_state.get("button_rects", {})

    for key, rect in rects.items():
        if not rect.collidepoint(pos):
            continue

        if key == "name":
            app.character_creation_state["selected_field"] = "name"
            return True

        if key.startswith("gender:"):
            app.character_creation_state["gender"] = key.split(":", 1)[1]
            return True

        if key == "create":
            confirm_character_creation(app)
            return True

        if key == "cancel":
            app.mode = "main_menu"
            return True

    return True


def handle_key(app, event):
    state = app.character_creation_state

    if event.key == pygame.K_ESCAPE:
        app.mode = "main_menu"
        return True

    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        confirm_character_creation(app)
        return True

    if event.key == pygame.K_TAB:
        cycle_gender(app)
        return True

    if state["selected_field"] == "name":
        handle_name_input(state, event)
        return True

    return True


def handle_name_input(state, event):
    if event.key == pygame.K_BACKSPACE:
        state["name"] = state["name"][:-1]
        return

    if event.unicode and len(state["name"]) < 18:
        state["name"] += event.unicode


def cycle_gender(app):
    state = app.character_creation_state
    current_index = GENDER_OPTIONS.index(state["gender"])
    state["gender"] = GENDER_OPTIONS[(current_index + 1) % len(GENDER_OPTIONS)]


def confirm_character_creation(app):
    name = app.character_creation_state["name"].strip()

    if not name:
        app.character_creation_state["message"] = "Introduce un nombre"
        return

    save_slot_id = get_available_save_slot_id()

    if save_slot_id is None:
        app.character_creation_state["message"] = "No hay huecos de guardado libres"
        return

    state = create_new_game_state(
        name,
        app.character_creation_state["gender"],
        app.game_data,
    )
    state["save_slot_id"] = save_slot_id

    scene_id = INITIAL_SCENE_ID if scene_exists(INITIAL_SCENE_ID) else FALLBACK_SCENE_ID
    state["current_scene"] = scene_id

    app.load_game_state(
        state,
        scene_payload={
            "target_spawn_id": INITIAL_SPAWN_ID,
        },
        dispatch_scene_entered=True,
    )
    app.mode = "game"
