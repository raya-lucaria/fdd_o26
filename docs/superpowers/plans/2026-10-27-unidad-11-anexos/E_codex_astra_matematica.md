**La corrección central es `Paralelo ⊂ Concurrente`, siempre que compares las mismas tareas y el mismo nivel de detalle.** La celda «paralelo sin concurrente» debe quedar como imposible. También hay que separar **asincronía**, que describe un contrato de ejecución, de **solapamiento de ejecución y espera**, que describe una traza.

No guardé un archivo: el encargo no especifica su ruta y este entorno permite únicamente lectura. Entrego el contenido completo aquí. No modifiqué archivos ni ejecuté benchmarks o pytest.

**1. Framework mínimo corregido y hallazgos**

Antes de introducir símbolos, fija estas condiciones:

- Analizas una ejecución concreta de un conjunto finito de tareas.
- Cada tarea representa **un flujo secuencial**, capaz de ocupar como máximo una CPU a la vez. Si delega trabajo paralelo, representa sus subtareas por separado.
- Conservas el mismo conjunto de tareas y la misma frontera del sistema al comparar propiedades. La CPU del servidor remoto no es CPU del cliente.
- Usas intervalos **semiabiertos**: `[a, b)` incluye `a`, excluye `b`.
- Los intervalos son finitos; `dur(A)` suma sus longitudes sin contar dos veces sus solapamientos.

| Elemento | Definición mínima corregida |
|---|---|
| Tiempo | `T = ℝ≥0`. Un instante `t ∈ T` se expresa en segundos o milisegundos. Reserva `T` para este conjunto; usa `D` para una duración total. |
| Tareas | `Tareas = {τ₁, …, τₙ}`. `τᵢ` identifica una tarea, no una duración ni necesariamente un objeto `asyncio.Task`. |
| Llegada | `arrival(τᵢ)` es cuando aparece la solicitud. Puede preceder al inicio de su atención. |
| Inicio y fin | `start(τᵢ)` es cuando admites la tarea para atenderla; `end(τᵢ)` es cuando termina. Para las tareas del ejemplo: `arrival ≤ start < end`. |
| Vida activa | `Lᵢ = [start(τᵢ), end(τᵢ))`. Incluye ejecución y suspensiones posteriores a la admisión, incluso la espera inicial de turno. |
| Ejecución | `exec(τᵢ) ⊆ Lᵢ`: instantes en que una CPU ejecuta ese flujo. |
| Espera | `wait(τᵢ) ⊆ Lᵢ`: instantes en que el flujo está suspendido esperando E/S o un temporizador pendiente. Esperar turno de CPU no pertenece aquí. |
| Lista | `ready(τᵢ) ⊆ Lᵢ`: puede continuar, pero todavía no recibe turno de ejecución. |
| Bloqueada por sincronización | Al introducir semáforos, locks o dependencias, añade `blocked(τᵢ)`: no puede continuar hasta obtener el permiso o resultado requerido. No lo confundas con E/S. |
| Partición de estados | `Lᵢ = exec(τᵢ) ⊔ wait(τᵢ) ⊔ ready(τᵢ) ⊔ blocked(τᵢ)`. `⊔` significa unión de conjuntos disjuntos. Inicialmente puedes omitir `blocked` cuando sea vacío. |
| Duraciones | `eᵢ = dur(exec(τᵢ))`, `wᵢ = dur(wait(τᵢ))`, `rᵢ = dur(ready(τᵢ))`, `bᵢ = dur(blocked(τᵢ))`. Entonces `end − start = eᵢ + wᵢ + rᵢ + bᵢ`. |
| Latencia | `latenciaᵢ = end(τᵢ) − arrival(τᵢ)`. Incluye la cola anterior a `start`. |
| Ejecutando en un instante | `ExecutingAt(t) = {τᵢ ∈ Tareas : t ∈ exec(τᵢ)}`. |
| Capacidad CPU | `P` es el número de unidades de ejecución disponibles en el modelo. `card(ExecutingAt(t)) ≤ P`. Para empezar, supone núcleos equivalentes sin SMT ni competencia externa. |
| Secuencial | Para todo `i ≠ j`: `end(τᵢ) ≤ start(τⱼ)` o `end(τⱼ) ≤ start(τᵢ)`. |
| Concurrente | Existen `i ≠ j` tales que `max(startᵢ, startⱼ) < min(endᵢ, endⱼ)`. Sus vidas activas se solapan durante un intervalo positivo. |
| Paralelo | Existen `i ≠ j` tales que `dur(exec(τᵢ) ∩ exec(τⱼ)) > 0`. Equivalentemente, hay un intervalo positivo con al menos dos tareas ejecutando. |
| Ejecución durante espera ajena | Existen `i ≠ j` tales que `dur(exec(τⱼ) ∩ wait(τᵢ)) > 0`. Es una propiedad observable de la traza; **no es la definición de asincronía**. |
| Asíncrono | La interfaz separa solicitar una operación de obtener su resultado: no obliga al llamador a bloquearse hasta su finalización. La finalización se observa mediante una notificación, callback, futuro u otro mecanismo. |

La elección de `start` debe aparecer junto al primer Gantt. Una solicitud esperando en la cola de entrada todavía puede no estar admitida; una corrutina ya admitida y esperando turno sí está en `ready`. Si cambias esa frontera, cambias qué solapamiento estás midiendo.

**Correcciones concretas de las fuentes:**

| Fuente | Problema | Corrección |
|---|---|---|
| [p26, 02_secuencial.md](/home/uumami/itam/fdd_p26/clase/16_computo/02_secuencial.md:34) y [03_concurrencia_y_asincronia.md](/home/uumami/itam/fdd_p26/clase/16_computo/03_concurrencia_y_asincronia.md:19) | Los intervalos cerrados hacen concurrentes dos tareas que solamente se tocan al terminar/empezar. También hacen coincidir `exec` y `wait` en sus fronteras. | Usa `[a, b)` y solapamiento de duración positiva. |
| p26, `02`, líneas 60–71 | Presenta la disyunción ejecución/espera como universal y define CPU-bound mediante `wait = ∅`. | La disyunción presupone un flujo secuencial. **CPU-bound describe un cuello de botella**, no ausencia absoluta de E/S; I/O-bound tampoco significa simplemente tener alguna espera. |
| p26, `02`, líneas 114–119 | Deduce que el tiempo total siempre es la suma de las vidas y que «nadie» usa CPU durante las esperas. | La suma exige tareas consecutivas sin huecos ni costos externos. La CPU queda sin trabajo **de las tareas observadas**; otros procesos pueden utilizarla. |
| p26, `02`, líneas 167–170 | Usa latencias que incluyen cola sin haber definido llegada. | Separa `end − arrival` de `end − start`. |
| p26, `03`, líneas 39–96 | Define asincronía como `execⱼ ∩ waitᵢ ≠ ∅`, pero sitúa M2 como asíncrono sin ese solapamiento. | Renombra la fórmula como «ejecución durante espera ajena». M2 puede usar una interfaz asíncrona y atender tareas secuencialmente. |
| p26, `03`, líneas 93–103 | La fórmula de M2 no exige vidas disjuntas. | Añade expresamente la condición secuencial. No basta con prohibir `execⱼ ∩ waitᵢ`. |
| p26, `03`, líneas 139–165 | M3 tiene huecos de ejecución que el modelo original no representa formalmente. Además, falta `i ≠ j` en su condición de concurrencia. | Añade `ready` y exige tareas distintas. |
| [p26, 05_paralelismo.md](/home/uumami/itam/fdd_p26/clase/16_computo/05_paralelismo.md:41) | La demostración concluye correctamente `Paralelo ⇒ Concurrente`, pero el título escribe `Paralelo ⊃ Concurrente`. | La inclusión correcta es `Paralelo ⊂ Concurrente`. |
| [o26, página 2](/home/uumami/itam/fdd_o26/course/10_apis/2_computo_y_concurrencia/2_concurrente_paralelo_asincrono.md:178) | La celda «paralelo sin concurrente» cuenta operaciones de aplicación para una propiedad y subtareas internas para la otra. | Declárala imposible a granularidad fija. Explica NumPy aparte como cambio de nivel de observación. |
| p26, `03`, líneas 174–179; o26, página 2, líneas 33 y 300 | Extienden la restricción del GIL a toda ejecución de los hilos. | Restringe la afirmación a ejecución de Python bajo el mismo GIL. |
| p26, `03`, líneas 216–218 | Compara 3.6 s de ocio total con 0.6 s de ocio principal. | El ocio total concurrente es `0.6 + 0.1 + 0.1 = 0.8 s`: reducción `3.6/0.8 = 4.5×`. |
| p26, `05`, tabla de Amdahl | Para fracción serial 90 %, publica 1.07× y 1.08× con 4 y 8 CPU. | Corresponden aproximadamente **1.08× y 1.10×**. La tabla de o26 es correcta. |

**¿Puede `wait = ∅` en M3?** Sí, como simplificación de tareas exclusivamente de CPU. Entre turnos, una tarea está en `ready`; si espera adquirir el GIL, puede estar en `blocked`. Por tanto:

```text
wait(τᵢ) = ∅  no implica  exec(τᵢ) = Lᵢ.
```

**¿Hace falta `i ≠ j` en `exec(τⱼ) ∩ wait(τᵢ)`?** Con la partición de estados ya es matemáticamente redundante: una misma tarea no puede ejecutar y esperar simultáneamente. Conviene conservarlo para expresar que otra tarea aprovecha ese intervalo y mantener coherencia con las demás definiciones.

**La prueba corregida de la inclusión** necesita declarar `exec(τᵢ) ⊆ Lᵢ`:

```text
exec(τᵢ) ∩ exec(τⱼ) ⊆ Lᵢ ∩ Lⱼ

Si la intersección izquierda tiene duración positiva,
también la tiene la derecha.

Por tanto: Paralelo ⇒ Concurrente.
```

El recíproco es falso: basta una CPU que alterne entre dos tareas todavía inconclusas.

**Restricción GIL.** Introduce una proyección de la ejecución:

```text
exec_Python(τᵢ) ⊆ exec(τᵢ)

Para cada intérprete I con GIL habilitado y todo t:
card({τᵢ asociada a I : t ∈ exec_Python(τᵢ)}) ≤ 1
```

Esto no impone `P = 1` a la máquina ni limita toda ejecución nativa. El código compilado que libera el GIL puede seguir utilizando CPU mientras otro hilo ejecuta Python. Un único event loop ejecuta una tarea a la vez por su planificación cooperativa, incluso sin GIL. [Documentación de CPython](https://docs.python.org/3.14/c-api/threads.html), [documentación de asyncio](https://docs.python.org/3.14/library/asyncio-task.html#task-object).

Para el curso basta asumir un intérprete por proceso. Como precisión docente, un proceso también puede alojar intérpretes con GIL independientes. [Documentación de subintérpretes](https://docs.python.org/3.14/c-api/subinterpreters.html).

**Asincronía y event loop.** La definición actual de la página 2 es demasiado específica: llamar una función `async def` produce una corrutina; no necesariamente una tarea programada. Además, `await` no garantiza una suspensión cuando el resultado ya está disponible. [Corrutinas y tareas](https://docs.python.org/3.14/library/asyncio-task.html#awaitables).

La secuencia conceptual que debe mostrar el diagrama es:

```text
ready → exec → wait → ready → exec → terminada
          │
          └─ si necesita un permiso pendiente → blocked → ready
```

El event loop selecciona una tarea lista y la ejecuta hasta que se suspende o termina. Cuando llega una respuesta, la tarea queda habilitada para continuar; **no interrumpe automáticamente** a la que está ejecutando. El diagrama debe distinguir «respuesta disponible» de «tarea reanudada».

`gather` incorpora varias operaciones a esa planificación; el semáforo limita cuántas pueden entrar a una región. Su límite no es `P`: un permiso puede permanecer ocupado mientras la tarea espera red.

**Duración total, speedup y Amdahl:**

```text
D = t_fin_de_medición − t_inicio_de_medición
```

Si no hay preparación ni cierre fuera de las tareas:

```text
D = maxᵢ end(τᵢ) − minᵢ start(τᵢ)
```

Para una ejecución secuencial:

```text
D = Σᵢ dur(Lᵢ) + huecos + costos externos a las tareas
```

El speedup siempre declara su referencia:

```text
speedup = D_base / D_nueva
```

No tiene unidades. Menor que 1 significa que la nueva versión tarda más.

Para Amdahl, usa `s` como fracción serial y conserva `P` para capacidad:

```text
0 ≤ s ≤ 1
D_ideal(P) = D₁ × [s + (1 − s)/P]
speedup_ideal(P) = 1 / [s + (1 − s)/P]
```

Supone carga fija, fracción serial constante, trabajo repartible suficientemente divisible, recursos equivalentes y reparto perfecto. Si `s > 0`, el límite es `1/s`; si `s = 0`, el modelo da `speedup = P`, sin techo finito.

Con costos adicionales y desequilibrio:

```text
D_real(P) = D₁ × [s + (1 − s)/P] + h(P)
```

`h(P)` recoge costos que ese modelo ideal omite. No conviertas todo costo adicional en una fracción serial constante: puede crecer con `P`.

La [página 4 actual](/home/uumami/itam/fdd_o26/course/10_apis/2_computo_y_concurrencia/4_vectorizar.md:244) acierta al advertir que **0.7 % de CPU no determina `s`**. También debe aclarar que una medición por debajo o encima de la curva exige revisar sus supuestos; Amdahl no es un límite universal entre implementaciones que cambian algoritmo, representación o acceso a memoria.

**Speedup de procesos.** Separa `k`, número de procesos trabajadores, de `P`, capacidad CPU:

```text
speedup_pool(k) = D_pool(1) / D_pool(k)
speedup_aplicación(k) = D_secuencial_directa / D_pool(k)
```

Son comparaciones distintas. La medición publicada da:

```text
speedup_pool(2) = 2.34 / 1.45 ≈ 1.61×
speedup_pool(4) = 2.34 / 1.00 = 2.34×
```

No permite identificar por sí sola la fracción serial.

Para `n` trabajos **iguales, independientes, indivisibles y exclusivamente de CPU**, cada uno de duración `c`, una aproximación más concreta es:

```text
q = min(k, P)
D_pool(k) ≈ techo(n/q) × c + h(k)
```

Esto muestra por qué importan el tamaño de los trabajos, las últimas tandas incompletas y el costo de transferir datos. Crear procesos no garantiza ni paralelismo efectivo ni mejora.

**Vectorización.** Conserva la separación de la página 4: vectorizar no implica utilizar varias CPU. La aceleración publicada es `0.188/0.0119 ≈ 15.8×`; esa razón no demuestra paralelismo ni cuantifica SIMD. Muchas operaciones de NumPy liberan el GIL, pero no todas; liberarlo tampoco crea automáticamente otros hilos. [Documentación de NumPy](https://numpy.org/doc/stable/reference/thread_safety.html).

La fórmula exacta de suma de cuadrados de la página 4 es correcta:

```text
Σ desde j=0 hasta n−1 de j² = (n−1)n(2n−1)/6
```

La comparación mediante `isclose` verifica proximidad numérica, no igualdad exacta.

**Distribuido.** En [07_distribuido_intro.md](/home/uumami/itam/fdd_p26/clase/16_computo/07_distribuido_intro.md:179), elimina `Distribuido ⊇ Paralelo ⊇ Concurrente`. Distribución describe la ubicación y comunicación entre componentes; no constituye esa inclusión entre ejecuciones.

También corrige:

- «No existe reloj global» → no se presupone un reloj perfectamente sincronizado y accesible a todos. Puedes usar un tiempo global ideal para razonar sin afirmar que los nodos lo conocen.
- `Mem(nᵢ) ∩ Mem(nⱼ) = ∅` requiere hablar de celdas físicas o espacios identificados por nodo, no de valores ni direcciones numéricas.
- La concurrencia **causal entre eventos**, mencionada con relojes vectoriales, no es la definición de solapamiento temporal entre tareas.
- Agregar máquinas no elimina Amdahl para una carga fija.
- `D ≈ duración de una petición` necesita suficiente capacidad, independencia y ausencia de saturación; no es una consecuencia automática de usar asyncio o distribuir.

**2. Orden de introducción para licenciatura**

Cada paso debe terminar con su consecuencia arquitectónica antes de mostrar código.

| Paso | Símbolos y explicación | Ejemplo y decisión de arquitectura |
|---|---|---|
| 1 | Una tarea `τᵢ`; conjunto `Tareas`. | Una llamada HTTP; luego las 20 llamadas. Fija que observas el cliente. |
| 2 | Tiempo `T`, `start`, `end`, intervalo `[a,b)`. | El lote tarda 4.04 s; media de 0.202 s por llamada. Dibuja atención una por una. |
| 3 | `exec`, `wait`, `dur`; después `eᵢ`, `wᵢ`. | El cliente acumuló aproximadamente 0.03 s de CPU. Acelerar únicamente su cálculo tiene poco margen. |
| 4 | `ready`; posteriormente `blocked`. | Una respuesta puede estar disponible sin recibir turno. Introduce colas, capacidad limitada y semáforos. |
| 5 | `ExecutingAt(t)` y `P`. | Una fila de CPU muestra quién ejecuta. Distingue solicitudes pendientes de capacidad de cálculo. |
| 6 | Secuencial y concurrencia. | Solapar vidas permite mantener varias solicitudes pendientes. Presenta pool de hilos y atención mediante eventos. |
| 7 | `execⱼ ∩ waitᵢ`; también `waitᵢ ∩ waitⱼ`. | Se solapan cálculos breves con esperas y varias esperas entre sí. Habla de límites del servidor y conexiones. |
| 8 | Asincronía como contrato; estados del event loop. | Compara llamadas esperadas una por una con varias pendientes. Define corrutina, programación de tareas y suspensión. |
| 9 | Paralelismo y GIL. | Añade una segunda fila CPU. Presenta procesos para cálculo independiente, con costos de comunicación. |
| 10 | `D`, speedup, `s`, Amdahl y `h(P)`. | Evalúa si el trabajo compensa repartirlo; distingue latencia individual, duración del lote y capacidad de atención. |
| 11 | Jerarquía de tareas y distribución. | Una llamada a NumPy puede contener trabajo interno; una petición puede delegar a otro proceso o nodo. Explicita cada frontera. |

**Tratamiento correcto de las cifras iniciales:**

```text
D = 4.04 s
CPU medida ≈ 0.03 s
D − CPU ≈ 4.01 s

0.03 / 4.04 ≈ 0.743 % → 0.7 %
4.01 / 4.04 ≈ 99.257 % → 99.3 %
```

Presenta el 99.3 % como **aproximación del tiempo sin CPU del cliente**, dominado por espera en este experimento. No lo identifiques exactamente con `Σwᵢ`: puede incluir espera de turno y otros efectos. `process_time` mide CPU de todo el proceso, no de una tarea individual. Con ejecución multihilo paralela puede acumular más segundos de CPU que segundos de pared. [Documentación de los relojes de Python](https://docs.python.org/3.14/library/time.html#time.process_time).

Para enseñar, puedes construir una aproximación homogénea de 20 tareas con media de 1.5 ms de CPU y 200.5 ms restantes por llamada. Etiquétala como **reconstrucción ilustrativa**, no como traza medida.

Si únicamente eliminaras los 0.03 s de CPU, manteniendo intacto el resto:

```text
speedup máximo ≈ 4.04/4.01 ≈ 1.0075×
```

Esa cuenta motiva cambiar cómo se organizan las esperas.

**3. Tabla de propiedades verificable mediante el Gantt**

La clasificación corresponde a **las ejecuciones dibujadas**; una biblioteca no garantiza por sí misma esos resultados.

| Ejecución ilustrada | Vidas solapadas | Ejecución durante espera ajena | Máximo de tareas ejecutando | Paralela | Interfaz asíncrona |
|---|:---:|:---:|:---:|:---:|---|
| Llamadas bloqueantes una por una | No | No | 1 | No | No en este ejemplo |
| Operaciones asíncronas atendidas una por una | No | No | 1 | No | Sí |
| CPU por turnos en una CPU, sin E/S | Sí | No | 1 | No | No se deduce del Gantt |
| Hilos con E/S bloqueante y ejecución Python alternada | Sí | Sí | 1 | No | No para las llamadas de cada hilo |
| Corrutinas con esperas solapadas en un loop | Sí | Sí | 1 | No | Sí |
| Trabajos exclusivamente de CPU simultáneos en dos CPU | Sí | No | 2 | Sí | No se deduce del Gantt |
| Trabajo mixto con ejecución simultánea en dos CPU | Sí | Sí | 2 | Sí | No se deduce del Gantt |

La matriz corregida queda:

| | No paralelo | Paralelo |
|---|---|---|
| No concurrente | Posible: vidas disjuntas | **Imposible al mismo nivel de tareas** |
| Concurrente | Posible: vidas solapadas, ejecución alternada | Posible: ejecución simultánea |

Para verificar una figura:

- Comprueba que cada tarea tiene exactamente un estado durante toda su vida activa.
- Cuenta únicamente los tramos `exec` para comprobar capacidad CPU.
- Cuenta también `wait`, `ready` y `blocked` al comprobar solapamiento de vidas.
- Rotula qué significa cada fila CPU y qué procesos o intérpretes contiene.
- Usa eventos de solicitud, suspensión y reanudación para explicar asincronía: el Gantt de ocupación por sí solo no distingue hilos de corrutinas.
- No deduzcas paralelismo únicamente de una reducción del tiempo total.

El cambio de matriz debe realizarse posteriormente en [tools/gen_computo.py](/home/uumami/itam/fdd_o26/tools/gen_computo.py:307), además del texto de la página 2; el SVG es generado.

**4. Mini-ejemplo completo: tres tareas**

Reutiliza los tiempos actuales del generador: cada tarea ejecuta **20 ms**, espera **200 ms** y ejecuta otros **20 ms**. Son tiempos didácticos, distintos de la medición de 20 llamadas.

Las tres llegan y se admiten en `t = 0`. Hay un hilo, `P = 1`, sin costos de coordinación ni bloqueos de sincronización.

| Tarea | `start` | `end` | `exec` | `wait` | `ready` |
|---|---:|---:|---|---|---|
| τ₁ | 0 | 240 | `[0,20) ∪ [220,240)` | `[20,220)` | ∅ |
| τ₂ | 0 | 260 | `[20,40) ∪ [240,260)` | `[40,240)` | `[0,20)` |
| τ₃ | 0 | 280 | `[40,60) ∪ [260,280)` | `[60,260)` | `[0,40)` |

Gantt por intervalos; las columnas no están a escala. `E`: ejecuta; `W`: espera; `R`: lista; `—`: terminada.

| | 0–20 | 20–40 | 40–60 | 60–220 | 220–240 | 240–260 | 260–280 |
|---|---|---|---|---|---|---|---|
| τ₁ | E | W | W | W | E | — | — |
| τ₂ | R | E | W | W | W | E | — |
| τ₃ | R | R | E | W | W | W | E |
| CPU | τ₁ | τ₂ | τ₃ | ociosa | τ₁ | τ₂ | τ₃ |

**Evaluación del framework:**

```text
Tareas = {τ₁, τ₂, τ₃}

L₁ = [0,240)
L₂ = [0,260)
L₃ = [0,280)

(e₁,e₂,e₃) = (40,40,40) ms
(w₁,w₂,w₃) = (200,200,200) ms
(r₁,r₂,r₃) = (0,20,40) ms
(b₁,b₂,b₃) = (0,0,0) ms

dur(L₁) = 40 + 200 + 0  = 240 ms
dur(L₂) = 40 + 200 + 20 = 260 ms
dur(L₃) = 40 + 200 + 40 = 280 ms
```

Como todas llegaron en cero, sus latencias son 240, 260 y 280 ms.

```text
ExecutingAt(30)  = {τ₂}
ExecutingAt(100) = ∅
ExecutingAt(230) = {τ₁}

maxₜ card(ExecutingAt(t)) = 1 ≤ P = 1
```

Hay concurrencia:

```text
L₁ ∩ L₂ = [0,240)
dur(L₁ ∩ L₂) = 240 ms > 0
```

Hay ejecución durante espera ajena:

```text
exec(τ₂) ∩ wait(τ₁) = [20,40)
dur(...) = 20 ms > 0
```

No hay paralelismo: todas las intersecciones de ejecución entre tareas distintas son vacías. En el supuesto de ejecución Python bajo un mismo GIL, también se cumple el límite de una tarea ejecutando Python.

La asincronía no se prueba con esas intersecciones: esta misma ocupación puede corresponder al ejemplo de hilos o al de corrutinas.

```text
D_concurrente = 280 ms
Trabajo CPU total = 3 × 40 = 120 ms
Ocio de la única CPU = 280 − 120 = 160 ms
Utilización = 120/280 ≈ 42.86 %
```

La suma de esperas es 600 ms, aunque el lote dura 280 ms. **Las esperas por tarea no se suman para obtener el ocio global cuando se solapan.**

En secuencia, admite cada tarea cuando termina la anterior:

```text
(start₁,start₂,start₃) = (0,240,480) ms
(end₁,end₂,end₃) = (240,480,720) ms

D_secuencial = 3 × (20 + 200 + 20) = 720 ms
speedup = 720/280 ≈ 2.57×
```

Ahora utiliza **tres procesos disponibles sobre dos CPU**, como el Gantt actual de procesos:

```text
τ₁: exec [0,20) ∪ [220,240); wait [20,220)
τ₂: exec [0,20) ∪ [220,240); wait [20,220)
τ₃: ready [0,20); exec [20,40) ∪ [240,260); wait [40,240)
```

Las tres siguen admitidas en cero.

```text
ExecutingAt(10) = {τ₁,τ₂}
card(ExecutingAt(10)) = 2 ≤ P = 2

exec(τ₁) ∩ exec(τ₂) = [0,20) ∪ [220,240)
dur(...) = 40 ms > 0

D = 260 ms
speedup respecto a la secuencia = 720/260 ≈ 2.77×
```

Superar 2× aquí no contradice Amdahl: la mejora también solapa esperas. Tampoco representa un pool de dos trabajadores: **tres procesos sobre dos CPU** es una configuración diferente.

La utilización conjunta es:

```text
120/(2 × 260) ≈ 23.08 %
```

Ambas CPU están ociosas durante `[40,220)`: 180 ms. Con varias CPU, `D − trabajo_CPU_total` deja de ser una fórmula del ocio.

Para evaluar también Amdahl sin atribuirle el solapamiento de E/S, añade una **variante exclusivamente de CPU**, explícitamente otra carga de tres tareas:

```text
τ₁: preparación serial de 40 ms.
τ₂ y τ₃: 100 ms cada una; ambas dependen de τ₁.
```

Una CPU tarda `40 + 100 + 100 = 240 ms`. Con dos CPU:

```text
τ₁: [0,40)
τ₂: [40,140), CPU 1
τ₃: [40,140), CPU 2

s = 40/240 = 1/6
D_ideal(2) = 240 × [1/6 + (5/6)/2] = 140 ms
speedup_ideal(2) = 240/140 = 12/7 ≈ 1.71×
```

Si el uso del pool añade 20 ms de gestión al lote:

```text
D_pool(2) = 140 + 20 = 160 ms
speedup_aplicación(2) = 240/160 = 1.50×
```

Si el pool de un trabajador también cuesta esos 20 ms:

```text
D_pool(1) = 260 ms
speedup_pool(2) = 260/160 = 1.625×
```

El límite algebraico `1/s = 6` requiere poder seguir subdividiendo los 200 ms repartibles. **Con τ₂ y τ₃ indivisibles, más de dos CPU no mejoran los 140 ms**. Esa distinción conecta Amdahl con el diseño real de tareas.

La notación Unicode y los bloques `text` bastan para este material. Confirmé el uso de `dollarmath` en el [renderer local](/home/uumami/itam/raya_lucaria/packages/static/src/raya_static/rendering.py:134); reservaría LaTeX para fracciones extensas o desarrollos posteriores. Las particiones, intervalos y Gantt resultan legibles sin él.