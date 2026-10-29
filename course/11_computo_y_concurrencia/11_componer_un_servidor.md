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

**Página 11 · Cómputo y concurrencia** · Pregunta: **de una configuración, ¿cuántos procesos, hilos y conexiones resultan?** · Respuesta: **cada worker crea su pool local. `async def` corre en un hilo y `def` en hilos aparte. Los topes locales se multiplican.**

Un **proceso** es un programa en ejecución con memoria propia y al menos un hilo. $N$ representa trabajadores y $k$ un tope real, según [[notacion-computo]]. Consulta [[pools-y-recursos]].

## A. El pool local de cada worker

**Términos.**

| Término | Definición |
|---|---|
| Worker | Proceso que atiende peticiones mediante su hilo `async` u otros hilos. |
| Réplica | Copia del servicio en otra máquina o contenedor. |
| Balanceador | Programa que reparte peticiones entre réplicas. |
| Backend | Proceso de Postgres que atiende una conexión. |

**Definición.** Un **pool local** es el conjunto de conexiones que crea y usa un worker.

**Figura.**

::: figure {#cmp-ancla-servidor title="Cada worker tiene su loop y su pool; cada conexión directa es un backend de Postgres"}
![Ruta de una petición: cliente, balanceador, réplica con N workers, cada uno con loop y pool local, y una conexión al servidor Postgres por cada conexión del pool](_assets/cmp-ancla-servidor.svg)
:::

Cómo leerla: cuenta el pool resaltado. PgBouncer reutiliza pocas conexiones a Postgres para muchos clientes. Cuenta ambos grupos por separado.

**Cuenta.** Conexiones abiertas, consultas activas y CPU usada son cantidades distintas. Cada conexión directa crea un backend, aunque esté ociosa.

**Ejemplo.** Un pool con 10 conexiones y 2 consultas activas produce 10 backends y 2 consultas activas (supuesto del ejemplo).

**Arquitectura.**

- **Qué es:** el pool pertenece al proceso creador.
- **Cuándo sí:** el worker es dueño único de sus conexiones.
- **Cuándo no:** varios procesos no comparten un pool; compartirlo entre hilos depende de la biblioteca.
- **Qué cuesta:** cada worker añade su pool al servidor.
- **Sistema real:** PgBouncer comparte backends en modo transacción y aplica su propio `max_client_conn`.

Decisión: suma los pools de todos los workers.

## B. `async def`, `def` y esperar sin bloquear

**Términos.**

| Término | Definición |
|---|---|
| Loop | Único hilo que ejecuta, una por una, las tareas `async` de un worker. |
| Bloquear / ceder | Bloquear duerme el hilo; ceder permite atender otras tareas durante la espera. |
| Limitador de hilos | Restringe los hilos usados por FastAPI para funciones `def`. AnyIO ofrece $k_h=40$ tokens configurables por loop. |
| Latido | Tic registrado cada 10 ms para comprobar que el loop sigue vivo. |

**Definición.** Un **endpoint** responde a una dirección del servidor. FastAPI ejecuta `async def` en el loop y `def` mediante el limitador.

**Figura.**

::: figure {#cmp-async-vs-def title="Lo que cuenta no es async o def, sino si la espera bloquea el hilo o lo cede"}
![Tres paneles con 12 peticiones de 0.5 s: async def con time.sleep tarda 6 s porque el loop se bloquea y el latido se detiene; def con time.sleep tarda 0.5 s porque cada petición usa su hilo; async def con await asyncio.sleep tarda 0.5 s porque await cede el hilo](_assets/cmp-async-vs-def.svg)
:::

Cómo leerla: cada fila representa una petición. La última muestra el latido del loop.

::: definition {#cmp-def-srv-tiempo-espera title="Tiempo de n peticiones simultáneas que esperan"}
**Qué dice.** El tiempo depende de bloquear el loop, ocupar tokens o ceder el hilo.

**Variables.**

- $n$: peticiones simultáneas (peticiones).
- $w$: espera individual (s).
- $k_h$: capacidad del limitador; 40 por omisión en AnyIO (tokens).
- $T$: tiempo hasta terminar la última petición (s).

**Fórmulas.**

$$T_{\text{async + sleep}} \approx n\,w$$

$$T_{\text{def}} \approx \left\lceil \frac{n}{k_h} \right\rceil w$$

$$T_{\text{async + await}} \approx w$$

**Por qué es así.**

- `time.sleep` bloquea el único hilo del loop; las $n$ esperas se suman.
- `def` usa rondas de hasta $k_h$ hilos; cada ronda dura $w$.
- `await asyncio.sleep` cede el hilo; todas las peticiones esperan juntas.
:::

**Ejemplo paso a paso.**

1. **Datos.** $n=12$, $w=0{,}5$ s, $k_h=40$.
2. **`async def` con `sleep`.** $12\times0{,}5=6$ s.
3. **`def`.** $\lceil 12/40\rceil=\lceil 0{,}3\rceil=1$ ronda; $1\times0{,}5=0{,}5$ s.
4. **`async def` con `await`.** $w=0{,}5$ s.
5. **Contraste medido.** 6,02 s, 0,53 s y 0,52 s; el arranque explica las milésimas adicionales.
6. **Lectura.** Con $n=100$, `def` requiere $\lceil 100/40\rceil=3$ rondas: 1,5 s. `await` conserva 0,5 s.

**Medición (D1, celda 11.1).** Un worker recibe 12 peticiones simultáneas que esperan 0.5 s:

| Versión | Dónde corre | Qué pasa | Total medido | Hueco máximo del latido |
|---|---|---|---|---|
| `def` con `time.sleep` | un hilo por petición | las 12 esperan juntas | 0.53 s | 0.01 s |
| `async def` con `time.sleep` | loop único | una petición cada vez | 6.02 s | 6.01 s |
| `async def` con `await asyncio.sleep` | loop | `await` cede el hilo | 0.52 s | 0.01 s |

El **hueco máximo** mide el intervalo sin tics. El bloqueo síncrono detuvo el loop casi todo el tiempo. Medido en 8 CPU.

**Arquitectura.**

- **Qué es:** FastAPI ejecuta `def` en hilos y `async def` en el loop.
- **Cuándo sí:** usa `await` para esperas asíncronas y `def` para bibliotecas bloqueantes.
- **Cuándo no:** `time.sleep` o una consulta síncrona dentro de `async def` bloquean el loop.
- **Qué cuesta:** cada `def` activo ocupa un token; los hilos ociosos no cuentan.
- **Sistema real:** FastAPI usa AnyIO mediante Starlette y corre sobre uvicorn.

Decisión: usa `def` si la espera bloquea; usa `async def` si admite `await`.

## C. Presupuesto de conexiones

**Definición.** El **presupuesto de conexiones** es el máximo de conexiones que tu servicio puede abrir contra un servidor.

`max_connections` limita las conexiones de Postgres. Las plazas reservadas guardan 3 por omisión para superusuarios (`superuser_reserved_connections`).

::: definition {#cmp-def-srv-presupuesto title="Presupuesto de conexiones"}
**Qué dice.** Cada worker tiene un pool local. El máximo total multiplica réplicas, workers y conexiones.

**Variables.**

- $R$: cantidad de réplicas (réplicas).
- $N$: workers por réplica (procesos).
- $k$: máximo del pool por worker (conexiones).
- $M$: `max_connections` de Postgres (conexiones).
- $s_{\text{su}}$: plazas reservadas para superusuarios (conexiones).

**Fórmula.**

$$R\times N\times k \;\le\; M - s_{\text{su}}$$

**Por qué es así.**

- Cada réplica contiene $N$ pools de hasta $k$ conexiones.
- Las $R$ réplicas permiten $R\times N\times k$ conexiones.
- El servicio dispone de $M-s_{\text{su}}$ plazas.
:::

**Figura (tabla).** Todos son supuestos del ejemplo para un mismo servidor.

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
4. **Comparación.** $120>97$; el exceso es $120-97=23$ (calculado).
5. **Lectura.** Es capacidad potencial. Las 97 excluyen otros consumidores; `SHOW max_connections` comprueba $M$.

**Arquitectura.**

- **Qué es:** suma topes locales de réplicas, workers y pools.
- **Cuándo sí:** calcúlalo antes de cambiar $R$, $N$ o $k$.
- **Cuándo no:** no estima consultas activas ni CPU.
- **Qué cuesta:** aumentar réplicas multiplica conexiones posibles ([[arquitectura-y-estrategia]]).
- **Sistema real:** Postgres aplica `max_connections`; PgBouncer reduce backends necesarios.

Decisión: compara $R\times N\times k$ con la capacidad antes de escalar.

## D. Workers y cores: `uvicorn --workers N`

**Definición.** Un **core** ejecuta un hilo a la vez. `uvicorn --workers N` inicia un supervisor y $N$ procesos worker.

Cada worker posee loop, memoria y pool. El supervisor no atiende peticiones. Con `--workers 1`, el proceso principal ejecuta el servidor.

::: definition {#cmp-def-srv-workers title="CPU que usa un servicio con N workers"}
**Qué dice.** Cada worker ejecuta Python en un hilo a la vez. Más workers aprovechan más CPU, hasta el límite disponible.

**Variables.**

- $N$: cantidad de workers (procesos).
- $P$: CPU lógicas disponibles (CPU).
- $p_{\text{ef}}$: cores activos simultáneos, limitados por workers y CPU (cores).

**Fórmula.**

$$p_{\text{ef}} \le \min(N,\,P)$$

**Por qué es así.**

- Cada worker aporta como máximo un hilo de Python ejecutándose y un core.
- Con $N<P$ sobran cores; con $N>P$ los workers compiten por las $P$ disponibles.
- La espera reduce el uso; además, memoria, contadores y cachés no se comparten.
:::

**Ejemplo paso a paso.**

1. **Datos.** $N=2$ workers, $P=8$ CPU.
2. **Cota.** $\min(2,8)=2$: hasta 2 cores.
3. **Verificación (celda 11.3).** `/quien` devuelve 2 PID distintos. Cada **PID** identifica un proceso.
4. **Reparto.** El supervisor comparte la entrada. Una conexión keep-alive produjo 20 de 20 respuestas del mismo PID.
5. **Conexiones nuevas.** La prueba repartió 11 y 9; el worker recibe conexiones, no peticiones.
6. **Estado local.** Cada contador solo registra las peticiones de su worker.
7. **Cálculo.** Cuatro trabajos de 300 ms tardaron 1.3 a 1.6 s con 1 worker.
8. **Dos workers.** Repartidos 2 y 2, tardaron 0.7 a 0.9 s. Un reparto 3 y 1 casi no mejora.
9. **Lectura.** Los hilos de Python puro se turnan por el GIL. Compartir estado exige base de datos o caché externa.

## E. El pool de Postgres, visto desde el servidor

**Definición.** `pg_stat_activity` muestra una fila por proceso de Postgres. En una conexión directa, esa fila representa su backend.

::: definition {#cmp-def-srv-backends title="Conexiones, consultas activas y backends"}
**Qué dice.** Cada conexión crea un backend. Conexiones abiertas, consultas activas y cores usados son cantidades distintas.

**Variables.**

- $n_{\text{con}}$: conexiones abiertas y backends en `pg_stat_activity` (conexiones).
- $a$: consultas ejecutándose ahora (consultas).
- $P_{\text{pg}}$: CPU lógicas de Postgres (CPU).

**Relaciones.**

$$a \le n_{\text{con}},\qquad \text{cores en uso} \le \min(a,\,P_{\text{pg}})$$

**Por qué es así.**

- Cada consulta requiere una conexión; las conexiones ociosas cuentan solo en $n_{\text{con}}$.
- Los cores dependen de $a$, aunque Postgres puede paralelizar una consulta.
:::

**Ejemplo paso a paso.**

1. **Datos.** Un pool de psycopg abre 10 conexiones; 2 ejecutan consultas.
2. **Backends.** $n_{\text{con}}=10$ filas de `pg_stat_activity` (celda 11.4, con Docker).
3. **Consultas activas.** $a=2$.
4. **Presupuesto.** El pool ocupa 10 de 97 plazas. Con $R\times N=12$ pools, ocuparía 120.
5. **Lectura.** 10 backends no implican 10 consultas ni 10 cores.

## Katas

::: problem {#cmp-kata-p11-1 title="Kata 1 · Endpoint que llama a una API externa"}
Una API externa tarda 0,8 s. Llegan 30 peticiones simultáneas a un worker. ¿Qué forma eliges y cuánto tardan?
:::

::: answer {of="cmp-kata-p11-1"}
**Elige:** `async def` con `await` y `httpx.AsyncClient`; $T\approx w=0{,}8$ s.

**Porque:** la espera cede el hilo y las 30 peticiones avanzan juntas.

**Descarta:** `def` usa 30 hilos: $\lceil30/40\rceil\times0{,}8=0{,}8$ s; la 41.ª petición requeriría otra ronda. `httpx.get` bloquearía: $30\times0{,}8=24$ s.
:::

::: problem {#cmp-kata-p11-2 title="Kata 2 · Biblioteca síncrona"}
Un driver síncrono usa un pool de 10 conexiones. Cada consulta tarda 0,2 s. Llegan 100 peticiones. ¿Qué eliges?
:::

::: answer {of="cmp-kata-p11-2"}
**Elige:** `def`.

**Porque:** el limitador requiere $\lceil100/40\rceil=3$ rondas, $0{,}6$ s. El pool requiere $\lceil100/10\rceil\times0{,}2=2$ s y manda.

**Descarta:** `async def` bloquearía $100\times0{,}2=20$ s. Subir $k_h$ solo ayuda si el servidor soporta más conexiones.
:::

::: problem {#cmp-kata-p11-3 title="Kata 3 · Cálculo pesado"}
Cada petición calcula durante 2 s de CPU en Python puro. Con $P=4$ CPU llegan 8 peticiones. ¿Qué cambias?
:::

::: answer {of="cmp-kata-p11-3"}
**Elige:** `def` o un pool de procesos, con `uvicorn --workers 4`.

**Porque:** $p_{\text{ef}}\le\min(N,P)=\min(4,4)=4$; $\lceil8/4\rceil=2$ rondas de 2 s tardan 4 s (ideal).

**Descarta:** `async def` también rondaría 4 s, pero bloquearía cada loop. Un worker con `def` tardaría unos 16 s.
:::

::: problem {#cmp-kata-p11-4 title="Kata 4 · Dimensionar workers, pool y réplicas"}
Postgres tiene `max_connections=100` y 3 plazas reservadas. Hay 2 réplicas, 3 workers y pools de 10. Dimensiona 4 réplicas.
:::

::: answer {of="cmp-kata-p11-4"}
**Elige:** (a) $2\times3\times10=60\le97$: margen de 37. (b) $4\times3\times10=120>97$: exceso de 23.

**Cambia:** baja $k$ a 8, pues $4\times3\times8=96\le97$, o usa PgBouncer en modo transacción.

**Descarta:** subir `max_connections` sin más consume memoria. Los 12 pools de 10 representan capacidad potencial, no consultas activas.
:::

## Si hay tiempo

Con PgBouncer, distingue el tope de clientes del tope de conexiones a Postgres.

## Notebook

- Celda 11.1: ejecuta `app_arq.py`; compara 12 peticiones y el latido en `/def-bloqueante`, `/async-bloqueante` y `/async-await`: cerca de 0.5 s, 6 s y 0.5 s.
- Celda 11.2: calcula $R\times N\times k$ con $R=3$, $N=4$ y $k=10$; imprime 120 y el exceso de 23 sobre 97.
- Celda 11.3: usa `uvicorn --workers 2`; muestra 2 PID, contadores locales y 4 cálculos simultáneos de 300 ms con 1 y 2 workers.
- Celda 11.4 (con Docker): psycopg abre 10 conexiones; `pg_stat_activity` muestra 10 backends, pocas consultas activas y el presupuesto.
