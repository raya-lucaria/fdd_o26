No pude escribir el entregable en `cp_estr.md`: el entorno bloqueó la operación porque todo el filesystem está montado en modo de solo lectura. El repositorio quedó intacto y no ejecuté benchmarks ni `pytest`.

## Dictamen

La sección actual funciona como guía de notebook:

> definición breve → código → explicación línea por línea → salida → figura

Debe invertirse:

> definición → figura/Gantt → matemática → ejemplo → patrón arquitectónico → código mínimo al final

Además, si será una unidad propia, la ruta natural es `course/11_computo_y_concurrencia/`, con assets en su propio `_assets/` y notebook en `codigo/11_computo_y_concurrencia/`.

## 1. Crítica por página

### `0_index.md`

Mover al final o a un apéndice:

- Todo `## Antes de la clase`, incluidos Git, `uv sync`, servidor y kernel.
- La explicación línea por línea de esos comandos.

Cortar o reescribir:

- «Las tres páginas centrales las separan con una definición, un comando y una salida»: refuerza el orden rechazado.
- La preparación repetida en la página 1.
- `## Qué no cubre esta sección`: no se deben diferir colas, límites, timeouts y escalado si la unidad ahora se enfoca en arquitectura.
- Las referencias del glosario a «la celda N»: deben apuntar a definiciones y figuras.

Convertir:

- Fusionar `En corto`, glosario y tabla de páginas en un mapa: **modelo → propiedad observable → patrón arquitectónico → decisión**.
- Añadir un diagrama de progresión: secuencial → concurrencia → event loop/pools → cálculo → arquitectura integrada.

### `1_donde_pasa_el_tiempo.md`

Mover al final:

- `## Arranque de la sección`: debe existir sólo en el índice.
- Celdas 1.1 y 1.2, sus salidas y explicaciones línea por línea.
- Dejar al final un único bloque `## Código mínimo: medir reloj y CPU`.

Cortar o corregir:

- «Tarea = ejecuta + espera» deja fuera el estado **lista**. La vida de una tarea puede contener `exec`, `wait` y `ready`.
- `reloj - process_time` no equivale estrictamente a espera de I/O: también incluye tiempo lista/desplanificado y otros costos.
- CPU-bound/I/O-bound deben presentarse como clasificación empírica dominante, no como equivalencias absolutas.
- Reducir el ejemplo de 100/500 llamadas al notebook.

Convertir:

- Añadir antes del Gantt la máquina de estados:
  `nueva → lista → ejecutando → esperando → lista → … → terminada`.
- Después del Gantt introducir progresivamente `T`, `Task`, `τᵢ`, `start`, `end`, `life`, `exec`, `wait`, `ready`, `ExecutingAt(t)` y `P`.
- Convertir `Por qué ese porcentaje decide todo` y el checklist final en una tabla: **señal / recurso ocioso / patrón útil / patrón inútil**.

Arquitectura que falta:

- Clientes → cola FIFO → un worker secuencial → dependencia.
- Cuándo sí: baseline, dependencia estricta, carga baja.
- Cuándo no: solicitudes independientes con I/O largo.
- Introducir capacidad y latencia de cola: con 0.2 s por solicitud, un worker completa alrededor de 5 solicitudes/s bajo ese modelo.

### `2_concurrente_paralelo_asincrono.md`

Mover al final:

- Celdas 2.1–2.5 y salidas.
- `sys.setswitchinterval` y los detalles dependientes de versión: notebook.

Cortar o corregir:

- Eliminar la matriz 2×2 actual y `cmp-matriz-2x2.svg`. A una granularidad fija:

  `paralelo ⇒ concurrente`

  Si dos tareas ejecutan simultáneamente, sus ciclos de vida necesariamente se solapan. «Paralelo no concurrente» es imposible.
- NumPy no es una excepción: visto como una sola tarea no hay dos tareas que clasificar; vistas sus subtareas internas, son paralelas y concurrentes.
- Definir asincronía sin depender primero de `Task`: una operación entrega un handle antes del resultado y permite separar inicio de obtención del resultado.
- Posponer `create_task` hasta haber explicado el event loop.

Convertir:

- Reemplazar la matriz por un diagrama de implicación: `paralelo ⇒ concurrente`, pero `concurrente ⇏ paralelo`; asincronía cruza el dibujo como mecanismo de control.
- Usar el mismo ejemplo en tres Gantts: secuencial, concurrente no paralelo y paralelo.
- Debajo, tabla verificable con `life(τᵢ) ∩ life(τⱼ)` y `exec(τᵢ) ∩ exec(τⱼ)`.
- Sustituir el código inicial de carrera por una traza `hilo A / hilo B / contador`; después mostrar la región crítica con `Lock`.

Arquitectura que falta:

- Hilo por conexión/thread pool.
- Prefork/pool de procesos.
- Memoria compartida frente a aislamiento.
- Región crítica como serialización deliberada.
- Restricción del GIL expresada por intérprete, no como restricción global del sistema.

### `3_asyncio_y_el_event_loop.md`

Mover al final:

- Todas las celdas 3.1–3.7.
- Conservar sólo tres demostraciones mínimas: traza, serie frente a `gather`, y bloqueo frente a offload.
- Las mediciones 20/100/500 pertenecen al notebook.

Cortar:

- La corrida aislada con 100 conexiones que dio 10.91 s: está confundida por cliente, pool, CPU y falta de repeticiones.
- «100 hilos o 1000 corrutinas es válido»: el límite depende de sockets, memoria, dependencia remota, pool y objetivo de latencia.
- La celda 3.1, porque duplica la introducción de asincronía.

Convertir:

- Reemplazar `cmp-event-loop.svg` por una figura de estados por tick: `LISTAS`, `EJECUTANDO`, `ESPERANDO`, `TERMINADAS`.
- Comparar bloqueo/offload lado a lado y distinguir explícitamente **lista** de **esperando I/O**.
- Explicar `gather`, `Semaphore`, `create_task` y `run_in_executor` mediante los diagramas descritos más abajo.

Arquitectura que falta:

- Un event loop por worker.
- Pool de conexiones y límite de concurrencia.
- Bulkhead: límites separados por dependencia.
- Pool de procesos precreado y acotado para CPU.
- Mostrar la cola del executor: delegar mueve la espera, no crea capacidad infinita.

### `4_vectorizar.md`

Mover al final:

- Celdas 4.1 y 4.2.
- La demostración de desbordamiento `int64`: notebook.
- El código que imprime Amdahl: ejercicio del notebook; la fórmula y tabla bastan en la página.

Cortar o corregir:

- No equiparar vectorización, SIMD y paralelismo.
- Reducir `float64`/`int64` a una advertencia sobre semántica numérica.
- No eliminar Amdahl si falta tiempo: es el vínculo entre medición y decisión arquitectónica.

Convertir:

- Mover `cmp-vectorizar.svg` inmediatamente después de la definición.
- Orden: figura → `speedup` y Amdahl → ejemplo medido.
- Convertir `Cuándo vectorizar no sirve` en matriz: **datos / dependencias / memoria / estrategia / riesgo**.
- Añadir arquitectura: petición → operación vectorizada, frente a petición → cola/pool de procesos. Marcar copias, temporales e hilos internos.

### `5_elegir_la_estrategia.md`

Mover al final:

- Celdas 5.1 y 5.2.
- `## Qué decide una API frente a esto` debe moverse antes del código y expandirse.

Cortar:

- La `lambda` no serializable puede quedar en el notebook; no merece ser uno de los dos ejemplos principales de la síntesis.
- La comparación 8/16 procesos de una sola corrida.
- La tabla completa de tiempos, porque repite las páginas anteriores.

Convertir:

- Antes del árbol, añadir una tabla de restricciones: tipo de trabajo, dependencia, recurso limitante, concurrencia, latencia objetivo, aislamiento y librerías.
- Reescribir anti-patrones como **fallo arquitectónico / señal observable / contención**, no como líneas de código.
- Añadir arquitectura integrada:

  `balanceador → workers → pools/límites separados para BD y API → pool o cola CPU`

- Incluir cola acotada, backpressure, timeouts, bulkheads, p99, thundering herd, Ley de Little y escalado vertical/horizontal.

## 2. Conceptos faltantes

Modelo formal:

- `T`, `Task = {τ₁,…,τₙ}`, `start`, `end`, `life`.
- `exec(τᵢ)`, `wait(τᵢ)` y `ready(τᵢ)`.
- `ExecutingAt(t)` y `|ExecutingAt(t)| ≤ P`.
- Definiciones formales de secuencial, concurrente y paralelo.
- Implicación correcta `paralelo ⇒ concurrente`.
- Asincronía como contrato/control, no como sinónimo de concurrencia.
- GIL definido sobre hilos de un intérprete.
- `speedup`, Amdahl y sus supuestos.

`asyncio`:

- Estados nueva/lista/ejecutando/esperando/terminada.
- Diferencia entre objeto corrutina y `Task`.
- Cola lista, registro de I/O/timers y promoción a lista.
- `await` sólo cede cuando lo esperado está pendiente.
- `create_task`, `gather`, `Semaphore`, Future/executor.
- Timeout, cancelación y propagación de errores.

Arquitectura:

- Cola, pool, capacidad finita y backpressure.
- Límite de concurrencia, pool de conexiones y bulkhead.
- Latencia de servicio, latencia de cola, throughput y p99.
- Ley de Little: `L = λW`.
- Timeouts/deadlines y cancelación.
- Thundering herd.
- CPU en el camino de la petición.
- Prefork, thread-per-connection, event-loop worker y event loop + process pool.
- Escalado vertical/horizontal y estado compartido.

## 3. Event loop explicado por estados

Definición:

Un event loop es un planificador cooperativo que corre en un hilo. Toma una tarea lista, la ejecuta hasta que termina o encuentra un `await` pendiente, registra qué evento debe despertarla y continúa con otra tarea lista. Si ninguna está lista, pide al sistema operativo esperar el próximo evento; no hace busy waiting.

Estados:

`NUEVA → LISTA → EJECUTANDO → ESPERANDO → LISTA → … → TERMINADA`

Supuesto: cada tramo de CPU dura 10 ms. A espera 100 ms; B, 50 ms; C, 80 ms desde sus respectivos `await`.

| Tick / tiempo | Listas antes | Ejecuta | Resultado | Esperando después |
|---|---|---|---|---|
| registro, `t=0` | `[A,B,C]` | — | tres tareas programadas | `∅` |
| 1, `0–10` | `[A,B,C]` | A | `await`; despierta en 110 | `{A@110}` |
| 2, `10–20` | `[B,C]` | B | `await`; despierta en 70 | `{B@70,A@110}` |
| 3, `20–30` | `[C]` | C | `await`; despierta en 110 | `{B@70,A@110,C@110}` |
| `30–70` | `[]` | — | el SO espera; despierta B | `{A@110,C@110}` |
| 4, `70–80` | `[B]` | B | B termina | `{A@110,C@110}` |
| `80–110` | `[]` | — | despiertan A y C | `∅` |
| 5, `110–120` | `[A,C]` | A | A termina; C sigue lista | `∅` |
| 6, `120–130` | `[C]` | C | C termina | `∅` |

La observación clave: entre 110 y 120, C ya no está esperando su timer; está **lista**, esperando turno.

Figura nueva: `cmp-event-loop-estados.svg`, con ocho paneles y cuatro cajas fijas:

- cola `LISTAS`;
- ranura única `EJECUTANDO`;
- conjunto `ESPERANDO`, con evento/deadline;
- `TERMINADAS`.

Debajo debe llevar un Gantt con los mismos colores para `ready`, `exec` y `wait`.

## 4. Diagramas para las primitivas

`create_task`:

- Tres carriles: tarea padre, tarea creada y event loop.
- Padre: `create_task(A)` → trabajo independiente B → `await A`.
- Comparar con `create_task(A); await A` inmediato, donde no se aprovecha ninguna espera.
- Mostrar que devuelve un handle y programa A; no devuelve el resultado.

`gather`:

- Fan-out/fan-in:
  `padre → [A,B,C] → líneas de vida concurrentes → barrera → [rA,rB,rC]`.
- El Gantt muestra que abre cuando termina la más lenta.
- Los resultados conservan el orden de entrada, no el de finalización.
- A un lado, `await A → await B → await C` muestra la suma de esperas.

`Semaphore(K)`:

- `N tareas → cola del semáforo → K permisos → recurso limitado → release`.
- Con cinco tareas y `K=2`, mostrar tres tandas.
- Etiquetar que limita simultaneidad, no peticiones por segundo.
- Dos dependencias deben tener semáforos separados para formar un bulkhead.

`run_in_executor`:

- `Task → submit → cola acotada → worker/proceso → Future → cola LISTAS → reanudación`.
- Carriles B y C siguen avanzando mientras el worker calcula.
- Dibujar serialización/IPC para procesos.
- Pool de hilos para I/O bloqueante; procesos para Python CPU-bound.
- El pool debe estar precreado y su cola visible.

## 5. Unidad nueva: seis páginas, 120 minutos

Ruta propuesta: `course/11_computo_y_concurrencia/`.

| Página | Min | Contenido y arquitectura |
|---|---:|---|
| `1_tareas_tiempo_y_secuencial.md` | 18 | Estados, modelo `T/τ/exec/wait/ready`, Gantt, servidor secuencial, cola y capacidad |
| `2_concurrencia_paralelismo_y_gil.md` | 22 | Definiciones formales, implicación correcta, hilos/procesos/GIL, carrera, thread pool y prefork |
| `3_event_loop_y_control.md` | 28 | Traza por ticks, corrutina/Task, `create_task`, `gather`, `Semaphore`, bloqueo y executor |
| `4_capacidad_colas_y_servidores.md` | 22 | Worker pools, colas acotadas, backpressure, bulkheads, timeouts, p99, `L=λW`, thundering herd |
| `5_computo_vectorizacion_y_amdahl.md` | 18 | Vectorización, procesos, speedup, Amdahl, memoria, oversubscription y CPU fuera del request path |
| `6_elegir_y_justificar.md` | 12 | Caso integral, árbol, balanceador/workers/pools, escalado vertical-horizontal y checklist |
| **Total** | **120** | |

Cada página debe repetir:

1. `Qué es`.
2. `Cómo se ve`.
3. `Propiedad formal`.
4. `Ejemplo resuelto`.
5. `Patrón de arquitectura`.
6. `Código mínimo`, siempre al final.

El notebook nuevo debería vivir en `codigo/11_computo_y_concurrencia/computo.ipynb` y organizarse por esos seis temas. En cada tema: baseline repetido → una modificación → predicción → ejecución → traza → versión incorrecta → corrección → decisión arquitectónica.