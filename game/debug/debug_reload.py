import os
import sys

from core.save_manager import save_state


def restart_game_with_current_state(state):
    save_state(state)

    os.execv(
        sys.executable,
        [sys.executable] + sys.argv,
    )