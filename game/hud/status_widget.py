import pygame

from game.ui.retro import INK, LINE, draw_frame


def draw_status_widget(app):
    health = app.state.get("health", {})
    current = max(0, health.get("current", 10))
    maximum = max(1, health.get("max", 10))
    screen = app.screen
    x, y, width, height = 18, 18, 210, 48
    draw_frame(screen, (x, y, width, height))
    label = app.small_font.render(f"VIDA  {current}/{maximum}", True, INK)
    screen.blit(label, (x + 12, y + 6))
    # Barra de vida clasica: marco oscuro y relleno solido.
    pygame.draw.rect(screen, INK, (x + 12, y + 28, width - 24, 10), 2)
    filled = round((width - 28) * min(current, maximum) / maximum)
    if filled:
        pygame.draw.rect(screen, LINE, (x + 14, y + 30, filled, 6))
