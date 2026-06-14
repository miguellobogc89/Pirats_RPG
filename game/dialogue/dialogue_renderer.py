import pygame

from game.dialogue.dialogue_manager import (
    draw_current_dialogue_text,
    get_dialogue_state,
    is_dialogue_active,
)
from game.ui.sprite_renderer import draw_sprite_centered
from game.ui.ui_components import (
    PARCHMENT_LIGHT,
    TEXT_DARK,
    TEXT_DISABLED,
    WOOD_DARK,
    WOOD_MID,
    draw_panel,
)


DIALOGUE_MARGIN = 34
DIALOGUE_HEIGHT = 132
PORTRAIT_SIZE = 112
PANEL_GAP = 10
PADDING_X = 26
PADDING_Y = 22


def draw_dialogue(app):
    if not is_dialogue_active(app):
        return

    portrait_rect = pygame.Rect(
        DIALOGUE_MARGIN,
        app.screen.get_height() - DIALOGUE_HEIGHT - DIALOGUE_MARGIN,
        PORTRAIT_SIZE,
        DIALOGUE_HEIGHT,
    )
    rect = pygame.Rect(
        portrait_rect.right + PANEL_GAP,
        portrait_rect.y,
        app.screen.get_width() - DIALOGUE_MARGIN * 2,
        DIALOGUE_HEIGHT,
    )
    rect.width -= PORTRAIT_SIZE + PANEL_GAP
    draw_portrait_box(app, portrait_rect)
    draw_panel(app.screen, rect)

    dialogue_state = get_dialogue_state(app) or {}
    speaker_name = dialogue_state.get("speaker_name")
    text_rect = pygame.Rect(
        rect.x + PADDING_X,
        rect.y + PADDING_Y,
        rect.width - PADDING_X * 2,
        rect.height - PADDING_Y * 2,
    )
    y = text_rect.y

    if speaker_name:
        speaker_surface = app.font.render(str(speaker_name), True, WOOD_DARK)
        app.screen.blit(speaker_surface, (text_rect.x, y))
        pygame.draw.line(
            app.screen,
            WOOD_MID,
            (text_rect.x, y + speaker_surface.get_height() + 4),
            (text_rect.x + speaker_surface.get_width() + 28, y + speaker_surface.get_height() + 4),
            2,
        )
        y += speaker_surface.get_height() + 14

    lines = wrap_text(draw_current_dialogue_text(app), app.font, text_rect.width)

    for line in lines[:3]:
        text_surface = app.font.render(line, True, TEXT_DARK)
        app.screen.blit(text_surface, (text_rect.x, y))
        y += app.font.get_height() + 4

    hint = app.small_font.render("E / Enter", True, TEXT_DISABLED)
    app.screen.blit(
        hint,
        (
            rect.right - hint.get_width() - 18,
            rect.bottom - hint.get_height() - 12,
        ),
    )


def draw_portrait_box(app, rect):
    draw_panel(app.screen, rect)
    inner_rect = pygame.Rect(rect.x + 12, rect.y + 12, rect.width - 24, rect.height - 24)
    pygame.draw.rect(
        app.screen,
        PARCHMENT_LIGHT,
        inner_rect,
        border_radius=6,
    )
    pygame.draw.rect(
        app.screen,
        WOOD_MID,
        inner_rect,
        2,
        border_radius=6,
    )

    dialogue_state = get_dialogue_state(app) or {}
    portrait_path = dialogue_state.get("portrait_path")

    if portrait_path:
        sprite_rect = draw_sprite_centered(
            app.screen,
            portrait_path,
            inner_rect.centerx,
            inner_rect.centery,
            inner_rect.width - 10,
            inner_rect.height - 10,
        )

        if sprite_rect is not None:
            return

    placeholder = app.big_font.render("?", True, TEXT_DISABLED)
    app.screen.blit(
        placeholder,
        (
            inner_rect.centerx - placeholder.get_width() // 2,
            inner_rect.centery - placeholder.get_height() // 2,
        ),
    )


def wrap_text(text, font, max_width):
    words = str(text).split()

    if not words:
        return [""]

    lines = []
    current_line = ""

    for word in words:
        candidate = word if current_line == "" else f"{current_line} {word}"

        if font.size(candidate)[0] <= max_width:
            current_line = candidate
            continue

        if current_line:
            lines.append(current_line)

        current_line = word

    if current_line:
        lines.append(current_line)

    return lines
