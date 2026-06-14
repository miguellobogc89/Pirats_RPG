from core.data_loader import load_game_data
from core.game_state import create_initial_state
from game.pygame_app import PygameApp


def main():
    game_data = load_game_data()
    state = create_initial_state(game_data)
    app = PygameApp(state, game_data)

    try:
        app.run()
    except KeyboardInterrupt:
        print("Juego cerrado desde terminal.")


if __name__ == "__main__":
    main()
