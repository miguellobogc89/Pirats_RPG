SEASON_NAMES = {
    "spring": "Primavera",
    "summer": "Verano",
    "fall": "Otoño",
    "winter": "Invierno",
}


def ensure_time_state(state):
    if "time" not in state:
        state["time"] = {
            "hour": 6,
            "minute": 0,
        }


def update_time(state, dt):
    ensure_time_state(state)

    # 1 segundo real = 1 minuto de juego
    state["time"]["minute"] += dt * 1

    if state["time"]["minute"] >= 60:
        state["time"]["minute"] -= 60
        state["time"]["hour"] += 1

    if state["time"]["hour"] >= 24:
        state["time"]["hour"] = 0


def get_time_text(state):
    ensure_time_state(state)

    hour = int(state["time"]["hour"])
    minute = int(state["time"]["minute"])

    return f"{hour:02d}:{minute:02d}"


def get_calendar_text(state, game_data):
    seasons = ["spring", "summer", "fall", "winter"]
    season_key = seasons[state["season_index"]]
    season_name = SEASON_NAMES.get(season_key, season_key)

    return f"Día {state['day']} · {season_name}"