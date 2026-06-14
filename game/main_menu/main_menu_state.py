MAIN_MENU_OPTIONS = [
    ("new_game", "Nueva partida"),
    ("load_game", "Cargar"),
    ("options", "Opciones"),
    ("quit", "Salir"),
]


def create_main_menu_state():
    return {
        "selected_index": 0,
        "hovered_index": None,
        "show_options": False,
        "show_load_game": False,
        "load_selected_index": 0,
        "load_hovered_index": None,
        "saved_games": [],
        "load_button_rects": [],
        "message": "",
        "button_rects": [],
    }
