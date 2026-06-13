import pygame

from game.combat.ui.combat_layout import UNIT_POSITIONS
from game.combat.ui.pixel_icons import draw_large_pixel_icon
from game.combat.combat_status import get_status_definition


ALLY_PANEL = (235, 240, 224)
ENEMY_PANEL = (240, 224, 218)
BAR_BG = (55, 55, 55)
BAR_HP = (172, 58, 58)
BAR_HP_LOW = (190, 105, 50)
BAR_HP_GOOD = (75, 145, 92)
BAR_READY = (70, 135, 210)


def draw_units(app, combat):
    draw_unit(app, combat["player"], "player", "player", False, combat)

    creatures = combat["creatures"]

    if len(creatures) > 0:
        draw_unit(app, creatures[0], "rock_turtle", "creature_0", False, combat)

    if len(creatures) > 1:
        draw_unit(app, creatures[1], "fire_worm", "creature_1", False, combat)

    for enemy in combat["enemies"]:
        if enemy.get("hidden", False):
            continue

        draw_unit(app, enemy, "farm_slime", enemy["unit_id"], True, combat)


def draw_unit(app, actor, actor_type, unit_id, enemy_side, combat):
    base_x, base_y = UNIT_POSITIONS[unit_id]
    x_offset, y_offset = get_animation_offset(unit_id, combat)

    x = base_x + x_offset
    y = base_y + y_offset

    if should_skip_dead_flash(actor):
        return

    panel_color = ALLY_PANEL

    if enemy_side:
        panel_color = ENEMY_PANEL

    if actor["hp"] <= 0:
        panel_color = (170, 160, 145)

    radius = 44
    pending_action = combat["ui"].get("pending_action")
    targetable = False

    if pending_action is not None:
        if actor["team"] == "enemy" and actor["hp"] > 0:
            targetable = True

    if targetable:
        target_rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

        combat["ui"]["target_buttons"].append(
            {
                "rect": target_rect,
                "target_id": actor["unit_id"],
                "enabled": True,
            }
        )

        pygame.draw.circle(app.screen, (255, 235, 120), (x, y), radius + 20)
    active_unit_id = combat.get("active_unit_id")
    is_active = active_unit_id == unit_id

    if is_active:
        pygame.draw.circle(app.screen, (120, 190, 255), (x, y), radius + 17)

    if combat.get("last_target") == unit_id:
        pygame.draw.circle(app.screen, (255, 210, 120), (x, y), radius + 14)

    if combat.get("last_actor") == unit_id:
        pygame.draw.circle(app.screen, (245, 245, 170), (x, y), radius + 9)

    pygame.draw.circle(app.screen, panel_color, (x, y), radius)
    pygame.draw.circle(app.screen, app.DARK, (x, y), radius, 3)

    draw_large_pixel_icon(app, actor_type, x - 27, y - 27)
    draw_unit_panel(app, actor, x - 88, y + 56, panel_color)

    if actor.get("last_damage", 0) > 0:
        app.draw_text(f"-{actor['last_damage']}", x + 34, y - 58, app.WARN, app.big_font)

    if actor.get("last_missed", False):
        app.draw_text("MISS", x + 22, y - 58, app.WARN, app.big_font)


def should_skip_dead_flash(actor):
    if actor["hp"] > 0:
        return False

    death_timer = actor.get("death_timer", 0)

    if death_timer <= 0:
        return False

    blink_frame = int(death_timer * 20)

    if blink_frame % 2 == 0:
        return True

    return False


def draw_unit_panel(app, actor, x, y, panel_color):
    pygame.draw.rect(app.screen, panel_color, (x, y, 176, 64), border_radius=8)
    pygame.draw.rect(app.screen, app.DARK, (x, y, 176, 64), 2, border_radius=8)

    app.draw_text(actor["name"], x + 8, y + 6, app.DARK, app.small_font)
    app.draw_text(f"{actor['hp']}/{actor['max_hp']}", x + 8, y + 24, app.DARK, app.small_font)

    draw_bar(app, x + 68, y + 27, 94, 10, actor["display_hp"], actor["max_hp"], "hp")
    draw_bar(app, x + 68, y + 43, 94, 8, actor["action_charge"], actor["action_max"], "ready")

    draw_status_icons(app, actor, x + 8, y + 42)


def draw_bar(app, x, y, width, height, value, max_value, bar_type):
    if value < 0:
        value = 0

    percent = 0

    if max_value > 0:
        percent = value / max_value

    if percent > 1:
        percent = 1

    filled_width = int(width * percent)

    color = BAR_READY

    if bar_type == "hp":
        color = BAR_HP_GOOD

        if percent <= 0.5:
            color = BAR_HP

        if percent <= 0.25:
            color = BAR_HP_LOW

    pygame.draw.rect(app.screen, BAR_BG, (x, y, width, height), border_radius=4)
    pygame.draw.rect(app.screen, color, (x, y, filled_width, height), border_radius=4)
    pygame.draw.rect(app.screen, app.DARK, (x, y, width, height), 1, border_radius=4)


def draw_status_icons(app, actor, x, y):
    current_x = x

    if actor.get("guarding", False):
        pygame.draw.circle(app.screen, (210, 220, 245), (current_x + 8, y + 8), 8)
        pygame.draw.circle(app.screen, app.DARK, (current_x + 8, y + 8), 8, 1)
        app.draw_text("D", current_x + 4, y, app.DARK, app.small_font)
        current_x += 22

    for status in actor.get("statuses", []):
        status_data = get_status_definition(status["id"])

        if status_data is None:
            continue

        pygame.draw.circle(app.screen, (240, 190, 120), (current_x + 8, y + 8), 9)
        pygame.draw.circle(app.screen, app.DARK, (current_x + 8, y + 8), 9, 1)

        app.draw_text(
            status_data["icon"],
            current_x + 2,
            y,
            app.DARK,
            app.small_font,
        )

        current_x += 26


def get_animation_offset(unit_id, combat):
    x_offset = 0
    y_offset = 0

    if combat["animation_timer"] <= 0:
        return x_offset, y_offset

    progress = combat["animation_timer"] / combat["animation_duration"]

    if combat.get("last_actor") == unit_id:
        direction = 1

        if unit_id.startswith("enemy"):
            direction = -1

        if progress > 0.5:
            x_offset = int(20 * direction)
        else:
            x_offset = int(8 * direction)

    if combat.get("last_target") == unit_id:
        shake = int(progress * 12)

        if shake % 2 == 0:
            x_offset -= 6
        else:
            x_offset += 6

    return x_offset, y_offset