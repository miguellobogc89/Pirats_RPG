SEASON_NAMES = {
    "spring": "Primavera",
    "summer": "Verano",
    "fall": "Otoño",
    "winter": "Invierno",
}

MINUTES_PER_REAL_SECOND = 10
DISPLAY_MINUTE_STEP = 10
WAKE_UP_HOUR = 6
WAKE_UP_MINUTE = 0


def ensure_time_state(state):
    if "time" not in state:
        state["time"] = {
            "hour": WAKE_UP_HOUR,
            "minute": WAKE_UP_MINUTE,
        }


def reset_time_to_wake_up(state):
    ensure_time_state(state)

    state["time"]["hour"] = WAKE_UP_HOUR
    state["time"]["minute"] = WAKE_UP_MINUTE


def update_time(state, dt):
    ensure_time_state(state)

    state["time"]["minute"] += dt * MINUTES_PER_REAL_SECOND

    while state["time"]["minute"] >= 60:
        state["time"]["minute"] -= 60
        state["time"]["hour"] += 1

    while state["time"]["hour"] >= 24:
        state["time"]["hour"] -= 24


def get_time_text(state):
    ensure_time_state(state)

    hour = int(state["time"]["hour"])
    minute = int(state["time"]["minute"])

    display_minute = int(minute / DISPLAY_MINUTE_STEP) * DISPLAY_MINUTE_STEP

    return f"{hour:02d}:{display_minute:02d}"


def get_calendar_text(state, game_data):
    seasons = ["spring", "summer", "fall", "winter"]
    season_key = seasons[state["season_index"]]
    season_name = SEASON_NAMES.get(season_key, season_key)

    return f"Día {state['day']} · {season_name}"