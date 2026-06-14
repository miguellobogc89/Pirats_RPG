from game.npcs.npc_interaction import get_nearby_npc, interact_with_npc
from game.npcs.npc_loader import load_npcs_from_scene
from game.npcs.npc_renderer import draw_npcs


__all__ = [
    "draw_npcs",
    "get_nearby_npc",
    "interact_with_npc",
    "load_npcs_from_scene",
]
