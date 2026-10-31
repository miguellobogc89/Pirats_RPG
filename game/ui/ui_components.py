import pygame

from game.ui.ui_theme import (
    BORDER_RADIUS_SMALL,
)


from game.ui.retro import INK, LINE, PAPER, SHADE, draw_frame

# Paleta en grises de alto contraste, estilo Game Boy.
WOOD_DARK = INK
WOOD_MID = LINE
WOOD_LIGHT = SHADE

PARCHMENT = PAPER
PARCHMENT_LIGHT = SHADE
PARCHMENT_DISABLED = (224, 224, 224)

TEXT_DARK = INK
TEXT_LIGHT = PAPER
TEXT_DISABLED = (150, 150, 150)

BAR_BACKGROUND = PAPER


def draw_text(screen, font, text, x, y, color):
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))


def draw_panel(screen, rect):
    draw_frame(screen, rect)


def get_content_panel_rect(content_rect, padding=12):
    return pygame.Rect(
        content_rect.x - padding,
        content_rect.y - padding,
        content_rect.width + padding * 2,
        content_rect.height + padding * 2,
    )


def draw_content_panel(screen, content_rect, padding=12):
    panel_rect = get_content_panel_rect(content_rect, padding)
    draw_panel(screen, panel_rect)

    return pygame.Rect(
        panel_rect.x + padding,
        panel_rect.y + padding,
        panel_rect.width - padding * 2,
        panel_rect.height - padding * 2,
    )


def draw_window(screen, rect, title, font, title_font):
    draw_panel(screen, rect)

    header_rect = pygame.Rect(
        rect.x + 8,
        rect.y + 8,
        rect.width - 16,
        36,
    )

    # Cabecera invertida (fondo oscuro, texto claro).
    pygame.draw.rect(screen, INK, header_rect)

    title_surface = title_font.render(str(title), False, TEXT_LIGHT)
    screen.blit(
        title_surface,
        (header_rect.x + 10, header_rect.y + (header_rect.height - title_surface.get_height()) // 2),
    )


def draw_button(screen, rect, enabled=True, pressed=False):
    color = PARCHMENT_DISABLED if not enabled else (PARCHMENT if not pressed else PARCHMENT_LIGHT)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, INK if enabled else TEXT_DISABLED, rect, 2)


def draw_button_text(screen, font, text, rect, enabled=True):
    color = TEXT_DARK

    if not enabled:
        color = TEXT_DISABLED

    surface = font.render(str(text), True, color)

    x = rect.x + (rect.width - surface.get_width()) // 2
    y = rect.y + (rect.height - surface.get_height()) // 2

    screen.blit(surface, (x, y))


def draw_labeled_button(screen, font, rect, text, enabled=True, pressed=False):
    draw_button(screen, rect, enabled, pressed)
    draw_button_text(screen, font, text, rect, enabled)


def draw_label_value(
    screen,
    font,
    label,
    value,
    x,
    y,
    label_color=TEXT_DISABLED,
    value_color=TEXT_DARK,
):
    label_surface = font.render(str(label), True, label_color)
    screen.blit(label_surface, (x, y))

    value_surface = font.render(str(value), True, value_color)
    screen.blit(
        value_surface,
        (
            x + label_surface.get_width() + 6,
            y,
        ),
    )


def draw_progress_bar(
    screen,
    rect,
    value,
    max_value,
    fill_color,
    background_color=BAR_BACKGROUND,
    border_color=WOOD_DARK,
):
    percent = 0

    if max_value > 0:
        percent = value / max_value

    if percent < 0:
        percent = 0

    if percent > 1:
        percent = 1

    fill_width = int(rect.width * percent)

    pygame.draw.rect(
        screen,
        background_color,
        rect,
        border_radius=0,
    )

    fill_rect = pygame.Rect(
        rect.x,
        rect.y,
        fill_width,
        rect.height,
    )

    pygame.draw.rect(
        screen,
        fill_color,
        fill_rect,
        border_radius=0,
    )

    pygame.draw.rect(
        screen,
        border_color,
        rect,
        1,
        border_radius=0,
    )


def draw_scrollbar(
    screen,
    rect,
    total_items,
    visible_items,
    first_visible_index,
    track_color=BAR_BACKGROUND,
    thumb_color=WOOD_MID,
    border_color=WOOD_DARK,
):
    if total_items <= visible_items:
        return

    pygame.draw.rect(
        screen,
        track_color,
        rect,
        border_radius=0,
    )

    max_first_index = total_items - visible_items
    thumb_height = int(rect.height * (visible_items / total_items))

    if thumb_height < 14:
        thumb_height = 14

    available_height = rect.height - thumb_height
    thumb_y = rect.y

    if max_first_index > 0:
        thumb_y += int(available_height * (first_visible_index / max_first_index))

    thumb_rect = pygame.Rect(
        rect.x,
        thumb_y,
        rect.width,
        thumb_height,
    )

    pygame.draw.rect(
        screen,
        thumb_color,
        thumb_rect,
        border_radius=0,
    )

    pygame.draw.rect(
        screen,
        border_color,
        rect,
        1,
        border_radius=0,
    )


def draw_dialog_box(screen, rect, title, body, font, title_font):
    draw_window(screen, rect, title, font, title_font)

    body_x = rect.x + 20
    body_y = rect.y + 58

    for line in body:
        draw_text(
            screen,
            font,
            line,
            body_x,
            body_y,
            TEXT_DARK,
        )

        body_y += 22


def draw_dropdown(screen, rect, text, font, enabled=True):
    draw_button(screen, rect, enabled)

    draw_text(
        screen,
        font,
        text,
        rect.x + 10,
        rect.y + 8,
        TEXT_DARK,
    )

    draw_text(
        screen,
        font,
        "v",
        rect.right - 22,
        rect.y + 8,
        TEXT_DARK,
    )


def draw_list_box(screen, rect):
    draw_panel(screen, rect)


def draw_tab(screen, rect, text, font, selected=False):
    fill = PARCHMENT

    if selected:
        fill = PARCHMENT_LIGHT

    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_top_left_radius=BORDER_RADIUS_SMALL,
        border_top_right_radius=BORDER_RADIUS_SMALL,
    )

    pygame.draw.rect(
        screen,
        WOOD_DARK,
        rect,
        2,
        border_top_left_radius=BORDER_RADIUS_SMALL,
        border_top_right_radius=BORDER_RADIUS_SMALL,
    )

    if selected:
        pygame.draw.line(
            screen,
            fill,
            (rect.x + 2, rect.bottom - 1),
            (rect.right - 2, rect.bottom - 1),
            2,
        )

    draw_button_text(
        screen,
        font,
        text,
        rect,
        True,
    )


def get_tab_rects(tabs, labels, font, x, y, height=34, padding_x=14, gap=4):
    rects = {}
    current_x = x

    for tab in tabs:
        label = labels.get(tab, tab)
        width = font.size(label)[0] + padding_x * 2
        rects[tab] = pygame.Rect(current_x, y, width, height)
        current_x += width + gap

    return rects


def draw_tab_bar(screen, tabs, labels, selected_tab, font, x, y):
    rects = get_tab_rects(tabs, labels, font, x, y)

    for tab in tabs:
        draw_tab(
            screen,
            rects[tab],
            labels.get(tab, tab),
            font,
            tab == selected_tab,
        )

    return rects
