import pygame

from game.cartography.expedition_setup import create_expedition_setup
from game.cartography.ship_storage_transfer import (
    move_inventory_to_ship_storage,
    move_ship_storage_to_inventory,
)


def handle_cartography_event(app, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            handle_cartography_click(app, event.pos)

        return True

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            handle_cartography_escape(app)

        return True

    return True


def handle_cartography_click(app, position):
    ui_state = app.cartography_ui_state

    if ui_state.modal_open:
        handle_modal_click(app, position)
        return

    if (
        ui_state.expedition_button is not None
        and ui_state.expedition_button.collidepoint(position)
    ):
        if ui_state.selected_region_id is not None:
            ui_state.expedition_setup = create_expedition_setup(
                ui_state.selected_region_id,
                app.expedition_manager,
                app.cartography_manager.ship_storage,
                state=app.state,
            )
            ui_state.modal_open = True

        return

    for region_id, rect in ui_state.region_cells.items():
        if rect.collidepoint(position):
            ui_state.selected_region_id = region_id
            ui_state.expedition_setup = None
            return


def handle_modal_click(app, position):
    ui_state = app.cartography_ui_state

    for transfer_button in ui_state.inventory_transfer_buttons:
        if transfer_button["rect"].collidepoint(position):
            transfer_inventory_item_to_storage(app, transfer_button["item_id"])
            return

    for transfer_button in ui_state.storage_transfer_buttons:
        if transfer_button["rect"].collidepoint(position):
            transfer_storage_item_to_inventory(app, transfer_button["item_id"])
            return

    if (
        ui_state.cancel_button is not None
        and ui_state.cancel_button.collidepoint(position)
    ):
        ui_state.modal_open = False
        ui_state.expedition_setup = None
        return

    if (
        ui_state.launch_button is not None
        and ui_state.launch_button.collidepoint(position)
    ):
        launch_selected_expedition(app)


def handle_cartography_escape(app):
    ui_state = app.cartography_ui_state

    if ui_state.modal_open:
        ui_state.modal_open = False
        ui_state.expedition_setup = None
        return

    app.cartography_menu_open = False


def launch_selected_expedition(app):
    ui_state = app.cartography_ui_state
    region_id = ui_state.selected_region_id

    if region_id is None:
        app.add_log("Selecciona una region antes de zarpar.")
        return

    setup = create_expedition_setup(
        region_id,
        app.expedition_manager,
        app.cartography_manager.ship_storage,
        state=app.state,
    )
    ui_state.expedition_setup = setup

    if not setup.can_launch:
        app.add_log(get_expedition_setup_error_message(setup))
        return

    result = consume_requirements_and_start_expedition(app, region_id, setup)

    if result["success"]:
        ui_state.pending_expedition_region_id = None
        ui_state.modal_open = False
        ui_state.expedition_setup = None
        app.state["cartography"] = app.cartography_manager.get_save_data()
        region = app.cartography_manager.get_region_view_data(region_id)
        region_name = region["name"] if region is not None else region_id
        app.add_log(
            f"Expedicion iniciada: {region_name}. Requisitos consumidos."
        )
        return

    app.add_log(get_expedition_error_message(result))


def consume_requirements_and_start_expedition(app, region_id, setup):
    ship_storage = app.cartography_manager.ship_storage
    consumed_items = []
    consumed_gold = setup.gold_required

    if app.state["resources"].get("gold", 0) < setup.gold_required:
        refresh_expedition_setup(app)
        return {
            "success": False,
            "reason": "gold_consume_failed",
            "required_gold": setup.gold_required,
        }

    app.state["resources"]["gold"] -= setup.gold_required

    for item_id, required_amount in setup.required_items.items():
        if ship_storage.remove_item(item_id, required_amount):
            consumed_items.append((item_id, required_amount))
            continue

        rollback_consumed_requirements(app, consumed_gold, consumed_items)
        refresh_expedition_setup(app)
        return {
            "success": False,
            "reason": "required_item_consume_failed",
            "item_id": item_id,
            "required_amount": required_amount,
        }

    assigned_resources = setup.get_assigned_resources()
    result = app.expedition_manager.start_expedition(
        region_id,
        assigned_resources=assigned_resources,
    )

    if result["success"]:
        return result

    rollback_consumed_requirements(app, consumed_gold, consumed_items)
    refresh_expedition_setup(app)
    return result


def rollback_consumed_requirements(app, consumed_gold, consumed_items):
    app.state["resources"]["gold"] = app.state["resources"].get("gold", 0) + consumed_gold

    for item_id, amount in consumed_items:
        app.cartography_manager.ship_storage.add_item(item_id, amount)


def transfer_inventory_item_to_storage(app, item_id):
    result = move_inventory_to_ship_storage(
        app.state,
        app.cartography_manager.ship_storage,
        item_id,
        1,
    )
    handle_transfer_result(app, result)


def transfer_storage_item_to_inventory(app, item_id):
    result = move_ship_storage_to_inventory(
        app.state,
        app.cartography_manager.ship_storage,
        item_id,
        1,
    )
    handle_transfer_result(app, result)


def handle_transfer_result(app, result):
    refresh_expedition_setup(app)
    app.state["cartography"] = app.cartography_manager.get_save_data()

    if result["success"]:
        return

    app.add_log(get_transfer_error_message(result))


def refresh_expedition_setup(app):
    ui_state = app.cartography_ui_state

    if ui_state.selected_region_id is None:
        ui_state.expedition_setup = None
        return

    ui_state.expedition_setup = create_expedition_setup(
        ui_state.selected_region_id,
        app.expedition_manager,
        app.cartography_manager.ship_storage,
        state=app.state,
    )


def get_transfer_error_message(result):
    reason = result.get("reason")

    if reason == "item_type_not_allowed":
        return "Ese item no puede ir en la bodega."

    if reason == "not_enough_inventory_items":
        return "No tienes suficiente cantidad en el inventario."

    if reason == "not_enough_ship_storage_items":
        return "No hay suficiente cantidad en la bodega."

    if reason == "ship_storage_full":
        return "La bodega esta llena."

    if reason == "inventory_full":
        return "El inventario esta lleno."

    return "No se pudo mover el item."


def get_expedition_setup_error_message(setup):
    if "region_not_reachable" in setup.validation_errors:
        return "No puedes zarpar a esa region desde el puerto actual."

    if "region_not_found" in setup.validation_errors:
        return "La region seleccionada no existe."

    if "not_enough_gold" in setup.validation_errors:
        return f"Falta oro para zarpar. Necesitas {setup.gold_required}."

    if "not_enough_required_items" in setup.validation_errors:
        return "Faltan items requeridos en la bodega."

    if "cargo_capacity_exceeded" in setup.validation_errors:
        return "La carga seleccionada supera la capacidad de la bodega."

    return "No se pudo preparar la expedicion."


def get_expedition_error_message(result):
    reason = result.get("reason")

    if reason == "region_not_reachable":
        return "No puedes zarpar a esa region desde el puerto actual."

    if reason == "region_not_found":
        return "La region seleccionada no existe."

    if reason == "not_enough_gold":
        required_gold = result.get("required_gold", 0)
        return f"Falta oro para zarpar. Necesitas {required_gold}."

    if reason == "not_enough_required_items":
        return "Faltan items requeridos en la bodega."

    if reason == "gold_consume_failed":
        required_gold = result.get("required_gold", 0)
        return f"No se pudo consumir el oro. Necesitas {required_gold}."

    if reason == "required_item_consume_failed":
        return "No se pudieron consumir los items requeridos."

    return "No se pudo iniciar la expedicion."
