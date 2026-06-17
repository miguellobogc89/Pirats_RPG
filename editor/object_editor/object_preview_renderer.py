import pygame

from game.world.object_sprite_layout import (
    get_object_footprint_rect,
    get_object_sprite_rect,
)

PREVIEW_BG = (28, 31, 36)
GRID_COLOR = (58, 63, 72)
GRID_CENTER_COLOR = (90, 96, 108)
FOOTPRINT_COLOR = (80, 180, 255)
FOOTPRINT_SOLID_COLOR = (220, 88, 88)
FOOTPRINT_SELECTED_COLOR = (242, 203, 92)
ANCHOR_COLOR = (255, 210, 90)
TEXT_COLOR = (220, 220, 220)
SELECTED_COLOR = (245, 248, 255)
HANDLE_FILL = (38, 41, 48)
STATUS_BG = (22, 24, 29)
PLAYER_REF = (96, 168, 245, 70)
INTERACTION_COLOR = (94, 224, 194)


def make_handle_rects(rect, size=8):
    points = {
        "nw": rect.topleft,
        "n": (rect.centerx, rect.top),
        "ne": rect.topright,
        "e": (rect.right, rect.centery),
        "se": rect.bottomright,
        "s": (rect.centerx, rect.bottom),
        "sw": rect.bottomleft,
        "w": (rect.left, rect.centery),
    }
    return {
        key: pygame.Rect(pos[0] - size // 2, pos[1] - size // 2, size, size)
        for key, pos in points.items()
    }


def draw_handles(screen, handle_rects, color=SELECTED_COLOR):
    for handle_rect in handle_rects.values():
        pygame.draw.rect(screen, HANDLE_FILL, handle_rect)
        pygame.draw.rect(screen, color, handle_rect, 1)


def draw_grid(screen, rect, tile_size, pan):
    center_x = rect.centerx
    center_y = rect.centery

    start_x = center_x + pan[0] % tile_size
    while start_x > rect.left:
        start_x -= tile_size

    start_y = center_y + pan[1] % tile_size
    while start_y > rect.top:
        start_y -= tile_size

    end_x = rect.right
    end_y = rect.bottom

    x = start_x
    while x <= end_x:
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (x, start_y),
            (x, end_y),
        )
        x += tile_size

    y = start_y
    while y <= end_y:
        pygame.draw.line(
            screen,
            GRID_COLOR,
            (start_x, y),
            (end_x, y),
        )
        y += tile_size


def draw_object_preview(screen, rect, state, sprite=None, tile_size=32):
    pygame.draw.rect(screen, PREVIEW_BG, rect)
    previous_clip = screen.get_clip()
    screen.set_clip(rect)

    zoomed_tile_size = max(8, int(tile_size * state.preview_zoom))
    draw_grid(screen, rect, zoomed_tile_size, state.preview_pan)

    preview_cell = [0, 0]
    camera_offset = (
        -rect.centerx - state.preview_pan[0],
        -rect.centery - state.preview_pan[1],
    )

    footprint_rect = get_object_footprint_rect(
        preview_cell,
        state.footprint,
        tile_size=zoomed_tile_size,
        camera_offset=camera_offset,
    )
    footprint_rect.move_ip(state.footprint_preview_offset)

    draw_player_reference(screen, footprint_rect, zoomed_tile_size)

    footprint_color = FOOTPRINT_SOLID_COLOR if state.solid else FOOTPRINT_COLOR
    pygame.draw.rect(screen, footprint_color, footprint_rect, 2)
    footprint_handles = make_handle_rects(footprint_rect, 8)

    if state.selected_element == "footprint":
        pygame.draw.rect(screen, FOOTPRINT_SELECTED_COLOR, footprint_rect, 1)
        draw_handles(screen, footprint_handles, FOOTPRINT_SELECTED_COLOR)

    anchor_x = footprint_rect.left
    anchor_y = footprint_rect.top

    pygame.draw.circle(screen, ANCHOR_COLOR, (anchor_x, anchor_y), 5)
    draw_interaction_points(screen, footprint_rect, state, state.preview_zoom)

    pygame.draw.line(
        screen,
        ANCHOR_COLOR,
        (anchor_x - 10, anchor_y),
        (anchor_x + 10, anchor_y),
        2,
    )

    pygame.draw.line(
        screen,
        ANCHOR_COLOR,
        (anchor_x, anchor_y - 10),
        (anchor_x, anchor_y + 10),
        2,
    )

    if sprite is None:
        draw_selection_status(screen, rect, state)
        screen.set_clip(previous_clip)
        return {
            "preview_rect": rect,
            "footprint_rect": footprint_rect,
            "footprint_handles": footprint_handles,
            "anchor_pos": [anchor_x, anchor_y],
            "sprite_rect": None,
            "sprite_handles": {},
            "tile_size": zoomed_tile_size,
        }

    sprite_size = getattr(state, "sprite_size", None)
    if sprite_size is None:
        new_w = sprite.get_width()
        new_h = sprite.get_height()
        state.sprite_size = [new_w, new_h]
    else:
        new_w = max(8, int(sprite_size[0]))
        new_h = max(8, int(sprite_size[1]))

    scaled_sprite_size = [
        max(8, int(new_w * state.preview_zoom)),
        max(8, int(new_h * state.preview_zoom)),
    ]
    scaled_sprite_offset = [
        int(state.sprite_offset[0] * state.preview_zoom),
        int(state.sprite_offset[1] * state.preview_zoom),
    ]
    sprite_rect = get_object_sprite_rect(
        preview_cell,
        state.footprint,
        scaled_sprite_size,
        scaled_sprite_offset,
        tile_size=zoomed_tile_size,
        camera_offset=camera_offset,
    )
    sprite_rect.move_ip(state.footprint_preview_offset)

    scaled_sprite = pygame.transform.scale(sprite, sprite_rect.size)
    screen.blit(scaled_sprite, sprite_rect)
    sprite_handles = make_handle_rects(sprite_rect, 8)

    if state.selected_element == "sprite":
        pygame.draw.rect(screen, SELECTED_COLOR, sprite_rect, 1)
        draw_handles(screen, sprite_handles, SELECTED_COLOR)

    draw_selection_status(screen, rect, state)
    screen.set_clip(previous_clip)

    return {
        "preview_rect": rect,
        "footprint_rect": footprint_rect,
        "footprint_handles": footprint_handles,
        "anchor_pos": [anchor_x, anchor_y],
        "sprite_rect": sprite_rect,
        "sprite_handles": sprite_handles,
        "tile_size": zoomed_tile_size,
    }


def draw_player_reference(screen, footprint_rect, tile_size):
    ref_rect = pygame.Rect(0, 0, tile_size, tile_size)
    ref_rect.center = footprint_rect.center
    overlay = pygame.Surface(ref_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(overlay, PLAYER_REF, overlay.get_rect(), border_radius=3)
    pygame.draw.rect(overlay, (180, 215, 255, 110), overlay.get_rect(), 1, border_radius=3)
    screen.blit(overlay, ref_rect)


def draw_interaction_points(screen, footprint_rect, state, zoom):
    for index, point in enumerate(state.interaction_points):
        point_x = int(footprint_rect.x + point[0] * zoom)
        point_y = int(footprint_rect.y + point[1] * zoom)
        pygame.draw.circle(screen, INTERACTION_COLOR, (point_x, point_y), 6)
        pygame.draw.circle(screen, (20, 24, 26), (point_x, point_y), 3)
        font = pygame.font.SysFont("segoeui", 10, bold=True)
        label = font.render(str(index + 1), True, INTERACTION_COLOR)
        screen.blit(label, (point_x + 8, point_y - 7))


def draw_selection_status(screen, rect, state):
    if state.selected_element is None:
        return

    status_rect = pygame.Rect(rect.x, rect.bottom - 28, rect.w, 28)
    pygame.draw.rect(screen, STATUS_BG, status_rect)

    font = pygame.font.SysFont("segoeui", 12)
    sprite_size = state.sprite_size or ["auto", "auto"]
    text = (
        f"Offset {state.sprite_offset}    "
        f"Size {sprite_size}    "
        f"Footprint {state.footprint[0]} x {state.footprint[1]}"
    )
    surface = font.render(text, True, TEXT_COLOR)
    screen.blit(surface, (status_rect.x + 10, status_rect.y + 7))

