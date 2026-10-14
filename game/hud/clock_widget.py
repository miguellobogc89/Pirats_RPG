"""In-game clock in the upper-right corner."""
from game.time.time_manager import get_time_text

def draw_clock_widget(app):
    time_text = get_time_text(app.state)
    width = app.screen.get_width()
    label = app.small_font.render(time_text, True, (65, 65, 65))
    app.screen.blit(label, (width - label.get_width() - 20, 20))
