import pygame


PREVIEW_BG = (28, 31, 36)
GRID_COLOR = (70, 75, 84)
FOOTPRINT_COLOR = (80, 180, 255)
ANCHOR_COLOR = (255, 210, 90)


def draw_object_preview(screen, rect, state, sprite=None, tile_size=32):
    pygame.draw.rect(screen, PREVIEW_BG, rect)
    pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    center_x = rect.centerx
    center_y = rect.centery

    footprint_w = state.footprint[0] * tile_size
    footprint_h = state.footprint[1] * tile_size

    footprint_rect = pygame.Rect(
        center_x - footprint_w // 2,
        center_y - footprint_h // 2,
        footprint_w,
        footprint_h,
    )

    for x in range(footprint_rect.left, footprint_rect.right + 1, tile_size):
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (x, footprint_rect.top),
            (x, footprint_rect.bottom),
        )

    for y in range(footprint_rect.top, footprint_rect.bottom + 1, tile_size):
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (footprint_rect.left, y),
            (footprint_rect.right, y),
        )

    pygame.draw.rect(screen, FOOTPRINT_COLOR, footprint_rect, 2)

    anchor_x = footprint_rect.left
    anchor_y = footprint_rect.top

    pygame.draw.circle(screen, ANCHOR_COLOR, (anchor_x, anchor_y), 5)

    if sprite is None:
        return {
            "preview_rect": rect,
            "footprint_rect": footprint_rect,
            "anchor_pos": [anchor_x, anchor_y],
            "sprite_rect": None,
        }

    new_w = sprite.get_width()
    new_h = sprite.get_height()

    preview_sprite = sprite

    sprite_pos = (
        anchor_x + state.sprite_offset[0],
        anchor_y + state.sprite_offset[1],
    )

    pygame.draw.line(
        screen,
        (255, 210, 90),
        (anchor_x - 10, anchor_y),
        (anchor_x + 10, anchor_y),
        2,
    )

    pygame.draw.line(
        screen,
        (255, 210, 90),
        (anchor_x, anchor_y - 10),
        (anchor_x, anchor_y + 10),
        2,
    )

    screen.blit(preview_sprite, sprite_pos)

    return {
        "preview_rect": rect,
        "footprint_rect": footprint_rect,
        "anchor_pos": [anchor_x, anchor_y],
        "sprite_rect": pygame.Rect(
            sprite_pos[0],
            sprite_pos[1],
            new_w,
            new_h,
        ),
    }