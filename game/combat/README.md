# Sistemas de combate

- `action/`: combate de acción en tiempo real (motor, IA de enemigos, sigilo y efectos). Es el sistema que usa la historia, por ejemplo el combate de la playa (`game/story/beach_monster_combat.py`). Ver `action/README.md` y `action/ARCHITECTURE.md`.
- `legacy_turn_based/`: **ANTIGUO**, combate por turnos con barras de acción. Se conserva completo; `game/pygame_app.py` sigue creando su `CombatManager`.

No confundir las barras de acción del combate antiguo con el combate libre en tiempo real.
