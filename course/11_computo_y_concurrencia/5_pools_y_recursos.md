---
id: pools-y-recursos
title: "Pools y recursos"
nav_title: "Pools y recursos"
summary: "Qué libera await y qué no, por qué un pool de conexiones no es un semáforo, cómo se reutiliza una conexión, por qué se suelta antes de la espera larga y cómo se dimensiona un pool con la Ley de Little."
status: ready
estimated_time: 18m
tags: [pool, conexiones, keep-alive, semaphore, httpx, requests, postgresql, pgbouncer, little]
prerequisites: [concurrencia-acotada]
---

# Pools y recursos

**Página 5 de 8 · Cómputo y concurrencia** · Pregunta: un pool de 5 conexiones tiene 5 peticiones en vuelo; ¿la sexta puede usar una de esas conexiones?, ¿una conexión se reutiliza al terminar?, ¿qué libera `await` y qué no? · Meta: distinguir **cuántas tareas gestionas** de **cuántos recursos ocupas**, y dimensionar cada tope con una cuenta.

| Término | Definición de una línea | Símbolo |
|---|---|---|
| **recurso** | Cosa finita que una tarea ocupa y otra no puede usar mientras tanto: hilo, conexión, permiso, CPU, el hilo del loop | $k$ cuántos hay |
| **concurrencia de tareas** | Cuántas tareas están vivas a la vez, aunque casi todas esperen | $L$ con la frontera en el programa |
| **concurrencia de recursos** | Cuántos recursos están ocupados de verdad en un instante | $L$ con la frontera en el recurso, $\le k$ |
| **pool** | Conjunto de objetos reales reutilizables que se prestan y se devuelven: conexiones, hilos, procesos | $k$ objetos |
| **conexión persistente** (*keep-alive*) | Conexión que, al terminar su petición, queda abierta para la siguiente | — |
| **tiempo de retención** | Cuánto tiempo una tarea tiene prestado un recurso | $W_{\text{conexión}}$ |
| **bloqueada en el pool** | La tarea espera una conexión que otra tarea tiene que devolver | `blocked` |

## En corto

- **Un `await` que suspende libera el hilo del loop, y nada más.** La conexión prestada y el permiso tomado siguen ocupados mientras la tarea espera; vuelven cuando la tarea los devuelve.
- **Hay dos concurrencias.** El event loop sube la de tareas (miles de peticiones gestionadas a la vez); los semáforos y los pools acotan la de recursos (cuántas conexiones, hilos o permisos se ocupan). 1000 peticiones HTTP no necesitan 1000 hilos ni 1000 conexiones a la BD.
- **Un pool guarda objetos; un semáforo sólo cuenta.** El pool abre, presta, recupera, reutiliza, cierra y reemplaza conexiones rotas, y se dimensiona con Little: conexiones en uso $=\lambda\cdot W_{\text{conexión}}$.

## Recurso

::: definition {#cmp-def-recurso title="Recurso"}
**En palabras.** Un recurso es algo finito que una tarea ocupa: mientras lo tiene, ninguna otra tarea lo puede usar; si no queda ninguno, la tarea que lo pide pasa a `blocked`.

**Formalmente.** Un tipo de recurso tiene $k$ unidades. Si $\operatorname{Ocupa}(t)$ es el conjunto de tareas que tienen una unidad en el instante $t$, entonces $\operatorname{card}(\operatorname{Ocupa}(t))\le k$ para todo $t$. Una tarea que pide una unidad cuando $\operatorname{card}(\operatorname{Ocupa}(t))=k$ está en `blocked` hasta que otra la devuelve. Modelo completo en [[notacion-computo]].

La **concurrencia de tareas** es cuántas tareas están vivas a la vez. La **concurrencia de recursos** es $\operatorname{card}(\operatorname{Ocupa}(t))$. La segunda nunca pasa de $k$; la primera puede ser mucho mayor.
:::

**Otro ángulo.** Cinco recursos que aparecen en esta unidad y si otra tarea puede usarlos mientras la dueña espera:

| Recurso | Lo ocupa | ¿Otra tarea lo puede usar mientras la dueña espera? | Cuántos hay |
|---|---|---|---|
| el hilo del event loop | la tarea que ejecuta | **sí**, si la dueña espera con `await` | 1 por loop |
| un hilo que ejecuta código bloqueante (`requests.get`, `time.sleep`) | esa llamada | **no**: el hilo está bloqueado hasta que vuelva | los que crees; el servidor de la clase, uno por conexión |
| un permiso de `Semaphore(k)` | la tarea dentro del `async with` | **no**, hasta salir del bloque | $k$ |
| una conexión prestada por un pool | la tarea que la pidió | **no**: lleva una petición o consulta a la vez | $k$ del pool |
| una conexión **devuelta** al pool | nadie | **sí**: la próxima tarea que pida la toma | — |

::: definition {#cmp-def-retencion title="Tiempo de retención y Little en el recurso"}
**En palabras.** El tiempo de retención es cuánto tiempo una tarea tiene prestado un recurso, desde que lo toma hasta que lo devuelve; no es la latencia de toda la petición. Con la frontera puesta en el recurso, Little dice cuántas unidades están ocupadas en promedio.

**Formalmente.** $W_{\text{recurso}}=\operatorname{dur}([\text{toma},\text{devuelve}))$, promediado sobre las tareas. En régimen estable, $L_{\text{recurso}}=\lambda\cdot W_{\text{recurso}}$ y, como $\operatorname{card}(\operatorname{Ocupa}(t))\le k$, también $L_{\text{recurso}}\le k$. Modelo completo en [[notacion-computo]].
:::

**Matemática.** Con la frontera puesta en el recurso ([[concurrencia-acotada]]):

$$L_{\text{recurso}}=\lambda\cdot W_{\text{recurso}}\le k$$

Una petición puede vivir 2 s y retener la conexión a la BD sólo 0.05 s: con $\lambda=100$ peticiones/s, $L=100\times0.05=5$ conexiones ocupadas en promedio, no $100\times2=200$.

**Ejemplo.** El servidor de la clase con 20 llamadas `requests.get` sueltas, una tras otra (celda 5.1): **concurrencia de tareas 1**, pero se abrieron 20 conexiones, una por llamada, y el servidor dedicó un hilo distinto a cada una. Con una `Session`, la misma concurrencia de tareas usa 1 conexión y 1 hilo.

**Arquitectura.** *Qué es:* separar en el diseño dos números: cuántas peticiones aceptas y cuántos recursos reales consumes por ellas. *Cuándo sí:* siempre que hables con algo que cobra por conexión (una BD, un servidor de un hilo por conexión, una API con tope). *Cuándo no:* un script que hace tres llamadas. *Qué cuesta:* un tope por recurso y una cola delante de cada uno. *Sistema real:* PostgreSQL atiende cada conexión con un proceso propio (*backend*); su `max_connections` vale 100 por omisión. Mil clientes HTTP no pueden tener una conexión cada uno.

## Cuatro roles: quién corre, quién entra, qué conexión usas, quién ejecuta

::: definition {#cmp-def-pool title="Pool"}
**En palabras.** Un pool es un conjunto de $k$ objetos reales y reutilizables (conexiones, hilos, procesos) que se crean una vez, se prestan a una tarea, se recuperan cuando la tarea los devuelve y se reutilizan para la siguiente; el pool también cierra los que sobran y reemplaza los que se rompen.

**Formalmente.** Un pool es un recurso de $k$ unidades **con identidad**: $\operatorname{Libres}(t)\cup\operatorname{Prestadas}(t)$ es el conjunto de objetos abiertos, con $\operatorname{card}(\operatorname{Prestadas}(t))\le k$; `get` mueve un objeto de libres a prestadas (o deja a la tarea en `blocked` si no hay libres) y `put` lo regresa. Modelo completo en [[notacion-computo]].

Un pool de conexiones es, aproximadamente, un semáforo de $k$ permisos **más** los objetos **más** ese ciclo de vida.
:::

**Otro ángulo.** Una petición recorre cuatro piezas que hacen cosas distintas:

::: figure {#cmp-roles-recursos title="Cuatro roles distintos en una sola petición"}
![Cuatro columnas. Event loop: quién corre; planifica tareas en un hilo y await libera ese hilo. Semáforo: quién entra; cuenta k permisos, no guarda objetos, y await no suelta el permiso. Pool: qué conexión usas; guarda conexiones reales, las abre, presta, recupera, cierra y reemplaza rotas, y await no devuelve la conexión. Servidor o base de datos: quién ejecuta, del otro lado de la red. Abajo, una petición las recorre en cinco pasos.](_assets/cmp-roles-recursos.svg)
:::

| Pieza | Decide | Vive en | Sin ella |
|---|---|---|---|
| **event loop** | **quién corre**: qué tarea lista ejecuta ahora | el cliente, un hilo | cada espera bloquea un hilo; hacen falta hilos para solaparlas |
| **semáforo** | **quién entra**: cuántas tareas pasan a la vez | el cliente | todas las tareas llegan al pool o al servidor a la vez |
| **pool** | **qué conexión usas** | el cliente (o un proceso aparte, como PgBouncer) | cada petición abre y cierra su conexión |
| **servidor / BD** | **quién ejecuta** la consulta o la petición | otro proceso, otra máquina | — |

Semáforo contra pool, rasgo por rasgo:

| Rasgo | `Semaphore(k)` | Pool de $k$ conexiones |
|---|---|---|
| limita cuántas tareas avanzan a la vez | sí | sí (si bloquea al llenarse; ver la nota) |
| guarda objetos reales | no: sólo un contador | sí: sockets abiertos |
| reutiliza | no hay nada que reutilizar | sí: la conexión devuelta sirve a la siguiente |
| abre y cierra | no | sí |
| detecta y reemplaza conexiones rotas | no | sí (validación al prestar, *pre-ping*) |
| hace esperar cuando está lleno | sí, siempre | **depende del pool**: `httpx` y los pools de BD sí; `requests.Session` por omisión **no** |
| necesita event loop | `asyncio.Semaphore` sí; `threading.Semaphore` no | no: con hilos, el hilo se bloquea esperando conexión |

> [!WARNING]
> **No todos los pools bloquean.** `requests.Session` usa el pool de `urllib3` con `pool_maxsize=10` y `pool_block=False`: con 20 hilos sobre una sola `Session` abre 20 conexiones a la vez, al devolverlas guarda 10 y tira las otras 10 con el aviso `Connection pool is full, discarding connection` (medido en esta máquina). Ese pool es un **caché** de conexiones, no un tope. `httpx.Limits(max_connections=k)` sí hace esperar a la $(k+1)$-ésima.

::: definition {#cmp-def-cota-pool title="Cota del pool"}
**En palabras.** Un pool de $k$ conexiones que bloquea al llenarse es un tope: a lo más $k$ peticiones están en vuelo, así que el throughput no pasa de $k$ entre lo que cada una retiene su conexión, y $n$ peticiones iguales tardan al menos $\lceil n/k\rceil$ olas.

**Formalmente.** $L_{\text{conexión}}\le k\ \Rightarrow\ \lambda\le k/W_{\text{conexión}}$, y $T\ge\lceil n/k\rceil\cdot W_{\text{conexión}}$. Es la cota del semáforo con $W_{\text{conexión}}$ en lugar de $e+w$. Modelo completo en [[notacion-computo]].
:::

**Matemática.** Pool de 5 conexiones (`httpx.Limits(max_connections=5)`), peticiones que retienen la conexión 0.2 s: $\lambda\le5/0.2=25$ peticiones/s, pase lo que pase con el número de tareas; 20 peticiones tardan al menos $\lceil20/5\rceil\times0.2=0.8$ s. El pool **también** es un tope, como el semáforo de [[concurrencia-acotada]]; la diferencia es lo que hay detrás del tope.

**Arquitectura.** *Qué es:* cada pieza en su capa; el loop no limita recursos y el pool no planifica. *Cuándo sí:* un servicio con `asyncio` que habla con una BD o una API: loop para las tareas, pool para las conexiones, semáforo si quieres un tope de entrada distinto. *Cuándo no:* un semáforo «por si acaso» igual al pool: no baja lo que está en vuelo, sólo cambia dónde esperan las tareas (celda 5.4). *Qué cuesta:* tres números que configurar y documentar. *Sistema real:* `psycopg_pool.AsyncConnectionPool(min_size, max_size, timeout)`; SQLAlchemy con `pool_size=5`, `max_overflow=10`, `pool_timeout=30` por omisión y `pool_pre_ping=False` por omisión (con `pool_pre_ping=True` valida la conexión al prestarla); `httpx.Limits(max_connections=100, max_keepalive_connections=20)` por omisión.

## Qué libera `await`

::: definition {#cmp-def-await-libera title="Lo que libera await"}
`await` sobre una operación pendiente **suspende la tarea y devuelve el hilo del loop** ([[asincrono-y-el-event-loop]]). No suelta nada más: la conexión prestada, el permiso del semáforo y cualquier lock que la tarea tenga **siguen ocupados** hasta que la tarea los devuelva explícitamente (`put`, salir del `async with`).
:::

**Otro ángulo.**

| Mientras la tarea hace `await` … | ¿Se libera? | Consecuencia |
|---|---|---|
| el hilo del event loop | **sí** | otras tareas listas corren |
| la conexión que tiene prestada | **no** | sigue fuera del pool; nadie más la usa |
| el permiso del `Semaphore` | **no** | sigue tomado hasta salir del bloque `async with sem` |
| un hilo bloqueado en `time.sleep` o `requests.get` | **no** (no hay `await`: es síncrono) | ese hilo no hace nada más hasta que vuelva |
| una conexión ya devuelta al pool | **sí** | la próxima tarea que pida una la toma |

**Matemática.** En la partición de la vida de una tarea ([[notacion-computo]]), el tramo en que la tarea espera la red con la conexión prestada es `wait` para ella, **y** cuenta en $W_{\text{conexión}}$. El tramo en que espera una conexión libre es `blocked`. Para el pool, sólo importa:

$$W_{\text{conexión}}=\operatorname{dur}(\text{desde get hasta put})$$

aunque casi todo ese tramo sea `wait`.

**Ejemplo.** Cien peticiones, pool de 10 conexiones, un loop: 10 tienen conexión y esperan respuesta; 90 están `blocked` en la cola del pool **sin ocupar ninguna conexión**; el loop sigue atendiendo a todas (aceptar nuevas, parsear las que ya volvieron). Concurrencia de tareas 100; concurrencia de recursos 10.

**Arquitectura.** *Qué es:* leer cada `await` preguntando qué recursos tiene prestados la tarea en ese momento. *Cuándo sí:* en todo bloque `async with pool.connection()` o `async with sem` que contenga otro `await` lento. *Cuándo no:* un `await` corto dentro de la consulta misma (es la consulta). *Qué cuesta:* nada. *Sistema real:* una conexión de PostgreSQL ejecuta **una** consulta a la vez (el modo *pipeline* de libpq encola varias, pero el servidor las ejecuta una tras otra); otra tarea no la puede usar mientras tanto.

## El ciclo de una conexión y la reutilización

::: definition {#cmp-def-keep-alive title="Conexión persistente (keep-alive)"}
Una **conexión persistente** sigue abierta después de responder y lleva la siguiente petición sin volver a conectar. En HTTP/1.1 es el comportamiento por omisión. Con los clientes de esta unidad (`requests`, `httpx`), una conexión HTTP/1.1, igual que una conexión de BD, lleva **una petición activa a la vez**; el protocolo permite *pipelining* (varias peticiones seguidas, respuestas en el mismo orden), que casi nadie usa. HTTP/2 **multiplexa** varias en la misma conexión.
:::

**Otro ángulo.**

::: figure {#cmp-ciclo-conexion title="Ciclo de una conexión del pool"}
![Tres estados de una conexión: sin abrir, libre en el pool y prestada en vuelo. Abrir cuesta TCP, TLS y autenticación; get la presta, put la devuelve libre y se reutiliza; se cierra si queda inactiva o el servidor la cierra; si se rompe en vuelo el pool la descarta y abre otra. Abajo, con 5 conexiones prestadas a p1 a p5, la petición 6 espera en la cola del pool.](_assets/cmp-ciclo-conexion.svg)
:::

- **Sin abrir → libre:** el pool paga abrirla (TCP; con HTTPS, TLS; con una BD, autenticación) una sola vez.
- **Libre → prestada (`get`):** la conexión lleva una petición; nadie más la usa.
- **Prestada → libre (`put`):** vuelve al pool y la siguiente tarea la toma **sin abrir otra**.
- **→ cerrada:** inactiva más del tiempo configurado, el servidor la cerró, o se rompió en vuelo (el pool la descarta y abre otra).

**Matemática.** Con $n$ peticiones y $c_{\text{abrir}}$ el costo de abrir una conexión:

$$\text{costo de abrir}=\begin{cases}n\cdot c_{\text{abrir}} & \text{una conexión por llamada}\\ k\cdot c_{\text{abrir}} & \text{pool de }k\text{ conexiones reutilizadas}\end{cases}$$

**Ejemplo (medido aquí, y lo que no se ve aquí).**

| Medición en esta máquina | Valor |
|---|---|
| 20 `requests.get` sueltos: puertos distintos del cliente | 20 |
| 20 llamadas con `requests.Session`: puertos distintos | 1 (la conexión llega a su petición n.º 20) |
| 200 llamadas sin `Session` | 0.28 s (1.40 ms c/u) |
| 200 llamadas con `Session` | 0.17 s (0.83 ms c/u) |
| sólo abrir y cerrar una conexión TCP local | 0.062 ms |

- **En localhost la reutilización ahorra poco, y casi nada de eso es TCP.** El handshake local cuesta 0.062 ms; el resto de la diferencia es lo que `requests.get` construye y tira en cada llamada (una `Session`, un adaptador, un pool).
- **Lo que esta máquina no muestra:** en una red real, una conexión nueva cuesta al menos 1 viaje de ida y vuelta (RTT) de TCP más 1 (TLS 1.3) o 2 (TLS 1.2) de TLS antes del primer byte. Con un RTT **supuesto** de 50 ms, son 100–150 ms por conexión nueva; reutilizar los ahorra en cada llamada después de la primera.
- Aquí el beneficio visible es **contar**: 20 conexiones y 20 hilos del servidor contra 1 y 1.

**Arquitectura.** *Qué es:* un cliente (`Session`, `httpx.Client`, un pool de BD) por proceso y por destino, creado una vez. *Cuándo sí:* muchas llamadas al mismo host. *Cuándo no:* una llamada aislada a un host que no repites. *Qué cuesta:* conexiones abiertas ocupan memoria y, del otro lado, un hilo o un proceso del servidor; por eso los pools cierran las inactivas. *Sistema real:* navegadores y `httpx` reutilizan conexiones por host; las bibliotecas de BD validan la conexión antes de prestarla porque un firewall pudo cerrarla en silencio.

## Un pool de 5 con 20 peticiones

**Otro ángulo.** La sexta petición no puede usar ninguna de las 5 conexiones mientras sigan en vuelo: espera en la cola **del pool** (`blocked`) y toma la primera que vuelve.

::: figure {#cmp-gantt-pool title="Un pool de 5 conexiones con 20 peticiones: cuatro olas"}
![Gantt de 0 a 1000 ms. Cinco carriles, uno por conexión; cada conexión lleva una petición a la vez: la conexión 1 lleva p1, p6, p11 y p16 en cuatro olas de 200 ms. La petición 6 espera en la cola del pool de 0 a 200 ms y luego viaja por la conexión 1. La cola tiene 15, 10, 5 y 0 peticiones. Total 800 ms.](_assets/cmp-gantt-pool.svg)
:::

El mismo esquema como texto (W en vuelo por una conexión, B esperando conexión, — terminada):

| | 0–0.2 s | 0.2–0.4 s | 0.4–0.6 s | 0.6–0.8 s |
|---|---|---|---|---|
| conexión 1 | p1 | p6 | p11 | p16 |
| conexión 2 | p2 | p7 | p12 | p17 |
| conexión 3 | p3 | p8 | p13 | p18 |
| conexión 4 | p4 | p9 | p14 | p19 |
| conexión 5 | p5 | p10 | p15 | p20 |
| p6 | B | W | — | — |
| cola del pool | 15 | 10 | 5 | 0 |

Cómo leer cada tramo, con un solo hilo del loop en una CPU del cliente:

- **$[0,0.2)$, conexiones 1 a 5:** p1 a p5 tomaron una conexión cada una en el instante 0 y mandaron su petición. Están en `wait`: su petición viaja por **su** conexión y el servidor la tiene 0.2 s. No ocupan el hilo del loop.
- **$[0,0.2)$, p6 a p20:** están en `blocked`, no en `ready`. Lo que les falta no es CPU (el hilo del loop está casi siempre libre), sino una conexión, y las 5 están prestadas a tareas que esperan respuesta. Por eso la cola del pool tiene 15.
- **En 0.2 s:** llega la respuesta de p1 por la conexión 1. p1 pasa a `ready`, el loop la ejecuta unos microsegundos (lee la respuesta) y la conexión 1 vuelve al pool. La primera de la cola, p6, la toma: pasa de `blocked` a `wait` **en la conexión 1**. Lo mismo ocurre con p2→p7 en la conexión 2, y así hasta p5→p10.
- **Cada ola repite eso:** la conexión $j$ lleva, una tras otra, $p_j$, $p_{j+5}$, $p_{j+10}$ y $p_{j+15}$. Ninguna conexión lleva dos peticiones a la vez.

**Matemática.** Con $n=20$, $k=5$ y $W_{\text{conexión}}=0.2$ s, la cota del semáforo vale igual para el pool:

$$T\ge\left\lceil n/k\right\rceil\cdot W_{\text{conexión}}=\left\lceil20/5\right\rceil\times0.2=0.8\ \text{s}$$

Little con la frontera en las conexiones: $\lambda=5/0.2=25$ peticiones/s y $L=\lambda\cdot W=25\times0.2=5$: las 5 conexiones ocupadas todo el tiempo.

**Ejemplo (celda 5.2).** Medido: 0.83 s, 5 puertos distintos, 5 peticiones por ola en 4 olas y exactamente 4 peticiones por conexión. La primera de tres repeticiones tardó más (el primer uso de `httpx` en el proceso); por eso se reporta la mediana.

**Arquitectura.** *Qué es:* el pool como tope de recursos con cola propia. *Cuándo sí:* siempre que el destino aguante menos conexiones que tareas tienes. *Cuándo no:* si $k$ es mayor que el número de tareas, el tope no actúa. *Qué cuesta:* las peticiones de la cola acumulan `blocked`; su latencia sube aunque nadie esté calculando. *Sistema real:* `httpx` tiene un *pool timeout* (parte de `httpx.Timeout`): si una petición espera conexión más de eso, falla con `PoolTimeout` en vez de esperar para siempre.

## Conexiones del cliente = hilos ocupados del servidor

**Otro ángulo.** El servidor de la clase es un `ThreadingHTTPServer`: **un hilo por conexión**, vivo mientras la conexión siga abierta ([[secuencial-concurrente-paralelo]]). Lo que el cliente decide sobre conexiones se convierte en hilos del otro lado:

| Cliente | Conexiones abiertas | Hilos del servidor ocupados |
|---|---|---|
| 20 `requests.get` sueltos, en serie | 20, una tras otra | 20 hilos distintos, uno a la vez |
| una `Session`, en serie | 1 | 1 hilo que atiende las 20 |
| `httpx` con `Limits(max_connections=5)` y 20 tareas | 5 | 5 a la vez |
| una `Session` compartida por 20 hilos | 20 a la vez (no bloquea) | 20 a la vez |

**Matemática.** Con la frontera puesta en el servidor, sus hilos ocupados son $L_{\text{servidor}}=\lambda\cdot W$. Si cada cliente reparte su tráfico en un pool de $k$ conexiones y hay $r$ clientes iguales:

$$L_{\text{servidor}}\le r\cdot k$$

**Ejemplo.** Cuatro réplicas de una API con un pool de 10 conexiones cada una abren hasta $4\times10=40$ conexiones a la misma BD (cifras supuestas). Si la BD acepta 30, los pools locales, cada uno correcto, suman un exceso.

**Arquitectura.** *Qué es:* el pool del cliente es la carga del servidor. *Cuándo sí:* dimensiona la suma de todos los pools contra lo que acepta el destino. *Cuándo no:* destinos que multiplexan (HTTP/2) o que no cobran por conexión. *Qué cuesta:* coordinar tamaños entre réplicas. *Sistema real:* PostgreSQL (un proceso por conexión); Apache httpd con el MPM `worker` (un hilo por conexión).

## Soltar el recurso antes de la espera larga

::: definition {#cmp-def-soltar-antes title="Soltar antes"}
**Soltar antes** es devolver un recurso (conexión, permiso) en cuanto deja de usarse, **antes** de una espera que no lo necesita, y volver a pedirlo después si hace falta. Reduce $W_{\text{conexión}}$ sin cambiar la latencia de la petición.
:::

**Otro ángulo.**

::: figure {#cmp-pool-soltar-antes title="Soltar la conexión antes de la espera larga"}
![Dos Gantt de 0 a 2500 ms con 6 tareas y un pool de 3 conexiones; cada tarea consulta la BD 100 ms, llama a una API lenta 1000 ms y escribe 100 ms. Arriba, retener: cada tarea guarda su conexión durante la API y las tareas 4 a 6 esperan una ola entera; total 2400 ms. Abajo, soltar: la tarea devuelve la conexión antes de la API y toma otra para escribir; las esperas se solapan sin ocupar conexión; total 1300 ms.](_assets/cmp-pool-soltar-antes.svg)
:::

| | Retener | Soltar |
|---|---|---|
| orden | `get` → consulta → API → escribe → `put` | `get` → consulta → `put` → API → `get` → escribe → `put` |
| $W_{\text{conexión}}$ por tarea (figura) | 1200 ms | 200 ms (100 + 100) |
| total de la figura | 2400 ms | 1300 ms |
| la conexión durante la API | prestada, sin uso | libre: otra tarea la usa |

Cómo leer la figura:

- **Retener, $[0,1200)$:** las tareas 1 a 3 tienen las conexiones 1 a 3. Durante su API (de 100 a 1100 ms) están en `wait` por la API, **y** su conexión de BD sigue prestada sin llevar nada. Las tareas 4 a 6 están en `blocked`: no les falta CPU, les falta una conexión que nadie usa pero nadie devolvió. En 1200 ms las tres primeras devuelven su conexión y empieza la segunda ola.
- **Soltar:** la tarea 1 usa la conexión 1 de 0 a 100 ms y la devuelve; la tarea 4 la toma en 100 ms. Durante su API, cada tarea está en `wait` **sin conexión**. Al terminar la API pide una conexión otra vez para escribir; si las 3 están prestadas, queda en `blocked` hasta que se libere una.

**Matemática.** Con $k$ conexiones, $\lambda\le k/W_{\text{conexión}}$. En la celda 5.3: $n=12$ tareas, $k=3$, 0.2 s con la conexión y 0.5 s en otra API:

- retener: $W_{\text{conexión}}=0.7$ s, $T\approx\lceil12/3\rceil\times0.7=4\times0.7=2.8$ s;
- soltar: $W_{\text{conexión}}=0.2$ s, $T\approx\lceil12/3\rceil\times0.2+0.5=0.8+0.5=1.3$ s (la última ola todavía espera su API).

**Ejemplo.** Medido con el pool simple de la celda 5.3: retener 2.81 s, soltar 1.31 s. Ahora el caso que pidió el profesor, con **cifras supuestas**: un endpoint consulta la BD (50 ms), llama a un modelo de IA (60 s) y guarda el resultado (50 ms), con un pool de 10 conexiones.

| | $W_{\text{conexión}}$ | $\lambda\le10/W_{\text{conexión}}$ |
|---|---|---|
| retiene la conexión durante la IA | 60.1 s | $\approx0.17$ peticiones/s (10 por minuto) |
| suelta antes y pide otra para guardar | 0.1 s | 100 peticiones/s |

La IA tarda lo mismo en los dos casos; lo que cambia es cuántas peticiones caben.

**Arquitectura.** *Qué es:* transacciones cortas; nunca una llamada de red externa dentro de una transacción de BD. *Cuándo sí:* toda espera larga que no use el recurso (otra API, un modelo, un archivo grande). *Cuándo no:* si la consulta y la escritura deben ser **una** transacción atómica; entonces se rediseña (guardar un estado «pendiente», llamar fuera, confirmar después) en vez de retener. *Qué cuesta:* un segundo `get` (barato si la conexión se reutiliza) y pensar la consistencia. *Sistema real:* PgBouncer en modo *transaction* devuelve la conexión del servidor al terminar cada transacción, no al cerrar el cliente.

## Tres topes distintos

::: definition {#cmp-def-tres-topes title="Tope de tareas, de entrada y de recursos"}
- **Tope de tareas:** cuántas corrutinas o hilos existen. `gather(*…)` sin límite crea una por elemento; las corrutinas son baratas, los hilos no.
- **Tope de entrada:** cuántas tareas pasan una compuerta a la vez (`Semaphore(k)`). Cuenta permisos; no guarda nada.
- **Tope de recursos:** cuántos objetos reales hay (conexiones del pool, hilos de un `ThreadPoolExecutor`, procesos).
:::

**Otro ángulo.**

| Tope | Lo pone | Si falta | Si sobra (más alto de lo útil) |
|---|---|---|---|
| tareas | cuántas creas | — | memoria por tarea; con hilos, una pila por hilo |
| entrada | `Semaphore(k)` | todas llegan al pool a la vez | no baja lo que está en vuelo: manda el pool |
| recursos | `Limits`, `max_size`, `max_workers` | cada petición abre la suya | satura al destino (BD, servidor) |

**Matemática.** Con un semáforo de $k_s$ permisos sobre un pool de $k_p$ conexiones, lo que está en vuelo es

$$\min(k_s,k_p)$$

si cada tarea con permiso usa una conexión exclusiva. Un semáforo **sólo baja lo que está en vuelo si es menor que el pool**. Con $k_s=k_p$, la espera queda en el semáforo y no en el pool; con $k_s>k_p$, el semáforo limita cuántas peticiones llegan a la cola del pool, pero no agrega conexiones. Con 20 peticiones de 0.2 s y $k_p=5$:

| $k_s$ | $\min(k_s,5)$ | Cota $\lceil20/\min\rceil\times0.2$ | Medido (celda 5.4) |
|---:|---:|---|---|
| 32 | 5 | $4\times0.2=0.8$ s | 0.83 s, 5 puertos |
| 5 | 5 | $4\times0.2=0.8$ s | 0.83 s, 5 puertos |
| 3 | 3 | $7\times0.2=1.4$ s | 1.43 s, **3** puertos |

**Ejemplo: la cola dentro del pool cuesta CPU.** Con 500 llamadas de 0.2 s, `Semaphore(100)` y un pool de 100, lo ideal serían 5 olas (≈1 s). Medido: 7.86 s, con 7.45 s de **CPU del cliente**, y 182 puertos distintos con `max_connections=100` (el pool cerró y reabrió conexiones). El perfil señala a `httpcore` (versión 1.0.9): en cada evento recorre las peticiones en cola contra todas las conexiones, un costo que crece con cola × conexiones. Con `Semaphore(32)` delante del mismo pool de 100: 3.42 s. Es una propiedad de **esta** implementación, medida en esta máquina, no una ley; la lección general sí lo es: **mide antes de subir un tope**, y un semáforo menor que el pool mantiene corta la cola del pool.

**Arquitectura.** Dimensionar de abajo hacia arriba:

| Decisión | Criterio |
|---|---|
| 1. pool (recursos) | lo que acepta el destino (la BD, el servidor, el proveedor), no el tráfico; ejemplos: `TCPConnector(limit=100)` de `aiohttp`, `Limits(max_connections=100)` de `httpx` |
| 2. semáforo (entrada) | opcional; $\le$ pool si quieres la espera fuera del pool; lo pones tú |
| 3. tareas | acotadas si cada una cuesta memoria (hilos) o si llegan sin fin: cola acotada ([[concurrencia-acotada]]) |
| cuándo no | tres topes iguales sin una razón para cada uno |
| qué cuesta | cada tope agrega una cola que hay que vigilar |

## Pools de hilos y de procesos: el mismo patrón

::: definition {#cmp-def-pool-trabajadores title="Pool de trabajadores"}
`ThreadPoolExecutor` y `ProcessPoolExecutor` son pools cuyos objetos son **trabajadores** (hilos o procesos) en lugar de conexiones: se crean una vez, toman tareas de una cola interna y se reutilizan. Mismo ciclo: crear, prestar (asignar tarea), recuperar, reutilizar, cerrar.
:::

**Otro ángulo.**

| Pool | Objeto | Costo de crear uno | Por omisión |
|---|---|---|---|
| de conexiones HTTP | socket abierto (TCP, TLS) | handshake | `httpx`: 100 conexiones, 20 persistentes |
| de conexiones de BD | conexión autenticada | handshake + autenticación + un proceso del servidor | SQLAlchemy: 5 + 10 de desborde |
| `ThreadPoolExecutor` | hilo | crear un hilo | `min(32, CPUs + 4)` hilos |
| `ProcessPoolExecutor` | proceso con su intérprete | arrancar Python, importar | `os.process_cpu_count()` procesos (3.13+; antes, `os.cpu_count()`) |

**Matemática.** Si crear el pool cuesta $c_{\text{crear}}$ y lo creas en cada una de $n$ llamadas, pagas $n\cdot c_{\text{crear}}$; creado una vez, $c_{\text{crear}}$. Es la misma cuenta de abrir conexiones.

**Ejemplo.** Medición de referencia (una corrida, 8 CPU lógicas): 10 llamadas mínimas con un `ProcessPoolExecutor` de 2 procesos creado en cada llamada, 0.73 s; con uno solo para todas, 0.07 s. La celda vive en [[calcular-en-paralelo]].

**Arquitectura.** *Qué es:* un pool por proceso, creado al arrancar el servicio. *Cuándo sí:* siempre que haya más de una tarea. *Cuándo no:* **el pool por llamada** (crear el executor, el `Client` o la conexión dentro del manejador o del bucle) es un anti-patrón: paga el costo de crear en cada petición y no reutiliza nada. *Qué cuesta:* cerrar el pool al apagar (`with`, o un *shutdown* del servicio). *Sistema real:* el executor por omisión de `asyncio` (`to_thread`, `run_in_executor(None, …)`) es un `ThreadPoolExecutor` compartido.

## Arquitectura: 1000 peticiones HTTP y 10 conexiones a PostgreSQL

**Otro ángulo.** Un API server con `asyncio` recibe 1000 peticiones simultáneas; cada una consulta PostgreSQL 0.2 s:

| Capa | Cuántos | Quién lo controla |
|---|---|---|
| peticiones HTTP abiertas | 1000 corrutinas | el event loop (tope de tareas) |
| hilos | 1 (el del loop) por proceso | el diseño |
| permisos | opcional, $\le10$ | un `Semaphore` |
| conexiones a PostgreSQL | 10 | el pool de la aplicación |
| procesos del servidor PostgreSQL | 10 | uno por conexión |

- **El loop atiende las 1000**: acepta, parsea y responde. **El pool deja hablar con la BD a 10.** Las 990 restantes están `blocked` en la cola del pool sin ocupar conexión.
- **PgBouncer** es un pool **externo**: muchos clientes (réplicas, procesos) se conectan a él y él reparte pocas conexiones reales a PostgreSQL. Modos: *session* (la conexión se presta por sesión de cliente), *transaction* (por transacción: el que más comparte) y *statement* (por sentencia).

**Matemática.** Little con la frontera en el pool, **cifras supuestas** (las de [[notacion-computo]]): $\lambda=50$ peticiones/s.

| Dependencia | $W_{\text{conexión}}$ | Conexiones en uso $L=\lambda W$ | Con pool de 10 |
|---|---|---|---|
| normal | 0.2 s | $50\times0.2=10$ | 100 % de utilización nominal: con variabilidad hace falta margen; comprueba la cola y el $p_{99}$ |
| lenta | 2 s | $50\times2=100$ | $\lambda\le10/2=5$/s: llegan 50/s y salen 5/s |

**Ejemplo: qué pasa cuando la dependencia pasa de 0.2 s a 2 s.**

1. Cada consulta retiene su conexión 10 veces más: Little pide 100 conexiones y hay 10.
2. **El pool se agota**: la cola del pool crece unas 45 peticiones por segundo.
3. La latencia de todas sube, aunque su consulta no haya cambiado: la mayor parte es `blocked`.
4. Sin límites, las corrutinas en cola se acumulan en memoria y los clientes reintentan, lo que empeora la cola.
5. **Lo que se diseña:** *timeout* de adquisición del pool (falla rápido en vez de esperar para siempre); **backpressure** (rechazar con `503` o `429` cuando la cola pasa de un tamaño); *deadline* de extremo a extremo; y **no** subir el pool a 100, porque eso sólo mueve la cola a PostgreSQL, que ahora tiene 100 procesos compitiendo por las mismas CPU y discos.

**Arquitectura.** *Qué es:* event loop para la concurrencia de tareas, pool para la de recursos, PgBouncer cuando hay muchos procesos cliente. *Cuándo sí:* servicios con muchas peticiones que esperan y una BD finita. *Cuándo no:* un servicio interno con pocas peticiones: un pool chico y nada más. *Qué cuesta:* un proceso más (PgBouncer) y en modo *transaction* se pierden cosas de sesión (variables `SET`, *prepared statements* según la versión). *Sistema real:* la suma de pools de todas las réplicas, o la de PgBouncer, se dimensiona con el `max_connections` de PostgreSQL.

Resumen de quién hace qué:

| Pieza | Responde |
|---|---|
| event loop | quién corre |
| semáforo | quién entra |
| pool | qué conexión usas |
| PostgreSQL | quién ejecuta SQL |

## La decisión hasta aquí

| Si observas… | Entonces | Página |
|---|---|---|
| el reloj es casi todo espera ($\rho$ pequeño) | reorganiza las esperas, no aceleres el cálculo | 1 |
| pocas decenas de esperas con biblioteca bloqueante | hilos | 2 |
| cientos o miles de esperas | `asyncio` en un loop | 3 |
| muchas tareas contra un destino finito | un tope $k$ con `Semaphore`, dimensionado con $\lambda\le k/W$ | 4 |
| muchas llamadas al mismo destino | **un cliente o pool por proceso, creado una vez** (`Session`, `httpx.AsyncClient`, pool de BD) | 5 |
| un recurso retenido durante una espera que no lo usa | **suéltalo antes** y pídelo de nuevo | 5 |
| un semáforo y un pool juntos | **semáforo $\le$ pool, o ninguno**; el pool se dimensiona con lo que acepta el destino | 5 |
| varios procesos o réplicas contra la misma BD | **suma los pools**; si no cabe, un pool externo (PgBouncer) | 5 |

## Código

Todas las celdas usan el servidor de la clase (`FDD_SILENCIO=1 uv run python servidor.py`) y su endpoint `GET /quien`, que responde **el puerto de tu conexión**, **el hilo del servidor que la atiende** y **cuántas peticiones lleva esa conexión**. Un puerto distinto es una conexión TCP distinta.

**Haz (celda 5.1):** cuenta conexiones con `requests.get` suelto y con una `Session`.

```python
import requests
from cable import URL

def resume(nombre, vistos):                   # vistos: las respuestas de /quien
    puertos = {v["puerto"] for v in vistos}   # puerto del cliente: uno por conexión TCP
    hilos = {v["hilo"] for v in vistos}       # hilo del servidor que atendió esa conexión
    n_max = max(v["peticion_en_conexion"] for v in vistos)  # peticiones de la conexión más usada
    print(f"{nombre}: {len(puertos)} puertos · {len(hilos)} hilos del servidor"
          f" · hasta {n_max} peticiones por conexión")

resume("suelto ", [requests.get(f"{URL}/quien").json() for _ in range(20)])  # una conexión por llamada
with requests.Session() as s:                 # la Session guarda la conexión entre llamadas
    resume("Session", [s.get(f"{URL}/quien").json() for _ in range(20)])
```

**Python que quizá no has visto.**
- `requests.Session()` — un cliente con su propio pool de conexiones; `s.get` reutiliza la conexión abierta. `requests.get` suelto crea una sesión, la usa una vez y la tira: por eso abre una conexión nueva cada vez. Hace falta aquí porque es justo lo que se compara.
- `with … as s:` — cierra la sesión (y sus conexiones) al salir del bloque.
- `{v["puerto"] for v in vistos}` — un conjunto: los repetidos cuentan una vez, así que su tamaño es cuántas conexiones distintas hubo.

**Qué pasó.**

| | Conexiones (puertos) | Hilos del servidor | Peticiones por conexión |
|---|---|---|---|
| suelto | 20 | 20 | 1 |
| `Session` | 1 | 1 | 1 … 20 |

Cada conexión nueva del cliente fue un hilo nuevo del servidor de la clase.

**Deberías ver:**

```text
suelto : 20 puertos · 20 hilos del servidor · hasta 1 peticiones por conexión
Session: 1 puertos · 1 hilos del servidor · hasta 20 peticiones por conexión
```

**Haz (celda 5.2):** 20 peticiones de 0.2 s con un pool de 5 conexiones.

```python
import asyncio, time
from collections import Counter
import httpx

limites = httpx.Limits(max_connections=5)     # el pool del cliente: a lo más 5 conexiones
async with httpx.AsyncClient(limits=limites, timeout=30) as cliente:
    async def una(i):
        d = (await cliente.get(f"{URL}/quien?lento=0.2")).json()   # 0.2 s en el servidor
        return i, round((time.perf_counter() - t0) / 0.2), d       # ola = fin / 0.2 s
    t0 = time.perf_counter()
    res = await asyncio.gather(*(una(i) for i in range(20)))      # 20 a la vez
print(f"20 peticiones, pool de 5: {time.perf_counter() - t0:.2f} s")
print("puertos distintos:", len({d["puerto"] for _, _, d in res}))
print("peticiones por ola:", dict(sorted(Counter(ola for _, ola, _ in res).items())))
print("peticiones por conexión:", sorted(Counter(d["puerto"] for _, _, d in res).values()))
```

**Python que quizá no has visto.**
- `httpx.Limits(max_connections=5)` — el tamaño del pool de `httpx`. A diferencia del de `requests`, **hace esperar** a la sexta petición hasta que vuelva una conexión. Hace falta aquí para que el pool, no el número de tareas, sea el tope.
- `async with httpx.AsyncClient(...)` — abre el cliente (y su pool) y lo cierra al salir; `async` porque cerrar conexiones también espera la red.
- `asyncio.gather(*(una(i) for i in range(20)))` — lanza las 20 corrutinas a la vez y espera todas; el `*` reparte el generador en 20 argumentos.
- `Counter(...)` — cuenta cuántas veces aparece cada valor: peticiones por ola y por puerto.

**Qué pasó.** Las 20 tareas se crearon a la vez (concurrencia de tareas 20), pero sólo 5 tuvieron conexión (concurrencia de recursos 5). Las otras 15 quedaron `blocked` en la cola del pool y salieron en olas, como en la figura `cmp-gantt-pool`:

| ola | peticiones que terminan | cola del pool al empezar la ola |
|---:|---:|---:|
| 1 | 5 | 15 |
| 2 | 5 | 10 |
| 3 | 5 | 5 |
| 4 | 5 | 0 |

**Deberías ver:**

```text
20 peticiones, pool de 5: 0.83 s
puertos distintos: 5
peticiones por ola: {1: 5, 2: 5, 3: 5, 4: 5}
peticiones por conexión: [4, 4, 4, 4, 4]
```

**Haz (celda 5.3):** un pool hecho a mano con `asyncio.Queue`, y retener contra soltar.

```python
async def con_pool(retener, k=3, n=12):
    pool = asyncio.Queue()
    for i in range(k):
        pool.put_nowait(f"conexión-{i}")      # k conexiones (simuladas) a la BD
    async def tarea():
        c = await pool.get()                  # pedir prestada: espera si no queda ninguna
        await asyncio.sleep(0.2)              # la consulta usa la conexión
        if not retener: pool.put_nowait(c)    # soltar ANTES de la espera larga
        await asyncio.sleep(0.5)              # otra API: no necesita la BD
        if retener: pool.put_nowait(c)        # soltar DESPUÉS: la tuvo 0.7 s
    t0 = time.perf_counter()
    await asyncio.gather(*(tarea() for _ in range(n)))
    return time.perf_counter() - t0
for retener in (True, False):
    print(f"{'retiene' if retener else 'suelta '} la conexión: {await con_pool(retener):.2f} s")
```

**Python que quizá no has visto.**
- `asyncio.Queue()` — una cola para corrutinas. `await pool.get()` saca un objeto o, si está vacía, **suspende** la tarea hasta que alguien meta uno; `put_nowait(c)` lo devuelve. Hace falta aquí porque eso **es** un pool: una cola de objetos reales. Un `Semaphore` sólo guardaría el número 3, no las conexiones.
- `async def tarea()` dentro de otra función — una corrutina que ve `pool` y `retener` de la función de afuera.
- `await` de nivel superior — el notebook ya tiene un loop corriendo; por eso no hay `asyncio.run`.

**Qué pasó.** Con $k=3$, cuatro olas de tareas. Al retener, cada ola ocupa las conexiones 0.7 s: $4\times0.7=2.8$ s. Al soltar, cada ola las ocupa 0.2 s y las esperas de la otra API se solapan sin conexión: $4\times0.2+0.5=1.3$ s.

| | Conexión en uso por tarea | Olas | Cuenta |
|---|---|---|---|
| retiene | 0.7 s | 4 | $4\times0.7=2.8$ s |
| suelta | 0.2 s | 4 | $4\times0.2+0.5=1.3$ s |

**Deberías ver:**

```text
retiene la conexión: 2.81 s
suelta  la conexión: 1.31 s
```

**Haz (celda 5.4):** un `Semaphore` encima del pool: ¿quién limita?

```python
async def lote(permisos, conexiones, n=20):
    sem = asyncio.Semaphore(permisos)                       # tope de entrada: cuenta permisos
    limites = httpx.Limits(max_connections=conexiones)      # tope de recursos: conexiones reales
    async with httpx.AsyncClient(limits=limites, timeout=30) as c:
        async def una():
            async with sem:                                 # el permiso se retiene durante el await
                return (await c.get(f"{URL}/quien?lento=0.2")).json()["puerto"]
        t0 = time.perf_counter()
        puertos = await asyncio.gather(*(una() for _ in range(n)))
    return time.perf_counter() - t0, len(set(puertos))

for permisos, conexiones in [(32, 5), (5, 5), (3, 5)]:
    t, p = await lote(permisos, conexiones)
    print(f"Semaphore({permisos:2d}) + pool de {conexiones}: {t:.2f} s · {p} puertos")
```

**Python que quizá no has visto.**
- `asyncio.Semaphore(permisos)` y `async with sem:` — toma un permiso al entrar y lo suelta al salir del bloque, también si hay error. Hace falta aquí para tener un tope de entrada **distinto** del tope del pool y ver cuál manda.

**Qué pasó.** Lo que está en vuelo es $\min(k_s,k_p)$. Con 32 o 5 permisos manda el pool (5); con 3 manda el semáforo, son 7 olas ($\lceil20/3\rceil$) y el pool nunca abre más de 3 conexiones.

**Deberías ver:**

```text
Semaphore(32) + pool de 5: 0.83 s · 5 puertos
Semaphore( 5) + pool de 5: 0.83 s · 5 puertos
Semaphore( 3) + pool de 5: 1.43 s · 3 puertos
```

**Haz (celda 5.5, opcional):** 500 llamadas con un pool de 100, con un semáforo de 100 y con uno de 32.

```python
for permisos, conexiones in [(100, 100), (32, 100)]:
    t, p = await lote(permisos, conexiones, n=500)          # la función de la celda 5.4
    print(f"500 llamadas, Semaphore({permisos}) + pool de {conexiones}: {t:.2f} s · {p} puertos")
```

**Qué pasó.** Con 100 permisos la cola vive **dentro** del pool de `httpx`, y la gestión de esa cola consume CPU del cliente: el tiempo pasa de las 5 olas ideales a varios segundos, y aparecen más puertos que conexiones permitidas. Con 32 permisos la cola queda en el semáforo y el pool sólo ve 32 peticiones a la vez. Mide `time.process_time()` alrededor de la llamada si quieres ver la CPU del cliente.

**Deberías ver:**

```text
500 llamadas, Semaphore(100) + pool de 100: 7.86 s · 182 puertos
500 llamadas, Semaphore(32) + pool de 100: 3.42 s · 32 puertos
```

La versión larga y paso a paso está en el notebook, tema 5.

## Al diseñar / al revisar código de IA, busca…

- **Un `requests.get`, `httpx.get` o `httpx.AsyncClient()` dentro del bucle o del manejador.** Una conexión nueva por llamada y un pool que nunca se reutiliza. Un cliente por proceso y por destino, creado una vez.
- **Un `ThreadPoolExecutor`/`ProcessPoolExecutor` creado por llamada.** El mismo anti-patrón con trabajadores.
- **Una llamada lenta (otra API, un modelo de IA) dentro de `async with pool.connection()` o de una transacción.** Retiene la conexión toda la espera; suéltala antes.
- **Creer que `await` libera la conexión o el permiso.** Sólo libera el hilo del loop.
- **Un `Semaphore` mayor o igual que el pool «para limitar».** No baja lo que está en vuelo (manda el pool); si quieres la espera fuera del pool, hazlo menor o igual.
- **Contar con que una `requests.Session` compartida por muchos hilos pone un tope.** Su pool no bloquea por omisión (`pool_block=False`): abre de más y tira conexiones.
- **El tamaño del pool sacado del tráfico («1000 usuarios, 1000 conexiones»).** Se saca de lo que acepta el destino y de $\lambda\cdot W_{\text{conexión}}$, sumando todas las réplicas.
- **Pools sin *timeout* de adquisición.** Cuando la dependencia se pone lenta, la cola crece sin límite.

Sigue con [[calcular-en-paralelo]].
