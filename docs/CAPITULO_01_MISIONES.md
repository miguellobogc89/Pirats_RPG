# PIRATS RPG — CAPÍTULO 1: RECUPERAR EL HOGAR
**Documento maestro de diseño narrativo y de misiones — v1.0 — 13/10/2026**

Este archivo es la referencia para implementar el capítulo 1 en Unity. Recoge las decisiones acordadas, separa los detalles de balance por concretar y NO implica que los sistemas estén implementados. Evitar añadir misiones principales artificiales para conversaciones, entregas de objetos o el amanecer.

## 0. Visión y reglas narrativas

- Contraste esencial: **Brumazul de día** es acogedora, luminosa y bulliciosa; **de noche** el exterior es peligroso. Las zonas seguras se conquistan mediante acciones del jugador.
- El protagonista llega en barco de noche. El marinero se marcha. Una enorme criatura legendaria y lenta lo persigue hacia un pasillo de acceso al pueblo, cerrado por una puerta. Puede intentar luchar o huir, pero al principio carece de equipo; termina inconsciente. **No programar una derrota obligatoria**: en fases posteriores, con preparación y equipo, se podrá superar la amenaza. El prólogo puede resolverse mediante desmayo/derrota en condiciones normales.
- Despierta **en la cama de la posada**, de día. El pueblo puede explorarse libremente.
- El padre del protagonista se llama **Almarin Velhart**. La finca heredada está deteriorada, pero es habitable; está fuera del recinto seguro del pueblo.
- **La verja (valla)** y la puerta aseguran el perímetro, pero no eliminan las criaturas que ya están dentro.
- El anciano conserva la llave del taller cerrado de Almarin; **no la entrega en el capítulo 1**. La identidad, nombre y motivaciones precisas del anciano se diseñarán después.
- La puerta del pueblo cierra al anochecer. Hay criaturas nocturnas más pequeñas y rápidas fuera del pueblo; pueden combatirse o esquivarse, no causan muerte automática.
- La recuperación de la playa del prólogo es una posibilidad posterior; no se completa en este capítulo.
- Un **marinero itinerante** visita el puerto algunos días; puede conocerse durante el capítulo 1 y será importante para abrir las misiones marítimas posteriores. No forzar su línea argumental aquí.

## 1. Mapa de misiones definitivo (estructura)

PRÓLOGO (no es una misión del diario)
  Llegada en barco → persecución/combate → desmayo → cama de la posada
  ↓
MISIÓN PRINCIPAL 1 — LAS TIERRAS DE ALMARIN
  Anciano pide en posada visitar la finca → llegar y hablar con él
  ↓ [en esa conversación, cierre de M1 e inicio de M2]
MISIÓN PRINCIPAL 2 — UN TECHO PROPIO
  Reparar valla → construir puerta con cerrojo → hablar con anciano → ESCRITURA
     ↳ SECUNDARIA S1 — EL HIERRO QUE CANTA
        Investigar a artesana Sylvarin → volver al herrero → CERROJO
        ↳ SECUNDARIA S2 — CUANDO CALLAN LAS CAMPANAS
           Solicitud de ayuda de artesana → requiere arma para luchar →
           limpiar taller → artesana instala campanas → BOTAS +2 y COMERCIO
  ↓
INTERVALO LIBRE: sin misión principal nueva automática.
  Explorar, vender, comprar pociones, conseguir espada y realizar S2.
  ↓ [hablar con anciano en posada, recibir espada si es la primera vez, responder «Estoy preparado»]
MISIÓN PRINCIPAL 3 — LA ÚLTIMA MADRIGUERA
  Traslado a finca de noche → incursión cerrada → criaturas/nidos → jefe
  → victoria → amanecer → finca segura → FIN DEL CAPÍTULO 1

**Regla fundamental:** cada misión principal comienza al concluir la anterior, salvo la pausa deliberada entre M2 y M3: tras recibir la escritura, M3 **no se activa automáticamente**; requiere hablar con el anciano en la posada y aceptar el desafío. S1 y S2 son misiones secundarias independientes, conectadas entre sí y con M2, sin repetir encargos para obtener más cerrojos.

## 2. Prólogo — Llegada a Brumazul

**Inicio:** desembarco nocturno en la playa; el marinero abandona el lugar.
**Desarrollo:** aparición de una criatura enorme, lenta y aterradora; persecución y posible combate. El jugador llega al corredor hacia la puerta cerrada del pueblo. No dispone del equipo adecuado. En condiciones normales acaba inconsciente.
**Final:** fundido y despertar en una cama de la posada a la mañana siguiente.
**Objetivo de diseño:** enseñar peligro, movimiento y contraste noche/día sin establecer una derrota inevitable por script.
**Pendiente de diseño:** identidad de la gran criatura, quién recoge al protagonista y explicación de su llegada a la posada.

## 3. Misión principal 1 — Las tierras de Almarin

**Activación:** en la introducción de la posada, el anciano pide al protagonista que lo busque en la **entrada de la finca**.
**Objetivo:** localizar la finca y hablar con el anciano allí.
**Finalización:** comienza la conversación en la finca, se cierra M1 y en esa misma conversación se activa M2.
**Intervienen:** anciano; posadero como presencia/contexto opcional.
**Juego:** exploración inicial libre de Brumazul; no convertir «despertar» o «hablar con alguien» en misiones extra.
**Recompensa:** avance narrativo, descubrimiento de la herencia.

## 4. Misión principal 2 — Un techo propio

**Activación:** durante la conversación que cierra M1, el anciano explica que la finca de Almarin necesita asegurar el perímetro y encarga repararlo.
**Objetivo global:** cerrar el perímetro con valla reparada y puerta provista de cerrojo.
**Intervienen:** anciano; herrero Gorathûn y artesana Sylvarin en S1.
**Finalización:** tras reparar la valla y montar la puerta, el jugador habla con el anciano y recibe la **escritura de la finca**.
**Recompensa:** escritura (recompensa narrativa/emocional), experiencia a ajustar y reconocimiento de la propiedad. No equivale a finca limpia ni totalmente segura.

### Objetivo 2.1 — Reparar la valla
- Reunir piezas de madera disponibles por el entorno.
- **Opcional:** encontrar un hacha que ya existe en la finca.
- **Opcional:** talar árboles con el hacha para obtener más madera.
- Construir/reparar los tramos de valla dañados.
- Cualquier madera adecuada sirve para esta primera reparación. **No aplicar por ahora estadísticas superiores por madera recién cortada**: las calidades, resistencia y durabilidad podrán desarrollarse posteriormente.
- Experiencia por acciones de tala/construcción según sistema de progresión; **no fijar todavía cifras ni un bonus artificial solo por encontrar el hacha**.
- Al terminar el último tramo, **se completa el objetivo**, no toda M2.

### Objetivo 2.2 — Construir e instalar la puerta
- Tras completar la valla, se hace visible la necesidad de cerrar el hueco de entrada.
- Conseguir madera y un **cerrojo con candado**.
- El herrero no tiene cerrojos disponibles; ofrece fabricar uno a cambio del favor de S1.
- Construir e instalar la puerta y colocar el cerrojo.
- **Transición automática sin intervención artificial del anciano:** al reparar el último tramo de valla se actualiza el objetivo a «Construir la puerta»; el jugador descubre el requisito del cerrojo al consultar el punto de construcción.
- Al cerrar el perímetro, regresar a hablar con el anciano para finalizar M2.

### Conversación de cierre de M2
- El anciano entrega la **escritura de Almarin**. Justificación propuesta: Almarin dejó instrucciones para entregarla cuando el heredero demostrara compromiso con la finca.
- Advierte que la valla protege frente a nuevas intrusiones, pero las criaturas ya han anidado dentro.
- Le dice al protagonista que **cuando esté preparado, lo busque en la posada**.
- El anciano se marcha; **no** inicia inmediatamente M3, **no** hace transición automática a la noche y **no** entrega pociones.
- El jugador tiene libertad real para recolectar, comerciar, explorar y preparar su equipo.

## 5. Secundaria S1 — El hierro que canta

**Activación:** el jugador pide al herrero Gorathûn un cerrojo para la puerta de la finca.
**Finalización:** investiga las piezas metálicas, regresa al herrero, le explica lo descubierto y recibe el cerrojo fabricado.
**Intervienen:** herrero Gorathûn (nombre definitivo pendiente) y artesana Sylvarin (nombre pendiente).
**Recompensa:** cerrojo para M2; desbloqueo de la línea secundaria S2. No hay que repetir S1 para obtener otro cerrojo.

### Desarrollo
1. El herrero, orgulloso y gruñón, no tiene cerrojos en existencias. Línea de humor de referencia: «¡Aquí todo el mundo tiene ya un cerrojo! ¡Hasta los gallineros están cerrados!».
2. Sospecha que una artesana Sylvarin está copiando su trabajo porque le encargó piezas metálicas inusuales; pide investigar qué fabrica a cambio de forjar el cerrojo.
3. El jugador visita a la artesana y descubre que está fabricando **campanas/campanillas** para ahuyentar pequeñas criaturas parecidas a ratas que han ocupado su taller.
4. La artesana conoce por tradición Sylvarin que el sonido de esas campanas puede disuadir a tales criaturas; **no ha podido instalarlas dentro porque el taller está infestado**. El metal es necesario por el sonido que produce, no para imitar el oficio del herrero.
5. La artesana pide ayuda para recuperar el taller. Se abre S2, que podrá completarse cuando el protagonista consiga un arma.
6. El jugador vuelve al herrero, resuelve el malentendido y obtiene el cerrojo.

**Tono:** humor de carácter y fricción cultural personal, no hostilidad racial genérica. Diálogos definitivos pendientes.
**Decisiones de diálogo:** se había explorado permitir decir la verdad o alimentar las sospechas; **no se ha confirmado como mecánica definitiva**. Si se implementa, no debe bloquear el cerrojo ni S2.

## 6. Secundaria S2 — Cuando callan las campanas

**Activación:** la artesana Sylvarin explica que su taller está ocupado por pequeñas criaturas y solicita ayuda durante S1. La misión puede quedar pendiente hasta obtener una espada.
**Requisito de ejecución:** poseer un arma con la que eliminar las criaturas. No exigir haber completado M3.
**Finalización:** el jugador limpia el taller, elimina el foco/nido, la artesana entra e instala las campanas y el taller reabre.
**Intervienen:** artesana Sylvarin y criaturas pequeñas similares a ratas.
**Recompensas:**
- **Botas de cuero Sylvarin: +2 defensa**, fabricadas con materiales que trabaja la artesana.
- **Desbloqueo permanente de compra/venta en su taller** de materiales orgánicos: cuero, fibras vegetales, pieles, hierbas y otros materiales coherentes con su oficio.
- Posibilidad futura de ampliar el comercio/cadena secundaria, por diseñar.

### Desarrollo
1. El jugador descubre el encargo en S1, pero inicialmente no tiene arma.
2. Tras obtener la espada del anciano, puede **optar por hacer S2 antes de la incursión principal**, o ir directamente a la finca.
3. Entra solo en el taller y derrota unas pocas criaturas **mucho más fáciles que el jefe de la finca**; localiza y elimina el pequeño nido.
4. La artesana entra una vez despejado el interior e instala las campanas.
5. Se oye su sonido y se muestra que disuaden nuevas intrusiones. **Las campanas no sustituyen el combate:** el jugador elimina las criaturas que ya estaban dentro y las campanas previenen que regresen.
6. La artesana entrega las botas y habilita su comercio.

**Propósito sistémico:** primer combate opcional de baja dificultad, recompensa tangible de preparación para M3, ejemplo de liberar una zona/negocio que cambia permanentemente el mundo.
**Importante:** el jugador puede ignorar S2, incluso tras comenzar M3; tras morir podrá volver a realizarla.

## 7. Interludio de preparación y entrega de la espada

**Tras M2:** no hay misión principal activa de forma automática. El anciano espera en la posada.
**Primer encuentro con el anciano en la posada:** explica que las criaturas ya están dentro de la finca y entrega la **espada básica de Almarin**. **No entrega pociones**.
**Pregunta:** «¿Estás preparado?».
- **No / Todavía no:** conserva la espada; puede explorar, comerciar, comprar pociones, hacer S2, recolectar y vender. No se inicia M3.
- **Sí / Estoy preparado:** el anciano dice que explicará el plan **en la finca esa noche**; se activa M3 y se hace la transición a la incursión nocturna.
- En conversaciones posteriores vuelve a preguntar si está preparado; **no vuelve a entregar espada**.

**Diseño intencional de aprendizaje:** un jugador impaciente puede aceptar de inmediato y descubrir que el jefe es muy difícil con solo la espada. Un jugador atento puede comprar pociones y/o hacer S2 para obtener botas +2. No forzar ni anunciar una ruta óptima. La victoria sin botas/pociones debe seguir siendo posible con habilidad; evitar muertes programadas o dificultad arbitraria.

## 8. Misión principal 3 — La última madriguera

**Activación:** en la posada, el jugador responde afirmativamente a «¿Estás preparado?» después de obtener la espada (si aún no la tenía).
**Inicio jugable:** transición a **dentro de la finca por la noche**. El anciano explica brevemente allí el objetivo, sale de la finca y **cierra la puerta desde fuera**.
**Regla de incursión:** **VENCER O MORIR**. Una vez dentro, no se puede salir ni abandonar voluntariamente la misión.
**Finalización:** derrotar al jefe de la infestación y neutralizar su última madriguera.
**Intervienen:** anciano solo en la escena inicial; criaturas nocturnas y jefe en el combate.
**Recompensa:** finca libre de infestación, experiencia y materiales/loot del jefe por concretar; transición al amanecer y fin del capítulo.

### Secuencia jugable
1. Traslado nocturno al interior de la finca; el anciano explica el problema y sale cerrando la puerta. Justificación narrativa sugerida: impedir que las criaturas escapen del perímetro.
2. Explorar la finca de noche; luchar contra criaturas pequeñas y localizar focos/nidos.
3. Progresar hasta la madriguera mayor y enfrentarse a un jefe más resistente, con ataques reconocibles y esquivables.
4. Al derrotarlo y eliminar el foco final, la misión termina.
5. Fundido a negro y amanecer. El jugador queda libre en una finca tranquila y segura; **no aparece el anciano inmediatamente** ni se lanza otra misión principal.

### Dificultad y preparación
- **Solo espada:** enfrentamiento muy difícil, pero técnicamente ganable.
- **Espada + pociones compradas:** combate exigente pero razonable.
- **Espada + pociones + botas Sylvarin (+2 defensa):** ventaja clara, sin trivializar al jefe.
- Las botas deben afectar de forma perceptible el daño recibido; números finales dependen del sistema de combate.
- Las criaturas de S2 son bastante más sencillas que las de esta misión.

### Derrota y reintentos
- Si muere, el jugador **despierta en la posada**; conserva la espada, el equipamiento y los objetos de misión.
- Puede comprar más pociones, reunir recursos, completar S2 y prepararse antes del siguiente intento.
- Para reintentar debe volver a hablar con el anciano en la posada y responder «Estoy preparado». Se repite la transición nocturna y el cierre de la puerta, **pero sin entregar otra espada** ni repetir íntegra la exposición narrativa.
- **Pendiente de decidir en implementación:** si las criaturas/nidos ya eliminados persisten entre intentos o se reinicia la incursión. Se había propuesto conservar progreso, pero la nueva regla «vencer o morir» exige revisar el balance y la coherencia del reintento. No asumir una de las opciones sin decidirla.
- **Pendiente:** penalización por derrota, si existe; no perder objetos clave ni bloquear el progreso.

### Escala provisional, no cerrada
- Duración orientativa: **10–15 minutos o más** de exploración/combate, no un encuentro fugaz.
- Esquema de referencia sujeto a prototipo: enemigos iniciales aislados → grupos en jardín/huerta → madriguera mayor y jefe.
- Número, tipos de criaturas, patrones del jefe, salud, daño, número de nidos y checkpoints: **pendientes de diseño y pruebas**.

## 9. Fin del capítulo — El hogar recuperado

**Disparador:** victoria contra el jefe y neutralización del foco final.
**Secuencia:** fundido a negro → mañana luminosa → finca silenciosa, sin infestación → exploración libre.
**Resultado:** finca segura y utilizable como hogar (cama, descanso, almacenamiento y usos básicos por implementar). La casa sigue deteriorada y necesitará reformas futuras.
**No crear una misión independiente** para «entrar en la casa», «amanecer» o «recibir felicitaciones».
**No hacer aparecer al anciano inmediatamente** para entregar la llave del taller o encadenar otra misión.

### Ganchos posteriores, no parte obligatoria de C1
- Taller de Almarin cerrado y llave custodiada por el anciano; misterio de la herencia.
- Nuevos encargos de la artesana/herrero, aprovechando el comercio desbloqueado.
- Marinero itinerante del puerto y futuras expediciones marítimas.
- Playa del prólogo: limpieza, protección y aprovechamiento posterior.
- Desarrollo de reformas, agricultura y ampliación de la finca.

## 10. Requisitos de implementación en Unity

### Sistema de misiones
- Separar **misiones principales**, **secundarias** y **objetivos/subobjetivos**. M2 contiene valla y puerta: **no son dos misiones principales**.
- Cada misión con ID estable, estados (bloqueada/disponible/activa/completada), disparadores, condiciones y recompensas.
- S1 y S2 son independientes de la misión principal, aunque S1 proporciona el cerrojo necesario para M2. S2 no debe bloquear M3.
- Mantener **pausa sin misión principal activa** entre escritura y aceptación de la incursión; la espada se entrega antes de elegir.
- NPCs consultan estados de misión e inventario para escoger diálogo. No codificar cada progresión como lógica aislada en cada NPC.
- Guardado de: estado de misiones, escritura, espada entregada, materiales, equipo, tienda desbloqueada, estado de taller, puerta/valla, finca segura y resultado de la incursión.
- La puerta cerrada de la finca durante M3 impide salir; al morir o vencer se sale del estado de incursión.
- Preparar diálogos ramificados para «Estoy preparado / Todavía no» y reintentos sin recompensa duplicada.

### Sistemas que este capítulo necesita
1. Exploración diurna/nocturna, transiciones de tiempo y zonas seguras.
2. Interacción y conversaciones con NPC.
3. Inventario, equipamiento, estadísticas de defensa, consumibles.
4. Recolección de madera, herramienta hacha, tala opcional, energía y construcción de valla/puerta.
5. Comercio, compra/venta y desbloqueo persistente de taller.
6. Misiones con objetivos opcionales y dependencias; recompensas narrativas e inventario.
7. Combate, enemigos, nidos, jefe, derrota/reaparición y reintento.
8. Guardado/carga de estado del mundo.

## 11. Pendientes explícitos (no bloquear el inicio de implementación de sistemas)
- Nombres, biografías y diálogos definitivos del anciano, herrero y artesana.
- Cantidades de materiales, experiencia y precios; duración de jornadas, campana y horarios.
- Ubicaciones definitivas en el mapa, arte y tipos de criaturas.
- Reglas exactas de persistencia de nidos tras morir, balance del jefe y penalización de derrota.
- Justificación final de por qué el anciano conserva la espada y la llave del taller.
- Si habrá decisiones morales en S1 y cuáles son sus efectos.
- Identidad/lore del gran monstruo del prólogo y del jefe de la finca.

**Criterio rector:** el capítulo enseña a explorar, trabajar, comerciar, elegir, prepararse y luchar a través de una motivación clara: **recuperar un hogar**. El jugador decide cuándo exponerse al desafío principal; la curiosidad y las misiones secundarias hacen más llevadero el combate sin volverse obligatorias.
