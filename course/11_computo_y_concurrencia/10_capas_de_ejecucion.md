---
id: capas-de-ejecucion
title: "Capas de ejecución"
nav_title: "Capas de ejecución"
summary: "Quién ejecuta una tarea, quién decide su turno y cómo leer una configuración como uvicorn --workers 2 para saber cuánto puede correr a la vez."
status: ready
estimated_time: 15m
tags: [hilos, procesos, planificador, runtime, gil, workers, paralelismo]
prerequisites: [secuencial-concurrente-paralelo]
---

# Capas de ejecución

**Página 10 · Cómputo y concurrencia** · Pregunta: **¿quién ejecuta el trabajo y quién decide su turno?**

**Respuesta:** los hilos ejecutan el trabajo. El sistema operativo los asigna a CPU lógicas. El runtime reparte tareas entre hilos. El pool puede limitar el paralelismo.

Recordatorio ([[secuencial-concurrente-paralelo]]):

- **Proceso.** Programa en ejecución, con memoria propia y al menos un hilo.
- **Hilo.** Secuencia de instrucciones que comparte memoria y recibe turnos en una CPU lógica.
- **Tarea.** Flujo secuencial administrado por el programa o runtime.

## A. Quién ejecuta y quién planifica

**Definición.**

| Término | Definición |
|---|---|
| **Runtime** | Biblioteca o programa que reparte tareas entre hilos. `asyncio` administra así sus tareas. |
| **Planificador** | Decide qué unidad usa cada recurso en cada instante. |
| **CPU lógica** | Unidad de ejecución visible al sistema operativo: núcleo o hilo del procesador. |
| **Exclusión global** | Permite ejecutar cierto código a un solo hilo. El GIL cumple esa función en CPython. |

**Figura.**

::: figure {#cmp-capas title="Pertenecer no es ejecutar: el sistema operativo planifica hilos y el runtime planifica tareas"}
![Dos columnas. Pertenencia: máquina, proceso, hilo, tarea. Ejecución: el sistema operativo asigna hilos a CPU lógicas; el runtime reparte tareas entre hilos, y una tarea puede cambiar de hilo.](_assets/cmp-capas.svg)
:::

Cómo leerla: cada flecha identifica quién decide una asignación.

**Un caso concreto: `python trabajo.py`.**

1. El sistema operativo crea un proceso, asigna memoria e inicia el hilo principal.
2. `threading.Thread` solicita un hilo; `ProcessPoolExecutor`, procesos. El sistema operativo los crea.
3. El sistema operativo asigna hilos a CPU lógicas. Los rota cuando faltan CPU.
4. Con `asyncio`, un hilo alterna tareas. El sistema operativo solo ve ese hilo.

Chrome suele abrir un proceso por pestaña o sitio para aislar fallas. Un videojuego comparte memoria mediante hilos. PostgreSQL abre un proceso por conexión ([[componer-un-servidor|página 11]]). Elige procesos para aislar memoria e hilos para compartirla.

**Figura.**

::: figure {#cmp-gantt-tres-planificaciones title="El mismo trabajo tarda 400, 400 o 100 ms según cuántas unidades avanzan a la vez"}
![Tres diagramas de Gantt del mismo trabajo: tareas cooperativas en un hilo, 400 ms; cuatro hilos con exclusión global, 400 ms; cuatro hilos en cuatro CPU, 100 ms.](_assets/cmp-gantt-tres-planificaciones.svg)
:::

Cómo leerla: sigue cada fila y distingue avance, espera rayada y tiempo total.

**Cuenta.** Supuestos: $n=4$ tareas independientes y $e=100$ ms de cálculo. Todas están disponibles en $t=0$. No hay costos extra. Son tiempos ideales.

::: definition {#cmp-def-tiempo-ideal title="Tiempo ideal de un lote de tareas"}
**Qué dice.** El tiempo ideal es el número de rondas multiplicado por su duración. Cada ronda agrupa tareas simultáneas.

**Variables.**

- $n$: número de tareas del lote (tareas).
- $e$: duración de una tarea sola, en ms.
- $p_{\text{ef}}$: tareas que avanzan simultáneamente de verdad (número de tareas).
- $T_{\text{ideal}}$: tiempo total sin costos extra, en ms.

**Regla de $p_{\text{ef}}$.** Es el menor de tres límites:

- CPU lógicas libres.
- Hilos repartidos por el runtime.
- Hilos permitidos por la exclusión global.

**Fórmula.**

$$T_{\text{ideal}}=\left\lceil\frac{n}{p_{\text{ef}}}\right\rceil e$$

**Por qué es así.**

- $n/p_{\text{ef}}$ cuenta rondas porque cada una adelanta $p_{\text{ef}}$ tareas.
- El techo redondea una ronda incompleta. 5 tareas con $p_{\text{ef}}=4$ requieren 2 rondas, no 1.25.
- Multiplicar por $e$ convierte rondas en tiempo. El menor límite determina cuántas tareas avanzan.
:::

**Ejemplo paso a paso.**

1. **Datos.** $n=4$, $e=100$ ms.
2. **Caso (a), tareas cooperativas en un hilo.** $p_{\text{ef}}=1$ → $\lceil 4/1\rceil=4$ rondas → $4\times100=400$ ms.
3. **Caso (b), 4 hilos con exclusión global y 4 CPU.** Límites: 4 CPU, 4 hilos y 1 permitido. $p_{\text{ef}}=1$ → $\lceil 4/1\rceil=4$ rondas → $4\times100=400$ ms.
4. **Caso (c), 4 hilos en 4 CPU libres, sin exclusión.** Los límites son 4, 4 y 4. $p_{\text{ef}}=4$ → $\lceil 4/4\rceil=1$ ronda → $1\times100=100$ ms.
5. **Lectura.** En (b), la exclusión limita el avance a uno. Por eso tarda 400 ms.

$p_{\text{ef}}$ depende del trabajo, los recursos, el runtime, las exclusiones y el pool. No es una ley general.

**Arquitectura.**

- **Qué es:** el pool limita $p_{\text{ef}}$ junto con las CPU, el runtime y las exclusiones.
- **Cuándo sí:** aumentarlo ayuda si impone el límite. Por ejemplo, 1 hilo y 4 CPU libres sin exclusión global.
- **Cuándo no:** no ayuda cuando otro factor limita a 1. En (b), más hilos no reducen los 400 ms.
- **Qué cuesta:** cada hilo consume memoria y causa cambios de contexto, cuando la CPU cambia de hilo.
- **Sistema real:** los procesos o extensiones nativas pueden evitar ese límite. Con el GIL, los hilos no suman cálculo de Python.

Decisión: antes de aumentar un pool, identifica qué limita $p_{\text{ef}}$.

## B. Leer una configuración

**Definición.**

| Término | Definición |
|---|---|
| **Paralelismo posible** | Unidades que pueden ejecutar simultáneamente según hardware, runtime, exclusiones y configuración. |
| **Tope admitido** | Máximo de tareas aceptadas en curso. |
| **Ocupación** | Fracción del tiempo que un recurso está en uso. |
| **Rendimiento** | Trabajos terminados por unidad de tiempo. |

**Figura.**

| Cantidad | Qué responde | Se lee de | Se obtiene |
|---|---|---|---|
| paralelismo posible | cuántas unidades ejecutan | hardware, runtime, exclusiones | configuración y documentación |
| tope admitido | cuántas tareas entran | servidor o pool | configuración |
| ocupación | cuánto se usa un recurso | recurso y ventana | medición |
| rendimiento | cuántos trabajos terminan | ventana de tiempo | medición |

Cómo leerla: las dos primeras cantidades vienen de la configuración; las otras dos se miden.

::: definition {#cmp-def-cuatro-cantidades title="Leer paralelismo posible, tope admitido, ocupación y rendimiento"}
**Qué dice.** La configuración indica paralelismo posible y tope admitido. La ejecución permite medir ocupación y rendimiento.

**Variables.**

- $P$: CPU lógicas de la máquina (CPU lógicas).
- $N$: workers o procesos que reciben trabajo (procesos).
- $g$: hilos que ejecutan bytecode simultáneamente por proceso; 1 con el GIL habilitado (hilos).
- Paralelismo posible de bytecode: hilos que pueden ejecutar instrucciones de Python simultáneamente (hilos). Se lee.
- Tope admitido: máximo aceptado de tareas en curso (tareas). Se lee.
- Ocupación: tiempo de uso de un recurso (entre 0 y 1). Se mide.
- Rendimiento: trabajos terminados por unidad de tiempo (trabajos por segundo). Se mide.

**Fórmula.**

$$\text{paralelismo posible de bytecode}=\min(P,\ N\cdot g)$$

**Por qué es así.**

- Cada worker tiene su propio GIL y aporta $g$ hilos. $N$ workers aportan $N\cdot g$.
- El total no puede superar las $P$ CPU lógicas. Por eso se toma el menor.
- Es la idea de $p_{\text{ef}}$: el menor límite determina el avance.
:::

**Ejemplo paso a paso.** Comando `uvicorn app:app --workers 2`, con GIL habilitado y $P=8$. Cada worker es un proceso.

1. **Datos.** `--workers 2` da $N=2$; el GIL da $g=1$; $P=8$.
2. **Procesos.** Hay 2 procesos worker, cada uno con intérprete y GIL propios. El intérprete ejecuta bytecode.
3. **Cuenta.** $N\cdot g=2\times1=2$ y $\min(8,2)=2$.
4. **Lectura.** Como máximo, dos hilos ejecutan bytecode simultáneamente, aunque $P=8$.

Una extensión nativa que suelta el GIL puede usar más CPU lógicas. Una operación larga de NumPy puede hacerlo. Sin GIL, el límite no aplica. El comando no fija un tope admitido; `--limit-concurrency` lo fijaría.

**Arquitectura.**

- **Qué es:** el comando permite calcular el paralelismo posible antes de ejecutar.
- **Cuándo sí:** sirve para elegir workers según $P$ y el cálculo en Python.
- **Cuándo no:** no predice ocupación ni rendimiento; ambas cantidades deben medirse.
- **Qué cuesta:** cada worker duplica la memoria del intérprete y sus pools locales.
- **Sistema real:** en Docker, `--cpus` limita la CPU y `--cpuset-cpus` selecciona CPU lógicas.

Decisión: el comando da un techo. Si la carga queda debajo, otro factor limita.

## C. Qué hace cada herramienta de Python cuando paralelizas

**Definición.** **Paralelizar** es repartir trabajo entre unidades que avanzan simultáneamente en CPU distintas.

**Figura (tabla).**

| Herramienta | ¿Cuántos procesos? | ¿Usa varias CPU para calcular? | Qué está haciendo |
|---|---|---|---|
| `threading`, `ThreadPoolExecutor` | 1 | No: el GIL deja ejecutar Python a un hilo | Reparte tareas entre hilos. Mientras uno espera la red, otro avanza |
| `asyncio` | 1 | No: un hilo, una CPU | Un hilo alterna tareas y combina esperas |
| `multiprocessing`, `ProcessPoolExecutor` | varios, uno por trabajador | Sí | Crea procesos con intérprete y GIL propios; copia los datos |
| `joblib.Parallel` con `n_jobs` > 1 | varios, por omisión | Sí | Usa procesos mediante `loky`; puede usar hilos si lo pides |
| NumPy, Polars ([[vectorizar]]) | 1 | Sí, dentro de una operación | El código nativo suelta el GIL y puede iniciar hilos |
| Python sin GIL (3.13, opcional) | 1 | Sí, también con hilos | Varios hilos ejecutan Python sin candado global |

**Ejemplo.** Considera las 4 tareas de 100 ms del Gantt. `ThreadPoolExecutor(4)` tarda 400 ms porque ejecuta un hilo. `ProcessPoolExecutor(4)` tarda cerca de 100 ms, más inicio y copia ([[calcular-en-paralelo]]). Si `top` muestra 4 CPU al 100 %, existen varios procesos o código nativo. No son 4 hilos de Python.

**Arquitectura.**

- **Qué es:** la herramienta se elige según el factor limitante.
- **Cuándo sí:** usa hilos o `asyncio` para esperas. Usa procesos para Python y NumPy o Polars para arreglos.
- **Cuándo no:** evita procesos cuando las tareas duran menos que su inicio y copia.
- **Qué cuesta:** cada proceso duplica el intérprete y los datos recibidos.
- **Sistema real:** scikit-learn y otras bibliotecas usan `joblib` cuando aceptan `n_jobs`.

Decisión: usa procesos cuando el trabajo calcula en Python y supera el costo de repartirlo.

**Cómo saber si usó varias CPU.** Compara el tiempo de reloj con el tiempo de CPU.

::: definition {#cmp-def-cpu-vs-reloj title="Cómo saber si una herramienta usó varias CPU"}
**Qué dice.** Tiempos parecidos indican una CPU. Si el tiempo de CPU es $u$ veces mayor, trabajaron unas $u$ CPU.

**Variables.**

- $T_{\text{reloj}}$: duración completa del trabajo, en s.
- $T_{\text{cpu}}$: suma del tiempo de cálculo de todas las CPU, en s.
- $u$: CPU efectivas usadas simultáneamente en promedio (número de CPU).

**Fórmula.**

$$u\approx\frac{T_{\text{cpu}}}{T_{\text{reloj}}}$$

**Por qué es así.**

- Una CPU entrega 1 s de cálculo por cada 1 s de reloj.
- $u$ CPU entregan $u\cdot T_{\text{reloj}}$ de cálculo. Despejar $u$ produce la división.
- Es aproximado. Las esperas no cuentan como CPU y debes sumar la CPU de procesos hijos.
:::

**Ejemplo paso a paso.** Celda 10.2: 4 tareas de Python puro, de unos 0.5 s de CPU cada una. Máquina de 8 CPU. Cifras **medidas**.

1. **Hilos.** $T_{\text{reloj}}=2.20$ s y $T_{\text{cpu}}=2.14$ s → $u\approx2.14/2.20\approx0.97$ CPU. Los 4 hilos compartieron una CPU por el GIL.
2. **Procesos.** $T_{\text{reloj}}=1.09$ s y $T_{\text{cpu}}=3.69$ s sumando los 4 procesos → $u\approx3.69/1.09\approx3.4$ CPU. El inicio de procesos también cuenta en el reloj.
3. **`joblib` (segunda llamada).** $T_{\text{reloj}}=0.92$ s y $T_{\text{cpu}}=3.21$ s → $u\approx3.5$ CPU. `joblib` reutiliza procesos, por eso la segunda llamada inicia más rápido.
4. **Lectura.** Los hilos usaron una CPU; los procesos y `joblib`, casi cuatro.

## Katas

::: problem {#cmp-kata-p10-1 title="Kata 1 · 200 descargas de 0.3 s"}
Descargas 200 archivos. Cada uno espera la red durante 0.3 s y casi no usa CPU. Tienes 4 CPU lógicas. La API acepta 50 conexiones simultáneas. ¿Hilos, procesos o asyncio? ¿Cuántas en curso?
:::

::: answer {of="cmp-kata-p10-1"}
**Elige:** `asyncio` o `ThreadPoolExecutor`, con 50 descargas en curso.

**Porque:** es espera, no cálculo. Sin tope: $\lceil 200/200\rceil\times300=300$ ms. Con tope: $\lceil 200/50\rceil\times300=4\times300=1200$ ms (1.2 s). En secuencia: $200\times0.3=60$ s.

**Descarta:** procesos, por su memoria y arranque. También descarta superar el límite de la API.
:::

::: problem {#cmp-kata-p10-2 title="Kata 2 · 8 imágenes de 2 s de cálculo"}
Procesas 8 imágenes. Cada una requiere 2 s de cálculo en Python puro. Tienes 4 CPU lógicas libres. ¿Qué usas y cuánto tarda?
:::

::: answer {of="cmp-kata-p10-2"}
**Elige:** `ProcessPoolExecutor(4)`.

**Porque:** $p_{\text{ef}}=\min(4\text{ CPU},4\text{ procesos})=4$ y $T_{\text{ideal}}=\lceil 8/4\rceil\times2=4$ s.

**Descarta:** hilos: $p_{\text{ef}}=1$ y $8\times2=16$ s. Con 8 procesos siguen siendo 4 s y gastas más memoria.
:::

::: problem {#cmp-kata-p10-3 title="Kata 3 · Servidor con --workers 4"}
Un servidor usa `--workers 4`, GIL habilitado y $P=8$. Cada petición consume 100 ms de bytecode. Llegan 8 peticiones simultáneas. ¿Cuánto tarda? ¿Ayuda añadir hilos?
:::

::: answer {of="cmp-kata-p10-3"}
**Elige:** leer el techo sin añadir hilos.

**Porque:** $\min(P,N\cdot g)=\min(8,4\times1)=4$. Entonces $p_{\text{ef}}=4$ y $T_{\text{ideal}}=\lceil 8/4\rceil\times100=200$ ms.

**Descarta:** más hilos por worker. El GIL impide sumar bytecode. `--workers 8` bajaría a 100 ms, duplicando más memoria.
:::

::: problem {#cmp-kata-p10-4 title="Kata 4 · Una operación larga de NumPy"}
Una llamada a NumPy tarda 2 s de reloj. Mides $T_{\text{cpu}}=7.6$ s. La máquina tiene 4 CPU lógicas. Piensas repartirla entre 4 procesos. ¿Conviene?
:::

::: answer {of="cmp-kata-p10-4"}
**Elige:** dejar la llamada como está.

**Porque:** $u\approx7.6/2=3.8$. Ya usa casi las 4 CPU lógicas mediante código nativo que suelta el GIL.

**Descarta:** procesos. No quedan CPU libres y pagarías la copia de datos. Un proceso sí puede usar varias CPU.
:::

## Si hay tiempo

Otros lenguajes reparten el trabajo de otras formas.

| Lenguaje | ¿Usa varias CPU? | En palabras simples |
|---|---|---|
| Go | Sí, por omisión | Las *goroutines* son tareas ligeras. El runtime las reparte entre hilos. `GOMAXPROCS` limita cuántas ejecutan, no cuántas existen |
| Elixir y Erlang (BEAM) | Sí, por omisión | Sus «procesos» son tareas ligeras, no procesos del sistema. Usa un planificador por CPU lógica; `+S` lo cambia |
| Node.js | No para tu código | Un hilo ejecuta JavaScript. Archivos y DNS usan 4 hilos internos. DNS busca direcciones. Para más CPU: `worker_threads` o procesos |
| Java | Sí | Los hilos normales pertenecen al sistema. Los virtuales usan pocos hilos «portadores». No crean CPU nuevas |

## Notebook

- Celda 10.1, hilos: lanza 4 hilos. Cada uno imprime su PID y nombre. Espera un PID y cuatro nombres distintos.
- Celda 10.1, procesos: lanza 2 procesos. Cada uno imprime su PID. Espera dos PID distintos.
- Celda 10.2: compara 4 hilos, 4 procesos y `joblib`. Espera CPU ≈ reloj con hilos y CPU mayor con procesos.
