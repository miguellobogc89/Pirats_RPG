# Arquitectura de IA y sigilo (microfase 3.5 cerrada)

El motor es independiente de Pygame; Unity sera el adaptador final.

## Responsabilidades

- `engine.py`: mundo, entidades, dano, ataques, eventos y compatibilidad de APIs existentes.
- `enemy_brain.py`: seleccion de estado y coordinacion de comportamientos.
- `components.py`: perfil inmutable `StealthConfig` por enemigo.
- `movement_component.py`: navegacion y movimiento evitando obstaculos.
- `behavior_components.py`: patrulla y busqueda (incluye pistas aproximadas).
- `stealth.py`: geometria, visibilidad y generacion de puntos de busqueda.
- `stealth_demo.py`: presentacion Pygame, no contiene decisiones de IA.

## Uso por enemigo

```python
from game.combat.action.engine import CombatWorld, Fighter
from game.combat.action.components import StealthConfig

world = CombatWorld(width=900, height=620)
world.add(Fighter("player", "player", 120, 310))
world.add(Fighter(
    "guard", "enemy", 565, 220,
    stealth=StealthConfig(vision_range=245, chase_speed=110,
                          search_duration=15),
    patrol_points=((565, 220), (565, 490)),
))
# Un actor sin cerebro no percibe, patrulla ni ataca automaticamente.
world.add(Fighter("decoration", "enemy", 300, 300, brain_enabled=False))
```

Sin `StealthConfig`, un enemigo mantiene la IA basica de combate
(agresion por proximidad), pero no obtiene deteccion ni patrulla por vision.
Para una entidad completamente pasiva, usar `brain_enabled=False`.

La bandera `CombatWorld.perception_enabled` existe solo para compatibilidad
con los prototipos antiguos. Para nuevos enemigos, usar `StealthConfig`.

## Estados y eventos

Patrulla -> sorpresa -> persecucion -> confusion (1 s) -> busqueda
(15 s) -> fin de busqueda (1 s) -> patrulla. Si recupera la vision,
vuelve a persecucion. Los eventos `aggro`, `confused` y
`search_ended` permiten disparar animaciones desde Unity.

## Contrato para la migracion a Unity

El cerebro decide estados, los comportamientos solicitan desplazamientos
y el adaptador reproduce eventos. Los perfiles seran ScriptableObjects,
los comportamientos componentes de Unity y la navegacion un servicio comun.

## Alcance

Esta microfase extrae los comportamientos de IA, no toda la simulacion
de combate. `Fighter` conserva temporalmente estado de combate y sigilo
por compatibilidad con el prototipo. La migracion a C# separara ese estado
sin modificar la logica ya validada en la demo.

Pruebas: `py -3.12 -m unittest tests.test_action_stealth`
Demo: `py -3.12 -m game.combat.action.stealth_demo`
