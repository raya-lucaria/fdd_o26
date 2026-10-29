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

Cómo leerla: cuenta el pool resaltado. PgBouncer recibe conexiones de clientes y mantiene menos conexiones con Postgres. Cuéntalas por separado.

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

**Cuenta.** Con $n$ peticiones simultáneas que esperan $w$ y $k_h$ tokens:

$$T_{\text{async + sleep}} \approx n\,w,\qquad T_{\text{def}} \approx \left\lceil \frac{n}{k_h} \right\rceil w,\qquad T_{\text{async + await}} \approx w.$$

Con $n=12$, $w=0{,}5$ s y $k_h=40$: $12\cdot0{,}5=6$ s, $\lceil 12/40\rceil\cdot0{,}5=0{,}5$ s y $0{,}5$ s (calculados, aproximaciones).

**Ejemplo (D1, celda 11.1).** Un worker recibe 12 peticiones simultáneas que esperan 0.5 s, en tres versiones:

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

**Definición.** El **presupuesto de conexiones** es el máximo permitido contra un servidor: $R\times N\times k$, con $R$ réplicas, $N$ workers por réplica y $k$ conexiones máximas por pool.

**Figura (tabla).** Los valores son supuestos del ejemplo; el servidor es el mismo para todas. Una plaza de superusuario reserva una conexión para quien administra Postgres.

| Concepto | Símbolo | Valor | Naturaleza |
|---|---|---|---|
| Réplicas | $R$ | 3 | supuesto |
| Workers por réplica | $N$ | 4 | supuesto |
| Máximo por pool | $k$ | 10 | supuesto |
| `max_connections` de Postgres | | 100 | supuesto (valor frecuente) |
| Plazas de superusuario | | 3 | supuesto |

**Cuenta.**

$$R\times N\times k = 3\times 4\times 10 = 120 \quad\text{frente a}\quad 100-3 = 97.$$

Los 120 valen si 10 es el máximo total por pool y todas las conexiones llegan al mismo servidor. Representan capacidad potencial, no conexiones ya abiertas. `reserved_connections` indica cuántas plazas adicionales están reservadas. Las 97 suponen `reserved_connections=0`. Otros consumidores reducen esa capacidad. `SHOW max_connections` la comprueba. Si todos los pools se llenan, el total excede 97 por 23 (calculado).

**Arquitectura.**

- **Qué es:** suma los topes locales de réplicas, workers y pools.
- **Cuándo sí:** calcúlalo antes de cambiar $R$, $N$ o $k$.
- **Cuándo no:** no estima consultas activas ni CPU.
- **Qué cuesta:** aumentar las réplicas multiplica las conexiones posibles, aunque cada pool no cambie ([[arquitectura-y-estrategia]]).
- **Sistema real:** Postgres limita conexiones con `max_connections`; usa PgBouncer si la cuenta supera al servidor.

Decisión: compara $R\times N\times k$ con la capacidad disponible antes de escalar el servicio.

## Si hay tiempo

Con PgBouncer, hay un tope para conexiones de clientes y otro para conexiones a Postgres.

## Notebook

- Celda 11.1: lanza `app_arq.py` con uvicorn en un subproceso, un proceso iniciado por el notebook y usado como worker. Envía 12 peticiones a `/def-bloqueante`, a `/async-bloqueante` y a `/async-await`. Imprime el total y el hueco máximo del latido. Los resultados son cerca de 0.5 s, cerca de 6 s y cerca de 0.5 s.
- Celda 11.2: calcula $R\times N\times k$ con $R=3$, $N=4$, $k=10$ y lo compara con 97. Imprime 120 y el exceso de 23.
