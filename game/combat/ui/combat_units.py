import pygame

from game.combat.ui.combat_layout import UNIT_POSITIONS
from game.ui.ui_components import draw_progress_bar


BAR_BG = (55, 55, 55)
BAR_HP = (172, 58, 58)
BAR_HP_LOW = (190, 105, 50)
BAR_HP_GOOD = (75, 145, 92)
BAR_READY = (70, 135, 210)
SPRITE_HEIGHT = 128
SPRITE_ASSETS = {
    "player": "assets/combat/player.png",
    "rock_turtle": "assets/combat/tortuga de piedra.png",
    "fire_worm": "assets/combat/gusano de fuego.png",
    "farm_slime": "assets/combat/slime.png",
}

_sprite_cache = {}


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

    sprite = get_combat_sprite(actor_type)
    sprite_rect = sprite.get_rect(midbottom=(x, y + 56))
    pending_action = combat["ui"].get("pending_action")
    targetable = False

    if pending_action is not None:
        if actor["team"] == "enemy" and actor["hp"] > 0:
            targetable = True

    if targetable:
        combat["ui"]["target_buttons"].append(
            {
                "rect": sprite_rect,
                "target_id": actor["unit_id"],
                "enabled": True,
            }
        )

    active_unit_id = combat.get("active_unit_id")
    is_active = active_unit_id == unit_id
    should_dim = should_dim_actor(actor, is_active, combat)

    draw_unit_sprite(app, sprite, sprite_rect, should_dim, is_active, targetable, combat, unit_id)
    draw_unit_bars(app, actor, sprite_rect.centerx - 46, sprite_rect.y - 18)

    if actor.get("last_damage", 0) > 0:
        app.draw_text(
            f"-{actor['last_damage']}",
            sprite_rect.right - 20,
            sprite_rect.y - 28,
            app.WARN,
            app.big_font,
        )

    if actor.get("last_missed", False):
        app.draw_text("MISS", sprite_rect.right - 20, sprite_rect.y - 28, app.WARN, app.big_font)


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


def get_combat_sprite(actor_type):
    if actor_type in _sprite_cache:
        return _sprite_cache[actor_type]

    sprite_path = SPRITE_ASSETS[actor_type]
    image = pygame.image.load(sprite_path).convert()
    image = remove_edge_background(image)
    bounds = image.get_bounding_rect()

    if bounds.width > 0 and bounds.height > 0:
        image = image.subsurface(bounds).copy()

    scale = SPRITE_HEIGHT / image.get_height()
    sprite_width = int(image.get_width() * scale)
    sprite = pygame.transform.smoothscale(image, (sprite_width, SPRITE_HEIGHT))
    _sprite_cache[actor_type] = sprite

    return sprite


def remove_edge_background(image):
    width = image.get_width()
    height = image.get_height()
    rgb_data = pygame.image.tostring(image, "RGB")
    transparent_pixels = get_edge_background_pixels(rgb_data, width, height)
    rgba_data = bytearray(width * height * 4)

    for pixel_index in range(width * height):
        rgb_index = pixel_index * 3
        rgba_index = pixel_index * 4

        rgba_data[rgba_index] = rgb_data[rgb_index]
        rgba_data[rgba_index + 1] = rgb_data[rgb_index + 1]
        rgba_data[rgba_index + 2] = rgb_data[rgb_index + 2]
        rgba_data[rgba_index + 3] = 0 if transparent_pixels[pixel_index] else 255

    return pygame.image.frombuffer(bytes(rgba_data), (width, height), "RGBA").convert_alpha()


def get_edge_background_pixels(rgb_data, width, height):
    total_pixels = width * height
    transparent_pixels = bytearray(total_pixels)
    checked_pixels = bytearray(total_pixels)
    pending_pixels = []

    for x in range(width):
        add_background_pixel(pending_pixels, checked_pixels, rgb_data, width, x)
        add_background_pixel(
            pending_pixels,
            checked_pixels,
            rgb_data,
            width,
            (height - 1) * width + x,
        )

    for y in range(height):
        add_background_pixel(pending_pixels, checked_pixels, rgb_data, width, y * width)
        add_background_pixel(
            pending_pixels,
            checked_pixels,
            rgb_data,
            width,
            y * width + width - 1,
        )

    while pending_pixels:
        pixel_index = pending_pixels.pop()
        transparent_pixels[pixel_index] = 1
        x = pixel_index % width
        y = pixel_index // width

        if x > 0:
            add_background_pixel(
                pending_pixels,
                checked_pixels,
                rgb_data,
                width,
                pixel_index - 1,
            )

        if x < width - 1:
            add_background_pixel(
                pending_pixels,
                checked_pixels,
                rgb_data,
                width,
                pixel_index + 1,
            )

        if y > 0:
            add_background_pixel(
                pending_pixels,
                checked_pixels,
                rgb_data,
                width,
                pixel_index - width,
            )

        if y < height - 1:
            add_background_pixel(
                pending_pixels,
                checked_pixels,
                rgb_data,
                width,
                pixel_index + width,
            )

    return transparent_pixels


def add_background_pixel(pending_pixels, checked_pixels, rgb_data, width, pixel_index):
    if checked_pixels[pixel_index]:
        return

    checked_pixels[pixel_index] = 1

    if is_background_pixel(rgb_data, pixel_index):
        pending_pixels.append(pixel_index)


def is_background_pixel(rgb_data, pixel_index):
    rgb_index = pixel_index * 3
    red = rgb_data[rgb_index]
    green = rgb_data[rgb_index + 1]
    blue = rgb_data[rgb_index + 2]

    if red < 220 or green < 220 or blue < 220:
        return False

    return max(red, green, blue) - min(red, green, blue) <= 14


def should_dim_actor(actor, is_active, combat):
    active_unit_id = combat.get("active_unit_id")

    if active_unit_id is None:
        return False

    active_actor = get_active_actor(combat)

    if active_actor is None:
        return False

    if active_actor["team"] != "player":
        return False

    if actor["team"] != "player":
        return False

    return not is_active


def get_active_actor(combat):
    active_unit_id = combat.get("active_unit_id")

    if combat["player"]["unit_id"] == active_unit_id:
        return combat["player"]

    for creature in combat["creatures"]:
        if creature["unit_id"] == active_unit_id:
            return creature

    for enemy in combat["enemies"]:
        if enemy["unit_id"] == active_unit_id:
            return enemy

    return None


def draw_unit_sprite(app, sprite, rect, should_dim, is_active, targetable, combat, unit_id):
    surface = sprite

    if should_dim or combat.get("last_target") == unit_id:
        surface = sprite.copy()

        if should_dim:
            surface.fill((90, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)

        if combat.get("last_target") == unit_id:
            surface.fill((255, 205, 205, 255), special_flags=pygame.BLEND_RGBA_MULT)

    if is_active and not should_dim and get_active_actor(combat)["team"] == "player":
        outline_rect = rect.inflate(10, 10)
        pygame.draw.rect(app.screen, (255, 235, 120), outline_rect, 2, border_radius=8)

    if targetable:
        outline_rect = rect.inflate(8, 8)
        pygame.draw.rect(app.screen, (255, 235, 120), outline_rect, 2, border_radius=8)

    app.screen.blit(surface, rect)


def draw_unit_bars(app, actor, x, y):
    bar_width = 92

    draw_progress_bar(
        app.screen,
        pygame.Rect(x, y, bar_width, 8),
        actor["display_hp"],
        actor["max_hp"],
        get_hp_bar_color(actor["display_hp"], actor["max_hp"]),
        background_color=BAR_BG,
        border_color=app.DARK,
    )
    draw_progress_bar(
        app.screen,
        pygame.Rect(x, y + 11, bar_width, 6),
        actor["action_charge"],
        actor["action_max"],
        BAR_READY,
        background_color=BAR_BG,
        border_color=app.DARK,
    )


def get_hp_bar_color(value, max_value):
    if value < 0:
        value = 0

    percent = 0

    if max_value > 0:
        percent = value / max_value

    if percent > 1:
        percent = 1

    color = BAR_HP_GOOD

    if percent <= 0.5:
        color = BAR_HP

    if percent <= 0.25:
        color = BAR_HP_LOW

    return color


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
