---
id: notacion-computo
title: "El modelo matemático"
nav_title: "Modelo matemático"
summary: "La página 0 de Cómputo y concurrencia, para leer antes que las demás. Define cada objeto de la unidad en palabras, en fórmula y en el Gantt: tarea, vida, los cuatro estados, ρ, secuencial, concurrente y paralelo, asíncrono, GIL, speedup, Amdahl, Little y la cota del semáforo. Todo se evalúa con un solo ejemplo de tres tareas."
status: ready
tags: [concurrencia, notacion, modelo-matematico, gantt, amdahl, little]
prerequisites: [computo-y-concurrencia]
---

# El modelo matemático

**Página 0 · Cómputo y concurrencia** (se lee primero) · Pregunta: ¿qué significa exactamente cada palabra y cada símbolo que usan las ocho páginas? · Meta: que cualquier Gantt de la unidad se pueda verificar con estas definiciones y una cuenta.

Cada concepto va en un bloque con tres líneas: **En palabras**, **Formalmente** y **En el Gantt**. Las páginas 1–8 repiten las dos primeras, con las mismas palabras, donde usan el concepto. Si una página dice otra cosa, **manda esta**.

## Todos los símbolos

| Símbolo | Significado | Se usa en la página |
|---|---|---|
| $t$, $[a,b)$ | un instante; intervalo que incluye $a$ y excluye $b$ | 1–8 |
| $\operatorname{dur}(X)$ | duración total de un conjunto de instantes | 1, 2 |
| $\mathcal{T}=\{\tau_1,\dots,\tau_n\}$ | las $n$ tareas observadas | 1–8 |
| $\operatorname{arrival}$, $\operatorname{start}$, $\operatorname{end}$ | llega la solicitud, el sistema la admite, termina | 1, 4, 5 |
| $\operatorname{vida}(\tau)$, $d$ | $[\operatorname{start},\operatorname{end})$ y su duración | 1, 2 |
| $\operatorname{latencia}(\tau)$ | $\operatorname{end}-\operatorname{arrival}$ | 1, 8 |
| $\operatorname{exec}$, $e$ | instantes en que una CPU corre la tarea, y su duración | 1–3 |
| $\operatorname{wait}$, $w$ | instantes en que espera algo externo al programa | 1–3 |
| $\operatorname{ready}$, $r$ | instantes en que podría avanzar y no tiene turno | 1–3, 6 |
| $\operatorname{blocked}$, $b$ | instantes en que espera algo que otra tarea del programa debe soltar | 2, 4, 5 |
| $\rho$ | $e/d$ con la tarea sola | 1, 6 |
| $T$, $C$, $U$ | duración del lote, CPU del lote, utilización | 1–3 |
| $P$, $\operatorname{ExecutingAt}(t)$ | CPU lógicas; tareas que ejecutan en $t$ | 2, 6 |
| $\operatorname{hilo}(\tau)$ | hilo del sistema operativo que ejecuta $\tau$ | 3 |
| $\operatorname{exec}_{\mathrm{Python}}$ | la parte de la ejecución que corre bytecode de Python | 2, 6 |
| $N$, $k$ | trabajadores; tope real (permisos, conexiones, procesos) | 2, 4–6 |
| $S$, $S(N)$, $E(N)$ | speedup con base declarada; contra un trabajador; eficiencia | 2, 6 |
| $T_{\text{pool}}(k)$, $h(k)$ | tiempo con un pool de $k$; costos que crecen con $k$ | 6 |
| $f$ | fracción serial (Amdahl) | 6 |
| $L$, $\lambda$, $W$ | en vuelo, rendimiento, tiempo dentro (Little) | 1, 3–5, 8 |
| $W_{\text{recurso}}$, $W_{\text{conexión}}$ | tiempo que una tarea retiene un recurso | 5 |
| $\lceil n/k\rceil\cdot(e+w)$ | cota del semáforo | 4, 5 |

## Convenciones

- **Frontera.** Se observa un sistema elegido, casi siempre el cliente. La CPU del servidor remoto no es CPU del cliente: desde el cliente, el trabajo del servidor es espera.
- **Granularidad.** Se fija un conjunto de tareas y se compara siempre sobre ese mismo conjunto. Cada tarea es **un flujo secuencial**: ocupa a lo más una CPU a la vez. Si por dentro reparte trabajo, sus subtareas son otro conjunto, a otra escala.
- **Unidades.** Las trazas ilustrativas van en milisegundos; las mediciones reales, en segundos.
- **Dibujo.** Ejecuta relleno, espera con contorno, lista rayada, bloqueada en ámbar; una fila por tarea y una fila por CPU (o por hilo del loop, o por GIL), rotulada.

**El ejemplo único.** Tres tareas iguales; cada una **ejecuta 20 ms, espera 200 ms la red y ejecuta 20 ms**. Es una traza ilustrativa, no una medición. Las tres llegan en $t=0$. Los mini-ejemplos de abajo salen de él; la evaluación completa está al final.

## Tiempo e intervalo semiabierto

::: definition {#cmp-def-mod-intervalo title="Instante, intervalo semiabierto y duración"}
**En palabras.** Un instante es un punto del reloj; un intervalo $[a,b)$ incluye su inicio y excluye su fin, así que dos intervalos que se tocan en un borde no se solapan.

**Formalmente.** $\operatorname{dur}(X)$ suma las longitudes de los intervalos disjuntos que forman $X$:

$$[a,b)=\{t\ge0 : a\le t<b\}$$

**En el Gantt.** El eje horizontal es $t$. Una barra que acaba en $x=240$ y otra que empieza en $x=240$ se tocan y no se solapan.
:::

**Mini-ejemplo.** $[0,240)\cap[240,480)=\varnothing$: el instante 240 es de la segunda tarea. $\operatorname{dur}([0,20)\cup[220,240))=40$ ms: lo que ejecuta $\tau_1$.

## Tarea y vida

::: definition {#cmp-def-mod-tarea title="Tarea, vida y latencia"}
**En palabras.** Una tarea es un flujo secuencial de trabajo con inicio y fin, observado desde un sistema elegido (casi siempre el cliente); vive desde que ese sistema la admite hasta que termina, y su latencia suma además la cola previa.

**Formalmente.** Con $\mathcal{T}=\{\tau_1,\dots,\tau_n\}$ y $\operatorname{arrival}(\tau)\le\operatorname{start}(\tau)<\operatorname{end}(\tau)$:

$$\operatorname{vida}(\tau)=[\operatorname{start}(\tau),\operatorname{end}(\tau)),\qquad d(\tau)=\operatorname{end}-\operatorname{start},\qquad \operatorname{latencia}(\tau)=\operatorname{end}-\operatorname{arrival}$$

**En el Gantt.** Una fila por tarea; la vida va del borde izquierdo de su primera barra al borde derecho de la última. La cola previa ($\operatorname{start}-\operatorname{arrival}$) no aparece en su fila.
:::

| Instante | Qué marca | En una API |
|---|---|---|
| $\operatorname{arrival}(\tau)$ | llega la solicitud | el cliente envía la petición |
| $\operatorname{start}(\tau)$ | el sistema observado **admite** la tarea | en `asyncio`, al crear la `Task`; con hilos, al arrancar el hilo; en un servidor, cuando un hilo toma la conexión |
| $\operatorname{end}(\tau)$ | termina | sale la última respuesta |

**Mini-ejemplo.** En secuencia, $\tau_3$ llega en 0, la admiten en 480 y termina en 720: $d=240$, $\operatorname{latencia}=720$, cola $=480$. Dos tercios de su latencia ($480/720$) son cola.

## Ejecución

::: definition {#cmp-def-mod-exec title="Ejecución"}
**En palabras.** La tarea ejecuta cuando una CPU corre sus instrucciones: parsear un JSON, un bucle.

**Formalmente.**

$$\operatorname{exec}(\tau)\subseteq\operatorname{vida}(\tau),\qquad e=\operatorname{dur}(\operatorname{exec}(\tau))$$

**En el Gantt.** Barra rellena en la fila de la tarea, y el mismo tramo ocupado en una fila de CPU.
:::

**Mini-ejemplo.** $\operatorname{exec}(\tau_1)=[0,20)\cup[220,240)$, $e=40$ ms.

## Espera

::: definition {#cmp-def-mod-wait title="Espera"}
**En palabras.** La tarea espera cuando le falta algo externo al programa: la red, el disco, un temporizador.

**Formalmente.**

$$\operatorname{wait}(\tau)\subseteq\operatorname{vida}(\tau),\qquad w=\operatorname{dur}(\operatorname{wait}(\tau))$$

**En el Gantt.** Barra con contorno y sin relleno; la fila de CPU no la cuenta.
:::

**Mini-ejemplo.** $\operatorname{wait}(\tau_1)=[20,220)$, $w=200$ ms. `time.sleep` y `asyncio.sleep` también son `wait`: esperan un temporizador.

## Lista

::: definition {#cmp-def-mod-ready title="Lista"}
**En palabras.** La tarea está lista cuando podría avanzar pero no tiene turno: le falta una CPU, el GIL o el hilo del loop.

**Formalmente.**

$$\operatorname{ready}(\tau)\subseteq\operatorname{vida}(\tau),\qquad r=\operatorname{dur}(\operatorname{ready}(\tau))$$

**En el Gantt.** Barra rayada.
:::

**Mini-ejemplo.** Con `gather` en un hilo, $\tau_3$ nace en 0 y el hilo lo tienen $\tau_1$ y luego $\tau_2$: $\operatorname{ready}(\tau_3)=[0,40)$, $r=40$ ms.

## Bloqueada

::: definition {#cmp-def-mod-blocked title="Bloqueada"}
**En palabras.** La tarea está bloqueada cuando espera algo que otra tarea del mismo programa tiene que soltar o producir: un permiso, un `Lock`, una conexión del pool, un resultado.

**Formalmente.**

$$\operatorname{blocked}(\tau)\subseteq\operatorname{vida}(\tau),\qquad b=\operatorname{dur}(\operatorname{blocked}(\tau))$$

**En el Gantt.** Franja ámbar («espera permiso»), distinta del contorno de la espera de red.
:::

**Mini-ejemplo.** Con `Semaphore(2)`, $\tau_3$ pide permiso en 40, no hay, y lo recibe en 240 cuando $\tau_1$ sale: $\operatorname{blocked}(\tau_3)=[40,240)$, $b=200$ ms. Quien hace `await gather(…)` también está bloqueada: espera resultados de otras tareas del programa.

## Partición y prueba operativa

::: definition {#cmp-def-mod-particion title="Partición de la vida"}
**En palabras.** En cada instante de su vida una tarea está en exactamente uno de los cuatro estados, así que las cuatro duraciones suman la vida.

**Formalmente.** ($\sqcup$: unión de conjuntos disjuntos)

$$\operatorname{vida}(\tau)=\operatorname{exec}(\tau)\sqcup\operatorname{wait}(\tau)\sqcup\operatorname{ready}(\tau)\sqcup\operatorname{blocked}(\tau)\quad\Rightarrow\quad d=e+w+r+b$$

**En el Gantt.** Un trazo vertical dentro de la vida de una tarea cruza exactamente una barra de su fila.
:::

**La prueba operativa** para clasificar un tramo:

1. «Si ahora mismo le doy una CPU libre, y con ella el GIL y el hilo del loop, ¿avanza?» **Sí → `ready`.**
2. Si no avanza, ¿qué tiene que ocurrir? Algo fuera del programa (llega un paquete, termina el disco, vence un temporizador) → **`wait`**. Otra tarea del programa suelta un permiso, un lock o una conexión, o entrega un resultado → **`blocked`**.

Dos consecuencias:

- **Esperar el GIL es `ready`**, no `blocked`: el GIL es parte del turno de ejecución, como la CPU.
- **`time.sleep` dentro del loop** deja a esa tarea en `wait` sin soltar el hilo del loop. Las tareas que ya podían avanzar quedan en `ready`; las que aún esperan su E/S, su temporizador o a otra tarea siguen en `wait` o `blocked`.

**Mini-ejemplo.** $\tau_3$ con `gather`: $40+200+40+0=280=\operatorname{end}-\operatorname{start}$. Con `Semaphore(2)`: $40+200+40+200=480$.

## ρ: CPU-bound e I/O-bound

::: definition {#cmp-def-mod-rho title="ρ, CPU-bound e I/O-bound"}
**En palabras.** $\rho$ es la fracción de la vida que la tarea ejecuta, medida con la tarea sola; cerca de 1 es CPU-bound, pequeña es I/O-bound.

**Formalmente.**

$$\rho(\tau)=\frac{e}{d}\qquad\text{medido con } r=b=0$$

**En el Gantt.** Con la tarea sola, la longitud de sus barras rellenas entre la de toda su fila.
:::

**Mini-ejemplo.** $\rho=40/240=1/6\approx16.7\%$: cinco sextos de su vida espera, es I/O-bound. Acelerar la ejecución gana a lo más $1/(1-\rho)=1.2$ veces.

Nombra el cuello de botella, no la ausencia de E/S, y cambia con la máquina, la carga o la frontera.

## Ejecutando en $t$, CPU y lote

::: definition {#cmp-def-mod-executingat title="ExecutingAt y P"}
**En palabras.** $\operatorname{ExecutingAt}(t)$ son las tareas que ejecutan en el instante $t$; nunca son más que las CPU lógicas $P$.

**Formalmente.**

$$\operatorname{ExecutingAt}(t)=\{\tau_i : t\in\operatorname{exec}(\tau_i)\},\qquad \operatorname{card}(\operatorname{ExecutingAt}(t))\le P$$

**En el Gantt.** Un trazo vertical en $t$, contando sólo barras rellenas.
:::

::: definition {#cmp-def-mod-lote title="Duración del lote, CPU y utilización"}
**En palabras.** $T$ es lo que tarda el lote completo, $C$ la CPU que usaron todas sus tareas y $U$ la fracción de la CPU disponible que se usó.

**Formalmente.**

$$T=\max_i\operatorname{end}(\tau_i)-\min_i\operatorname{start}(\tau_i),\qquad C=\sum_i e_i,\qquad U=\frac{C}{P\cdot T}$$

**En el Gantt.** $T$ es el ancho del dibujo; $U$, el área ocupada de las filas de CPU entre su área total.
:::

$P$ son **CPU lógicas** (con SMT, dos por núcleo físico): `os.cpu_count()`, u `os.process_cpu_count()` (3.13+) si hay afinidad. Una cuota como `docker --cpus` no cambia `os.cpu_count()`, pero sí limita cuánta CPU recibes. En la unidad 3, $P$ se usó para rendimiento; aquí no.

**Mini-ejemplo.** Con `gather`: $\operatorname{ExecutingAt}(30)=\{\tau_2\}$, $\operatorname{ExecutingAt}(100)=\varnothing$; $T=280$, $C=120$, $U=120/280=42.9\%$.

## Secuencial

::: definition {#cmp-def-mod-secuencial title="Ejecución secuencial"}
**En palabras.** Ningún par de vidas se solapa: cada tarea empieza cuando la anterior terminó.

**Formalmente.**

$$\forall i\ne j:\quad \operatorname{vida}(\tau_i)\cap\operatorname{vida}(\tau_j)=\varnothing$$

**En el Gantt.** Ningún trazo vertical corta dos vidas; tocarse en un borde no cuenta.
:::

**Mini-ejemplo.** Vidas $[0,240)$, $[240,480)$, $[480,720)$: $T=\sum_i d_i=720$ ms. Sólo en secuencia, y sin huecos, el total es la suma de las vidas.

## Concurrente

::: definition {#cmp-def-mod-concurrente title="Ejecución concurrente"}
**En palabras.** Al menos dos vidas se solapan un tramo de duración positiva: una tarea empezó antes de que otra terminara.

**Formalmente.**

$$\exists\, i\ne j:\quad \operatorname{dur}\big(\operatorname{vida}(\tau_i)\cap\operatorname{vida}(\tau_j)\big)>0$$

**En el Gantt.** Algún trazo vertical corta dos o más vidas, sea cual sea el estado de cada una.
:::

Con intervalos semiabiertos, «la intersección no es vacía» y «la intersección dura algo» son lo mismo, así que **concurrente = no secuencial**.

Un caso particular útil: la traza **solapa esperas** si $\exists i\ne j:\ \operatorname{dur}(\operatorname{wait}(\tau_i)\cap\operatorname{exec}(\tau_j))>0$. En el Gantt, un trazo vertical corta una espera de una tarea y una ejecución de otra.

**Mini-ejemplo.** Con `gather`: $\operatorname{vida}(\tau_1)\cap\operatorname{vida}(\tau_2)=[0,240)$, 240 ms: concurrente. $\operatorname{wait}(\tau_1)\cap\operatorname{exec}(\tau_2)=[20,40)$: solapa esperas.

## Paralelo, y por qué implica concurrente

::: definition {#cmp-def-mod-paralelo title="Ejecución paralela"}
**En palabras.** Al menos dos tareas ejecutan en el mismo instante; exige al menos dos CPU.

**Formalmente.** Equivale a $\operatorname{card}(\operatorname{ExecutingAt}(t))\ge2$ en un tramo de duración positiva:

$$\exists\, i\ne j:\quad \operatorname{dur}\big(\operatorname{exec}(\tau_i)\cap\operatorname{exec}(\tau_j)\big)>0$$

**En el Gantt.** Dos barras rellenas en la misma vertical, en dos filas de CPU distintas.
:::

**Teorema.** Paralelo $\Rightarrow$ concurrente, y solapa esperas $\Rightarrow$ concurrente.

**Prueba.**

1. Por definición, la ejecución cae dentro de la vida:

$$\operatorname{exec}(\tau)\subseteq\operatorname{vida}(\tau),\qquad \operatorname{wait}(\tau)\subseteq\operatorname{vida}(\tau)$$

2. Intersecar conserva la inclusión:

$$\operatorname{exec}(\tau_i)\cap\operatorname{exec}(\tau_j)\ \subseteq\ \operatorname{vida}(\tau_i)\cap\operatorname{vida}(\tau_j)$$

3. La duración de un subconjunto no excede la del conjunto:

$$0<\operatorname{dur}\big(\operatorname{exec}(\tau_i)\cap\operatorname{exec}(\tau_j)\big)\ \le\ \operatorname{dur}\big(\operatorname{vida}(\tau_i)\cap\operatorname{vida}(\tau_j)\big)$$

4. La izquierda positiva es paralelo; la derecha positiva es concurrente. Con $\operatorname{wait}(\tau_i)\cap\operatorname{exec}(\tau_j)$ el argumento es el mismo. $\square$

El recíproco es falso: con `gather` las vidas se solapan y nunca ejecutan dos tareas a la vez. Quedan **tres casos, no cuatro**:

| | No paralelo | Paralelo |
|---|---|---|
| **No concurrente** | secuencial: vidas disjuntas | **imposible** con las mismas tareas (teorema) |
| **Concurrente** | vidas solapadas, ejecución por turnos: hilos con GIL, `asyncio` | ejecución simultánea: procesos |

**Cambio de escala.** Un `A @ B` de NumPy parece paralelo sin ser concurrente: usa 8 CPU y tu programa tiene una tarea. Fija $\mathcal{T}$. Si $\mathcal{T}=\{$tu llamada$\}$, hay una vida, nada se solapa y $\operatorname{card}(\operatorname{ExecutingAt}(t))\le1$: secuencial. Si $\mathcal{T}$ son los hilos de BLAS, hay vidas solapadas y varias ejecutando: concurrente y paralelo. Con ningún $\mathcal{T}$ sale paralelo sin concurrente. SIMD es otra cosa: una instrucción opera sobre varios datos en un núcleo; es paralelismo de datos, no de tareas.

**Mini-ejemplo.** Tres procesos sobre dos CPU: $\operatorname{ExecutingAt}(10)=\{\tau_1,\tau_2\}$, cardinal $2\le P=2$: paralelo, y por el teorema, concurrente.

## Asíncrono: un mecanismo, no una región del Gantt

::: definition {#cmp-def-mod-asincrono title="Llamada síncrona y llamada asíncrona"}
**En palabras.** Una llamada asíncrona regresa antes del resultado; quien lo necesita hace `await`, se suspende y cede su hilo para que corra otra tarea lista. Una síncrona retiene el hilo hasta el resultado.

**Formalmente.** Síncrona: mientras la operación está pendiente, $\operatorname{hilo}(\tau)$ no ejecuta ninguna otra tarea. Asíncrona: hace posible

$$\exists\, i\ne j:\quad \operatorname{hilo}(\tau_i)=\operatorname{hilo}(\tau_j)\ \ \text{y}\ \ \operatorname{dur}\big(\operatorname{wait}(\tau_i)\cap\operatorname{exec}(\tau_j)\big)>0$$

**En el Gantt.** No es un color ni una región: se ve sólo con la fila de hilo, cuando la espera de una tarea coincide con la ejecución de otra **del mismo hilo**.
:::

- El Gantt de tres hilos y el de `gather` son idénticos; los distingue la fila de hilo.
- **Asíncrono no implica concurrente.** `await` uno tras otro da el Gantt secuencial de 720 ms.
- Llamar una `async def` sólo crea una corrutina, que no corre hasta que se agenda (`create_task`, `gather`) o se espera con `await`; un `await` sobre algo ya terminado no suspende.

**Mini-ejemplo.** Con `gather`, $\operatorname{hilo}(\tau_1)=\operatorname{hilo}(\tau_2)$ y $\operatorname{wait}(\tau_1)\cap\operatorname{exec}(\tau_2)=[20,40)$: $\tau_1$ cedió el hilo. Con tres hilos la intersección es la misma, pero entre hilos distintos.

## Cooperativo contra preventivo

::: definition {#cmp-def-mod-cooperativo title="Planificación cooperativa y preventiva"}
**En palabras.** En la planificación cooperativa la tarea que corre suelta el hilo ella misma, en un `await` que suspende o al terminar; en la preventiva el sistema operativo le quita el turno (y en CPython el GIL le pide soltar el intérprete).

**Formalmente.** Cooperativa: si $\tau_k$ ejecuta un tramo $e_k$ sin `await`, toda tarea $\tau_j$ habilitada en ese loop acumula

$$r_j\ \ge\ e_k$$

Preventiva: el tramo que un hilo retiene el intérprete lo acota, de forma orientativa, `sys.getswitchinterval()` (5 ms por omisión).

**En el Gantt.** Cooperativa: una barra rellena larga en el hilo del loop, con barras rayadas en las demás filas del mismo largo. Preventiva: barras rellenas de unos 5 ms que se alternan entre hilos.
:::

Una respuesta que llega habilita a su tarea (pasa de `wait` a `ready`); **no interrumpe** a la que ejecuta. El intervalo del GIL es orientativo: una función interna larga en C puede excederlo.

**Mini-ejemplo.** Si $\tau_3$ calcula 2000 ms sin `await` dentro del loop, $\tau_1$, cuya respuesta llega en 220, queda en `ready` hasta 2040: $r_1=1820\ge$ lo que quedaba del cálculo.

## El GIL, por intérprete

::: definition {#cmp-def-mod-gil title="GIL por intérprete"}
**En palabras.** En un intérprete con GIL, a lo más un hilo ejecuta bytecode de Python en cada instante; en este curso hay un intérprete por proceso.

**Formalmente.** Con $\operatorname{exec}_{\mathrm{Python}}(\tau)\subseteq\operatorname{exec}(\tau)$, para cada intérprete $I$ y cada $t$:

$$\operatorname{card}\{\tau \text{ de } I : t\in\operatorname{exec}_{\mathrm{Python}}(\tau)\}\le1$$

**En el Gantt.** La fila «GIL del proceso» nunca tiene dos tramos a la vez; un hilo que quiere ejecutar Python sin tener el GIL va rayado (listo).
:::

- **No impone $P=1$.** El código nativo que suelta el GIL (E/S bloqueante, `time.sleep`, muchas operaciones de NumPy y BLAS, no todas) puede ejecutar en otra CPU mientras un hilo ejecuta Python.
- La restricción es por intérprete: $K$ procesos son $K$ GIL y hasta $\min(K,P)$ CPU con Python.
- La compilación *free-threaded* de CPython, opcional y con soporte oficial desde 3.14 (PEP 779, 2025), la quita. Los subintérpretes existen, pero no se usan aquí.
- Un event loop ejecuta una tarea a la vez por su planificación cooperativa, **con o sin GIL**.

**Mini-ejemplo.** Dos hilos que sólo calculan en un proceso con $P=8$: se alternan cada ~5 ms; nunca hay dos tramos de Python en la misma vertical. Concurrente, no paralelo.

## Speedup, eficiencia y Amdahl

::: definition {#cmp-def-mod-speedup title="Speedup y eficiencia"}
**En palabras.** El speedup divide el tiempo de una versión base, que siempre se declara, entre el de la nueva; la eficiencia reparte ese speedup entre los $N$ trabajadores.

**Formalmente.**

$$S=\frac{T_{\text{base}}}{T_{\text{nueva}}},\qquad S(N)=\frac{T(1)}{T(N)},\qquad E(N)=\frac{S(N)}{N}$$

**En el Gantt.** El cociente de los anchos de dos trazas del mismo conjunto de tareas.
:::

| Símbolo | Definición | Nota |
|---|---|---|
| $N$ | trabajadores entre los que se reparte (hilos, procesos) | no es $P$ (CPU) ni $n$ (tareas) |
| $k$ | tope real de lo que corre o está en vuelo: procesos de un pool, permisos, conexiones | en un pool de procesos, $N=k$ |
| $\operatorname{speedup}_{\text{pool}}(k)=T_{\text{pool}}(1)/T_{\text{pool}}(k)$ | el pool contra sí mismo con un trabajador | esconde el costo de tener pool |
| $\operatorname{speedup}_{\text{aplicación}}(k)=T_{\text{secuencial}}/T_{\text{pool}}(k)$ | contra la versión directa, sin pool | lo que gana tu programa |
| $h(k)$ | costos que crecen con el número de trabajadores: arrancar procesos, serializar, IPC | un costo fijo cabe en $f$; uno que crece con $k$, no |

**Pool con tareas iguales.** $n$ tareas iguales, independientes, indivisibles y sólo de CPU, de $c$ cada una, con $k$ procesos:

$$T_{\text{pool}}(k)\approx\left\lceil n/\min(k,P)\right\rceil c+h(k)$$

Con $k>P$ la fórmula deja de ser exacta (el sistema intercala los $k$ procesos en $P$ CPU), pero siempre $T\ge n\,c/P$. Regla práctica: $k=\min(n,P)$.

::: definition {#cmp-def-mod-amdahl title="Ley de Amdahl"}
**En palabras.** Si una fracción $f$ del tiempo con un trabajador no se reparte, el speedup nunca pasa de $1/f$, por más trabajadores que agregues.

**Formalmente.**

$$T(N)=T(1)\left(f+\frac{1-f}{N}\right),\qquad S(N)=\frac{1}{f+(1-f)/N},\qquad \lim_{N\to\infty}S(N)=\frac{1}{f}$$

**En el Gantt.** El tramo serial mide lo mismo con 1 o con $N$ filas de CPU; sólo el tramo repartible se divide entre las $N$ filas.
:::

Supone carga fija, $f$ constante, parte repartible divisible tanto como haga falta, trabajadores equivalentes, $N\le P$ y ningún costo que crezca con $N$; si alguno falla, $T_{\text{real}}(N)=T(1)\,(f+(1-f)/N)+h(N)$. Con tareas indivisibles, además, $S\le\min(N,P,n)$. Vectorizar o cambiar de algoritmo cambia $T(1)$: Amdahl no compara implementaciones distintas.

**Mini-ejemplo (traza ilustrativa).** $n=3$ tareas de cálculo de $c=400$ ms; en secuencia, 1200 ms; $h=0$:

| $k$ | $P$ | Cuenta | $T$ (ms) | $S$ | $E$ |
|---:|---:|---|---:|---:|---:|
| 1 | 8 | $\lceil3/1\rceil\times400$ | 1200 | 1 | 1 |
| 2 | 8 | $\lceil3/2\rceil\times400$ | 800 | 1.5 | 0.75 |
| 3 | 8 | $\lceil3/3\rceil\times400$ | 400 | 3 | 1 |
| 4 | 8 | $\lceil3/4\rceil\times400$ | 400 | 3 | 0.75 |
| 3 | 2 | $T\ge3\times400/2$ | $\ge600$ | $\le2$ | — |

Con $k=2$ la tercera tarea corre sola: la granularidad, no Amdahl, fija el 1.5. Con $h=20$ ms: $\operatorname{speedup}_{\text{pool}}(2)=1220/820\approx1.49$ y $\operatorname{speedup}_{\text{aplicación}}(2)=1200/820\approx1.46$.

**Con la medición de referencia** (`calcula`, 4 tareas, pool de 1, 2 y 4 procesos; una corrida en una máquina de 8 CPU lógicas): $T_{\text{pool}}=1.45$, $0.75$ y $0.54$ s.

- Base declarada: el mismo pool con un proceso. $\operatorname{speedup}_{\text{pool}}(2)=1.45/0.75\approx1.93$, $E\approx0.97$; $\operatorname{speedup}_{\text{pool}}(4)=1.45/0.54\approx2.69$, $E\approx0.67$.
- Ajuste $T(N)=a+b/N$: de $a+b=1.45$ y $a+b/2=0.75$ salen $b=1.40$ y $a=0.05$. Predice $T(4)=0.40$ s; medido, 0.54: el modelo no ajusta el punto que queda.
- $f=a/T(1)\approx0.034$; techo $1/f\approx29$; con $n=4$ tareas, nunca más de 4.
- Tres puntos para dos parámetros y una corrida: que los 0.14 s de más sean arranque e IPC es una hipótesis, no una medición.

**Vectorizar no es $S(N)$.** Bucle contra NumPy, $0.141/0.0091\approx15.5$: speedup contra otra implementación en el mismo núcleo, no un reparto entre trabajadores.

## Little y la cota del semáforo

::: definition {#cmp-def-mod-little title="Ley de Little"}
**En palabras.** En régimen estable, las tareas en vuelo en promedio son el rendimiento por el tiempo medio que cada una pasa dentro de la frontera elegida.

**Formalmente.** Si a lo más $k$ caben dentro, $L\le k$:

$$L=\lambda\cdot W\qquad\Rightarrow\qquad \lambda\le\frac{k}{W}$$

**En el Gantt.** $L$ es el número promedio de vidas que corta un trazo vertical; con todas las tareas dentro de la ventana, $L=\sum_i d_i/T$.
:::

$W_{\text{recurso}}$ o $W_{\text{conexión}}$ es el tiempo medio que una tarea **retiene** un recurso concreto (la conexión, desde que la presta hasta que la devuelve); no es la latencia de toda la petición.

::: definition {#cmp-def-mod-cota-semaforo title="Cota del semáforo"}
**En palabras.** Con $n$ tareas iguales que retienen un permiso toda su duración $e+w$ y $k$ permisos, algún permiso atiende por lo menos $\lceil n/k\rceil$ tareas una tras otra.

**Formalmente.**

$$T\ \ge\ \left\lceil n/k\right\rceil\cdot(e+w)$$

**En el Gantt.** Ningún trazo vertical corta más de $k$ tareas fuera de la franja ámbar; las demás están bloqueadas.
:::

Es una cota inferior: las listas, el arranque y los costos del loop se suman encima.

| Caso | Cuenta | Resultado |
|---|---|---|
| ejemplo único con `Semaphore(2)` | $\lceil3/2\rceil\times240$ | $T\ge480$ ms (contra 280 sin tope) |
| ejemplo único con `gather` | $L=(240+260+280)/280$ | $\approx2.79$ en vuelo; en secuencia, $720/720=1$ |
| servidor secuencial, $k=1$, $W=0.202$ s | $\lambda\le1/0.202$ | $\le4.95$ peticiones/s |
| 20 llamadas en serie, $T=4.04$ s | $\lambda=20/4.04$, $W=0.202$ | $L=4.95\times0.202=1.0$ |
| 20 llamadas con 32 hilos, $T=0.23$ s | $\lambda=20/0.23\approx87$/s, $W\approx0.202$ | $L\approx17.6$; coincide con el speedup $4.04/0.23$ sólo porque $W$ es el mismo en las dos versiones |
| tope 32, $W=0.2$ s | $\lambda\le32/0.2$ | $\le160$/s; 500 llamadas $\ge3.125$ s |
| 500 llamadas, cota del semáforo | $\lceil500/32\rceil\times0.2=16\times0.2$ | $\ge3.2$ s (medido: 3.32 con hilos, 3.39 con `asyncio`) |
| pool de BD, $\lambda=50$/s, $W=0.2$ s (cifras supuestas) | $L=50\times0.2$ | 10 conexiones en uso: un pool de 10 justo alcanza |
| la misma BD con $W=2$ s | $L=50\times2=100>10$ | con tope 10, $\lambda\le10/2=5$/s: las otras 45/s hacen cola |

Little dimensiona semáforos, pools y colas con la misma cuenta: **conexiones en uso = $\lambda\cdot W$**. Un tope no es un *rate limit*: $\lambda\le k/W$ depende de $W$.

## El ejemplo único, evaluado completo

### Secuencial (o `await` uno tras otro): 720 ms

| Tarea | start | end | exec | wait | ready |
|---|---:|---:|---|---|---|
| $\tau_1$ | 0 | 240 | $[0,20)\cup[220,240)$ | $[20,220)$ | $\varnothing$ |
| $\tau_2$ | 240 | 480 | $[240,260)\cup[460,480)$ | $[260,460)$ | $\varnothing$ |
| $\tau_3$ | 480 | 720 | $[480,500)\cup[700,720)$ | $[500,700)$ | $\varnothing$ |

- Vidas disjuntas: **secuencial**. $T=720=\sum_i d_i$; $C=120$; $U=120/720=16.7\%$.
- Latencias 240, 480 y 720 (media 480) aunque $d=240$ para las tres.

### Con `gather` (o con tres hilos): 280 ms

| Tarea | start | end | exec | wait | ready |
|---|---:|---:|---|---|---|
| $\tau_1$ | 0 | 240 | $[0,20)\cup[220,240)$ | $[20,220)$ | $\varnothing$ |
| $\tau_2$ | 0 | 260 | $[20,40)\cup[240,260)$ | $[40,240)$ | $[0,20)$ |
| $\tau_3$ | 0 | 280 | $[40,60)\cup[260,280)$ | $[60,260)$ | $[0,40)$ |

Como texto (columnas no a escala; E ejecuta, W espera, R lista, — terminada):

| | 0–20 | 20–40 | 40–60 | 60–220 | 220–240 | 240–260 | 260–280 |
|---|---|---|---|---|---|---|---|
| τ1 | E | W | W | W | E | — | — |
| τ2 | R | E | W | W | W | E | — |
| τ3 | R | R | E | W | W | W | E |
| hilo (o CPU) | τ1 | τ2 | τ3 | ocioso | τ1 | τ2 | τ3 |

1. **Partición.** $r=(0,20,40)$, $b=0$: $d=(240,260,280)$.
2. **Concurrente** y **solapa esperas**: $[0,240)$ y $[20,40)$, ver arriba.
3. **No paralelo.** $\max_t\operatorname{card}(\operatorname{ExecutingAt}(t))=1$.
4. $T=280$; $C=120$; ocio $[60,220)$, 160 ms; $U=42.9\%$. $\sum_i w_i=600$ ms en un lote de 280: las esperas se solaparon.
5. Speedup sobre la secuencia (base declarada): $720/280\approx2.57$. Latencias 240, 260, 280.

### Una tarea calcula dentro del loop: 2080 ms

$\tau_3$ se cambia por un **cálculo de 2000 ms sin ningún `await`**; $\tau_1$ y $\tau_2$ siguen iguales, en el mismo loop.

| Tarea | start | end | exec | wait | ready |
|---|---:|---:|---|---|---|
| $\tau_1$ | 0 | 2060 | $[0,20)\cup[2040,2060)$ | $[20,220)$ | $[220,2040)$ |
| $\tau_2$ | 0 | 2080 | $[20,40)\cup[2060,2080)$ | $[40,240)$ | $[0,20)\cup[240,2060)$ |
| $\tau_3$ | 0 | 2040 | $[40,2040)$ | $\varnothing$ | $[0,40)$ |

- $d_1=40+200+1820=2060$; $d_2=40+200+1840=2080$; $d_3=2000+40=2040$.
- $C=2080=T$: $U=100\%$, y aun así las respuestas de 220 y 240 ms esperan listas hasta 2040. Utilización alta no significa buen servicio.
- Con el cálculo en otro proceso (*offload*), ese tramo es `wait` de $\tau_3$ y $\tau_1$, $\tau_2$ vuelven a terminar en 240 y 260.

### Tres procesos sobre dos CPU: 260 ms

| Tarea | exec | wait | ready |
|---|---|---|---|
| $\tau_1$ | $[0,20)\cup[220,240)$ (CPU 1) | $[20,220)$ | $\varnothing$ |
| $\tau_2$ | $[0,20)\cup[220,240)$ (CPU 2) | $[20,220)$ | $\varnothing$ |
| $\tau_3$ | $[20,40)\cup[240,260)$ (CPU 1) | $[40,240)$ | $[0,20)$ |

- $\tau_3$ está lista en $[0,20)$ porque las dos CPU las ocupan $\tau_1$ y $\tau_2$; en 240 vuelve a la CPU 1, que $\tau_1$ soltó en 240.
- **Paralelo:** $\operatorname{dur}(\operatorname{exec}(\tau_1)\cap\operatorname{exec}(\tau_2))=40$ ms.
- $T=260$; speedup sobre la secuencia $720/260\approx2.77$, casi todo por solapar esperas (contra hilos sólo se ganan 20 ms).
- $U=120/(2\times260)\approx23.1\%$: la CPU 1 está ociosa en $[40,220)$ y la CPU 2 en $[20,220)$ y $[240,260)$.

## Propiedades que se leen en un Gantt

La clasificación es de **la ejecución dibujada**: una biblioteca no la garantiza por sí sola.

| Ejecución ilustrada | Dónde | Concurrente | Solapa esperas | Máx. ejecutando | Paralela | Interfaz asíncrona |
|---|---|:---:|:---:|:---:|:---:|---|
| llamadas bloqueantes una por una | `cmp-gantt-secuencial` | no | no | 1 | no | no |
| `await` uno tras otro | `cmp-gantt-await-en-serie` | no | no | 1 | no | sí |
| dos hilos que sólo calculan, por turnos del GIL | página 2 | sí | no | 1 | no | no se deduce |
| hilos con E/S bloqueante | `cmp-gantt-hilos` | sí | sí | 1 | no | no, en cada hilo |
| corrutinas con `gather` en un loop | `cmp-gantt-asyncio` | sí | sí | 1 | no | sí |
| trabajos sólo de CPU en dos procesos | página 6 | sí | no | 2 | sí | no se deduce |
| tareas mixtas en tres procesos sobre dos CPU | `cmp-gantt-procesos` | sí | sí | 2 | sí | no se deduce |

Para verificar una figura:

- Cada tarea está en **exactamente un estado** en cada instante de su vida.
- La capacidad de CPU se comprueba contando **sólo** barras de ejecución; el solapamiento de vidas, contando también esperas, listas y bloqueadas.
- Cada fila de CPU dice qué representa (una CPU, el GIL de un proceso, el hilo del loop).
- **Ningún paralelismo se deduce de que el total bajó**: con `gather` baja de 720 a 280 ms con una sola CPU.

## Advertencias de medición

- **El 99.4 % no es $\sum w$.** En 20 llamadas en serie, $T=4.04$ s y $C\approx0.02$ s: $(T-C)/T\approx99.4\%$ es **tiempo sin CPU del cliente**, dominado aquí por la red pero con turnos y otros efectos. Eliminar toda la CPU daría a lo más $1/0.994\approx1.006$ veces; los segundos publicados se redondean por separado.
- **`process_time` mide el proceso, no una tarea.** Suma la CPU de todos sus hilos (con NumPy/BLAS puede dar CPU/reloj $>1$) y **no cuenta procesos hijos**; para ellos, `os.times()` (`children_user`, `children_system`), sólo cuando ya terminaron y fueron esperados.
- **Una corrida es una corrida.** El ruido entre corridas puede ser del orden de las diferencias pequeñas (20 ms entre hilos y procesos, 0.07 s entre hilos y `asyncio`).

Sigue con [[donde-pasa-el-tiempo]]; el índice de la unidad está en [[computo-y-concurrencia]].
