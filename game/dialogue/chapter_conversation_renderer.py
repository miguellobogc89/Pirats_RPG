"""Pygame presentation of conversations; story text stays in JSON.

Cuadro de dialogo al estilo Game Boy: marco doble, texto pixelado,
cursor de seleccion y flecha que parpadea al final.
"""
import pygame

from game.ui.retro import INK, LINE, draw_cursor, draw_frame, draw_more_arrow

BOX_MARGIN = 24
BOX_HEIGHT = 150
TEXT_PADDING_X = 30
TEXT_PADDING_TOP = 30
LINE_HEIGHT = 28
MAX_LINES = 3


def wrap_lines(text, font, max_width):
    lines, line = [], ""
    for word in str(text).split():
        trial = (line + " " + word).strip()
        if font.size(trial)[0] > max_width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def draw_chapter_conversation(scene, speaker, message, choices=None, selected=0):
    from game.scenes.brumazul_scene import WIDTH, HEIGHT
    app = scene.app
    s = app.screen
    text_font = getattr(app, "dialogue_font", app.small_font)
    rect = pygame.Rect(BOX_MARGIN, HEIGHT - BOX_HEIGHT - BOX_MARGIN, WIDTH - BOX_MARGIN * 2, BOX_HEIGHT)
    draw_frame(s, rect)

    # Nombre de quien habla en una pestaña sobre el cuadro.
    if speaker:
        name = app.font.render(str(speaker), False, INK)
        tab = pygame.Rect(rect.x + 18, rect.y - name.get_height() - 14, name.get_width() + 28, name.get_height() + 18)
        draw_frame(s, tab)
        s.blit(name, (tab.x + 14, tab.y + 9))

    x = rect.x + TEXT_PADDING_X
    y = rect.y + TEXT_PADDING_TOP
    if choices:
        for i, choice in enumerate(choices):
            row_y = y + i * LINE_HEIGHT
            if i == selected:
                draw_cursor(s, x - 18, row_y + 3, 11)
            s.blit(text_font.render(str(choice), False, INK), (x, row_y))
        return

    for i, line in enumerate(wrap_lines(message, text_font, rect.width - TEXT_PADDING_X * 2)[:MAX_LINES]):
        s.blit(text_font.render(line, False, INK), (x, y + i * LINE_HEIGHT))

    from game.dialogue.chapter_dialogues import get_chapter_ui_text
    hint = app.small_font.render(get_chapter_ui_text("continue_hint"), False, LINE)
    s.blit(hint, (rect.right - hint.get_width() - 46, rect.bottom - hint.get_height() - 12))
    draw_more_arrow(s, rect.right - 34, rect.bottom - 24)
