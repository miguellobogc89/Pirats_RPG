"""Independent notification API: loot stacks, quest updates and acknowledged alerts."""
MAX_VISIBLE_NOTIFICATIONS = 6
NOTIFICATION_DURATIONS = {"corner": 4.0, "center": 0, "loot": 2.6}


def get_notifications(app):
    if not hasattr(app, "_notifications"):
        app._notifications = []
    return app._notifications


def notify(app, message, notification_type="corner", *, item_id=None, amount=1, title=None):
    kind = notification_type if notification_type in NOTIFICATION_DURATIONS else "corner"
    entry = {"type": kind, "message": str(message), "title": title or "",
             "item_id": item_id, "amount": amount,
             "duration": NOTIFICATION_DURATIONS[kind],
             "time_left": NOTIFICATION_DURATIONS[kind]}
    notifications = get_notifications(app)
    notifications.append(entry)
    # Never discard an important alert awaiting acknowledgement.
    for old in list(notifications):
        if len(notifications) <= MAX_VISIBLE_NOTIFICATIONS:
            break
        if old["type"] != "center":
            notifications.remove(old)
    return entry


def notify_loot(app, item_id, amount=1):
    from game.data.item_database import get_item_data
    data = get_item_data(item_id) or {}
    return notify(app, data.get("name", item_id), "loot", item_id=item_id, amount=amount)


def notify_quest(app, message):
    return notify(app, message, "corner")


def notify_important(app, message, title="Aviso importante"):
    return notify(app, message, "center", title=title)


def active_important(app):
    return next((n for n in get_notifications(app) if n["type"] == "center"), None)


def acknowledge_important(app):
    active = active_important(app)
    if active is None:
        return False
    get_notifications(app).remove(active)
    return True


def handle_notification_event(app, event):
    import pygame
    if active_important(app) is None:
        return False
    if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
        acknowledge_important(app)
        return True
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        from game.notifications.notification_renderer import important_button_rect
        if important_button_rect(app.screen).collidepoint(event.pos):
            acknowledge_important(app)
        return True
    # Important notifications are modal until acknowledged.
    return True


def update_notifications(app, dt):
    for notification in get_notifications(app):
        if notification["type"] != "center":
            notification["time_left"] -= dt
    app._notifications = [n for n in get_notifications(app)
                          if n["type"] == "center" or n["time_left"] > 0]


def notify_character_dialogue(scene, message, speaker="Yo"):
    """Character speech uses the existing dialogue panel, never corner alerts.

    Unlike status notifications this is opened by an explicit interaction and
    dismissed using the scene's normal dialogue controls.
    """
    if scene.npc_dialogue is not None:
        return False
    scene.npc_dialogue = (speaker, [str(message)])
    scene.npc_dialogue_index = 0
    return True
