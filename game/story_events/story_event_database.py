SUPPORTED_EVENTS = [
    "scene_entered",
    "scene_exited",
    "area_entered",
    "area_exited",
    "npc_talked",
    "object_interacted",
    "item_collected",
    "item_total_reached",
    "object_repaired",
    "crop_planted",
    "expedition_completed",
]

SUPPORTED_ACTIONS = [
    "advance_story",
    "set_story_step",
    "notify",
    "start_dialogue",
    "give_item",
    "remove_item",
    "give_gold",
    "remove_gold",
    "unlock_recipe",
    "set_flag",
    "unset_flag",
]

SUPPORTED_CONDITIONS = [
    "story_step",
    "flag",
    "scene_id",
    "npc_id",
    "object_id",
    "interaction_id",
    "interaction_mode",
    "item_id",
    "amount",
]

EVENT_PHASES = [
    "before",
    "main",
    "after",
]


STORY_EVENTS = [
    {
        "id": "intro_arrive_port_notice",
        "event": "scene_entered",
        "phase": "main",
        "once": True,
        "conditions": {
            "story_step": "arrive_port",
            "scene_id": "intro_port",
        },
        "actions": [
            {
                "type": "notify",
                "message": "Has llegado al puerto.",
                "notification_type": "center",
            },
        ],
    },
    {
        "id": "intro_reach_farm_gate_from_area",
        "event": "area_entered",
        "phase": "after",
        "once": True,
        "conditions": {
            "story_step": "arrive_port",
            "scene_id": "farm",
        },
        "actions": [
            {
                "type": "advance_story",
            },
        ],
    },
    {
        "id": "intro_old_man_talked",
        "event": "npc_talked",
        "phase": "after",
        "once": True,
        "conditions": {
            "story_step": "talk_old_man",
        },
        "actions": [
            {
                "type": "advance_story",
            },
        ],
    },
    {
        "id": "intro_collect_wood",
        "event": "item_collected",
        "phase": "after",
        "once": True,
        "conditions": {
            "story_step": "collect_wood",
            "item_id": "wood",
            "amount": 1,
        },
        "actions": [
            {
                "type": "advance_story",
            },
        ],
    },
]
