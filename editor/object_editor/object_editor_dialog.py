import pygame

from editor.object_editor.object_preview_renderer import draw_object_preview


COLOR_OVERLAY = (0, 0, 0)
COLOR_MODAL = (34, 37, 43)
COLOR_PANEL = (42, 46, 54)
COLOR_BORDER = (95, 100, 110)
COLOR_TEXT = (230, 230, 230)
COLOR_MUTED = (165, 170, 178)
COLOR_BUTTON = (58, 64, 74)
COLOR_BUTTON_HOVER = (72, 80, 92)


def draw_text(screen, font, text, x, y, color=COLOR_TEXT):
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))


def draw_button(screen, rect, label, action):
    mouse_pos = pygame.mouse.get_pos()

    color = COLOR_BUTTON

    if rect.collidepoint(mouse_pos):
        color = COLOR_BUTTON_HOVER

    pygame.draw.rect(screen, color, rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=4)

    font = pygame.font.SysFont("consolas", 14)
    text = font.render(label, True, COLOR_TEXT)

    screen.blit(
        text,
        (
            rect.centerx - text.get_width() // 2,
            rect.centery - text.get_height() // 2,
        ),
    )

    return {
        "rect": rect,
        "action": action,
    }


def draw_field(screen, font, label, value, x, y, width):
    draw_text(screen, font, label, x, y, COLOR_MUTED)

    rect = pygame.Rect(x, y + 18, width, 28)

    pygame.draw.rect(screen, (28, 31, 36), rect, border_radius=4)
    pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=4)

    draw_text(screen, font, value, rect.x + 8, rect.y + 7)

    return rect


def draw_object_editor_dialog(screen, state, sprite=None):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    modal_w = int(screen.get_width() * 0.82)
    modal_h = int(screen.get_height() * 0.78)

    modal_x = (screen.get_width() - modal_w) // 2
    modal_y = (screen.get_height() - modal_h) // 2

    modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

    pygame.draw.rect(screen, COLOR_MODAL, modal_rect, border_radius=8)
    pygame.draw.rect(screen, COLOR_BORDER, modal_rect, 2, border_radius=8)

    font_title = pygame.font.SysFont("consolas", 20, bold=True)
    font = pygame.font.SysFont("consolas", 14)

    draw_text(screen, font_title, "Editor de objetos", modal_x + 18, modal_y + 14)

    content_y = modal_y + 54
    padding = 18

    right_w = 270
    left_w = modal_w - right_w - padding * 3

    grid_rect = pygame.Rect(
        modal_x + padding,
        content_y,
        left_w,
        modal_h - 92,
    )

    fields_x = grid_rect.right + padding
    fields_y = content_y

    pygame.draw.rect(screen, COLOR_PANEL, grid_rect, border_radius=6)
    pygame.draw.rect(screen, COLOR_BORDER, grid_rect, 1, border_radius=6)

    preview_layout = draw_object_preview(
        screen,
        grid_rect.inflate(-24, -24),
        state,
        sprite,
        32,
    )

    buttons = []

    field_w = right_w

    draw_field(screen, font, "ID", state.object_id, fields_x, fields_y, field_w)
    fields_y += 56

    draw_field(screen, font, "Nombre", state.name, fields_x, fields_y, field_w)
    fields_y += 56

    draw_field(screen, font, "Sprite", state.sprite, fields_x, fields_y, field_w)
    fields_y += 56

    draw_field(screen, font, "Tipo", state.object_type, fields_x, fields_y, field_w)
    fields_y += 56

    draw_field(
        screen,
        font,
        "Footprint",
        f"{state.footprint[0]} x {state.footprint[1]}",
        fields_x,
        fields_y,
        field_w,
    )
    fields_y += 56

    draw_field(
        screen,
        font,
        "Sprite offset",
        str(getattr(state, "sprite_offset", [0, 0])),
        fields_x,
        fields_y,
        field_w,
    )
    fields_y += 56

    draw_field(
        screen,
        font,
        "Solid",
        str(state.solid),
        fields_x,
        fields_y,
        field_w,
    )
    fields_y += 50

    load_png_rect = pygame.Rect(fields_x, fields_y, field_w, 30)
    buttons.append(draw_button(screen, load_png_rect, "Cargar PNG", "object_load_png"))
    fields_y += 38

    save_rect = pygame.Rect(fields_x, fields_y, field_w, 30)
    buttons.append(draw_button(screen, save_rect, "Guardar", "object_confirm_save"))
    fields_y += 38

    cancel_rect = pygame.Rect(fields_x, fields_y, field_w, 30)
    buttons.append(draw_button(screen, cancel_rect, "Cancelar", "object_cancel"))

    return {
        "buttons": buttons,
        "preview_layout": preview_layout,
    }