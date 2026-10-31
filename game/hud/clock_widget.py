"""Shared day-and-time panel for all gameplay scenes."""
import pygame
from game.time.time_manager import get_time_text
from game.ui.retro import INK, draw_frame


def draw_clock_widget(app):
    screen = app.screen
    width = 170
    rect = pygame.Rect(screen.get_width() - width - 18, 18, width, 48)
    draw_frame(screen, rect)
    day = app.state.get("day", app.state.get("time", {}).get("day", 1))
    day_label = app.small_font.render(f"DIA {day}", True, INK)
    clock_label = app.font.render(get_time_text(app.state), True, INK)
    screen.blit(day_label, (rect.x + 12, rect.y + 6))
    screen.blit(clock_label, (rect.right - clock_label.get_width() - 12, rect.y + 21))
