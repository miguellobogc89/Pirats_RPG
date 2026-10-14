"""Pure chapter-one exit resolver. Scene geometry is in modular data/scenes."""
SCENE_IDS = {
    "pueblo": "brumazul_pueblo",
    "puerto": "brumazul_puerto",
    "playa": "brumazul_playa",
    "granja": "brumazul_granja",
    "salon_posada": "brumazul_taberna",
    "habitacion_posada": "brumazul_posada",
    "taller_sylvarin": "brumazul_taller_sylvarin",
    "casa_almarin": "brumazul_casa_almarin",
    "taller_almarin": "brumazul_taller_almarin",
    "madriguera_artesana": "brumazul_madriguera",
}


def find_chapter_exit(scene_id, x, y, layout=None):
    if scene_id == "brumazul_pueblo":
        if 425 <= x <= 550 and y <= 105:
            return "brumazul_taberna", (485, 700)
        if 1035 <= x <= 1115 and 245 <= y <= 270:
            return "brumazul_taberna", (485, 700)
        if 1225 <= x <= 1285 and 425 <= y <= 450:
            return "brumazul_taller_sylvarin", (400, 555)
        if x <= 115 and 410 <= y <= 500:
            return "brumazul_granja", (780, 375)
        if 580 <= x <= 720 and y >= 960:
            return "brumazul_puerto", (400, 145)
        if 450 <= x < 580 and y >= 960:
            return "brumazul_playa", (400, 55)
    if scene_id == "brumazul_granja":
        if x >= 842 and 330 <= y <= 420:
            return "brumazul_pueblo", (145, 455)
        if 255 <= x <= 290 and 275 <= y <= 300:
            return "brumazul_casa_almarin", (400, 480)
        if 450 <= x <= 490 and 275 <= y <= 300:
            return "brumazul_taller_almarin", (400, 480)
    if scene_id == "brumazul_puerto":
        if 350 <= x <= 450 and y <= 45:
            return "brumazul_pueblo", (650, 925)
        if x <= 45 and 390 <= y <= 490:
            return "brumazul_playa", (650, 440)
    # Interior doors are introduced only after validating their scene geometry.
    return None
