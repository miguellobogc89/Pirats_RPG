"""Mouse-driven placement mode. World simulation continues normally."""
import pygame
from game.world.grid_manager import TILE_SIZE, world_to_grid
from game.world.camera import get_camera_position
from game.data.item_database import get_item_data
from game.inventory.hotbar_manager import get_active_item_id
from game.inventory.item_transactions import spend, quantity
from game.construction.construction_manager import can_place_object, place_object
from game.ui.sprite_renderer import draw_item_sprite


def stop_placement(app):
    app.placement_mode = False
    app.placement_item_id = None


def placement_target(app, mouse_pos):
    item_id = getattr(app, "placement_item_id", None)
    if not app.placement_mode or item_id != get_active_item_id(app.state):
        return None
    item = get_item_data(item_id)
    if not item or item.get("type") != "placeable" or quantity(app.state, item_id) <= 0:
        return None
    width, height = item.get("footprint", [1, 1])
    player = app.state["player"]
    cx, cy = get_camera_position(player["x"], player["y"], app.screen.get_width(),
                                 app.screen.get_height(), app.get_scene_world_width(), app.get_scene_world_height())
    gx, gy = world_to_grid(mouse_pos[0] + cx, mouse_pos[1] + cy)
    player_gx, player_gy = world_to_grid(player["x"], player["y"] + 6)
    overlaps_player = gx <= player_gx < gx + width and gy <= player_gy < gy + height
    valid = (gx >= 0 and gy >= 0 and not overlaps_player and
             (gx + width) * TILE_SIZE <= app.get_scene_world_width() and
             (gy + height) * TILE_SIZE <= app.get_scene_world_height() and
             can_place_object(app.state, gx, gy, width, height))
    rect = pygame.Rect(round(gx * TILE_SIZE - cx), round(gy * TILE_SIZE - cy),
                       width * TILE_SIZE, height * TILE_SIZE)
    return item_id, gx, gy, width, height, valid, rect


def place_at_mouse(app, mouse_pos):
    target = placement_target(app, mouse_pos)
    if target is None:
        stop_placement(app)
        return False
    item_id, gx, gy, width, height, valid, rect = target
    if not valid:
        return False
    if not spend(app.state, item_id, 1):
        return False
    if not place_object(app.state, item_id, gx, gy, width, height):
        from game.inventory.item_transactions import receive
        receive(app.state, item_id, 1)
        return False
    app.skill_manager.register_action("object_placed")
    if get_active_item_id(app.state) != item_id:
        stop_placement(app)
    return True


def draw_placement_preview(app):
    if app.menu_open or app.stash_open or app.cartography_menu_open:
        return
    target = placement_target(app, pygame.mouse.get_pos())
    if target is None:
        return
    item_id, gx, gy, width, height, valid, rect = target
    tint = (62, 171, 98, 90) if valid else (204, 62, 65, 110)
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    surface.fill(tint)
    app.screen.blit(surface, rect.topleft)
    pygame.draw.rect(app.screen, tint[:3], rect, 2)
    item = get_item_data(item_id)
    if draw_item_sprite(app.screen, item, rect, padding=2) is None:
        label = app.font.render(item.get("icon", "?"), True, tint[:3])
        app.screen.blit(label, label.get_rect(center=rect.center))
