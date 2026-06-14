BLOCKED_CELLS = set()
SCENE_COLLISION_RECTS = []


def is_map_cell_blocked(grid_x, grid_y):
    if (grid_x, grid_y) in BLOCKED_CELLS:
        return True

    from game.world.grid_manager import TILE_SIZE, grid_to_world

    world_x, world_y = grid_to_world(grid_x, grid_y)
    cell_rect = (world_x, world_y, TILE_SIZE, TILE_SIZE)

    for collision_rect in SCENE_COLLISION_RECTS:
        if collision_rect.colliderect(cell_rect):
            return True

    return False

def load_test_collisions():
    for x in range(20, 35):
        BLOCKED_CELLS.add((x, 15))


def set_scene_collision_rects(collision_rects):
    SCENE_COLLISION_RECTS.clear()
    SCENE_COLLISION_RECTS.extend(collision_rects)


def get_scene_collision_rects():
    return list(SCENE_COLLISION_RECTS)

from game.world.grid_manager import world_to_grid
from game.world_objects import WORLD_OBJECTS


def is_world_object_cell_blocked(state, grid_x, grid_y):
    if not state.get("_use_legacy_world_objects", True):
        return False

    destroyed_objects = state.get("destroyed_world_objects", [])

    for world_object in WORLD_OBJECTS:
        if world_object["id"] in destroyed_objects:
            continue

        if world_object["type"] not in ["tree", "rock", "bush"]:
            continue

        object_grid_x, object_grid_y = world_to_grid(
            world_object["x"],
            world_object["y"],
        )

        if grid_x == object_grid_x and grid_y == object_grid_y:
            return True

    return False
