import pygame

GODOT_BG = (30, 34, 38)
GODOT_PANEL = (38, 42, 48)
GODOT_FIELD = (45, 50, 58)
GODOT_BORDER = (90, 96, 108)
GODOT_BORDER_ACTIVE = (120, 170, 210)
GODOT_TEXT = (232, 232, 232)
GODOT_MUTED = (158, 166, 178)
GODOT_ACCENT = (80, 130, 160)
GODOT_WARNING = (220, 170, 80)
GODOT_ERROR = (220, 90, 90)
GODOT_DANGER = (180, 70, 70)


def get_inspector_font(size=13, bold=False):
    return pygame.font.SysFont("consolas", size, bold=bold)


def get_font(size=13, bold=False):
    return get_inspector_font(size, bold)


def draw_text(screen, text, x, y, color=GODOT_TEXT, size=13, bold=False):
    font = get_inspector_font(size, bold)
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))
    return surface.get_width(), surface.get_height()


def draw_property_row_bg(screen, rect):
    pygame.draw.rect(screen, GODOT_FIELD, rect, border_radius=4)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=4)


def draw_tooltip(screen, text, mouse_pos):
    font = get_inspector_font(12)
    padding = 8
    surface = font.render(str(text), True, GODOT_TEXT)

    rect = pygame.Rect(
        mouse_pos[0] + 14,
        mouse_pos[1] + 14,
        surface.get_width() + padding * 2,
        surface.get_height() + padding * 2,
    )

    pygame.draw.rect(screen, GODOT_PANEL, rect, border_radius=4)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=4)
    screen.blit(surface, (rect.x + padding, rect.y + padding))


def draw_inspector_panel(screen, rect, title="Inspector"):
    pygame.draw.rect(screen, GODOT_PANEL, rect, border_radius=6)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=6)

    draw_text(screen, title, rect.x + 12, rect.y + 10, GODOT_TEXT, 15, True)

    return rect.y + 42