import pygame


GODOT_BG = (32, 34, 39)
GODOT_PANEL = (38, 41, 48)
GODOT_FIELD = (28, 30, 35)
GODOT_BORDER = (72, 78, 88)
GODOT_BORDER_ACTIVE = (115, 157, 220)
GODOT_TEXT = (218, 222, 228)
GODOT_MUTED = (148, 154, 164)
GODOT_SECTION = (45, 49, 57)
GODOT_ACCENT = (86, 145, 214)
GODOT_DANGER = (189, 82, 82)


def get_inspector_font(size=13, bold=False):
    return pygame.font.SysFont("segoeui", size, bold=bold)


def draw_text(screen, text, x, y, color=GODOT_TEXT, size=13, bold=False):
    font = get_inspector_font(size, bold)
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))
    return surface.get_rect(topleft=(x, y))


def draw_inspector_panel(screen, rect, title="Inspector"):
    pygame.draw.rect(screen, GODOT_BG, rect, border_radius=3)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=3)
    draw_text(screen, title, rect.x + 10, rect.y + 8, GODOT_TEXT, 13, True)
    pygame.draw.line(
        screen,
        GODOT_BORDER,
        (rect.x, rect.y + 32),
        (rect.right, rect.y + 32),
    )
    return rect.y + 40


def draw_property_row_bg(screen, rect):
    pygame.draw.rect(screen, GODOT_PANEL, rect)
    pygame.draw.line(screen, (48, 52, 60), rect.bottomleft, rect.bottomright)


def draw_tooltip(screen, text, pos):
    font = get_inspector_font(12)
    surface = font.render(str(text), True, GODOT_TEXT)
    rect = surface.get_rect()
    rect.topleft = (pos[0] + 14, pos[1] + 14)
    rect.inflate_ip(14, 8)
    pygame.draw.rect(screen, (20, 22, 26), rect, border_radius=3)
    pygame.draw.rect(screen, GODOT_BORDER, rect, 1, border_radius=3)
    screen.blit(surface, (rect.x + 7, rect.y + 4))
