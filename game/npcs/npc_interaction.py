from game.notifications import notify
from game.dialogue import start_dialogue


def get_nearby_npc(player, npcs, interaction_range):
    closest_npc = None
    closest_distance = interaction_range

    for npc in npcs:
        dx = npc["position"]["x"] - player["x"]
        dy = npc["position"]["y"] - player["y"]
        distance = (dx * dx + dy * dy) ** 0.5

        if distance <= closest_distance:
            closest_npc = npc
            closest_distance = distance

    return closest_npc


def interact_with_npc(app, npc):
    dialogue_id = npc.get("dialogue_id")

    if dialogue_id:
        started = start_dialogue(
            app,
            dialogue_id,
            speaker_name=npc.get("name"),
            portrait_path=npc.get("portrait_path"),
        )

        if started:
            return

    notify(app, f"Hola, soy {npc['name']}", notification_type="center")
