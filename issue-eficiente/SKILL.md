---
name: issue-eficiente
description: Implementa issues con un único escritor, delegación proporcional y control verificable de coste y contexto. Úsala para ejecución con subagentes; no para consultas de estado ni revisiones aisladas.
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
| Supervisor independiente del flujo | `gpt-5.6-terra` | `medium` |
| Implementación habitual | `gpt-5.6-terra` | `high` |
| Comprobación mecánica, acotada y verificable | `gpt-5.6-luna` | `medium` |
| Diagnóstico o revisión de riesgo acotado | `gpt-5.6-sol` | `high` |
| Arquitectura especialmente difícil, fallos sutiles del compilador, bloqueos persistentes | `gpt-6-astra` | `high` |

Elige directamente Sol o Astra cuando la dificultad y el riesgo lo justifiquen; no exijas recorrer Luna → Terra → Sol → Astra. En RetroSharp, Astra puede aportar valor en semántica, análisis estático o corrección entre targets; una extracción física de proyectos no lo requiere por sí sola.

La selección de subagentes forma parte de este flujo. Especifica `model`, `reasoning_effort` y `fork_turns: "none"` en la herramienta que los crea. Darle a un agente el nombre de un modelo en su prompt no configura ese modelo. Comprueba la respuesta o metadatos disponibles; distingue solicitado de confirmado.

Una skill no cambia automáticamente el modelo de la sesión principal. Si no puedes aplicar un ajuste mediante un control soportado, indícalo una vez y continúa con el modelo disponible. Respeta elecciones explícitas del usuario. Ante modelos no disponibles, usa una alternativa disponible de función comparable y declara la sustitución. Evita investigar catálogos en cada issue y usar `xhigh` o superior por rutina.

El escritor hace la exploración necesaria y sigue con la implementación. Separa un preparador solo para una incertidumbre independiente cuyo resultado reduzca trabajo posterior. Paraleliza únicamente tareas independientes que vayas a utilizar; respeta la serialización de builds/tests del repositorio.

Cada encargo contiene objetivo, worktree/base, alcance de escritura, decisiones relevantes, evidencia localizada y aceptación. El informe devuelve en hasta 800 palabras resultado, archivos/evidencia y pendientes. Reutiliza al escritor que progresa; no dupliques su trabajo ni sustituyas su contexto por rutina.

### Bucle acotado

- Acota la primera consulta o comando: usa el identificador o ruta más estrechos disponibles y, cuando la herramienta lo permita, limita su salida a 5.000 tokens. Amplía solo después de inspeccionar el primer resultado y demostrar qué evidencia falta.
- Antes de iniciar un nuevo tramo sustantivo, comprueba las métricas disponibles. Un contexto que alcance el 75 % de su ventana o una sesión con 120 ejecuciones de comandos activa un cortacircuitos: termina únicamente la acción acotada en curso y, en la siguiente transición material, entrega un checkpoint de hasta 800 palabras y cierra esa sesión antes de abrir una continuación limpia. Mantén un solo escritor activo y no repitas la exploración ya documentada.
- Si esas métricas no están disponibles, usa como señales equivalentes las salidas truncadas, la relectura del mismo inventario o la pérdida repetida de decisiones ya tomadas.
- El cortacircuitos protege la continuidad; no reduce la aceptación, no declara éxito y no interrumpe una compilación, prueba o publicación que siga progresando.

## Supervisión integrada

### Espera eficiente

Trata el trabajo delegado y los checks externos como estados de espera orientada a eventos. Después de lanzar un agente o un gate, registra una sola vez qué evento falta y cuál será la siguiente acción; después usa el mecanismo menos costoso que pueda observar ese evento de verdad:

- Para un agente delegado, usa una sola `wait_agent(timeout_ms: 600000)` o la espera soportada más cercana a diez minutos. Consume su notificación al llegar. Un timeout no es una anomalía: en la siguiente continuación repite únicamente esa espera. Reserva `list_agents` para estados contradictorios o una entrega perdida, no para comprobar actividad.
- Para CI u otro sistema externo, usa un watcher bloqueante del proveedor o del harness, con intervalo moderado, que termine al cambiar el estado. `wait_agent` no observa CI y no debe usarse para ello.
- Si terminar el turno deja el Goal dormido hasta un evento, cede el turno con el Goal activo. Terminar un turno no significa detener, pausar ni bloquear el objetivo.
- Si el Goal se reactiva inmediatamente sin estado nuevo, no produzcas finales ni checkpoints vacíos. Reanuda directamente una única espera larga sobre la fuente correcta. Un timeout sin novedad permite repetir esa espera en la siguiente continuación, sin releer inventarios ni emitir estado invariable.

Al recibir una entrega, fallo, bloqueo o transición terminal, abandona la espera y ejecuta la siguiente acción. Evita bucles de polling dirigidos por el modelo: una herramienta puede permanecer bloqueada esperando, pero no debe provocar turnos periódicos de razonamiento sin información nueva.

El coordinador supervisa en cada relevo, fallo, fin de gate y antes del cierre. En fases largas revisa también al recibir una entrega parcial o antes de iniciar el siguiente tramo sustantivo. Cada comprobación debe nacer de un evento o una decisión real, nunca de un reloj.

Comprueba brevemente:

- **Progreso:** ¿hay evidencia nueva, un criterio satisfecho o una hipótesis descartada?
- **Alcance:** ¿cada cambio y nueva tarea contribuye a la issue o a un prerrequisito demostrado?
- **Contexto:** ¿se repiten inventarios/documentos, hay salidas truncadas o informes demasiado extensos?
- **Coste:** ¿el modelo corresponde al riesgo y los agentes aportan resultados utilizados?

Corrige lecturas redundantes y limita las salidas en cuanto aparezcan. Reutiliza informes terminados, notificaciones y esperas permitidas; evita `list_agents` periódico y verificaciones repetidas sin motivo.

Tras dos intentos sobre el mismo bloqueo sin nueva evidencia, solicita un diagnóstico acotado al modelo adecuado: Sol para riesgo acotado; Astra para dificultad excepcional o un bloqueo que persiste tras la intervención de Sol. Envía la pregunta concreta, hipótesis descartadas y evidencia mínima, y devuelve la conclusión al escritor. Si resolverla exige implementación continuada, asigna esa parte acotada al especialista, serializando el relevo del escritor. Una compilación larga o una espera legítima no son estancamiento. Si el obstáculo es falta de información, permisos o capacidad del entorno, identifica esa carencia en lugar de seguir escalando modelos.

Aplica el cortacircuitos de contexto en la siguiente transición material. Conserva el proceso o gate que progresa y realiza el relevo antes de comenzar otro tramo sustantivo.

Si hay métricas accesibles, usa deltas entre checkpoints y separa entrada nueva, cacheada y salida. Los tokens acumulados no son el tamaño del contexto ni el coste facturado; la cuota de cuenta no mide una issue. Si faltan métricas, declara esa limitación y usa señales observables. No inventes presupuestos ni porcentajes de ahorro.

### Supervisor independiente obligatorio en trabajos largos

Activa un subagente supervisor de solo lectura cuando el plan tenga al menos tres entregables sustantivos de implementación, se acumulen unos treinta minutos de trabajo activo, o aparezcan dos intentos sin nueva evidencia sobre el mismo bloqueo. Evalúa esos umbrales solo en una intervención motivada por un evento; no mantengas un turno vivo para alcanzarlos. Preparación, revisión y ejecución de tests no cuentan como entregables adicionales; el tiempo de espera de agentes, procesos o CI no es trabajo activo y no activa por sí solo esta regla.

Lee [supervision.md](references/supervision.md) y crea un único supervisor con Terra `medium` y `fork_turns: "none"`. Su función es comprobar que el trabajo aporta progreso, no implementar ni duplicar el diagnóstico técnico. Encárgale una primera comprobación al activarlo y seguimientos solo después de un nuevo tramo sustantivo de actividad, en el siguiente checkpoint disponible. Adelanta una revisión ante una nueva señal fuerte; agrupa avisos repetidos. El coordinador inicia estos encargos y debe registrar su recepción y resultado: crear un agente y dejarlo esperando no cumple la supervisión.

Aplica las correcciones de proceso verificadas antes de encargar otro ciclo equivalente y comprueba su efecto en el siguiente checkpoint. Si coinciden atasco y escalado técnico, usa el dictamen del supervisor para formular un único encargo de diagnóstico, evitando dos investigaciones del mismo problema. No reinicies escritores que progresan ni interrumpas gates legítimos para cumplir una cadencia. Si no puedes crear o contactar al supervisor, informa de esa limitación y conserva los checkpoints propios sin afirmar que hubo revisión independiente.

La supervisión no sustituye la revisión final de corrección. Al llegar al cierre, integra sus hallazgos pendientes en el paquete de revisión final y evita un seguimiento periódico adicional. Esta skill exige supervisión durante la ejecución; no instala un temporizador externo ni garantiza vigilancia cuando la sesión está detenida. No actives automatizaciones, exportación de telemetría ni cambios globales por invocarla.

## Revisión y entrega

Sobre un diff estable, encarga una única sesión independiente de solo lectura que cubra por sí misma especificación y normas relevantes. Selecciona el modelo según la tabla: Terra para cambios rutinarios, Sol para riesgo acotado y Astra para la dificultad excepcional identificada. Su encargo exige resolver ambos ejes dentro de esa sesión, sin crear descendientes ni invocar un flujo de revisión que los cree. Una revisión adicional solo procede si el usuario o el repositorio la exige, o si existe una laguna concreta que la primera no puede cerrar.

Devuelve los hallazgos al mismo escritor y dirige las comprobaciones posteriores al mismo revisor mediante `followup_task` o el mecanismo equivalente; limita cada recheck a los hallazgos abiertos. Durante las correcciones ejecuta validaciones focales. Ejecuta el gate completo obligatorio una vez sobre el candidato estable y repítelo solo si falla y el código cambia para corregirlo, cambia el head revisado o el repositorio lo exige explícitamente.

Fallos ajenos se documentan con evidencia, sin absorberlos. Declara la issue completada solo cuando los criterios estén satisfechos; si existe un bloqueo real que requiere intervención externa, entrega el checkpoint correspondiente. El ahorro no justifica una entrega incompleta.

Entrega resultado, decisiones, validaciones y limitaciones reales. Añade una línea de modelos efectivos y escalados relevantes si hay evidencia; no un relato de cada llamada.
