import pygame


def draw_status_widget(app):
    health = app.state.get("health", {})
    current = max(0, health.get("current", 10))
    maximum = max(1, health.get("max", 10))
    screen = app.screen
    x, y, width, height = 18, 18, 210, 48
    pygame.draw.rect(screen, (247, 247, 247), (x, y, width, height), border_radius=8)
    pygame.draw.rect(screen, (130, 130, 130), (x, y, width, height), 2, border_radius=8)
    label = app.small_font.render(f"VIDA  {current}/{maximum}", True, (95, 95, 95))
    screen.blit(label, (x + 12, y + 6))
    pygame.draw.rect(screen, (115, 115, 115), (x + 12, y + 29, width - 24, 11), border_radius=4)
    filled = round((width - 28) * min(current, maximum) / maximum)
    if filled:
        pygame.draw.rect(screen, (180, 180, 180), (x + 14, y + 31, filled, 7), border_radius=3)
