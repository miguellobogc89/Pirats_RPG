import pygame


def get_object_sprite_rect(
    cell,
    footprint,
    sprite_size,
    sprite_offset=None,
    tile_size=16,
    camera_offset=(0, 0),
):
    sprite_offset = sprite_offset or [0, 0]
    sprite_width = max(1, int(sprite_size[0]))
    sprite_height = max(1, int(sprite_size[1]))
    footprint_x = cell[0] * tile_size - camera_offset[0]
    footprint_y = cell[1] * tile_size - camera_offset[1]

    return pygame.Rect(
        int(footprint_x + sprite_offset[0]),
        int(footprint_y + sprite_offset[1]),
        sprite_width,
        sprite_height,
    )


def get_object_footprint_rect(
    cell,
    footprint,
    tile_size=16,
    camera_offset=(0, 0),
):
    return pygame.Rect(
        int(cell[0] * tile_size - camera_offset[0]),
        int(cell[1] * tile_size - camera_offset[1]),
        int(footprint[0] * tile_size),
        int(footprint[1] * tile_size),
    )
