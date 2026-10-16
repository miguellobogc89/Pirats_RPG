import pygame


def draw_pixel_rect(app, x, y, size, color):
    pygame.draw.rect(app.screen, color, (x, y, size, size))


def draw_pixels(app, x, y, size, pixels):
    for pixel in pixels:
        px = x + pixel[0] * size
        py = y + pixel[1] * size
        color = pixel[2]
        draw_pixel_rect(app, px, py, size, color)


def draw_large_pixel_icon(app, actor_type, x, y):
    size = 6

    if actor_type == "player":
        draw_pixel_player(app, x, y, size)
        return

    if actor_type == "rock_turtle":
        draw_pixel_turtle(app, x, y, size)
        return

    if actor_type == "fire_worm":
        draw_pixel_worm(app, x, y, size)
        return

    if actor_type == "farm_slime":
        draw_pixel_slime(app, x, y, size)
        return


def draw_pixel_player(app, x, y, size):
    skin = (220, 170, 120)
    coat = (50, 80, 120)
    pants = (45, 45, 55)
    hat = (70, 45, 30)

    pixels = [
        (3, 0, hat), (4, 0, hat),
        (2, 1, hat), (3, 1, hat), (4, 1, hat), (5, 1, hat),
        (3, 2, skin), (4, 2, skin),
        (2, 3, coat), (3, 3, coat), (4, 3, coat), (5, 3, coat),
        (2, 4, coat), (3, 4, coat), (4, 4, coat), (5, 4, coat),
        (1, 4, skin), (6, 4, skin),
        (3, 5, pants), (4, 5, pants),
        (2, 6, pants), (5, 6, pants),
    ]

    draw_pixels(app, x, y, size, pixels)


def draw_pixel_turtle(app, x, y, size):
    shell = (95, 120, 90)
    rock = (95, 95, 85)
    skin = (70, 120, 80)

    pixels = [
        (2, 2, skin), (5, 2, skin),
        (1, 3, skin), (2, 3, shell), (3, 3, rock), (4, 3, rock), (5, 3, shell), (6, 3, skin),
        (1, 4, skin), (2, 4, shell), (3, 4, rock), (4, 4, rock), (5, 4, shell), (6, 4, skin),
        (2, 5, shell), (3, 5, shell), (4, 5, shell), (5, 5, shell),
        (1, 6, skin), (6, 6, skin),
    ]

    draw_pixels(app, x, y, size, pixels)


def draw_pixel_worm(app, x, y, size):
    body = (190, 75, 45)
    fire = (240, 150, 45)
    dark = (95, 45, 35)

    pixels = [
        (5, 1, fire),
        (4, 2, fire), (5, 2, body),
        (3, 3, body), (4, 3, body), (5, 3, body),
        (2, 4, body), (3, 4, body), (4, 4, body),
        (1, 5, body), (2, 5, body), (3, 5, dark),
        (0, 6, dark), (1, 6, body),
    ]

    draw_pixels(app, x, y, size, pixels)


def draw_pixel_slime(app, x, y, size):
    slime = (95, 170, 105)
    light = (150, 220, 150)
    dark = (45, 90, 55)

    pixels = [
        (3, 2, light), (4, 2, light),
        (2, 3, slime), (3, 3, slime), (4, 3, slime), (5, 3, slime),
        (1, 4, slime), (2, 4, slime), (3, 4, dark), (4, 4, slime), (5, 4, dark), (6, 4, slime),
        (1, 5, slime), (2, 5, slime), (3, 5, slime), (4, 5, slime), (5, 5, slime), (6, 5, slime),
        (2, 6, dark), (3, 6, slime), (4, 6, slime), (5, 6, dark),
    ]

    draw_pixels(app, x, y, size, pixels)