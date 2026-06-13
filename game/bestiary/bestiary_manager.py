from game.bestiary.bestiary_state import ensure_bestiary_state
from game.bestiary.creature_database import get_creature_data


class BestiaryManager:
    def __init__(self, state):
        self.state = state
        ensure_bestiary_state(self.state)

    def get_owned_creatures(self):
        ensure_bestiary_state(self.state)
        return self.state["bestiary"]["owned_creatures"]

    def get_active_party(self):
        ensure_bestiary_state(self.state)

        party = []
        owned_creatures = self.state["bestiary"]["owned_creatures"]

        for creature_index in self.state["bestiary"]["active_party"]:
            if creature_index < 0:
                continue

            if creature_index >= len(owned_creatures):
                continue

            party.append(owned_creatures[creature_index])

        return party

    def get_creature_display_name(self, owned_creature):
        creature_data = get_creature_data(owned_creature["creature_id"])

        if creature_data is None:
            return owned_creature["creature_id"]

        nickname = owned_creature.get("nickname")

        if nickname is not None and nickname != "":
            return f"{nickname} ({creature_data['name']})"

        return creature_data["name"]