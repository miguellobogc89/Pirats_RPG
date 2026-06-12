import pygame

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