from game.world.grid_manager import world_to_grid


def get_exit_transition_for_player(scene_data, player):
    if scene_data is None:
        return None

    player_cell = list(world_to_grid(player["x"], player["y"]))

    for exit_data in scene_data.get("exits", []):
        if player_cell not in exit_data.get("cells", []):
            continue

        target_links = exit_data.get("target_links", [])

        if not target_links:
            return None

        target_link = target_links[0]
        target_scene_id = target_link.get("target_scene_id")
        target_spawn_id = target_link.get("target_spawn_id")

        if not target_scene_id:
            return None

        return {
            "exit_id": exit_data.get("id"),
            "target_scene_id": target_scene_id,
            "target_spawn_id": target_spawn_id,
        }

    return None
