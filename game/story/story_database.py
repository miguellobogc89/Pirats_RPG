INTRO_CHAPTER_ID = "intro"

INTRO_STEPS = [
    "arrive_port",
    "reach_farm_gate",
    "talk_old_man",
    "collect_wood",
    "repair_workshop",
    "plant_first_crop",
    "first_expedition",
]

STORY_STEP_LABELS = {
    "arrive_port": "Llega al puerto",
    "reach_farm_gate": "Ve hasta la entrada de la granja",
    "talk_old_man": "Habla con el anciano",
    "collect_wood": "Reune madera",
    "repair_workshop": "Repara el taller",
    "plant_first_crop": "Planta tu primer cultivo",
    "first_expedition": "Prepara tu primera expedicion",
}


def get_intro_step_index(step_id):
    if step_id not in INTRO_STEPS:
        return 0

    return INTRO_STEPS.index(step_id)


def get_next_intro_step(step_id):
    current_index = get_intro_step_index(step_id)
    next_index = current_index + 1

    if next_index >= len(INTRO_STEPS):
        return INTRO_STEPS[-1]

    return INTRO_STEPS[next_index]


def get_story_step_label(step_id):
    return STORY_STEP_LABELS.get(step_id, step_id)
