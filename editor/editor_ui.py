import pygame


PANEL_WIDTH = 240
BUTTON_HEIGHT = 34
BUTTON_MARGIN = 10


OBJECT_BUTTONS = [
    ("bush", "Bush"),
    ("small_rock", "Small Rock"),
    ("big_rock", "Big Rock"),
    ("tree", "Tree"),
    ("house", "House"),
]


def draw_button(screen, rect, label, active=False):
    font = pygame.font.SysFont(None, 24)

    color = (80, 80, 80)
    if active:
        color = (120, 170, 120)

    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (180, 180, 180), rect, 1)

    text = font.render(label, True, (255, 255, 255))
    screen.blit(text, (rect.x + 10, rect.y + 8))


def draw_editor_panel(screen, mode, selected_object_type, zoom):
    screen_width = screen.get_width()
    panel_x = screen_width - PANEL_WIDTH

    pygame.draw.rect(
        screen,
        (35, 35, 35),
        (panel_x, 0, PANEL_WIDTH, screen.get_height()),
    )

    font = pygame.font.SysFont(None, 24)

    buttons = []

    y = 15

    title = font.render("Editor", True, (240, 240, 240))
    screen.blit(title, (panel_x + BUTTON_MARGIN, y))
    y += 40

    objects_rect = pygame.Rect(panel_x + BUTTON_MARGIN, y, 100, BUTTON_HEIGHT)
    collisions_rect = pygame.Rect(panel_x + 120, y, 105, BUTTON_HEIGHT)

    draw_button(screen, objects_rect, "Objects", mode == "objects")
    draw_button(screen, collisions_rect, "Collision", mode == "collisions")

    buttons.append({"rect": objects_rect, "action": "mode_objects"})
    buttons.append({"rect": collisions_rect, "action": "mode_collisions"})

    y += BUTTON_HEIGHT + 18

    section = font.render("Object", True, (220, 220, 220))
    screen.blit(section, (panel_x + BUTTON_MARGIN, y))
    y += 32

    for object_type, label in OBJECT_BUTTONS:
        rect = pygame.Rect(
            panel_x + BUTTON_MARGIN,
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

        y += BUTTON_HEIGHT + BUTTON_MARGIN

    y += 12

    zoom_title = font.render(f"Zoom: {zoom:.1f}x", True, (220, 220, 220))
    screen.blit(zoom_title, (panel_x + BUTTON_MARGIN, y))
    y += 32

    minus_rect = pygame.Rect(panel_x + BUTTON_MARGIN, y, 60, BUTTON_HEIGHT)
    plus_rect = pygame.Rect(panel_x + 80, y, 60, BUTTON_HEIGHT)

    draw_button(screen, minus_rect, "-")
    draw_button(screen, plus_rect, "+")

    buttons.append({"rect": minus_rect, "action": "zoom_out"})
    buttons.append({"rect": plus_rect, "action": "zoom_in"})

    return buttons


def get_clicked_panel_action(mouse_pos, buttons):
    for button in buttons:
        if button["rect"].collidepoint(mouse_pos):
            return button

    return None