"""Canonical entry point for the modular Pygame game.

The legacy python_simulator is not launched or imported here.
"""
import argparse

from core.data_loader import load_game_data
from core.game_state import create_initial_state, normalize_state
from core.save_manager import load_latest_saved_state
from game.pygame_app import PygameApp
from game.scenes.scene_loader import scene_exists


def main():
    parser = argparse.ArgumentParser(description="Pirats RPG - modular game")
    parser.add_argument(
        "--new-game", action="store_true",
        help="Start from a fresh game state without loading an existing save.",
    )
    parser.add_argument(
        "--test-beach", action="store_true",
        help="Launch the Brumazul beach prologue without changing saved games.",
    )
    args = parser.parse_args()

    game_data = load_game_data()
    saved_state = None if (args.new_game or args.test_beach) else load_latest_saved_state()
    state = (
        normalize_state(saved_state, game_data)
        if saved_state is not None
        else create_initial_state(game_data)
    )

    if args.test_beach:
        from game.scenes.scene_loader import load_scene_data
        beach = load_scene_data("brumazul_playa")
        state["current_scene"] = "brumazul_playa"
        state["player"]["x"] = beach["player_spawn"]["x"]
        state["player"]["y"] = beach["player_spawn"]["y"]

    # Never silently teleport the player to a hard-coded test scene.
    # Invalid legacy scene IDs fall back to the modular default.
    if not scene_exists(state.get("current_scene", "")):
        state["current_scene"] = "farm"
        state["player"]["x"] = 160
        state["player"]["y"] = 160

    app = PygameApp(state, game_data)
    if (saved_state is not None and not args.new_game) or args.test_beach:
        app.mode = "game"
        app.dispatch_scene_entered_event()

    try:
        app.run()
    except KeyboardInterrupt:
        print("Juego cerrado desde teclado")


if __name__ == "__main__":
    main()
