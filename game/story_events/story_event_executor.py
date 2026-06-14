from game.dialogue import start_dialogue
from game.inventory.inventory_manager import add_item, remove_item_quantity
from game.notifications import notify
from game.story.story_manager import advance_story_step, set_story_step
from game.story_events.story_event_state import set_flag, unset_flag


def execute_story_event_actions(app, actions, payload=None):
    results = []

    for action in actions:
        results.append(execute_story_event_action(app, action, payload or {}))

    return results


def execute_story_event_action(app, action, payload):
    action_type = action.get("type")

    if action_type == "advance_story":
        return advance_story_step(app.state, app=app)

    if action_type == "set_story_step":
        return set_story_step(app.state, action.get("step_id"), app=app)

    if action_type == "notify":
        notify(
            app,
            action.get("message", ""),
            notification_type=action.get("notification_type", "corner"),
        )
        return True

    if action_type == "start_dialogue":
        return start_dialogue(
            app,
            action.get("dialogue_id"),
            speaker_name=action.get("speaker_name"),
            portrait_path=action.get("portrait_path"),
        )

    if action_type == "give_item":
        return add_item(app.state, action.get("item_id"), action.get("amount", 1))

    if action_type == "remove_item":
        return remove_item_quantity(
            app.state,
            action.get("item_id"),
            action.get("amount", 1),
        )

    if action_type == "give_gold":
        resources = app.state.setdefault("resources", {})
        resources["gold"] = resources.get("gold", 0) + action.get("amount", 0)
        return True

    if action_type == "remove_gold":
        resources = app.state.setdefault("resources", {})
        amount = action.get("amount", 0)

        if resources.get("gold", 0) < amount:
            return False

        resources["gold"] -= amount
        return True

    if action_type == "unlock_recipe":
        recipe_id = action.get("recipe_id")

        if not recipe_id:
            return False

        unlocked_recipes = app.state.setdefault("unlocked_recipes", [])

        if recipe_id not in unlocked_recipes:
            unlocked_recipes.append(recipe_id)

        return True

    if action_type == "set_flag":
        flag_id = action.get("flag")

        if not flag_id:
            return False

        set_flag(app.state, flag_id)
        return True

    if action_type == "unset_flag":
        flag_id = action.get("flag")

        if not flag_id:
            return False

        unset_flag(app.state, flag_id)
        return True

    return False
