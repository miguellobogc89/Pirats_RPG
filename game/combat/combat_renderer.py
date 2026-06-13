from game.combat.ui.combat_layout import (
    draw_overlay,
    draw_main_panel,
    draw_header,
    draw_battlefield_background,
)
from game.combat.ui.combat_units import draw_units
from game.combat.ui.combat_actions import draw_actions
from game.combat.ui.combat_log import draw_log
from game.combat.ui.combat_result import draw_result_panel


def draw_combat(manager):
    if not manager.active:
        return

    app = manager.app
    combat = manager.combat

    combat["ui"]["action_buttons"] = []
    combat["ui"]["target_buttons"] = []

    draw_overlay(app)
    draw_main_panel(app)
    draw_header(app, combat)
    draw_battlefield_background(app)
    draw_units(app, combat)
    draw_actions(app, combat)
    draw_log(app, combat)
    draw_result_panel(app, combat)