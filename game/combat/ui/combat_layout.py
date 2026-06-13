import pygame
from game.ui.ui_components import draw_panel

BOTTOM_PANEL_HEIGHT = 170

_farm_background = None
_farm_background_scaled = None
_farm_background_size = None


UNIT_POSITIONS = {
    "player": (155, 250),
    "creature_0": (310, 195),
    "creature_1": (310, 310),
    "enemy_0": (690, 165),
    "enemy_1": (730, 255),
    "enemy_2": (690, 345),
}


def draw_bottom_panel(app):
    screen = app.screen
    rect = pygame.Rect(
        0,
        screen.get_height() - BOTTOM_PANEL_HEIGHT,
        screen.get_width(),
        BOTTOM_PANEL_HEIGHT,
    )

    draw_panel(
        app.screen,
        rect,
    )


def draw_battlefield_background(app):
    global _farm_background
    global _farm_background_scaled
    global _farm_background_size

    screen = app.screen
    screen.fill((0, 0, 0))

    if _farm_background is None:
        _farm_background = pygame.image.load("assets/combat/farm.png").convert()

    image_width = _farm_background.get_width()
    image_height = _farm_background.get_height()
    scale = screen.get_width() / image_width
    scaled_width = screen.get_width()
    scaled_height = int(image_height * scale)
    scaled_size = (scaled_width, scaled_height)

    if _farm_background_scaled is None or _farm_background_size != scaled_size:
        _farm_background_scaled = pygame.transform.scale(
            _farm_background,
            scaled_size,
        )
        _farm_background_size = scaled_size

    screen.blit(_farm_background_scaled, (0, 0))


def get_actor_by_unit_id(combat, unit_id):
    if combat["player"]["unit_id"] == unit_id:
        return combat["player"]

    for creature in combat["creatures"]:
        if creature["unit_id"] == unit_id:
            return creature

    for enemy in combat["enemies"]:
        if enemy["unit_id"] == unit_id:
            return enemy

    return None
