from core.data_loader import load_game_data
from core.game_state import create_initial_state
from core.save_manager import load_saved_state
from game.pygame_app import PygameApp


def main():
    game_data = load_game_data()
    saved_state = load_saved_state()
    if saved_state is None:
        state = create_initial_state(game_data)
    else:
        state = saved_state

    app = PygameApp(state, game_data)
    app.run()


if __name__ == "__main__":
    main()
