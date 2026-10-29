---
id: componer-un-servidor
title: "Componer un servidor"
nav_title: "Componer un servidor"
summary: "Cada worker crea su pool local, def y async def se ejecutan en sitios distintos y los topes locales se multiplican: de una configuración se calculan procesos, hilos y conexiones."
status: ready
estimated_time: 25m
tags: [worker, replica, pool, fastapi, anyio, async, postgres, pgbouncer, conexiones]
prerequisites: [pools-y-recursos, asincrono-y-el-event-loop, concurrencia-acotada]
---

# Componer un servidor

**Página 11 · Cómputo y concurrencia** · Pregunta: **de una configuración, ¿cuántos procesos, hilos y conexiones resultan?** · Respuesta: **cada worker, un proceso que atiende peticiones, crea su pool local de conexiones. `async def` corre en un hilo y `def` en hilos aparte. Los topes locales se multiplican.**

Un **proceso** es un programa en ejecución con memoria propia y al menos un hilo. $N$ representa los trabajadores y $k$ el tope real de permisos, conexiones o procesos, según [[notacion-computo]]. Consulta el dimensionamiento en [[pools-y-recursos]].

## A. El pool local de cada worker

**Términos.**

| Término | Definición |
|---|---|
| Worker | Un **worker** es un proceso que atiende peticiones con su propio hilo para tareas `async` o con otros hilos. |
| Réplica | Una **réplica** es una copia del servicio en otra máquina o en un entorno aislado llamado contenedor. |
| Balanceador | Un **balanceador** es el programa que reparte las peticiones entre las réplicas. |
| Backend | Un **backend** de Postgres es el proceso del servidor de bases de datos que atiende una conexión. |

**Definición.** Un **pool local** es el conjunto de conexiones que crea y usa un worker.

**Figura.**

::: figure {#cmp-ancla-servidor title="Cada worker tiene su loop y su pool; cada conexión directa es un backend de Postgres"}
![Ruta de una petición: cliente, balanceador, réplica con N workers, cada uno con loop y pool local, y una conexión al servidor Postgres por cada conexión del pool](_assets/cmp-ancla-servidor.svg)
:::

Cómo leerla: cuenta el pool resaltado. PgBouncer (un programa intermedio que reutiliza pocas conexiones a Postgres para muchos clientes) recibe conexiones de clientes y mantiene menos conexiones con Postgres. Cuéntalas por separado.

**Cuenta.** Las conexiones abiertas, las consultas activas y la CPU usada son cantidades distintas. Cada conexión directa a Postgres tiene un backend, aunque esté ociosa. Una consulta puede usar varios trabajadores paralelos del servidor. Ninguna cifra se deduce de otra.

**Ejemplo.** Un pool de 10 conexiones abiertas, con 2 ejecutando consultas, produce 10 backends y 2 consultas activas (supuesto del ejemplo).

**Arquitectura.**

- **Qué es:** el pool pertenece al proceso que lo creó.
- **Cuándo sí:** el worker es el dueño único de sus conexiones.
- **Cuándo no:** no supongas que varios procesos comparten un pool. Compartirlo entre hilos depende de la biblioteca.
- **Qué cuesta:** cada worker añade su pool a la cuenta del servidor.
- **Sistema real:** Postgres crea un backend por conexión directa. Una transacción reúne varias operaciones. En modo transacción, PgBouncer comparte menos backends entre más clientes. También respeta su propio `max_client_conn`.

Decisión: suma los pools de todos los workers al dimensionar el servidor.

## B. `async def`, `def` y esperar sin bloquear

**Términos.**

| Término | Definición |
|---|---|
| Loop | El **loop** es el único hilo que ejecuta las tareas `async` de un worker, una a la vez. |
| Bloquear / ceder | Una espera **bloquea** si el hilo queda dormido; **cede** si lo libera para atender otras tareas mientras espera. |
| Limitador de hilos | El **limitador de hilos** restringe cuántos hilos usa FastAPI para funciones `def`. AnyIO administra esos hilos. Ofrece $k_h=40$ **tokens** configurables por loop; cada token reserva un hilo. |
| Latido | El **latido** es un tic que el servidor anota cada 10 ms para comprobar que el loop sigue vivo. |

**Definición.** Un **endpoint** es la función que responde a una dirección del servidor. FastAPI ejecuta un endpoint `async def` en el **loop**. Ejecuta un endpoint `def` en un hilo del limitador. El resultado depende de si la espera bloquea o cede.

**Figura.**

::: figure {#cmp-async-vs-def title="Lo que cuenta no es async o def, sino si la espera bloquea el hilo o lo cede"}
![Tres paneles con 12 peticiones de 0.5 s: async def con time.sleep tarda 6 s porque el loop se bloquea y el latido se detiene; def con time.sleep tarda 0.5 s porque cada petición usa su hilo; async def con await asyncio.sleep tarda 0.5 s porque await cede el hilo](_assets/cmp-async-vs-def.svg)
:::

Cómo leerla: cada fila es una petición; la última fila de cada panel muestra el latido. Los tics indican que el loop sigue vivo.

::: definition {#cmp-def-srv-tiempo-espera title="Tiempo de n peticiones simultáneas que esperan"}
**Qué dice.** El tiempo total de un lote de peticiones que solo esperan depende de si la espera bloquea el hilo, de si cada petición usa un token del limitador o de si la espera cede el hilo.

**Variables.**

- $n$: número de peticiones simultáneas (peticiones).
- $w$: cuánto espera cada petición sola (s).
- $k_h$: tokens del limitador de hilos, es decir, cuántas funciones `def` pueden correr a la vez (40 por omisión en AnyIO).
- $T$: tiempo total hasta que termina la última petición (s).

**Fórmulas.**

$$T_{\text{async + sleep}} \approx n\,w$$

$$T_{\text{def}} \approx \left\lceil \frac{n}{k_h} \right\rceil w$$

$$T_{\text{async + await}} \approx w$$

**Por qué es así.**

- `async def` con `time.sleep`: el loop es un solo hilo y `sleep` lo duerme. La petición 2 no empieza hasta que termina la 1, así que las esperas se suman: $n$ veces $w$.
- `def`: cada petición ocupa un token y un hilo, y todas duermen a la vez. Caben $k_h$ por ronda. La división $n/k_h$ cuenta las rondas y el techo $\lceil\ \rceil$ las redondea hacia arriba, porque una ronda incompleta cuesta una ronda entera. Cada ronda dura $w$.
- `async def` con `await asyncio.sleep`: `await` cede el hilo, así que el loop atiende a las demás mientras esperan. Todas esperan juntas y el total es una sola espera, $w$.
:::

**Ejemplo paso a paso.**

1. **Datos.** $n=12$, $w=0{,}5$ s, $k_h=40$.
2. **`async def` con `sleep`.** $12\times0{,}5=6$ s.
3. **`def`.** $\lceil 12/40\rceil=\lceil 0{,}3\rceil=1$ ronda, así que $1\times0{,}5=0{,}5$ s.
4. **`async def` con `await`.** $w=0{,}5$ s.
5. **Contraste con lo medido.** 6,02 s, 0,53 s y 0,52 s: las fórmulas son aproximaciones y los medidos añaden milésimas de arranque.
6. **Lectura.** Si $n$ superara $k_h$ (por ejemplo $n=100$), `def` pasaría a $\lceil 100/40\rceil=3$ rondas, 1,5 s, mientras `await` seguiría en 0,5 s.

**Medición (D1, celda 11.1).** Un worker recibe 12 peticiones simultáneas que esperan 0.5 s, en tres versiones:

| Versión | Dónde corre | Qué pasa | Total medido | Hueco máximo del latido |
|---|---|---|---|---|
| `def` con `time.sleep` | un hilo por petición | las 12 duermen a la vez | 0.53 s | 0.01 s |
| `async def` con `time.sleep` | el loop, un solo hilo | `sleep` bloquea el hilo: una petición a la vez | 6.02 s | 6.01 s |
| `async def` con `await asyncio.sleep` | el loop | `await` cede el hilo: el loop atiende a las otras mientras esperan | 0.52 s | 0.01 s |

El **hueco máximo** es el intervalo más largo sin tics. Indica cuánto tiempo estuvo bloqueado el loop. Con `async def` y `time.sleep`, nadie más fue atendido durante casi todo el total. Medido en 8 CPU.

**Arquitectura.**

- **Qué es:** FastAPI ejecuta las funciones `def` en hilos del limitador y las `async def` en el loop.
- **Cuándo sí:** usa `async def` con `await` para esperas. Usa `def` para bibliotecas que bloquean y no permiten `await`.
- **Cuándo no:** nunca pongas `time.sleep` ni una consulta sin `await` dentro de una `async def`. Bloquearías el loop del worker. Un `def` llamado directamente desde una `async def` tampoco pasa a otro hilo.
- **Qué cuesta:** cada `def` en ejecución ocupa un token. Si faltan tokens, las demás funciones esperan. Los hilos ociosos no cuentan.
- **Sistema real:** FastAPI usa AnyIO mediante Starlette, su base para atender peticiones. Todo corre sobre uvicorn, el programa que ejecuta la aplicación.

Decisión: identifica si la espera bloquea el hilo. Si bloquea, usa `def`; si admite `await`, usa `async def`.

## C. Presupuesto de conexiones

**Definición.** El **presupuesto de conexiones** es el máximo de conexiones que tu servicio puede abrir contra un servidor.

Dos términos del servidor: `max_connections` es el tope de conexiones simultáneas que acepta Postgres. Las **plazas reservadas** son las conexiones de ese tope guardadas para superusuarios (`superuser_reserved_connections`, 3 por omisión), de modo que quien administra pueda entrar aunque el servicio llene el resto.

::: definition {#cmp-def-srv-presupuesto title="Presupuesto de conexiones"}
**Qué dice.** Cada réplica tiene varios workers y cada worker su propio pool, así que el máximo de conexiones es un producto, no una suma.

**Variables.**

- $R$: número de réplicas (copias del servicio).
- $N$: workers por réplica (procesos).
- $k$: conexiones máximas del pool de un worker (conexiones).
- $M$: `max_connections` de Postgres (conexiones).
- $s_{\text{su}}$: plazas reservadas para superusuarios (conexiones).

**Fórmula.**

$$R\times N\times k \;\le\; M - s_{\text{su}}$$

**Por qué es así.**

- $k$ es el tope de un solo pool, y un pool pertenece a un solo worker.
- Cada réplica tiene $N$ workers, cada uno con su pool: $N\times k$ por réplica.
- Hay $R$ réplicas iguales: se multiplica otra vez por $R$.
- El lado derecho es lo que el servidor deja usar al servicio: el tope menos las plazas guardadas.
:::

**Figura (tabla).** Los valores son supuestos del ejemplo; el servidor es el mismo para todas.

| Concepto | Símbolo | Valor | Naturaleza |
|---|---|---|---|
| Réplicas | $R$ | 3 | supuesto |
| Workers por réplica | $N$ | 4 | supuesto |
| Máximo por pool | $k$ | 10 | supuesto |
| `max_connections` de Postgres | $M$ | 100 | supuesto (valor frecuente) |
| Plazas de superusuario | $s_{\text{su}}$ | 3 | supuesto |

**Ejemplo paso a paso.**

1. **Por réplica.** $N\times k=4\times10=40$ conexiones posibles.
2. **Por servicio.** $R\times40=3\times40=120$.
3. **Capacidad.** $M-s_{\text{su}}=100-3=97$.
4. **Comparación.** $120>97$: el exceso es $120-97=23$ (calculado).
5. **Lectura.** El presupuesto es capacidad potencial, no conexiones ya abiertas: el problema aparece solo si todos los pools se llenan a la vez. Las 97 suponen que no hay otros consumidores; `SHOW max_connections` comprueba $M$.

**Arquitectura.**

- **Qué es:** suma los topes locales de réplicas, workers y pools.
- **Cuándo sí:** calcúlalo antes de cambiar $R$, $N$ o $k$.
- **Cuándo no:** no estima consultas activas ni CPU.
- **Qué cuesta:** aumentar las réplicas multiplica las conexiones posibles, aunque cada pool no cambie ([[arquitectura-y-estrategia]]).
- **Sistema real:** Postgres limita conexiones con `max_connections`; usa PgBouncer si la cuenta supera al servidor.

Decisión: compara $R\times N\times k$ con la capacidad disponible antes de escalar el servicio.

## D. Workers y cores: `uvicorn --workers N`

**Definición.** Un **core** es una unidad de CPU que ejecuta un hilo a la vez. `uvicorn --workers N` arranca un proceso **supervisor** que lanza $N$ procesos worker. Cada worker tiene su propio loop, su propia memoria y su propio pool local. El supervisor es el proceso que tú lanzas, no atiende peticiones, y de él cuelgan los $N$ workers; con `--workers 1` no hay hijos y el servidor corre en el proceso principal.

::: definition {#cmp-def-srv-workers title="CPU que usa un servicio con N workers"}
**Qué dice.** Un worker es un proceso con un loop, y un loop corre código de Python en un hilo a la vez. Más workers permiten usar más CPU, hasta las que haya.

**Variables.**

- $N$: workers (procesos).
- $P$: CPU lógicas disponibles en la máquina (CPU).
- $p_{\text{ef}}$: cuántos cores trabajan de verdad a la vez. Es la misma idea de la página 10, el menor de los límites que dejan avanzar, con otros límites: aquí los workers y las CPU.

**Fórmula.**

$$p_{\text{ef}} \le \min(N,\,P)$$

**Por qué es así.**

- Cada worker aporta como mucho un hilo corriendo Python, y por eso como mucho un core.
- Con $N<c$ sobran cores; con $N>c$ los workers compiten por las $P$ que hay.
- Es una cota, no una promesa: un worker que espera (red, disco) no usa su core.
- La memoria de cada worker es suya, así que un contador o una caché en memoria **no se comparte** entre workers.
:::

**Ejemplo paso a paso.**

1. **Datos.** $N=2$ workers, $P=8$ CPU.
2. **Cota.** $\min(2,8)=2$: hasta 2 cores, aunque la máquina tenga 8.
3. **Verificación (celda 11.3).** Con 2 workers y una conexión nueva por petición, `/quien` devuelve 2 PID distintos. Un **PID** es el número que identifica a un proceso: dos PID distintos son dos procesos distintos.
4. **Reparto de conexiones.** El supervisor abre un solo punto de entrada y lo comparte con los workers; cada conexión nueva la toma uno de ellos. El worker se asigna a la **conexión**, no a la petición: un cliente con una sola conexión keep-alive (una misma conexión que se reutiliza para varias peticiones) cae siempre en el mismo worker (20 de 20 peticiones en un mismo PID); con conexiones nuevas se reparten (en la prueba, 11 y 9).
5. **Estado local.** Cada worker cuenta sus peticiones en su propio contador: los dos contadores suman el total y ninguno ve al otro.
6. **Cálculo.** Con 4 peticiones simultáneas de 300 ms de CPU (celda 11.3): 1 worker tarda cerca de 1.3 a 1.6 s, porque los hilos de Python puro se turnan por el GIL; 2 workers repartidos 2 y 2 tardan cerca de 0.7 a 0.9 s, casi la mitad. Si las 4 conexiones caen en 3 y 1, casi no mejora.
7. **Lectura.** Para compartir estado entre workers hace falta algo externo (base de datos, caché en otro proceso), no una variable.

## E. El pool de Postgres, visto desde el servidor

**Definición.** `pg_stat_activity` es la vista de Postgres con una fila por proceso del servidor. Para una conexión directa, esa fila es su backend.

::: definition {#cmp-def-srv-backends title="Conexiones, consultas activas y backends"}
**Qué dice.** Abrir una conexión crea un backend, la use o no. Cuántas conexiones hay abiertas, cuántas consultas corren y cuántos cores se usan son tres cantidades distintas.

**Variables.**

- $n_{\text{con}}$: conexiones abiertas, igual a backends vistos en `pg_stat_activity` (conexiones).
- $a$: consultas ejecutándose en este instante (consultas).
- $P_{\text{pg}}$: CPU lógicas del servidor de Postgres (CPU).

**Relaciones.**

$$a \le n_{\text{con}},\qquad \text{cores en uso} \le \min(a,\,P_{\text{pg}})$$

**Por qué es así.**

- Una consulta necesita una conexión, así que $a\le n_{\text{con}}$; una conexión ociosa cuenta en $n_{\text{con}}$ pero no en $a$.
- Cada consulta corre en su backend y usa a lo más un core (más si el servidor la paraleliza), de modo que los cores en uso salen de $a$, no de $n_{\text{con}}$.
:::

**Ejemplo paso a paso.**

1. **Datos.** Un pool de psycopg (la biblioteca de Python que se conecta a Postgres) abre 10 conexiones, de las cuales 2 ejecutan consultas.
2. **Backends.** $n_{\text{con}}=10$ filas de `pg_stat_activity` (celda 11.4, con Docker).
3. **Consultas activas.** $a=2$.
4. **Contra el presupuesto.** Este pool aporta 10 de las 97 plazas; con $R\times N=12$ pools como en la sección C, serían 120.
5. **Lectura.** Mirar `pg_stat_activity` cuenta conexiones, no carga: 10 backends no significan 10 consultas ni 10 cores.

## Katas

::: problem {#cmp-kata-p11-1 title="Kata 1 · Endpoint que llama a una API externa"}
Un endpoint recibe una petición, llama con `httpx` a una API externa que tarda 0,8 s y devuelve el resultado. Llegan 30 peticiones simultáneas a un worker. ¿`async def`, `def` o `async def` con `await`? ¿Cuánto tarda el lote?
:::

::: answer {of="cmp-kata-p11-1"}
**Elige:** `async def` con `await` sobre `httpx.AsyncClient`. **Porque:** $T\approx w=0{,}8$ s; la espera cede el hilo y las 30 avanzan juntas. **Descarta:** `def` (también serviría: $\lceil30/40\rceil\times0{,}8=0{,}8$ s, pero gasta un hilo por petición y a partir de la 41.ª peticiones simultáneas esperarían otra ronda); `async def` con el cliente síncrono `httpx.get` (bloquea el loop: $30\times0{,}8=24$ s).
:::

::: problem {#cmp-kata-p11-2 title="Kata 2 · Biblioteca síncrona"}
Tu endpoint usa un driver de base de datos síncrono (sin `await`) con un pool de 10 conexiones; cada consulta tarda 0,2 s. Llegan 100 peticiones simultáneas. ¿Qué forma usas y cuánto tarda?
:::

::: answer {of="cmp-kata-p11-2"}
**Elige:** `def`. **Porque:** la biblioteca bloquea y no admite `await`; FastAPI la corre en hilos. Dos límites: el limitador da $\lceil100/40\rceil=3$ rondas, $0{,}6$ s; el pool da $\lceil100/10\rceil\times0{,}2=2$ s. Manda el más estrecho, el pool: 2 s. **Descarta:** `async def` (la llamada bloquearía el loop: $100\times0{,}2=20$ s); subir $k_h$ solo ayuda si el servidor aguanta más conexiones.
:::

::: problem {#cmp-kata-p11-3 title="Kata 3 · Cálculo pesado"}
Un endpoint calcula durante 2 s de CPU (Python puro) por petición. La máquina tiene $P=4$ CPU y llegan 8 peticiones simultáneas. ¿`async def` o `def`? ¿Qué más cambias para usar los cores?
:::

::: answer {of="cmp-kata-p11-3"}
**Elige:** `def` (o un pool de procesos) **y** `uvicorn --workers 4`. **Porque:** $p_{\text{ef}}\le\min(N,P)=\min(4,4)=4$: con 4 workers, 8 peticiones son $\lceil8/4\rceil=2$ rondas de 2 s, 4 s (ideal). **Descarta:** `async def` con el cálculo dentro: con 4 workers el lote también tardaría cerca de 4 s, pero cada cálculo bloquea el loop de su worker y las demás peticiones de ese worker no son atendidas; un solo worker con `def` (los hilos de Python puro no suman cores: unos 16 s; los 16 s solo valen con un worker).
:::

::: problem {#cmp-kata-p11-4 title="Kata 4 · Dimensionar workers, pool y réplicas"}
Postgres tiene `max_connections=100` y 3 plazas reservadas. Tu servicio usa 2 réplicas, 3 workers por réplica y pool de 10. (a) ¿Cuántas conexiones puede abrir? (b) Quieres 4 réplicas con 3 workers: ¿cabe? ¿Qué cambiarías?
:::

::: answer {of="cmp-kata-p11-4"}
**Elige:** (a) $2\times3\times10=60\le97$, cabe con 37 de margen. (b) $4\times3\times10=120>97$: no cabe, excede por 23. **Cambia:** bajar $k$ a 8 ($4\times3\times8=96\le97$), o poner PgBouncer en modo transacción delante. **Descarta:** subir `max_connections` sin más (cada backend consume memoria del servidor) y creer que 12 pools de 10 equivalen a 10 consultas activas: son capacidad potencial, no carga.
:::

## Si hay tiempo

Con PgBouncer, hay un tope para conexiones de clientes y otro para conexiones a Postgres.

## Notebook

- Celda 11.1: lanza `app_arq.py` con uvicorn en un subproceso, un proceso iniciado por el notebook y usado como worker. Envía 12 peticiones a `/def-bloqueante`, a `/async-bloqueante` y a `/async-await`. Imprime el total y el hueco máximo del latido. Los resultados son cerca de 0.5 s, cerca de 6 s y cerca de 0.5 s.
- Celda 11.2: calcula $R\times N\times k$ con $R=3$, $N=4$, $k=10$ y lo compara con 97. Imprime 120 y el exceso de 23.
- Celda 11.3: lanza `app_arq.py` con `uvicorn --workers 2`, muestra los procesos con `ps`, cuenta los PID distintos que responden (2) y el contador local de cada worker (el estado en memoria no se comparte), y compara 4 cálculos simultáneos de 300 ms con 1 worker y con 2.
- Celda 11.4 (con Docker): abre un pool de psycopg de 10 conexiones contra Postgres y consulta `pg_stat_activity`: aparecen 10 backends, mientras las consultas activas son pocas; imprime también la cuenta del presupuesto.
