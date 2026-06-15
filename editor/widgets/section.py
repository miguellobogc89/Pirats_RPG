import pygame


COLOR_SECTION = (45, 49, 57)
COLOR_SECTION_HOVER = (55, 60, 70)
COLOR_BORDER = (72, 78, 88)
COLOR_TEXT = (220, 224, 230)


def draw_section_header(screen, rect, title, expanded, action, section_id):
    mouse_pos = pygame.mouse.get_pos()
    color = COLOR_SECTION_HOVER if rect.collidepoint(mouse_pos) else COLOR_SECTION
    pygame.draw.rect(screen, color, rect)
    pygame.draw.line(screen, COLOR_BORDER, rect.bottomleft, rect.bottomright)

    font = pygame.font.SysFont("segoeui", 13, bold=True)
    arrow = "v" if expanded else ">"
    arrow_surface = font.render(arrow, True, COLOR_TEXT)
    title_surface = font.render(title, True, COLOR_TEXT)
    screen.blit(arrow_surface, (rect.x + 8, rect.y + 6))
    screen.blit(title_surface, (rect.x + 26, rect.y + 6))

    return {
        "rect": rect,
        "action": action,
        "section_id": section_id,
    }
