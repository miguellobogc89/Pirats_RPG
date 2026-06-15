import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAVE_FILE = PROJECT_ROOT / "save.json"
SAVE_DIR = PROJECT_ROOT / "saves"
MAX_SAVE_SLOTS = 3
SAVE_SLOT_IDS = [
    f"slot_{index}"
    for index in range(1, MAX_SAVE_SLOTS + 1)
]


def save_state(state):
    save_slot_id = state.get("save_slot_id")

    if save_slot_id not in SAVE_SLOT_IDS:
        save_slot_id = get_available_save_slot_id()

    if save_slot_id is None:
        raise RuntimeError("No hay huecos de guardado disponibles.")

    state["save_slot_id"] = save_slot_id
    save_path = get_save_slot_path(save_slot_id)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    with save_path.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)

    return save_path


def load_saved_state(save_slot_id="slot_1"):
    save_path = get_save_slot_path(save_slot_id)

    if not save_path.exists():
        return None

    with save_path.open("r", encoding="utf-8") as file:
        state = json.load(file)

    state["save_slot_id"] = save_slot_id
    return state


def list_saved_games():
    saved_games = []

    for save_slot_id in SAVE_SLOT_IDS:
        saved_state = load_saved_state(save_slot_id)

        if saved_state is None:
            continue

        saved_games.append({
            "id": save_slot_id,
            "label": get_saved_game_label(saved_state, save_slot_id),
            "path": get_save_slot_path(save_slot_id),
        })

    return saved_games


def get_latest_saved_game():
    saved_games = list_saved_games()

    if not saved_games:
        return None

    return max(
        saved_games,
        key=lambda saved_game: saved_game["path"].stat().st_mtime,
    )


def load_latest_saved_state():
    latest_saved_game = get_latest_saved_game()

    if latest_saved_game is None:
        return None

    return load_saved_state(latest_saved_game["id"])


def get_saved_game_label(saved_state, save_slot_id):
    player = saved_state.get("player", {}) if isinstance(saved_state, dict) else {}
    time = saved_state.get("time", {}) if isinstance(saved_state, dict) else {}
    slot_number = get_save_slot_number(save_slot_id)
    name = player.get("name") or f"Partida {slot_number}"
    day = saved_state.get("day", time.get("day", 1)) if isinstance(saved_state, dict) else 1
    return f"Slot {slot_number} - {name} - Dia {day}"


def get_available_save_slot_id():
    for save_slot_id in SAVE_SLOT_IDS:
        if not get_save_slot_path(save_slot_id).exists():
            return save_slot_id

    return None


def get_save_slot_path(save_slot_id):
    if save_slot_id == "slot_1":
        return SAVE_FILE

    return SAVE_DIR / f"{save_slot_id}.json"


def get_save_slot_number(save_slot_id):
    try:
        return int(save_slot_id.split("_", 1)[1])
    except (IndexError, ValueError):
        return 1
