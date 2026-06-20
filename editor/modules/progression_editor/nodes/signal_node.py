SIGNAL_TYPE_OPTIONS = [
    {"id": "interact_object", "label": "Interactuar con objeto"},
    {"id": "destroy_object", "label": "Destruir objeto"},
    {"id": "collect_item", "label": "Recolectar item"},
    {"id": "kill_enemy", "label": "Matar enemigo"},
    {"id": "enter_scene", "label": "Entrar en escena"},
    {"id": "talk_to_npc", "label": "Hablar con NPC"},
]


def get_default_signal_type_id():
    return SIGNAL_TYPE_OPTIONS[0]["id"]


def get_signal_type_label(signal_type_id):
    for option in SIGNAL_TYPE_OPTIONS:
        if option["id"] == signal_type_id:
            return option["label"]

    return "Señal desconocida"