# Simulador funcional Python (independiente de Unity)

En la raiz del repositorio:

```bash
python -m pip install -r python_simulator/requirements.txt
python python_simulator/main.py
```

WASD/flechas: mover; espacio/F/clic izquierdo: atacar; E/Enter: hablar cerca de NPC; Escape: cerrar dialogo. Al morir contra el monstruo se cambia a la habitacion y se guarda `python_simulator/save.json`. En el siguiente arranque se carga la habitacion. Para reiniciar la prueba, borra `python_simulator/save.json`.

Las escenas se definen en `scenes/*.json` para reutilizar su estructura en Unity mediante un importador futuro. La simulacion Python y la implementacion Unity son motores separados; Unity no ejecuta directamente este Python. No se ha alterado ningun archivo del proyecto Unity.
