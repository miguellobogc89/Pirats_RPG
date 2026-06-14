def create_default_story_event_state():
    return {
        "completed_events": [],
        "flags": {},
    }


def ensure_story_event_state(state):
    if not isinstance(state.get("story_events"), dict):
        state["story_events"] = create_default_story_event_state()

    story_event_state = state["story_events"]

    if not isinstance(story_event_state.get("completed_events"), list):
        story_event_state["completed_events"] = []

    if not isinstance(story_event_state.get("flags"), dict):
        story_event_state["flags"] = {}

    return story_event_state


def is_event_completed(state, event_id):
    story_event_state = ensure_story_event_state(state)
    return event_id in story_event_state["completed_events"]


def mark_event_completed(state, event_id):
    story_event_state = ensure_story_event_state(state)

    if event_id not in story_event_state["completed_events"]:
        story_event_state["completed_events"].append(event_id)


def get_flag(state, flag_id):
    story_event_state = ensure_story_event_state(state)
    return bool(story_event_state["flags"].get(flag_id))


def set_flag(state, flag_id, value=True):
    story_event_state = ensure_story_event_state(state)
    story_event_state["flags"][flag_id] = bool(value)


def unset_flag(state, flag_id):
    story_event_state = ensure_story_event_state(state)
    story_event_state["flags"].pop(flag_id, None)
