import pygame
from pathlib import Path


_sprite_cache = {}
_scaled_sprite_cache = {}
_missing_sprites = set()


def get_sprite(sprite_path):
    if sprite_path in _sprite_cache:
        return _sprite_cache[sprite_path]

    if sprite_path in _missing_sprites:
        return None

    if not Path(sprite_path).exists():
        _missing_sprites.add(sprite_path)
        return None

    try:
        sprite = pygame.image.load(sprite_path).convert_alpha()
    except pygame.error:
        _missing_sprites.add(sprite_path)
        return None

    _sprite_cache[sprite_path] = sprite

    return sprite


def get_scaled_sprite(sprite_path, max_width, max_height):
    cache_key = (sprite_path, max_width, max_height)

    if cache_key in _scaled_sprite_cache:
        return _scaled_sprite_cache[cache_key]

    sprite = get_sprite(sprite_path)

    if sprite is None:
        return None

    scale = min(max_width / sprite.get_width(), max_height / sprite.get_height())
    width = max(1, int(sprite.get_width() * scale))
    height = max(1, int(sprite.get_height() * scale))
    scaled_sprite = pygame.transform.scale(sprite, (width, height))
    _scaled_sprite_cache[cache_key] = scaled_sprite

    return scaled_sprite


def draw_sprite_centered(screen, sprite_path, center_x, center_y, max_width, max_height):
    sprite = get_scaled_sprite(sprite_path, max_width, max_height)

    if sprite is None:
        return None

    rect = sprite.get_rect(center=(center_x, center_y))
    screen.blit(sprite, rect)

    return rect


def draw_sprite_in_rect(screen, sprite_path, rect, padding=4):
    return draw_sprite_centered(
        screen,
        sprite_path,
        rect.centerx,
        rect.centery,
        rect.width - padding * 2,
        rect.height - padding * 2,
    )


def draw_item_sprite(screen, item_data, rect, padding=4):
    sprite_path = item_data.get("sprite")

    if sprite_path is None:
        return None

    return draw_sprite_in_rect(screen, sprite_path, rect, padding)
