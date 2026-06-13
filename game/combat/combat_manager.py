from game.combat.combat_state import create_test_combat_state
from game.combat.combat_input import handle_combat_event
from game.combat.combat_renderer import draw_combat
from game.combat.combat_turns import update_combat


class CombatManager:
    def __init__(self, app):
        self.app = app
        self.active = False
        self.combat = None

    def is_active(self):
        return self.active

    def start_test_combat(self):
        combat_state = create_test_combat_state(self.app)

        if combat_state is None:
            return

        self.combat = combat_state
        self.active = True

    def update(self, dt):
        if not self.active:
            return

        self.update_result_timer(dt)
        update_combat(self, dt)
        self.update_visuals(dt)

    def update_visuals(self, dt):
        hp_speed = 55

        for actor in self.get_all_actors():
            if actor["display_hp"] > actor["hp"]:
                actor["display_hp"] -= hp_speed * dt

                if actor["display_hp"] < actor["hp"]:
                    actor["display_hp"] = actor["hp"]

            if actor["display_hp"] < actor["hp"]:
                actor["display_hp"] = actor["hp"]

        if self.combat["animation_timer"] > 0:
            self.combat["animation_timer"] -= dt

            if self.combat["animation_timer"] < 0:
                self.combat["animation_timer"] = 0

    def get_all_actors(self):
        actors = [
            self.combat["player"],
        ]

        for creature in self.combat["creatures"]:
            actors.append(creature)

        for enemy in self.combat["enemies"]:
            actors.append(enemy)

        return actors

    def handle_event(self, event):
        handle_combat_event(self, event)

    def end_combat(self):
        self.active = False

    def add_log(self, message):
        self.combat["log"].append(message)
        self.combat["log"] = self.combat["log"][-7:]

    def draw(self):
        draw_combat(self)

    def calculate_damage(self, actor, target, ability):
        from game.combat.combat_damage import calculate_damage

        return calculate_damage(actor, target, ability)
    
    def update_result_timer(self, dt):
        if self.combat.get("combat_result") is None:
            return

        self.combat["result_timer"] += dt

        if self.combat["result_timer"] >= self.combat["result_exit_delay"]:
            self.end_combat()