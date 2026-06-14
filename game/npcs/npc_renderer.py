from game.ui.sprite_renderer import draw_sprite_centered


def draw_npcs(app, camera_x, camera_y):
    for npc in getattr(app, "scene_npcs", []):
        draw_npc(app, npc, camera_x, camera_y)


def draw_npc(app, npc, camera_x, camera_y):
    x = int(npc["position"]["x"] - camera_x)
    y = int(npc["position"]["y"] - camera_y)
    radius = npc.get("radius", 18)
    sprite_path = npc.get("sprite")
    selected = getattr(app, "nearby_npc", None) is not None
    selected = selected and app.nearby_npc["id"] == npc["id"]

    if sprite_path:
        sprite_rect = draw_sprite_centered(
            app.screen,
            sprite_path,
            x,
            y,
            radius * 2,
            radius * 2,
        )

        if sprite_rect is not None:
            if selected:
                app.draw_text("E", x - 5, y - radius - 26, app.WARN, app.big_font)

            draw_npc_name(app, npc, x, y, radius)
            return

    app.draw_text("N", x - 6, y - 10, app.DARK, app.big_font)
    draw_npc_name(app, npc, x, y, radius)

    if selected:
        app.draw_text("E", x - 5, y - radius - 26, app.WARN, app.big_font)


def draw_npc_name(app, npc, x, y, radius):
    app.draw_text(
        npc.get("name", npc["id"]),
        x - 34,
        y + radius + 8,
        app.DARK,
        app.small_font,
    )
