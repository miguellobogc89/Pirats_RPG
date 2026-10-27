"""Arte de la playa de Brumazul: un mapa continuo, no sprites de plataformas.

Todas las coordenadas son de mundo (704x704). Los elementos decorativos
no crean colisiones: las rocas ocupan obstaculos ya definidos en la escena.
La paleta usa exclusivamente cuatro grises puros.
"""
from functools import lru_cache
from math import sin

import pygame


SIZE = 704
WHITE = (240, 240, 240)
LIGHT = (184, 184, 184)
MID = (104, 104, 104)
BLACK = (24, 24, 24)


def _shore_x(y):
    # Costado occidental; el borde escalonado evita curvas suavizadas.
    return 84 + 4 * round((8 * sin(y / 63) + 5 * sin(y / 27)) / 4)


def _pebble(surface, x, y, size=5):
    """Guijarro bajo, no acantilado ni plataforma flotante."""
    x, y = int(x), int(y)
    pygame.draw.rect(surface, MID, (x, y + 2, size + 2, max(2, size // 2)))
    pygame.draw.rect(surface, BLACK, (x + 1, y, size, max(2, size // 2)))
    pygame.draw.rect(surface, LIGHT, (x + 2, y, max(2, size // 2), 2))


def _boulder(surface, x, y, width, height):
    """Roca baja pixelada apoyada en una sombra de arena."""
    x, y, width, height = map(int, (x, y, width, height))
    pygame.draw.ellipse(surface, LIGHT, (x - 3, y + height - 5, width + 6, 10))
    pygame.draw.polygon(surface, BLACK, [
        (x, y + height - 5), (x + 2, y + height // 3),
        (x + width // 4, y + 2), (x + 3 * width // 4, y),
        (x + width - 2, y + height // 3), (x + width, y + height - 4),
        (x + width - 4, y + height), (x + 4, y + height),
    ])
    pygame.draw.polygon(surface, MID, [
        (x + 4, y + height - 6), (x + 5, y + height // 3 + 1),
        (x + width // 4 + 1, y + 5), (x + 3 * width // 4 - 2, y + 4),
        (x + width - 6, y + height // 3 + 2),
        (x + width - 5, y + height - 7),
    ])
    pygame.draw.polygon(surface, LIGHT, [
        (x + 7, y + height // 3 + 1), (x + width // 4 + 2, y + 6),
        (x + width // 2, y + 6), (x + width // 2 - 2, y + height // 2),
        (x + 7, y + height // 2 + 1),
    ])
    pygame.draw.rect(surface, BLACK, (x + width // 2, y + height // 2, 3, 5))


@lru_cache(maxsize=1)
def _beach_surface():
    """Construir el decorado solo una vez; en juego se hace un blit."""
    art = pygame.Surface((SIZE, SIZE))
    art.fill(WHITE)

    # Arena: variaciones de pocos pixeles, sin cuadrícula de depuración.
    for gy in range(173, SIZE - 8, 23):
        for gx in range(110, SIZE - 6, 23):
            n = (gx * 13 + gy * 17 + gx * gy // 23) % 19
            if n in (0, 4, 9, 13):
                x, y = gx + n % 5, gy + n % 7
                pygame.draw.rect(art, LIGHT, (x, y, 5, 2))
                pygame.draw.rect(art, MID, (x + 7, y + 3, 2, 2))
            elif n == 5:
                x, y = gx + 4, gy + 5
                pygame.draw.rect(art, MID, (x + 3, y - 3, 2, 5))
                pygame.draw.rect(art, MID, (x, y - 1, 4, 2))
                pygame.draw.rect(art, LIGHT, (x + 5, y, 4, 2))

    # Banco arenoso / pedregoso del norte, continuo y transitable.
    pygame.draw.rect(art, LIGHT, (0, 0, SIZE, 158))
    for y in range(31, 158, 13):
        for x in range(11, SIZE - 15, 29):
            marker = (x * 5 + y * 11) % 7
            if marker <= 2:
                pygame.draw.rect(art, MID, (x, y, 6, 2))
                pygame.draw.rect(art, WHITE, (x + 2, y - 3, 3, 2))
    pygame.draw.rect(art, MID, (0, 155, SIZE, 3))
    for x in range(0, SIZE, 16):
        pygame.draw.rect(art, WHITE, (x + 3, 158, 8, 2))

    # El camino sigue conectado al acceso norte del juego.
    pygame.draw.rect(art, WHITE, (350, 0, 100, 158))
    for y in range(16, 160, 21):
        for x in (361, 385, 418, 441):
            pygame.draw.rect(art, LIGHT, (x + (y % 5), y, 3, 2))
    # Límite rocoso SOLO en el borde del mapa, pegado al terreno.
    for x in list(range(0, 346, 19)) + list(range(456, SIZE, 19)):
        n = (x // 19 * 7) % 5
        pygame.draw.rect(art, BLACK, (x, 0, 18, 10 + n))
        pygame.draw.rect(art, MID, (x + 2, 0, 14, 6 + n))
        pygame.draw.rect(art, LIGHT, (x + 4, 0, 7, 2 + n // 2))
        pygame.draw.rect(art, MID, (x + 12, 9 + n, 2, 5))

    # Mar al oeste de la playa. Bandas pixeladas / espuma siguiendo la costa.
    for y in range(164, SIZE, 4):
        shore = _shore_x(y)
        pygame.draw.rect(art, MID, (0, y, shore - 3, 4))
        # Borde de espuma y arena húmeda: perfil variable pero continuo.
        pygame.draw.rect(art, BLACK, (shore - 11, y, 5, 4))
        pygame.draw.rect(art, LIGHT, (shore - 6, y, 6, 4))
        pygame.draw.rect(art, WHITE, (shore, y, 4, 4))
        pygame.draw.rect(art, LIGHT, (shore + 4, y, 8, 4))
    # Ondas separadas de la orilla: no son líneas de cuadrícula.
    for y in range(184, SIZE - 10, 33):
        for x in (8, 30, 49):
            if x + 18 < _shore_x(y) - 10:
                shift = (y * 3 + x) % 8
                pygame.draw.rect(art, LIGHT, (x, y + shift, 16, 2))
                pygame.draw.rect(art, WHITE, (x + 5, y + shift - 3, 8, 2))

    # Arena del borde: conchas y piedras de pocos pixeles.
    for y in range(190, SIZE - 12, 36):
        edge = _shore_x(y)
        _pebble(art, edge + 23 + (y % 11), y + 8, 3)
        pygame.draw.rect(art, MID, (edge + 41, y + 18, 3, 2))
    return art


def draw_beach_ground(screen, camera_x, camera_y):
    screen.blit(_beach_surface(), (-int(camera_x), -int(camera_y)))


def draw_beach_rocks(screen, camera_x, camera_y, collision_rects):
    """Varias rocas bajas ocupan cada obstaculo, no uno enorme estirado."""
    for rect in collision_rects:
        if rect.width < 60 or rect.height < 30:
            continue  # puertas y otros obstaculos pequeños se dibujan aparte
        cluster = pygame.Surface((int(rect.width), int(rect.height)), pygame.SRCALPHA)
        # Sombra de piedras dispersas, integrada en la arena.
        pygame.draw.ellipse(cluster, LIGHT, (0, 4, rect.width, rect.height - 5))
        count = max(2, min(4, (rect.width + 12) // 36))
        gap = rect.width / count
        for i in range(count):
            bx = int(i * gap + 2)
            width = int(min(gap + 11, rect.width - bx))
            height = max(16, min(30, int(rect.height * .58) + (i % 2) * 3))
            by = int(rect.height * .68 - height + (i % 2) * 7)
            _boulder(cluster, bx, by, max(14, width), height)
        if rect.height > 60:
            _boulder(cluster, rect.width // 4, rect.height - 35, rect.width // 2, 26)
        screen.blit(cluster, (int(rect.x - camera_x), int(rect.y - camera_y)))


def draw_beach_pickup(screen, x, y):
    """Piedra recogible: icono relleno legible, no circulo de debug."""
    x, y = int(x), int(y)
    pygame.draw.rect(screen, BLACK, (x - 6, y - 2, 12, 6))
    pygame.draw.rect(screen, MID, (x - 4, y - 5, 8, 4))
    pygame.draw.rect(screen, LIGHT, (x - 3, y - 4, 4, 2))
