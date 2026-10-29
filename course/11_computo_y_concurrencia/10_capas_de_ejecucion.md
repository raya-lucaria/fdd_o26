---
id: capas-de-ejecucion
title: "Capas de ejecución"
nav_title: "Capas de ejecución"
summary: "Quién ejecuta una tarea, quién decide su turno y cómo leer una configuración como uvicorn --workers 2 para saber cuánto puede correr a la vez."
status: ready
estimated_time: 12m
tags: [hilos, procesos, planificador, runtime, gil, workers, paralelismo]
prerequisites: [secuencial-concurrente-paralelo]
---

# Capas de ejecución

**Página 10 · Cómputo y concurrencia** · Pregunta: **cuando algo corre, ¿quién lo ejecuta y quién decide su turno?** · Respuesta: **los hilos ejecutan el trabajo, el sistema operativo los asigna a CPU lógicas y el runtime reparte tareas entre ellos; el pool puede limitar el paralelismo, pero no lo determina por sí solo.**

Recordatorio ([[secuencial-concurrente-paralelo]]):

- **Proceso.** Un proceso es un programa en ejecución con memoria propia y al menos un hilo.
- **Hilo.** Un hilo es una secuencia de instrucciones que comparte la memoria de su proceso y que el sistema operativo asigna a una CPU lógica.
- **Tarea.** Una tarea es un flujo secuencial de trabajo que el programa o runtime administra como unidad.

## A. Quién ejecuta y quién planifica

**Definición.**

| Término | Definición |
|---|---|
| **Runtime** | Un runtime es una biblioteca o máquina virtual que reparte tareas entre hilos. |
| **Planificador** | Un planificador decide qué unidad usa cada recurso en cada instante. |
| **CPU lógica** | Una CPU lógica es la unidad de ejecución que ve el sistema operativo: un núcleo o hilo de hardware. |
| **Exclusión global** | Una exclusión global es un candado que deja a lo sumo un hilo ejecutando cierto código; el GIL de CPython es una. |

**Figura.**

::: figure {#cmp-capas title="Pertenecer no es ejecutar: el sistema operativo planifica hilos y el runtime planifica tareas"}
![Dos columnas. Pertenencia: máquina, proceso, hilo, tarea. Ejecución: el sistema operativo asigna hilos a CPU lógicas; el runtime reparte tareas entre hilos, y una tarea puede cambiar de hilo.](_assets/cmp-capas.svg)
:::

Cómo leerla: cada flecha de ejecución identifica quién decide la asignación.

**Figura.**

::: figure {#cmp-gantt-tres-planificaciones title="El mismo trabajo tarda 400, 400 o 100 ms según cuántas unidades avanzan a la vez"}
![Tres diagramas de Gantt del mismo trabajo: tareas cooperativas en un hilo, 400 ms; cuatro hilos con exclusión global, 400 ms; cuatro hilos en cuatro CPU, 100 ms.](_assets/cmp-gantt-tres-planificaciones.svg)
:::

Cómo leerla: sigue cada fila y distingue avance, espera rayada y tiempo total.

**Cuenta.** Supuestos del ejemplo: $n=4$ tareas independientes de $e=100$ ms de cálculo, disponibles en $t=0$, sin costos extra (tiempos ideales). Con $p_{\text{ef}}$ unidades que avanzan a la vez:

$$T_{\text{ideal}}=\left\lceil \frac{n}{p_{\text{ef}}}\right\rceil e$$

Regla del ejemplo: $p_{\text{ef}}$ es el menor entre las CPU lógicas libres, los hilos que el runtime reparte y los hilos que la exclusión global deja ejecutar.

Calculado: (a) un solo hilo ejecuta, así que $p_{\text{ef}}=1$, $\lceil 4/1\rceil\cdot 100=400$ ms. (b) la exclusión global deja ejecutar a uno, $p_{\text{ef}}=1$, $\lceil 4/1\rceil\cdot 100=400$ ms. (c) hay 4 hilos y 4 CPU libres, $p_{\text{ef}}=4$, $\lceil 4/4\rceil\cdot 100=100$ ms. En (b) hay cuatro hilos y cuatro CPU, pero solo uno avanza porque la exclusión global lo impone.

$p_{\text{ef}}$ depende del trabajo disponible, el hardware, el runtime, las exclusiones y el tamaño del pool; no es una ley general.

**Arquitectura.**

- **Qué es:** el tamaño del pool es uno de los factores que fijan $p_{\text{ef}}$, junto con las CPU, el runtime y las exclusiones.
- **Cuándo sí:** conviene cuando el pool limita $p_{\text{ef}}$, por ejemplo, con 1 hilo y 4 CPU libres, si el código no retiene la exclusión global (una extensión nativa que la suelta, o procesos).
- **Cuándo no:** no ayuda cuando otro factor ya limita a 1, como en (b); más hilos no reducen los 400 ms.
- **Qué cuesta:** cada hilo consume memoria y provoca cambios de contexto, costos ausentes del ejemplo ideal.
- **Sistema real:** en CPython con GIL, los hilos solapan esperas, pero no suman cálculo de Python.

Decisión: antes de aumentar un pool, identifica qué factor limita hoy a $p_{\text{ef}}$.

## B. Leer una configuración

**Definición.**

| Término | Definición |
|---|---|
| **Paralelismo posible** | El paralelismo posible es el número de unidades que pueden ejecutar a la vez según hardware, runtime, exclusiones y configuración. |
| **Tope admitido** | El tope admitido es el máximo de tareas que el sistema acepta en curso. |
| **Ocupación** | La ocupación es la fracción del tiempo durante la cual un recurso está en uso. |
| **Rendimiento** | El rendimiento es el número de trabajos terminados por unidad de tiempo durante una ventana. |

**Figura.**

| Cantidad | Qué responde | Se lee de | Se obtiene |
|---|---|---|---|
| paralelismo posible | cuántas unidades ejecutan a la vez | hardware, runtime, exclusiones | configuración y documentación |
| tope admitido | cuántas tareas entran en curso | límites del servidor o del pool | configuración |
| ocupación | cuánto se usa un recurso | un recurso, en una ventana | medición |
| rendimiento | cuántos trabajos terminan | una ventana de tiempo | medición |

Cómo leerla: las dos primeras cantidades se leen de la configuración; las dos últimas se miden.

**Ejemplo.** Comando `uvicorn app:app --workers 2`, en CPython con GIL habilitado y $P=8$ CPU lógicas (supuestos del ejemplo). El comando crea 2 procesos worker. Cada proceso tiene su propio intérprete y GIL. Por tanto, a lo sumo dos hilos ejecutan bytecode de Python a la vez: uno por worker. Calculado: paralelismo posible de bytecode = 2, aunque $P=8$.

Esa cota no limita la CPU total: una extensión nativa que suelta el GIL (NumPy en una operación larga, por ejemplo) puede usar más CPU lógicas. Sin GIL, la cota no aplica. El comando tampoco fija un tope admitido; `--limit-concurrency` lo fijaría.

**Arquitectura.**

- **Qué es:** el comando permite obtener el paralelismo posible antes de ejecutar el sistema.
- **Cuándo sí:** sirve para dimensionar workers frente a $P$ y al cálculo ejecutado en Python.
- **Cuándo no:** no permite predecir la ocupación ni el rendimiento; ambas cantidades requieren medición.
- **Qué cuesta:** cada worker duplica la memoria del intérprete y sus pools locales.
- **Sistema real:** en Docker, `--cpus` limita el presupuesto de CPU del contenedor y `--cpuset-cpus` fija cuáles CPU lógicas usa.

Decisión: del comando se obtiene un techo de paralelismo; si la carga queda debajo, otro factor impone el límite.

## Si hay tiempo

Los runtimes asignan tareas y paralelismo de formas distintas. Cada fila explicita su condición.

| Runtime | Qué ejecuta en paralelo | Condición documentada |
|---|---|---|
| CPython con GIL | un hilo de bytecode por intérprete | habilitado, que es lo habitual |
| CPython sin GIL | varios hilos de bytecode | compilación sin GIL, opcional desde 3.13 |
| Go | goroutines sobre hilos del sistema | `GOMAXPROCS` limita el paralelismo de ejecución de Go, no el número de goroutines |
| BEAM (Erlang, Elixir) | procesos ligeros sobre planificadores | planificadores normales configurables con `+S`; la expulsión se basa en reducciones |
| Node.js | un hilo por contexto de JavaScript | 4 hilos de libuv por omisión, solo para ciertas operaciones; `worker_threads` para paralelismo |
| Java | hilos de plataforma e hilos virtuales | los virtuales corren sobre hilos portadores; no crean CPU |

## Notebook

- Celda 10.1, parte de hilos: lanza 4 hilos. Cada uno imprime el PID del proceso y el nombre de su hilo. Salida esperada: un solo PID repetido y cuatro nombres de hilo distintos.
- Celda 10.1, parte de procesos: lanza 2 procesos y cada uno imprime su PID. Salida esperada: dos PID distintos.
