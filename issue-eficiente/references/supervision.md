# Supervisión y métricas

Lee esta referencia al activar el supervisor independiente definido en `SKILL.md`, cuando el usuario pida un monitor externo o sea necesario interpretar telemetría. La comprobación habitual sigue perteneciendo al coordinador.

## Responsabilidades

| Responsable | Qué puede comprobar | Límite |
| --- | --- | --- |
| Coordinador | Progreso, relación de cambios con aceptación, reparto, reintentos, calidad de relevos | Comparte contexto y posibles errores con la ejecución |
| Aplicación/harness | Capacidades que su versión realmente exponga: límites, compactación, estados, permisos, eventos de uso | No presupongas que juzga pertinencia de cambios ni optimiza el gasto de cada issue |
| Supervisor independiente | Revisar una anomalía con contrato, diff y evidencia acotada | También consume tokens; no necesita leer toda la conversación |

Una skill guía turnos activos. No ejecuta un proceso permanente ni garantiza revisiones con cadencia exacta cuando el agente está ocupado, detenido o sin herramientas accesibles.

La espera entre eventos sigue la sección `Espera eficiente` de `SKILL.md`: el coordinador usa una espera que observe la fuente real y evita turnos de razonamiento sin estado nuevo. Esta referencia no define una segunda cadencia.

## Contrato del subagente supervisor

Usa los umbrales y la cadencia de `SKILL.md`; no mantengas un segundo calendario. Reutiliza el mismo supervisor y envía solo cambios desde el checkpoint anterior. El supervisor devuelve el control después de cada encargo; no hace polling, no crea agentes ni espera indefinidamente por su cuenta.

Paquete inicial y posteriores deltas, orientativamente hasta 800 palabras por encargo:

- Objetivo, exclusiones y criterios de aceptación pendientes/completados.
- Agentes activos con función y modelo efectivo, y trabajos que tienen encargados.
- Progreso desde el checkpoint anterior, intentos fallidos y próxima acción propuesta.
- Resumen de cambios y hasta tres evidencias breves con procedencia: un resultado de gate, una muestra de consultas repetidas, un diff concreto o un mensaje de agente. Incluye evidencia de ejecución, no solo la valoración del coordinador.
- Deltas de consumo y contexto si están disponibles, con su unidad y alcance; en otro caso, «no disponible».

El supervisor puede consultar fuentes concretas en modo lectura si el paquete no permite concluir; debe pedir o localizar la evidencia mínima que falta. No lee todo el historial ni reinventa el mapa del repositorio. Un criterio pendiente por sí solo no prueba atasco; una hipótesis descartada con evidencia sí es progreso.

Respuesta breve, orientativamente hasta 150 palabras: `continuar`, `corregir` o `evidencia insuficiente`; señal y evidencia; una acción prioritaria; qué resultado permitiría comprobar su efecto. No inventes ahorro, umbrales monetarios ni precisión temporal.

Ante `corregir`, el coordinador contrasta la evidencia y registra acción y resultado esperado, o una razón concreta para no aplicar la recomendación. Corrige repeticiones, alcance o reparto dentro de la autorización vigente antes del próximo ciclo equivalente. En el siguiente checkpoint comprueba si apareció evidencia nueva; si persiste el problema, cambia la hipótesis o escala el diagnóstico en lugar de repetir la misma corrección. Una alerta no autoriza cambios fuera del alcance, interrupciones de procesos, publicación ni descarte de trabajo.

Ante `evidencia insuficiente`, aporta un dato concreto en la siguiente interacción útil; no conviertas el seguimiento en una investigación exhaustiva. Un fallo técnico que necesita especialista se deriva una sola vez según la tabla de modelos. La revisión final sigue comprobando la corrección del producto.

## Supervisión externa opcional

Si el usuario solicita implementarla, prefiere un observador determinista que use eventos de ejecución y uso disponibles. Solo llama a un modelo ante una anomalía que requiera interpretación. Una automatización periódica puede inspeccionar checkpoints si la aplicación lo permite, pero no presupongas que ofrece lectura completa de subagentes, control inmediato o límites duros de gasto.

Antes de activar un monitor, determina sesión/descendientes en alcance, métricas disponibles, umbrales y acciones autorizadas. Por defecto, una alerta informa; no interrumpe escritores, mata procesos, cambia modelos ni descarta trabajo. Preserva autorizaciones previas y no exijas nueva confirmación si el usuario ya definió estas acciones.

Señales útiles, como heurísticas ajustables:

- Varios checkpoints sin nueva evidencia mientras crecen llamadas y consumo; excluye gates largos y esperas legítimas.
- Repetición de las mismas consultas, informes completos o resultados truncados.
- Cambios sin relación demostrable con un criterio de aceptación o prerrequisito.
- Delegados que repiten un inventario existente o producen resultados que nadie utiliza.
- Presupuesto explícito próximo a agotarse. Advierte antes y respeta el límite pactado; no declares éxito para encajar en él.

Para una revisión puntual, basta: objetivo y exclusiones, checkpoint anterior/actual, resumen del diff, últimas decisiones, verificaciones y deltas de uso disponibles. El supervisor devuelve anomalía, evidencia y una acción concreta, o ausencia de hallazgos. Agrupa alertas repetidas; no crees un supervisor del supervisor.

## Lectura correcta del consumo

- Usa herramientas soportadas antes que leer logs o bases internas. Comprueba qué mide cada campo y si incluye descendientes; evita dobles sumas y contadores acumulados de turnos anteriores.
- Distingue entrada sin caché, entrada cacheada, salida y razonamiento. El razonamiento puede estar incluido en la salida: no lo sumes dos veces.
- Contexto actual, tokens procesados acumulados, cuota de cuenta y dinero son magnitudes diferentes. No calcules precios sin tarifas y modalidad de facturación aplicables.
- Una entrada grande puede ser necesaria; una entrada pequeña repetida sin avance también puede desperdiciar recursos. Relaciona el consumo con evidencia útil.
- Si el harness no expone la información, indica «no disponible». La compactación automática mantiene manejable el historial; por sí sola no demuestra ausencia de desviación del alcance.

## Puntos de integración documentados

Referencias consultadas el 5 de septiembre de 2026; verifica la versión instalada antes de implementar controles:

- [Codex App Server](https://developers.openai.com/codex/app-server): eventos `thread/tokenUsage/updated`, estado de turnos y `turn/steer` para aportar instrucciones al turno activo. `turn/steer` no cambia modelo ni esfuerzo. Una instrucción encolada no prueba recepción; verifica el turno receptor.
- [Configuración de Codex](https://learn.chatgpt.com/docs/config-file/config-reference): contexto, umbral de compactación y ajustes de subagentes. No alteres configuración global para instrumentar una única issue sin autorización.
