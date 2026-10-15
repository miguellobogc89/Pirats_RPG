import pygame

from game.notifications.notification_manager import get_notifications
from game.ui.ui_components import (
    TEXT_DARK,
    TEXT_LIGHT,
    WOOD_DARK,
    WOOD_MID,
    draw_panel,
)


CORNER_WIDTH = 330
CORNER_HEIGHT = 44
LOOT_WIDTH = 190
LOOT_HEIGHT = 34
CENTER_WIDTH = 520
CENTER_HEIGHT = 82
PADDING = 14
GAP = 8


def draw_notifications(app):
    notifications = get_notifications(app)

    if not notifications:
        return

    draw_corner_notifications(app, notifications)
    draw_loot_notifications(app, notifications)
    draw_center_notifications(app, notifications)


def draw_corner_notifications(app, notifications):
    corner_notifications = [
        notification
        for notification in notifications
        if notification["type"] == "corner"
    ]
    x = app.screen.get_width() - CORNER_WIDTH - 18
    y = 18

    for notification in reversed(corner_notifications):
        rect = pygame.Rect(x, y, CORNER_WIDTH, CORNER_HEIGHT)
        draw_notification_box(app, rect, notification, app.small_font)
        y += CORNER_HEIGHT + GAP


def draw_loot_notifications(app, notifications):
    from game.data.item_database import get_item_data
    from game.ui.sprite_renderer import draw_item_sprite
    entries = [n for n in notifications if n["type"] == "loot"]
    x = app.screen.get_width() - 98
    y = app.screen.get_height() - 100
    for n in reversed(entries):
        rect = pygame.Rect(x, y, 78, 46)
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        draw_panel(surface, surface.get_rect())
        data = get_item_data(n["item_id"]) if n.get("item_id") else None
        icon_rect = pygame.Rect(7, 6, 34, 34)
        if not data or draw_item_sprite(surface, data, icon_rect, padding=2) is None:
            pygame.draw.rect(surface, WOOD_MID, icon_rect, border_radius=4)
            glyph = app.small_font.render((data or {}).get("icon", "?"), True, TEXT_LIGHT)
            surface.blit(glyph, glyph.get_rect(center=icon_rect.center))
        count = app.small_font.render("x" + str(n.get("amount", 1)), True, TEXT_DARK)
        surface.blit(count, (45, (rect.height - count.get_height()) // 2))
        surface.set_alpha(get_notification_alpha(n))
        app.screen.blit(surface, rect.topleft)
        y -= 52


def important_panel_rect(screen):
    return pygame.Rect((screen.get_width() - 520) // 2,
                       (screen.get_height() - 194) // 2, 520, 194)


def important_button_rect(screen):
    panel = important_panel_rect(screen)
    return pygame.Rect(panel.centerx - 72, panel.bottom - 53, 144, 36)


def draw_center_notifications(app, notifications):
    important = next((n for n in notifications if n["type"] == "center"), None)
    if important is None:
        return
    veil = pygame.Surface(app.screen.get_size(), pygame.SRCALPHA)
    veil.fill((20, 18, 15, 130))
    app.screen.blit(veil, (0, 0))
    rect = important_panel_rect(app.screen)
    draw_panel(app.screen, rect)
    title = app.font.render(important.get("title") or "Aviso importante", True, TEXT_DARK)
    app.screen.blit(title, title.get_rect(center=(rect.centerx, rect.top + 34)))
    lines = wrap_text(important["message"], app.small_font, rect.width - 44, max_lines=3)
    for i, line in enumerate(lines):
        line_surf = app.small_font.render(line, True, TEXT_DARK)
        app.screen.blit(line_surf, line_surf.get_rect(center=(rect.centerx, rect.top + 75 + i * 23)))
    button = important_button_rect(app.screen)
    pygame.draw.rect(app.screen, WOOD_DARK, button, border_radius=5)
    label = app.font.render("Aceptar", True, TEXT_LIGHT)
    app.screen.blit(label, label.get_rect(center=button.center))


def draw_notification_box(app, rect, notification, font, compact=False, centered=False):
    surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    alpha = get_notification_alpha(notification)
    surface.set_alpha(alpha)

    local_rect = pygame.Rect(0, 0, rect.width, rect.height)
    draw_panel(surface, local_rect)

    if compact:
        pygame.draw.rect(
            surface,
            WOOD_MID,
            pygame.Rect(8, 8, 4, rect.height - 16),
            border_radius=2,
        )

    text_color = TEXT_DARK

    if centered:
        text_color = TEXT_LIGHT
        pygame.draw.rect(surface, WOOD_DARK, local_rect, 3, border_radius=10)

    draw_notification_text(
        surface,
        notification["message"],
        font,
        text_color,
        local_rect,
        centered,
    )
    app.screen.blit(surface, rect.topleft)


def get_notification_alpha(notification):
    time_left = notification["time_left"]
    duration = notification["duration"]

    if duration <= 0:
        return 255

    if time_left > 0.5:
        return 255

    return max(0, min(255, int(255 * (time_left / 0.5))))


def draw_notification_text(surface, message, font, color, rect, centered):
    max_width = rect.width - PADDING * 2
    lines = wrap_text(message, font, max_width, max_lines=2)
    total_height = len(lines) * font.get_height()

    if centered:
        y = rect.y + (rect.height - total_height) // 2
    else:
        y = rect.y + (rect.height - total_height) // 2

    for line in lines:
        text_surface = font.render(line, True, color)

        if centered:
            x = rect.x + (rect.width - text_surface.get_width()) // 2
        else:
            x = rect.x + PADDING

        surface.blit(text_surface, (x, y))
        y += font.get_height()


def wrap_text(text, font, max_width, max_lines=2):
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

        if len(lines) >= max_lines:
            break

    if len(lines) < max_lines and current_line:
        lines.append(current_line)

    if len(lines) > max_lines:
        lines = lines[:max_lines]

    if lines and font.size(lines[-1])[0] > max_width:
        lines[-1] = truncate_text(lines[-1], font, max_width)

    if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = truncate_text(lines[-1], font, max_width)

    return lines


def truncate_text(text, font, max_width):
    ellipsis = "..."
    truncated = text

    while truncated and font.size(truncated + ellipsis)[0] > max_width:
        truncated = truncated[:-1]

    return truncated + ellipsis if truncated else ellipsis
