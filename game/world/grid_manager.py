TILE_SIZE = 32


def world_to_grid(x, y):
    grid_x = int(x // TILE_SIZE)
    grid_y = int(y // TILE_SIZE)

    return grid_x, grid_y


def grid_to_world(grid_x, grid_y):
    x = grid_x * TILE_SIZE
    y = grid_y * TILE_SIZE

    return x, y


def grid_to_world_center(grid_x, grid_y):
    x = grid_x * TILE_SIZE + TILE_SIZE // 2
    y = grid_y * TILE_SIZE + TILE_SIZE // 2

    return x, y


def snap_world_to_grid(x, y):
    grid_x, grid_y = world_to_grid(x, y)
    return grid_to_world(grid_x, grid_y)


def snap_world_to_grid_center(x, y):
    grid_x, grid_y = world_to_grid(x, y)
    return grid_to_world_center(grid_x, grid_y)