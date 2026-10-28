---
id: computo-y-concurrencia
title: "Cómputo y concurrencia"
nav_title: "Cómputo y concurrencia"
summary: "Dónde pasa el tiempo de un programa, qué distingue secuencial, concurrente, paralelo y asíncrono, cómo se acota la concurrencia con semáforos y pools, cuándo repartir el cálculo en procesos o vectorizarlo, y qué arquitectura sale de cada medición."
status: ready
estimated_time: 138m
tags: [concurrencia, asyncio, hilos, procesos, pools, numpy, arquitectura, notebook]
prerequisites: [apis-y-http, el-gil]
---

# Cómputo y concurrencia

**Unidad 11** · el modelo matemático (página 0) y 8 páginas · unos 138 min · sesión del martes 27 de octubre, 19:00–20:30

Meta: ante un trabajo que espera, calcula o hace las dos cosas, **decidir con una medición** si va en secuencia, con hilos, con `asyncio`, con un tope, con un pool, con procesos o vectorizado, y defender esa decisión con un Gantt y una cuenta.

## En corto

- **Una tarea ejecuta, espera, está lista o está bloqueada.** Dónde pasa su tiempo decide la estrategia; la página 1 lo mide antes de proponer nada.
- **Cada modelo deja una huella observable y cada huella pide un patrón de arquitectura.** Las páginas recorren esa cadena una vez por concepto y la página 8 la junta.
- **Toda la unidad corre contra el servidor local de la clase** (`servidor.py`, con `?lento=` para fabricar espera y `/quien` para ver conexiones), más funciones locales para fabricar cálculo. Después de instalar, no hace falta internet.

## Del modelo a la decisión

| Modelo | Propiedad observable | Patrón de arquitectura | Decisión |
|---|---|---|---|
| exec contra wait ($\rho$) | con la tarea sola, CPU del cliente entre tiempo de reloj | presupuesto de latencia; servidor secuencial como línea base | ¿se acelera el cálculo o se reorganizan las esperas? |
| concurrente | un trazo vertical del Gantt corta dos o más vidas | hilo por conexión | hilos para E/S bloqueante en pocas decenas |
| asíncrono | esperas solapadas **en un mismo hilo** | servidor con event loop | `asyncio` para cientos o miles de esperas |
| `ready` en el loop | tramos rayados mientras el loop calcula | *offload*: loop + pool de procesos | nada de cálculo largo dentro del loop |
| `blocked` y Little | tareas formadas por un permiso; $\lambda\le k/W$ | concurrencia acotada, *backpressure*, *bulkhead* | el tope $k$ de cada dependencia |
| pool de recursos | puertos y conexiones reutilizados; conexiones en uso $=\lambda W$ | pool de conexiones, PgBouncer | tamaño del pool según lo que aguanta la BD, no según el tráfico |
| paralelo y GIL | dos filas de CPU ocupadas a la vez | pool de procesos, prefork | $k=\min(n,P)$ procesos para cálculo |
| fracción serial y cambio de escala | $T(N)$ medido; bucle contra NumPy | empujar el cálculo al motor (NumPy, Polars, SQL) | vectorizar antes de repartir |

## Las páginas

| # | Página | Qué contesta | Min |
|---:|---|---|---:|
| 0 | [[notacion-computo]] | **Se lee primero.** El modelo matemático: cada concepto en palabras, en fórmula y en el Gantt, con el ejemplo de tres tareas evaluado | 15 |
| 1 | [[donde-pasa-el-tiempo]] | Por qué 20 peticiones tardan 20 veces lo que una, y cómo se separa ejecutar de esperar | 12 |
| 2 | [[secuencial-concurrente-paralelo]] | Qué propiedad de la traza nombra cada palabra, por qué todo lo paralelo es concurrente y qué se rompe al compartir memoria | 20 |
| 3 | [[asincrono-y-el-event-loop]] | Cómo espera muchas peticiones un solo hilo, quién decide el turno y qué detiene al loop | 20 |
| 4 | [[concurrencia-acotada]] | Cómo se lanzan cientos de tareas sin tumbar a nadie: `gather`, semáforo, Little | 15 |
| 5 | [[pools-y-recursos]] | Qué libera `await` y qué no, qué guarda un pool que un semáforo no, y cómo se dimensiona | 18 |
| 6 | [[calcular-en-paralelo]] | Cuándo rinden los procesos, cuántos usar y qué dice Amdahl de la medición | 15 |
| 7 | [[vectorizar]] | Qué hacer cuando el trabajo calcula sobre muchos datos: sacar el bucle del intérprete | 8 |
| 8 | [[arquitectura-y-estrategia]] | Los tres modelos de servidor, capacidad con Little y el árbol de decisión aplicado a tres casos | 15 |

## Glosario breve

Todos los términos se definen primero en [[notacion-computo]] (página 0) y se repiten, con las mismas palabras, en la página donde se usan.

| Término | En una línea | Pág. |
|---|---|---:|
| Tarea | Flujo secuencial de trabajo con inicio y fin, observado desde un sistema elegido (casi siempre el cliente) | 1 |
| Ejecuta / espera / lista | Usa la CPU / espera red, disco o un temporizador / podría seguir pero no tiene turno | 1 |
| CPU-bound / I/O-bound | Cuello de botella en ejecutar / en esperar, medido con la tarea sola | 1 |
| Secuencial / concurrente | Vidas disjuntas / vidas que se solapan | 2 |
| Paralelo | Dos tareas ejecutando en el mismo instante; exige al menos 2 CPU y siempre es concurrente | 2 |
| Asíncrono | La llamada regresa antes del resultado y quien espera cede el hilo | 3 |
| Event loop / corrutina | Planificador cooperativo de un hilo / función que se suspende en `await` | 3 |
| Bloqueada | Espera algo que otra tarea del programa debe soltar: permiso, lock, conexión | 4 |
| Semáforo / Ley de Little | Cuenta permisos de entrada / tareas en vuelo = rendimiento × tiempo en el sistema | 4 |
| Pool | Conjunto de objetos reales reutilizables (conexiones, hilos, procesos) que se prestan y se devuelven | 5 |
| Speedup / Amdahl | Cociente entre un tiempo base declarado y el nuevo / techo que impone la fracción serial | 6 |
| Vectorizar | Aplicar una operación a un arreglo entero en código compilado | 7 |

## Antes de la clase

**El aula no tiene internet: haz esto antes, con red.** La unidad tiene su propia plantilla, `codigo/11_computo/`, con `requests`, `httpx`, `numpy` y `matplotlib`; instalarlos exige descargar.

**Haz 1 · trae lo nuevo del curso, crea la rama de la clase y copia la plantilla a tu carpeta:**

```bash
cd {tu_fork_de_la_clase}
git switch main && git fetch upstream && git merge --ff-only upstream/main
git switch -c clase-11-computo
[ -n "$GHUSER" ] && mkdir -p estudiantes/$GHUSER/11_computo \
  && cp -r codigo/11_computo/. estudiantes/$GHUSER/11_computo/ \
  && cd estudiantes/$GHUSER/11_computo && uv sync
```

- `clase-11-computo` es una rama de trabajo: **esta unidad no tiene entrega y no se abre pull request**. Tu `main` sigue avanzando con fast-forward.
- Todo el trabajo vive en `estudiantes/<login>/11_computo/`, versionado y en un solo lugar; el `.venv/` queda fuera de git.
- `uv sync` es el único paso que necesita red.

**Deberías ver** al final una línea `Installed … packages`.

**Haz 2 · arranca el servidor** en una terminal aparte, dentro de tu carpeta `11_computo`:

```bash
FDD_SILENCIO=1 uv run python servidor.py
```

`FDD_SILENCIO=1` apaga la radiografía de cada petición, que estorbaría al medir cientos de llamadas. Escucha en el puerto 8026: si dejaste corriendo el servidor de la unidad 10, apágalo antes con Ctrl+C. **Deja esta terminal abierta toda la clase.**

**Haz 3 · abre `computo.ipynb`** en VS Code y elige como kernel el `.venv` de `11_computo`. Sus celdas llevan el número de la página: `celda 4.2` es la segunda de la página 4.

## Fuera de alcance

- **Sistemas distribuidos**: varias máquinas, relojes que no coinciden, consenso y fallas parciales.
- **APIs avanzadas**: polling, SSE, WebSocket, webhooks, gRPC y GraphQL, y el diseño de reintentos y colas entre servicios.

Empieza por [[notacion-computo]], el modelo matemático; después, [[donde-pasa-el-tiempo]].
