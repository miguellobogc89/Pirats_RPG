# Laboratorio de combate de accion — fase 1

Este modulo es independiente de las escenas del capitulo 1 y **no lee ni escribe save.json**.

## Ejecutar

Desde la raiz del repositorio (Windows):

```powershell
py -3.12 -m unittest tests.test_action_combat -v
py -3.12 -m game.combat.action.demo
```

La demo requiere `pygame`; el motor y sus pruebas solo usan la biblioteca estandar.

**Controles:** WASD/flechas mover, clic izquierdo atacar hacia el cursor, espacio atacar hacia la ultima direccion, R reiniciar y ESC salir.

## Fase 1

- Numeros flotantes de daño, distintos para daño recibido e infligido.
- Flash blanco o rojo por impacto e indicador intermitente de invulnerabilidad.
- Chispas/particulas, estela de ataque y efectos distintos para fallos y golpes a invulnerables.
- Hitstop visual, sacudida de camara y efecto ampliado al morir.
- Retroceso, aturdimiento y bloqueo temporal de movimiento y ataques (reglas del motor).
- Indicadores de aturdimiento y aro de invulnerabilidad.
- Eventos con coordenadas, duracion e intensidad, reutilizables por un adaptador Unity.

## Arquitectura para migracion a Unity

- `engine.py`: reglas de combate sin Pygame; eventos `attack`, `miss`, `blocked`, `hit`, `stun`, `invulnerability`, `death`, `aggro` y `telegraph`.
- `feedback.py`: adaptador de efectos exclusivamente Pygame; **no calcula daño**.
- `demo.py`: orquestacion y dibujo de la arena.
- `tests/test_action_combat.py`: pruebas de reglas y contrato de eventos.

En Unity, portar las reglas a C# y consumir estos eventos con VFX, UI y camara nativos. Los sprites, las particulas Pygame y la camara no se trasladan literalmente. El hitstop de esta demo pausa la simulacion de forma visual y no modifica el tiempo de las reglas.

**Limitaciones:** no hay obstaculos, animaciones definitivas, inventario, misiones ni persistencia. Las escenas existentes no se han migrado.


## Fase 2 — jugador

- WASD: movimiento.
- Clic izquierdo (soltar): ataque cuerpo a cuerpo; combo de tres golpes. Mantener 0,55 s y soltar: golpe cargado (28 de energía).
- Clic derecho: proyectil hacia el cursor (12 de energía, recarga 0,75 s).
- Espacio: dash hacia WASD o la orientación actual (24 de energía, recarga 0,72 s, invulnerabilidad breve).
- Energía regenerable (19/s), proyectiles con colisiones y caducidad, eventos shoot/dash independientes de Pygame.
- El golpe normal se ejecuta al soltar el botón izquierdo para distinguirlo del golpe cargado.
