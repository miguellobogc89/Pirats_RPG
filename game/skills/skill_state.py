def create_default_skill_state():
    return {
        "level": 1,
        "xp": 0,
        "total_xp": 0,
    }


def create_default_skills_state(skill_database):
    skills = {}

    for skill_id in skill_database:
        skills[skill_id] = create_default_skill_state()

    return skills