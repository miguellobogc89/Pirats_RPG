import pygame

from game.ui.ui_components import draw_scrollbar


LOG_RECT = pygame.Rect(570, 490, 366, 126)
LOG_CONTENT_RECT = pygame.Rect(590, 522, 310, 76)
LOG_VISIBLE_MESSAGES = 4


def draw_log(app, combat):
    title = "REGISTRO"

    if combat.get("combat_result") == "victory":
        title = "VICTORIA"

    if combat.get("combat_result") == "defeat":
        title = "DERROTA"

    app.draw_text(title, LOG_RECT.x + 20, LOG_RECT.y, app.DARK, app.font)

    visible_messages, first_visible_index = get_visible_log_messages(combat)

    previous_clip = app.screen.get_clip()
    app.screen.set_clip(LOG_CONTENT_RECT)

    log_y = LOG_CONTENT_RECT.y

    for message in visible_messages:
        app.draw_text(message, LOG_CONTENT_RECT.x, log_y, app.DARK, app.small_font)
        log_y += 20

    app.screen.set_clip(previous_clip)

    draw_scrollbar(
        app.screen,
        pygame.Rect(918, LOG_CONTENT_RECT.y, 8, LOG_CONTENT_RECT.height),
        len(combat["log"]),
        LOG_VISIBLE_MESSAGES,
        first_visible_index,
        border_color=app.DARK,
    )

    if combat.get("combat_result") is not None:
        app.draw_text("Saliendo del combate...", 728, 608, app.DARK, app.small_font)
    else:
        app.draw_text("ESC salir", 860, 608, app.DARK, app.small_font)


def get_visible_log_messages(combat):
    messages = combat["log"]
    total_messages = len(messages)
    max_first_index = total_messages - LOG_VISIBLE_MESSAGES

    if max_first_index < 0:
        max_first_index = 0

    scroll_offset = combat["ui"].get("log_scroll_offset", 0)

    if scroll_offset < 0:
        scroll_offset = 0

    if scroll_offset > max_first_index:
        scroll_offset = max_first_index

    combat["ui"]["log_scroll_offset"] = scroll_offset

    first_visible_index = max_first_index - scroll_offset
    last_visible_index = first_visible_index + LOG_VISIBLE_MESSAGES

    return messages[first_visible_index:last_visible_index], first_visible_index
