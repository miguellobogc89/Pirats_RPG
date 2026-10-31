# Guía de estilo visual — Pirats RPG

Objetivo: pixel art con la claridad de un RPG clásico (inspiración Pokémon Rojo/Azul, sin ser un clon), en **rejilla de 32 px** y más detallado. De momento todo se ve en **escala de grises** (el juego convierte la pantalla a grises al final de cada fotograma), así que los assets pueden generarse en color.

## 1. Reglas fijas

| Regla | Valor |
|---|---|
| Rejilla del arte | **32 × 32 px** por casilla, nativo (sin escalar) |
| Escalado | si algo se escala, siempre sin suavizado (`pygame.transform.scale`) |
| Personajes | **32 × 32** (o 32 × 48 si necesitan más altura), centrados en su casilla |
| Objetos de 1 casilla | rocas, arbustos, carteles, cofres: 32 × 32 |
| Objetos grandes | palmeras y árboles altos: 64 × 96 aprox.; edificios: múltiplos de 32 (p. ej. 160 × 128) |
| Perspectiva | cenital ligeramente inclinada (vista "desde arriba y un poco de frente") |
| Luz | desde **arriba a la izquierda**; sombra abajo a la derecha |
| Contorno | 1 px oscuro alrededor de personajes y objetos |
| Tonos | paleta limitada (5–7 tonos), sin antialiasing |
| Fuente | familia Jersey (pixel, OFL): Jersey 10 para textos pequeños, Jersey 15 en diálogos, Jersey 20 en títulos |
| Fondo | transparente (PNG) |
| Mapas | dimensiones y zonas transitables en múltiplos de **32 px** para que el arte y las colisiones coincidan |

## 2. Qué se hace por código y qué se genera

**Por código (sin gastar créditos)** — `game/world/terrain_tiles.py` y `game/world/tilemap.py`:
- Suelo: hierba, flores, camino, arena, agua.
- Bordes automáticos entre camino y hierba.
- Límites del mapa: lo que no es transitable se rellena según el tema de la escena:
  - `village` / `farm` (pueblo, granja): hierba y caminos; fuera, bosque.
  - `port` (puerto): muelle de tablones; fuera, mar.
  - `interior` (casa, talleres, posada): suelo de madera, pared encima y negro alrededor.
  - `cave` (madrigueras): suelo de cueva; fuera, rocas.
- Mapas dibujados casilla a casilla: en el JSON de la escena, `"tilemap": {"rows": [...]}` con una letra por casilla. Letras: `J` selva, `s` arena, `w` arena mojada, `~` agua, `=` agua profunda, `R` roca, `r` roca en el agua, `g` hierba, `p` camino, `d` muelle, `T` árbol. Las colisiones salen solas del terreno (selva, agua y rocas bloquean). Objetos encima en `"decor"` (naufragio, cofre, puerta, salida, palmeras). Primer mapa así: la playa.

**Con PixelLab (por prompt)**:
- Naturaleza: rocas, árboles, palmeras, arbustos (y un árbol "de borde" que sustituya al provisional del bosque).
- Personajes: protagonista (4 direcciones + andar) y NPCs.
- Edificios y objetos especiales.

## 3. Carpetas y nombres

```
assets/generated/
  nature/     rock_small_01.png, palm_01.png, tree_border.png ...
  characters/ hero_down.png, hero_walk_down_01.png, npc_herrero_down.png ...
  buildings/  house_01.png, posada.png, taller.png ...
```

Nombres en minúscula, con guion bajo y número de variante.

## 4. Plantillas de prompt

Describir solo el objeto; el estilo y el tamaño se fijan en la herramienta (16×16 o el que toque, vista top-down, fondo transparente). Usar siempre la **misma imagen de referencia de estilo** una vez elegida.

- Roca: `small grey beach rock, rounded, top-down RPG view, dark outline, light from top-left`
- Palmera: `tropical palm tree, curved trunk, top-down RPG overworld, dark outline`
- Árbol de borde: `round leafy tree that tiles seamlessly side by side to form a forest wall, top-down RPG overworld`
- Protagonista: `young pirate with bandana and short vest, top-down RPG overworld sprite, 4 directions`
- NPC: `old village elder with beard and walking stick, top-down RPG overworld sprite`
- Edificio: `small fishing village house with thatched roof and wooden door, top-down RPG overworld`

## 5. Presupuesto de la prueba gratuita (40 generaciones)

1. Prueba de estilo y elección de referencia: 3–4
2. Naturaleza (3 rocas, 2 palmeras, 2 árboles, 2 arbustos): ~9
3. Protagonista 4 direcciones + andar: ~6–8
4. NPCs principales: ~6
5. Edificios: ~4
6. Reserva para repetir: ~5

Antes de lanzar cada tipo, comprobar cuántas generaciones cuesta: algunas herramientas nuevas gastan mucho más que una.
