"""HUD visible only during interactive gameplay."""
import pygame
from game.hud.hotbar_widget import draw_hotbar_widget

def draw_play_hud(app):
    if app.phase != "free" or app.journal_open:
        return
    screen = app.screen
    font = app.small_font
    # Life panel: upper left.
    life = pygame.Rect(18, 14, 208, 62)
    pygame.draw.rect(screen, (249, 247, 240), life, border_radius=8)
    pygame.draw.rect(screen, (140, 135, 125), life, 1, border_radius=8)
    screen.blit(font.render("VIDA", True, (65, 65, 65)), (30, 22))
    hp = max(0, min(100, app.hp))
    pygame.draw.rect(screen, (222, 217, 210), (30, 47, 166, 13), border_radius=4)
    if hp:
        pygame.draw.rect(screen, (170, 67, 66), (30, 47, round(166 * hp / 100), 13), border_radius=4)
    screen.blit(font.render(f"{hp}/100", True, (65, 65, 65)), (164, 22))
    # Time panel: upper right.
    time_rect = pygame.Rect(screen.get_width() - 180, 14, 162, 62)
    pygame.draw.rect(screen, (249, 247, 240), time_rect, border_radius=8)
    pygame.draw.rect(screen, (140, 135, 125), time_rect, 1, border_radius=8)
    night = app.time_of_day == "night"
    label = "NOCHE" if night else "DIA"
    symbol = "LUNA" if night else "SOL"
    screen.blit(font.render("TIEMPO", True, (65, 65, 65)), (time_rect.x + 12, 22))
    screen.blit(app.font.render(f"{symbol} / {label}", True, (65, 65, 65)), (time_rect.x + 12, 45))
    # Reuse the existing hotbar component, backed by chapter inventory.
    app.refresh_menu_state()
    draw_hotbar_widget(app)
