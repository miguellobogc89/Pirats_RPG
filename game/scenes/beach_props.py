"""Objetos dibujados por codigo para la playa (placeholders hasta tener sprites).

Naufragio, cofre, puerta cerrada, salida, palmeras y campo de piedras.
Coordenadas de mundo; se les resta la camara al dibujar.
"""
import math
from functools import lru_cache

import pygame

from game.ui.sprite_renderer import draw_pixel_tree
from game.world.terrain_tiles import DARK, DEEP, INK, LIGHT, MID, PALE, TILE, WHITE, variant_for


@lru_cache(maxsize=4)
def _wreck_sprite(width, height):
    """Casco de barco volcado de lado, con tablas rotas y costillas al aire."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = width / 2, height / 2
    rx, ry = width / 2 - 6, height / 2 - 6
    # Sombra en la arena.

    def inside(x, y):
        # Proa en punta arriba, popa redondeada abajo.
        t = (y - cy) / ry
        if t < 0:
            half = rx * (1 - abs(t) ** 1.6) ** 0.8 if abs(t) < 1 else 0
        else:
            half = rx * (1 - t ** 2) ** 0.5 if t < 1 else 0
        return abs(x - cx) <= half

    # Tablas del casco (horizontales), con huecos donde el casco esta roto.
    for y in range(height):
        for x in range(width):
            if not inside(x, y):
                continue
            plank = (y // 9) % 2
            broken = (0.25 * height < y < 0.42 * height and x > cx + 4) or (0.62 * height < y < 0.72 * height and x < cx - 6)
            if broken:
                color = DEEP if (x + y) % 5 else INK
            else:
                color = (LIGHT, MID)[plank]
                if y % 9 == 8:
                    color = DARK
                elif (x * 7 + y * 3 + variant_for(x // 6, y // 9)) % 23 == 0:
                    color = DARK
            surf.fill(color, (x, y, 1, 1))
    # Quilla central y costillas.
    pygame.draw.line(surf, INK, (int(cx), 8), (int(cx), height - 8), 3)
    for i in range(2, 7):
        y = int(height * i / 7)
        xs = [x for x in range(width) if inside(x, y)]
        if xs:
            pygame.draw.line(surf, DEEP, (xs[0] + 2, y), (xs[-1] - 2, y), 2)
    # Contorno del casco.
    for y in range(height):
        for x in range(width):
            if inside(x, y) and not (inside(x - 2, y) and inside(x + 2, y) and inside(x, y - 2) and inside(x, y + 2)):
                surf.fill(INK, (x, y, 1, 1))
    # Ventanas de la bodega.
    for y in (int(height * 0.3), int(height * 0.5), int(height * 0.7)):
        surf.fill(INK, (int(cx - 14), y, 7, 9))
        surf.fill(INK, (int(cx + 8), y, 7, 9))
    return surf


def draw_wreck(screen, rect, camera):
    x, y, w, h = rect
    screen.blit(_wreck_sprite(w, h), (x - camera[0], y - camera[1]))
    # Tablas sueltas alrededor.
    for i, (dx, dy, length, angle) in enumerate(((w + 10, 30, 30, 0.4), (w + 4, h * 0.55, 26, -0.3),
                                                 (-26, h * 0.4, 28, 0.2), (w * 0.3, h + 8, 30, 1.2),
                                                 (w + 16, h * 0.8, 22, 0.9))):
        sx, sy = x + dx - camera[0], y + dy - camera[1]
        ex, ey = sx + math.cos(angle) * length, sy + math.sin(angle) * length
        pygame.draw.line(screen, INK, (sx, sy), (ex, ey), 6)
        pygame.draw.line(screen, MID, (sx, sy), (ex, ey), 3)


def draw_chest(screen, cell, camera):
    x, y = cell[0] * TILE - camera[0], cell[1] * TILE - camera[1]
    body = pygame.Rect(x + 4, y + 10, 24, 18)
    pygame.draw.rect(screen, DEEP, body.move(2, 2))
    pygame.draw.rect(screen, MID, body)
    pygame.draw.rect(screen, LIGHT, (body.x, body.y, body.width, 6))
    pygame.draw.rect(screen, INK, body, 2)
    pygame.draw.line(screen, INK, (body.x, body.y + 6), (body.right - 1, body.y + 6), 2)
    pygame.draw.rect(screen, WHITE, (body.centerx - 2, body.y + 5, 4, 5))
    pygame.draw.rect(screen, INK, (body.centerx - 2, body.y + 5, 4, 5), 1)


def draw_gate(screen, rect, camera):
    """Puerta de madera cerrada encajada entre rocas."""
    x, y, w, h = rect
    door = pygame.Rect(x - camera[0] + 4, y - camera[1] + 2, w - 6, h - 4)
    pygame.draw.rect(screen, DEEP, door.move(-3, 3))
    pygame.draw.rect(screen, MID, door)
    for px in range(door.x + 6, door.right, 6):
        pygame.draw.line(screen, DARK, (px, door.y + 2), (px, door.bottom - 3), 1)
    for py in (door.y + 10, door.bottom - 12):
        pygame.draw.rect(screen, INK, (door.x, py, door.width, 4))
        pygame.draw.rect(screen, LIGHT, (door.x + 2, py + 1, 3, 2))
    pygame.draw.rect(screen, INK, door, 2)


def draw_exit_marker(screen, rect, camera):
    """Camino que se adentra en el bosque, marcado con huellas."""
    x, y, w, h = rect
    for i in range(4):
        fx = x + w // 2 - camera[0] + (6 if i % 2 else -6)
        fy = y + h + 8 + i * 14 - camera[1]
        pygame.draw.ellipse(screen, MID, (fx - 3, fy - 4, 6, 8))


def draw_palm(screen, cell, camera):
    cx = cell[0] * TILE + TILE // 2 - camera[0]
    bottom = cell[1] * TILE + TILE - camera[1]
    pygame.draw.ellipse(screen, DEEP, (cx - 14, bottom - 8, 28, 9))
    draw_pixel_tree(screen, cx, bottom - 44, 62, 88, "palm")


def draw_stone_field(screen, rect, camera):
    """Zona con piedras sueltas: aqui siempre se encuentra algo que lanzar."""
    x, y, w, h = rect
    for i in range(22):
        hsh = variant_for(i, 77)
        px = x + hsh % w - camera[0]
        py = y + (hsh >> 9) % h - camera[1]
        size = 7 + (hsh >> 4) % 5
        pygame.draw.ellipse(screen, DEEP, (px - 1, py + 1, size + 2, size - 1))
        pygame.draw.ellipse(screen, INK, (px - 1, py - 1, size + 2, size))
        pygame.draw.ellipse(screen, MID if i % 3 else LIGHT, (px, py, size, size - 2))
        pygame.draw.line(screen, WHITE, (px + 2, py + 1), (px + size // 2, py + 1), 1)
