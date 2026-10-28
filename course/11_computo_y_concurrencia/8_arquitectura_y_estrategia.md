---
id: arquitectura-y-estrategia
title: "Arquitectura y estrategia"
nav_title: "Arquitectura y estrategia"
summary: "Lo que la unidad midió, junto y convertido en diseño: tres modelos de servidor, capacidad con la Ley de Little, latencia de cola y p99, timeouts, reintentos, aislamiento y escalado, un árbol de decisión, los anti-patrones con su señal y tres casos resueltos."
status: ready
estimated_time: 15m
tags: [concurrencia, arquitectura, little, capacidad, timeouts, backpressure, bulkhead, escalado, decision]
prerequisites: [vectorizar]
---

# Arquitectura y estrategia

**Página 8 de 8 · Cómputo y concurrencia** · Pregunta: con lo que ya mediste, ¿cómo se diseña un servicio o un proceso que espera y calcula, y cómo sabes que elegiste mal? · Meta: elegir un modelo de servidor y sus topes con una cuenta de Little, y defender la decisión de tres casos con lo que hay que medir.

| Término | Definición de una línea | Símbolo |
|---|---|---|
| **modelo de servidor** | Cómo un servidor reparte sus conexiones entre hilos, un event loop o procesos | — |
| **throughput** | Peticiones que terminan por segundo, en régimen estable | $\lambda$ |
| **capacidad** | El $\lambda$ más alto que el sistema sostiene cumpliendo su latencia objetivo y sin acumular cola | $\lambda_{\max}$ |
| **latencia de cola / de servicio** | Lo que una petición espera antes de que la admitan / lo que dura desde que la admiten | $\operatorname{start}-\operatorname{arrival}$ / $d$ |
| **p99** | La latencia que el 99 % de las peticiones no supera | $p_{99}$ |
| **timeout / deadline** | Tope de espera de una llamada / instante absoluto en que la petición entera deja de servir | $t_{\max}$ |
| **backoff** | Pausa creciente entre reintentos, con un componente al azar (*jitter*) | — |
| **bulkhead** | Un tope separado por dependencia, para que una lenta no agote los recursos de las demás | $k_i$ |
| **backpressure** | La señal que frena al productor cuando la cola acotada se llena | — |

## En corto

- **Ninguna idea es nueva aquí: se junta.** Cada página dejó una medición y un patrón; esta página los pone lado a lado y añade lo que un servicio real necesita encima: timeouts, reintentos, aislamiento, escalado.
- **La cuenta que manda es $L=\lambda\cdot W$.** Dimensiona hilos, permisos, conexiones y colas, y explica por qué una dependencia lenta tumba a un servidor que con la misma carga funcionaba.
- **Primero las restricciones, después la herramienta.** Tipo de trabajo, dependencia, recurso limitante, concurrencia, latencia objetivo y aislamiento deciden; el árbol de decisión es el resumen de esas preguntas.

## Tres modelos de servidor

::: definition {#cmp-def-arq-modelo-servidor title="Modelo de servidor"}
La regla con la que un servidor asigna **ejecutores** (hilos, procesos, el hilo de un event loop) a las conexiones que acepta. Hay tres modelos básicos: **hilo por conexión** (cada conexión tiene su hilo de principio a fin), **event loop** (un hilo atiende todas las conexiones y cada manejador cede el hilo en cada espera) y **prefork o multiproceso** (un maestro crea $K$ procesos que aceptan del mismo socket). El modelo decide **qué cuesta cada conexión** y, por lo tanto, cuántas aguanta.
:::

**Otro ángulo.**

::: figure {#cmp-arq-servidores title="Tres modelos de servidor lado a lado, y el híbrido"}
![Tres modelos de servidor lado a lado. Hilo por conexión: accept entrega cada conexión a un hilo y todos tocan un estado con un Lock; cuesta un hilo con su pila por conexión; sí para pocas conexiones y código bloqueante, no para miles de conexiones ociosas; ejemplo, el ThreadingHTTPServer de la clase. Event loop: un selector vigila los sockets, las listas pasan a una cola y un hilo las ejecuta una a la vez; sí para miles de conexiones que esperan, no para manejadores que calculan o bloquean; nginx, Node.js, Uvicorn. Prefork: un maestro crea K procesos que aceptan del mismo socket, cada uno con su GIL; sí para cálculo por petición y aislar fallos, no para estado compartido en memoria; Gunicorn. Abajo, el híbrido: un event loop por proceso.](_assets/cmp-arq-servidores.svg)
:::

| | Hilo por conexión | Event loop | Prefork / multiproceso | Híbrido: loop + procesos |
|---|---|---|---|---|
| **Qué ocupa cada conexión** | un hilo con su pila, mientras viva la conexión | un socket y una corrutina | un proceso entero mientras la atiende | una corrutina dentro de uno de $K$ procesos |
| **Quién decide el turno** | el sistema operativo (preventivo) y el GIL | cada manejador, en su `await` (cooperativo) | el sistema operativo, un GIL por proceso | cooperativo dentro del proceso, preventivo entre procesos |
| **Paralelismo de cálculo** | no, en Python con GIL | no | sí, hasta $P$ | sí, hasta $P$ |
| **Lo rompe** | miles de conexiones ociosas; un pico sin tope | una llamada bloqueante o un cálculo en el loop | estado en memoria que deba compartirse; memoria $\times K$ | lo mismo que al loop, en cada proceso |
| **Lo viste en** | [[secuencial-concurrente-paralelo]] | [[asincrono-y-el-event-loop]] | [[calcular-en-paralelo]] | [[calcular-en-paralelo]] (*offload*) |

**Matemática.** Lo que cuesta un modelo se cuenta con Little: los ejecutores ocupados en promedio son $L=\lambda\cdot W$, donde $W$ es lo que una petición retiene su ejecutor. En hilo por conexión, $L$ son **hilos vivos**; en prefork con workers síncronos, **procesos ocupados**; en un event loop, **corrutinas** (y la CPU que usan, $\lambda\cdot e$, no puede pasar de 1 hilo).

**Ejemplo.** El servidor de la clase es `ThreadingHTTPServer`: un hilo por conexión, sin tope de hilos, un único `Lock` para `ventas` y una cola de `listen` de 1024 conexiones. En la corrida de referencia de 500 llamadas con 32 en vuelo terminó a unas 151 peticiones/s, y cada una duerme 0.2 s:

$$L=151\times0.2\approx30\ \text{hilos ocupados}$$

Si la misma carga llegara con $W=2$ s (una dependencia lenta), $L\approx300$ hilos. Nada en `servidor.py` lo impide: así se cae un servidor de hilo por conexión.

**Arquitectura.**

| Modelo | Cuándo sí | Cuándo no | Qué cuesta | Sistema real |
|---|---|---|---|---|
| hilo por conexión | decenas o cientos de conexiones, librerías bloqueantes | miles de conexiones abiertas que casi no hablan (keep-alive largo, WebSocket) | memoria por hilo; sin tope, un pico abre miles | `ThreadingHTTPServer` (la clase); Apache httpd con MPM `worker` |
| event loop | miles de conexiones que casi sólo esperan | manejadores que calculan o usan librerías bloqueantes | todo el código del camino debe ser `async`; un bloqueo congela a todos | nginx, Node.js, Uvicorn; Redis ejecuta sus comandos en un hilo |
| prefork / multiproceso | cálculo por petición en Python; aislar fallos (un proceso muere, los otros siguen) | estado en memoria que deba ser uno solo | $K\times$ la memoria de un proceso; $K>P$ no suma en cálculo | Gunicorn (maestro + workers; su documentación sugiere $2\times$ núcleos $+1$ workers como punto de partida); PostgreSQL es multiproceso pero no prefork: crea un proceso *backend* por cada conexión que acepta |
| híbrido | servicios `async` en producción que deben usar todos los núcleos | una máquina de 1 CPU | lo de los dos: memoria $\times K$ y disciplina `async` | nginx (`worker_processes auto`); Gunicorn con workers de Uvicorn; `uvicorn --workers` |

## Capacidad, latencia y la cola

::: definition {#cmp-def-arq-little title="Ley de Little"}
**En palabras.** En régimen estable, el número medio de peticiones dentro de una frontera es lo que entra por segundo por lo que cada una pasa dentro. Con un tope de $k$ dentro, el throughput no pasa de $k$ entre ese tiempo.

**Formalmente.** $L=\lambda\cdot W$, con $L$ la ocupación media, $\lambda$ el throughput y $W$ el tiempo medio dentro de la frontera elegida. Si $L\le k$, entonces $\lambda\le k/W$. Modelo completo en [[notacion-computo]].
:::

::: definition {#cmp-def-arq-capacidad title="Throughput y capacidad"}
**En palabras.** El throughput es cuántas peticiones terminan por segundo; la capacidad es el throughput más alto que el sistema sostiene cumpliendo una latencia objetivo declarada y sin que la cola crezca.

**Formalmente.** $\lambda$ = peticiones terminadas por segundo en régimen estable (lo que entra es lo que sale). $\lambda_{\max}=\max\{\lambda : p_{99}(\lambda)\le\text{objetivo y la cola no crece}\}$. El techo ideal $k/W$ de Little es una cota superior de $\lambda_{\max}$, no su valor. Modelo completo en [[notacion-computo]].

Sin el objetivo, la capacidad no está definida: casi cualquier sistema «aguanta» más carga si se acepta esperar más.
:::

::: definition {#cmp-def-arq-latencia-cola title="Latencia de cola y latencia de servicio"}
Con la notación de la unidad, la latencia que percibe quien pidió se parte en dos:

$$\operatorname{latencia}(\tau)=\underbrace{\operatorname{start}(\tau)-\operatorname{arrival}(\tau)}_{\text{cola: aún no la admiten}}+\underbrace{d(\tau)}_{\text{servicio: ya admitida}}$$

La de servicio depende del trabajo; la de cola depende **de la carga**: crece cuando llegan más peticiones de las que el sistema termina.
:::

::: definition {#cmp-def-arq-percentil title="Percentil 99 (p99)"}
Ordena las latencias de todas las peticiones de una ventana: $p_{99}$ es el valor que el 99 % no supera. El promedio esconde la cola de la distribución; el $p_{99}$ la muestra. Se mide sobre **todas** las peticiones, incluidas las que fallaron o vencieron, o la degradación desaparece de la gráfica.
:::

**Otro ángulo.**

::: figure {#cmp-arq-little title="Ley de Little con las cifras medidas"}
![Ley de Little: L igual a lambda por W, peticiones en vuelo igual a throughput por latencia. Un tubo con 32 peticiones en vuelo, cada una dentro 0.2 s, entran y salen 160 por segundo: 32 = 160 por 0.2. Debajo, 500 llamadas con 32 en vuelo son 16 tandas de 0.2 s: cota de 3.2 s contra 3.32 s medidos, 151 por segundo. En serie, 20 llamadas con L = 1 dan 5 por segundo; medido 20 entre 4.04 s, 4.95 por segundo. Despejando, W es a lo más 32 / 151, unos 0.212 s: una cota superior, no una medición. El servidor de la clase con 151 por segundo y 0.2 s tiene unos 30 hilos ocupados; si W sube a 2 s, unos 300.](_assets/cmp-arq-little.svg)
:::

**Matemática.** Tres cuentas, todas de [[concurrencia-acotada]] y [[pools-y-recursos]]:

- **Little:** $L=\lambda\cdot W$. Con un tope de $k$ en vuelo, $L\le k$ y entonces $\lambda\le k/W$.
- **Cota del tope:** $n$ tareas iguales con $k$ en vuelo tardan al menos $\lceil n/k\rceil\cdot W$.
- **Sobrecarga sostenida:** si llegan $\lambda_{\text{entra}}$ y salen $\lambda_{\max}<\lambda_{\text{entra}}$, la cola crece $\lambda_{\text{entra}}-\lambda_{\max}$ peticiones por segundo, y la latencia de cola con ella. Una cola más grande sólo retrasa el momento en que se nota.
- **Fan-out y p99:** si una petición necesita 10 respuestas independientes y cada una queda bajo un umbral con probabilidad 0.99, todas quedan bajo él con probabilidad $0.99^{10}\approx0.904$: casi 1 de cada 10 peticiones paga la cola de alguna. Los percentiles no se suman.

**Ejemplo.** Con las mediciones de la unidad (corrida de referencia en una máquina de 8 CPU lógicas):

| Caso | $L$ | $\lambda$ ideal $=L/W$ | Medido | Lectura |
|---|---:|---:|---|---|
| 20 llamadas en serie | 1 | 5/s | 20 en 4.04 s, unas 4.95/s | coincide: $W\approx0.202$ s |
| 500 llamadas, 32 hilos | 32 | 160/s | 500 en 3.32 s, unas 151/s | 94 % del ideal; cota 3.2 s |
| 500 llamadas, `asyncio` con tope 32 | 32 | 160/s | 500 en 3.39 s | parejo con hilos |
| servidor de la clase a 151/s | — | — | $151\times0.2\approx30$ hilos | con $W=2$ s, unos 300 |

Con $\lambda=500/3.32\approx151$/s y $L\le32$, Little sólo da una cota: $W=L/\lambda\le32/151\approx0.212$ s. No se midió $W$ ni un sobrecosto de 12 ms por llamada: la distancia entre la cota de 3.2 s y los 3.32 medidos mezcla el costo de cliente, servidor y red local con la última tanda incompleta (500 no es múltiplo de 32), que baja la ocupación media por debajo de 32.

**Arquitectura.**

- **Qué es:** dimensionar con Little. Los hilos, permisos y conexiones que necesitas son $\lambda\cdot W$ de **esa** frontera: el pool de la BD se dimensiona con lo que tarda cada préstamo de conexión, no con lo que tarda la petición HTTP completa.
- **Cuándo sí:** siempre que fijes un tope, un pool o un número de workers. Si un proveedor acepta 10 peticiones/s y tarda 1.5 s, hacen falta unas $10\times1.5=15$ en vuelo para llegar a su cuota. Ese $k$ no hace respetar la cuota: si $W$ baja a 0.5 s, los mismos 15 dejan pasar 30/s. La cuota se aplica con un limitador de tasa aparte ([[concurrencia-acotada]]).
- **Cuándo no:** Little habla de **promedios** en régimen estable. No te da el $p_{99}$ ni garantiza nada durante un pico.
- **Qué cuesta:** medir $\lambda$ y $W$ en la misma frontera. Mezclar el $W$ del cliente con el $\lambda$ del servidor da números sin sentido.
- **Sistema real:** el `max_connections` de PostgreSQL, el tamaño de un pool como PgBouncer, el número de workers de Gunicorn y el `Semaphore(32)` de la unidad salen de la misma cuenta.

## Timeouts, deadlines y cancelación

::: definition {#cmp-def-arq-timeout title="Timeout y deadline"}
Un **timeout** es el tope de espera de **una** llamada: al vencer, quien espera deja de esperar y recibe un error. Un **deadline** es un **instante absoluto** para la petición entera: cada paso recibe sólo **lo que queda** del presupuesto, no un timeout completo nuevo. Un timeout significa «no sé», no «no pasó»: del otro lado la operación pudo haberse hecho.
:::

**Otro ángulo.** Qué se suelta al vencer un timeout depende de quién esperaba:

| Quién esperaba | Al vencer | Qué sigue ocupado |
|---|---|---|
| una corrutina (`asyncio.timeout`, `wait_for`) | la tarea se **cancela**: le llega `CancelledError` en su `await` y sus `async with` sueltan permiso y conexión | nada en tu proceso, si el código no atrapa la cancelación |
| un hilo con `requests.get(..., timeout=…)` | la llamada lanza una excepción y el hilo sigue | nada, pero un hilo **no** se puede cancelar desde fuera si no tiene timeout |
| cualquiera de los dos | el cliente deja de esperar | el servidor remoto puede seguir trabajando (y cobrando) |

**Matemática.** Sin timeout, una llamada colgada tiene $W\to\infty$: retiene su hilo, permiso o conexión para siempre, y con $\lambda$ fijo Little dice $L=\lambda W$ crece hasta agotar el tope $k$. Con un deadline $t_{\max}$ que cubra la petición completa (adquirir la conexión del pool, conectar, cada lectura y los reintentos), $W\le t_{\max}$ y $L\le\lambda\cdot t_{\max}$: con $\lambda=50$/s y $t_{\max}=2$ s, a lo más 100 en vuelo. Los timeouts de `requests` y `httpx` no bastan para eso: limitan conectar o el silencio entre lecturas, no la duración total.

**Ejemplo.** Presupuesto de 2 s para una petición que consulta la BD y llama a una API: si la BD tardó 0.5 s, la API recibe un timeout de 1.5 s, no de 2 s. Con timeouts fijos de 2 s por paso la petición podría tardar 4 s y responder cuando el cliente ya se fue.

**Arquitectura.**

- **Qué es:** toda llamada de red lleva timeout; la petición lleva un deadline que se reparte.
- **Cuándo sí:** siempre. Lo que se discute es el valor, no la existencia.
- **Cuándo no:** no hay caso razonable sin timeout; un trabajo que de verdad tarda minutos no va en el camino de la petición (va a una cola de trabajos).
- **Qué cuesta:** errores visibles en vez de esperas invisibles, y decidir qué hacer con el «no sé».
- **Sistema real:** `requests` **no** tiene timeout por omisión; `httpx` sí (5 s para conectar, leer, escribir y esperar el pool, cada uno por separado). PostgreSQL tiene `statement_timeout`. En `asyncio`, `asyncio.timeout()` (3.11+) es un deadline sobre todo el bloque.

## Reintentos, idempotencia y estampidas

::: definition {#cmp-def-arq-backoff title="Reintento con backoff exponencial y jitter"}
Repetir una llamada que falló por una causa **transitoria** (timeout, `429`, `503`), esperando antes del intento $j$ una pausa $\text{base}\cdot2^{j}$ con un componente al azar (*jitter*) y un número máximo de intentos. Sólo es seguro si la operación es **idempotente**: repetirla deja el servidor igual que hacerla una vez ([[metodos-y-status]]).
:::

::: definition {#cmp-def-arq-estampida title="Estampida (thundering herd)"}
Muchos clientes o tareas que **despiertan a la vez** para pedir lo mismo: reintentos sincronizados tras una caída, todas las peticiones que encuentran expirada la misma llave de caché, todos los workers que despiertan por una sola conexión. La carga llega concentrada justo cuando el sistema intenta recuperarse.
:::

**Otro ángulo.**

| Respuesta | ¿Reintentar? | Por qué |
|---|---|---|
| timeout, `503` | sí, con backoff, si es idempotente | transitorio; el timeout es «no sé» |
| `429` | sí, respetando `Retry-After` | el servidor dice cuándo |
| `400`, `401`, `403`, `404` | no | el error es tuyo: repetir da lo mismo |
| `POST` sin `Idempotency-Key` | no | puede crear dos ventas |

**Matemática.** Con base 0.1 s y 3 intentos, las pausas son 0.1, 0.2 y 0.4 s más el azar. Los reintentos **se multiplican por capa**: si tres capas reintentan 3 veces cada una, una falla abajo produce hasta $3^3=27$ intentos contra la dependencia que ya estaba mal.

**Ejemplo.** El servidor de la clase implementa `Idempotency-Key` en `POST /ventas`: guarda la respuesta por llave y, si llega la misma llave, devuelve la guardada sin crear otra venta. Con esa llave, el `POST` se puede reintentar.

**Arquitectura.**

- **Qué es:** reintentar en **una** capa, con tope de intentos, backoff con jitter y sólo operaciones idempotentes; contra estampidas, además, juntar las peticiones iguales en una (*request coalescing*).
- **Cuándo sí:** fallos transitorios de una dependencia que se recupera.
- **Cuándo no:** errores `4xx` del cliente; operaciones no idempotentes; cuando el deadline ya no alcanza para otro intento.
- **Qué cuesta:** más carga en el peor momento si se hace mal; por eso el jitter (separa los reintentos en el tiempo) y el tope.
- **Sistema real:** los SDK de AWS reintentan con backoff y jitter; nginx tiene `proxy_cache_lock` para que una sola petición llene una llave de caché mientras las demás esperan.

## Aislar y frenar: bulkhead, cola acotada y backpressure

::: definition {#cmp-def-arq-bulkhead-backpressure title="Bulkhead, cola acotada y backpressure"}
**Bulkhead:** un tope (semáforo o pool) **por dependencia**, de modo que si una se vuelve lenta sólo agota su propio tope. **Cola acotada:** una cola con capacidad máxima $Q$ entre quien recibe y quien procesa. **Backpressure:** lo que pasa cuando esa cola se llena: el productor espera o la petición se rechaza (`429` o `503`), en vez de acumularse sin límite.
:::

**Otro ángulo.**

| Mecanismo | Qué limita | Qué **no** limita | Página |
|---|---|---|---|
| `gather` | nada: reúne resultados | cuántas tareas existen ni cuántas están en vuelo | [[concurrencia-acotada]] |
| `Semaphore(k)` | cuántas entran a la región | cuántas esperan permiso | [[concurrencia-acotada]] |
| pool de $k$ conexiones | cuántas conexiones reales se usan | cuántas tareas esperan conexión | [[pools-y-recursos]] |
| cola de capacidad $Q$ | cuánto trabajo pendiente se acepta | la entrada, si no hay rechazo | esta página |

**Matemática.** En una cola que el consumidor vacía a $\lambda$ por segundo, la última petición de una cola llena espera unos $Q/\lambda$ segundos antes de su $\operatorname{start}$. Con un deadline de $D$ segundos, una cola con $Q>\lambda D$ guarda peticiones que ya no van a llegar a tiempo.

**Ejemplo.** Una API con dos dependencias, A y B, y un solo `Semaphore(20)` compartido: si A pasa de 0.2 s a 2 s, Little dice que A necesita $10\times$ más permisos para el mismo $\lambda$; se los quita a B, que estaba sana. Con `Semaphore(10)` para cada una, A se satura sola y B sigue respondiendo.

**Arquitectura.**

- **Qué es:** un tope por dependencia, una cola acotada antes del trabajo caro y un rechazo explícito cuando se llena.
- **Cuándo sí:** varias dependencias de distinta confiabilidad; ráfagas más rápidas que el consumidor.
- **Cuándo no:** una sola dependencia (el bulkhead sólo agrega capacidad ociosa); una cola sin tope (mueve el problema a la memoria y a la latencia).
- **Qué cuesta:** topes mal repartidos dejan capacidad sin usar; el cliente tiene que saber qué hacer con un `429`.
- **Sistema real:** `asyncio.Queue(maxsize=…)`; el `request_queue_size = 1024` de `servidor.py` es la cola del kernel antes del `accept`; un broker como Redis o RabbitMQ delante de workers de Celery; un pool por base de datos ([[pools-y-recursos]]).

## Escalar: vertical, horizontal y el estado compartido

::: definition {#cmp-def-arq-escalado title="Escalado vertical y horizontal"}
**Vertical:** la misma instancia recibe más recursos (CPU, RAM); la topología no cambia. **Horizontal:** varias **réplicas** del mismo servicio detrás de un balanceador. Escalar horizontalmente exige que el estado que importa **no viva en la memoria de una réplica**, sino en algo compartido (una BD, un caché externo).
:::

**Otro ángulo.**

| Pregunta | Vertical | Horizontal |
|---|---|---|
| ¿qué se multiplica? | CPU y RAM de una caja | réplicas, cada una con sus procesos y sus pools |
| ¿qué no ayuda? | si el cuello es una dependencia externa | si el cuello es la BD compartida: cada réplica le pone más presión |
| ¿qué exige? | nada en el código | servicio sin estado en memoria |
| ¿qué aporta además? | — | sigue funcionando si se cae una réplica |

**Matemática.** Los topes locales se **multiplican**: 4 réplicas $\times$ 2 procesos $\times$ 8 conexiones por pool son $4\times2\times8=64$ conexiones contra la BD. Si la BD acepta 40, ningún pool local lo impide. Y si cada petición gasta $e$ segundos de CPU, una máquina con $P$ CPU no pasa de $\lambda_{\max}\approx P/e$: con 8 CPU y 50 ms (supuestos), $8/0.05=160$/s por réplica, sin importar cuántos hilos tenga.

**Ejemplo.** El servidor de la clase guarda `ventas` y las respuestas por `Idempotency-Key` **en un diccionario en memoria**, protegidos por un `Lock` que sólo coordina los hilos de **ese** proceso. Dos réplicas tendrían dos verdades: una venta creada en la réplica 1 no existe en la 2, y un reintento con la misma llave que cae en la otra réplica crea la venta otra vez. Por eso **no se puede replicar** sin mover ese estado a una BD.

**Arquitectura.**

- **Qué es:** vertical primero (es más barato en complejidad); horizontal cuando la máquina toca techo o hace falta disponibilidad.
- **Cuándo sí horizontal:** servicio sin estado en memoria y un cuello local (CPU del cálculo en el camino de la petición).
- **Cuándo no:** estado en memoria; cuello en una dependencia compartida.
- **Qué cuesta:** balanceador, estado externo, y vigilar el presupuesto global de conexiones.
- **Sistema real:** nginx como balanceador frente a varias instancias de Uvicorn; PgBouncer para que muchas réplicas compartan pocas conexiones a PostgreSQL.

## Las restricciones antes que la herramienta

Antes de escoger hilos, `asyncio` o procesos, se contestan seis preguntas. Cada una tiene una medición y una consecuencia:

| Restricción | Pregunta | Cómo se mide | Qué decide |
|---|---|---|---|
| **tipo de trabajo** | ¿espera o calcula? | $\rho=e/d$ con la tarea sola: CPU del cliente contra reloj ([[donde-pasa-el-tiempo]]) | esperar → hilos o `asyncio`; calcular → vectorizar o procesos |
| **dependencia** | ¿quién está del otro lado y cuánto aguanta? | cuota del proveedor, `max_connections` de la BD, `429` recibidos | el tope $k$ y el tamaño del pool |
| **recurso limitante** | ¿qué se agota primero: CPU, conexiones, memoria, el hilo del loop, la cuota? | CPU/reloj, conexiones en uso, tareas en `blocked` | dónde poner el tope y qué escalar |
| **concurrencia** | ¿cuántas en vuelo hacen falta? | $L=\lambda\cdot W$ | número de hilos, permisos o conexiones |
| **latencia objetivo** | ¿cuánto puede tardar una petición? | $p_{99}$ de todas las peticiones, deadline | timeouts, cola acotada, si el trabajo va en el camino de la petición o a una cola |
| **aislamiento** | ¿qué no debe caerse si otra cosa se cae? | qué pasa al hacer lenta una dependencia | bulkhead, procesos en vez de hilos, estado fuera de la memoria |

**El árbol** resume las dos primeras columnas:

::: figure {#cmp-arbol-decision title="Árbol de decisión: de dónde pasa el tiempo a la estrategia"}
![Árbol de decisión. Primera pregunta: el tiempo se va en esperar red o disco, o en calcular; se decide midiendo tiempo de reloj contra tiempo de CPU. Si espera: si hay librería async como httpx, asyncio con gather y un Semaphore, para miles de esperas en un hilo; si no, hilos con ThreadPoolExecutor, para decenas o cientos. Si calcula: si opera sobre arreglos o columnas de números, vectoriza con NumPy o Polars; si no, si cada pedazo es independiente y tarda más que arrancar un proceso, procesos con ProcessPoolExecutor hasta el número de CPU; si no, secuencial y mejora el algoritmo. Si hay esperas y cálculo juntos, asyncio para la red y procesos para el cálculo.](_assets/cmp-arbol-decision.svg)
:::

Los costos que respaldan cada rama, de la corrida de referencia:

| Trabajo | Estrategia | Tiempo |
|---|---|---:|
| 20 llamadas de 0.2 s | secuencial | 4.04 s |
| 500 llamadas de 0.2 s | 32 hilos | 3.32 s |
| 500 llamadas de 0.2 s | `asyncio` con tope 32 | 3.39 s |
| 4 cálculos `calcula` | 1 proceso | 1.45 s |
| 4 cálculos `calcula` | 4 procesos | 0.54 s |
| suma de cuadrados | bucle de Python | 0.141 s |
| suma de cuadrados | NumPy | 0.0091 s |

Las filas de cálculo y las de NumPy son cargas distintas: no se comparan entre sí.

## Anti-patrones: fallo, señal y contención

Un anti-patrón no truena: funciona y anula la ventaja de la estrategia que dice usar. Por eso se busca con una señal medible, no a ojo.

| Fallo arquitectónico | Señal observable | Contención |
|---|---|---|
| **`await` en serie** (`for …: await …`) | $T$ es la suma de las llamadas: 720 ms en la traza del ejemplo, no 280 | `gather` o `create_task`, con tope ([[asincrono-y-el-event-loop]]) |
| **bloquear el loop** (`time.sleep`, `requests`, un cálculo dentro de `async def`) | todas las latencias suben a la del bloqueo: 2060 y 2080 ms en vez de 240 y 260 en la traza; el latido se detiene | cliente `async`, o `run_in_executor` con pool de procesos ([[calcular-en-paralelo]]) |
| **pool por llamada** | el arranque se paga en cada petición: 0.73 s contra 0.07 s en la corrida de referencia | crear el pool una vez y reutilizarlo ([[pools-y-recursos]]) |
| **`lambda` a un proceso** | `PicklingError` (celda 8.2) | la función vive en un módulo importable (`trabajo_computo.py`) |
| **más workers que CPU en trabajo que calcula** | $T$ deja de bajar al pasar $k>P$: 16 tareas cortas tardaron 1.31 s con 8 procesos y 1.32 s con 16, en 8 CPU (una corrida, fuera del notebook) | $k=\min(n,P)$ ([[calcular-en-paralelo]]) |
| **retener un recurso durante una espera larga** (la conexión a la BD mientras se llama a otra API) | conexiones en uso $=\lambda\cdot W$ con el $W$ de la espera larga; tareas en `blocked` esperando el pool | soltar antes de esperar ([[pools-y-recursos]]) |
| **hilo por conexión sin tope** | hilos vivos crecen con $W$: unos 30 con 0.2 s, unos 300 con 2 s, a 151/s | tope de workers, cola acotada, timeouts |
| **llamada sin timeout** | tareas que nunca terminan; $L$ sube hasta el tope | timeout en toda llamada, deadline en la petición |
| **reintentos sin backoff ni tope** | picos de carga sincronizados después de cada caída | backoff con jitter, tope de intentos, una sola capa reintenta |

La fila de «más workers que CPU» **sólo aplica a trabajo que calcula**: para esperar, cientos de hilos o miles de corrutinas son válidos, porque no ocupan CPU mientras esperan.

## Tres casos

Las cifras de los tres casos son **supuestos** para hacer la cuenta, no mediciones: en un caso real se miden primero.

### Caso A · Scraper de 10 000 URLs de 50 dominios

| Restricción | Respuesta |
|---|---|
| tipo de trabajo | espera: como las 20 llamadas medidas, casi todo el tiempo es red (99.4 % sin CPU del cliente en la medición de la página 1) |
| dependencia | 50 sitios ajenos: cortesía con cada uno y `429` posibles |
| recurso limitante | conexiones y la cuota de cada dominio, no la CPU |
| concurrencia | supuesto $W\approx0.5$ s y $k=100$: $\lambda\le100/0.5=200$/s |
| latencia objetivo | ninguna por URL; importa el total y poder reanudar |
| aislamiento | un dominio lento no debe frenar a los demás |

**Decisión.** `asyncio` con un `httpx.AsyncClient` (su pool reutiliza conexiones por host, pero `max_connections` es un límite compartido entre todos los destinos), un semáforo global de 100 y **un semáforo por dominio** (bulkhead, por ejemplo 2 en vuelo por dominio), timeout por llamada, reintento con backoff sólo en `GET` y respetando `Retry-After`, y el resultado de cada URL guardado al terminarla para reanudar. Si la librería disponible es `requests`, hilos con `Session` por hilo y el mismo esquema de topes.

**La cuenta.** En serie: $10\,000\times0.5=5000$ s. Con $\lambda=200$/s: $10\,000/200=50$ s. Procesos: **no**, no hay cálculo que repartir; si el parseo del HTML resulta pesado ($\rho$ alto al medirlo), ese parseo va a un pool de procesos aparte.

**Qué se mide.** $T$ total y $\lambda$ real contra 200/s; cuántos `429` y timeouts por dominio; conexiones abiertas (puertos distintos, como con `/quien` en [[pools-y-recursos]]); el $p_{99}$ por dominio para detectar el lento.

### Caso B · API que sirve un modelo

| Restricción | Respuesta |
|---|---|
| tipo de trabajo | calcula: la predicción es CPU (o GPU) por petición |
| dependencia | el modelo cargado en memoria de cada worker |
| recurso limitante | CPU; memoria $\times K$ por tener el modelo en cada proceso |
| concurrencia | **supuesto**: 8 workers y 80 ms por predicción: techo ideal $8/0.08=100$/s; la capacidad que cumple el $p_{99}$ se mide y queda debajo |
| latencia objetivo | interactiva: un $p_{99}$ declarado y un deadline |
| aislamiento | una predicción lenta no debe congelar la recepción de las demás |

**Decisión.** Recibe con Uvicorn. Ejecuta la predicción fuera del loop, en un pool de $\min(\text{workers},P)$ procesos creado al arrancar; carga el modelo una vez por proceso (o usa un híbrido de $K$ procesos, cada uno con su loop). Delante del pool, una **cola acotada** que responde `429` o `503` con `Retry-After` cuando se llena: sin ella, la latencia de cola crece sin límite. Hilos sólo si la librería suelta el GIL durante la predicción, y entonces cuidando que procesos e hilos internos no pidan más CPU que $P$ entre todos.

**La cuenta.** **Supuesto** de demanda: 300/s contra un techo ideal de 100/s por réplica. Faltan al menos $200$/s: o 3 réplicas sin estado detrás de un balanceador ($3\times100=300$, sin margen), o *batching* (juntar varias predicciones en una llamada al modelo) si el costo por lote crece menos que el número de elementos. Con 300/s de entrada y 100/s de salida en una sola réplica, la cola crecería 200 peticiones por segundo.

**Qué se mide.** $p_{99}$ contra carga creciente (dónde se dobla: esa es la capacidad); largo de la cola y rechazos; CPU por worker; latencia de cola separada de la de servicio.

### Caso C · Pipeline que ingesta 3 APIs y transforma con NumPy y pandas

| Restricción | Respuesta |
|---|---|
| tipo de trabajo | dos fases: ingesta que espera, transformación que calcula |
| dependencia | tres proveedores con cuotas y latencias distintas |
| recurso limitante | la cuota de cada API en la ingesta; la CPU (y la memoria) en la transformación |
| concurrencia | por API: $L_i=\lambda_i\cdot W_i$ estima la ocupación media; **supuesto**: una API de 10 peticiones/s que tarda 1.5 s necesita unas 15 en vuelo para usar su cuota |
| latencia objetivo | ninguna por petición; importa el total del lote |
| aislamiento | una API caída no debe detener la ingesta de las otras dos |

**Decisión.** Ingesta con `asyncio`: un `AsyncClient` (pool de conexiones) por host y, por API, un **limitador de tasa** que aplica su cuota y un **semáforo independiente** que acota cuántas van en vuelo (bulkhead): $L=\lambda W$ estima la ocupación, pero no garantiza la cuota ni fija por sí solo el tope. Timeouts, reintentos sólo en `GET`. Transformación: concatenar **una vez** todas las respuestas en un `DataFrame` o arreglo y operar por columnas: en la medición de [[vectorizar]], bucle 0.141 s contra NumPy 0.0091 s (unas 16 veces). Procesos **sólo** si después de vectorizar el cálculo sigue dominando y los datos se parten sin copiar mucho entre procesos. Escalado vertical primero; horizontal sólo si el lote deja de caber en una máquina.

**La cuenta.** Amdahl: desde el punto de vista del cálculo, la ingesta y la concatenación son la fracción serial $f$; repartir la transformación entre $N$ procesos no baja el total por debajo de ese tramo. Medir las dos fases por separado dice cuál atacar.

**Qué se mide.** $T$ de ingesta y $T$ de transformación por separado; $\rho$ de la transformación; errores y reintentos por API; memoria máxima al concatenar.

| Caso | Tramo dominante | Estrategia | Patrones clave |
|---|---|---|---|
| A · scraper | espera | `asyncio` (o hilos) con topes | tope global + bulkhead por dominio, pool de conexiones, timeout, backoff, reanudar |
| B · modelo | cálculo | loop en el borde + pool de procesos | offload, cola acotada con `429`, batching, réplicas sin estado |
| C · pipeline | espera, luego cálculo | `asyncio` → vectorizar | bulkhead por API, pool por host, timeouts, vectorizar antes de repartir |

## La decisión hasta aquí

| Si el trabajo o la situación… | Haz | Por qué (la medición) | Página |
|---|---|---|---|
| casi todo es tiempo sin CPU del cliente | reorganiza las esperas, no aceleres el cálculo | 20 llamadas: 4.04 s, 99.4 % sin CPU del cliente | [[donde-pasa-el-tiempo]] |
| espera, pocas decenas, con librería bloqueante | hilos (`ThreadPoolExecutor`) | 20 llamadas con 32 hilos: 0.23 s | [[secuencial-concurrente-paralelo]] |
| varias tareas modifican un mismo estado | una región crítica corta con `Lock` | sin `Lock`: 199,769 de 400,000 sumas esperadas | [[secuencial-concurrente-paralelo]] |
| espera, cientos o miles, con librería `async` | `asyncio` con `gather` o `create_task` | una corrutina en espera no ocupa un hilo | [[asincrono-y-el-event-loop]] |
| un `async def` llama algo bloqueante o calcula | sácalo del loop | el loop deja a todas en `ready` mientras tanto | [[asincrono-y-el-event-loop]] |
| muchas llamadas a una dependencia | tope $k=\lambda\cdot W$ con `Semaphore` | 500 llamadas, tope 32: cota 3.2 s, medido 3.32 s | [[concurrencia-acotada]] |
| muchas peticiones al mismo host o a una BD | un pool de conexiones creado una vez, del tamaño que aguanta la BD; suelta la conexión antes de esperas largas | conexiones en uso $=\lambda\cdot W$ | [[pools-y-recursos]] |
| calcula en Python, pedazos independientes | pool de procesos con $k=\min(n,P)$, creado una vez | 4 cálculos: 1.45 s con 1 proceso, 0.54 s con 4 | [[calcular-en-paralelo]] |
| un servicio `async` que también calcula | *offload*: loop + pool de procesos | el cálculo cuenta como espera del loop | [[calcular-en-paralelo]] |
| calcula sobre arreglos numéricos | vectoriza antes de repartir | bucle 0.141 s contra NumPy 0.0091 s | [[vectorizar]] |
| un servidor que atiende muchas conexiones | el modelo según qué cuesta cada conexión: hilos, event loop, prefork o híbrido | servidor de la clase: unos 30 hilos a 151/s con 0.2 s | esta página |
| toda llamada de red | timeout por llamada y deadline por petición | sin timeout, $W\to\infty$ y $L$ llega al tope | esta página |
| fallos transitorios | reintento con backoff y jitter, sólo si es idempotente | 3 capas × 3 intentos = 27 intentos | esta página |
| varias dependencias de distinta confiabilidad | un tope por dependencia y cola acotada con rechazo | una lenta agota un tope compartido | esta página |
| hace falta más capacidad | vertical primero; horizontal sólo sin estado en memoria | `ventas` en memoria: dos réplicas, dos verdades | esta página |

> [!NOTE]
> **Si sólo recuerdas una cosa:** mide dónde pasa el tiempo y qué recurso se agota primero; el modelo y los topes salen de $L=\lambda\cdot W$ en esa frontera, y toda espera lleva un timeout. La herramienta (hilos, `asyncio`, procesos, NumPy) es la consecuencia, no el punto de partida.

## Código

**Haz (celda 8.1):** calcula con Little lo que debió tardar el lote de 500 llamadas y cuántos hilos ocupa en el servidor.

```python
import math

k, W = 32, 0.2                  # tope en vuelo y segundos que tarda cada llamada
n, medido = 500, 3.32           # llamadas y segundos medidos (pon los tuyos)

lam_ideal = k / W               # Little con L = k: λ ≤ k / W
cota = math.ceil(n / k) * W     # ⌈n/k⌉ tandas de W segundos
lam_medido = n / medido         # peticiones terminadas por segundo
W_max = k / lam_medido          # L ≤ k, así que W = L / λ ≤ k / λ: una cota, no una medida

print(f"λ ideal  {lam_ideal:.0f}/s   cota  {cota:.2f} s")
print(f"λ medido {lam_medido:.0f}/s   W ≤ {W_max:.3f} s")
print(f"hilos del servidor: {lam_medido * W:.0f}; con W = 2 s: {lam_medido * 2:.0f}")
```

**Python que quizá no has visto.**

| Pieza | Qué es | Por qué hace falta aquí |
|---|---|---|
| `math.ceil` | redondea hacia arriba | 500 / 32 = 15.6 tandas son 16: la última tanda incompleta también tarda $W$ |
| `{x:.0f}`, `{x:.3f}` | formato con 0 o 3 decimales dentro de un f-string | separa la cifra útil del ruido de la división |

**Qué pasó.**

| Cantidad | Cuenta | Valor |
|---|---|---:|
| $\lambda$ ideal | $32/0.2$ | 160/s |
| cota | $\lceil500/32\rceil\times0.2=16\times0.2$ | 3.20 s |
| $\lambda$ medido | $500/3.32$ | 151/s |
| cota superior de $W$ | $32/151$ | 0.212 s |
| hilos del servidor | $151\times0.2$; con $W=2$: $151\times2$ | 30; 301 |

**Deberías ver** (con los 3.32 s de la corrida de referencia; con tu medición cambian las dos últimas líneas):

```text
λ ideal  160/s   cota  3.20 s
λ medido 151/s   W ≤ 0.212 s
hilos del servidor: 30; con W = 2 s: 301
```

- 0.212 s es un tope para $W$, no una medición: $L$ promedio es menor que 32 (la última tanda va incompleta), así que los 12 ms no son un sobrecosto medido por llamada.

**Haz (celda 8.2):** manda una `lambda` a un proceso.

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=2) as pool:
    futuro = pool.submit(lambda x: x * 2, 21)   # la función viaja serializada con pickle
    try:
        print(futuro.result())                  # relanza aquí el error del envío
    except Exception as e:
        print(f"{type(e).__name__} · {e}")
```

**Python que quizá no has visto.**

| Pieza | Qué es | Por qué hace falta aquí |
|---|---|---|
| `ProcessPoolExecutor(max_workers=2)` | un pool de 2 procesos hijo que se reutilizan | es el pool de las páginas 5 y 6; aquí sólo importa cómo le llega la función |
| `pool.submit(f, x)` | agenda `f(x)` en un hijo y regresa **de inmediato** un futuro | el envío (y su error) ocurre fuera de tu línea |
| `lambda x: x * 2` | una función sin nombre | `pickle` manda funciones **por nombre** (módulo + nombre): una `lambda` no tiene un nombre que el hijo pueda importar |
| `futuro.result()` | espera el resultado o relanza el error que ocurrió | sin esta línea el error pasaría en silencio |

**Qué pasó.**

| Paso | Dónde | Qué ocurre |
|---|---|---|
| 1 | padre | `submit` pone la llamada en la cola del pool y devuelve el futuro |
| 2 | padre | para cruzar al hijo, la llamada se serializa con `pickle` |
| 3 | padre | `pickle` busca la función como `__main__.<lambda>` y no la encuentra |
| 4 | padre | el error queda guardado en el futuro; ningún hijo ejecutó nada |
| 5 | padre | `result()` relanza el error y el `except` lo imprime |

**Deberías ver:**

```text
PicklingError · Can't pickle <function <lambda> at 0x77c41e5440f0>: it's not found as __main__.<lambda>
```

- La dirección `0x…` y la redacción del mensaje cambian entre corridas y versiones de Python; el tipo `PicklingError` es el mismo con cualquier método de arranque (`fork`, `spawn`, `forkserver`), porque el pool siempre serializa la función.
- **La función que va a un proceso vive en un módulo importable**, como `calcula` en `trabajo_computo.py`: así `pickle` la nombra y el hijo la encuentra.

La versión larga y paso a paso está en el notebook, tema 8.

## Al diseñar / al revisar código de IA, busca…

- **Un servidor o cliente sin ningún timeout.** `requests.get(url)` sin `timeout=` espera para siempre.
- **Reintentos en un bucle sin pausa, sin tope o sobre un `POST` sin `Idempotency-Key`.** Multiplican la carga y pueden duplicar efectos.
- **Un solo semáforo o pool compartido por varias dependencias.** Una lenta agota a las demás: un tope por dependencia.
- **Colas sin `maxsize`.** Sin tope no hay backpressure, sólo memoria y latencia creciendo.
- **Estado en un `dict` global en un servicio que «se va a escalar».** Dos réplicas, dos verdades.
- **`max_workers`, tamaño de pool o número de réplicas sin una cuenta.** Pide el $\lambda$ y el $W$ que los justifican, y el total de conexiones que suman contra la BD.
- **Cálculo dentro de `async def`, pools creados dentro del manejador, `for …: await …`, `lambda` a procesos.** Los anti-patrones de la tabla de arriba, con su señal.

Aquí termina la unidad. La siguiente clase es **patrones y protocolos de comunicación**: qué hacer cuando dos programas no esperan una respuesta inmediata, sino un evento.

Vuelve a [[computo-y-concurrencia]].
