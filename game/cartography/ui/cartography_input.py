import pygame

from game.cartography.expedition_setup import create_expedition_setup


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

    setup = ui_state.expedition_setup

    if setup is None or setup.region_id != region_id:
        setup = create_expedition_setup(
            region_id,
            app.expedition_manager,
            app.cartography_manager.ship_storage,
        )
        ui_state.expedition_setup = setup

    if not setup.can_launch:
        app.add_log(get_expedition_setup_error_message(setup))
        return

    result = app.expedition_manager.start_expedition(
        region_id,
        assigned_resources=setup.get_assigned_resources(),
    )

    if result["success"]:
        ui_state.pending_expedition_region_id = None
        ui_state.modal_open = False
        ui_state.expedition_setup = None
        region = app.cartography_manager.get_region_view_data(region_id)
        region_name = region["name"] if region is not None else region_id
        app.add_log(f"Expedicion iniciada: {region_name}")
        return

    app.add_log(get_expedition_error_message(result))


def get_expedition_setup_error_message(setup):
    if "region_not_reachable" in setup.validation_errors:
        return "No puedes zarpar a esa region desde el puerto actual."

    if "region_not_found" in setup.validation_errors:
        return "La region seleccionada no existe."

    if "not_enough_supplies" in setup.validation_errors:
        return f"Faltan provisiones para zarpar. Necesitas {setup.provisions_required}."

    if "cargo_capacity_exceeded" in setup.validation_errors:
        return "La carga seleccionada supera la capacidad de la bodega."

    return "No se pudo preparar la expedicion."


def get_expedition_error_message(result):
    reason = result.get("reason")

    if reason == "region_not_reachable":
        return "No puedes zarpar a esa region desde el puerto actual."

    if reason == "region_not_found":
        return "La region seleccionada no existe."

    if reason == "not_enough_supplies":
        required_supplies = result.get("required_supplies", 0)
        return f"Faltan provisiones para zarpar. Necesitas {required_supplies}."

    return "No se pudo iniciar la expedicion."
