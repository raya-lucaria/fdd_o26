---
id: secuencial-concurrente-paralelo
title: "Secuencial, concurrente y paralelo"
nav_title: "Secuencial, concurrente, paralelo"
summary: "Tres propiedades de una traza que se comprueban en el Gantt: vidas disjuntas, vidas que se solapan y dos tareas ejecutando en el mismo instante. Todo lo paralelo es concurrente; con hilos se comparte memoria y aparece la condición de carrera; con procesos se aísla y se paga en copias. Y la arquitectura que sale de cada una: hilo por conexión contra prefork."
status: ready
estimated_time: 20m
tags: [concurrencia, paralelismo, hilos, procesos, gil, condicion-de-carrera, lock, speedup, gantt, arquitectura]
prerequisites: [donde-pasa-el-tiempo, el-gil]
---

# Secuencial, concurrente y paralelo

**Página 2 de 8 · Cómputo y concurrencia** · Pregunta: alguien te dice «hazlo concurrente», otro «hazlo paralelo»; ¿afirman lo mismo, y cómo lo compruebas en un Gantt? · Meta: clasificar cualquier traza con una cuenta, saber qué se rompe cuando los hilos comparten un dato y elegir entre hilo por conexión y procesos.

| Término | Definición de una línea | Símbolo |
|---|---|---|
| proceso | programa corriendo, con su memoria y su intérprete | — |
| hilo | línea de ejecución dentro de un proceso; comparte la memoria del proceso | $\operatorname{hilo}(\tau)$ |
| CPU lógica | lo que el sistema puede poner a ejecutar a la vez | $P$ |
| GIL | candado de un intérprete: un solo hilo ejecuta bytecode de Python a la vez | $\operatorname{exec}_{\mathrm{Python}}$ |
| secuencial | ningún par de vidas se solapa | $\operatorname{vida}(\tau_i)\cap\operatorname{vida}(\tau_j)=\varnothing$ |
| concurrente | al menos dos vidas se solapan un tramo de duración positiva | $\operatorname{dur}(\operatorname{vida}\cap\operatorname{vida})>0$ |
| paralelo | al menos dos tareas ejecutan en el mismo instante | $\operatorname{card}(\operatorname{ExecutingAt}(t))\ge2$ |
| utilización | CPU usada entre CPU disponible en el lote | $U=C/(P\cdot T)$ |
| condición de carrera | el resultado depende del orden en que se intercalan dos hilos que tocan el mismo dato | — |
| región crítica | trozo que sólo un hilo a la vez puede ejecutar; se protege con un `Lock` | — |
| speedup, eficiencia | tiempo con 1 trabajador entre tiempo con $N$; speedup entre $N$ | $S(N)$, $E(N)$ |

## En corto

- **Secuencial, concurrente y paralelo son propiedades de la traza, no de la biblioteca.** Se leen en el Gantt: vidas disjuntas, vidas solapadas, dos barras de ejecución en el mismo instante.
- **Paralelo implica concurrente; el recíproco es falso.** Hilos con GIL y `asyncio` son concurrentes y no paralelos; procesos sobre varias CPU son las dos cosas.
- **Hilos comparten memoria; procesos no.** Compartir abarata y abre la condición de carrera (que se cierra con un `Lock`, a costa de serializar); aislar protege y cuesta copias y arranque. De ahí salen dos servidores: hilo por conexión y prefork.

## Qué ejecuta: proceso, hilo, CPU lógica y GIL

La definición larga de estos cuatro está en [[el-gil]]. Aquí va el resumen que hace falta para leer los Gantt de esta página.

| | Qué es | Memoria | Cuántos ejecutan Python a la vez | Qué te da |
|---|---|---|---|---|
| **proceso** | un programa corriendo | propia: no ve las variables de otro proceso | uno por proceso (cada uno trae su intérprete y su GIL) | cálculo simultáneo; aislamiento |
| **hilo** | una línea de ejecución dentro de un proceso | **compartida** con los demás hilos del proceso | uno entre todos los hilos del proceso | solapar esperas; barato de crear |
| **CPU lógica** | lo que el sistema puede poner a ejecutar a la vez (con SMT, dos por núcleo) | no aplica | — | el tope $P$ de ejecuciones simultáneas |
| **GIL** | el candado de un intérprete de CPython | no aplica | uno por intérprete | hilos que se turnan para ejecutar Python |

::: definition {#cmp-def-gil-interprete title="GIL por intérprete"}
**En palabras.** En un intérprete con GIL, a lo más un hilo ejecuta bytecode de Python en cada instante; en este curso hay un intérprete por proceso.

**Formalmente.** Con $\operatorname{exec}_{\mathrm{Python}}(\tau)\subseteq\operatorname{exec}(\tau)$, para cada intérprete $I$ y cada $t$: $\operatorname{card}\{\tau \text{ de } I : t\in\operatorname{exec}_{\mathrm{Python}}(\tau)\}\le1$. ([[notacion-computo]])
:::

**Otro ángulo.** Dos hilos que sólo calculan, en un proceso, con $P=8$. El GIL pide al hilo que lo tiene que lo suelte cada `sys.getswitchinterval()` (5 ms por omisión); el otro lo toma. Gantt como texto (E ejecuta Python, R lista sin turno):

| | 0–5 ms | 5–10 ms | 10–15 ms | 15–20 ms | … |
|---|---|---|---|---|---|
| hilo A | E | R | E | R | … |
| hilo B | R | E | R | E | … |
| GIL del proceso | A | B | A | B | … |

- Las vidas se solapan: es **concurrente**. Nunca hay dos E en la misma columna: **no es paralelo**, aunque sobren 7 CPU.
- Lo que el GIL impide no es cambiar de hilo (cambia cada 5 ms); lo que nunca hay es **ejecución simultánea de Python** dentro de un intérprete.
- Esperar el GIL es `ready` (lista), no espera: si el hilo recibiera el GIL, avanzaría.

**Matemática.** Para cada intérprete $I$ y cada instante $t$:

$$\operatorname{card}\{\tau \text{ de } I : t\in\operatorname{exec}_{\mathrm{Python}}(\tau)\}\le1$$

Eso **no** impone $P=1$: el código nativo que suelta el GIL (E/S bloqueante, `time.sleep`, muchas operaciones de NumPy y BLAS) puede ejecutar en otra CPU mientras otro hilo ejecuta Python. La compilación *free-threaded* de CPython, opcional y con soporte oficial desde 3.14 (PEP 779, 2025), quita la restricción.

**Ejemplo.** La medición de [[el-gil]]: 4 hilos que calculan tardan lo mismo que 1. La de esta página (celda 2.1): 20 hilos que **esperan** tardan casi lo mismo que una llamada, porque esperar suelta el GIL.

**Arquitectura.** Un proceso de Python con muchos hilos aprovecha **una** CPU para su Python. Para usar $P$ CPU con Python puro hacen falta $P$ procesos (o código nativo que suelte el GIL). Es la razón de que los servidores de Python en producción arranquen varios procesos (prefork, abajo).

## Secuencial y concurrente: vidas que se tocan o se solapan

::: definition {#cmp-def-secuencial-formal title="Ejecución secuencial"}
**En palabras.** Ningún par de vidas se solapa: cada tarea empieza cuando la anterior terminó.

**Formalmente.** $\forall i\ne j:\ \operatorname{vida}(\tau_i)\cap\operatorname{vida}(\tau_j)=\varnothing$, sobre un conjunto fijo $\mathcal{T}$. ([[notacion-computo]])
:::

::: definition {#cmp-def-concurrente title="Ejecución concurrente"}
**En palabras.** Al menos dos vidas se solapan un tramo de duración positiva: una tarea empezó antes de que otra terminara.

**Formalmente.** $\exists i\ne j:\ \operatorname{dur}(\operatorname{vida}(\tau_i)\cap\operatorname{vida}(\tau_j))>0$. ([[notacion-computo]])

No dice cuántas CPU hay ni si alguien ejecuta a la vez: sólo que una tarea empezó antes de que otra terminara.
:::

**Otro ángulo.** Las vidas son intervalos semiabiertos $[\operatorname{start},\operatorname{end})$: incluyen el inicio y excluyen el fin. Dos vidas que se tocan en un borde **no** se solapan.

| Vidas | Intersección | Dura | Clasificación |
|---|---|---:|---|
| $[0,240)$ y $[240,480)$ | $\varnothing$ | 0 | se tocan: secuencial |
| $[0,240)$ y $[0,260)$ | $[0,240)$ | 240 ms | se solapan: concurrente |

**Matemática.** Con intervalos semiabiertos, «la intersección no es vacía» y «la intersección dura algo» dicen lo mismo, así que **concurrente = no secuencial**: cada traza cae exactamente en una de las dos.

**Ejemplo** (el ejemplo único: tres tareas de 20 ms ejecuta + 200 ms espera + 20 ms ejecuta; traza ilustrativa).

| Versión | Vidas | ¿Concurrente? | $T$ |
|---|---|---|---:|
| una tras otra | $[0,240)$, $[240,480)$, $[480,720)$ | no: disjuntas | 720 ms |
| tres hilos (o `gather`) | $[0,240)$, $[0,260)$, $[0,280)$ | sí: $[0,240)$ dura 240 ms | 280 ms |

**Arquitectura.** El servidor secuencial de la página 1 (una conexión a la vez) es la traza secuencial: con $W=0.202$ s atiende a lo más $1/0.202\approx4.95$ peticiones/s. Volverlo concurrente es dejar que la vida de una petición empiece antes de que acabe la anterior: el patrón más simple es **un hilo por conexión** (abajo).

## Paralelo: dos tareas ejecutan en el mismo instante

::: definition {#cmp-def-paralelo title="Ejecución paralela"}
**En palabras.** Al menos dos tareas ejecutan en el mismo instante; exige al menos dos CPU.

**Formalmente.** $\exists i\ne j:\ \operatorname{dur}(\operatorname{exec}(\tau_i)\cap\operatorname{exec}(\tau_j))>0$, es decir, $\operatorname{card}(\operatorname{ExecutingAt}(t))\ge2$ en un tramo de duración positiva, con $\operatorname{ExecutingAt}(t)=\{\tau_i : t\in\operatorname{exec}(\tau_i)\}$. ([[notacion-computo]]) Siempre $\operatorname{card}(\operatorname{ExecutingAt}(t))\le P$, así que exige $P\ge2$.
:::

**Otro ángulo.** Las mismas tres tareas, primero con hilos (un proceso, un GIL) y luego en tres procesos sobre dos CPU.

::: figure {#cmp-gantt-hilos title="Hilos: las esperas se solapan, la ejecución se turna por el GIL"}
![Diagrama de Gantt con tiempo en milisegundos y una fila por hilo, más una fila de CPU que representa el GIL del proceso. Tres hilos empiezan en 0. Cada uno ejecuta 20 ms, espera 200 ms y ejecuta 20 ms. El hilo 2 queda listo sin turno de 0 a 20 ms y el hilo 3 de 0 a 40 ms, dibujados rayados. Las tres esperas se solapan, pero la fila de CPU nunca tiene dos tramos al mismo tiempo. Total 280 ms contra 720 del secuencial.](_assets/cmp-gantt-hilos.svg)
:::

Lectura de la figura:

- Todo ocurre en **una** CPU con un GIL: el hilo 1 ejecuta de 0 a 20 ms; el hilo 2 queda listo de 0 a 20 porque el GIL lo tiene el hilo 1, y el hilo 3 de 0 a 40 porque lo tienen el 1 y luego el 2.
- Un trazo vertical en $t=100$ corta las tres vidas (todas en espera): **concurrente**.
- En $t=30$ ejecuta el hilo 2 mientras el 1 espera: **solapa esperas**. Eso es todo lo que gana: 720 → 280 ms.
- La fila de CPU tiene a lo más un tramo en cada instante: $\max_t\operatorname{card}(\operatorname{ExecutingAt}(t))=1$, **no paralelo**.
- Los tramos rayados del arranque son `ready`: el hilo podría ejecutar, pero el GIL lo tiene otro.

::: figure {#cmp-gantt-procesos title="Procesos: dos CPU ejecutan al mismo tiempo"}
![Diagrama de Gantt con tiempo en milisegundos, una fila por proceso y dos filas de CPU. Los procesos 1 y 2 ejecutan de 0 a 20 ms al mismo tiempo, uno en la CPU 1 y otro en la CPU 2; el proceso 3 queda listo sin CPU, rayado, de 0 a 20 ms y ejecuta de 20 a 40 en la CPU 1. Las esperas de 200 ms se solapan. Las dos filas de CPU tienen tramos simultáneos. Total 260 ms, sólo 20 menos que con hilos.](_assets/cmp-gantt-procesos.svg)
:::

Lectura de la figura:

- En $t=10$ las dos filas de CPU están ocupadas: $\operatorname{ExecutingAt}(10)=\{\tau_1,\tau_2\}$, cardinal 2 $\le P=2$: **paralelo**.
- Los procesos 1 y 2 ejecutan de 0 a 20 ms en la CPU 1 y la CPU 2. El proceso 3 queda `ready` de 0 a 20 ms porque las dos CPU están ocupadas; en 20 el proceso 1 pasa a esperar la red, suelta la CPU 1 y el 3 ejecuta ahí de 20 a 40. En 240 el 3 vuelve a la CPU 1, que el 1 soltó al terminar.
- **Ningún paralelismo se deduce de que el total bajó:** con hilos también bajó (a 280 ms) con una sola CPU. El paralelismo se ve en dos barras de ejecución en la misma vertical.

**Matemática.** La utilización $U=C/(P\cdot T)$, con $C=3\times40=120$ ms de CPU en las tres versiones:

| Versión | $P$ | $T$ (ms) | $U$ | Máx. ejecutando |
|---|---:|---:|---:|---:|
| secuencial | 1 | 720 | $120/720=16.7\%$ | 1 |
| tres hilos | 1 | 280 | $120/280=42.9\%$ | 1 |
| tres procesos | 2 | 260 | $120/(2\times260)\approx23.1\%$ | 2 |

Pasar a procesos **baja** la utilización: se agregó una CPU y las dos pasan casi todo el tiempo ociosas: la CPU 1 en $[40,220)$ y la CPU 2 en $[20,220)$ y $[240,260)$. Con tareas que casi sólo esperan, el paralelismo rinde 20 ms; lo que rindió fue solapar esperas.

**Ejemplo** (medición real, celda 2.2; una corrida en la máquina del profesor, 8 CPU lógicas): 4 cálculos de `calcula` con 1, 2 y 4 procesos tardan 1.45, 0.75 y 0.54 s. Aquí sí hay paralelismo útil, porque las tareas sólo calculan ($\rho\approx1$).

**Arquitectura.** Con Python puro, paralelo significa **varios procesos** (o librerías que sueltan el GIL). En un servidor eso es **prefork**: un maestro arranca $K$ procesos y cada uno atiende peticiones. Va completo en la sección de arquitectura de abajo.

## Paralelo implica concurrente: tres casos, no cuatro

**Teorema.** Si una ejecución es paralela, es concurrente.

**Prueba.**

1. Por definición, $\operatorname{exec}(\tau)\subseteq\operatorname{vida}(\tau)$ para toda tarea.
2. Entonces $\operatorname{exec}(\tau_i)\cap\operatorname{exec}(\tau_j)\subseteq\operatorname{vida}(\tau_i)\cap\operatorname{vida}(\tau_j)$, y la duración de un subconjunto no excede la del conjunto.
3. Si la izquierda dura algo positivo (paralelo), la derecha también (concurrente). $\square$

**El recíproco es falso:** con tres hilos las vidas se solapan (concurrente) y nunca ejecutan dos a la vez (no paralelo). El mismo argumento prueba que **solapar esperas implica concurrente**: $\operatorname{wait}(\tau)$ también está dentro de la vida.

::: figure {#cmp-conjuntos title="Secuencial, concurrente y paralelo como conjuntos de trazas"}
![Diagrama de conjuntos de las trazas de un mismo grupo de tareas, con la misma granularidad. A la izquierda, secuencial: ningún par de vidas se solapa, con un mini Gantt de T1 y luego T2, como un for con requests o await uno tras otro. A la derecha, concurrente: algún par de vidas se solapa, con T1 y T2 intercaladas en una CPU, como hilos con GIL o asyncio con gather. Dentro de concurrente, la región paralelo: dos tareas ejecutan en el mismo instante en dos CPU, como procesos. Secuencial y concurrente no se tocan; paralelo implica concurrente; asíncrono no es una región del dibujo.](_assets/cmp-conjuntos.svg)
:::

| | No paralelo | Paralelo |
|---|---|---|
| **No concurrente** | secuencial: vidas disjuntas (720 ms) | **imposible** con las mismas tareas (teorema) |
| **Concurrente** | por turnos: hilos con GIL, `asyncio` (280 ms) | ejecución simultánea: procesos (260 ms) |

> [!NOTE]
> **Cambio de granularidad.** Un `A @ B` de NumPy parece paralelo sin ser concurrente: usa 8 CPU y tu programa tiene una tarea. Fija $\mathcal{T}$. Si $\mathcal{T}=\{$tu llamada$\}$, hay una vida, nada se solapa: secuencial. Si $\mathcal{T}$ son los hilos de BLAS, hay vidas solapadas y varias ejecutando: concurrente y paralelo. Con ningún $\mathcal{T}$ sale paralelo sin concurrente. SIMD es otra cosa: una instrucción opera sobre varios datos en un núcleo; es paralelismo de datos, no de tareas, y $\operatorname{card}(\operatorname{ExecutingAt}(t))$ sigue valiendo 1. Va en [[vectorizar]].

## Propiedades que se verifican en el Gantt

La clasificación es de **la ejecución dibujada**: una biblioteca no la garantiza sola (un `asyncio` con `await` uno tras otro es secuencial).

| Ejecución ilustrada | Dónde | Concurrente | Solapa esperas | Máx. ejecutando | Paralela | Interfaz asíncrona |
|---|---|:---:|:---:|:---:|:---:|---|
| llamadas bloqueantes una por una | `cmp-gantt-secuencial` (página 1) | no | no | 1 | no | no |
| `await` uno tras otro | `cmp-gantt-await-en-serie` (página 3) | no | no | 1 | no | sí |
| dos hilos que sólo calculan, por turnos del GIL | tabla de texto de arriba | sí | no | 1 | no | no se deduce |
| hilos con E/S bloqueante | `cmp-gantt-hilos` | sí | sí | 1 | no | no, en cada hilo |
| corrutinas con `gather` en un loop | `cmp-gantt-asyncio` (página 3) | sí | sí | 1 | no | sí |
| trabajos sólo de CPU en dos procesos | página 6 | sí | no | 2 | sí | no se deduce |
| tareas mixtas en tres procesos sobre dos CPU | `cmp-gantt-procesos` | sí | sí | 2 | sí | no se deduce |

Para verificar una figura:

- Cada tarea está en **exactamente un estado** en cada instante de su vida.
- La capacidad de CPU se comprueba contando **sólo** barras de ejecución; el solapamiento de vidas, contando también esperas y listas.
- Cada fila de CPU dice qué representa: una CPU, el GIL de un proceso, el hilo del loop.

## Memoria compartida contra aislada: la condición de carrera

::: definition {#cmp-def-condicion-de-carrera title="Condición de carrera"}
Hay **condición de carrera** cuando el resultado de un programa depende del orden en que se intercalan dos o más hilos que leen y escriben el mismo dato. Ocurre porque una operación que se escribe en una línea, como `contador += 1`, son varios pasos (leer, sumar, escribir) y otro hilo puede ejecutar entre ellos.
:::

**Otro ángulo.** Traza de dos hilos que suman 1 al mismo contador, que empieza en 5. El GIL cambia de hilo entre la lectura y la escritura de A:

| Paso | hilo A | hilo B | contador |
|---:|---|---|---:|
| 1 | lee `actual = 5` | — | 5 |
| 2 | (le quitan el turno) | lee `actual = 5` | 5 |
| 3 | — | escribe `5 + 1` | 6 |
| 4 | escribe `5 + 1` | — | **6** |

Dos sumas, el contador subió 1: **la suma de B se perdió**. Nadie truena ni avisa. El GIL no lo evita: garantiza que cada instrucción de bytecode corra entera, no que lo hagan las tres de `+=` juntas.

Desde Python 3.10 el intérprete sólo cambia de hilo en ciertos puntos: al entrar a una función y al volver al inicio de un bucle. Por eso un `contador += 1` solo, con GIL, casi nunca muestra la pérdida; sin GIL (3.14t) la muestra con facilidad. La celda 2.3 mete la llamada `suma_uno` entre leer y escribir: entrar a esa función es un punto donde el intérprete puede cambiar de hilo.

**Matemática.** Con 4 hilos y 100 000 sumas cada uno, lo esperado es $4\times100\,000=400\,000$. Cada intercalado como el de la tabla pierde una suma, así que el resultado es $400\,000-(\text{sumas perdidas})\le400\,000$, y el número de pérdidas cambia de corrida a corrida.

**Ejemplo** (medición real, celda 2.3): esperado 400,000, obtenido 199,769 en una corrida. Obtener 400,000 en **una** corrida **no prueba** que no haya carrera: sólo que esa vez el intercalado no la mostró.

::: definition {#cmp-def-region-critica title="Región crítica y Lock"}
Una **región crítica** es un trozo de código que lee y escribe un dato compartido y que **sólo un hilo a la vez** puede ejecutar. Un `threading.Lock` la protege: `with candado:` entra si nadie lo tiene y, si no, deja al hilo `blocked` (espera algo que otra tarea del mismo programa debe soltar: no es `wait`, porque no falta nada externo, ni `ready`, porque no le falta CPU) hasta que el otro salga; al salir lo suelta, incluso si hubo un error.
:::

Con el `Lock`, el paso 2 de la traza cambia: B intenta entrar, A tiene el candado, B queda `blocked` hasta que A escribe 6 y sale; entonces B lee 6 y escribe 7.

**Arquitectura: memoria compartida contra aislada.**

| | Hilos (memoria compartida) | Procesos (memoria aislada) |
|---|---|---|
| comunicar un dato | leer la variable: gratis | copiarlo (serializar con `pickle`, mandarlo, deserializar) |
| riesgo | condición de carrera en todo dato mutable compartido | ninguno sobre variables ordinarias; sí sobre un archivo o una BD que compartan |
| defensa | `Lock` alrededor de la región crítica | no compartir; juntar resultados al final |
| una falla | un hilo que corrompe memoria o se cuelga con el `Lock` afecta a todo el proceso | un proceso que muere no tumba a los otros |
| costo de crear | bajo | alto: arrancar un intérprete e importar módulos |

**La región crítica es serialización deliberada.** Mientras un hilo está dentro del `with`, los demás que la necesitan están `blocked`: ese trozo corre en serie aunque haya 32 hilos. Por eso se protege **lo mínimo** (leer y escribir el dato, no la llamada de red de 0.2 s). Un `Lock` que envuelve el cuerpo entero convierte a los hilos en una ejecución secuencial con más pasos. En la página 6 ese trozo serial tiene nombre: fracción serial $f$.

**Sistema real: el servidor de la clase.** `servidor.py` cuenta las peticiones con `peticiones += 1`, y ese `+=` va dentro de `with candado:`, con un único `Lock` global que también protege el diccionario `ventas`. Sin él, dos peticiones simultáneas pueden perder una cuenta, como en la tabla (raro con GIL, frecuente sin él); el candado lo garantiza en cualquier versión.

## Arquitectura: hilo por conexión contra prefork

::: figure {#cmp-arq-servidor-clase title="El servidor de la clase: un hilo por conexión y un Lock global"}
![Diagrama del servidor de la clase por dentro. A la izquierda, varios clientes abren conexiones; entran a la cola listen del kernel, de capacidad 1024; accept toma cada conexión y ThreadingHTTPServer crea un hilo nuevo para ella, sin tope de hilos, que vive lo que vive la conexión con keep-alive. Todos los hilos llegan a un único Lock que protege el estado compartido en memoria: el diccionario de ventas y el contador de peticiones. Una marca señala los dos riesgos: no hay límite de hilos y el Lock global serializa.](_assets/cmp-arq-servidor-clase.svg)
:::

**Hilo por conexión.**

- **Qué es.** Cada conexión aceptada recibe un hilo que la atiende de principio a fin. El servidor de la clase es `ThreadingHTTPServer`: un hilo por conexión, **sin tope**; `request_queue_size = 1024` es la cola `listen` del kernel, no de Python; con HTTP/1.1 y keep-alive, el hilo vive lo que vive la conexión; `?lento=` hace `time.sleep` y bloquea **sólo su hilo**.
- **Cuándo sí.** Pocas decenas o cientos de conexiones, trabajo que casi sólo espera, librerías bloqueantes (`requests`, un driver de BD síncrono). El código se lee de arriba abajo.
- **Cuándo no.** Miles de conexiones ociosas (keep-alive, WebSocket): cada una retiene un hilo. Manejadores que calculan en Python: el GIL los turna en una CPU.
- **Qué cuesta.** Una pila por hilo y un cambio de contexto por turno; sin tope, un pico abre tantos hilos como conexiones. Todo estado compartido pide `Lock`, y un `Lock` global es un punto de serialización.
- **Sistema real.** `ThreadingHTTPServer` (el de la clase), Apache httpd con MPM `worker`.

**Prefork (procesos creados al arrancar).**

- **Qué es.** Un proceso maestro crea $K$ procesos al arrancar; cada uno acepta conexiones del mismo socket y las atiende. Cada proceso tiene su intérprete y su GIL.
- **Cuándo sí.** Peticiones que calculan en Python ($K$ procesos usan hasta $\min(K,P)$ CPU); aislar fallas (un proceso que muere no tumba a los demás).
- **Cuándo no.** Estado en memoria que todas las peticiones deben ver: el diccionario `ventas` del servidor de la clase, con 4 procesos, serían 4 diccionarios distintos. Ese estado se muda a una BD o a Redis.
- **Qué cuesta.** $K$ veces la memoria de un proceso; arranque lento; $K>P$ en carga de CPU no agrega capacidad.
- **Sistema real.** Gunicorn con workers `sync` (su documentación sugiere `2 × núcleos + 1` como punto de partida), Apache MPM `prefork`, PostgreSQL (un proceso por conexión).

| | Hilo por conexión | Prefork |
|---|---|---|
| unidad que atiende | hilo | proceso |
| ejecuta Python a la vez | 1 por proceso | hasta $\min(K,P)$ |
| estado en memoria | compartido, con `Lock` | aislado: uno por proceso |
| tope natural | ninguno (hay que ponerlo) | $K$ |
| una falla | puede tumbar a todo el proceso | queda en su proceso |
| sirve para | esperas, pocas decenas o cientos | cálculo por petición, aislamiento |

Los dos se combinan: Gunicorn con workers de hilos (`gthread`) es prefork **y** hilos en cada proceso. El tercer modelo, un event loop que espera miles de conexiones en un hilo, es la página siguiente; los tres lado a lado, en [[arquitectura-y-estrategia]].

## Speedup y eficiencia con procesos

::: definition {#cmp-def-speedup title="Speedup y eficiencia"}
**En palabras.** El speedup divide el tiempo de una versión base, que siempre se declara, entre el de la nueva; la eficiencia reparte ese speedup entre los $N$ trabajadores.

**Formalmente.** $S=T_{\text{base}}/T_{\text{nueva}}$; contra un trabajador, $S(N)=T(1)/T(N)$; $E(N)=S(N)/N$. ([[notacion-computo]])

 $E=1$ es reparto perfecto. Todo speedup **declara su base**: aquí la base es el mismo pool con un proceso.
:::

**Otro ángulo.** Si repartir fuera gratis, 4 procesos tardarían la cuarta parte: $1.45/4\approx0.363$ s. Tardaron 0.54 s. La diferencia es lo que **no** se repartió.

**Matemática** (mediciones de referencia: 4 tareas de `calcula`, pool de 1, 2 y 4 procesos, una corrida en una máquina de 8 CPU lógicas; tus cifras serán otras):

| $N$ | $T(N)$ (s) | $S(N)=T(1)/T(N)$ | $E(N)=S/N$ |
|---:|---:|---:|---:|
| 1 | 1.45 | 1 | 1 |
| 2 | 0.75 | $1.45/0.75\approx1.93$ | $\approx0.97$ |
| 4 | 0.54 | $1.45/0.54\approx2.69$ | $\approx0.67$ |

- Es $\operatorname{speedup}_{\text{pool}}$: el pool contra sí mismo con un proceso. No hay en la tabla una versión directa sin pool, así que no mide lo que gana la aplicación y esconde el costo de tener pool.
- **Estos tres números no identifican la fracción serial $f$.** Se puede ajustar un modelo de dos parámetros a tres puntos, pero queda un solo grado de libertad para comprobarlo, es una sola corrida, y decir que lo no repartido es arranque de procesos y copias es una hipótesis, no una medición. Se retoma, con Amdahl, en [[calcular-en-paralelo]].

**Ejemplo.** La eficiencia baja de 0.97 a 0.67 al pasar de 2 a 4 procesos sobre 8 CPU: no faltan CPU. Lo que crece es lo que no se reparte.

**Arquitectura.** Antes de subir $K$ en un pool de procesos o en prefork, mide $T(1)$, $T(2)$ y $T(4)$. Si $E$ cae rápido, más procesos sólo agregan memoria; el arreglo está en el trabajo (menos copias, tareas más grandes, vectorizar), no en el número de procesos.

## La decisión hasta aquí

| Si el trabajo… | Huella medible | Usa | Página |
|---|---|---|---:|
| casi todo espera | CPU del cliente $\ll$ reloj ($\rho$ pequeño) | reorganizar esperas: solaparlas | 1 |
| casi todo calcula | CPU $\approx$ reloj ($\rho\approx1$) | acelerar o repartir el cálculo | 1 |
| espera, pocas decenas de llamadas, librería bloqueante | con hilos, $T$ cae hacia una llamada | hilos (o un servidor de hilo por conexión) | 2 |
| calcula en Python puro | 4 hilos ≈ 1 hilo; con procesos $T$ baja | procesos, a lo más $P$ (prefork en un servidor) | 2 |
| comparte un dato mutable entre hilos | resultado distinto entre corridas | `Lock` sólo alrededor de la región crítica, o no compartir | 2 |
| necesita aislamiento entre peticiones | una falla no debe tumbar a las demás | procesos; el estado compartido va a una BD | 2 |

## Código

Todo corre contra el servidor de la clase (`FDD_SILENCIO=1 uv run python servidor.py`, en otra terminal) desde `computo.ipynb`.

**Haz (celda 2.1):** las 20 llamadas de la página 1, ahora con 32 hilos.

```python
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from cable import URL                      # http://127.0.0.1:8026, el servidor de la clase

def pide(i):                               # el servidor duerme 0.2 s y contesta
    return requests.get(f"{URL}/ventas?lento=0.2", timeout=5).status_code

inicio = time.perf_counter()
with ThreadPoolExecutor(max_workers=32) as hilos:   # hasta 32 hilos del mismo proceso
    codigos = list(hilos.map(pide, range(20)))      # lanza las 20 sin esperar a la anterior
print(f"{len(codigos)} llamadas, status {set(codigos)}, {time.perf_counter() - inicio:.2f} s")
```

**Python que quizá no has visto.**

| Qué | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `ThreadPoolExecutor(max_workers=32)` | un pool de hasta 32 hilos que se crean una vez y se reutilizan | da un hilo a cada llamada bloqueante para que sus esperas se solapen |
| `with … as hilos:` | al salir del bloque espera a que terminen todos los hilos y los cierra | sin él, el reloj se detendría antes de que acaben las llamadas |
| `hilos.map(pide, range(20))` | reparte las 20 llamadas entre los hilos y devuelve los resultados **en orden** | lanza todas sin esperar a la anterior; `list(...)` espera a que estén todas |

**Qué pasó.** Con 20 tareas y 32 hilos, cada llamada tuvo su hilo y quedaron 12 ociosos. Gantt simplificado (cada llamada ejecuta unos ms y espera ~0.2 s):

| | 0 → ~0.2 s | ~0.2 → 0.23 s |
|---|---|---|
| hilos 1–20 | arrancan casi a la vez; cada uno manda su petición y **espera** (suelta el GIL) | reciben respuesta por turnos del GIL y terminan |
| hilos 21–32 | sin trabajo | sin trabajo |
| GIL | casi siempre libre | un hilo a la vez |

Las vidas se solapan (concurrente) y la ejecución nunca es simultánea (no paralela). Contra 4.04 s en serie, el ahorro es **espera solapada**, no cálculo repartido. Con la medición de referencia, $L=\lambda W\approx(20/0.23)\times0.202\approx17.6$ llamadas en vuelo en promedio. Coincide con el speedup sobre la serie, $4.04/0.23$, sólo porque cada llamada sigue durando $W\approx0.202$ s en las dos versiones.

**Deberías ver** (tu número cambia con tu máquina y su carga):

```text
20 llamadas, status {200}, 0.23 s
```

**Haz (celda 2.2):** el mismo cálculo, 4 veces, con 1, 2 y 4 procesos.

```python
import os
import time
from concurrent.futures import ProcessPoolExecutor
from trabajo_computo import calcula        # vive en un archivo: el proceso hijo la importa

def mide(n_procesos):
    inicio = time.perf_counter()
    with ProcessPoolExecutor(max_workers=n_procesos) as procesos:
        list(procesos.map(calcula, [5_000_000] * 4))   # 4 trabajos idénticos de sólo CPU
    return time.perf_counter() - inicio                # incluye arrancar los procesos

print("CPU lógicas:", os.cpu_count())      # el tope P de ejecución simultánea
for n in (1, 2, 4):
    print(f"{n} proceso(s): {mide(n):.2f} s")
```

**Python que quizá no has visto.**

| Qué | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `ProcessPoolExecutor(max_workers=n)` | arranca `n` procesos, cada uno con su intérprete y su GIL | es la única forma, con Python puro, de que dos cálculos ejecuten a la vez |
| `from trabajo_computo import calcula` | importa la función desde un archivo | el proceso hijo recibe el **nombre** de la función y la importa; una función definida en la celda vive en `__main__` del kernel y el hijo no la encuentra (ver [[el-gil]]) |
| `if __name__ == "__main__":` (no aparece) | en un archivo `.py`, protege el código que lanza procesos para que el hijo no lo repita al importar | en el notebook no hace falta porque el hijo importa `trabajo_computo`, no la celda; en un script, sí |

**Qué pasó.** Con $n=4$ tareas iguales y $N$ procesos, $P$ = 8:

| $N$ | Tandas $\lceil4/N\rceil$ | $T(N)$ medido | Ideal $T(1)/N$ |
|---:|---:|---:|---:|
| 1 | 4 | 1.45 s | — |
| 2 | 2 | 0.75 s | $T(1)/2$ |
| 4 | 1 | 0.54 s | $T(1)/4$ |

Con 2 procesos hay dos filas de CPU ocupadas a la vez: paralelo. El total queda por encima del ideal en las dos filas: lo que no se repartió. $S$ y $E$ con estos números, en la sección de speedup de arriba.

**Deberías ver:**

```text
CPU lógicas: 8
1 proceso(s): 1.45 s
2 proceso(s): 0.75 s
4 proceso(s): 0.54 s
```

**Haz (celda 2.3):** 4 hilos suman 1 al mismo contador, 100 000 veces cada uno, sin candado.

```python
import sys, threading
sys.setswitchinterval(1e-6)          # turno cada 1 µs (de fábrica, 5 ms): la carrera aparece casi siempre
contador = 0
def suma_uno(x):                     # la llamada abre un punto donde el intérprete puede cambiar de hilo
    return x + 1
def suma(veces):
    global contador                  # los 4 hilos escriben la misma variable
    for _ in range(veces):
        actual = contador            # 1. leer
        contador = suma_uno(actual)  # 2-3. sumar y escribir
hilos = [threading.Thread(target=suma, args=(100_000,)) for _ in range(4)]
for h in hilos: h.start()
for h in hilos: h.join()             # espera a que terminen los cuatro
print(f"esperado {4 * 100_000:,}, obtenido {contador:,}")
sys.setswitchinterval(0.005)         # regresa al valor de fábrica para las celdas siguientes
```

**Python que quizá no has visto.**

| Qué | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `sys.setswitchinterval(1e-6)` | cada cuánto pide el intérprete al hilo con el GIL que lo suelte | con 5 ms la carrera ocurre sólo a veces; con 1 µs se ve casi siempre. No garantiza el intercalado: depende de la versión de Python |
| `suma_uno(actual)` | una función trivial entre leer y escribir | desde 3.10 el intérprete cambia de hilo al entrar a una función; sin esa llamada la carrera casi nunca aparece con GIL |
| `global contador` | la función escribe la variable del módulo, no una local | es el dato compartido entre los hilos |
| `threading.Thread(target=…, args=…)` | crea un hilo que correrá `suma(100_000)` | se quieren 4 hilos sobre el mismo dato |
| `h.start()` / `h.join()` | arranca el hilo / espera a que termine | sin `join`, el `print` leería el contador a medias |

**Qué pasó.** La traza de la tabla de la condición de carrera, repetida muchas veces: un hilo lee, el intérprete le da el turno a otro en la llamada a `suma_uno`, el otro lee el mismo valor, y una de las dos escrituras pisa a la otra. Faltan 400,000 − 199,769 sumas. El programa no truena ni avisa, y el número cambia en cada corrida. Si una corrida da 400,000, **eso no prueba que no haya carrera**.

**Deberías ver** (el obtenido cambia en cada corrida):

```text
esperado 400,000, obtenido 199,769
```

**Haz (celda 2.4):** el mismo conteo, con un `Lock` alrededor de la región crítica.

```python
import sys, threading
sys.setswitchinterval(1e-6)          # el mismo forzado de la celda 2.3
contador, candado = 0, threading.Lock()
def suma_uno(x):
    return x + 1
def suma_con_candado(veces):
    global contador
    for _ in range(veces):
        with candado:                # región crítica: leer y escribir sin que otro hilo se cuele
            contador = suma_uno(contador)
hilos = [threading.Thread(target=suma_con_candado, args=(100_000,)) for _ in range(4)]
for h in hilos: h.start()
for h in hilos: h.join()
print(f"esperado {4 * 100_000:,}, obtenido {contador:,}")
sys.setswitchinterval(0.005)         # regresa al valor de fábrica
```

**Python que quizá no has visto.**

| Qué | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `threading.Lock()` | crea un candado que sólo un hilo puede tener a la vez | protege la lectura y la escritura del contador |
| `with candado:` | toma el candado al entrar (o deja al hilo `blocked` hasta que se libere) y lo suelta al salir, incluso si hay error | junta leer y escribir: el cambio de hilo puede ocurrir, pero el otro hilo no entra al bloque |

**Qué pasó.** La traza con candado:

| Paso | hilo A | hilo B | contador |
|---:|---|---|---:|
| 1 | toma el candado, lee 5 | — | 5 |
| 2 | (le quitan el turno) | intenta entrar: `blocked` | 5 |
| 3 | escribe 6, suelta el candado | — | 6 |
| 4 | — | toma el candado, lee 6, escribe 7 | 7 |

La celda define todo de nuevo (contador, `suma_uno`, el candado) para no depender de la anterior. El precio: la región crítica corre en serie; aquí es casi todo el cuerpo del bucle, así que los 4 hilos no aportan nada más que corrección.

**Deberías ver:**

```text
esperado 400,000, obtenido 400,000
```

La versión larga y paso a paso está en el notebook, tema 2.

## Al diseñar / al revisar código de IA, busca…

- **«Concurrente» o «paralelo» sin un Gantt ni una medición.** Pregunta qué tareas se cuentan, cuántas CPU, y cuánto tarda con 1 y con $N$. Que el total bajara no prueba paralelismo.
- **Hilos o `asyncio` para acelerar un cálculo en Python puro.** Son concurrentes, no paralelos: el GIL los turna en una CPU.
- **Un contador, lista o diccionario compartido entre hilos, escrito sin `Lock`** (`+=`, leer y luego escribir). Es una carrera aunque hoy el resultado salga bien.
- **Un `Lock` que envuelve todo el cuerpo, o una llamada de red dentro del `with`.** Serializa la parte que querías solapar.
- **Un servidor de hilo por conexión sin tope ni timeouts** frente a tráfico público: un pico o una dependencia lenta abre un hilo por conexión hasta agotar memoria.
- **Prefork (o varias réplicas) con estado en variables del proceso.** Cada proceso tiene su copia: las respuestas dependen de qué proceso te tocó.
- **Procesos con una función definida en la celda o un `lambda`.** El hijo no la encuentra; debe vivir en un archivo importable.
- **Un speedup sin base declarada, o $f$ despejada de una sola corrida.**

Sigue con [[asincrono-y-el-event-loop]]: cómo espera muchas peticiones un solo hilo, y quién decide el turno.
