import pygame

from game.data.item_database import get_item_data
from game.inventory.hotbar_manager import get_active_hotbar_index
from game.inventory.inventory_state import INVENTORY_COLUMNS, INVENTORY_ROWS
from game.inventory.stash_state import STASH_COLUMNS, STASH_ROWS, ensure_stash_state
from game.ui.slot_renderer import draw_slot
from game.ui.ui_components import TEXT_DARK, draw_panel


STASH_RECT = pygame.Rect(90, 55, 780, 540)
SLOT_SIZE = 50
SLOT_GAP = 7


def draw_stash_overlay(app):
    ensure_stash_state(app.state)

    overlay = pygame.Surface((app.screen.get_width(), app.screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 135))
    app.screen.blit(overlay, (0, 0))

    draw_panel(app.screen, STASH_RECT)
    app.draw_text("Cofre", STASH_RECT.x + 28, STASH_RECT.y + 22, TEXT_DARK, app.big_font)
    app.draw_text("Inventario", STASH_RECT.x + 28, 358, TEXT_DARK, app.big_font)
    app.draw_text("ESC cerrar", STASH_RECT.right - 112, STASH_RECT.y + 28, TEXT_DARK, app.small_font)

    mouse_pos = pygame.mouse.get_pos()
    app.stash_slot_hitboxes = []
    app.inventory_slot_hitboxes = []

    hovered_slot = draw_grid(
        app,
        container_id="stash",
        grid=app.state["stash"]["grid"],
        rows=STASH_ROWS,
        columns=STASH_COLUMNS,
        x0=get_grid_x(app.screen.get_width(), STASH_COLUMNS),
        y0=112,
        mouse_pos=mouse_pos,
        hitboxes=app.stash_slot_hitboxes,
    )
    inventory_hovered_slot = draw_grid(
        app,
        container_id="inventory",
        grid=app.state["inventory"]["grid"],
        rows=INVENTORY_ROWS,
        columns=INVENTORY_COLUMNS,
        x0=get_grid_x(app.screen.get_width(), INVENTORY_COLUMNS),
        y0=405,
        mouse_pos=mouse_pos,
        hitboxes=app.inventory_slot_hitboxes,
        active_hotbar_index=get_active_hotbar_index(app.state),
        show_hotkeys=True,
    )

    if inventory_hovered_slot is not None:
        hovered_slot = inventory_hovered_slot

    if (
        not app.slot_ui_state.is_dragging
        and hovered_slot is not None
        and hovered_slot["slot"] is not None
    ):
        draw_slot_tooltip(app, hovered_slot["slot"], mouse_pos)

    if app.slot_ui_state.is_dragging and app.slot_ui_state.dragged_stack is not None:
        draw_dragged_stack(app, app.slot_ui_state.dragged_stack, mouse_pos)


def get_grid_x(screen_width, columns):
    grid_width = columns * SLOT_SIZE + (columns - 1) * SLOT_GAP
    return (screen_width - grid_width) // 2


def draw_grid(
    app,
    container_id,
    grid,
    rows,
    columns,
    x0,
    y0,
    mouse_pos,
    hitboxes,
    active_hotbar_index=None,
    show_hotkeys=False,
):
    hovered_slot = None
    slot_ui_state = app.slot_ui_state

    for row_index in range(rows):
        row = []

        if row_index < len(grid):
            row = grid[row_index]

        for column_index in range(columns):
            slot = None

            if column_index < len(row):
                slot = row[column_index]

            slot_index = row_index * columns + column_index
            slot_rect = pygame.Rect(
                x0 + column_index * (SLOT_SIZE + SLOT_GAP),
                y0 + row_index * (SLOT_SIZE + SLOT_GAP),
                SLOT_SIZE,
                SLOT_SIZE,
            )
            hovered = slot_rect.collidepoint(mouse_pos)
            hitbox = {
                "container_id": container_id,
                "rect": slot_rect,
                "row": row_index,
                "column": column_index,
                "index": slot_index,
                "slot": slot,
            }
            hitboxes.append(hitbox)

            if hovered:
                hovered_slot = hitbox

            visible_slot = slot

            if (
                slot_ui_state.is_dragging
                and slot_ui_state.drag_origin is not None
                and slot_ui_state.drag_origin.container_id == container_id
                and slot_ui_state.drag_origin.index == slot_index
            ):
                visible_slot = None

            selected = False

            if container_id == "inventory" and row_index == 0:
                selected = column_index == active_hotbar_index

            hotkey_label = None

            if show_hotkeys and row_index == 0:
                hotkey_label = str(column_index + 1)

            draw_slot(
                app.screen,
                slot_rect,
                visible_slot,
                app.font,
                app.small_font,
                selected=selected,
                hovered=hovered,
                hotkey_label=hotkey_label,
                text_color=TEXT_DARK,
                hotkey_position="top",
            )

    return hovered_slot


def draw_slot_tooltip(app, slot, mouse_pos):
    item_data = get_item_data(slot["item_id"])

    if item_data is None:
        return

    lines = [
        item_data["name"],
        item_data.get("description", "Sin descripcion."),
        f"Cantidad: {slot['amount']}",
        f"Tipo: {item_data.get('type', 'desconocido')}",
        f"ID: {slot['item_id']}",
    ]
    padding = 10
    line_height = 18
    width = max(app.small_font.size(line)[0] for line in lines) + padding * 2
    height = len(lines) * line_height + padding * 2
    tooltip_x = mouse_pos[0] + 14
    tooltip_y = mouse_pos[1] + 14

    if tooltip_x + width > app.screen.get_width():
        tooltip_x = mouse_pos[0] - width - 14

    if tooltip_y + height > app.screen.get_height():
        tooltip_y = mouse_pos[1] - height - 14

    tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, width, height)
    draw_panel(app.screen, tooltip_rect)

    text_y = tooltip_rect.y + padding

    for line in lines:
        app.draw_text(line, tooltip_rect.x + padding, text_y, TEXT_DARK, app.small_font)
        text_y += line_height


def draw_dragged_stack(app, stack, mouse_pos):
    drag_rect = pygame.Rect(
        mouse_pos[0] - SLOT_SIZE // 2,
        mouse_pos[1] - SLOT_SIZE // 2,
        SLOT_SIZE,
        SLOT_SIZE,
    )
    draw_slot(
        app.screen,
        drag_rect,
        stack,
        app.font,
        app.small_font,
        selected=True,
        text_color=TEXT_DARK,
    )
