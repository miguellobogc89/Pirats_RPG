import pygame


def render_bitmap(bitmap_data):
    width = bitmap_data["width"]
    height = bitmap_data["height"]
    pixel_size = bitmap_data.get("pixel_size", 1)
    palette = bitmap_data["palette"]
    bitmap = bitmap_data["bitmap"]

    surface = pygame.Surface(
        (width * pixel_size, height * pixel_size),
        pygame.SRCALPHA,
    )

    for y, row in enumerate(bitmap):
        for x, char in enumerate(row):
            color = palette.get(char)

            if color is None:
                continue

            rect = pygame.Rect(
                x * pixel_size,
                y * pixel_size,
                pixel_size,
                pixel_size,
            )

            surface.fill(color, rect)

    return surface