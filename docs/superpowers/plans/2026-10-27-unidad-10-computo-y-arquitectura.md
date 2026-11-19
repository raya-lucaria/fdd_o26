# Unidad 10 · APIs — secciones 10.2–10.4 (cómputo, protocolos, arquitectura) · Plan

> Plan de **contenido**. Tareas, flashcards y fichas quedan fuera a propósito (la prisa es la clase). El plan de detalle sólo cubre la sección 10.2, la de la clase 1.

**Origen.** `~/itam/fdd_p26/clase/16_computo` (secuencial/concurrente/paralelo/async, Gantt, `asyncio`, Amdahl, librerías y decisión) y `clase/18_intro_a_apis` (SSE, WebSocket, polling, webhooks, gRPC, GraphQL, SOAP). Se **simplifican**: se quitan los modelos M1–M6, la notación griega, el framework formal y toda analogía de cocina/restaurante. Se **agregan**: vectorización, arquitectura y patrones de diseño. Las cifras y los benchmarks de p26 NO se copian (sus CSV son valores redondos escritos a mano): se miden aquí contra `codigo/10_apis/servidor.py`.

## Reglas de escritura (las heredan todos los agentes)

- Sin analogías (ver memoria `sin-analogias`): qué es la cosa + comando que lo demuestra + salida real. Prohibido en prosa: «imagina», «es como», «como si», «analogía», «piensa en», restaurante/cocina/mesero. Comparaciones técnicas reales sí.
- Compacto y directo: párrafos ≤ 3 líneas, tabla antes que prosa, **bold** sólo en lo que se rompe si no se lee. Cada concepto con definición de una línea; el diagrama o el Gantt lo fija.
- Cada página abre con la pregunta/problema que la motiva (registro de `2_pipeline_de_datos/4_cuando_se_rompe.md`) y cierra con «Al diseñar / al revisar código de IA, busca…».
- Toda salida «Deberías ver» sale de correrla de verdad, una vez, con cargas chicas (el profesor pidió no devorar núcleos: máx. 4 workers, ≤ 500 llamadas, una sola corrida de `pytest tools/` al final).
- Convenciones del repo: ver `CLAUDE.md` (wikilinks sin escapar el pipe en tablas, callouts exactos, SVG con `width`/`height`, `@` en code span, ids de figuras únicos en todo el curso, fila en `_assets/CREDITOS.md`).

## Visión general: tres secciones, tres clases

| Sección | Clase | Pregunta | Decisión de diseño |
|---|---|---|---|
| **10.2 Cómputo y concurrencia** (`computo-y-concurrencia`) | hoy, 2026-10-27 | ¿Cómo ejecuta un programa el trabajo y cómo se reparte? | secuencial, concurrente, paralelo o vectorizado según dónde pase el tiempo |
| **10.3 Patrones y protocolos** (`patrones-y-protocolos`) | siguiente | ¿Cómo se comunican dos programas cuando hay que esperar un evento? | petición-respuesta, polling, long polling, SSE, WebSocket, webhook, gRPC, GraphQL, SOAP, cola |
| **10.4 Arquitectura de APIs** (`arquitectura-de-apis`) | tercera | ¿Cómo se arma un sistema con esas piezas sin que se caiga? | síncrono o asíncrono entre servicios, timeouts, `429`, backoff, idempotencia, colas, pools, escalado |

### 10.3 (contorno, ~5 páginas)
1. Mapa de patrones: quién inicia y quién espera (tabla única + diagrama de secuencia por patrón).
2. Polling y long polling (fórmula de peticiones desperdiciadas, medida contra el servidor).
3. Push: SSE, WebSocket y webhook (conexión larga, costo por conexión, firma HMAC, reintentos).
4. Contratos de otro estilo: gRPC (Protobuf, multiplexado HTTP/2), GraphQL (N+1, batching), SOAP (legado).
5. Cuadro de decisión + benchmark polling vs SSE vs webhook (peticiones desperdiciadas, retraso hasta el evento).

### 10.4 (contorno, ~5 páginas)
1. Síncrono vs asíncrono entre servicios; colas y backpressure.
2. Fallar bien: timeouts, `429`, backoff exponencial con jitter, idempotencia (retoma 10.1).
3. Pools y límites: tamaño de pool, conexiones persistentes, rate limiting.
4. Escalar: vertical vs horizontal, estado compartido, cuándo distribuir (un párrafo de latencia y sin reloj global).
5. Árbol de decisión integrador y caso de punta a punta.

---

# Plan de detalle · sección 10.2 «Cómputo y concurrencia» (clase 1)

**Meta.** Al terminar, el alumno decide con criterio medido si un trabajo se hace en secuencia, con hilos, con `asyncio`, con procesos o vectorizado, y sabe leer un Gantt que lo justifica.

**Dónde.** `course/10_apis/2_computo_y_concurrencia/` (índice `0_index.md`, id `computo-y-concurrencia`). Actualizar `course/10_apis/0_index.md` (fila 2). `session-17` en el calendario: **2026-10-27, 19:00–20:30**, `page: computo-y-concurrencia`. Si la clase dura 2 h, se avisa al profesor: el calendario y los tres documentos (`course/0_index.md`, `README.md`) se mueven juntos.

**Lo que NO repite.** Proceso, hilo, GIL, `ThreadPoolExecutor` / `ProcessPoolExecutor` y free-threading ya están en `[[el-gil]]` (9.2). Aquí se **enlazan** con wikilink y se resumen en una tabla de 6 líneas; la figura `py-gil.svg` no se copia (vive en `9_python/_assets`, fuera del alcance de esta sección): se enlaza la página.

## Páginas (5 + índice), ~110 min de material, corte marcado

| # | id | Pregunta que abre la página | Contenido | Min |
|---:|---|---|---|---:|
| 1 | `donde-pasa-el-tiempo` | ¿Por qué 20 peticiones tardan 20 veces lo que una? | Tarea = tramo que **ejecuta** + tramo que **espera**. CPU-bound vs I/O-bound (una definición, un comando: `?lento=` contra una cuenta). Gantt secuencial con la CPU inactiva. Medición: 20 llamadas en serie. | 15 |
| 2 | `procesos-hilos-y-gil` | ¿Qué es lo que se ejecuta y por qué importa? | Tabla compacta proceso/hilo/CPU lógica/GIL con enlace a `[[el-gil]]`. Memoria compartida vs aislada. Qué cuesta crear cada uno (medido). Cambio de contexto en una línea. | 15 |
| 3 | `concurrente-paralelo-asincrono` | ¿Concurrente, paralelo y asíncrono son lo mismo? | Tres definiciones separadas: **concurrente** = ciclos de vida que se solapan; **paralelo** = dos cosas ejecutándose en el mismo instante (≥ 2 CPU); **asíncrono** = una tarea no bloquea a otra mientras espera. Matriz de 2×2 con un ejemplo corrible por celda. Gantt por modelo (secuencial, hilos, `asyncio`, procesos). | 25 |
| 4 | `asyncio-y-el-event-loop` | ¿Cómo espera 100 peticiones un solo hilo? | `async`/`await`, event loop (traza de tiempos real), `gather`, el contraejemplo `await` en serie, `time.sleep` vs `asyncio.sleep`, un cálculo que **bloquea el loop** y la salida (`run_in_executor`/procesos). | 25 |
| 5 | `vectorizar` | ¿Y si el trabajo no espera sino que calcula sobre muchos datos? | Bucle de Python vs operación sobre un arreglo (NumPy): qué cambia (tipos homogéneos, memoria contigua, instrucciones SIMD, el bucle sale de Python). Medición. Cuándo vectoriza y cuándo no. Amdahl en una fórmula y una tabla. | 20 |
| 6 | `elegir-la-estrategia` | Dado un trabajo, ¿qué uso? | Árbol de decisión (espera → hilos o `asyncio`; calcula en Python → procesos; calcula sobre arreglos → vectorizar; todo junto → combinar), tabla de costos medidos y anti-patrones con comando (`await` en serie, pool por petición, más workers que CPU, `lambda` en procesos). | 10 |

**Corte si falta tiempo** (en este orden): primero se omite el cambio de contexto de la 2, luego Amdahl en la 5, luego la combinación en la 6. Las páginas 3 y 4 no se recortan.

### Conceptos que quedan definidos (y dónde)
tarea, ejecutar, esperar, CPU-bound, I/O-bound (1) · proceso, hilo, GIL (2, enlace) · concurrente, paralelo, asíncrono (3) · event loop, corrutina, `await`, `gather` (4) · vectorización, SIMD, arreglo contiguo, Amdahl (5) · pool, speedup (6). Cada término se **define antes de su primer uso** y se repite en el glosario de la sección (sin guarda automática; revisor humano).

### Figuras (generador nuevo `tools/gen_computo.py`, catálogo `DIAGRAMAS`, prefijo `cmp-`, test `tools/test_gen_computo.py`)

Se reconstruyen como SVG con `svg_base.py` desde los esquemas de `fdd_p26/clase/16_computo/scripts/generar_graficas.py` (tiempos constantes del script, sin depender de ninguna máquina) — **mejorados**: ejes rotulados en ms, leyenda ejecuta/espera/lista, CPU en una fila, sin letras griegas.

| id | Qué dibuja | Página |
|---|---|---|
| `cmp-gantt-secuencial` | 3 tareas en serie; tramos ejecuta/espera; fila CPU con «inactiva» | 1 |
| `cmp-gantt-hilos` | mismas tareas en hilos; espera solapada, ejecución turnada por el GIL | 3 |
| `cmp-gantt-asyncio` | mismas tareas en un hilo con `gather`; ejecución corta intercalada | 3, 4 |
| `cmp-gantt-await-en-serie` | el anti-patrón: `await` uno tras otro = secuencial | 4 |
| `cmp-gantt-procesos` | 2 CPU con ejecución simultánea | 3 |
| `cmp-matriz-2x2` | concurrente × paralelo y dónde cae cada estrategia | 3 |
| `cmp-event-loop` | traza del loop con 3 corrutinas (cuándo cede, cuándo reanuda) | 4 |
| `cmp-bloqueo-del-loop` | un cálculo de 2 s dentro del loop detiene a las demás | 4 |
| `cmp-vectorizar` | bucle elemento a elemento vs un arreglo con carriles SIMD | 5 |
| `cmp-amdahl` | curvas teóricas 1/(S+(1−S)/P) para S = 0.1, 0.25, 0.5 | 5 |
| `cmp-arbol-decision` | árbol de la página 6 | 6 |

Cada figura: `aria-label` ≥ 80 caracteres, fila en `course/10_apis/_assets/CREDITOS.md` (crear el `_assets/` de la unidad si no existe y que el test de créditos lo cubra), `::: figure {#cmp-… title="…"}` en su página.

### Código y medición
- **Servidor.** `servidor.py` ya acepta `?lento=<segundos>` (duerme y contesta) y atiende en hilos. Se verifica que 20 peticiones simultáneas no se serialicen; si hace falta, un endpoint `GET /calculo?n=` (bucle puro de Python, determinista) para la carga que calcula. No se rompe `test_apis_curriculum.py`.
- **Dependencias.** `pyproject.toml` de `codigo/10_apis` agrega `httpx` (cliente async) y `numpy` (vectorizar); se regenera `uv.lock`. Alternativa si el alumno falla instalando: `asyncio.to_thread(requests.get, …)`.
- **Notebook.** `codigo/10_apis/computo.ipynb`, generado por `tools/gen_notebook_computo.py` (patrón de `gen_notebook_apis.py`), con `tools/test_computo_curriculum.py` que lo compara byte a byte y comprueba, arrancando el servidor, que cada estrategia devuelve lo mismo que la secuencial. Las celdas de procesos viven en `codigo/10_apis/trabajo_computo.py` (un proceso nuevo reimporta su función; ver `BrokenProcessPool` en `[[el-gil]]`).
- **Benchmarks (una sola corrida, números reales en las páginas):** 20 / 100 / 500 llamadas con `?lento=0.2` en secuencia, hilos (≤ 32) y `asyncio`; cálculo con 1, 2 y 4 procesos; bucle de Python vs NumPy sobre 5 M de elementos. Tiempos de máquina del profesor, etiquetados como tales.

### Archivos

Nuevos: `course/10_apis/2_computo_y_concurrencia/{0_index,1_donde_pasa_el_tiempo,2_procesos_hilos_y_gil,3_concurrente_paralelo_asincrono,4_asyncio_y_el_event_loop,5_vectorizar,6_elegir_la_estrategia}.md`, `course/10_apis/_assets/{cmp-*.svg,CREDITOS.md}`, `tools/{gen_computo.py,test_gen_computo.py,gen_notebook_computo.py,test_computo_curriculum.py}`, `codigo/10_apis/{computo.ipynb,trabajo_computo.py}`.
Modificados: `course/10_apis/0_index.md`, `course/_official/calendar/1_2026-o26.yaml` (+ `session-17`), `course/0_index.md` y `README.md` sólo si cambia el horario, `codigo/10_apis/{pyproject.toml,uv.lock,servidor.py?}`, `CLAUDE.md`/`AGENTS.md` (mencionar los generadores nuevos).

### Verificación al final (secuencial)
`raya validate` + `raya build` (comando de `CLAUDE.md`), un solo `pytest tools/ -q`, lectura de coherencia de las 6 páginas, rastreo de analogías (`grep -iE "imagina|es como|como si|analog|piensa en|restaurante|cocina"`), y todos los «Deberías ver» contra la corrida real.

## Orquestación

1. **Contrato** (secuencial, yo): ids, orden, tabla de figuras, reglas de escritura, términos y su primera página, estructura fija de cada página (pregunta → definición → comando → salida → figura → «al diseñar/al revisar IA busca»). Va al scratchpad.
2. **Ronda adversarial del plan**: Codex astra (solo lectura) + un revisor Opus 5.5 leen este plan y el contrato sin ver mis conclusiones.
3. **Enjambre en paralelo (archivos disjuntos):** 6 escritores de página (Sonnet 5.5), 1 agente de figuras (`gen_computo.py` + test + créditos), 1 agente de servidor/notebook/medición, 1 agente de índices/calendario/CLAUDE. Revisión adversarial por página (Opus 5.5) leyendo, no ejecutando.
4. **Secuencial al final:** una corrida de benchmarks, `validate`/`build`/`pytest`, lectura de coherencia, commit(s) por área.

---

# ENMIENDAS tras la revisión adversarial (mandan sobre todo lo anterior)

Revisión Opus 5.5 incorporada; la de Codex astra sigue en curso (si llega, se aplica como segunda ronda).

**Páginas (5 + índice, ~100 min con corte).** Se funde `procesos-hilos-y-gil` en la 3 (ya está en `[[el-gil]]`; aquí sólo tabla + enlace). Orden final:

| # | id | Archivo | Min |
|---:|---|---|---:|
| 1 | `donde-pasa-el-tiempo` | `1_donde_pasa_el_tiempo.md` | 15 |
| 2 | `concurrente-paralelo-asincrono` | `2_concurrente_paralelo_asincrono.md` (tabla proceso/hilo/GIL con enlace a `[[el-gil]]`; **condición de carrera** con un contador sin lock que da un total equivocado y el `Lock` que lo arregla) | 30 |
| 3 | `asyncio-y-el-event-loop` | `3_asyncio_y_el_event_loop.md` | 25 |
| 4 | `vectorizar` | `4_vectorizar.md` | 20 |
| 5 | `elegir-la-estrategia` | `5_elegir_la_estrategia.md` | 10 |

Corte si falta tiempo: Amdahl (4), luego combinar estrategias (5). Las páginas 2 y 3 no se recortan. La figura `cmp-gantt-procesos` sigue en la 2.

**Definiciones corregidas.** *Asíncrono* = la llamada regresa antes de tener el resultado y quien espera cede el control de forma explícita (`await`); es un **modelo de programación**, no una celda de la matriz. La matriz `cmp-matriz-2x2` es concurrente × paralelo y ubica las estrategias (hilos, `asyncio`, procesos); `asyncio` y hilos son concurrentes y no paralelos en Python con GIL. Amdahl y «más workers que CPU» sólo aplican a trabajo que **calcula**; para esperar, 100 hilos o 1000 corrutinas es válido.

**Servidor (`codigo/10_apis/servidor.py`).**
- `request_queue_size` por omisión es 5: una subclase `class Servidor(ThreadingHTTPServer): request_queue_size = 1024` usada en `__main__` **y** en `tools/test_apis_curriculum.py` (el test arma su propio servidor).
- La radiografía imprime ~10 líneas por petición: agregar modo silencioso (variable de entorno `FDD_SILENCIO=1` o `?silencio=1`; elegir una y documentarla) para los benchmarks.
- `peticiones += 1` sin candado es una carrera real: protegerlo con el `candado` existente (o dejarlo como ejemplo y decirlo; elegir lo primero).
- `/calculo` **fuera**: corre bajo el GIL del servidor y no se paraleliza desde el cliente. El cálculo de las demostraciones vive en `trabajo_computo.py` (local). Lo único del servidor que calcula, si se usa, es para mostrar que se serializa.

**Benchmarks honestos.**
- Mismo límite de concurrencia en las tres estrategias, declarado en la tabla: hilos `max_workers=32`, `asyncio` con `Semaphore(32)` y `httpx.Limits(max_connections=32)`; y una fila extra «sin límite práctico» (100 hilos / 100 conexiones) sólo para mostrar que el tope es un parámetro, no del modelo.
- Secuencial **sólo con 20** llamadas (4 s); 100 y 500 se muestran como cálculo (N × 0.2 s) etiquetado «calculado, no medido».
- Descartar una corrida de calentamiento. Medir el cliente con `time.perf_counter`.
- NumPy: usar `float64` (la suma de cuadrados de 0..5 M desborda `int64`), comprobar que los resultados coinciden, medir aparte la creación del arreglo, descartar calentamiento. **No atribuir la ganancia a SIMD**: casi toda sale de sacar el bucle del intérprete; SIMD es factor secundario y se dice así.
- Procesos para el cálculo local: 1, 2 y 4 (tope 4), una sola corrida.

**Notebook.** En celdas se usa `await` de nivel superior; `asyncio.run(...)` sólo en archivos `.py` (en un notebook truena con «cannot be called from a running event loop»). `test_computo_curriculum.py` lo verifica. `asyncio.to_thread(requests.get, …)` no es `asyncio` real: son hilos (executor por omisión `min(32, cpu+4)`); si se menciona, se nombra así. Los pasos de instalación (`uv sync` con numpy y httpx) van como **trabajo previo a la clase** (aula sin internet): decirlo al inicio del índice.

**Anti-patrones y estilo.** «Cambio de contexto» y «turnada por el GIL» se prueban con una medición o un comando, no sólo con el dibujo.

**Repo.** Crear `course/10_apis/_assets/` con `CREDITOS.md`; confirmar que ningún id `cmp-*` exista ya (`grep -r "cmp-" course tools`); regenerar `uv.lock`; confirmar que el jueves 2026-10-22 no tuvo clase (no hay `cancellation`: dejar `session-17` el 2026-10-27 y avisar al profesor).
