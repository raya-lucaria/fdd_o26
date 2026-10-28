---
id: concurrencia-acotada
title: "Concurrencia acotada"
nav_title: "Concurrencia acotada"
summary: "gather lanza n esperas a la vez y junta sus resultados; Semaphore(k) deja entrar a lo más k y forma a las demás. Con la cota ⌈n/k⌉(e+w) y la Ley de Little se predice cuánto tardan 500 llamadas antes de medirlas."
status: ready
estimated_time: 15m
tags: [asyncio, gather, semaphore, little, backpressure, bulkhead, scatter-gather, httpx]
prerequisites: [asincrono-y-el-event-loop]
---

# Concurrencia acotada

**Página 4 de 8 · Cómputo y concurrencia** · Pregunta: **hay que hacer 500 llamadas y el servidor acepta unas 32 a la vez: ¿cuánto vas a tardar y cómo evitas tumbarlo?** · Meta: lanzar muchas esperas con `gather`, acotarlas con `Semaphore(k)`, predecir el tiempo con una cuenta y elegir $k$ con una medición.

| Término | Definición de una línea | Símbolo |
|---|---|---|
| `gather` | lanza $n$ corrutinas como tareas y espera a todas; devuelve sus resultados en el orden de los argumentos | — |
| fan-out / fan-in | repartir una petición en $n$ llamadas / juntar las $n$ respuestas en una | — |
| bloqueada | espera algo que **otra tarea del programa** tiene que soltar: un permiso, un lock, una conexión, un resultado | $\operatorname{blocked}(\tau)$, $b$ |
| semáforo | contador de permisos: tomar uno resta, devolverlo suma; sin permisos, la tarea se forma | $k$ |
| ventana deslizante | en cuanto una tarea suelta su permiso, entra la siguiente; no hay tandas | — |
| Ley de Little | tareas en vuelo = rendimiento × tiempo en el sistema | $L=\lambda W$ |
| *backpressure* | el lado saturado frena a quien le manda trabajo, en vez de aceptarlo todo | — |
| *bulkhead* | un tope separado por dependencia, para que una lenta no se lleve los permisos de las demás | $k_A$, $k_B$ |
| *rate limit* | tope de peticiones **por unidad de tiempo** que impone el proveedor | $\lambda_{\max}$ |

## En corto

- **`gather` sin tope tarda lo que la tarea más larga**, pero pone las $n$ llamadas en vuelo a la vez: miles de corrutinas cuestan poco al cliente, miles de conexiones abiertas no le cuestan poco al servidor.
- **`Semaphore(k)` es una ventana deslizante de $k$ permisos.** Con $n$ tareas iguales, $T\ge\lceil n/k\rceil(e+w)$ y $\lambda\le k/W$: 500 llamadas de 0.2 s con $k=32$ no bajan de 3.2 s.
- **Un tope de concurrencia no es un *rate limit* ni un pool.** Acota cuántas hay en vuelo; no cuántas por segundo (un `429` sigue posible) ni cuántas conexiones reales existen (eso es la página 5).

## `gather`: fan-out y fan-in

::: definition {#cmp-def-gather title="gather"}
`asyncio.gather(c_1, …, c_n)` recibe $n$ corrutinas (o tareas), **agenda cada una como `Task`** en el loop y devuelve una sola cosa que se espera con `await`. Cuando las $n$ terminan, entrega la lista de resultados **en el orden de los argumentos**, no en el de llegada.

- **Fan-out:** las $n$ arrancan en el mismo tick; cada una corre hasta su primer `await` y cede el hilo.
- **Fan-in:** quien hizo `await gather(…)` queda **bloqueada** hasta que termina la última.
- **Si una falla** (por omisión): `gather` propaga **la primera excepción** a quien espera y **no cancela** a las demás, que siguen corriendo. Con `return_exceptions=True`, la excepción ocupa su lugar en la lista y nada se propaga.
:::

**Otro ángulo.** El ejemplo único de la unidad (tres tareas de 20 ms ejecuta + 200 ms espera + 20 ms ejecuta) lanzado con `gather`:

::: figure {#cmp-gantt-gather title="gather: fan-out en un tick, esperas solapadas, fan-in en la última"}
![Diagrama de Gantt con eje de 0 a 300 ms y vidas de 240, 260 y 280 ms, total 280 ms, con una fila para la corrutina principal y una por cada tarea del ejemplo único. En t=0 la principal llama a gather y las tres tareas nacen juntas (fan-out); cada una ejecuta 20 ms por turnos en el único hilo del loop, las tareas 2 y 3 aparecen rayadas como listas mientras esperan turno, y después las tres esperas de red de 200 ms se dibujan solapadas. Las respuestas regresan, cada tarea ejecuta sus últimos 20 ms y la principal, bloqueada desde t=0, recibe la lista de resultados en t=280 cuando termina la última (fan-in).](_assets/cmp-gantt-gather.svg)
:::

El mismo Gantt como texto (columnas no a escala; E ejecuta, W espera red, R lista, B bloqueada, — terminada):

| | 0–20 | 20–40 | 40–60 | 60–220 | 220–240 | 240–260 | 260–280 |
|---|---|---|---|---|---|---|---|
| main | B | B | B | B | B | B | B |
| τ1 | E | W | W | W | E | — | — |
| τ2 | R | E | W | W | W | E | — |
| τ3 | R | R | E | W | W | W | E |
| hilo del loop | τ1 | τ2 | τ3 | ocioso | τ1 | τ2 | τ3 |

- `main` está en `blocked`, no en `wait`: lo que le falta lo producen otras tareas del programa, no la red.
- El resultado llega como `[r1, r2, r3]` aunque las tres hubieran terminado en otro orden.

**Matemática.** Si las $n$ tareas arrancan juntas ($\operatorname{start}=0$) y no hay tope, el lote dura lo que la vida más larga, y esa vida incluye las listas:

$$T=\max_i d_i,\qquad \max_i(e_i+w_i)\;\le\;T,\qquad \sum_i e_i\;\le\;T\ \text{(un solo hilo)}$$

Con el ejemplo: $\max_i(e_i+w_i)=240$, $\sum_i e_i=120$, y $T=\max(240,260,280)=280$ ms. Los 40 ms por encima de 240 son las listas de $\tau_3$: esperó turno de CPU, no red. Contra la secuencia, $720/280\approx2.57$.

**Ejemplo.** 20 llamadas a `/ventas?lento=0.2` con `gather` tardan 0.24 s contra 4.04 s en secuencia. La celda 4.1 usa `Semaphore(32)`, pero con $n=20<32$ ninguna tarea se queda sin permiso: es `gather` sin tope en la práctica, y $T\approx\max_i d_i\approx0.2$ s más el costo del loop y de abrir conexiones.

**Arquitectura: *scatter-gather*.**

| | |
|---|---|
| Qué es | un agregador recibe una petición, la reparte entre $n$ servicios o particiones (*scatter*) y combina las respuestas (*gather*) |
| Cuándo sí | las $n$ llamadas son **independientes** y $n$ tiene una cota conocida y pequeña: un tablero que pide ventas, inventario y clima; una consulta repartida entre fragmentos |
| Cuándo no | la llamada 2 necesita el resultado de la 1 (un `id`, un token): eso es una cadena de `await`; $n$ sin cota (la lista viene del usuario o de otra API): `gather` crea las $n$ tareas de golpe |
| Qué cuesta | $T$ es la **más lenta** de las $n$: una sola respuesta lenta retrasa a todas; hay que decidir qué hacer si una falla (resultado parcial o error) |
| Sistema real | Elasticsearch reparte cada búsqueda entre los fragmentos (*shards*) del índice y fusiona sus resultados en el nodo que recibió la consulta |

Si una falla debe cancelar a las demás, `gather` no lo hace por omisión; `asyncio.TaskGroup` (Python 3.11+) sí cancela las restantes en cuanto una lanza excepción.

## 500 llamadas sin tope

::: definition {#cmp-def-tope-concurrencia title="Tope de concurrencia"}
Un **tope de concurrencia** $k$ es el máximo de tareas que pueden estar **en vuelo a la vez** dentro de una frontera (por ejemplo, «llamadas a esta API que ya salieron y no han regresado»). Sin tope, `gather` sobre $n$ llamadas pone las $n$ en vuelo en el mismo tick.
:::

**Otro ángulo.** Qué cuesta cada una de las 500 llamadas, y a quién:

| Dónde | Qué ocupa una llamada en vuelo | Con 500 a la vez |
|---|---|---|
| el cliente: la corrutina | unos KB de memoria; la cambia el loop, no el sistema operativo | barato: 500 o 5000 corrutinas caben |
| el cliente: el socket | un descriptor de archivo y una conexión TCP | Linux suele dar 1024 descriptores por proceso (`ulimit -n`); con miles: `Too many open files` |
| la red | un puerto local y una conexión en la tabla del sistema | con decenas de miles, se agotan los puertos locales |
| el servidor de la clase | **un hilo por conexión, sin tope** (`ThreadingHTTPServer`, ver [[secuencial-concurrente-paralelo]]) | 500 hilos del servidor durmiendo a la vez |
| una base de datos | un proceso o una conexión del servidor | PostgreSQL acepta 100 conexiones por omisión (`max_connections`); la 101 recibe error |
| una API pública | un lugar en su cola | responde `429` o `503`, o tarda más para todos |

`httpx.AsyncClient` ya trae un tope propio: 100 conexiones por omisión. Sin semáforo, las 400 tareas sobrantes no fallan de inmediato, pero quedan formadas en el pool del cliente; eso se ve en [[pools-y-recursos]].

**Ejemplo.** El servidor de la clase duerme 0.2 s por llamada y aguanta 500 hilos dormidos. Uno real que hace trabajo por petición (consulta su BD, calcula) no: más conexiones simultáneas no le dan más capacidad, sólo más cola y más latencia para todos.

**Arquitectura: concurrencia acotada.** Toda llamada a algo externo lleva un tope explícito. El tope lo fija **el que recibe** (cuánto acepta el servidor, la BD, el proveedor), no el que manda. Que el cliente pueda crear 5000 corrutinas no es un argumento.

## `Semaphore(k)` y el estado bloqueada

::: definition {#cmp-def-semaforo title="Semáforo"}
Un **semáforo** es un contador de permisos que empieza en $k$, más una cola de tareas que esperan:

- **acquire** (entrar): si el contador es mayor que 0, le resta 1 y la tarea sigue; si vale 0, la tarea se forma al final de la cola y se suspende.
- **release** (salir): suma 1 y despierta a la **primera** de la cola, que vuelve a restar 1 y entra.

`async with sem:` hace acquire al entrar al bloque y release al salir, **también si el bloque lanza excepción**. El semáforo cuenta permisos; no guarda conexiones ni objetos.
:::

::: definition {#cmp-def-bloqueada title="Bloqueada"}
**En palabras.** La tarea está bloqueada cuando espera algo que otra tarea del mismo programa tiene que soltar o producir: un permiso, un `Lock`, una conexión del pool, un resultado.

**Formalmente.** $\operatorname{blocked}(\tau)\subseteq\operatorname{vida}(\tau)$ y $b=\operatorname{dur}(\operatorname{blocked}(\tau))$. ([[notacion-computo]])

Una tarea está **bloqueada**, $t\in\operatorname{blocked}(\tau)$, si no avanzaría aunque le dieras CPU, y lo que le falta lo tiene que soltar o producir **otra tarea del mismo programa**: un permiso del semáforo, un `Lock`, una conexión del pool, el resultado de otra tarea. Se distingue de la espera de red (`wait`), que depende de algo externo, y de lista (`ready`), que sólo necesita turno. Con $b=\operatorname{dur}(\operatorname{blocked})$, la vida queda partida en cuatro: $d=e+w+r+b$.
:::

**Otro ángulo.** El flujo de una tarea por el semáforo, y el Gantt de 8 tareas con $k=3$:

::: figure {#cmp-flujo-semaforo title="acquire y release: un contador y una cola"}
![Diagrama de flujo de una tarea que llega a async with sem. Primero una decisión: si el contador de permisos es mayor que cero, se le resta uno y la tarea entra al bloque para hacer su llamada de red; si vale cero, la tarea se forma al final de la cola de espera del semáforo y queda bloqueada. Al salir del bloque, release suma uno al contador y despierta a la primera tarea de la cola, que resta uno y entra. Un recuadro muestra el contador con k igual a 3 y la cola en orden de llegada.](_assets/cmp-flujo-semaforo.svg)
:::

::: figure {#cmp-gantt-semaforo title="8 tareas, 3 permisos: la franja «espera permiso» no es espera de red"}
![Diagrama de Gantt de 8 tareas iguales con un semáforo de 3 permisos. Las tres primeras toman permiso de inmediato y hacen su llamada: un tramo corto de ejecución y uno largo de espera de red. Las otras cinco aparecen con una franja ámbar de espera de permiso, que es el estado bloqueada, dibujada distinta de la espera de red. Cada vez que una tarea termina y suelta su permiso entra la primera de la cola, de modo que en ningún instante hay más de tres tareas dentro del bloque y la entrada avanza como una ventana deslizante, no en tandas fijas.](_assets/cmp-gantt-semaforo.svg)
:::

- **Ámbar (bloqueada)** = el semáforo dice «no hay lugar». Lo resuelve otra tarea al soltar.
- **Contorno (espera red)** = la tarea ya está dentro y la respuesta no ha llegado. Lo resuelve el servidor.
- Un trazo vertical nunca corta más de 3 tareas dentro del bloque: $L_{\text{dentro}}(t)\le k$.

**Matemática.** Dentro del bloque hay a lo más $k$ tareas en cada instante. Si cada tarea retiene su permiso $e+w$, el tiempo total de permisos ocupados es $\sum_i(e_i+w_i)$ y hay $k$ permisos:

$$T\;\ge\;\frac{\sum_i(e_i+w_i)}{k},\qquad\text{y con }n\text{ tareas iguales:}\qquad T\;\ge\;\left\lceil n/k\right\rceil\cdot(e+w)$$

La segunda es más fuerte: algún permiso atiende por lo menos $\lceil n/k\rceil$ tareas una tras otra. Es cota inferior: listas, arranque y costos del loop se suman encima.

**Ejemplo.** El ejemplo único con `Semaphore(2)`: la cota da $\lceil3/2\rceil\times240=480$ ms, contra 280 sin tope. La traza ilustrativa (B bloqueada; la última fila cuenta permisos libres):

| | 0–20 | 20–40 | 40–220 | 220–240 | 240–260 | 260–280 | 280–460 | 460–480 |
|---|---|---|---|---|---|---|---|---|
| τ1 | E | W | W | E | — | — | — | — |
| τ2 | R | E | W | W | R | E | — | — |
| τ3 | R | R | B | B | E | W | W | E |
| hilo del loop | τ1 | τ2 | ocioso | τ1 | τ3 | τ2 | ocioso | τ3 |
| permisos libres | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |

1. $\tau_1$ toma permiso en 0, $\tau_2$ en 20. En 40, $\tau_3$ por fin tiene turno, encuentra el contador en 0 y se forma: $\operatorname{blocked}(\tau_3)=[40,240)$.
2. En 240, $\tau_1$ sale: release suma 1 y despierta a $\tau_3$, que resta 1. El contador se queda en 0 y el permiso cambia de dueño.
3. Partición de $\tau_3$: $e=40$, $w=200$, $r=40$, $b=200$; $d=480$. Aquí la cota se alcanza exacta: $T=480$.

**Arquitectura: *backpressure*.**

| | |
|---|---|
| Qué es | cuando el lado de abajo está lleno, el de arriba **espera** en vez de mandar más; con el semáforo, la espera es el estado `blocked` de las tareas formadas |
| Cuándo sí | siempre que produces trabajo más rápido de lo que la dependencia lo atiende: un *scraper*, un ETL que baja páginas de una API, un consumidor de una cola |
| Cuándo no | cuando no puedes hacer esperar a quien produce (un sensor que no se detiene): ahí toca descartar o rechazar (`429`, `503`) |
| Qué cuesta | latencia para las formadas; y con `gather` las $n$ corrutinas **ya existen** en memoria aunque estén bloqueadas: el semáforo limita a las que están en vuelo, no a las que se crearon |
| Sistema real | `asyncio.Queue(maxsize=…)`: `put` bloquea cuando la cola está llena (se ve en el notebook); la cola `listen` del servidor de la clase (1024) es el mismo límite en el kernel |

## Ventana deslizante, no tandas

::: definition {#cmp-def-ventana-deslizante title="Ventana deslizante"}
Con un semáforo de $k$ permisos, **en cuanto una tarea suelta su permiso entra la siguiente de la cola**. El conjunto de tareas dentro del bloque es una ventana de ancho $k$ que avanza tarea por tarea. Partir la lista en tandas de $k$ y hacer `gather` de cada tanda es otra cosa: la tanda siguiente no empieza hasta que termina **la más lenta** de la anterior.
:::

**Otro ángulo.** Con tareas iguales los dos dibujos coinciden y se ven «olas»; con duraciones distintas se separan:

| | Ventana deslizante (`Semaphore(k)`) | Tandas (`gather` de $k$ en $k$) |
|---|---|---|
| Quién entra | la primera de la cola, en cuanto se libera **un** permiso | las $k$ siguientes, cuando terminan **todas** las de la tanda |
| Permisos ociosos | ninguno mientras haya cola | todos los que ya terminaron, esperando a la más lenta |
| Una llamada lenta | retiene **un** permiso; los otros $k-1$ siguen girando | detiene a las $k$ |
| $T$ | $\ge\max\!\big(\sum_i(e_i+w_i)/k,\ \max_i(e_i+w_i)\big)$ | $\sum_{\text{tandas}}\max_{i\in\text{tanda}}(e_i+w_i)$ |

**Matemática.** Cuenta ilustrativa (duraciones supuestas): 500 llamadas, $k=32$; 484 tardan 0.2 s y 16 tardan 2 s, una en cada tanda de 32.

- Tandas: 16 tandas, cada una espera a su lenta: $16\times2=32$ s.
- Ventana: $\sum_i(e_i+w_i)=484\times0.2+16\times2=128.8$ s de permiso; $128.8/32\approx4.0$ s es la cota, y las 16 lentas caben en paralelo dentro de la ventana.

**Ejemplo.** Con las 500 llamadas iguales de la celda 4.1, $\lceil500/32\rceil=16$: 15 vueltas completas de 32 y una de 20. La cota $16\times0.2=3.2$ s se compara abajo con lo medido.

**Arquitectura.** Para acotar, un semáforo alrededor de la llamada, no un `for` que parte la lista en trozos. El bloque `async with sem:` envuelve **sólo** la llamada a la dependencia: parsear, guardar o calcular dentro del bloque retiene el permiso sin usar el servidor.

## La cota contra la medición

**Otro ángulo.** El mismo tope de 32 en los dos modelos: hilos con `ThreadPoolExecutor(max_workers=32)` (página 2) y `asyncio` con `Semaphore(32)` y `httpx.Limits(max_connections=32)` (celda 4.1). La cota es $\lceil n/32\rceil\times0.2$ s.

| Llamadas | Secuencial | Cota $\lceil n/32\rceil\cdot0.2$ | Hilos, tope 32 | `asyncio`, tope 32 |
|---:|---:|---:|---:|---:|
| 20 | 4.04 s (medido) | 0.2 s | 0.23 s | 0.24 s |
| 100 | ≈ 20 s (calculado, no medido) | 0.8 s | 0.82 s | 0.89 s |
| 500 | ≈ 100 s (calculado, no medido) | 3.2 s | 3.32 s | 3.39 s |

- Ninguna medición baja de su cota: la cuenta predice el orden de magnitud **antes** de correr nada.
- Con el mismo tope, hilos y `asyncio` quedan cerca: **el tiempo lo fija la concurrencia permitida, no el modelo.** Son una corrida en la máquina del profesor; tus cifras cambian, la forma no.
- Lo que separa a los modelos es el costo por tarea en vuelo (un hilo contra una corrutina) cuando $k$ crece a cientos o miles, no el tiempo con $k=32$.

## La Ley de Little

::: definition {#cmp-def-ley-de-little title="Ley de Little"}
**En palabras.** En régimen estable, las tareas en vuelo en promedio son el rendimiento por el tiempo medio que cada una pasa dentro de la frontera elegida.

**Formalmente.** $L=\lambda\cdot W$; si a lo más $k$ caben dentro, $L\le k$ y $\lambda\le k/W$. ([[notacion-computo]])

En un sistema en régimen estable, con una frontera que eliges, **las tareas en vuelo en promedio** ($L$) son el **rendimiento** ($\lambda$, tareas que terminan por segundo) por el **tiempo medio que cada una pasa dentro** ($W$):

$$L=\lambda\cdot W$$

Si a lo más $k$ caben dentro, $L\le k$, y por tanto $\lambda\le k/W$. No supone nada sobre el orden de atención ni sobre la distribución de los tiempos.
:::

**Otro ángulo.** La frontera es «dentro del bloque `async with sem`». Lo que entra es una tarea que obtuvo permiso; lo que sale, una que lo soltó.

| Símbolo | En las 500 llamadas |
|---|---|
| $k$ | 32 permisos |
| $W$ | tiempo con permiso: ≈ 0.2 s (lo que duerme el servidor, más la red local) |
| $\lambda$ | llamadas que terminan por segundo |
| $L$ | permisos ocupados en promedio |

**Matemática.** Con los números del lote de 500 (medición de referencia: 3.32 s con hilos, 3.39 s con `asyncio`):

1. Techo: $\lambda\le k/W=32/0.2=160$ llamadas/s, así que $T\ge500/160=3.125$ s.
2. La cota del semáforo es más fuerte, $\lceil500/32\rceil\times0.2=3.2$ s, porque la última vuelta lleva 20 tareas y deja 12 permisos ociosos.
3. Rendimiento medido: $\lambda=500/3.32\approx151$/s con hilos y $500/3.39\approx147$/s con `asyncio`.
4. Ocupación: $L=\lambda W\approx151\times0.2\approx30$ de 32 permisos ocupados en promedio. El tope está casi lleno todo el tiempo: subir $k$ es lo único que sube $\lambda$, mientras el servidor aguante.

**Ejemplo.** Al revés, para dimensionar: si necesitas 400 llamadas/s a una API con $W=0.2$ s, hacen falta $L=400\times0.2=80$ en vuelo, así que $k\ge80$. Si el proveedor sólo acepta 32 simultáneas, el techo es 160/s con cualquier modelo de concurrencia.

**Arquitectura: dimensionar $k$.**

| | |
|---|---|
| Qué es | elegir el tope con lo que **acepta el que recibe**, medido o documentado, y comprobar con Little qué rendimiento da |
| Cómo se mide | subir $k$ paso a paso (8, 16, 32, 64…) y graficar $T$ y la latencia por llamada: mientras $T$ baje cerca de $\lceil n/k\rceil W$, el servidor aguanta; cuando $T$ deja de bajar o la latencia por llamada sube, pasaste lo que acepta |
| Cuándo no basta | si $W$ cambia (la dependencia se pone lenta), el mismo $k$ da otro $\lambda$: con $W=2$ s y $k=32$, $\lambda\le16$/s |
| Qué cuesta | un $k$ adivinado: chico, desperdicia capacidad; grande, satura al otro lado y la latencia de todos sube |
| Sistema real | el $k=32$ de esta página, comprobado contra la tabla de arriba: ninguna medición baja de su cota y todas quedan cerca de ella |

## Tres topes que se confunden

::: definition {#cmp-def-rate-limit title="Rate limit"}
Un **rate limit** es un tope sobre $\lambda$: cuántas peticiones **por unidad de tiempo** acepta el proveedor, normalmente por cliente o por token. Lo que excede recibe `429 Too Many Requests`, a veces con un header `Retry-After` que dice cuántos segundos esperar.
:::

**Otro ángulo.**

| Tope | Acota | Herramienta | Qué no evita |
|---|---|---|---|
| de concurrencia | $L$: cuántas en vuelo | `Semaphore(k)`, `max_workers` | un `429`: con $W$ chico, $k/W$ puede rebasar la cuota |
| de tasa (*rate limit*) | $\lambda$: cuántas por segundo | un limitador de tasa (cubeta de fichas) del lado del cliente, y respetar `Retry-After` | tener 500 conexiones abiertas a la vez |
| de recursos reales | conexiones, hilos, procesos que existen | un pool: `httpx.Limits`, `ThreadPoolExecutor` | nada de lo anterior por sí solo; se ve en [[pools-y-recursos]] |

**Matemática.** El tope de concurrencia da $\lambda\le k/W$, que **depende de $W$**. Con $k=32$: si $W=0.2$ s, $\lambda\le160$/s; si las respuestas salen de un caché y $W=0.02$ s, $\lambda\le1600$/s. Un proveedor con cuota de 10 peticiones/s (cifra supuesta) responde `429` en los dos casos.

**Ejemplo.** La API de GitHub documenta un límite de 5000 peticiones por hora para un usuario autenticado: es tasa, no concurrencia. Con `Semaphore(32)` y $W=0.2$ s puedes llegar a 160/s y agotar la hora en poco más de 30 s.

**Arquitectura: *bulkhead*, un semáforo por dependencia.**

| | |
|---|---|
| Qué es | un tope separado por dependencia (`sem_api_a = Semaphore(10)`, `sem_bd = Semaphore(5)`), para que una dependencia lenta sólo agote **sus** permisos |
| Por qué | con un tope global compartido, Little reparte los permisos según $W$. Cuenta ilustrativa: dos APIs con el mismo $\lambda$; si A pasa de 0.2 a 2 s, $L_A/L_B=W_A/W_B=10$, y A retiene $10/11\approx91\,\%$ de los 32 permisos (unos 29). B, que está sana, se queda con unos 3 |
| Cuándo sí | varias dependencias externas de distinta confiabilidad en el mismo proceso |
| Cuándo no | una sola dependencia: un tope basta |
| Qué cuesta | topes mal repartidos dejan permisos ociosos en una dependencia mientras otra tiene cola |
| Sistema real | Hystrix, de Netflix (hoy en mantenimiento), lo popularizó con un pool de hilos por dependencia; Resilience4j lo ofrece como `Bulkhead` |

## Cuándo no usar `gather`

| Situación | Por qué no | Qué va |
|---|---|---|
| la llamada 2 necesita el resultado de la 1 | no son independientes: el fan-out no tiene qué repartir | `await` en cadena; `gather` sólo en los tramos independientes |
| $n$ sin cota (millones de URLs, un flujo que no termina) | crea las $n$ tareas en memoria aunque el semáforo deje pasar $k$ | una cola acotada y $k$ trabajadores que toman de ella (notebook, tema 4; página 8) |
| una falla debe detener todo | `gather` no cancela a las demás | `asyncio.TaskGroup` |
| el trabajo calcula en vez de esperar | el loop no solapa cálculo | procesos ([[calcular-en-paralelo]]) |

## La decisión hasta aquí

| Página | Pregunta | Regla |
|---|---|---|
| 1 | ¿dónde pasa el tiempo? | medir $\operatorname{exec}$ contra $\operatorname{wait}$ con la tarea sola; si domina la espera, reorganizar esperas |
| 2 | ¿pocas decenas de esperas con una librería bloqueante? | hilos, con `max_workers` como tope |
| 3 | ¿cientos de esperas con un cliente asíncrono? | `asyncio` con `gather`; nada que bloquee dentro del loop |
| **4** | **¿muchas esperas independientes contra una dependencia finita?** | **`gather` + `Semaphore(k)`, con $k$ medido contra lo que acepta el servidor; $\lambda\le k/W$** |
| **4** | **¿varias dependencias?** | **un semáforo por dependencia (*bulkhead*)** |
| **4** | **¿el proveedor tiene cuota por tiempo?** | **además del tope, un limitador de tasa y respetar `429` / `Retry-After`** |
| **4** | **¿$n$ sin cota?** | **cola acotada + $k$ trabajadores, no `gather`** |

## Código

La celda 4.1 repite el lote de 20, 100 y 500 llamadas con un tope de 32 y deja comparar cada tiempo con su cota. La 4.2, opcional, muestra el orden de los resultados y qué pasa cuando una falla.

**Haz (celda 4.1):** 20, 100 y 500 llamadas a `/ventas?lento=0.2`, con a lo más 32 en vuelo.

```python
import asyncio, time, httpx
from cable import URL
async def pide(cliente, sem):
    async with sem:  # toma un permiso; si no hay, la tarea queda bloqueada en la cola
        return (await cliente.get(f"{URL}/ventas?lento=0.2")).status_code  # cede el hilo durante la espera

async def lote(n):
    sem = asyncio.Semaphore(32)  # 32 permisos: a lo más 32 dentro del bloque
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=32), timeout=30) as cliente:  # pool con el mismo tope
        return await asyncio.gather(*(pide(cliente, sem) for _ in range(n)))  # n tareas; resultados en orden

for n in (20, 100, 500):
    inicio = time.perf_counter()
    codigos = await lote(n)  # await de nivel superior: el notebook ya tiene un loop corriendo
    print(f"{n:>3} llamadas, asyncio con 32: {time.perf_counter() - inicio:5.2f} s  ({set(codigos)})")
```

**Python que quizá no has visto:**

| Construcción | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `async with sem:` | llama a `acquire` al entrar y a `release` al salir del bloque, también si hay excepción o `return` | garantiza que el permiso vuelve; con `acquire`/`release` a mano, una excepción entre los dos pierde un permiso para siempre |
| `gather(*(… for _ in range(n)))` | el generador produce $n$ corrutinas y `*` las pasa como $n$ argumentos separados | `gather` recibe argumentos sueltos, no una lista |
| `httpx.AsyncClient` | cliente HTTP cuyo `get` es una corrutina: se espera con `await` y cede el hilo | `requests.get` bloquearía el hilo del loop y las 500 irían en serie |
| `httpx.Limits(max_connections=32)` | tope de conexiones abiertas del pool del cliente (por omisión, 100) | iguala el tope de conexiones reales al de permisos; la diferencia entre los dos es tema de [[pools-y-recursos]] |
| `timeout=30` | máximo para conectar, leer, escribir y conseguir conexión del pool (por omisión, 5 s) | da margen a un lote largo; sin timeout, una llamada colgada retendría su permiso para siempre |

**Qué pasó:** cada tiempo contra su cota $\lceil n/32\rceil\times0.2$ s.

| $n$ | $\lceil n/32\rceil$ | Cota | Medido |
|---:|---:|---:|---:|
| 20 | 1 | 0.2 s | 0.24 s |
| 100 | 4 | 0.8 s | 0.89 s |
| 500 | 16 | 3.2 s | 3.39 s |

`{200}` es el conjunto de códigos de estado: las $n$ respondieron 200. Con 20, el semáforo no hizo esperar a nadie; con 500, cada tarea pasó en promedio la mayor parte del lote bloqueada en la cola del semáforo y sólo ≈ 0.2 s dentro.

**Deberías ver:**

```text
 20 llamadas, asyncio con 32:  0.24 s  ({200})
100 llamadas, asyncio con 32:  0.89 s  ({200})
500 llamadas, asyncio con 32:  3.39 s  ({200})
```

**Haz (celda 4.2, opcional):** tres llamadas en una sola `gather`; la segunda pide una venta que no existe.

```python
import asyncio, httpx
from cable import URL

async def pide(cliente, ruta):
    r = await cliente.get(f"{URL}{ruta}")
    r.raise_for_status()  # un 404 se vuelve excepción (httpx no lo hace solo)
    return r.status_code

rutas = ["/ventas?lento=0.3", "/ventas/99999?lento=0.1", "/ventas?lento=0.2"]
async with httpx.AsyncClient(timeout=30) as cliente:
    res = await asyncio.gather(*(pide(cliente, r) for r in rutas), return_exceptions=True)  # la excepción ocupa su lugar
for ruta, x in zip(rutas, res):
    print(f"{ruta:<24} {x if isinstance(x, int) else type(x).__name__}")
```

**Python que quizá no has visto:**

| Construcción | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `return_exceptions=True` | la excepción de una tarea se devuelve como un elemento más de la lista | sin él, `await gather` lanzaría la del 404 a los 0.1 s y perderías los otros dos resultados en esa línea |
| `async with` de nivel superior | abre y cierra el cliente dentro de la celda, con el loop del notebook | igual que `await` suelto: en un `.py` iría dentro de una `async def` llamada con `asyncio.run` |

**Qué pasó:** la segunda llamada terminó primero (0.1 s) y aun así aparece en el segundo lugar: la lista sigue el orden de los argumentos. Su error quedó en la lista como objeto `HTTPStatusError`; las otras dos completaron. Sin `return_exceptions=True`, la excepción habría salido del `await` a los 0.1 s; las otras dos tareas no se cancelan, quedan sueltas y nadie recoge su resultado.

**Deberías ver:**

```text
/ventas?lento=0.3        200
/ventas/99999?lento=0.1  HTTPStatusError
/ventas?lento=0.2        200
```

La versión larga y paso a paso está en el notebook, tema 4.

## Al diseñar / al revisar código de IA, busca…

- **`gather` sobre una lista que viene de fuera sin `Semaphore`**: pone $n$ llamadas en vuelo a la vez. Pregunta cuánto acepta el servidor y dónde está el tope.
- **Un `Semaphore` creado dentro de la función que llama cada tarea**: cada tarea tiene su propio semáforo y el tope no existe. Debe ser uno, compartido.
- **El tope partido en tandas** (`for trozo in trozos: await gather(*trozo)`): cada tanda espera a su más lenta. Pide un semáforo.
- **`acquire()` sin `release()` en un `finally`**: una excepción se queda con el permiso. Pide `async with sem:`; `BoundedSemaphore` lanza `ValueError` si alguien suelta de más.
- **Trabajo de más dentro de `async with sem:`** (parsear, escribir a disco, calcular): retiene el permiso sin usar el servidor.
- **Un `Semaphore(k)` presentado como protección contra `429`**: acota $L$, no $\lambda$. Si la API documenta una cuota por tiempo, hace falta un limitador de tasa.
- **Un solo tope para varias dependencias**: una lenta se lleva los permisos de las demás. Pide un semáforo por dependencia.
- **Un $k$ sin justificación** (`Semaphore(1000)`, `max_connections=500`): pide la medición o la cifra documentada del servidor, y la cuenta $\lambda\le k/W$.
- **`gather` sin decidir qué pasa si una falla**: por omisión propaga la primera excepción y las demás siguen; ¿se quería `return_exceptions=True` o `TaskGroup`?

Sigue con [[pools-y-recursos]].
