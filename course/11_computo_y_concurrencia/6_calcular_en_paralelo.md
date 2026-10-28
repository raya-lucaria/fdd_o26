---
id: calcular-en-paralelo
title: "Calcular en paralelo"
nav_title: "Calcular en paralelo"
summary: "Un cálculo dentro del event loop detiene a todas las tareas; la salida es mandarlo a un pool de procesos con run_in_executor. Cuánto rinden los procesos lo dicen el speedup, la eficiencia y la ley de Amdahl, y cuántos usar lo dice min(k, P)."
status: ready
estimated_time: 15m
tags: [procesos, run-in-executor, offload, speedup, amdahl, pool, arquitectura]
prerequisites: [pools-y-recursos]
---

# Calcular en paralelo

**Página 6 de 8 · Cómputo y concurrencia** · Pregunta: un servicio `asyncio` que atiende cientos de esperas recibe una petición que calcula 1.2 s en Python; ¿qué les pasa a las demás, a dónde se manda ese cálculo y cuántos procesos rinden? · Meta: sacar el cálculo del loop a un pool de procesos, medir lo que se gana con $S(N)$ y $E(N)$, y saber qué techo pone la fracción serial $f$.

| Término | Definición de una línea | Símbolo |
|---|---|---|
| cálculo en el loop | Código que ejecuta sin ningún `await` dentro de una corrutina: ninguna otra tarea del loop avanza mientras corre | `ready` de las demás |
| *offload* | Mandar el cálculo fuera del hilo del loop, a otro proceso, y esperar el resultado con `await` | — |
| serializar | Convertir un objeto en bytes para mandarlo a otro proceso (`pickle`) | parte de $h(k)$ |
| trabajadores | Hilos o procesos entre los que se reparte el trabajo | $N$ (en un pool, $N=k$) |
| speedup | Tiempo base declarado entre tiempo nuevo | $S(N)=T(1)/T(N)$ |
| eficiencia | Speedup por trabajador | $E(N)=S(N)/N$ |
| fracción serial | Parte de $T(1)$ que no se reparte | $f$ |
| ley de Amdahl | Speedup máximo cuando una fracción $f$ no se reparte | $S(N)=1/(f+(1-f)/N)$ |
| costo de repartir | Arrancar procesos, serializar, comunicar: crece con $k$ | $h(k)$ |

## En corto

- **Un cálculo dentro del loop no lo interrumpe nadie.** El loop es cooperativo: las respuestas que ya llegaron se quedan en `ready` hasta que el cálculo suelta el hilo. Con hilos, el intérprete pide soltar el GIL cada 5 ms aproximadamente; el loop no cambia de tarea hasta un `await`.
- **La salida es *offload*:** `await loop.run_in_executor(pool, calcula)` con un `ProcessPoolExecutor`. El cálculo pasa a otro proceso, con su propio GIL, y para el loop se vuelve una espera más. `to_thread` sirve para código bloqueante que **espera**, no para calcular en Python.
- **Repartir tiene costo y techo.** Los procesos cuestan arrancar y serializar ($h(k)$); la fracción serial $f$ pone el techo $1/f$; y más procesos que CPU no agregan capacidad: $k=\min(n,P)$.

## Un cálculo dentro del loop lo bloquea

::: definition {#cmp-def-calculo-en-el-loop title="Cálculo dentro del loop"}
Un tramo de código que **ejecuta sin llegar a un `await` que suspenda**, dentro de una corrutina que corre en el event loop. Mientras dura:

- el hilo del loop está ocupado por esa tarea, así que **ninguna otra tarea del loop ejecuta**;
- las tareas cuya espera ya terminó pasan de `wait` a `ready`: **pueden avanzar y no tienen turno**;
- nadie la saca: la planificación del loop es **cooperativa** y sólo recupera el control en un `await` que suspende o cuando la tarea termina.

Una llamada bloqueante (`time.sleep`, `requests.get`) produce el mismo efecto con `wait` en lugar de `exec`: la tarea no cede el hilo.
:::

**Otro ángulo.** El ejemplo único de la unidad con $\tau_3$ cambiada por un cálculo de 2000 ms sin `await` (traza ilustrativa, la de [[notacion-computo]]):

::: figure {#cmp-bloqueo-del-loop title="Un cálculo sin await detiene el loop"}
![Diagrama de Gantt con eje en milisegundos de 0 a 2200. Las corrutinas 1 y 2 ejecutan 20 ms, lanzan una petición y esperan 200 ms; la corrutina 3 calcula 2000 ms dentro del loop sin ningún await. Las respuestas llegan a los 220 y 240 ms, pero las corrutinas 1 y 2 quedan listas sin turno, rayadas, hasta los 2040 y 2060 ms, porque el loop no recupera el control hasta que el cálculo termina. Total 2080 ms; sin el cálculo en el loop, las dos peticiones terminan a los 240 y 260 ms.](_assets/cmp-bloqueo-del-loop.svg)
:::

Cómo leer la figura. Todo ocurre en **un hilo, el del loop, en una CPU**:

- **$[0,40)$:** el hilo ejecuta $\tau_1$ (0–20) y luego $\tau_2$ (20–40); cada una manda su petición y llega a un `await` que suspende. $\tau_2$ está en `ready` de 0 a 20 y $\tau_3$ de 0 a 40: pueden ejecutar, pero el único hilo está ocupado.
- **$[40,2040)$:** el hilo ejecuta el cálculo de $\tau_3$. $\tau_1$ está en `wait` hasta 220 ms (su respuesta viaja) y $\tau_2$ hasta 240 ms. Desde ahí las dos están en `ready` (rayadas): su respuesta ya está en el socket, pero el loop no puede pasarlas a ejecutar porque $\tau_3$ no llega a ningún `await` y nadie la saca del hilo.
- **$[2040,2080)$:** $\tau_3$ termina y suelta el hilo; el loop ejecuta $\tau_1$ (2040–2060) y después $\tau_2$ (2060–2080), en el orden en que quedaron listas.

| Planificación | Quién saca a una tarea de `exec` | Cada cuánto | Efecto de un cálculo de 2 s |
|---|---|---|---|
| hilos con GIL (preventiva) | el intérprete pide soltar el GIL | cada `sys.getswitchinterval()`, 5 ms por omisión (orientativo: una función interna larga puede excederlo) | los demás hilos reciben turnos; el cálculo no se acelera |
| event loop (cooperativa) | la propia tarea, en un `await` que suspende | nunca, si no hay `await` | ninguna otra tarea del loop ejecuta en 2 s |

**Matemática.** Con la partición $d=e+w+r$ de cada tarea ($b=0$):

| Tarea | $e$ (ms) | $w$ (ms) | $r$ (ms) | $d$ (ms) | sin el cálculo en el loop |
|---|---:|---:|---:|---:|---:|
| $\tau_1$ | 40 | 200 | 1820 | 2060 | 240 |
| $\tau_2$ | 40 | 200 | 1840 | 2080 | 260 |
| $\tau_3$ (cálculo) | 2000 | 0 | 40 | 2040 | — |

$C=40+40+2000=2080=T$, así que $U=C/(P\cdot T)=100\,\%$ con $P=1$. **La CPU nunca estuvo ociosa y las dos peticiones tardaron unas 8 veces más** (2060 contra 240 ms, 2080 contra 260). Utilización alta no es buen servicio: lo que creció fue $r$, el tiempo en `ready`.

**Ejemplo.** Medido (celda 6.1, abajo): una corrutina `latido` imprime cada 0.1 s y otra llama `calcula()` sin `await`. El latido se detiene **1.23 s**, lo que dura el cálculo, y luego vuelve a salir cada 0.1 s: ningún error, ningún aviso.

**Arquitectura · no calcules en el camino de la petición.**

| | |
|---|---|
| **Qué es** | En un servidor con event loop (Uvicorn, FastAPI con `async def`, aiohttp), el manejador sólo recibe, espera y responde; el cálculo de más de unas decenas de milisegundos sale del hilo del loop |
| **Por qué** | Un loop atiende **todas** las conexiones de su proceso. 2 s de cálculo en un manejador = 2 s sin atender a nadie: ni peticiones nuevas, ni respuestas que ya llegaron, ni el *health check* |
| **Cuándo sí calcular en el loop** | Cálculo de microsegundos o pocos milisegundos (parsear un JSON chico, validar un campo): mandarlo fuera cuesta más que hacerlo |
| **Qué cuesta no hacerlo** | La latencia de **todas** las peticiones del proceso sube a la del cálculo más largo; con $\lambda$ fijo, Little ($L=\lambda W$) dice que las conexiones en vuelo crecen igual |
| **Sistema real** | FastAPI corre en un pool de hilos los manejadores escritos con `def` (no `async def`) para no bloquear el loop; un `async def` que llama pandas o un modelo en Python bloquea el loop de su worker |

## La salida: mandar el cálculo a un proceso

::: definition {#cmp-def-offload title="Offload con run_in_executor"}
**Offload** es sacar un trabajo del hilo del loop y esperarlo como una espera más. `loop.run_in_executor(pool, f, *args)`:

1. manda `f(*args)` al *executor* `pool` (un `ThreadPoolExecutor` o un `ProcessPoolExecutor`; con `None`, el pool de hilos por omisión del loop);
2. **regresa de inmediato** con un futuro que se puede esperar con `await`;
3. con `await`, la corrutina se suspende y **devuelve el hilo del loop**; el loop sigue atendiendo otras tareas;
4. cuando `f` termina en el pool, el futuro se completa y la corrutina pasa a `ready`.

Con un `ProcessPoolExecutor`, `f` corre en **otro proceso**, con su propio intérprete y su propio GIL, en otra CPU.
:::

**Otro ángulo.** Tres formas de ejecutar el mismo trabajo desde una corrutina:

::: figure {#cmp-run-in-executor title="run_in_executor: el cálculo sale del hilo del loop"}
![Diagrama de Gantt con eje de 0 a 2500 ms y tres carriles. La corrutina ejecuta un instante, manda un cálculo de 2000 ms a un ProcessPoolExecutor con run_in_executor y espera el futuro con await. El carril del hilo del loop muestra un latido cada 100 ms que no se detiene durante los 2000 ms, porque el loop no calcula. El carril del proceso del pool calcula de 0 a 2000 ms en otra CPU con su propio GIL; al terminar, el resultado vuelve al loop y la corrutina se reanuda.](_assets/cmp-run-in-executor.svg)
:::

Cómo leer la figura. Hay **dos procesos en dos CPU**:

- **Hilo del loop (proceso principal, CPU 1):** la corrutina ejecuta un instante, llama `run_in_executor` y llega a `await`; desde ahí está en `wait`, porque espera un futuro que otro proceso va a completar, no CPU. El hilo queda libre y ejecuta el latido cada 100 ms: el latido pasa de `wait` (su `sleep`) a `ready` y a `exec` sin demora, porque nadie más retiene el hilo.
- **Proceso del pool (CPU 2):** ejecuta el cálculo de 0 a 2000 ms con su propio intérprete y su propio GIL; para él es `exec`. No compite con el hilo del loop porque es otro proceso en otra CPU.
- **Al terminar:** el resultado viaja serializado al proceso principal, el futuro se completa y la corrutina pasa a `ready`; en el siguiente turno del loop se reanuda.

| Desde una corrutina | Dónde corre | Sirve para | Con un cálculo en Python puro |
|---|---|---|---|
| `calcula()` directo | el hilo del loop | trabajo de microsegundos | **bloquea el loop** todo lo que dure |
| `await asyncio.to_thread(f)` | un hilo del pool por omisión, mismo proceso, mismo GIL | código bloqueante que **espera**: `requests.get`, leer un archivo, un driver de BD sin versión `async` | el loop recibe turnos (el intérprete pide soltar el GIL cada 5 ms aproximadamente), pero el cálculo **no se acelera**: dos cálculos en dos hilos tardan lo que dos en serie, y cada uno le disputa el GIL al hilo del loop |
| `await loop.run_in_executor(pool_de_procesos, f)` | otro proceso, otro GIL, otra CPU | **cálculo en Python** de decenas de milisegundos o más | el loop sigue libre y los cálculos corren en paralelo, hasta $\min(k,P)$ a la vez |

**Matemática.** Pon la frontera en las tareas del loop. Con *offload*, el cálculo de $\tau_3$ corre fuera del hilo del loop, así que **para el loop es `wait`**, como la red:

| Tarea | $e$ en el loop (ms) | $w$ (ms) | $d$ (ms) |
|---|---:|---:|---:|
| $\tau_1$ | 40 | 200 | 240 |
| $\tau_2$ | 40 | 200 | 260 (20 de `ready` al inicio) |
| $\tau_3$ | ≈ 0 | 2000 (el cálculo, en otro proceso) | ≈ 2040 + $h$ (40 de `ready` al inicio) |

$\tau_1$ y $\tau_2$ vuelven a 240 y 260 ms. El cálculo **no se acorta**: sigue tardando sus 2000 ms más el costo $h$ de mandarlo y traer el resultado. Lo que cambia es **quién lo paga**: sólo la petición que pidió el cálculo, no todas.

**Ejemplo.** Medido (celda 6.2): el mismo latido y el mismo `calcula()`, ahora con `run_in_executor` y un `ProcessPoolExecutor(max_workers=1)`. Los cinco latidos salen cada 0.1 s mientras el cálculo corre en otro proceso. El cálculo tardó un poco más que dentro del loop: ese tiempo incluye arrancar el proceso, mandarle la tarea y recibir el resultado (una corrida no permite repartir la diferencia entre esas tres cosas).

**Arquitectura · offload: loop + pool de procesos + cola.**

::: figure {#cmp-arq-offload title="Offload: el loop atiende, un pool de procesos calcula"}
![Arquitectura de offload. Los clientes llegan a un proceso principal con un event loop en un hilo, que atiende las conexiones y nunca calcula: el manejador hace await de loop.run_in_executor. El trabajo pasa por una cola interna, con los argumentos serializados con pickle, a un pool de P procesos, cada uno con su GIL y su CPU. El resultado vuelve serializado, completa un futuro y la corrutina se reanuda. Abajo, la versión en varias máquinas: API, cola externa como Redis o RabbitMQ, workers y almacén de resultados.](_assets/cmp-arq-offload.svg)
:::

| | |
|---|---|
| **Qué es** | Un proceso con event loop recibe las peticiones; un pool de procesos, creado **una vez** al arrancar el servicio, hace el cálculo; entre los dos hay una cola de trabajos |
| **Cuándo sí** | Servicio `async` con algunas rutas que calculan decenas de milisegundos o más en Python: generar un reporte, ajustar un modelo chico, procesar una imagen |
| **Cuándo no** | Cálculo de microsegundos (serializar cuesta más); cálculo que ya corre fuera del GIL en código compilado (NumPy grande): ahí basta un hilo; resultados de minutos (la petición HTTP no debe esperar tanto: cola externa y el cliente consulta después) |
| **Qué cuesta** | Arrancar los procesos (una vez), serializar argumentos y resultados (cada vez), memoria de $k$ intérpretes |
| **Sistema real** | En una máquina: `ProcessPoolExecutor` detrás de FastAPI. En varias: Celery con Redis o RabbitMQ como cola, workers en otras máquinas y un almacén de resultados |

**La cola del executor no tiene tope.** `submit` y `run_in_executor` **nunca bloquean** a quien manda: el `ProcessPoolExecutor` guarda en memoria todo lo pendiente. Si llegan 10 cálculos por segundo y el pool termina 4, la cola crece 6 por segundo y la latencia de cada cálculo crece con ella. **Delegar mueve la espera, no crea capacidad.** Acótala tú:

- un `asyncio.Semaphore(k)` antes de `run_in_executor` (la página [[concurrencia-acotada]]), o
- contar lo pendiente y responder `503` o `429` cuando pase de un tope (*backpressure*).

La capacidad de cálculo es $\lambda\le P/e$: con 8 CPU y 50 ms de CPU por petición (cifras supuestas), a lo más 160 peticiones de cálculo por segundo, con cualquier número de hilos o corrutinas.

## Lo que cuesta un proceso: arrancar y serializar

::: definition {#cmp-def-serializacion title="Serializar para cruzar entre procesos"}
Dos procesos **no comparten variables**. Todo lo que cruza de uno a otro se **serializa** (se convierte en bytes, en Python con `pickle`), viaja por una tubería del sistema operativo y se reconstruye del otro lado como **una copia**.

- **La función viaja por nombre**, no por código: `pickle` manda «módulo + nombre» y el hijo la importa. Por eso la función tiene que vivir en un módulo importable (`trabajo_computo.py`).
- **Una `lambda` o una función anidada no tiene un nombre importable**: `pickle` no la puede mandar.
- **Argumentos y resultado viajan copiados**, en los dos sentidos, cada llamada.
:::

**Otro ángulo.** Qué cruza y cómo:

| Lo que mandas | Cómo cruza | Costo | Si falla |
|---|---|---|---|
| `calcula`, definida en `trabajo_computo.py` | por nombre: el hijo hace `import trabajo_computo` | casi nada | — |
| una función definida en una celda | por nombre, en `__main__` del kernel | casi nada | con `spawn` o `forkserver` (macOS, Windows, Linux desde 3.14) el hijo no la encuentra |
| `lambda x: x * 2` o una función anidada | no tiene nombre importable | — | `PicklingError` al mandarla |
| el argumento `5_000_000` | copia serializada | unos bytes | — |
| un `DataFrame` de 1 GB | copia serializada, ida | proporcional al tamaño, más la memoria duplicada | memoria, lentitud |
| una variable global que el hijo modifica | no cruza: el hijo cambia **su** copia | — | el padre nunca ve el cambio |

**Matemática.** Los costos de repartir se juntan en $h(k)$. Unos son fijos (arrancar el pool una vez); otros crecen con $k$ y con lo que viaja:

$$T_{\text{real}}(k)\approx T_{\text{ideal}}(k)+h(k),\qquad h(k)=\text{arranque}(k)+\text{serializar ida y vuelta}+\text{IPC}$$

Un costo fijo cabe en la fracción serial $f$; uno que crece con $k$, no, y por eso el speedup medido queda debajo de la curva de Amdahl.

**Ejemplo.** Mediciones de referencia (una corrida, máquina de 8 CPU lógicas):

- crear un pool en cada una de 10 llamadas mínimas: 0.73 s; un pool para las 10: 0.07 s (la página [[pools-y-recursos]]). Arrancar procesos se paga **por pool**, no por llamada, si el pool se reutiliza;
- mandar una `lambda` a un `ProcessPoolExecutor`:

```text
PicklingError · Can't pickle <function <lambda> at 0x77c41e5440f0>: it's not found as __main__.<lambda>
```

**Arquitectura · qué mandar por la tubería.**

| | |
|---|---|
| **Qué es** | Diseñar la tarea para que viaje poco: mandar una ruta de archivo, un id, un rango de filas; que el hijo lea lo suyo y devuelva un resumen |
| **Cuándo sí** | Siempre que el dato sea grande respecto al cálculo |
| **Cuándo no basta** | Si cada tarea necesita el mismo dato grande, serializarlo $n$ veces domina $h$: memoria compartida (`multiprocessing.shared_memory`), un archivo en disco o un motor que ya calcule en paralelo por dentro (la página [[vectorizar]]) |
| **Qué cuesta** | Diseñar la partición del trabajo; perder la comodidad de «todo está en memoria» |
| **Sistema real** | Celery serializa los argumentos de cada tarea (JSON por omisión) y por eso se le manda el id de un registro, no el registro; Spark manda el código a donde están los datos |

## Speedup y eficiencia: cuánto rinden los procesos

::: definition {#cmp-def-speedup-base title="Speedup y eficiencia, con su base declarada"}
**En palabras.** El speedup dice cuántas veces más rápido terminó el lote con la versión nueva que con una base que siempre se declara; la eficiencia dice qué parte de cada trabajador se aprovechó.

**Formalmente.** $S=T_{\text{base}}/T_{\text{nueva}}$; con $N$ trabajadores, $S(N)=T(1)/T(N)$ y $E(N)=S(N)/N$. $S<1$ significa que empeoró; $E=1$ es reparto perfecto. Con un pool de $k$ procesos, $\operatorname{speedup}_{\text{pool}}(k)=T_{\text{pool}}(1)/T_{\text{pool}}(k)$ compara el pool contra sí mismo y esconde el costo de tener pool; $\operatorname{speedup}_{\text{aplicación}}(k)=T_{\text{secuencial}}/T_{\text{pool}}(k)$ compara contra la versión directa, sin pool. Modelo completo en [[notacion-computo]].
:::

**Otro ángulo.** Cuatro tareas de `calcula(5_000_000)` con un pool de 1, 2 y 4 procesos, en una máquina de 8 CPU lógicas (medición de referencia de [[notacion-computo]], una corrida; tus cifras serán otras):

| $k$ | $T_{\text{pool}}(k)$ (s) | $\operatorname{speedup}_{\text{pool}}(k)$ | $E(k)$ | ideal $T_{\text{pool}}(1)/k$ (s) |
|---:|---:|---:|---:|---:|
| 1 | 1.45 | 1 | 1 | 1.45 |
| 2 | 0.75 | $1.45/0.75\approx1.93$ | $\approx0.97$ | 0.725 |
| 4 | 0.54 | $1.45/0.54\approx2.69$ | $\approx0.67$ | 0.363 |

La salida de esa medición de referencia (`ProcessPoolExecutor(max_workers=k).map(calcula, [5_000_000] * 4)` con $k=1,2,4$):

```text
CPU lógicas: 8
1 proceso(s): 1.45 s
2 proceso(s): 0.75 s
4 proceso(s): 0.54 s
```

**Matemática.** Con tareas iguales e indivisibles, el reparto ideal acota: $S(N)\le\min(N,P,n)$. Aquí $n=4$, $P=8$: con $k=4$ el techo es 4 y se obtuvo 2.69. La distancia entre 0.54 s y 0.363 s es lo que costó repartir.

**Ejemplo.** Esta tabla da $\operatorname{speedup}_{\text{pool}}$, **no** $\operatorname{speedup}_{\text{aplicación}}$: no tiene una corrida de las 4 llamadas sin pool. Para saber si el pool le gana a no tener pool, mide también `for _ in range(4): calcula(5_000_000)` directo; la diferencia contra $T_{\text{pool}}(1)$ es el costo fijo del pool.

**Arquitectura · map-reduce en una máquina.**

| | |
|---|---|
| **Qué es** | Partir el trabajo en trozos independientes (*map*, en el pool), y juntar los resultados en el padre (*reduce*: una suma, un `concat`) |
| **Cuándo sí** | Trozos independientes, de cálculo largo respecto a lo que viaja: simular 1000 escenarios, procesar 200 archivos, ajustar un modelo por cliente |
| **Cuándo no** | Trozos que dependen unos de otros; un *reduce* caro (juntar 4 `DataFrame` grandes copia todo de vuelta) |
| **Qué cuesta** | Partir, serializar y juntar son **fracción serial**: corren en el padre, uno tras otro |
| **Sistema real** | `ProcessPoolExecutor.map`, `multiprocessing.Pool.map`; a escala de varias máquinas, Spark (fuera de alcance) |

## Amdahl: el techo que pone la fracción serial

::: definition {#cmp-def-amdahl title="Fracción serial y ley de Amdahl"}
**En palabras.** La fracción serial $f$ es la parte del tiempo con un trabajador que no se puede repartir. Si el resto se reparte perfectamente, el speedup queda acotado por $1/f$ aunque se agreguen trabajadores sin límite.

**Formalmente.** Con $f\in[0,1]$ la fracción serial de $T(1)$:

$$T(N)=T(1)\left(f+\frac{1-f}{N}\right),\qquad S(N)=\frac{1}{f+(1-f)/N},\qquad \lim_{N\to\infty}S(N)=\frac{1}{f}$$

Modelo completo en [[notacion-computo]]. **Supuestos:** carga fija; $f$ constante; la parte repartible se divide tanto como haga falta; trabajadores equivalentes; $N\le P$; ningún costo que crezca con $N$. Si alguno falla, $T_{\text{real}}(N)=T(1)\,(f+(1-f)/N)+h(N)$.
:::

**Otro ángulo.** La curva para tres valores de $f$:

::: figure {#cmp-amdahl title="Speedup teórico de Amdahl según la fracción serial"}
![Gráfica de la ley de Amdahl. Eje horizontal: N, número de trabajadores, de 1 a 16. Eje vertical: speedup, tiempo con 1 entre tiempo con N. Una diagonal punteada marca el speedup ideal igual a N. Tres curvas teóricas uno entre f más uno menos f sobre N: con f igual a 0.1 su techo es 10, con f igual a 0.25 su techo es 4, con f igual a 0.5 su techo es 2. Cada curva sube rápido con pocos trabajadores y se aplana hacia su techo. Modelo ideal: carga fija, fracción serial constante y sin costos que crezcan con N.](_assets/cmp-amdahl.svg)
:::

| $f$ | $S(2)$ | $S(4)$ | $S(8)$ | techo $1/f$ |
|---:|---:|---:|---:|---:|
| 0.10 | 1.82 | 3.08 | 4.71 | 10 |
| 0.25 | 1.60 | 2.29 | 2.91 | 4 |
| 0.50 | 1.33 | 1.60 | 1.78 | 2 |

Con $f=0.25$, pasar de 4 a 8 trabajadores multiplica el speedup por $2.91/2.29\approx1.27$: el doble de procesos da 27 % más.

**Matemática.** Una carga **sólo de CPU** (traza ilustrativa de [[notacion-computo]], distinta del ejemplo de espera): $\tau_1$ prepara 40 ms en serie; $\tau_2$ y $\tau_3$ calculan 100 ms cada una y dependen de $\tau_1$.

| | Cuenta | Resultado |
|---|---|---|
| una CPU | $T(1)=40+100+100$ | 240 ms |
| fracción serial | $f=40/240$ | $1/6$ |
| dos CPU, Amdahl | $T(2)=240\,(1/6+(5/6)/2)$ | 140 ms |
| speedup | $S(2)=240/140=12/7$ | $\approx1.71$ |
| con 20 ms de gestión del pool | $T_{\text{pool}}(2)=140+20$; $\operatorname{speedup}_{\text{aplicación}}(2)=240/160$ | 160 ms; 1.50 |
| si el pool de uno también cuesta 20 | $T_{\text{pool}}(1)=260$; $\operatorname{speedup}_{\text{pool}}(2)=260/160$ | 1.625 |
| techo algebraico | $1/f$ | 6 |

El techo 6 **sólo vale si los 200 ms repartibles se pueden seguir partiendo**. Con $\tau_2$ y $\tau_3$ indivisibles, $S\le\min(N,P,n)$ con $n=2$ tareas repartibles: más de dos CPU no bajan de 140 ms.

**Ejemplo · ajuste ilustrativo con la medición, no una medición de $f$.** Se ajusta $T(N)=a+b/N$ a la tabla de speedup:

- de $a+b=1.45$ y $a+b/2=0.75$ salen $b=2\times(1.45-0.75)=1.40$ y $a=0.05$;
- predice $T(4)=0.05+1.40/4=0.40$ s; se midió 0.54 s;
- leído con Amdahl, $f=a/T(1)\approx0.034$ y techo $1/f\approx29$.

El punto que quedaba para comprobar el modelo lo contradice. Por qué es sólo ilustración:

- son **3 puntos para 2 parámetros**: queda un solo grado de libertad para comprobar el modelo;
- es **una corrida**: el ruido entre corridas puede mover cada $T(N)$ algunas centésimas;
- los 0.14 s que $T(4)$ queda por encima de la predicción son compatibles con un $h(k)$ que crece con $k$ (arranque de procesos e IPC), pero eso es una **hipótesis**: Amdahl no lo modela, así que $a$ mezcla parte serial con costos de repartir;
- con $n=4$ tareas indivisibles, el techo real es 4 aunque la cuenta diga 29.

**Arquitectura · antes de repartir, achica $f$ y $T(1)$.**

| | |
|---|---|
| **Qué es** | Medir qué parte del trabajo es serial (leer el archivo, partir, juntar) antes de comprar procesos; el techo $1/f$ no lo mueve ningún $N$ |
| **Cuándo sí repartir** | $f$ pequeña, trozos independientes y largos, $N\le P$ |
| **Cuándo no** | $f$ grande (el paso serial domina); cuando otra implementación baja $T(1)$ más que cualquier reparto. Amdahl compara una implementación consigo misma: vectorizar (la página [[vectorizar]]) cambia $T(1)$, no $N$ |
| **Qué cuesta** | Cada proceso: memoria, arranque, serialización. El último proceso agregado rinde menos que el primero |
| **Sistema real** | Un ETL que lee un CSV de 10 GB en un solo hilo y luego reparte el cálculo: la lectura es $f$; Polars o un formato columnar (Parquet) la reducen antes de pensar en procesos |

## Cuántos procesos

::: definition {#cmp-def-cuantos-procesos title="Tiempo de un pool de procesos, T_pool(k)"}
**En palabras.** $T_{\text{pool}}(k)$ es lo que tarda un lote de tareas de cálculo en un pool de $k$ procesos: a lo más $\min(k,P)$ ejecutan a la vez, así que el lote sale en tandas, más el costo de repartir; más procesos que CPU no bajan el piso.

**Formalmente.** Para $n$ tareas iguales, independientes, indivisibles y sólo de CPU, de duración $c$, con $P$ CPU lógicas:

$$T_{\text{pool}}(k)\approx\left\lceil \frac{n}{\min(k,P)}\right\rceil c+h(k),\qquad T\ge\frac{n\,c}{P}$$

La regla práctica es $k=\min(n,P)$. Modelo completo en [[notacion-computo]].
:::

**Otro ángulo.** $n=3$ tareas de $c=400$ ms, $h=0$ (traza ilustrativa de [[notacion-computo]]):

| $k$ | $P$ | Cuenta | $T$ (ms) | $S$ | $E$ |
|---:|---:|---|---:|---:|---:|
| 1 | 8 | $\lceil3/1\rceil\times400$ | 1200 | 1 | 1 |
| 2 | 8 | $\lceil3/2\rceil\times400$ | 800 | 1.5 | 0.75 |
| 3 | 8 | $\lceil3/3\rceil\times400$ | 400 | 3 | 1 |
| 4 | 8 | $\lceil3/4\rceil\times400$ | 400 | 3 | 0.75 |
| 3 | 2 | $T\ge3\times400/2$ | $\ge600$ | $\le2$ | — |

Con $k=2$ la tercera tarea corre sola en una segunda tanda: **la granularidad, no Amdahl, fija el 1.5**. Con $k=4$ sobra un proceso que no tiene qué hacer.

**Matemática · más procesos que CPU no suma.** Con $n=16$ tareas de $c$ y $P=8$:

| $k$ | $\min(k,P)$ | $T_{\text{pool}}(k)$ |
|---:|---:|---|
| 8 | 8 | $\lceil16/8\rceil c+h(8)=2c+h(8)$ |
| 16 | 8 | $\ge 16c/8=2c$, más $h(16)>h(8)$ |

Los 8 procesos extra se turnan por las mismas 8 CPU: el piso $n\,c/P$ no cambia y el costo de repartir sí crece. **Esta regla es de trabajo que calcula.** Para esperar, 100 hilos o 1000 corrutinas es válido: mientras esperan no ocupan CPU.

**Ejemplo.** En la medición de referencia, $n=4$ y $P=8$: la regla da $k=\min(4,8)=4$, el mayor que se midió. Un quinto proceso no tendría tarea.

**Arquitectura · cuántos workers.**

| | |
|---|---|
| **Qué es** | Fijar $k$ con $P$ y con $n$, no con el tráfico: el pool de cálculo lo limita la CPU, el de conexiones lo limita la BD (la página [[pools-y-recursos]]) |
| **Cuándo sí $k=P$** | Servicio dedicado a calcular, con trabajo suficiente para todas las CPU |
| **Cuándo menos** | Si en la misma máquina corren el loop, la BD u otros servicios: reserva CPU para ellos. Si $n<P$, $k=n$ |
| **Qué cuesta equivocarse** | $k$ grande: memoria de $k$ intérpretes, cambios de contexto, $h(k)$; $k$ chico: CPU ociosa |
| **Sistema real** | `ProcessPoolExecutor()` sin `max_workers` usa `os.process_cpu_count()` (3.13+). En un contenedor con `--cpus 2` sobre una máquina de 8, `os.cpu_count()` sigue diciendo 8: fija $k$ con la cuota. Gunicorn sugiere `2 × núcleos + 1` workers *sync*, pero esos workers también esperan red; para cálculo puro, $k=P$ |

**Procesos: cuándo sí y cuándo no.**

| Situación | Procesos | En su lugar |
|---|---|---|
| cálculo en Python puro, largo, en tareas independientes | **sí**, $k=\min(n,P)$ | — |
| cálculo largo dentro de un servicio `async` | **sí**, con `run_in_executor` y una cola acotada | — |
| cálculo sobre arreglos numéricos | todavía no | vectorizar primero ([[vectorizar]]) |
| esperas de red o disco | no: arranque y copia sin ganancia | hilos, `asyncio` |
| código bloqueante que espera, dentro de `asyncio` | no | `asyncio.to_thread` |
| cálculo de microsegundos | no: serializar cuesta más | directo |
| tareas que comparten y modifican un mismo dato grande | con cuidado | memoria compartida, una BD o rediseñar la partición |

## La decisión hasta aquí

| Si el trabajo… | Haz | Por qué | Página |
|---|---|---|---:|
| casi sólo espera ($\rho$ pequeño) | reorganizar las esperas, no acelerar la CPU | la CPU del cliente es una fracción mínima de $T$ | 1 |
| espera, en pocas decenas, con librería bloqueante | hilos | el GIL se suelta mientras cada hilo espera | 2 |
| espera, en cientos o miles, con librería `async` | `asyncio` + `gather` | una corrutina en espera cuesta mucho menos que un hilo | 3 |
| hace muchas llamadas a una dependencia | `Semaphore(k)`, $k$ medido | $\lambda\le k/W$; no tumbar al otro lado | 4 |
| habla muchas veces con el mismo host o BD | un pool de conexiones, dimensionado con Little | reutilizar conexiones; conexiones en uso $=\lambda W$ | 5 |
| **calcula más de unas decenas de ms dentro de un servicio `async`** | **`run_in_executor` + `ProcessPoolExecutor` creado una vez, con la cola acotada** | **el loop no se detiene; delegar no crea capacidad** | **6** |
| **llama código bloqueante que espera, dentro de `asyncio`** | **`asyncio.to_thread`** | **un hilo basta para esperar; no sirve para calcular en Python** | **6** |
| **calcula en Python puro, en tareas independientes** | **pool de $k=\min(n,P)$ procesos; medir $f$ antes** | **paralelo exige otro GIL; techo $1/f$; más procesos que CPU no suma** | **6** |

## Código

Tres celdas: el latido que se detiene con un cálculo en el loop, el mismo latido con el cálculo en otro proceso, y la tabla de Amdahl. **El servidor no hace falta en esta página**: todo es cálculo local. `calcula` vive en `trabajo_computo.py` porque un proceso hijo la importa por nombre.

**Haz (celda 6.1):** un latido cada 0.1 s y, en el mismo loop, un cálculo sin `await`.

```python
import asyncio
import time
from trabajo_computo import calcula

async def latido(veces):
    for i in range(veces):
        print(f"{time.perf_counter() - t0:4.2f} s  latido {i}")
        await asyncio.sleep(0.1)                   # cede el loop 0.1 s
async def calculo():
    await asyncio.sleep(0.15)                      # deja salir dos latidos antes
    inicio = time.perf_counter()
    calcula()                                      # ~2 s de Python sin ningún await
    print(f"      el cálculo duró {time.perf_counter() - inicio:.2f} s sin ceder el hilo")
t0 = time.perf_counter()
await asyncio.gather(latido(5), calculo())         # las dos, en el mismo loop
```

> [!NOTE]
> **Python que quizá no has visto.**
>
> - `async def`: define una corrutina; al llamarla no corre, devuelve un objeto que el loop agenda. Aquí hace falta para que `latido` pueda ceder el hilo en cada `await`.
> - `await asyncio.sleep(0.1)`: suspende la corrutina 0.1 s y devuelve el hilo al loop. Es el único punto donde `latido` deja correr a otra tarea.
> - `await asyncio.gather(a, b)`: agenda las dos corrutinas como tareas del mismo loop y espera a ambas. `await` suelto funciona porque el notebook ya tiene un loop corriendo; `asyncio.run` truena ahí.

**Qué pasó.** Gantt simplificado, en segundos (los bordes salen de la salida de abajo):

| | 0–0.15 | 0.15 → fin del cálculo | después |
|---|---|---|---|
| `latido` | latidos 0 y 1 | **`ready`**: su `sleep(0.1)` venció y no tiene turno | latidos 2, 3, 4 cada 0.1 s |
| `calculo` | `wait` (`asyncio.sleep(0.15)`) | **`exec`**: `calcula()`, 1.23 s | terminada |
| hilo del loop | alterna | **ocupado por `calcula()`** | alterna |

**Deberías ver** (en la máquina del profesor; tus segundos cambian, la forma no):

```text
0.00 s  latido 0
0.10 s  latido 1
      el cálculo duró 1.23 s sin ceder el hilo
1.38 s  latido 2
1.48 s  latido 3
1.59 s  latido 4
```

- Entre `latido 1` y `latido 2` pasan $1.38-0.10=1.28$ s, no 0.1 s: 0.05 s antes de que empiece el cálculo y 1.23 s de cálculo.
- No hubo error ni aviso: un loop bloqueado sólo se nota en la latencia.

**Haz (celda 6.2):** el mismo latido (de la celda 6.1), con el cálculo en un proceso del pool.

```python
import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from trabajo_computo import calcula

async def calculo_fuera(pool):
    await asyncio.sleep(0.15)                      # el mismo arranque que en 6.1
    loop = asyncio.get_running_loop()              # el loop que corre esta celda
    inicio = time.perf_counter()
    await loop.run_in_executor(pool, calcula)      # calcula en otro proceso; el loop sigue
    print(f"      el cálculo duró {time.perf_counter() - inicio:.2f} s en otro proceso")

t0 = time.perf_counter()
with ProcessPoolExecutor(max_workers=1) as pool:   # un proceso hijo, con su propio GIL
    await asyncio.gather(latido(5), calculo_fuera(pool))
```

> [!NOTE]
> **Python que quizá no has visto.**
>
> - `ProcessPoolExecutor(max_workers=1)`: un pool con un proceso hijo. El `with` lo cierra al final y espera a que el hijo termine. Hace falta un proceso, no un hilo, porque `calcula` es Python puro y un hilo compartiría el GIL.
> - `asyncio.get_running_loop()`: devuelve el loop que está corriendo la celda; `run_in_executor` es un método del loop.
> - `await loop.run_in_executor(pool, calcula)`: manda `calcula` al pool (por nombre, con `pickle`) y regresa un futuro; el `await` suspende a `calculo_fuera` y libera el hilo del loop mientras el hijo calcula. Se pasa `calcula`, no `calcula()`: con paréntesis se ejecutaría aquí, en el loop.

**Qué pasó.**

| | 0–0.15 | 0.15 → fin del cálculo | después |
|---|---|---|---|
| `latido` | latidos 0 y 1 | latidos 2, 3, 4 cada 0.1 s | terminada |
| `calculo_fuera` | `wait` | **`wait`** para el loop: espera el futuro | imprime y termina |
| proceso hijo | arranca | **`exec`**: `calcula()` en otra CPU | — |
| hilo del loop | alterna | **libre**: atiende a `latido` | — |

**Deberías ver:**

```text
0.00 s  latido 0
0.10 s  latido 1
0.20 s  latido 2
0.30 s  latido 3
0.40 s  latido 4
      el cálculo duró 1.28 s en otro proceso
```

- Los cinco latidos salen cada 0.1 s: el loop no se enteró del cálculo.
- El cálculo tardó un poco más que en la celda 6.1: incluye arrancar el proceso (el pool lo crea en el primer envío), mandar la tarea y traer el resultado.

**Haz (celda 6.3):** la tabla de Amdahl con una función de tres líneas.

```python
def amdahl(f, N):
    """Speedup con fracción serial f y N trabajadores (reparto perfecto)."""
    return 1 / (f + (1 - f) / N)

for f in (0.10, 0.25, 0.50):
    fila = [f"{amdahl(f, N):.2f}" for N in (2, 4, 8)]     # S(2), S(4), S(8)
    print(f"f={f:.2f} {fila} techo: {1 / f:.1f}")
print("f=0.25, de 4 a 8 trabajadores:", round(amdahl(0.25, 8) / amdahl(0.25, 4), 2), "veces más")
```

> [!NOTE]
> **Python que quizá no has visto.**
>
> - `[... for N in (2, 4, 8)]`: una lista por comprensión; arma la fila de speedups con $N=2,4,8$ en una línea.
> - `f"{x:.2f}"`: formatea un número con dos decimales.

**Qué pasó.** La función es la fórmula tal cual; no mide nada. Cada fila es una curva de la figura de Amdahl evaluada en 2, 4 y 8, y el techo es $1/f$. La última línea muestra lo que rinde duplicar los trabajadores cuando $f=0.25$.

**Deberías ver:**

```text
f=0.10 ['1.82', '3.08', '4.71'] techo: 10.0
f=0.25 ['1.60', '2.29', '2.91'] techo: 4.0
f=0.50 ['1.33', '1.60', '1.78'] techo: 2.0
f=0.25, de 4 a 8 trabajadores: 1.27 veces más
```

- Con $f=0.5$, 8 trabajadores no llegan a 2.
- El doble de procesos con $f=0.25$ da 1.27 veces más, no 2.

La versión larga y paso a paso está en el notebook, tema 6.

## Al diseñar / al revisar código de IA, busca…

- **Un bucle de cálculo, pandas fila por fila o un modelo en Python dentro de un `async def`.** Bloquea el loop de todo el proceso; pide `run_in_executor` con un `ProcessPoolExecutor`.
- **`asyncio.to_thread(calcula)` presentado como solución a un cálculo en Python.** Mantiene al loop con turnos, pero no acelera nada: el hilo comparte el GIL.
- **`run_in_executor` sin tope delante.** La cola del executor no tiene límite; pide un `Semaphore` o un rechazo `503`/`429`.
- **Un `ProcessPoolExecutor` creado dentro del manejador o del bucle.** Arrancar procesos se paga en cada petición; el pool se crea una vez.
- **Una `lambda`, una función anidada o una función de la celda enviada a procesos.** `pickle` no la manda o el hijo no la encuentra; debe vivir en un módulo importable.
- **Un `DataFrame` grande como argumento de cada tarea.** Se serializa y se copia cada vez; manda una ruta, un id o un rango.
- **`max_workers` mayor que las CPU para trabajo que calcula, o fijado con `os.cpu_count()` dentro de un contenedor con cuota.** Más procesos que CPU no suma.
- **«4 procesos, 4 veces más rápido».** Pide la tabla $T(1)$, $T(2)$, $T(4)$ con su base declarada y la fracción serial; el speedup del pool no es el de la aplicación.

Sigue con [[vectorizar]].
