from game.story.story_manager import get_current_story_step
from game.story_events.story_event_database import EVENT_PHASES, STORY_EVENTS
from game.story_events.story_event_executor import execute_story_event_actions
from game.story_events.story_event_state import (
    ensure_story_event_state,
    get_flag,
    is_event_completed,
    mark_event_completed,
)


def dispatch_story_event(app, event_type, payload=None):
    payload = payload or {}
    ensure_story_event_state(app.state)
    results = []

    for phase in EVENT_PHASES:
        results.extend(process_story_event_phase(app, event_type, payload, phase))

    return results


def process_story_event_phase(app, event_type, payload, phase):
    results = []

    for story_event in STORY_EVENTS:
        if story_event.get("event") != event_type:
            continue

        if story_event.get("phase", "main") != phase:
            continue

        if story_event.get("once", True) and is_event_completed(
            app.state,
            story_event["id"],
        ):
            continue

        if not conditions_match(app.state, story_event.get("conditions", {}), payload):
            continue

        action_results = execute_story_event_actions(
            app,
            story_event.get("actions", []),
            payload,
        )
        results.append(
            {
                "event_id": story_event["id"],
                "phase": phase,
                "action_results": action_results,
            }
        )

        if story_event.get("once", True):
            mark_event_completed(app.state, story_event["id"])

    return results


def conditions_match(state, conditions, payload):
    for condition_id, expected_value in conditions.items():
        if condition_id == "story_step":
            if get_current_story_step(state) != expected_value:
                return False
            continue

        if condition_id == "flag":
            if isinstance(expected_value, dict):
                flag_id = expected_value.get("id")
                required_value = expected_value.get("value", True)
            else:
                flag_id = expected_value
                required_value = True

            if get_flag(state, flag_id) != required_value:
                return False
            continue

        if condition_id == "amount":
            if payload.get("amount", 0) < expected_value:
                return False
            continue

        if payload.get(condition_id) != expected_value:
            return False

    return True
