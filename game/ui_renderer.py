import pygame
from game.time.time_manager import get_time_text, get_calendar_text

PANEL = (238, 230, 204)
DARK = (48, 55, 43)
ACCENT = (119, 146, 88)
WARN = (151, 76, 60)
WHITE = (250, 248, 235)


def draw_text(screen, font, text, x, y, color):
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))


def draw_bar(screen, x, y, w, h, current, maximum, color):
    pygame.draw.rect(screen, WHITE, (x, y, w, h))
    pygame.draw.rect(screen, DARK, (x, y, w, h), 2)

    fill_w = int(w * current / max(1, maximum))

    pygame.draw.rect(
        screen,
        color,
        (x + 2, y + 2, max(0, fill_w - 4), h - 4)
    )


def draw_hud(app):
    pygame.draw.rect(app.screen, PANEL, (0, 0, 960, 72))
    pygame.draw.line(app.screen, DARK, (0, 72), (960, 72), 3)

    health = app.state["health"]
    energy = app.state["energy"]

    draw_text(
        app.screen,
        app.font,
        f"HP {health['current']}/{health['max']}",
        24,
        14,
        DARK,
    )

    draw_bar(
        app.screen,
        24,
        40,
        160,
        14,
        health["current"],
        health["max"],
        WARN,
    )

    draw_text(
        app.screen,
        app.font,
        f"EN {energy['current']}/{energy['max']}",
        220,
        14,
        DARK,
    )

    draw_bar(
        app.screen,
        220,
        40,
        160,
        14,
        energy["current"],
        energy["max"],
        ACCENT,
    )

    draw_text(
        app.screen,
        app.font,
        get_calendar_text(app.state, app.game_data),
        690,
        12,
        DARK,
    )

    draw_text(
        app.screen,
        app.big_font,
        get_time_text(app.state),
        760,
        34,
        DARK,
    )


def draw_log(app):
    x = 710
    y = 120
    width = 220
    height = 260

    pygame.draw.rect(app.screen, PANEL, (x, y, width, height), border_radius=8)
    pygame.draw.rect(app.screen, DARK, (x, y, width, height), 3, border_radius=8)

    draw_text(app.screen, app.big_font, "LOG", x + 20, y + 18, DARK)

    last_messages = app.log[-10:]

    for index, message in enumerate(last_messages):
        draw_text(
            app.screen,
            app.small_font,
            message[:24],
            x + 16,
            y + 60 + index * 18,
            DARK,
        )
