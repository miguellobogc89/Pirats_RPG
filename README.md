# Pirats RPG

RPG de piratas en Python + Pygame. El capítulo 1 transcurre en Brumazul (playa, pueblo, posada, granja, puerto y talleres).

## Requisitos

```
pip install pygame
```

## Ejecutar

| Comando | Qué hace |
|---|---|
| `python main.py` | Juego. Carga la última partida guardada si existe. |
| `python main.py --new-game` | Empieza una partida nueva sin cargar guardados. |
| `python main.py --test-beach` | Prueba el prólogo de la playa sin tocar las partidas guardadas. |
| `python -m editor.editor_app` | Editor de escenas, objetos y progresión (Pygame). |
| `python editor.py` | Editor de balance antiguo (tkinter) para `data/*.json` de recursos, rutas y mejoras. |
| `python -m unittest discover tests` | Pruebas automáticas. |

## Estructura

- `main.py`: punto de entrada del juego.
- `core/`: reglas base, estado inicial, carga de datos y guardado.
- `game/`: sistemas del juego (escenas, combate, historia, diálogos, inventario, cultivo, crafteo, construcción, cartografía, HUD…).
  - `game/combat/action/`: combate de acción en tiempo real.
  - `game/combat/legacy_turn_based/`: combate antiguo por turnos (se conserva).
- `data/`: datos editables en JSON.
  - `data/scenes/`: escenas; `data/chapter_layouts/`: mapas transitables del capítulo 1.
  - `data/objects/`: definiciones de objetos del editor.
  - `data/dialogues/`, `data/missions/`: textos y misiones del capítulo 1.
- `editor/`: editor de escenas, objetos y progresión.
- `assets/`: sprites, iconos y bitmaps.
- `docs/`: diseño de misiones.
- `tests/`: pruebas.

## Partidas guardadas

Se guardan en `saves/slot_1.json`, `slot_2.json` y `slot_3.json`. Esa carpeta no se sube al repositorio.
Si existe un `save.json` antiguo en la raíz, el juego lo mueve automáticamente a `saves/slot_1.json`.
Un guardado dañado no bloquea el arranque: se renombra a `*.corrupt.json` y se ignora.

## Notas de prueba

Al cargar una partida se entregan materiales de prueba (madera, piedra, cuerda) y se rellena el inventario para probar el crafteo. Cada entrega ocurre una sola vez por partida.
