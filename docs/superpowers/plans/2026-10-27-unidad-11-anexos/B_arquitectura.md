# Arquitectura de concurrencia y cómputo — insumo para la unidad

Fuentes leídas: `fdd_p26/clase/16_computo/06,07` (árbol de decisión, chatbot v1→v4, pool, M1–M6), `18_intro_a_apis/02` (desglose DNS/TCP/TLS/servidor, keep-alive), `19_diseno_api/06` (proxy/LB/gateway, 429 + `Retry-After`), `20_arquitectura_de_software/05` (monolito vs distribuido, falacias), `15/03` (roofline, power wall); nuestras `course/10_apis/2_computo_y_concurrencia/1..5` y `codigo/10_apis/servidor.py`.

**Cómo atiende el servidor de la clase** (`servidor.py`): `ThreadingHTTPServer` = **un hilo por conexión**, sin tope de hilos; `request_queue_size = 1024` es el *backlog* del `listen()` (cola del kernel, no de Python); con `HTTP/1.1` y keep-alive el hilo vive lo que vive la conexión; `?lento=` hace `time.sleep` y bloquea **sólo su hilo**; el estado compartido (`ventas`, `peticiones`) va bajo un único `Lock` (sección crítica serializada). Es el patrón 1 del catálogo con sus dos riesgos visibles: no hay límite de concurrencia (riesgo de agotar memoria) y el `Lock` global es un punto de serialización. Úsalo como ejemplo vivo en la página de hilos.

Notación (consistente con p26): tarea τᵢ, `exec(τᵢ)` tramos en CPU, `wait(τᵢ)` tramos en espera, `P` CPUs, `H` hilos. Para servicios añado: λ throughput (peticiones/s), W latencia por petición (s), L peticiones en vuelo, c tope de concurrencia.

---

## 1. Catálogo de patrones

Formato: **Qué** · **Diagrama** · **Sí** · **No** · **Riesgo** · **Real**.

**1. Hilo por conexión.** Qué: cada conexión aceptada recibe un hilo que la atiende de principio a fin. Diagrama: socket `accept` → caja «despachador» → N cajas «hilo k» → caja «estado compartido + Lock». Sí: pocas conexiones (≲ cientos), trabajo que espera, librerías bloqueantes. No: miles de conexiones ociosas (keep-alive, WebSocket). Riesgo: sin tope → cada hilo reserva pila; un pico abre miles de hilos. Real: `ThreadingHTTPServer` (nuestro servidor), Apache httpd MPM `worker`.

**2. Prefork (procesos pre-creados).** Qué: un maestro crea K procesos al arrancar; cada uno acepta del mismo socket. Diagrama: maestro → K cajas proceso (cada una con su GIL) ← socket compartido. Sí: Python con trabajo de CPU por petición; aislar fallos (un proceso muere, los otros siguen). No: estado en memoria que deba compartirse entre peticiones. Riesgo: K × memoria del proceso; K mayor que núcleos en carga de CPU no suma. Real: Gunicorn (workers `sync`; su documentación sugiere `2 × núcleos + 1`), Apache MPM `prefork`, PostgreSQL (un proceso por conexión).

**3. Event loop (un hilo, muchas esperas).** Qué: un hilo atiende todas las conexiones; cada manejador cede en cada espera. Diagrama: cola de «listos» → loop → manejador ejecuta hasta `await` → registra el socket en el selector (`epoll`) → evento listo vuelve a la cola. Sí: miles de conexiones que casi sólo esperan; streaming/WebSocket. No: manejadores que calculan o usan librerías bloqueantes. Riesgo: una llamada bloqueante (`requests`, `time.sleep`, bucle largo) congela a **todas** las conexiones. Real: nginx, Node.js, Redis (comandos en un hilo), Uvicorn.

**4. Híbrido: un loop por núcleo.** Qué: prefork de K procesos, cada uno con su event loop. Diagrama: maestro → K procesos, dentro de cada uno un loop. Sí: servicios Python async en producción que deben usar todos los núcleos. No: máquina de 1 CPU (sobra). Real: nginx (`worker_processes auto`), Gunicorn con `UvicornWorker`.

**5. Worker pool (pool de hilos o procesos).** Qué: W workers creados una vez; las tareas entran a una cola interna y las toma el primero libre. Diagrama: productor → cola → W cajas worker → resultados. Sí: muchas tareas cortas; amortizar el costo de crear (medido: 0.73 s un pool por llamada vs 0.07 s un pool para todas). No: crear el pool dentro del manejador o del bucle. Riesgo: `max_workers` grande en CPU; `lambda` a procesos (`PicklingError`). Real: `ThreadPoolExecutor` (por omisión `min(32, CPUs+4)`), executor por omisión de `asyncio`, thread pool de libuv en Node (4 hilos por omisión).

**6. Límite de concurrencia (semáforo).** Qué: como máximo c operaciones en vuelo; la c+1 espera. Diagrama: N tareas → compuerta «c fichas» → recurso remoto; tareas sin ficha en fila. Sí: siempre que llames a algo externo; c se elige con la ley de Little y con el límite del proveedor. No: c sin medir ni justificar. Riesgo: c alto satura al otro lado o al propio cliente (medido: `asyncio` con c=100 tardó 10.91 s vs 3.41 s con c=32, una corrida). Real: nuestro `Semaphore(32)` + `httpx.Limits(max_connections=32)`.

**7. Cola y backpressure.** Qué: una cola **acotada** entre productor y consumidor; si se llena, el productor espera o se rechaza la petición (429/503). Diagrama: productor → cola [capacidad Q] → consumidores; flecha de retorno «llena: espera / 429». Sí: ráfagas más rápidas que el consumidor; desacoplar a quien recibe de quien procesa. No: cola sin tope (sólo mueve el problema a la memoria y a la latencia). Riesgo: latencia en cola = Q/λ, crece sin aviso. Real: `asyncio.Queue(maxsize=…)`, `request_queue_size` de nuestro servidor (backlog del kernel), RabbitMQ/Redis como broker de Celery.

**8. Bulkhead (compartimentos).** Qué: un pool/semáforo **separado** por dependencia, para que una lenta no consuma los recursos de las demás. Diagrama: servicio con 3 pools (API A: 10, API B: 10, BD: 5) → 3 dependencias; A en rojo no toca B. Sí: varias dependencias externas de distinta confiabilidad. No: una sola dependencia. Riesgo: tamaños mal repartidos dejan capacidad ociosa. Real: Hystrix de Netflix (hoy en mantenimiento) lo popularizó junto con el circuit breaker.

**9. Timeouts.** Qué: tope explícito de espera por llamada (conexión y lectura). Diagrama: Gantt de una tarea con barra de espera cortada en `t_max` → rama «error». Sí: **toda** llamada de red. No: hay excepción razonable; lo que cambia es el valor. Riesgo: sin timeout, una llamada colgada retiene su hilo/ficha para siempre y Little dice que L crece hasta agotar c. Real: `requests` no tiene timeout por omisión; `httpx` sí (5 s).

**10. Reintentos con backoff exponencial y jitter.** Qué: reintentar fallos transitorios (timeouts, 429, 503) esperando `base · 2ᵏ` más un azar. Diagrama: Gantt: intento 1 ✗, pausa 0.1, intento 2 ✗, pausa 0.2+azar, intento 3 ✓. Sí: errores transitorios y operaciones idempotentes (GET, PUT, o POST con `Idempotency-Key`, que nuestro servidor implementa). No: 4xx de cliente (400, 401, 403, 404); POST no idempotente. Riesgo: reintentos sincronizados = tormenta que tumba al servidor que se recuperaba; reintentar en cada capa multiplica (3 capas × 3 = 27). Real: SDKs de AWS; respetar `Retry-After`.

**11. Pool de conexiones / keep-alive.** Qué: reusar conexiones TCP/TLS abiertas en vez de abrir una por petición. Diagrama: cliente → pool (k conexiones) → servidor; primera petición con DNS+TCP+TLS, siguientes sin ellos. Sí: muchas peticiones al mismo host. No: tamaño del pool menor que c (las tareas esperan conexión, no red). Riesgo: crear un `Client`/`Session` por petición. Real: `requests.Session`, `httpx.Client`, PgBouncer y HikariCP (pools de BD).

**12. Batching.** Qué: agrupar k elementos en una sola llamada o una sola operación. Diagrama: k peticiones pequeñas → acumulador (tamaño k o tiempo t) → 1 llamada. Sí: costo fijo por llamada alto (red, arranque de kernel, GPU); el proveedor ofrece endpoint por lotes. No: latencia por elemento crítica. Riesgo: un lote grande falla entero; latencia del primero = espera del lote. Real: Batch API de OpenAI; batching dinámico de NVIDIA Triton; batching continuo de vLLM.

**13. Caché.** Qué: guardar la respuesta y no repetir la llamada o el cálculo. Diagrama: petición → caché (hit → respuesta) / (miss → origen → guardar). Sí: lecturas repetidas, datos que cambian poco. No: datos que deben ser frescos; escrituras. Riesgo: invalidación; estampida al expirar una llave popular. Real: `ETag`/`If-None-Match` → 304 en nuestro servidor; Redis; CDNs; `functools.lru_cache`.

**14. Offload de CPU (procesos o cola).** Qué: el manejador no calcula; delega a un pool de procesos (misma máquina) o a una cola con workers (otras máquinas). Diagrama: loop → `run_in_executor(ProcessPool)` → resultado; versión distribuida: API → cola → workers → almacén de resultados; el cliente consulta o recibe webhook. Sí: cálculo > decenas de ms dentro de un servicio async. No: cálculo de µs (serializar cuesta más). Riesgo: copiar datos grandes entre procesos. Real: Celery con Redis/RabbitMQ; chatbot v3/v4 de p26.

**15. Vectorizar en el borde.** Qué: al recibir datos, convertirlos una vez a arreglo/DataFrame y calcular con operaciones de columna, nunca fila por fila en Python. Diagrama: N respuestas JSON → **un** `DataFrame` → operaciones vectoriales → resultado. Sí: transformación numérica sobre muchos registros. No: lógica por registro con ramas y llamadas externas. Riesgo: `apply`/`iterrows` (bucle de Python disfrazado); `dtype` que desborda. Real: pandas/NumPy/Polars.

**16. Escalado vertical vs horizontal.** Qué: más CPU/RAM en una máquina vs más réplicas detrás de un balanceador. Diagrama: (a) una caja que crece; (b) LB → R réplicas sin estado → BD compartida. Sí vertical: primero, es más barato en complejidad. Sí horizontal: techo de la máquina, disponibilidad. No horizontal: estado en memoria (como `ventas` de nuestro servidor: dos réplicas tendrían dos verdades). Riesgo: la BD compartida se vuelve el cuello. Real: Kubernetes HPA, balanceadores de nube.

**17. Rate limiting en el borde.** Qué: tope de peticiones por cliente; excedente → `429` + `Retry-After`. Diagrama: clientes → gateway (contador por token) → servicio. Sí: API pública o cara. Real: API de GitHub (5000/h autenticado).

---

## 2. Ley de Little

**Enunciado.** En un sistema estable, L = λ · W: peticiones en vuelo = throughput × latencia. Se reescribe λ = L / W: con concurrencia L fija, el throughput lo decide la latencia.

**Con las mediciones de la unidad** (W ≈ 0.2 s por llamada):

| Caso | L (en vuelo) | λ teórico = L/W | λ medido | Comentario |
|---|---|---|---|---|
| Secuencial, 20 llamadas | 1 | 5/s | 20/4.04 = **4.95/s** | coincide |
| 32 hilos, 20 llamadas | 20 (N < c) | 100/s | 20/0.23 = 87/s | limita N, no c |
| 32 hilos, 500 llamadas | 32 | **160/s** | 500/3.32 = **151/s** | 94 % del ideal |
| asyncio c=32, 500 | 32 | 160/s | 500/3.41 = 147/s | |
| 100 hilos, 500 | 100 | 500/s | 500/1.52 = 329/s | sobrecosto crece |

- **Tiempo total predicho** para N llamadas con tope c: ⌈N/c⌉ · W = ⌈500/32⌉ · 0.2 = 16 · 0.2 = **3.2 s** (medido 3.32 s).
- **Latencia efectiva despejada**: W = L/λ = 32/151 = 0.212 s → 12 ms por llamada de sobrecosto (cliente + servidor + red local).
- **Al diseñar**: si un proveedor permite 600 peticiones/min (10/s) y su latencia es 1.5 s, c = λ·W = 10 · 1.5 = **15**. Más de 15 en vuelo sólo genera 429.
- **Del lado del servidor**: nuestro `ThreadingHTTPServer` con λ = 151/s y W = 0.2 s mantiene L ≈ 30 hilos vivos. Si W sube a 2 s (dependencia lenta) con el mismo λ, L = 300 hilos: así un servidor sin timeout ni tope se cae por una dependencia lenta.
- **Para CPU** el tope no es c sino P: λ_max ≈ P / exec(τ). Con 8 CPU y 50 ms de CPU por petición, ≤ 160/s sin importar cuántos hilos.

---

## 3. Mapa concepto → patrón → página

| Concepto | Patrón(es) que introduce | Página actual |
|---|---|---|
| exec/wait, CPU-bound vs I/O-bound, desglose DNS/TCP/TLS/servidor | timeouts (9), pool de conexiones (11) | `1_donde_pasa_el_tiempo` |
| concurrente (solapamiento de ciclos de vida), hilos, `Lock` | hilo por conexión (1, con `servidor.py`), worker pool (5), estado compartido | `2_concurrente_paralelo_asincrono` |
| paralelo, procesos, GIL | prefork (2), offload de CPU (14) | `2_…` |
| asíncrono, event loop | event loop (3), híbrido (4) | `3_asyncio_y_el_event_loop` |
| `Semaphore`, `gather`, Little | límite de concurrencia (6), cola + backpressure (7), reintentos (10) | `3_…` |
| vectorizar, Amdahl | vectorizar en el borde (15), batching (12) | `4_vectorizar` |
| elegir | bulkhead (8), caché (13), escalado (16), rate limit (17), los Casos | `5_elegir_la_estrategia` |

Si la sección se vuelve unidad propia, agregar una página «Arquitectura de un servicio» entre 4 y 5 con 6, 7, 8, 10, 16 y la ley de Little completa; las páginas 1–3 sólo nombran el patrón al final de cada concepto (paso (e) del brief).

---

## 4. Seis diagramas SVG (para `tools/gen_computo.py`, prefijo `cmp-`)

1. **`cmp-arq-servidor-hilos`** — `servidor.py` por dentro: clientes → backlog del kernel (1024) → `accept` → hilo 1…N → `dict ventas` con candado; marca en rojo «sin tope de hilos».
2. **`cmp-arq-tres-servidores`** — tres columnas lado a lado: hilo por conexión, event loop (selector + cola de listos), prefork (maestro + K procesos con su GIL). Etiqueta en cada una: qué consume por conexión.
3. **`cmp-arq-little`** — tubo con L=32 fichas en vuelo, entrada λ, salida λ, cada ficha 0.2 s; anotación L = λW, 32 = 160 · 0.2; debajo los 500 en 16 tandas.
4. **`cmp-arq-cliente-resiliente`** — tareas → semáforo (c) → pool de conexiones (k ≥ c) → API; en la flecha de retorno: timeout, 429 → backoff con jitter → reintento; bulkhead: dos semáforos para dos APIs.
5. **`cmp-arq-cola-backpressure`** — productor → cola acotada Q → W workers; flecha «llena → 429 / espera»; cuadro con latencia en cola = Q/λ.
6. **`cmp-arq-hibrido`** — un proceso con event loop para I/O → `run_in_executor` → pool de P procesos para CPU → resultado vuelve al loop; abajo, la versión distribuida: LB → réplicas → cola → workers.

---

## 5. Casos

**Caso A — scraper de 10 000 URLs de 50 dominios.** Tiempo: espera (≈ 99 %, como las 20 llamadas medidas). Estrategia: asyncio + `httpx.AsyncClient` (o hilos si la librería es `requests`). Arquitectura: semáforo global c y **semáforo por dominio** (bulkhead, cortesía con cada sitio), timeout, backoff ante 429, caché por URL para reanudar. Little: W ≈ 0.5 s, c = 100 → λ ≈ 200/s → ≈ 50 s total; secuencial = 5000 s. Procesos: no, no hay CPU que repartir; el parseo HTML se vuelve CPU sólo si es pesado, y entonces va a un pool de procesos aparte.

**Caso B — API que sirve un modelo (predicción).** Tiempo: CPU/GPU por petición (exec domina). Estrategia: el borde recibe con event loop (Uvicorn), la inferencia **no** corre en el loop: pool de procesos (P workers) o worker con GPU; **batching dinámico** para llenar la GPU; cola acotada con 429 cuando se llena; escalado horizontal con réplicas sin estado detrás de un balanceador. Hilos: no ayudan si el modelo es Python puro (GIL); sí si la librería libera el GIL (NumPy, PyTorch en sus operaciones). Little: con 8 workers y 80 ms por predicción, λ_max = 100/s; para 300/s → batching o 3 réplicas.

**Caso C — pipeline que ingesta 3 APIs y transforma con pandas/NumPy.** Dos fases con tramos distintos. Ingesta (espera): asyncio o hilos, **bulkhead** por API (cada una su límite y timeout), reintentos sólo en GET, pool de conexiones por host. Transformación (cálculo): concatenar **una vez** las respuestas en un `DataFrame` y vectorizar (16× medido sobre bucle); procesos sólo si tras vectorizar sigue dominando el cálculo y los datos se parten sin copiar mucho (Amdahl: la ingesta y la concatenación son la fracción serial). Escalado: vertical primero; horizontal sólo si un día no cabe en memoria.

| Caso | Tramo dominante | Estrategia | Patrones clave |
|---|---|---|---|
| A scraper | espera | asyncio / hilos | 6, 8, 9, 10, 13 |
| B modelo | cálculo | loop + procesos/GPU | 3, 4, 7, 12, 14, 16 |
| C pipeline | espera, luego cálculo | asyncio → vectorizar | 8, 9, 10, 11, 15 |
