import pygame

STATUS_BAR_HEIGHT = 28

COLOR_BAR = (24, 26, 30)
COLOR_BORDER = (95, 100, 110)
COLOR_TEXT_MUTED = (165, 170, 178)
COLOR_TEXT_OK = (150, 220, 160)


def get_object_at_cell(scene_data, object_definitions, cell):
    for object_data in reversed(scene_data["objects"]):
        object_type = object_data["type"]

        if object_type not in object_definitions:
            continue

        footprint = object_definitions[object_type]["footprint"]
        origin_cell = object_data["cell"]

        min_x = origin_cell[0]
        max_x = origin_cell[0] + footprint[0] - 1
        min_y = origin_cell[1]
        max_y = origin_cell[1] + footprint[1] - 1

        if min_x <= cell[0] <= max_x and min_y <= cell[1] <= max_y:
            return object_type

    return "-"


def draw_editor_status_bar(
    screen,
    scene_data,
    object_definitions,
    camera,
    mode,
    selected_object_type,
    status_message="",
):
    font = pygame.font.SysFont("consolas", 14)

    y = screen.get_height() - STATUS_BAR_HEIGHT

    pygame.draw.rect(
        screen,
        COLOR_BAR,
        (0, y, screen.get_width(), STATUS_BAR_HEIGHT),
    )

    pygame.draw.line(
        screen,
        COLOR_BORDER,
        (0, y),
        (screen.get_width(), y),
    )

    mouse_pos = pygame.mouse.get_pos()
    cell = camera.screen_to_cell(mouse_pos)

    object_type = get_object_at_cell(
        scene_data,
        object_definitions,
        cell,
    )

    collision_text = "no"
    if cell in scene_data["collisions"]:
        collision_text = "yes"

    terrain_text = "grass"

    dirty_text = "saved"
    if status_message:
        dirty_text = status_message

    text = (
        f"Scene: {scene_data.get('name', '-')} ({scene_data.get('id', '-')})   "
        f"Cell: {cell[0]}, {cell[1]}   "
        f"Object: {object_type}   "
        f"Collision: {collision_text}   "
        f"Terrain: {terrain_text}   "
        f"Mode: {mode}   "
        f"Selected: {selected_object_type}   "
        f"{dirty_text}"
    )

    color = COLOR_TEXT_MUTED

    if status_message:
        color = COLOR_TEXT_OK

    surface = font.render(text, True, color)
    screen.blit(surface, (10, y + 6))