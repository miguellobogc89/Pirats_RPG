# Combate de accion (nuevo, independiente)

Este motor se ha creado desde cero usando como referencia el encuentro de la playa y las criaturas de la granja/madriguera. **No modifica ninguna escena existente.**

## Probar

Desde la raiz del repositorio:

```bash
python -m unittest tests.test_action_combat -v
python -m game.combat.action.demo
```

La demo requiere `pygame`. Las pruebas del motor no requieren dependencias externas.

**Controles:** WASD o flechas para moverse; clic izquierdo para atacar hacia el cursor; espacio para atacar en la ultima direccion; R reinicia; ESC sale.

Incluye movimiento normalizado, orientacion, alcance y cono de ataque, cooldown, daño, invulnerabilidad, retroceso, aturdimiento, persecucion, aviso de ataque enemigo, muerte y eventos desacoplados.

**Limitaciones deliberadas:** sin colisiones con obstaculos, animaciones, inventario, misiones ni persistencia; son responsabilidades de adaptadores de escena. Las tres escenas actuales siguen usando su codigo anterior hasta una migracion posterior.
