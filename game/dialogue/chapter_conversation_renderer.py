"""Pygame presentation of conversations; story text stays in JSON."""
import pygame


def draw_chapter_conversation(scene, speaker, message, choices=None, selected=0):
    from game.scenes.brumazul_scene import WIDTH, HEIGHT, WHITE, LIGHT, INK
    s = scene.app.screen
    rect = pygame.Rect(35, HEIGHT - 190, WIDTH - 70, 140)
    pygame.draw.rect(s, WHITE, rect)
    pygame.draw.rect(s, LIGHT, rect, 1)
    scene.label(speaker, 55, HEIGHT - 173)
    if choices:
        for i, choice in enumerate(choices):
            scene.label(("> " if i == selected else "  ") + choice, 58, HEIGHT - 147 + i * 25)
    else:
        words, line, y = message.split(), "", HEIGHT - 144
        for word in words:
            trial = (line + " " + word).strip()
            if scene.app.small_font.size(trial)[0] > WIDTH - 125 and line:
                scene.label(line, 58, y)
                y += 22
                line = word
            else:
                line = trial
        if line:
            scene.label(line, 58, y)
    scene.label("ENTER / ESPACIO", WIDTH - 175, HEIGHT - 73)
