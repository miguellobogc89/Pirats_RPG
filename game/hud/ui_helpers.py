import pygame

PANEL = (249, 249, 249)
DARK = (125, 125, 125)
ACCENT = (175, 175, 175)
WARN = (155, 155, 155)
WHITE = (253, 253, 253)


def draw_text(screen, font, text, x, y, color):
    surface = font.render(str(text), True, DARK)
    screen.blit(surface, (x, y))


def draw_bar(screen, x, y, w, h, current, maximum, color):
    pygame.draw.rect(screen, WHITE, (x, y, w, h))
    pygame.draw.rect(screen, ACCENT, (x, y, w, h), 1)
    fill_w = max(0, int((w - 2) * current / max(1, maximum)))
    if fill_w:
        pygame.draw.rect(screen, (220, 220, 220), (x + 1, y + 1, fill_w, max(1, h - 2)))
