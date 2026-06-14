import pygame


PANEL_WIDTH = 260
TOP_BAR_HEIGHT = 46
STATUS_BAR_HEIGHT = 26

BUTTON_HEIGHT = 30
BUTTON_MARGIN = 8

COLOR_BG = (28, 30, 34)
COLOR_PANEL = (38, 41, 46)
COLOR_PANEL_DARK = (24, 26, 30)
COLOR_BUTTON = (55, 59, 66)
COLOR_BUTTON_HOVER = (68, 73, 82)
COLOR_BUTTON_ACTIVE = (86, 120, 92)
COLOR_BORDER = (95, 100, 110)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_MUTED = (165, 170, 178)
COLOR_ACCENT = (120, 170, 120)


OBJECT_BUTTONS = [
    ("bush", "Bush"),
    ("small_rock", "Small Rock"),
    ("big_rock", "Big Rock"),
    ("tree", "Tree"),
    ("house", "House"),
]
NON_PLACEABLE_OBJECT_TYPES = {"player"}


def draw_text(screen, font, text, x, y, color=COLOR_TEXT):
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))


def draw_button(screen, rect, label, active=False):
    mouse_pos = pygame.mouse.get_pos()

    color = COLOR_BUTTON
    if rect.collidepoint(mouse_pos):
        color = COLOR_BUTTON_HOVER
    if active:
        color = COLOR_BUTTON_ACTIVE

    pygame.draw.rect(screen, color, rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=4)

    font = pygame.font.SysFont("consolas", 15)
    text = font.render(label, True, COLOR_TEXT)

    text_x = rect.x + (rect.width - text.get_width()) // 2
    text_y = rect.y + (rect.height - text.get_height()) // 2

    screen.blit(text, (text_x, text_y))


def draw_top_toolbar(screen, mode, zoom):
    font = pygame.font.SysFont("consolas", 15)

    rect = pygame.Rect(0, 0, screen.get_width(), TOP_BAR_HEIGHT)
    pygame.draw.rect(screen, COLOR_PANEL_DARK, rect)
    pygame.draw.line(screen, COLOR_BORDER, (0, TOP_BAR_HEIGHT), (screen.get_width(), TOP_BAR_HEIGHT))

    buttons = []
    x = 10
    y = 8

    items = [
        ("Guardar", "save"),
        ("Objetos", "mode_objects"),
        ("Colisiones", "mode_collisions"),
        ("-", "zoom_out"),
        (f"{zoom:.1f}x", "none"),
        ("+", "zoom_in"),
    ]

    for label, action in items:
        width = 96
        if label in ["-", "+"]:
            width = 34
        if action == "none":
            width = 62

        button_rect = pygame.Rect(x, y, width, BUTTON_HEIGHT)

        active = False
        if action == "mode_objects" and mode == "objects":
            active = True
        if action == "mode_collisions" and mode == "collisions":
            active = True

        draw_button(screen, button_rect, label, active)

        if action != "none":
            buttons.append({
                "rect": button_rect,
                "action": action,
            })

        x += width + 8

    draw_text(
        screen,
        font,
        "RPG Map Constructor",
        screen.get_width() - PANEL_WIDTH + 14,
        14,
        COLOR_TEXT_MUTED,
    )

    return buttons


def get_object_buttons(object_definitions=None):
    if not object_definitions:
        return OBJECT_BUTTONS

    return [
        (object_type, object_type.replace("_", " ").title())
        for object_type in sorted(object_definitions)
        if object_type not in NON_PLACEABLE_OBJECT_TYPES
    ]


def draw_right_panel(screen, mode, selected_object_type, zoom, object_definitions=None):
    font = pygame.font.SysFont("consolas", 15)
    title_font = pygame.font.SysFont("consolas", 18, bold=True)

    screen_width = screen.get_width()
    panel_x = screen_width - PANEL_WIDTH

    pygame.draw.rect(
        screen,
        COLOR_PANEL,
        (panel_x, TOP_BAR_HEIGHT, PANEL_WIDTH, screen.get_height() - TOP_BAR_HEIGHT - STATUS_BAR_HEIGHT),
    )

    pygame.draw.line(
        screen,
        COLOR_BORDER,
        (panel_x, TOP_BAR_HEIGHT),
        (panel_x, screen.get_height() - STATUS_BAR_HEIGHT),
    )

    buttons = []

    x = panel_x + BUTTON_MARGIN
    y = TOP_BAR_HEIGHT + 14

    draw_text(screen, title_font, "Inspector", x, y)
    y += 34

    draw_text(screen, font, "Modo", x, y, COLOR_TEXT_MUTED)
    y += 24

    objects_rect = pygame.Rect(x, y, 112, BUTTON_HEIGHT)
    collisions_rect = pygame.Rect(x + 120, y, 112, BUTTON_HEIGHT)

    draw_button(screen, objects_rect, "Objects", mode == "objects")
    draw_button(screen, collisions_rect, "Collision", mode == "collisions")

    buttons.append({"rect": objects_rect, "action": "mode_objects"})
    buttons.append({"rect": collisions_rect, "action": "mode_collisions"})

    y += BUTTON_HEIGHT + 22

    draw_text(screen, font, "Object Library", x, y, COLOR_TEXT_MUTED)
    y += 24

    for object_type, label in get_object_buttons(object_definitions):
        rect = pygame.Rect(
            x,
            y,
            PANEL_WIDTH - BUTTON_MARGIN * 2,
            BUTTON_HEIGHT,
        )

        draw_button(
            screen,
            rect,
            label,
            mode == "objects" and object_type == selected_object_type,
        )

        buttons.append({
            "rect": rect,
            "action": "select_object",
            "object_type": object_type,
        })

        y += BUTTON_HEIGHT + 7

    y += 14

    pygame.draw.line(
        screen,
        COLOR_BORDER,
        (x, y),
        (screen_width - BUTTON_MARGIN, y),
    )

    y += 18

    draw_text(screen, font, "Properties", x, y, COLOR_TEXT_MUTED)
    y += 24

    draw_text(screen, font, f"Selected: {selected_object_type}", x, y)
    y += 22

    draw_text(screen, font, f"Zoom: {zoom:.2f}x", x, y)

    return buttons


def draw_status_bar(screen, cell=None, mode=None, selected_object_type=None, zoom=None):
    font = pygame.font.SysFont("consolas", 14)

    y = screen.get_height() - STATUS_BAR_HEIGHT

    pygame.draw.rect(
        screen,
        COLOR_PANEL_DARK,
        (0, y, screen.get_width(), STATUS_BAR_HEIGHT),
    )

    pygame.draw.line(screen, COLOR_BORDER, (0, y), (screen.get_width(), y))

    cell_text = "-"
    if cell is not None:
        cell_text = f"{cell[0]}, {cell[1]}"

    text = f"Cell: {cell_text}   Mode: {mode}   Object: {selected_object_type}   Zoom: {zoom:.2f}x"

    draw_text(screen, font, text, 10, y + 5, COLOR_TEXT_MUTED)


def draw_editor_panel(screen, mode, selected_object_type, zoom, object_definitions=None):
    buttons = []

    buttons.extend(draw_top_toolbar(screen, mode, zoom))
    buttons.extend(draw_right_panel(screen, mode, selected_object_type, zoom, object_definitions))

    return buttons


def get_clicked_panel_action(mouse_pos, buttons):
    for button in buttons:
        if button["rect"].collidepoint(mouse_pos):
            return button

    return None
