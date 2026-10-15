"""Shared day-and-time panel for all gameplay scenes."""
import pygame
from game.time.time_manager import get_time_text


def draw_clock_widget(app):
    screen = app.screen
    width = 170
    rect = pygame.Rect(screen.get_width() - width - 18, 18, width, 48)
    pygame.draw.rect(screen, (247, 243, 237), rect, border_radius=8)
    pygame.draw.rect(screen, (121, 92, 77), rect, 2, border_radius=8)
    day = app.state.get("day", app.state.get("time", {}).get("day", 1))
    day_label = app.small_font.render(f"DIA {day}", True, (92, 65, 48))
    clock_label = app.font.render(get_time_text(app.state), True, (57, 83, 115))
    screen.blit(day_label, (rect.x + 12, rect.y + 7))
    screen.blit(clock_label, (rect.right - clock_label.get_width() - 12, rect.y + 21))
