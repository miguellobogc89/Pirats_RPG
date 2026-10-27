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
        loaded_sprite = pygame.image.load(sprite_path)
    except pygame.error:
        _missing_sprites.add(sprite_path)
        return None

    try:
        if pygame.display.get_surface() is not None:
            sprite = loaded_sprite.convert_alpha()
        else:
            sprite = loaded_sprite
    except pygame.error:
        try:
            sprite = loaded_sprite.convert()
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


# Pixel art del simulador: cuatro tonos de gris, sin escalado suavizado.
# Las superficies de 16/24 px se cachean y se amplian con nearest-neighbor.
from functools import lru_cache

GB_WHITE = (240, 240, 240)
GB_LIGHT = (184, 184, 184)
GB_MID = (104, 104, 104)
GB_BLACK = (24, 24, 24)


@lru_cache(maxsize=16)
def _pixel_character(direction, npc):
    sprite = pygame.Surface((16, 16), pygame.SRCALPHA)

    def px(color, x, y, w, h):
        pygame.draw.rect(sprite, color, (x, y, w, h))

    # Botas y pantalones; los pies corresponden a la posicion del actor.
    px(GB_BLACK, 3, 12, 4, 4)
    px(GB_BLACK, 9, 12, 4, 4)
    px(GB_MID, 4, 12, 2, 2)
    px(GB_MID, 10, 12, 2, 2)

    # Casaca, mangas y cinturon.
    px(GB_BLACK, 3, 8, 10, 5)
    px(GB_MID if npc else GB_LIGHT, 4, 8, 8, 4)
    px(GB_BLACK, 6, 8, 4, 4)
    px(GB_LIGHT if npc else GB_MID, 7, 8, 2, 3)
    px(GB_BLACK, 4, 11, 8, 1)
    px(GB_LIGHT, 7, 11, 2, 1)
    px(GB_BLACK, 1, 9, 2, 3)
    px(GB_BLACK, 13, 9, 2, 3)
    px(GB_LIGHT, 1, 11, 2, 1)
    px(GB_LIGHT, 13, 11, 2, 1)

    # Cara y pelo, diferentes segun la orientacion.
    px(GB_BLACK, 5, 3, 6, 6)
    if direction == "up":
        px(GB_MID, 6, 4, 4, 4)
        px(GB_BLACK, 6, 6, 4, 2)
    else:
        px(GB_WHITE, 6, 4, 4, 4)
        if direction == "left":
            px(GB_BLACK, 6, 6, 1, 1)
        elif direction == "right":
            px(GB_BLACK, 9, 6, 1, 1)
        else:
            px(GB_BLACK, 6, 6, 1, 1)
            px(GB_BLACK, 9, 6, 1, 1)
        px(GB_MID, 7, 8, 2, 1)

    # Sombrero de ala ancha del pirata / cabello del NPC.
    if npc:
        px(GB_BLACK, 5, 1, 6, 3)
        px(GB_MID, 6, 1, 4, 2)
        px(GB_BLACK, 4, 3, 8, 1)
    else:
        px(GB_BLACK, 4, 0, 8, 3)
        px(GB_MID, 5, 1, 6, 1)
        px(GB_BLACK, 2, 3, 12, 2)
        px(GB_LIGHT, 6, 3, 4, 1)
    return sprite


def draw_pixel_actor(screen, x, y, direction="down", npc=False):
    """Dibuja un personaje 16x16 a escala 2; x,y indican los pies."""
    if direction not in ("up", "down", "left", "right"):
        direction = "down"
    x, y = int(x), int(y)
    pygame.draw.ellipse(screen, GB_LIGHT, (x - 12, y - 3, 24, 6))
    sprite = pygame.transform.scale(_pixel_character(direction, npc), (32, 32))
    screen.blit(sprite, (x - 16, y - 32))


@lru_cache(maxsize=1)
def _pixel_tree():
    sprite = pygame.Surface((24, 32), pygame.SRCALPHA)
    pygame.draw.rect(sprite, GB_BLACK, (10, 19, 5, 12))
    pygame.draw.rect(sprite, GB_MID, (11, 20, 3, 10))
    pygame.draw.rect(sprite, GB_BLACK, (7, 27, 11, 3))
    # Copa escalonada, sombreado y pequenos huecos entre hojas.
    for rect in ((7, 2, 11, 22), (3, 6, 18, 17),
                 (1, 11, 22, 10), (5, 1, 14, 23)):
        pygame.draw.rect(sprite, GB_BLACK, rect)
    for rect in ((8, 3, 9, 18), (4, 7, 16, 13),
                 (2, 12, 20, 7)):
        pygame.draw.rect(sprite, GB_MID, rect)
    for rect in ((8, 4, 6, 5), (4, 10, 5, 5),
                 (14, 8, 5, 5), (9, 15, 8, 4)):
        pygame.draw.rect(sprite, GB_LIGHT, rect)
    for x, y in ((7, 8), (17, 6), (5, 17), (13, 13), (18, 17)):
        pygame.draw.rect(sprite, GB_BLACK, (x, y, 2, 1))
    return sprite


def draw_pixel_tree(screen, center_x, center_y, width=72, height=96, species="oak"):
    """Arbol ilustrado PNG; conserva la caja de render, colisiones y fallback."""
    species = species if species in ("oak", "palm", "mangrove") else "oak"
    sprite = _atlas_scaled(species, int(width), int(height))
    if sprite is None:
        sprite = pygame.transform.scale(_pixel_tree(), (int(width), int(height)))
    rect = sprite.get_rect(center=(int(center_x), int(center_y)))
    screen.blit(sprite, rect)
    return rect


@lru_cache(maxsize=24)
def _pixel_building(door_column):
    sprite = pygame.Surface((24, 20), pygame.SRCALPHA)
    pygame.draw.rect(sprite, GB_BLACK, (2, 8, 20, 12))
    pygame.draw.rect(sprite, GB_LIGHT, (3, 10, 18, 9))
    # Tejado a dos aguas, con bordes dentados y tejas.
    pygame.draw.rect(sprite, GB_BLACK, (5, 0, 14, 3))
    pygame.draw.rect(sprite, GB_BLACK, (3, 3, 18, 3))
    pygame.draw.rect(sprite, GB_BLACK, (1, 6, 22, 5))
    pygame.draw.rect(sprite, GB_MID, (6, 1, 12, 2))
    pygame.draw.rect(sprite, GB_MID, (4, 4, 16, 2))
    pygame.draw.rect(sprite, GB_MID, (2, 7, 20, 2))
    for x, y in ((6, 2), (13, 2), (9, 5), (17, 5), (5, 8), (14, 8)):
        pygame.draw.rect(sprite, GB_LIGHT, (x, y, 3, 1))
    # Ventanas, basamento y puerta alineada con la entrada real.
    for x in (4, 18):
        pygame.draw.rect(sprite, GB_BLACK, (x, 12, 3, 5))
        pygame.draw.rect(sprite, GB_WHITE, (x + 1, 13, 1, 2))
    pygame.draw.rect(sprite, GB_MID, (3, 18, 18, 1))
    pygame.draw.rect(sprite, GB_BLACK, (door_column, 13, 4, 7))
    pygame.draw.rect(sprite, GB_MID, (door_column + 1, 14, 2, 6))
    pygame.draw.rect(sprite, GB_WHITE, (door_column + 2, 17, 1, 1))
    return sprite


def draw_pixel_building(screen, rect, door_x=None):
    """Casa ilustrada en el rectangulo original, sin cambiar puertas ni fisicas."""
    rect = pygame.Rect(rect)
    if rect.width <= 0 or rect.height <= 0:
        return
    sprite = _atlas_scaled("house", rect.width, rect.height)
    if sprite is not None:
        screen.blit(sprite, rect)
        return rect
    relative = .5 if door_x is None else (door_x - rect.x) / rect.width
    door_column = max(7, min(14, round(relative * 24) - 2))
    sprite = pygame.transform.scale(_pixel_building(door_column), rect.size)
    screen.blit(sprite, rect)
    return rect


@lru_cache(maxsize=1)
def _pixel_monster():
    sprite = pygame.Surface((24, 24), pygame.SRCALPHA)
    # Bestia rocosa con cuernos, garras y grietas visibles.
    pygame.draw.polygon(sprite, GB_BLACK, [(3, 10), (1, 0), (9, 6)])
    pygame.draw.polygon(sprite, GB_BLACK, [(21, 10), (23, 0), (15, 6)])
    pygame.draw.rect(sprite, GB_BLACK, (4, 7, 16, 14))
    pygame.draw.rect(sprite, GB_BLACK, (2, 11, 20, 8))
    pygame.draw.rect(sprite, GB_MID, (5, 8, 14, 11))
    pygame.draw.rect(sprite, GB_LIGHT, (6, 9, 5, 4))
    pygame.draw.rect(sprite, GB_LIGHT, (14, 10, 5, 3))
    for x in (7, 15):
        pygame.draw.rect(sprite, GB_BLACK, (x, 13, 3, 3))
        pygame.draw.rect(sprite, GB_WHITE, (x, 13, 2, 2))
        pygame.draw.rect(sprite, GB_BLACK, (x + 1, 14, 1, 1))
    pygame.draw.rect(sprite, GB_BLACK, (9, 18, 6, 2))
    pygame.draw.rect(sprite, GB_WHITE, (10, 18, 1, 1))
    pygame.draw.rect(sprite, GB_WHITE, (13, 18, 1, 1))
    for x in (4, 17):
        pygame.draw.rect(sprite, GB_BLACK, (x, 20, 4, 3))
    return sprite


def draw_pixel_monster(screen, center_x, center_y, preparing=False):
    """Silueta del enemigo; los telegraphs/vida siguen en el combate."""
    x, y = int(center_x), int(center_y)
    pygame.draw.ellipse(screen, GB_LIGHT, (x - 37, y + 25, 74, 12))
    sprite = pygame.transform.scale(_pixel_monster(), (72, 72))
    screen.blit(sprite, (x - 36, y - 39))
    if preparing:
        pygame.draw.rect(screen, GB_BLACK, (x - 30, y - 42, 60, 3))


# Atlas de arte real, generado para el simulador (no se renderizan formas
# geometricas cuando el PNG esta disponible). Cada celda tiene alfa propio.
_ART_ATLAS_PATH = "assets/world/gameboy_atlas.png"
_ART_ATLAS_RECTS = {
    "palm": (0, 0, 60, 85),
    "oak": (60, 0, 68, 86),
    "mangrove": (128, 0, 68, 82),
    "cliff": (0, 86, 112, 36),
    "rock": (112, 86, 56, 52),
    "house": (0, 139, 116, 77),
}


@lru_cache(maxsize=12)
def _atlas_part(name):
    atlas = get_sprite(_ART_ATLAS_PATH)
    source_rect = _ART_ATLAS_RECTS.get(name)
    if atlas is None or source_rect is None:
        return None
    return atlas.subsurface(pygame.Rect(source_rect)).copy()


@lru_cache(maxsize=128)
def _atlas_scaled(name, width, height):
    part = _atlas_part(name)
    if part is None:
        return None
    return pygame.transform.scale(part, (max(1, width), max(1, height)))


def draw_pixel_rock(screen, center_x, center_y, width=48, height=40):
    """Roca decorativa centrada en un obstaculo que ya existe en el mundo."""
    width, height = max(1, int(width)), max(1, int(height))
    sprite = _atlas_scaled("rock", width, height)
    if sprite is None:
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(sprite, GB_BLACK, sprite.get_rect())
        pygame.draw.ellipse(sprite, GB_MID, sprite.get_rect().inflate(-8, -8))
    rect = sprite.get_rect(center=(int(center_x), int(center_y)))
    screen.blit(sprite, rect)
    return rect


def draw_pixel_cliff(screen, rect):
    """Tramo de pared rocosa; debe dibujarse sobre un limite ya bloqueado."""
    rect = pygame.Rect(rect)
    if rect.width <= 0 or rect.height <= 0:
        return None
    sprite = _atlas_scaled("cliff", rect.width, rect.height)
    if sprite is not None:
        screen.blit(sprite, rect)
    else:
        pygame.draw.rect(screen, GB_BLACK, rect, 3)
        pygame.draw.rect(screen, GB_MID, rect.inflate(-6, -6), 2)
    return rect
