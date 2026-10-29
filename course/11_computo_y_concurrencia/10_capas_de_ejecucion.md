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

**Página 10 · Cómputo y concurrencia** · Pregunta: **¿quién ejecuta el trabajo y quién decide su turno?** · Respuesta: **los hilos ejecutan el trabajo. El sistema operativo los asigna a CPU lógicas. El runtime, componente que administra tareas, las reparte entre hilos. El pool puede limitar el paralelismo, pero no lo determina por sí solo.**

Recordatorio ([[secuencial-concurrente-paralelo]]):

- **Proceso.** Un proceso es un programa en ejecución con memoria propia y al menos un hilo.
- **Hilo.** Un hilo es una secuencia de instrucciones. Comparte la memoria del proceso y recibe turnos en una CPU lógica.
- **Tarea.** Una tarea es un flujo secuencial de trabajo. El programa o runtime la administra como unidad.

## A. Quién ejecuta y quién planifica

**Definición.**

| Término | Definición |
|---|---|
| **Runtime** | Un runtime es una biblioteca o programa que reparte tareas entre hilos. `asyncio` cumple esa función con sus tareas. |
| **Planificador** | Un planificador decide qué unidad usa cada recurso en cada instante. Sus turnos aparecen en los diagramas de Gantt. |
| **CPU lógica** | Una CPU lógica es la unidad de ejecución que ve el sistema operativo: un núcleo o hilo del procesador. |
| **Exclusión global** | Una exclusión global permite ejecutar cierto código a un solo hilo. El GIL de CPython, la versión habitual de Python, cumple esa función. |

**Figura.**

::: figure {#cmp-capas title="Pertenecer no es ejecutar: el sistema operativo planifica hilos y el runtime planifica tareas"}
![Dos columnas. Pertenencia: máquina, proceso, hilo, tarea. Ejecución: el sistema operativo asigna hilos a CPU lógicas; el runtime reparte tareas entre hilos, y una tarea puede cambiar de hilo.](_assets/cmp-capas.svg)
:::

Cómo leerla: cada flecha identifica quién decide una asignación.

**Un caso concreto: `python trabajo.py`.**

1. El sistema operativo crea un proceso, le da memoria y arranca el hilo principal. Ese hilo empieza a ejecutar tu código.
2. Tu código puede pedir más recursos: `threading.Thread` pide un hilo; `ProcessPoolExecutor`, procesos. Python los solicita y el sistema operativo los crea.
3. El sistema operativo mantiene la lista de hilos disponibles y las CPU lógicas libres. Asigna turnos y rota los hilos cuando faltan CPU.
4. Con `asyncio`, un hilo alterna tareas. El sistema operativo solo ve ese hilo.

Chrome suele abrir un proceso por pestaña o sitio. Si una se cuelga, las demás siguen. Un videojuego suele usar un proceso y varios hilos para dibujo, física, sonido y carga. PostgreSQL abre un proceso por conexión ([[componer-un-servidor|página 11]]). Elige procesos para aislar memoria e hilos para compartirla.

**Figura.**

::: figure {#cmp-gantt-tres-planificaciones title="El mismo trabajo tarda 400, 400 o 100 ms según cuántas unidades avanzan a la vez"}
![Tres diagramas de Gantt del mismo trabajo: tareas cooperativas en un hilo, 400 ms; cuatro hilos con exclusión global, 400 ms; cuatro hilos en cuatro CPU, 100 ms.](_assets/cmp-gantt-tres-planificaciones.svg)
:::

Cómo leerla: sigue cada fila y distingue avance, espera rayada y tiempo total.

**Cuenta.** Supuestos del ejemplo: $n=4$ tareas independientes de $e=100$ ms de cálculo. Todas están disponibles en $t=0$ y no hay costos extra. Son tiempos ideales.

::: definition {#cmp-def-tiempo-ideal title="Tiempo ideal de un lote de tareas"}
**Qué dice.** El **tiempo ideal** de un lote es el número de rondas que hacen falta, multiplicado por lo que dura cada ronda. Una ronda es un grupo de tareas que avanzan a la vez.

**Variables.**

- $n$: número de tareas del lote (cuántas hay que hacer).
- $e$: duración de una tarea sola, en ms.
- $p_{\text{ef}}$: **paralelismo efectivo**, cuántas tareas avanzan a la vez de verdad (número de tareas).
- $T_{\text{ideal}}$: tiempo total del lote sin costos extra, en ms.

**Regla de $p_{\text{ef}}$.** Es el menor de tres límites:

- CPU lógicas libres.
- Hilos que el runtime reparte.
- Hilos que la exclusión global deja ejecutar.

**Fórmula.**

$$T_{\text{ideal}}=\left\lceil\frac{n}{p_{\text{ef}}}\right\rceil e$$

**Por qué es así.**

- La división $n/p_{\text{ef}}$ cuenta cuántas rondas hacen falta: si avanzan $p_{\text{ef}}$ tareas a la vez, las $n$ tareas se agotan de a $p_{\text{ef}}$.
- El techo $\lceil\ \rceil$ redondea hacia arriba porque una última ronda incompleta igual cuesta una ronda entera: 5 tareas con $p_{\text{ef}}=4$ son 2 rondas, no 1.25.
- Multiplicar por $e$ convierte rondas en tiempo, porque cada ronda dura lo que dura una tarea sola.
- El mínimo de tres límites aparece porque basta un límite en 1 para que solo avance una tarea, aunque los otros dos sobren.
:::

**Ejemplo paso a paso.**

1. **Datos.** $n=4$, $e=100$ ms.
2. **Caso (a), tareas cooperativas en un hilo.** Ejecuta un hilo: $p_{\text{ef}}=1$ → $\lceil 4/1\rceil=4$ rondas → $4\times100=400$ ms.
3. **Caso (b), 4 hilos con exclusión global y 4 CPU.** Límites: 4 CPU libres, 4 hilos, 1 por la exclusión. El menor es 1: $p_{\text{ef}}=1$ → $\lceil 4/1\rceil=4$ rondas → $4\times100=400$ ms.
4. **Caso (c), 4 hilos en 4 CPU libres, sin exclusión.** Límites: 4, 4 y 4. $p_{\text{ef}}=4$ → $\lceil 4/4\rceil=1$ ronda → $1\times100=100$ ms.
5. **Lectura.** En (b) hay cuatro hilos y cuatro CPU, pero la exclusión solo deja avanzar a uno, así que 400 ms.

$p_{\text{ef}}$ depende del trabajo disponible, los recursos físicos, el runtime, las exclusiones y el tamaño del pool. No es una ley general.

**Arquitectura.**

- **Qué es:** el tamaño del pool ayuda a fijar $p_{\text{ef}}$ junto con las CPU, el runtime y las exclusiones.
- **Cuándo sí:** conviene si el pool impone el límite. Por ejemplo, hay 1 hilo y 4 CPU libres sin exclusión global. Esto ocurre con procesos o con una extensión nativa (código compilado, no Python) que suelta esa exclusión.
- **Cuándo no:** no ayuda si otro factor limita a 1. En (b), más hilos no reducen los 400 ms.
- **Qué cuesta:** cada hilo consume memoria y provoca cambios de contexto, momentos cuando la CPU cambia de hilo. El ejemplo ideal omite estos costos.
- **Sistema real:** con el GIL de CPython, un hilo avanza mientras otro espera, pero los hilos no suman cálculo de Python.

Decisión: antes de aumentar un pool, identifica qué factor limita $p_{\text{ef}}$.

## B. Leer una configuración

**Definición.**

| Término | Definición |
|---|---|
| **Paralelismo posible** | Número de unidades que pueden ejecutar simultáneamente según hardware, runtime, exclusiones y configuración. |
| **Tope admitido** | Máximo de tareas que el sistema acepta en curso. |
| **Ocupación** | Fracción del tiempo durante la cual un recurso está en uso. |
| **Rendimiento** | Número de trabajos terminados por unidad de tiempo durante una ventana. |

**Figura.**

| Cantidad | Qué responde | Se lee de | Se obtiene |
|---|---|---|---|
| paralelismo posible | cuántas unidades ejecutan a la vez | hardware, runtime, exclusiones | configuración y documentación |
| tope admitido | cuántas tareas entran en curso | límites del servidor o del pool | configuración |
| ocupación | cuánto se usa un recurso | un recurso, en una ventana | medición |
| rendimiento | cuántos trabajos terminan | una ventana de tiempo | medición |

Cómo leerla: las dos primeras cantidades vienen de la configuración; las otras dos se miden.

::: definition {#cmp-def-cuatro-cantidades title="Leer paralelismo posible, tope admitido, ocupación y rendimiento"}
**Qué dice.** De una configuración se leen dos cantidades (paralelismo posible y tope admitido) y de una ejecución se miden otras dos (ocupación y rendimiento).

**Variables y medidas.**

- $P$: número de CPU lógicas de la máquina (CPU lógicas).
- $N$: número de workers, procesos que recibe el servidor (procesos).
- $g$: hilos que ejecutan bytecode a la vez dentro de un proceso: 1 si el GIL está habilitado (hilos).
- Paralelismo posible de bytecode: cuántos hilos pueden ejecutar instrucciones de Python a la vez (hilos). Se lee de la configuración.
- Tope admitido: máximo de tareas en curso que el sistema acepta (tareas). Se lee de la configuración.
- Ocupación: fracción del tiempo en que un recurso está en uso (entre 0 y 1). Se mide.
- Rendimiento: trabajos terminados por unidad de tiempo (trabajos por segundo). Se mide.

**Fórmula.**

$$\text{paralelismo posible de bytecode}=\min(P,\ N\cdot g)$$

**Por qué es así.** Cada worker es un proceso con su propio GIL, así que aporta $g$ hilos ejecutando bytecode; $N$ workers aportan $N\cdot g$. Ese número no puede superar las $P$ CPU lógicas, y por eso se toma el menor de los dos. Es la misma idea de $p_{\text{ef}}$ en la caja de la sección A: el menor de los límites que dejan avanzar a las tareas, aquí con otros límites (CPU lógicas y workers por hilos permitidos).
:::

**Ejemplo paso a paso.** Comando `uvicorn app:app --workers 2`, con GIL habilitado y $P=8$. Un worker es un proceso que recibe trabajo.

1. **Datos.** `--workers 2` da $N=2$; el GIL habilitado da $g=1$; $P=8$.
2. **Procesos.** El comando crea 2 procesos worker, cada uno con su propio intérprete y GIL. El intérprete ejecuta bytecode, las instrucciones internas que produce Python.
3. **Cuenta.** $N\cdot g=2\times1=2$ y $\min(8,2)=2$.
4. **Lectura.** Como máximo dos hilos ejecutan bytecode simultáneamente, uno por worker, aunque $P=8$.

Este límite no cubre toda la CPU. Una extensión nativa que suelta el GIL puede usar más CPU lógicas. Una operación larga de NumPy puede hacerlo. Sin GIL, el límite no aplica. El comando tampoco fija un tope admitido; `--limit-concurrency` lo fijaría.

**Arquitectura.**

- **Qué es:** el comando permite obtener el paralelismo posible antes de ejecutar el sistema.
- **Cuándo sí:** sirve para elegir workers según $P$ y el cálculo ejecutado en Python.
- **Cuándo no:** no predice la ocupación ni el rendimiento; debes medir ambas cantidades.
- **Qué cuesta:** cada worker duplica la memoria del intérprete y sus pools locales.
- **Sistema real:** en Docker, `--cpus` limita la CPU disponible y `--cpuset-cpus` fija cuáles CPU lógicas usa.

Decisión: el comando da un techo de paralelismo. Si la carga queda debajo, otro factor impone el límite.

## C. Qué hace cada herramienta de Python cuando paralelizas

**Definición.** **Paralelizar** es repartir trabajo entre unidades que avanzan simultáneamente en CPU distintas. Cada herramienta de Python lo logra de forma diferente.

**Figura (tabla).**

| Herramienta | ¿Cuántos procesos? | ¿Usa varias CPU para calcular? | Qué está haciendo |
|---|---|---|---|
| `threading`, `ThreadPoolExecutor` | 1 | No: un solo hilo ejecuta Python a la vez (GIL) | Reparte tareas entre hilos del mismo proceso; mientras uno espera la red, otro avanza |
| `asyncio` | 1 | No: un hilo, una CPU | Un hilo alterna tareas; combina esperas, pero no calcula en paralelo |
| `multiprocessing`, `ProcessPoolExecutor` | varios, uno por trabajador | Sí | Arranca procesos con intérprete y GIL propios; copia los datos a cada proceso |
| `joblib.Parallel` con `n_jobs` > 1 | varios, por omisión | Sí | Reparte tareas entre procesos mediante el backend `loky`, su mecanismo interno; si lo pides, usa hilos |
| NumPy, Polars ([[vectorizar]]) | 1 | Sí, dentro de una operación | Una llamada usa código nativo que suelta el GIL y puede iniciar varios hilos propios |
| Python sin GIL (3.13, opcional) | 1 | Sí, también con hilos | Varios hilos ejecutan Python simultáneamente sin candado global |

**Ejemplo.** Considera las 4 tareas de 100 ms del Gantt. Con `ThreadPoolExecutor(4)` ocurre (b): 400 ms, porque solo ejecuta un hilo. Con `ProcessPoolExecutor(4)` ocurre (c): cerca de 100 ms, más el costo de iniciar procesos y copiar datos ([[calcular-en-paralelo]]). Si `top` muestra 4 CPU al 100 %, hay 4 procesos o código nativo con varios hilos. No son 4 hilos de Python.

**Arquitectura.**

- **Qué es:** elige la herramienta según el factor que limita el trabajo.
- **Cuándo sí:** usa hilos o `asyncio` para esperas. Usa procesos para cálculo en Python y NumPy o Polars para arreglos.
- **Cuándo no:** evita procesos si las tareas duran menos que su costo de arranque y copia.
- **Qué cuesta:** cada proceso duplica la memoria del intérprete y los datos recibidos.
- **Sistema real:** scikit-learn y otras bibliotecas usan `joblib` cuando aceptan `n_jobs`.

Decisión: antes de usar procesos, comprueba que el trabajo calcula en Python y dura más que su reparto.

**Cómo saber si usó varias CPU.** Compara cuánto tardó el reloj con cuánto trabajó la CPU.

::: definition {#cmp-def-cpu-vs-reloj title="Cómo saber si una herramienta usó varias CPU"}
**Qué dice.** Si el tiempo de CPU es parecido al tiempo de reloj, el trabajo usó una CPU. Si es unas $u$ veces mayor, usó unas $u$ CPU.

**Variables.**

- $T_{\text{reloj}}$: tiempo de reloj, lo que tardó el trabajo de principio a fin, en s.
- $T_{\text{cpu}}$: tiempo de CPU, suma del tiempo que todas las CPU estuvieron calculando para ese trabajo, en s.
- $u$: CPU efectivas, cuántas CPU trabajaron a la vez en promedio (número de CPU).

**Fórmula.**

$$u\approx\frac{T_{\text{cpu}}}{T_{\text{reloj}}}$$

**Por qué es así.** Una CPU entrega 1 s de cálculo por cada 1 s de reloj. Si $u$ CPU trabajan a la vez durante $T_{\text{reloj}}$, entre todas entregan $u\cdot T_{\text{reloj}}$ de cálculo. Despejar $u$ da la división. Es aproximado: esperar la red o el disco no cuenta como CPU, y medir procesos hijos exige sumar su CPU.
:::

**Ejemplo paso a paso.** Celda 10.2: 4 tareas de cálculo puro de Python, de unos 0.5 s de CPU cada una, en una máquina de 8 CPU (cifras **medidas**).

1. **Hilos.** $T_{\text{reloj}}=2.20$ s y $T_{\text{cpu}}=2.14$ s → $u\approx2.14/2.20\approx0.97$ CPU: los 4 hilos se turnaron una sola CPU por el GIL.
2. **Procesos.** $T_{\text{reloj}}=1.09$ s y $T_{\text{cpu}}=3.69$ s sumando los 4 procesos → $u\approx3.69/1.09\approx3.4$ CPU. No llega a 4 porque arrancar los procesos también cuenta en el reloj.
3. **`joblib` (segunda llamada).** $T_{\text{reloj}}=0.92$ s y $T_{\text{cpu}}=3.21$ s → $u\approx3.5$ CPU. Es la misma idea que los procesos: `joblib` reparte las tareas entre procesos trabajadores, que se reutilizan entre llamadas, y por eso la segunda llamada arranca más rápido.
4. **Lectura.** Los hilos usaron una CPU; los procesos y `joblib`, casi cuatro. Es lo que predice la tabla.

## Katas

::: problem {#cmp-kata-p10-1 title="Kata 1 · 200 descargas de 0.3 s"}
Descargas 200 archivos. Cada uno tarda 0.3 s esperando la red y casi nada de CPU. Tienes 4 CPU lógicas. La API acepta 50 conexiones simultáneas. ¿Hilos, procesos o asyncio? ¿Cuántas en curso?
:::

::: answer {of="cmp-kata-p10-1"}
**Elige:** `asyncio` (o `ThreadPoolExecutor`) con un tope de 50 descargas en curso. **Porque:** es espera, no cálculo; la exclusión global y las CPU no limitan. Sin tope, las 200 a la vez serían $\lceil 200/200\rceil\times300=300$ ms, pero la API solo aguanta 50. Con tope 50: $\lceil 200/50\rceil\times300=4\times300=1200$ ms (1.2 s), frente a $200\times0.3=60$ s en secuencia. **Descarta:** procesos, pagan memoria y arranque sin calcular nada; subir el tope sin mirar el servidor remoto, que puede limitarte.
:::

::: problem {#cmp-kata-p10-2 title="Kata 2 · 8 imágenes de 2 s de cálculo"}
Procesas 8 imágenes. Cada una pide 2 s de cálculo en Python puro. Tienes 4 CPU lógicas libres. ¿Qué usas y cuánto tarda?
:::

::: answer {of="cmp-kata-p10-2"}
**Elige:** `ProcessPoolExecutor(4)`. **Porque:** es cálculo en Python, así que $p_{\text{ef}}=\min(4\text{ CPU},4\text{ procesos})=4$ y $T_{\text{ideal}}=\lceil 8/4\rceil\times2=4$ s. **Descarta:** hilos, la exclusión global deja $p_{\text{ef}}=1$ y son $8\times2=16$ s; 8 procesos, el límite sigue siendo 4 CPU, así que siguen siendo 4 s y gastas más memoria.
:::

::: problem {#cmp-kata-p10-3 title="Kata 3 · Servidor con --workers 4"}
Un servidor corre con `--workers 4`, GIL habilitado y $P=8$. Cada petición gasta 100 ms de cálculo en bytecode. Llegan 8 peticiones a la vez. ¿Cuánto tarda en atenderlas? ¿Ayuda añadir hilos dentro de cada worker?
:::

::: answer {of="cmp-kata-p10-3"}
**Elige:** leer el techo de la configuración, sin añadir hilos. **Porque:** $\min(P,N\cdot g)=\min(8,4\times1)=4$, así que $p_{\text{ef}}=4$ y $T_{\text{ideal}}=\lceil 8/4\rceil\times100=200$ ms. **Descarta:** más hilos por worker, no suman bytecode por el GIL; si quieres bajar a 100 ms necesitas `--workers 8`, con el costo de duplicar memoria.
:::

::: problem {#cmp-kata-p10-4 title="Kata 4 · Una operación larga de NumPy"}
Una sola llamada a NumPy tarda 2 s de reloj. Mides $T_{\text{cpu}}=7.6$ s. La máquina tiene 4 CPU lógicas. Piensas repartirla entre 4 procesos. ¿Conviene?
:::

::: answer {of="cmp-kata-p10-4"}
**Elige:** dejar la llamada como está. **Porque:** $u\approx7.6/2=3.8$, ya usa casi las 4 CPU lógicas de la máquina dentro de la operación, con código nativo que suelta el GIL. **Descarta:** procesos, no hay CPU libres que sumar y pagarías copia de datos; la trampa es creer que un solo proceso usa una sola CPU.
:::

## Si hay tiempo

Otros lenguajes reparten el trabajo de otras formas.

| Lenguaje | ¿Usa varias CPU? | En palabras simples |
|---|---|---|
| Go | Sí, por omisión | Las *goroutines* son tareas muy ligeras de Go. El runtime las reparte entre hilos. `GOMAXPROCS` fija cuántas ejecutan simultáneamente, no cuántas existen |
| Elixir y Erlang (BEAM) | Sí, por omisión | BEAM ejecuta estos lenguajes. Sus «procesos» son tareas muy ligeras, no procesos del sistema. Por omisión, usa un planificador por CPU lógica; `+S` lo cambia |
| Node.js | No para tu código | Un hilo ejecuta JavaScript y el sistema espera la red. Archivos y DNS usan 4 hilos internos. DNS busca la dirección de red de un nombre. Para más CPU: `worker_threads` o varios procesos |
| Java | Sí | Los hilos normales pertenecen al sistema. Los virtuales son ligeros y usan pocos hilos del sistema, llamados «portadores». No crean CPU nuevas |

## Notebook

- Celda 10.1, parte de hilos: lanza 4 hilos. Cada uno imprime el PID, número que identifica al proceso, y su hilo. Salida esperada: un solo PID repetido y cuatro nombres de hilo distintos.
- Celda 10.1, parte de procesos: lanza 2 procesos y cada uno imprime su PID. Salida esperada: dos PID distintos.
- Celda 10.2, «¿cuántas CPU usa cada herramienta?»: corre 4 hilos, 4 procesos y `joblib` con el mismo cálculo y mide reloj y CPU de cada uno. Salida esperada: con hilos, CPU ≈ reloj (unas 1 CPU efectiva); con procesos y con `joblib`, CPU varias veces mayor que el reloj (varias CPU efectivas).
