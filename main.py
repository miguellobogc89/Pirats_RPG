from core.data_loader import load_game_data
from core.game_state import create_initial_state, normalize_state
from core.save_manager import load_latest_saved_state
from game.pygame_app import PygameApp


def main():
    game_data = load_game_data()
    saved_state = None

    if saved_state is None:
        state = create_initial_state(game_data)
        start_in_game = False
    else:
        state = normalize_state(saved_state, game_data)
        start_in_game = True

    app = PygameApp(state, game_data)

    if start_in_game:
        app.mode = "game"
        app.dispatch_scene_entered_event()

    try:
        app.run()
    except KeyboardInterrupt:
        print("Juego cerrado desde terminal.")


if __name__ == "__main__":
    main()
