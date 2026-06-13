from core.data_loader import load_game_data
from core.game_state import create_initial_state, normalize_state
from core.save_manager import load_saved_state
from game.pygame_app import PygameApp
from game.world.collision_manager import load_test_collisions


def main():
    game_data = load_game_data()
    saved_state = load_saved_state()
    if saved_state is None:
        state = create_initial_state(game_data)
    else:
        state = normalize_state(saved_state)

    load_test_collisions()

    app = PygameApp(state, game_data)

    try:
        app.run()
    except KeyboardInterrupt:
        print("Juego cerrado desde terminal.")


if __name__ == "__main__":
    main()
