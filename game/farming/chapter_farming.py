"""Mouse-driven farming on the existing chapter grid and inventory systems."""

from game.farming.farming_manager import (
    till_cell, water_cell, plant_crop, harvest_crop, get_crop_at_cell,
    is_crop_ready, ensure_farming_state,
)
from game.inventory.hotbar_manager import get_active_item_data, get_active_tool, get_active_item_id
from game.inventory.inventory_manager import remove_item
from game.inventory.item_transactions import receive
from game.inventory.inventory_manager import can_add_item
from game.world.grid_manager import world_to_grid
from game.world.action_range import can_interact_cell, face_target
from game.world.grid_manager import TILE_SIZE
from game.scenes.chapter_area_navigation import can_walk_chapter_area


def interact(scene, screen_pos):
    """Return True when a farming action was attempted; False for ordinary clicks."""
    app = scene.app
    player = app.state["player"]
    from game.world.camera import get_camera_position
    from game.scenes.brumazul_scene import WIDTH, HEIGHT
    cx, cy = get_camera_position(player["x"], player["y"], WIDTH, HEIGHT,
                                 scene.area_layout.get("width", 900),
                                 scene.area_layout.get("height", 760))
    wx, wy = screen_pos[0] + cx, screen_pos[1] + cy
    gx, gy = world_to_grid(wx, wy)
    tx, ty = gx * TILE_SIZE + TILE_SIZE // 2, gy * TILE_SIZE + TILE_SIZE // 2
    if not can_walk_chapter_area(scene.scene_id, tx, ty, scene.area_layout):
        return False
    state = app.state
    ensure_farming_state(state)
    crop = get_crop_at_cell(state, gx, gy)

    # Harvest takes priority over equipped tools, including on the player's tile.
    # Harvest reach is independent of the selected tool: 8 neighbors + own tile.
    if crop is not None and is_crop_ready(crop) and can_interact_cell(
        player, gx, gy, mode="eight", include_occupied=True
    ):
        face_target(player, gx, gy)
        from game.data.crop_database import get_crop_data
        data = get_crop_data(crop["crop_id"])
        if data and can_add_item(state, data["harvest_item"], data.get("harvest_amount", 1)):
            result = harvest_crop(state, tx, ty)
            if result["status"] == "harvested":
                if receive(state, result["item_id"], result["amount"]):
                    app.add_log(f"Cosechas {result['amount']} {result['item_id']}.")
                    app.skill_manager.register_action("crop_harvested")
        else:
            app.add_log("Inventario lleno.")
        return True

    tool = get_active_tool(state)
    item = get_active_item_data(state)
    mode = "eight" if tool == "watering_can" or (item and item.get("type") == "seed") else "cardinal"
    if not can_interact_cell(player, gx, gy, mode=mode, include_occupied=(mode == "eight")):
        return False
    face_target(player, gx, gy)

    if tool == "hoe":
        if till_cell(state, tx, ty):
            app.add_log("Tierra arada.")
        return True
    if tool == "watering_can":
        status = water_cell(state, tx, ty)
        if status == "watered":
            app.add_log("Tierra regada.")
        elif status == "not_tilled":
            app.add_log("Primero debes arar la tierra.")
        return True
    if item and item.get("type") == "seed" and item.get("crop_id") == "corn":
        result = plant_crop(state, tx, ty, "corn")
        if result == "planted":
            if remove_item(state, get_active_item_id(state), 1):
                app.add_log("Has sembrado maíz.")
            else:
                state["farming"]["crops"].remove(get_crop_at_cell(state, gx, gy))
        elif result == "not_tilled":
            app.add_log("Primero debes arar la tierra.")
        return True
    return False
