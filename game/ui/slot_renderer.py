import pygame

from game.data.item_database import get_item_data
from game.ui.sprite_renderer import draw_item_sprite
from game.ui.ui_components import (
    PARCHMENT_DISABLED,
    PARCHMENT_LIGHT,
    TEXT_DARK,
    TEXT_DISABLED,
    WOOD_DARK,
    WOOD_LIGHT,
    WOOD_MID,
)
from game.ui.ui_theme import BORDER_RADIUS_SMALL


SLOT_HOVER_BORDER = (218, 173, 77)
SLOT_SELECTED_BORDER = (255, 220, 100)


def draw_slot(
    screen,
    rect,
    stack,
    font,
    small_font=None,
    selected=False,
    hovered=False,
    disabled=False,
    hotkey_label=None,
    fill_color=None,
    selected_fill_color=None,
    border_color=None,
    text_color=None,
    hotkey_position="top",
):
    if small_font is None:
        small_font = font

    amount = 0

    if stack is not None:
        amount = stack.get("amount", 1)

    amount_badge_rect = get_amount_badge_rect(rect, amount, small_font)
    hotkey_visible = should_draw_hotkey(
        rect,
        hotkey_label,
        small_font,
        hotkey_position,
        amount_badge_rect,
    )
    hotkey_rect = None

    if hotkey_visible:
        hotkey_rect = get_hotkey_rect(rect, hotkey_label, small_font, hotkey_position)

    icon_rect = get_icon_rect(rect, hotkey_rect, amount_badge_rect)

    draw_slot_background(
        screen,
        rect,
        selected,
        hovered,
        disabled,
        fill_color=fill_color,
        selected_fill_color=selected_fill_color,
        border_color=border_color,
    )

    if stack is not None:
        draw_slot_item(
            screen,
            icon_rect,
            stack,
            font,
            small_font,
            disabled,
            text_color,
            amount_badge_rect,
        )

    if hotkey_visible:
        draw_slot_hotkey(
            screen,
            hotkey_rect,
            hotkey_label,
            small_font,
            disabled,
            text_color,
        )


def draw_slot_background(
    screen,
    rect,
    selected=False,
    hovered=False,
    disabled=False,
    fill_color=None,
    selected_fill_color=None,
    border_color=None,
):
    base_fill_color = fill_color or PARCHMENT_LIGHT
    selected_color = selected_fill_color or base_fill_color
    current_border_color = border_color or WOOD_DARK
    border_width = 2

    if selected:
        base_fill_color = selected_color
        border_width = 4

    if disabled:
        base_fill_color = PARCHMENT_DISABLED
        current_border_color = WOOD_MID

    if hovered:
        current_border_color = SLOT_HOVER_BORDER
        border_width = 3

    if selected:
        current_border_color = border_color or SLOT_SELECTED_BORDER
        border_width = 4

    pygame.draw.rect(
        screen,
        base_fill_color,
        rect,
        border_radius=BORDER_RADIUS_SMALL,
    )
    pygame.draw.rect(
        screen,
        current_border_color,
        rect,
        border_width,
        border_radius=BORDER_RADIUS_SMALL,
    )


def draw_slot_item(
    screen,
    icon_rect,
    stack,
    font,
    small_font,
    disabled=False,
    text_color=None,
    amount_badge_rect=None,
):
    item_data = get_item_data(stack["item_id"])

    if item_data is None:
        return

    sprite_rect = draw_item_sprite(screen, item_data, icon_rect, padding=2)

    if sprite_rect is None:
        draw_slot_icon(screen, icon_rect, item_data, font, disabled, text_color)

    amount = stack.get("amount", 1)

    if amount > 1:
        draw_slot_amount(
            screen,
            amount_badge_rect,
            amount,
            small_font,
            disabled,
            text_color,
        )


def draw_slot_icon(screen, rect, item_data, font, disabled=False, text_color=None):
    icon = item_data.get("icon", "?")
    color = TEXT_DISABLED if disabled else (text_color or TEXT_DARK)
    surface = font.render(str(icon), True, color)
    x = rect.x + (rect.width - surface.get_width()) // 2
    y = rect.y + (rect.height - surface.get_height()) // 2
    screen.blit(surface, (x, y))


def draw_slot_amount(screen, badge_rect, amount, small_font, disabled=False, text_color=None):
    if badge_rect is None:
        return

    color = TEXT_DISABLED if disabled else (text_color or TEXT_DARK)
    surface = small_font.render(str(amount), True, color)
    badge_padding_x = 4
    badge_padding_y = 1

    pygame.draw.rect(
        screen,
        PARCHMENT_LIGHT,
        badge_rect,
        border_radius=4,
    )
    pygame.draw.rect(
        screen,
        WOOD_DARK,
        badge_rect,
        1,
        border_radius=4,
    )

    x = badge_rect.x + badge_padding_x
    y = badge_rect.y + badge_padding_y
    screen.blit(surface, (x, y))


def draw_slot_hotkey(
    screen,
    hotkey_rect,
    hotkey_label,
    small_font,
    disabled=False,
    text_color=None,
):
    color = TEXT_DISABLED if disabled else (text_color or WOOD_LIGHT)
    surface = small_font.render(str(hotkey_label), True, color)
    screen.blit(surface, hotkey_rect)


def get_icon_rect(rect, hotkey_rect=None, amount_badge_rect=None):
    padding = 8
    icon_rect = pygame.Rect(
        rect.x + padding,
        rect.y + padding,
        rect.width - padding * 2,
        rect.height - padding * 2,
    )

    if hotkey_rect is not None and hotkey_rect.y <= rect.y + rect.height // 2:
        top_reserved = hotkey_rect.height + 3
        icon_rect.y += top_reserved
        icon_rect.height -= top_reserved

    if amount_badge_rect is not None:
        bottom_reserved = amount_badge_rect.height // 2
        icon_rect.height -= bottom_reserved

    if icon_rect.height < 12:
        icon_rect = rect.inflate(-12, -12)

    return icon_rect


def get_amount_badge_rect(rect, amount, small_font):
    if amount <= 1:
        return None

    surface = small_font.render(str(amount), True, TEXT_DARK)
    badge_padding_x = 4
    badge_padding_y = 1
    return pygame.Rect(
        rect.right - surface.get_width() - badge_padding_x * 2 - 4,
        rect.bottom - surface.get_height() - badge_padding_y * 2 - 4,
        surface.get_width() + badge_padding_x * 2,
        surface.get_height() + badge_padding_y * 2,
    )


def get_hotkey_rect(rect, hotkey_label, small_font, hotkey_position):
    surface = small_font.render(str(hotkey_label), True, TEXT_DARK)
    x = rect.x + 5
    y = rect.y + 4

    if hotkey_position == "bottom":
        y = rect.bottom - surface.get_height() - 4

    return pygame.Rect(x, y, surface.get_width(), surface.get_height())


def should_draw_hotkey(rect, hotkey_label, small_font, hotkey_position, amount_badge_rect):
    if hotkey_label is None:
        return False

    if rect.width < 44 or rect.height < 44:
        return False

    hotkey_rect = get_hotkey_rect(rect, hotkey_label, small_font, hotkey_position)

    if amount_badge_rect is not None and hotkey_rect.colliderect(amount_badge_rect):
        return False

    return True
