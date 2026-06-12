MARITIME RPG PROTOTYPE V4

Objetivo:
- Separar mecanica, datos, editor y visualizacion.
- Evitar cambiar codigo para balancear valores.

Ejecutar juego:
python main.py

Ejecutar editor de balance:
python editor.py

Dependencias:
pip install pygame

Controles juego:
Flechas: moverse entre zonas
Enter: ejecutar accion de zona
D: dormir / avanzar dia
S: guardar
ESC: abrir/cerrar menu
LEFT/RIGHT: cambiar tabs dentro del menu

Arquitectura:
core/rules_engine.py -> reglas del juego
data/*.json -> datos editables
editor.py -> editor visual de balance
main.py -> juego Pygame

Notas:
- Esta v4 no busca belleza final.
- Busca una base estable para validar reglas y balance.
- El siguiente paso seria mejorar el editor para crear recursos/rutas con formularios mas seguros.
