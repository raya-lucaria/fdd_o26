---
id: asincrono-y-el-event-loop
title: "Asíncrono y el event loop"
nav_title: "Asíncrono y el event loop"
summary: "Asíncrono es un mecanismo: la llamada regresa antes del resultado y quien espera cede su hilo con await. El event loop reparte ese hilo tick a tick entre las tareas listas, duerme sin gastar CPU mientras todas esperan, y se detiene entero si una tarea no cede."
status: ready
estimated_time: 20m
tags: [asyncio, event-loop, corrutinas, await, create-task, gather, cooperativo, servidor]
prerequisites: [secuencial-concurrente-paralelo]
---

# Asíncrono y el event loop

**Página 3 de 8 · Cómputo y concurrencia** · Pregunta: **¿cómo espera tres (o tres mil) respuestas un solo hilo, quién decide a quién le toca, y qué pasa en cada vuelta del loop?** · Meta: seguir tick por tick una traza de `gather(A, B, C)`, distinguir una tarea **lista** de una que **espera**, y reconocer la línea que detiene al loop entero.

| Término | Definición de una línea | Símbolo |
|---|---|---|
| hilo de una tarea | el hilo del sistema operativo que la ejecuta | $\operatorname{hilo}(\tau)$ |
| llamada asíncrona | regresa antes del resultado; quien lo necesita hace `await` y cede su hilo | — |
| planificación cooperativa | la tarea que corre suelta el turno ella misma, en un `await` o al terminar | — |
| planificación preventiva | el sistema operativo (y el GIL cada 5 ms) le quita el turno al hilo | — |
| corrutina | lo que devuelve llamar una `async def`: un objeto que todavía no corre | — |
| `Task` | corrutina agendada en el loop: avanza aunque nadie la espere | — |
| event loop | el ciclo de un hilo que corre las tareas listas y duerme hasta que alguna espera se cumple | — |
| tick | una vuelta del loop: correr las listas, preguntar al sistema, despertar | — |
| cola de listas | las tareas que ya pueden avanzar y esperan turno en el hilo del loop | $\operatorname{ready}$ |

## En corto

- **Asíncrono describe el código; concurrente describe la traza.** `await` uno tras otro es asíncrono y secuencial (720 ms); `gather` es asíncrono y concurrente (280 ms).
- **El event loop es un ciclo de tres pasos**: correr cada tarea lista hasta que se suspende en un `await` o termina; preguntar al sistema qué esperas se cumplieron, durmiendo sólo si no hay listas; pasar a listas las que despertaron. Que la respuesta llegue no significa que la tarea corra: pasa a **lista** y espera turno.
- **La planificación es cooperativa**: nadie interrumpe a la tarea que corre. Un `time.sleep`, un `requests.get` o un cálculo largo dentro del loop dejan sin turno a todas las tareas que ya podían avanzar.

## Asíncrono: la llamada regresa antes del resultado

::: definition {#cmp-def-asincrono title="Llamada síncrona y llamada asíncrona"}
**En palabras.** Una llamada asíncrona regresa antes del resultado; quien lo necesita hace `await`, se suspende y cede su hilo para que corra otra tarea lista. Una síncrona retiene el hilo hasta el resultado. ([[notacion-computo]])

Sea $\operatorname{hilo}(\tau)$ el hilo del sistema operativo que ejecuta la tarea $\tau$. **Formalmente:**

- Una llamada es **síncrona** (bloqueante) si, mientras la operación está pendiente, $\operatorname{hilo}(\tau)$ queda bloqueado: ninguna otra tarea de ese hilo ejecuta.
- Una llamada es **asíncrona** si **regresa antes del resultado** con un pendiente (un futuro, una `Task`). Cuando $\tau$ necesita el resultado hace `await`: **se suspende y devuelve su hilo** al planificador (el event loop), que da el turno a otra tarea lista.

Asíncrono es un **mecanismo** del código, no una propiedad del Gantt.
:::

**Otro ángulo.** Asíncrono y concurrente contestan dos preguntas distintas, y las cuatro combinaciones existen:

::: figure {#cmp-matriz-asincrono title="Bloqueante o asíncrono, concurrente o no: cuatro celdas que existen"}
![Matriz de dos por dos. Las filas dicen cómo está escrito el código: bloqueante, con requests o time.sleep, o asíncrono, con async y await. Las columnas dicen si la traza es concurrente. Bloqueante y no concurrente es la versión secuencial, 720 ms; bloqueante y concurrente son los hilos, 280 ms; asíncrono y no concurrente es await uno tras otro, 720 ms; asíncrono y concurrente es gather en un hilo, 280 ms. Abajo: asíncrono describe el código, concurrente describe la traza](_assets/cmp-matriz-asincrono.svg)
:::

| | La traza **no** es concurrente | La traza **es** concurrente |
|---|---|---|
| **código bloqueante** | `for` con `requests.get`: 720 ms | hilos (`ThreadPoolExecutor`): 280 ms; el sistema reparte el turno |
| **código asíncrono** | `await` uno tras otro: 720 ms | `gather` en un hilo: 280 ms; quien espera cede con `await` |

- Escribir `async def` **no basta**: sin `gather` ni `create_task` no hay otra tarea a quien darle el hilo.
- Los hilos solapan esperas **sin** código asíncrono: cada hilo se bloquea, pero hay varios.

**Matemática.** Lo que sólo un mecanismo asíncrono permite es solapar esperas **dentro de un mismo hilo**:

$$\exists\, i\ne j:\quad \operatorname{hilo}(\tau_i)=\operatorname{hilo}(\tau_j)\ \ \text{y}\ \ \operatorname{dur}\big(\operatorname{wait}(\tau_i)\cap\operatorname{exec}(\tau_j)\big)>0$$

Si $\tau_i$ hubiera hecho una llamada síncrona, su hilo estaría bloqueado durante $\operatorname{wait}(\tau_i)$ y $\tau_j$, del mismo hilo, no podría ejecutar ahí. Con el ejemplo único (cada tarea ejecuta 20 ms, espera 200 ms, ejecuta 20 ms):

| Versión | $\operatorname{hilo}(\tau_1)=\operatorname{hilo}(\tau_2)$ | $\operatorname{wait}(\tau_1)\cap\operatorname{exec}(\tau_2)$ | Se cumple |
|---|---|---|---|
| `gather` | sí, un hilo | $[20,220)\cap[20,40)=[20,40)$, 20 ms | **sí**: $\tau_1$ cedió el hilo |
| `await` en serie | sí | $[20,220)\cap\big([240,260)\cup[460,480)\big)=\varnothing$ | no: asíncrono sin concurrencia |
| tres hilos | **no** | $[20,40)$, 20 ms | no: el solapamiento ocurre entre hilos distintos |

El Gantt de hilos y el de `gather` son idénticos; lo que los distingue es la fila de hilo.

**Ejemplo.** La celda 3.1 crea una `Task` que tarda 0.2 s y pregunta si ya terminó **justo después de crearla**: `False`. La llamada regresó antes del resultado; el resultado llega después de un `await`.

**Arquitectura.** Interfaz asíncrona o bloqueante en las bibliotecas de E/S:

| | Bloqueante | Asíncrona |
|---|---|---|
| HTTP | `requests` | `httpx.AsyncClient`, `aiohttp` |
| PostgreSQL | `psycopg2` | `asyncpg`, `psycopg` 3 en modo async |
| esperar | `time.sleep` | `asyncio.sleep` |

- **Cuándo sí:** muchas esperas independientes (cientos o miles) en un proceso; servidores con muchas conexiones abiertas.
- **Cuándo no:** pocas llamadas (una serie o unos hilos bastan); el tiempo está en calcular, no en esperar; la biblioteca que necesitas sólo existe bloqueante.
- **Qué cuesta:** una función que hace `await` tiene que ser `async def`, y quien la llama también, hasta el loop; mezclar una biblioteca bloqueante dentro de ese código lo rompe (sección `time.sleep` abajo).
- **Sistema real:** `httpx` ofrece las dos interfaces con la misma API (`Client` y `AsyncClient`); FastAPI acepta manejadores `def` y `async def`, y corre los `def` fuera del loop.

## Cooperativo contra preventivo

::: definition {#cmp-def-cooperativo title="Planificación cooperativa y preventiva"}
**En palabras.** En la planificación cooperativa la tarea que corre suelta el hilo ella misma, en un `await` que suspende o al terminar; en la preventiva el sistema operativo le quita el turno (y en CPython el GIL le pide soltar el intérprete). ([[notacion-computo]])

- **Cooperativa** (event loop): la tarea que ejecuta suelta el hilo **ella misma**, en un `await` que suspende o al terminar. Nadie la interrumpe.
- **Preventiva** (hilos, procesos): el sistema operativo le quita la CPU al hilo cuando decide; en CPython, además, el GIL obliga a ceder el intérprete cada `sys.getswitchinterval()` segundos (5 ms por omisión).
:::

**Otro ángulo.**

| | Cooperativa | Preventiva |
|---|---|---|
| quién saca a la tarea de `exec` | la propia tarea, en un `await` | el sistema operativo; el GIL cada 5 ms |
| dónde puede cambiar el turno | sólo en los `await` visibles en el código | en cualquier instrucción |
| una tarea que calcula 2 s sin `await` | todas las demás quedan listas 2 s | las demás reciben turnos de unos 5 ms |
| una respuesta que llega | pasa a su tarea a **lista**; no interrumpe a la que corre | despierta al hilo; el sistema lo agenda |
| condiciones de carrera | sólo entre dos `await` de distintas tareas | entre cualesquiera dos instrucciones |

**Matemática.** En el loop, mientras $\tau_k$ ejecuta un tramo de $e_k$ sin `await`, toda tarea $\tau_j$ que ya podía avanzar acumula ese tramo como $\operatorname{ready}$:

$$r_j\ \ge\ e_k\qquad\text{para toda } \tau_j \text{ lista mientras corre el tramo de } \tau_k$$

Con hilos y GIL, el tramo sin ceder el intérprete ronda los 5 ms, sea cual sea $e_k$; el intervalo es orientativo y una función interna larga en C puede excederlo.

**Ejemplo.** En la traza de abajo, en el tick 1 A y B ejecutan 10 ms cada una sin `await`; C, lista desde $t=0$, no corre hasta 20 ms: $r_C=10+10=20$ ms. Si B calculara 2 s en lugar de 10 ms, $r_C$ sería 2010 ms: el loop no tiene manera de quitarle el turno.

**Arquitectura.**

- **Cuándo cooperativa:** el trabajo es casi todo espera y los tramos de ejecución son cortos (micro o milisegundos). A cambio, los cambios de turno son baratos y visibles en el código.
- **Cuándo preventiva:** hay tramos largos de cálculo, o bibliotecas que bloquean y no se pueden cambiar. El sistema garantiza turnos aunque el código no coopere.
- **Qué cuesta la cooperativa:** una sola tarea mal escrita degrada a todas las del loop; no hay aislamiento.
- **Sistema real:** el event loop de `asyncio`, Node.js y nginx son cooperativos; los hilos de `ThreadingHTTPServer` (el servidor de la clase, ver [[secuencial-concurrente-paralelo]]) son preventivos.

## Corrutina y `Task`

::: definition {#cmp-def-corrutina-task title="Corrutina y Task"}
- Llamar una función `async def` **no ejecuta nada**: devuelve una **corrutina**, un objeto que corre sólo cuando alguien la agenda (`create_task`, `gather`) o la espera con `await`.
- Una **`Task`** es una corrutina agendada en el loop: entra a la cola de listas y avanza en cuanto el hilo queda libre, **aunque nadie la espere**.
- `await x` suspende a quien lo escribe **sólo si `x` está pendiente**. Esperar algo que ya terminó, o una corrutina que llega a su `return` sin encontrar ninguna espera pendiente, no cede el hilo.
:::

**Otro ángulo.** La misma `f()`, cuatro maneras de usarla:

| Código | Qué pasa con `f` | ¿Hay concurrencia? |
|---|---|---|
| `c = f()` | se crea el objeto; **nunca corre** (al final Python avisa «coroutine was never awaited») | no |
| `await f()` | corre ahora, dentro de quien la espera, hasta terminar | no: quien espera no avanza |
| `t = asyncio.create_task(f())` | entra a la cola de listas; corre cuando quien la creó cede el hilo | sí, si quien la creó tiene otra cosa que hacer |
| `await asyncio.gather(f(), g())` | envuelve cada una en una `Task` y espera a todas | sí: programa varias y espera todas (el detalle, en [[concurrencia-acotada]]) |

::: figure {#cmp-create-task title="create_task agenda la corrutina; llamarla sola no la corre"}
![Dos Gantt de un hilo, de 0 a 140 ms. En los dos, main ejecuta de 0 a 20 ms, crea f a los 10 ms, cede el hilo con await asyncio.sleep de 20 a 120 ms y ejecuta de 120 a 130. Arriba, c igual a f sin create_task: la corrutina queda inerte y nunca corre. Abajo, con create_task, f queda lista de 10 a 20 ms, ejecuta de 20 a 30, espera 50 ms y ejecuta de 80 a 90, aunque main nunca hace await sobre ella](_assets/cmp-create-task.svg)
:::

**Ejemplo.** En la figura, `create_task(f())` ocurre a los 10 ms, pero `f` no corre hasta los 20: main todavía tiene el hilo. $\operatorname{ready}(f)=[10,20)$. A los 20 ms main cede con `await asyncio.sleep(0.1)` y el loop le da el turno a `f`. Con `c = f()`, en cambio, el hilo queda ocioso de 20 a 120 ms: no había otra tarea agendada.

**Arquitectura.** Tareas en segundo plano.

- **Qué es:** `create_task` para lanzar trabajo que avanza mientras la tarea principal sigue (registrar una métrica, precargar un dato).
- **Cuándo sí:** el trabajo es independiente y su resultado se recoge más tarde con `await t`.
- **Cuándo no:** «lanzar y olvidar» sin guardar la `Task`. El loop sólo guarda una referencia débil: una tarea sin referencia puede desaparecer a medio camino, y una excepción en ella sólo aparece como aviso («Task exception was never retrieved»).
- **Qué cuesta:** cada `Task` es un objeto de unos KB en memoria, sin hilo propio; miles son baratas.
- **Sistema real:** `asyncio.TaskGroup` (Python 3.11+) agrupa tareas, espera a todas y cancela las demás si una falla.

## El event loop, tick a tick

::: definition {#cmp-def-event-loop title="Event loop y tick"}
El **event loop** es un ciclo que corre en **un** hilo y guarda tres cosas: la **cola de listas**, las **esperas pendientes** (sockets, temporizadores, cada una con la tarea que la espera) y los vencimientos de los temporizadores. Cada vuelta del ciclo es un **tick**:

1. **Correr.** Saca de la cola de listas todas las tareas que hay al abrir el tick y corre cada una, una tras otra, hasta su siguiente `await` que suspende o hasta su fin.
2. **Preguntar.** Pide al sistema operativo qué esperas ya se cumplieron (`select`, `epoll`), durmiendo a lo más hasta el **temporizador más próximo**. Si la cola de listas no está vacía, pregunta sin dormir.
3. **Despertar.** Pasa a la cola de listas las tareas cuyas esperas se cumplieron. Correrán en el paso 1 del tick siguiente.
:::

**Otro ángulo.** El mismo ciclo, en pseudocódigo:

```text
mientras queden tareas:
    1. listas = todas las de la cola de listas            ← las que llegan durante el paso 1 esperan al tick siguiente
       para cada tarea en listas: córrela hasta su próximo await o su fin
    2. timeout = 0 si la cola de listas no está vacía; si no, max(0, vencimiento más próximo − ahora); sin temporizadores, sin límite
       cumplidas = sistema_operativo.select(esperas_pendientes, timeout)   ← aquí el hilo duerme
    3. para cada espera cumplida: su tarea → cola de listas
```

`asyncio` lo hace en un método (`_run_once`) que empieza por el paso 2: es el mismo ciclo, contado desde otro punto.

Los estados de una tarea (los de [[donde-pasa-el-tiempo]]), leídos dentro del loop:

| Estado | Dónde está la tarea | Qué la mueve al siguiente |
|---|---|---|
| nueva | corrutina creada, todavía sin agendar | `create_task` o `gather` la pone en la cola de listas |
| lista | en la cola de listas | el paso 1 del siguiente tick la corre |
| ejecutando | en el hilo del loop; sólo una a la vez | llega a un `await` que suspende (→ esperando) o a su `return` (→ terminada) |
| esperando | registrada con su socket o su temporizador | el paso 2 ve la espera cumplida; el paso 3 la pasa a lista |
| terminada | su resultado queda guardado en la `Task` | quien hacía `await` sobre ella pasa a lista |

**Sin espera activa.** En el paso 2 el hilo **duerme dentro del sistema operativo**: no gasta CPU revisando una y otra vez si ya llegó algo. El kernel lo despierta cuando un socket tiene datos o vence el `timeout`. Por eso un loop con mil conexiones ociosas usa casi 0 % de CPU.

**Matemática.** En el paso 2, con $t$ el instante actual y $\operatorname{vence}_j$ el vencimiento de cada temporizador pendiente:

$$\text{timeout}=\max\big(0,\ \min_j \operatorname{vence}_j - t\big)\qquad\text{si la cola de listas está vacía}$$

y $\text{timeout}=0$ si no lo está: hay trabajo pendiente y no se duerme. Sin temporizadores ni listas, duerme sin límite hasta que un socket tenga datos.

En la traza de abajo, al cerrar el tick 1 ($t=30$ ms) vencen A en 310, B en 120 y C en 230: $\text{timeout}=\min(310,120,230)-30=90$ ms.

**Ejemplo (traza ilustrativa).** `gather(A, B, C)`: cada tarea ejecuta 10 ms, hace `await asyncio.sleep(d)` y ejecuta 10 ms, con $d_A=0.3$ s, $d_B=0.1$ s, $d_C=0.2$ s. Un hilo, tiempos en ms; el vencimiento de cada `sleep` es el instante en que lo pidió más $d$.

| tick | t (ms) | ejecutando (en el único hilo) | listas **al abrir** el tick | esperando o bloqueadas **al cerrar** (vence) | qué pasó |
|---:|---|---|---|---|---|
| 0 | 0 | main | main | main (bloqueada) | main llama `gather`: crea tres `Task` (nuevas → listas) y hace `await`; main queda bloqueada: espera a otras tareas del programa |
| 1 | 0–30 | A → B → C | A, B, C | A (310), B (120), C (230), main (bloqueada) | A corre $[0,10)$ y pide `sleep(0.3)`: vence $10+300=310$; B corre $[10,20)$, vence 120; C corre $[20,30)$, vence 230 |
| 1 (pasos 2–3) | 30–120 | nadie | — | A, B, C, main | timeout $=120-30=90$ ms: el hilo duerme en `select`, CPU libre |
| 2 | 120–130 | B | B | A (310), C (230), main (bloqueada) | vence B → lista → corre sus 10 ms y termina; `gather` guarda su resultado |
| 2 (pasos 2–3) | 130–230 | nadie | — | A, C, main | timeout $=230-130=100$ ms |
| 3 | 230–240 | C | C | A (310), main (bloqueada) | vence C → lista → corre y termina |
| 3 (pasos 2–3) | 240–310 | nadie | — | A, main | timeout $=310-240=70$ ms |
| 4 | 310–320 | A | A | main pasa a lista | vence A → lista → corre y termina; `gather` completo: main pasa a lista |
| 5 | 320 | main | main | — | main recibe `['A', 'B', 'C']`: el orden de los argumentos, no el de llegada (B, C, A) |

Cómo leer la tabla: cada tick abre con el paso 1 y cierra con los pasos 2 y 3. La columna de listas se lee **antes** de correr el tick; la de esperando, **después**. Las filas «pasos 2–3» son el sueño en `select` y el despertar con que cierra el tick de arriba. Todo corre en un solo hilo: B queda lista de 0 a 10 ms porque el hilo lo tiene A, y C de 0 a 20 porque lo tienen A y luego B; en 120 B corre en cuanto vence porque el hilo está libre.

::: figure {#cmp-event-loop-ticks title="El event loop, tick por tick: quién corre, quién está lista, quién espera"}
![Traza del event loop de gather con tres tareas A, B y C, cada una ejecuta 10 ms, duerme con await asyncio.sleep y ejecuta 10 ms; A duerme 300 ms, B 100 y C 200. Una columna por tick y tres carriles: ejecutando, cola de listas y esperando con su vencimiento. En el tick 1 corren A, B y C hasta su sleep; de 30 a 120 ms el loop duerme en select con la CPU libre; en el tick 2 corre y termina B, en el 3 C, en el 4 A; en el tick 5, a los 320 ms, main recibe los resultados en el orden de los argumentos. Abajo, la fila de CPU en tiempo real](_assets/cmp-event-loop-ticks.svg)
:::

Las cuentas de la traza, con $\operatorname{start}=0$ para las tres (las crea el tick 0):

| Tarea | $\operatorname{exec}$ | $\operatorname{wait}$ | $\operatorname{ready}$ | $d=e+w+r$ |
|---|---|---|---|---|
| A | $[0,10)\cup[310,320)$ | $[10,310)$ | $\varnothing$ | $20+300+0=320$ |
| B | $[10,20)\cup[120,130)$ | $[20,120)$ | $[0,10)$ | $20+100+10=130$ |
| C | $[20,30)\cup[230,240)$ | $[30,230)$ | $[0,20)$ | $20+200+20=240$ |

- $T=320$ ms; $C=60$ ms de CPU; $U=60/320\approx18.8\,\%$. Las esperas suman $300+100+200=600$ ms y el lote dura 320: se solaparon.
- En secuencia serían $320+120+220=660$ ms, la suma de las vidas de cada tarea sola. Es justo lo que da la celda 3.5.
- main no ejecuta mientras espera a `gather`: espera a otras tareas del mismo programa, así que está `blocked` (definición en [[notacion-computo]]).

**Respuesta disponible no es tarea reanudada.** Que llegue la respuesta (o venza el temporizador) es un evento del sistema; reanudar la tarea es que el loop le dé el hilo. Lo primero la mueve de **esperando** a **lista**; lo segundo ocurre en el paso 1 de un tick posterior. En la traza el loop estaba ocioso y las dos cosas coincidieron, pero no tienen por qué:

| Variante (cifras supuestas) | A vence | A corre | $\operatorname{ready}(A)$ |
|---|---:|---:|---|
| la traza de arriba | 310 | 310 | $\varnothing$ |
| C, al reanudarse en 230, calcula 100 ms en lugar de 10 | 310 | 330 | $[310,330)$: lista sin turno |

En `asyncio` el paso 3 es literal: el temporizador vencido completa el futuro de `sleep`, y eso agenda el siguiente paso de la tarea en la cola de listas (`call_soon`). La tarea corre en la vuelta siguiente.

**Arquitectura.** El paso 2 es lo que hace posible un servidor de un hilo.

- **Qué es:** el selector del sistema operativo, `epoll` en Linux, `kqueue` en macOS y BSD; recibe miles de sockets y devuelve los que tienen datos, en una llamada.
- **Cuándo sí:** muchas esperas abiertas a la vez (conexiones, temporizadores) y tramos de ejecución cortos.
- **Cuándo no:** cuando el tick se alarga. Todo lo que corre en el paso 1 retrasa el paso 2 y, con él, a todas las tareas que ya tienen su respuesta.
- **Qué cuesta:** un solo hilo, así que **una CPU por loop**; el GIL no cambia nada aquí, el loop ejecuta una tarea a la vez con o sin él.
- **Sistema real:** `uvloop` sustituye el loop de `asyncio` por uno escrito sobre `libuv`, la misma biblioteca del loop de Node.js; Uvicorn lo usa si está instalado.

## Solapar esperas en un hilo: `gather` contra `await` en serie

::: definition {#cmp-def-await-en-serie title="await en serie"}
Un **`await` en serie** es un `await` dentro de un `for` (o varios `await` seguidos) sobre llamadas **independientes**: cada vuelta espera su resultado antes de lanzar la siguiente. El código es asíncrono, la traza es secuencial. El arreglo es agendar todas antes de esperar: `gather`.
:::

**Otro ángulo.** El ejemplo único (cada tarea ejecuta 20 ms, espera 200 ms la red, ejecuta 20 ms), en un hilo, de las dos maneras:

::: figure {#cmp-gantt-asyncio title="asyncio con gather: un hilo, cada await cede el turno"}
![Diagrama de Gantt de 0 a 800 ms: las mismas tres tareas como corrutinas en un solo hilo, lanzadas juntas con gather. Cada una ejecuta 20 ms hasta su await y cede el hilo; la siguiente, que estaba lista en rayado, corre entonces. Las tres esperas de 200 ms se solapan y la fila de CPU muestra tramos cortos intercalados. Total 280 ms, igual que con hilos, sin ningún hilo extra](_assets/cmp-gantt-asyncio.svg)
:::

::: figure {#cmp-gantt-await-en-serie title="await uno tras otro: async en el código, secuencial en el reloj"}
![Diagrama de Gantt de 0 a 800 ms: tres corrutinas con await una tras otra, sin gather. Cada await espera su respuesta completa de 200 ms antes de lanzar la siguiente llamada, así que el dibujo es idéntico al secuencial: total 720 ms y la CPU ociosa durante las tres esperas](_assets/cmp-gantt-await-en-serie.svg)
:::

El mismo `gather` como texto (E ejecuta, W espera, R lista, — terminada):

| | 0–20 | 20–40 | 40–60 | 60–220 | 220–240 | 240–260 | 260–280 |
|---|---|---|---|---|---|---|---|
| τ1 | E | W | W | W | E | — | — |
| τ2 | R | E | W | W | W | E | — |
| τ3 | R | R | E | W | W | W | E |
| hilo del loop | τ1 | τ2 | τ3 | duerme en `select` | τ1 | τ2 | τ3 |

**Matemática.**

| Magnitud | `await` en serie | `gather` |
|---|---|---|
| $T$ | $3\times240=720$ ms | 280 ms |
| $C=\sum e_i$ | 120 ms | 120 ms |
| $U=C/T$ | $16.7\,\%$ | $42.9\,\%$ |
| $r=(r_1,r_2,r_3)$ | $(0,0,0)$ | $(0,20,40)$ |
| latencias | 240, 480, 720 | 240, 260, 280 |
| speedup sobre la serie | 1 | $720/280\approx2.57$ |

$C$ es el mismo: el loop no ejecuta menos, **deja de estar ocioso** durante las esperas. Con `gather` aparecen tramos de `ready` (τ3 espera 40 ms su primer turno) y aun así todas terminan antes.

**Ejemplo (medición real).** La celda 3.4 hace 20 llamadas con `?lento=0.2` y `await` en serie: tarda lo mismo que las 20 llamadas con `requests` de la celda 1.2 (4.04 s, medición de referencia). Con `gather`, las mismas 20 tardan 0.24 s (la medición es de [[concurrencia-acotada]], con un tope de 32 que con 20 llamadas no actúa).

**Arquitectura.** Un endpoint que consulta varias fuentes.

- **Qué es:** el manejador lanza las llamadas independientes con `gather` y espera a todas; el tiempo lo pone la más lenta, no la suma.
- **Cuándo sí:** las llamadas no dependen una de otra (perfil, pedidos y recomendaciones de un mismo usuario).
- **Cuándo no:** la segunda necesita el resultado de la primera (un token, un id): ahí el `await` en serie es correcto.
- **Qué cuesta:** lanzar todas a la vez puede saturar a quien las recibe; el tope se ve en [[concurrencia-acotada]].
- **Sistema real:** el patrón se llama *scatter-gather*: un agregador consulta $n$ servicios y junta las respuestas.

## `time.sleep` contra `asyncio.sleep`: el loop bloqueado

::: definition {#cmp-def-llamada-bloqueante title="Llamada bloqueante dentro del loop"}
Una **llamada bloqueante dentro del loop** es una llamada síncrona (`time.sleep`, `requests.get`, un cálculo largo sin `await`) escrita dentro de una `async def`. La tarea que la hace se queda con el hilo del loop hasta que termina: el loop no vuelve al paso 2, nadie despierta, y **todas las demás tareas, aunque su respuesta ya haya llegado, quedan listas sin turno**.
:::

**Otro ángulo.**

| Dentro de `async def` | Qué hace con el hilo del loop | Para las demás tareas |
|---|---|---|
| `await asyncio.sleep(1)` | lo suelta; registra un temporizador | corren |
| `time.sleep(1)` | se lo queda 1 s, dormido | listas sin turno 1 s |
| `await cliente.get(url)` (`httpx.AsyncClient`) | lo suelta mientras llega la respuesta | corren |
| `requests.get(url)` | se lo queda hasta la respuesta | listas sin turno |
| un bucle de cálculo de 2 s | se lo queda 2 s, ejecutando | listas sin turno 2 s |

Para la tarea que llama `time.sleep`, ese tramo es `wait`: espera un temporizador. Para el loop es un tramo en el que el hilo no está disponible, y eso es lo que significa una llamada síncrona.

**Matemática.** La variante del ejemplo único (traza ilustrativa): $\tau_3$ se cambia por un cálculo de 2000 ms sin ningún `await`; $\tau_1$ y $\tau_2$ siguen iguales, en el mismo loop.

| Tarea | $\operatorname{exec}$ | $\operatorname{wait}$ | $\operatorname{ready}$ | $d$ |
|---|---|---|---|---|
| $\tau_1$ | $[0,20)\cup[2040,2060)$ | $[20,220)$ | $[220,2040)$ | $40+200+1820=2060$ |
| $\tau_2$ | $[20,40)\cup[2060,2080)$ | $[40,240)$ | $[0,20)\cup[240,2060)$ | $40+200+1840=2080$ |
| $\tau_3$ | $[40,2040)$ | $\varnothing$ | $[0,40)$ | $2000+0+40=2040$ |

- Las respuestas de $\tau_1$ y $\tau_2$ llegan a los 220 y 240 ms; sus tareas pasan a **lista** y se quedan ahí 1820 ms. Respuesta disponible, tarea sin reanudar.
- $C=40+40+2000=2080=T$: $U=100\,\%$. La CPU nunca estuvo ociosa y aun así las dos peticiones tardaron 2060 y 2080 ms en lugar de 240 y 260. Utilización alta no significa buen servicio.

**Ejemplo (traza ilustrativa).** Las tres tareas de la traza por ticks, con `time.sleep(d)` en lugar de `await asyncio.sleep(d)` (celda 3.5): A ocupa el hilo $[0,320)$, B $[320,440)$, C $[440,660)$. Todo ocurre en **un solo tick**, porque nadie regresa al loop. Total 660 ms contra 320: la suma de lo que dura cada tarea sola ($320+120+220$). Las vidas empiezan las tres en 0 y duran 320, 440 y 660 ms: la traza sigue siendo concurrente, pero no solapa ninguna espera.

**Arquitectura.** «Async de punta a punta».

- **Qué es:** dentro del loop, toda E/S pasa por bibliotecas asíncronas, y nada calcula más de unos milisegundos sin `await`.
- **Cuándo sí:** siempre que haya un loop atendiendo a otras tareas (un servidor, un cliente con cientos de llamadas).
- **Cuándo no aplica:** un script que hace una sola cosa y no tiene a nadie más en el loop; ahí bloquear no le cuesta a nadie.
- **Qué cuesta:** revisar cada dependencia. Una sola llamada bloqueante escondida en una biblioteca anula el modelo.
- **Sistema real:** el modo de depuración de `asyncio` (`PYTHONASYNCIODEBUG=1`) registra cada paso de una tarea que retuvo el hilo más de `loop.slow_callback_duration` (0.1 s por omisión). Cómo sacar del loop un cálculo o una biblioteca bloqueante es el tema de [[calcular-en-paralelo]].

## El servidor con event loop

::: definition {#cmp-def-servidor-event-loop title="Servidor con event loop"}
Un **servidor con event loop** atiende **todas** sus conexiones en un hilo: cada petición es una tarea del loop, que cede el hilo en cada espera (leer del socket, consultar la base de datos, llamar a otra API). Las conexiones abiertas son esperas registradas en el selector, no hilos.
:::

**Otro ángulo.**

```text
clientes ──► socket ──► selector (epoll): miles de conexiones, cada una con su tarea
                             │ paso 2: ¿cuáles tienen datos?
                             ▼
                    cola de listas ──► paso 1: el único hilo corre cada manejador hasta su await
                             ▲                         │
                             └──── paso 3 ◄────────────┘  (await BD, await API: la conexión vuelve al selector)
```

| | Hilo por conexión (página 2) | Event loop |
|---|---|---|
| qué ocupa una conexión abierta | un hilo con su pila | una tarea, unos KB |
| quién decide el turno | el sistema operativo | los `await` del código |
| una conexión que calcula 50 ms | frena su hilo; las demás siguen | frena a **todas** |
| bibliotecas | cualquiera | sólo asíncronas dentro del manejador |
| CPU por proceso | una para Python (el GIL); más sólo con código nativo que lo suelta | una por loop |

**Matemática (cifras supuestas, rotuladas).** Llegan $\lambda=1000$ peticiones/s; cada una pasa $W=0.2$ s en el servidor, casi todo esperando a la base de datos, y ejecuta $e=0.2$ ms de CPU.

| Pregunta | Cuenta | Resultado |
|---|---|---|
| conexiones en vuelo (Little) | $L=\lambda W=1000\times0.2$ | 200, todas en un hilo |
| CPU que usa el loop | $\lambda e=1000\times0.0002$ | 0.2 s por segundo: 20 % de una CPU |
| techo de un loop | $\lambda\le1/e=1/0.0002$ | 5000 peticiones/s, sin importar $W$ |
| un manejador calcula 50 ms | cada uno retiene el hilo 50 ms | toda conexión cuya respuesta llegue en esos 50 ms queda lista sin turno hasta que el manejador suelte el hilo; techo $\lambda\le1/0.05=20$/s |

Con hilo por conexión, las mismas 200 conexiones serían 200 hilos. Con un loop, la capacidad la decide la CPU por petición, no la espera.

**Arquitectura.**

- **Qué es:** un proceso, un hilo, un loop; las conexiones son tareas.
- **Cuándo sí:** miles de conexiones que casi sólo esperan: APIs que llaman a otras APIs, proxies, WebSocket, *streaming*.
- **Cuándo no:** manejadores que calculan (inferencia de un modelo, transformar un DataFrame grande) o que dependen de bibliotecas bloqueantes. El cálculo sale del loop a otro proceso: [[calcular-en-paralelo]].
- **Qué cuesta:** una CPU por loop; una llamada bloqueante congela todas las conexiones; el código entero tiene que ser `async`.
- **Un loop por worker:** para usar las $P$ CPU, se arrancan varios procesos, cada uno con su loop. nginx lo hace con `worker_processes auto` (un proceso por CPU); en Python, Gunicorn con workers `UvicornWorker`.
- **Sistemas reales:** nginx, Node.js (un loop; un pool de 4 hilos de `libuv` por omisión para lo que no tiene interfaz asíncrona), Redis (ejecuta los comandos en un hilo), Uvicorn sobre `asyncio` o `uvloop`. Los tres modelos de servidor, lado a lado, están en [[arquitectura-y-estrategia]].

## La decisión hasta aquí

| Pregunta | Respuesta | Evidencia |
|---|---|---|
| ¿Dónde está el tiempo de mi tarea? | medir $\rho$ con la tarea sola | `perf_counter` contra `process_time` (celda 1.1) |
| ¿Qué pasa si no hago nada? | las esperas se suman: $T=\sum d_i$ | 20 llamadas en serie, 4.04 s (celda 1.2) |
| ¿Cuántas peticiones por segundo da un servidor secuencial? | $\lambda\le1/W$ | $W=0.2$ s da 5/s |
| ¿Esperas independientes con una biblioteca bloqueante? | hilos: el sistema solapa las esperas entre hilos | 20 llamadas con 32 hilos, 0.23 s |
| ¿Cálculo de Python repartido entre CPU? | procesos, no hilos: el GIL | página 2; la medida, en la página 6 |
| ¿Muchas esperas independientes en un solo hilo? | `asyncio`: `gather` o `create_task`, con bibliotecas asíncronas | 3 tareas: 280 ms contra 720 |
| ¿Basta con escribir `async def` y `await`? | no: `await` en serie es secuencial | celda 3.4, el mismo tiempo que la celda 1.2 |
| ¿Puedo llamar `time.sleep`, `requests` o calcular dentro de `async def`? | no: bloquea el loop y deja a todas las tareas listas sin turno | celda 3.5: un solo tick, 660 ms contra 320 |
| ¿Servidor para miles de conexiones que casi sólo esperan? | event loop, un loop por CPU; el cálculo, fuera del loop | Little: 200 conexiones en un hilo al 20 % de CPU (cifras supuestas) |

## Código

Cinco celdas en el notebook, con `await` de nivel superior: una `Task` que regresa antes del resultado, un contador de ticks, la traza A/B/C, el `await` en serie contra el servidor de la clase y la misma traza con `time.sleep`.

> [!WARNING]
> En un notebook usa `await` suelto, como en estas celdas: el notebook ya tiene un loop corriendo. `asyncio.run(...)` sólo va en un archivo `.py`; dentro de una celda truena con `RuntimeError: asyncio.run() cannot be called from a running event loop`.

**Haz (celda 3.1):** llama una corrutina sin agendarla, y luego créala como `Task` y pregunta si terminó antes y después de esperarla.

```python
# celda 3.1
import asyncio

async def cuenta():                        # corrutina: puede suspenderse en un await
    await asyncio.sleep(0.2)               # espera 0.2 s cediendo el hilo al loop
    return 42

c = cuenta()                               # sólo crea el objeto: no corre nada
print("llamarla devuelve:", type(c).__name__)
c.close()                                  # se descarta sin correrla (evita el aviso)
tarea = asyncio.create_task(cuenta())      # la agenda en la cola de listas y regresa
print("justo después de crearla, terminó:", tarea.done())
resultado = await tarea                    # main cede el hilo hasta que la tarea termina
print("después de await, terminó:", tarea.done(), "y devolvió", resultado)
```

**Python que quizá no has visto**

| Construcción | Qué es | Por qué hace falta aquí |
|---|---|---|
| `async def` | define una función que, al llamarla, devuelve una corrutina en lugar de correr | es lo que se puede suspender en un `await` |
| `await x` | pide el resultado de `x`; si está pendiente, suspende a quien lo escribe y cede el hilo | sin él, main nunca suelta el hilo y `cuenta` no avanza |
| `asyncio.create_task(c)` | envuelve la corrutina en una `Task` y la pone en la cola de listas | es lo que la hace correr sin que nadie la espere todavía |
| `tarea.done()` | dice si la `Task` ya terminó | prueba que la llamada regresó antes del resultado |
| `c.close()` | cierra una corrutina que nunca corrió | sin él, Python avisa «coroutine was never awaited» |

**Qué pasó:**

| Línea | Estado de `cuenta` | Hilo del loop |
|---|---|---|
| `c = cuenta()` | nueva, nunca agendada | main |
| `create_task(...)` | lista | main (todavía no cede) |
| `await tarea` | ejecuta hasta `sleep`, espera 0.2 s, ejecuta y termina | main cede; durante la espera, el loop duerme en `select` |

**Deberías ver:**

```text
llamarla devuelve: coroutine
justo después de crearla, terminó: False
después de await, terminó: True y devolvió 42
```

**Haz (celda 3.2):** define `marca`, que imprime cada evento con el número de tick en que ocurre.

```python
# celda 3.2
import asyncio, time
loop = asyncio.get_running_loop()          # el loop que corre las celdas

def abre_tick():                           # corre al principio del tick siguiente
    global en_tick
    en_tick = False

def marca(texto):                          # imprime: tick, ms desde t0, texto
    global tick, en_tick
    if not en_tick:                        # primera línea de este tick: le toca número nuevo
        tick, en_tick = tick + 1, True
        loop.call_soon(abre_tick)          # call_soon: entra a la cola del tick siguiente
    print(f"tick {tick}  {(loop.time() - t0) * 1000:4.0f} ms  {texto}")
```

**Python que quizá no has visto**

| Construcción | Qué es | Por qué hace falta aquí |
|---|---|---|
| `asyncio.get_running_loop()` | el event loop que está corriendo este código | para pedirle la hora y agendarle una función |
| `loop.call_soon(f)` | pone `f` en la cola de listas; corre en el paso 1 del tick **siguiente** | marca el fin del tick actual: todo lo impreso antes de que corra `abre_tick` es del mismo tick |
| `loop.time()` | el reloj del loop, en segundos | es el reloj con el que el loop calcula los vencimientos |
| `global` | la función modifica una variable de la celda, no una local | `tick` y `en_tick` sobreviven entre llamadas |

**Qué pasó:** sólo se definieron dos funciones; `t0`, `tick` y `en_tick` los fija la celda 3.3. El contador numera **sólo las vueltas del loop en las que alguien imprime**: el loop da otras vueltas internas (correr un temporizador, avisar a `gather`) que no aparecen.

**Deberías ver:** nada; la celda no imprime.

**Haz (celda 3.3):** la traza de `gather(A, B, C)` con $d_A=0.3$, $d_B=0.1$, $d_C=0.2$ s.

```python
# celda 3.3
async def tarea(nombre, d):
    marca(f"{nombre} ejecuta 10 ms y hace await sleep({d})")
    time.sleep(0.01)                       # 10 ms con el hilo ocupado, sin ceder
    await asyncio.sleep(d)                 # cede el hilo; su temporizador vence en d s
    marca(f"{nombre} se reanuda, ejecuta 10 ms y termina")
    time.sleep(0.01)
    return nombre

t0, tick, en_tick = loop.time(), -1, False # reinicia el reloj y el contador
marca("main: gather crea A, B y C y hace await")
resultado = await asyncio.gather(tarea("A", 0.3), tarea("B", 0.1), tarea("C", 0.2))
marca(f"main recibe {resultado}")
```

**Python que quizá no has visto**

| Construcción | Qué es | Por qué hace falta aquí |
|---|---|---|
| `await asyncio.sleep(d)` | una espera que registra un temporizador en el loop y cede el hilo | es la espera que el loop puede solapar |
| `asyncio.gather(a, b, c)` | crea una `Task` por corrutina y espera a todas; devuelve los resultados en el orden de los argumentos | programa las tres antes de esperar |
| `time.sleep(0.01)` | retiene el hilo 10 ms | simula retener el hilo, no calcular: la tarea está en `wait`, no en `exec`; para las demás el efecto es el mismo, no les toca turno |
| `await` fuera de una función | el notebook acepta `await` de nivel superior | por eso no hace falta `asyncio.run` |

**Qué pasó:** cada línea impresa cae en un tick de la tabla de la sección del event loop.

| tick | ms | quién imprime | las demás |
|---:|---:|---|---|
| 0 | 0 | main | A, B, C listas |
| 1 | 0, 10, 20 | A, B, C, una tras otra | al terminar el tick, las tres esperando |
| 2 | 120 | B | A y C esperando; el loop durmió 90 ms antes |
| 3 | 230 | C | A esperando |
| 4 | 310 | A | — |
| 5 | 320 | main | `gather` devuelve `['A', 'B', 'C']` |

**Deberías ver:**

```text
tick 0     0 ms  main: gather crea A, B y C y hace await
tick 1     0 ms  A ejecuta 10 ms y hace await sleep(0.3)
tick 1    10 ms  B ejecuta 10 ms y hace await sleep(0.1)
tick 1    21 ms  C ejecuta 10 ms y hace await sleep(0.2)
tick 2   121 ms  B se reanuda, ejecuta 10 ms y termina
tick 3   232 ms  C se reanuda, ejecuta 10 ms y termina
tick 4   312 ms  A se reanuda, ejecuta 10 ms y termina
tick 5   322 ms  main recibe ['A', 'B', 'C']
```

Los milisegundos pueden variar uno o dos; los números de tick y el orden, no.

**Haz (celda 3.4):** 20 llamadas a `/ventas?lento=0.2`, cada una con su `await`, una tras otra.

```python
# celda 3.4
import time, httpx
from cable import URL

inicio = time.perf_counter()
async with httpx.AsyncClient(timeout=30) as cliente:    # cliente HTTP que cede el hilo al esperar
    for _ in range(20):
        r = await cliente.get(f"{URL}/ventas?lento=0.2")  # espera ésta antes de lanzar la siguiente
print(f"20 llamadas con await en serie: {time.perf_counter() - inicio:.2f} s")
```

**Python que quizá no has visto**

| Construcción | Qué es | Por qué hace falta aquí |
|---|---|---|
| `async with` | un `with` cuya entrada y salida se esperan con `await` | abrir y cerrar las conexiones del cliente también es E/S |
| `httpx.AsyncClient` | cliente HTTP con interfaz asíncrona | `requests` bloquearía el hilo del loop |
| `await cliente.get(...)` | pide la respuesta y cede el hilo mientras llega | el loop podría correr otras tareas, pero no hay otras |

**Qué pasó:**

```text
llamada 1   ├─ 0.2 s ─┤
llamada 2              ├─ 0.2 s ─┤
...                                     el loop duerme en select durante cada espera
llamada 20                                              ├─ 0.2 s ─┤   total ≈ 20 × 0.2 s
```

**Deberías ver:**

```text
20 llamadas con await en serie: 4.04 s
```

El mismo tiempo que la serie con `requests` de la celda 1.2 (4.04 s): la corrutina cedió el hilo y nadie lo usó.

**Haz (celda 3.5):** la traza de la celda 3.3 con `time.sleep` en lugar de `await asyncio.sleep`.

```python
# celda 3.5
async def tarea_bloqueante(nombre, d):
    marca(f"{nombre} ocupa el hilo 10 ms + time.sleep({d}) + 10 ms")
    time.sleep(d + 0.02)                   # duerme SIN soltar el hilo: el loop no recupera el turno
    marca(f"{nombre} termina")
    return nombre

t0, tick, en_tick = loop.time(), -1, False
marca("main: gather crea A, B y C y hace await")
tareas = [("A", 0.3), ("B", 0.1), ("C", 0.2)]
resultado = await asyncio.gather(*(tarea_bloqueante(n, d) for n, d in tareas))
marca(f"main recibe {resultado}")
```

**Python que quizá no has visto**

| Construcción | Qué es | Por qué hace falta aquí |
|---|---|---|
| `gather(*(… for …))` | el `*` desempaca el generador: cada corrutina pasa como un argumento | arma la lista de tareas sin escribirlas una por una |
| `time.sleep` dentro de `async def` | Python lo permite; no hay error | es justo el error que esta celda quiere mostrar |

**Qué pasó:** A, B y C imprimen todas en el **tick 1**: ninguna regresó al loop, así que nunca hubo paso 2.

| tick | ms | qué ocurre |
|---:|---|---|
| 0 | 0 | main crea las tres |
| 1 | 0–320 | A retiene el hilo; B y C, listas sin turno |
| 1 | 320–440 | B retiene el hilo; C, lista sin turno |
| 1 | 440–660 | C retiene el hilo |
| 2 | 660 | main recibe `['A', 'B', 'C']` |

**Deberías ver:**

```text
tick 0     0 ms  main: gather crea A, B y C y hace await
tick 1     0 ms  A ocupa el hilo 10 ms + time.sleep(0.3) + 10 ms
tick 1   320 ms  A termina
tick 1   320 ms  B ocupa el hilo 10 ms + time.sleep(0.1) + 10 ms
tick 1   440 ms  B termina
tick 1   440 ms  C ocupa el hilo 10 ms + time.sleep(0.2) + 10 ms
tick 1   661 ms  C termina
tick 2   661 ms  main recibe ['A', 'B', 'C']
```

660 ms contra los 320 de la celda 3.3: $60+600$, la suma de todo, igual que en secuencia.

La versión larga y paso a paso está en el notebook, tema 3.

## Al diseñar / al revisar código de IA, busca…

- **`await` dentro de un `for` sobre llamadas independientes**: es la serie con otra sintaxis. Pide `gather` (y el tope de [[concurrencia-acotada]]).
- **`time.sleep(`, `requests.`, `open(...).read()` de un archivo grande o un bucle de cálculo dentro de `async def`**: bloquea el loop sin que nada falle; las demás tareas quedan listas sin turno.
- **Una corrutina llamada sin `await` ni `create_task`** (`procesa(x)` suelto): nunca corre; el único síntoma es un aviso «never awaited».
- **`create_task` cuyo resultado no se guarda en ninguna variable**: la tarea puede desaparecer a medio camino y sus excepciones se pierden. Pide guardar la `Task` o usar `TaskGroup`.
- **`asyncio.run(` dentro de una celda de notebook**, o dentro de una función que ya corre en un loop.
- **«Es asíncrono, entonces es concurrente» o «es asíncrono, entonces es paralelo»**: asíncrono describe el código; lo concurrente se ve en la traza y lo paralelo exige dos CPU ejecutando a la vez.
- **Un servidor `async` cuyo manejador calcula** (un modelo, un DataFrame grande): cada petición frena a todas las conexiones del worker.
- **Un loop de espera activa** (`while not listo: pass` o `await asyncio.sleep(0)` en un bucle sin fin): gasta una CPU entera; el loop ya sabe dormir hasta el próximo evento.

Sigue con [[concurrencia-acotada]].
