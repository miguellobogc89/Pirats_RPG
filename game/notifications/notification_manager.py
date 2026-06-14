MAX_VISIBLE_NOTIFICATIONS = 5

NOTIFICATION_DURATIONS = {
    "corner": 3.0,
    "center": 3.2,
    "loot": 2.2,
}


def notify(app, message, notification_type="corner"):
    notifications = get_notifications(app)
    clean_type = normalize_notification_type(notification_type)
    duration = NOTIFICATION_DURATIONS[clean_type]
    notification = {
        "message": str(message),
        "type": clean_type,
        "duration": duration,
        "time_left": duration,
    }

    notifications.append(notification)
    trim_notifications(notifications)
    return notification


def update_notifications(app, dt):
    notifications = get_notifications(app)

    for notification in notifications:
        notification["time_left"] -= dt

    app._notifications = [
        notification
        for notification in notifications
        if notification["time_left"] > 0
    ]


def get_notifications(app):
    if not hasattr(app, "_notifications"):
        app._notifications = []

    return app._notifications


def normalize_notification_type(notification_type):
    if notification_type in NOTIFICATION_DURATIONS:
        return notification_type

    return "corner"


def trim_notifications(notifications):
    if len(notifications) <= MAX_VISIBLE_NOTIFICATIONS:
        return

    del notifications[:len(notifications) - MAX_VISIBLE_NOTIFICATIONS]
