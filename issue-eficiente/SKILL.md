---
name: issue-eficiente
description: Implementa issues con delegación proporcionada, selección de modelos por dificultad y supervisión del coste, contexto y alcance. Úsala al encargar una issue con subagentes y ahorro de tokens, o al pedir este flujo explícitamente; no para consultas de estado ni revisiones aisladas.
---

# Issue eficiente

Optimiza el coste de alcanzar una solución validada. La fuente de verdad es la issue vigente y las instrucciones del usuario; aplica las normas del repositorio. Ahorrar llamadas no sustituye los criterios de aceptación.

## Contrato y continuidad

- Identifica resultado, no objetivos, gates y autorizaciones. Conserva un registro breve de criterios pendientes/completados con evidencia, decisiones y siguiente acción; reutiliza el plan o checkpoint existente.
- Para trabajo nuevo, usa la base y aislamiento pedidos; en RetroSharp, por defecto `origin/master` vigente, worktree nuevo y rama `agent/<slug>`. Al reanudar, verifica y conserva el worktree, diff y evidencia existentes.
- El resultado por defecto es implementación y validación locales. Commit, push, PR, merge, cierre y limpieza requieren autorización del usuario, que puede estar ya concedida. No vuelvas a pedirla si está explícitamente incluida.

## Modelos y delegación

Coordina y conserva un único escritor responsable de integrar. Estas son preferencias operativas, no un benchmark ni una garantía de coste:

| Función | Modelo | Esfuerzo |
| --- | --- | --- |
| Coordinación | `gpt-5.6-terra` | `medium` |
| Implementación habitual | `gpt-5.6-terra` | `high` |
| Comprobación mecánica, acotada y verificable | `gpt-5.6-luna` | `medium` |
| Diagnóstico o revisión de riesgo acotado | `gpt-5.6-sol` | `high` |
| Arquitectura especialmente difícil, fallos sutiles del compilador, bloqueos persistentes | `gpt-6-astra` | `high` |

Elige directamente Sol o Astra cuando la dificultad y el riesgo lo justifiquen; no exijas recorrer Luna → Terra → Sol → Astra. En RetroSharp, Astra puede aportar valor en semántica, análisis estático o corrección entre targets; una extracción física de proyectos no lo requiere por sí sola.

La selección de subagentes forma parte de este flujo. Especifica `model`, `reasoning_effort` y `fork_turns: "none"` en la herramienta que los crea. Darle a un agente el nombre de un modelo en su prompt no configura ese modelo. Comprueba la respuesta o metadatos disponibles; distingue solicitado de confirmado.

Una skill no cambia automáticamente el modelo de la sesión principal. Si no puedes aplicar un ajuste mediante un control soportado, indícalo una vez y continúa con el modelo disponible. Respeta elecciones explícitas del usuario. Ante modelos no disponibles, usa una alternativa disponible de función comparable y declara la sustitución. Evita investigar catálogos en cada issue y usar `xhigh` o superior por rutina.

El escritor hace la exploración necesaria y sigue con la implementación. Separa un preparador solo para una incertidumbre independiente cuyo resultado reduzca trabajo posterior. Paraleliza únicamente tareas independientes que vayas a utilizar; respeta la serialización de builds/tests del repositorio.

Cada encargo contiene objetivo, worktree/base, alcance de escritura, decisiones relevantes, evidencia localizada y aceptación. El informe devuelve resultado, archivos/evidencia y pendientes. Reutiliza al escritor que progresa; no dupliques su trabajo ni sustituyas su contexto por rutina.

## Supervisión integrada

El coordinador supervisa en cada relevo, fallo, fin de gate y antes del cierre. En fases largas revisa también aproximadamente cada diez minutos de trabajo activo, aprovechando su siguiente intervención normal: no generes llamadas vacías para cumplir el reloj. Es una cadencia orientativa, no un temporizador ni un monitor en segundo plano.

Comprueba brevemente:

- **Progreso:** ¿hay evidencia nueva, un criterio satisfecho o una hipótesis descartada?
- **Alcance:** ¿cada cambio y nueva tarea contribuye a la issue o a un prerrequisito demostrado?
- **Contexto:** ¿se repiten inventarios/documentos, hay salidas truncadas o informes demasiado extensos?
- **Coste:** ¿el modelo corresponde al riesgo y los agentes aportan resultados utilizados?

Corrige lecturas redundantes y limita las salidas en cuanto aparezcan. Reutiliza informes terminados, notificaciones y esperas permitidas; evita `list_agents` periódico y verificaciones repetidas sin motivo.

Tras dos intentos sobre el mismo bloqueo sin nueva evidencia, solicita un diagnóstico acotado al modelo adecuado: Sol para riesgo acotado; Astra para dificultad excepcional o un bloqueo que persiste tras la intervención de Sol. Envía la pregunta concreta, hipótesis descartadas y evidencia mínima, y devuelve la conclusión al escritor. Si resolverla exige implementación continuada, asigna esa parte acotada al especialista, serializando el relevo del escritor. Una compilación larga o una espera legítima no son estancamiento. Si el obstáculo es falta de información, permisos o capacidad del entorno, identifica esa carencia en lugar de seguir escalando modelos.

Para contexto deteriorado, prepara un checkpoint corto con objetivo, estado del diff, decisiones, evidencia y pendientes antes de un relevo necesario. No reinicies agentes que siguen progresando para bajar un contador.

Si hay métricas accesibles, usa deltas entre checkpoints y separa entrada nueva, cacheada y salida. Los tokens acumulados no son el tamaño del contexto ni el coste facturado; la cuota de cuenta no mide una issue. Si faltan métricas, declara esa limitación y usa señales observables. No inventes presupuestos ni porcentajes de ahorro.

Para supervisión externa solicitada o interpretación de métricas, lee [supervision.md](references/supervision.md). No actives tareas periódicas, exportación de telemetría ni cambios globales por invocar esta skill.

## Revisión y entrega

Sobre un diff estable, encarga una única revisión independiente de solo lectura que cubra especificación y normas relevantes. Selecciona el modelo según la tabla: Terra para cambios rutinarios, Sol para riesgo acotado y Astra para la dificultad excepcional identificada. Usar Astra no añade una segunda revisión por defecto. Una segunda revisión necesita una laguna o riesgo concreto, no una plantilla. Evita sumar revisores de otras skills para volver a comprobar lo mismo; respeta cualquier revisión adicional exigida explícitamente por el usuario o repositorio.

Corrige hallazgos dentro del alcance y repite las validaciones afectadas y gates obligatorios según corresponda. Fallos ajenos se documentan con evidencia, sin absorberlos. Finaliza solo cuando los criterios estén satisfechos o exista un bloqueo real que requiera intervención externa; el ahorro no justifica una entrega incompleta.

Entrega resultado, decisiones, validaciones y limitaciones reales. Añade una línea de modelos efectivos y escalados relevantes si hay evidencia; no un relato de cada llamada.
