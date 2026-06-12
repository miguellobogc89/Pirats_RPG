def get_camera_position(player_x, player_y, screen_width, screen_height, world_width, world_height):
    camera_x = player_x - screen_width / 2
    camera_y = player_y - screen_height / 2

    camera_x = max(0, min(camera_x, world_width - screen_width))
    camera_y = max(0, min(camera_y, world_height - screen_height))

    return camera_x, camera_y