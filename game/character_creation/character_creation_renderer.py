import pygame

from game.character_creation.character_creation_state import GENDER_OPTIONS
from game.ui.ui_components import (
    TEXT_DARK,
    TEXT_DISABLED,
    draw_button_text,
    draw_panel,
)


PANEL_WIDTH = 520
PANEL_HEIGHT = 360


def draw_character_creation(app):
    app.screen.fill((54, 83, 78))
    panel_rect = pygame.Rect(
        (app.screen.get_width() - PANEL_WIDTH) // 2,
        (app.screen.get_height() - PANEL_HEIGHT) // 2,
        PANEL_WIDTH,
        PANEL_HEIGHT,
    )
    draw_panel(app.screen, panel_rect)

    title = app.big_font.render("Crear personaje", True, TEXT_DARK)
    app.screen.blit(
        title,
        (
            panel_rect.x + (panel_rect.width - title.get_width()) // 2,
            panel_rect.y + 28,
        ),
    )

    draw_name_field(app, panel_rect)
    draw_gender_options(app, panel_rect)
    draw_action_buttons(app, panel_rect)
    draw_message(app, panel_rect)


def draw_name_field(app, panel_rect):
    state = app.character_creation_state
    label = app.font.render("Nombre", True, TEXT_DARK)
    app.screen.blit(label, (panel_rect.x + 58, panel_rect.y + 96))

    input_rect = pygame.Rect(panel_rect.x + 58, panel_rect.y + 124, 404, 42)
    pygame.draw.rect(app.screen, (250, 248, 235), input_rect, border_radius=6)
    pygame.draw.rect(app.screen, (76, 49, 31), input_rect, 2, border_radius=6)

    display_name = state["name"]

    if state["selected_field"] == "name" and pygame.time.get_ticks() // 500 % 2 == 0:
        display_name += "|"

    text = app.font.render(display_name, True, TEXT_DARK)
    app.screen.blit(text, (input_rect.x + 12, input_rect.y + 10))
    state["button_rects"]["name"] = input_rect


def draw_gender_options(app, panel_rect):
    state = app.character_creation_state
    label = app.font.render("Apariencia", True, TEXT_DARK)
    app.screen.blit(label, (panel_rect.x + 58, panel_rect.y + 190))

    start_x = panel_rect.x + 58
    y = panel_rect.y + 220
    width = 126
    height = 38
    gap = 14

    for index, gender in enumerate(GENDER_OPTIONS):
        rect = pygame.Rect(start_x + index * (width + gap), y, width, height)
        selected = state["gender"] == gender
        draw_panel(app.screen, rect)

        if selected:
            pygame.draw.rect(app.screen, (250, 248, 235), rect.inflate(-8, -8), 2, border_radius=6)

        draw_button_text(app.screen, app.small_font, gender, rect, enabled=True)
        state["button_rects"][f"gender:{gender}"] = rect


def draw_action_buttons(app, panel_rect):
    state = app.character_creation_state
    create_rect = pygame.Rect(panel_rect.x + 142, panel_rect.bottom - 70, 116, 38)
    cancel_rect = pygame.Rect(panel_rect.x + 270, panel_rect.bottom - 70, 116, 38)

    draw_panel(app.screen, create_rect)
    draw_panel(app.screen, cancel_rect)
    draw_button_text(app.screen, app.small_font, "Crear", create_rect, enabled=True)
    draw_button_text(app.screen, app.small_font, "Volver", cancel_rect, enabled=True)

    state["button_rects"]["create"] = create_rect
    state["button_rects"]["cancel"] = cancel_rect


def draw_message(app, panel_rect):
    message = app.character_creation_state.get("message")

    if not message:
        return

    text = app.small_font.render(message, True, TEXT_DISABLED)
    app.screen.blit(
        text,
        (
            panel_rect.x + (panel_rect.width - text.get_width()) // 2,
            panel_rect.bottom - 104,
        ),
    )
