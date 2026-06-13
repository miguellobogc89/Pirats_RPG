import pygame


BG_PANEL = (236, 226, 196)
INNER_PANEL = (220, 207, 170)
GRASS_1 = (92, 145, 82)
GRASS_2 = (74, 126, 70)


UNIT_POSITIONS = {
    "player": (155, 250),
    "creature_0": (310, 195),
    "creature_1": (310, 310),
    "enemy_0": (690, 165),
    "enemy_1": (730, 255),
    "enemy_2": (690, 345),
}


def draw_overlay(app):
    screen = app.screen

    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 195))
    screen.blit(overlay, (0, 0))


def draw_main_panel(app):
    pygame.draw.rect(app.screen, BG_PANEL, (35, 28, 890, 585), border_radius=16)
    pygame.draw.rect(app.screen, app.DARK, (35, 28, 890, 585), 4, border_radius=16)


def draw_header(app, combat):
    pygame.draw.rect(app.screen, INNER_PANEL, (60, 50, 840, 48), border_radius=10)
    pygame.draw.rect(app.screen, app.DARK, (60, 50, 840, 48), 2, border_radius=10)

    title = "COMBATE"

    if combat.get("combat_result") == "victory":
        title = "VICTORIA"

    if combat.get("combat_result") == "defeat":
        title = "DERROTA"

    app.draw_text(title, 82, 62, app.DARK, app.big_font)

    if combat.get("combat_result") is not None:
        app.draw_text("ENTER / ESPACIO para salir", 350, 68, app.DARK, app.small_font)
        return

    active_unit_id = combat.get("active_unit_id")
    active_text = "Esperando barras..."

    if active_unit_id is not None:
        active_actor = get_actor_by_unit_id(combat, active_unit_id)

        if active_actor is not None:
            active_text = f"Actúa: {active_actor['name']}"

    app.draw_text(active_text, 350, 68, app.DARK, app.small_font)


def draw_battlefield_background(app):
    field_rect = pygame.Rect(60, 115, 840, 335)

    pygame.draw.rect(app.screen, GRASS_1, field_rect, border_radius=14)

    for y in range(125, 440, 18):
        for x in range(70, 890, 36):
            pygame.draw.line(app.screen, GRASS_2, (x, y), (x + 10, y + 6), 2)

    pygame.draw.rect(app.screen, app.DARK, field_rect, 3, border_radius=14)


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