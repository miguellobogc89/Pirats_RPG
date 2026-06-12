import pygame


def update_player_movement(state, speed, dt):
    keys = pygame.key.get_pressed()
    player = state["player"]

    dx = 0
    dy = 0

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += 1
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += 1

    if dx != 0 or dy != 0:
        length = (dx * dx + dy * dy) ** 0.5
        player["x"] += dx / length * speed * dt
        player["y"] += dy / length * speed * dt

    player["x"] = max(20, min(1580, player["x"]))
    player["y"] = max(20, min(1180, player["y"]))