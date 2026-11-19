# Auditoría matemática y notación canónica — unidad «Cómputo y concurrencia»

Fuentes leídas: `fdd_p26/clase/16_computo/{01,02,03,05,06,07}.md`; `fdd_o26/course/10_apis/2_computo_y_concurrencia/{1,2,3,4}_*.md`.

## 0. ¿LaTeX o Unicode?

**LaTeX con `$…$` / `$$…$$` en el sitio.** El renderer ya carga `dollarmath_plugin` + `MathRenderer` (`raya_lucaria/packages/static/src/raya_static/rendering.py:11,134`) y la unidad 3 ya lo usa (`course/3_arquitectura_de_computadoras/3_paralelismo_performance_energia/0_index.md:137-143`). Los subíndices Unicode (τᵢ, θ₁) dentro de bloques de código dependen de la fuente y no se alinean. Reglas: nombres de función en `\mathrm{exec}`; **nunca un `$` suelto en la prosa** (dinero, `$GHUSER` fuera de un code span): abre una fórmula. CLAUDE.md no lo menciona; añadirlo junto a la regla del `@`. Este documento usa Unicode sólo por legibilidad.

## 1. Especificación canónica

Convención: todo intervalo es **semiabierto** `[a, b)`; `|X|` = duración total (medida) de un conjunto de instantes X. Un modelo se evalúa sobre un conjunto de tareas 𝒯 elegido (la **granularidad**).

| Símbolo | Definición | Nota |
|---|---|---|
| t | instante, t ≥ 0 | p26 llamaba T a este conjunto: se elimina |
| 𝒯 = {τ₁,…,τₙ} | tareas: unidades de trabajo con inicio y fin | n = número de tareas |
| start(τ), end(τ) | primer y último instante de τ | start ≤ end |
| vida(τ) = [start(τ), end(τ)) | ciclo de vida | d(τ) = end − start = **latencia** (reloj) |
| exec(τ) ⊆ vida(τ) | instantes en que una CPU corre instrucciones de τ | |
| wait(τ) ⊆ vida(τ) | τ **no podría avanzar aunque hubiera CPU libre**: red, disco, timer, lock, semáforo | |
| ready(τ) ⊆ vida(τ) | τ **podría avanzar pero no tiene CPU** (o GIL, o el loop está ocupado) | estado «lista» |
| **Partición** | exec, wait, ready disjuntos dos a dos y exec ∪ wait ∪ ready = vida | ⇒ d = \|exec\| + \|wait\| + \|ready\| |
| ρ(τ) = \|exec(τ)\| / d(τ) **medido en aislamiento** (ready = ∅) | fracción que ejecuta | CPU-bound: ρ ≈ 1; I/O-bound: ρ ≈ 0 |
| T = max end − min start | tiempo total (*makespan*), lo que da `perf_counter` | |
| C = Σᵢ \|exec(τᵢ)\| | tiempo de CPU; lo aproxima `process_time` | suma todos los hilos del proceso; **no** cuenta procesos hijos |
| ExecutingAt(t) = {τ : t ∈ exec(τ)} | tareas ejecutando en t | |
| P | **CPU lógicas** disponibles (`os.cpu_count()`, o `os.process_cpu_count()` ≥ 3.13 si hay afinidad/cgroup) | ∀t: \|ExecutingAt(t)\| ≤ P |
| U = C / (P·T) | utilización de la CPU | |
| N | trabajadores (hilos, procesos, permisos de semáforo) | no confundir con P |

Prueba operativa de wait contra ready: «si ahora mismo le doy una CPU libre, ¿avanza?» No → wait. Sí → ready.

**Propiedades de un Gantt (sobre 𝒯 fijo):**

| Propiedad | Definición |
|---|---|
| secuencial | ∀ i≠j: vida(τᵢ) ∩ vida(τⱼ) = ∅ |
| concurrente | ∃ i≠j: vida(τᵢ) ∩ vida(τⱼ) ≠ ∅ (= no secuencial) |
| solapa esperas | ∃ i≠j: wait(τᵢ) ∩ exec(τⱼ) ≠ ∅ |
| paralelo | ∃ t: \|ExecutingAt(t)\| ≥ 2 (requiere P ≥ 2) |

**Teorema.** Paralelo ⇒ concurrente, y solapa esperas ⇒ concurrente. Prueba: t ∈ exec(τᵢ) ∩ exec(τⱼ) (o wait(τᵢ) ∩ exec(τⱼ)) y ambos ⊆ vida, luego t ∈ vida(τᵢ) ∩ vida(τⱼ).

**Asíncrono (mecanismo, no celda del Gantt).** Sea hilo(τ) el hilo del SO que ejecuta τ.
- Llamada **síncrona**: mientras la operación está pendiente, hilo(τ) queda bloqueado; ningún otro τ' con el mismo hilo ejecuta.
- Llamada **asíncrona**: regresa al instante con un pendiente (`Task`); cuando τ necesita el resultado hace `await`, **se suspende y devuelve su hilo al planificador** (event loop).
- Consecuencia medible: ∃ i≠j, hilo(τᵢ) = hilo(τⱼ), wait(τᵢ) ∩ exec(τⱼ) ≠ ∅. **Solapar esperas dentro de un mismo hilo sólo es posible si quien espera cedió el control.** Con hilos el solapamiento ocurre entre hilos distintos y lo decide el SO.
- **Cooperativo:** en el loop, τ sale de exec sólo en un `await` o al terminar. **Preventivo** (hilos): el SO, y en CPython el GIL cada `sys.getswitchinterval()` = 5 ms, pueden sacarla. Por eso un cálculo sin `await` convierte en ready a todas las demás tareas del loop.

**GIL.** ∀ proceso p, ∀ t: a lo más una tarea de p ejecuta bytecode de Python. Las demás que quieran ejecutar Python están en **ready**, no en wait. Lo liberan: llamadas bloqueantes de E/S y `time.sleep`, extensiones en C que lo sueltan (NumPy, BLAS) y la compilación *free-threaded* (opcional y soportada desde 3.14, PEP 779, 2025).

**Rendimiento.** T(N) = tiempo con N trabajadores; T(1) = la **mejor versión secuencial**.
- Speedup S(N) = T(1) / T(N); eficiencia E(N) = S(N) / N.
- Fracción serial **f** (no «S»: choca con speedup).
- Amdahl: S(N) = 1 / (f + (1 − f)/N); techo 1/f. Para CPU-bound, además S ≤ min(N, P, n).
- Little: L = λ·W, con L = tareas en vuelo promedio, λ = rendimiento (tareas/s) y W = latencia media. Con todas las tareas en la ventana, L = Σ d(τᵢ) / T. Con un tope N de trabajos en vuelo: λ ≤ N / W. **Sí se usa**: dimensionar `Semaphore`, pools y colas (10.4) es aplicar Little.

## 2. Errores y ambigüedades de p26

| # | Dónde | Problema | Corrección |
|---|---|---|---|
| 1 | 03, concurrencia | Intervalos cerrados: con end(τ₁) = start(τ₂), M1 resulta «concurrente» (se tocan en un punto) | Semiabiertos `[start, end)` |
| 2 | 02/05 | T es a la vez el conjunto de instantes, T_total y T de Amdahl; S es la fracción serial y la letra de Speedup | t, T (makespan), f, S(N) |
| 3 | 02 | exec ∪ wait no cubre la vida; READY aparece en 03 en prosa, fuera del framework; T_total = Σ(end−start) supone que no hay huecos | Partición exec/wait/ready; secuencial ⇒ T ≥ Σ d |
| 4 | 01/02 | CPU-bound ≡ wait = ∅: un solo byte leído vuelve I/O-bound a la tarea. El escenario B (3 % de espera) sería I/O-bound por definición y p26 lo llama CPU-bound | Razón ρ medida en aislamiento |
| 5 | 03 | «Sistema asíncrono» ≡ exec(τⱼ) ∩ wait(τᵢ) ≠ ∅: los hilos también lo cumplen, y por el teorema implica concurrencia ⇒ **la celda M2 «async no concurrente» es vacía**. «Ortogonales» es falso | Llamarlo «solapa esperas»; asíncrono = ceder el hilo (§1) |
| 6 | 03, M2 | Los cuantificadores ∀ i,j: wait(τᵢ) ≠ ∅ exigen que toda tarea tenga E/S; la fórmula es M1 con esperas | M2 = código `async` cuyo Gantt es secuencial (await en serie) |
| 7 | 03, M3 | «P = 1 por construcción»: con 8 CPU los hilos con GIL tampoco son paralelos; el límite es el intérprete, no P | Restricción del GIL por proceso |
| 8 | 01 | El GIL «nunca se libera» en CPU-bound | Se entrega cada 5 ms; lo que nunca hay es simultaneidad |
| 9 | 01/02 | P = «cores físicos» | CPU lógicas que el SO concede (SMT, `--cpus` de la unidad 8) |
| 10 | 06 | `ThreadPoolExecutor` para I/O etiquetado M3, que exige wait = ∅; por las definiciones de p26 sería M4, que exige H = 1 | Desaparece al quitar M1–M6 |
| 11 | 05/07 | «Distribuido ⊇ Paralelo ⊇ Concurrente» va al revés del teorema que 05 demuestra | Paralelo ⊆ Concurrente; distribuido es otro eje (memoria y red), no un nivel |
| 12 | 01 | Mem(pᵢ) ∩ Mem(pⱼ) = ∅ como ley | «Por omisión»; existen `shared_memory` y `mmap` |
| 13 | 05, M5b | T ≈ T_bd + T_inferencia sin importar N | Vale si N ≤ P; en general T_bd + ⌈N/P⌉·T_inf |
| 14 | 05/07 | S ≈ 0.05 afirmado sin medición; «distribuido escala sin Amdahl» | f se estima de mediciones; Amdahl vale también entre nodos con carga fija |

**Nuestras páginas:**
- p1:31 dice que el reloj es «la suma de los dos tramos», y p1:57 introduce un tercero. Debe decir «de los tres; aislada, ready = 0».
- p2:170 da como ideal 2.34/4 = 0.58 s, que supone f = 0. Usar el ajuste de §4.
- p3:151 habla de «tandas». El semáforo es una ventana deslizante; usar Little.
- p4:200 usa `S` como fracción serial: cambiar a `f`.
- p4:244 dice que los costos de arranque son algo «que la fórmula no cuenta». Un costo fijo **entra** en f; lo que la fórmula no cuenta es el costo que crece con N.
- p2:183/194 (la matriz) ver §3.
- La unidad 3 usa P para rendimiento (roofline). Aclarar en el glosario que aquí P son CPU lógicas.

## 3. La matriz 2×2

Con 𝒯 fija, la celda «paralelo y no concurrente» es **vacía por teorema**. NumPy no la llena:
- Una ufunc elemento a elemento (`arr * arr`, `np.sum`) corre en **un** núcleo. SIMD es paralelismo de **datos dentro de una instrucción**, por debajo del modelo de tareas: |ExecutingAt| = 1.
- BLAS (`@`) sí reparte en hilos, pero entonces sus subtareas internas son paralelas **y** concurrentes en esa granularidad.
- Se puede comprobar: CPU/reloj ≈ 1 con `arr*arr`, y > 1 con una matmul grande.

**Redacción final** (reemplaza la matriz por tres filas y una nota):

> Concurrente y paralelo no son dos ejes independientes: **todo lo paralelo es concurrente** (si dos tareas ejecutan en el mismo instante, sus vidas se solapan). Quedan tres casos: secuencial; concurrente sin paralelismo (hilos con GIL, `asyncio`); concurrente y paralelo (procesos). «Paralelo sin concurrente» no existe si cuentas las mismas tareas. Lo que a veces se nombra así es un cambio de escala: *una* operación de tu programa (una tarea, ni concurrente ni paralela a tu nivel) que por dentro reparte el trabajo. Una multiplicación de matrices con BLAS lo reparte en hilos, que son paralelos y concurrentes a su nivel. SIMD es otra cosa: una sola instrucción opera sobre varios datos en un solo núcleo; es paralelismo de datos, no de tareas. Asíncrono tampoco es una fila: es *cómo* cede el control quien espera.

## 4. Orden de introducción con un ejemplo único

El ejemplo coincide con las figuras actuales `cmp-gantt-asyncio` (280 ms) y `cmp-gantt-await-en-serie` (720 ms). Son 3 tareas iguales: exec 20 ms, wait 200 ms, exec 20 ms (d = 240, \|exec\| = 40).

| Paso | Símbolo | Evaluación |
|---|---|---|
| 1 | τ, vida, start, end, d | τ₁ secuencial: vida = [0, 240), d = 240 ms |
| 2 | exec, wait, partición | exec(τ₁) = [0,20) ∪ [220,240); wait = [20,220); 40 + 200 + 0 = 240 |
| 3 | reloj vs CPU, ρ | ρ = 40/240 = 16.7 % → I/O-bound. **Real (1.2):** C = 0.03 s, T = 4.04 s, ρ = 0.7 %, espera 99.3 % |
| 4 | secuencial, T | vidas [0,240), [240,480), [480,720): disjuntas (semiabiertas). T = 720 = Σd |
| 5 | ExecutingAt, P, U | máx \|ExecutingAt\| = 1; C = 120; U(P=1) = 120/720 = 16.7 % |
| 6 | concurrente | gather: vidas [0,240), [20,260), [40,280) se solapan; T = 280 |
| 7 | solapa esperas, asíncrono | wait(τ₁) ∩ exec(τ₂) = [20,40) con el mismo hilo ⇒ τ₁ cedió el control. U = 120/280 = 42.9 %; S = 720/280 = 2.57; cota T ≥ max d = 240 |
| 8 | ready | `cmp-bloqueo-del-loop`: τ₃ calcula [40, 2040) sin `await`; ready(τ₁) = [220, 2040). d(τ₁) = 40 + 200 + 1820 = 2060; T = 2080 |
| 9 | GIL | hilos: el mismo Gantt que el paso 7; un cálculo en 4 hilos: \|ExecutingAt\| ≤ 1, el resto ready |
| 10 | paralelo + teorema | 3 tareas CPU de 400 ms, N = 2 procesos: [0,400) en CPU0 y en CPU1, la tercera [400,800). T = 800, S = 1.5, E = 0.75; aquí la cota es ⌈n/N⌉, no Amdahl |
| 11 | S, E (real, celda 2.3, P = 8, n = 4) | S(2) = 2.34/1.45 = 1.61, E = 0.81; S(4) = 2.34/1.00 = 2.34, E = 0.59 |
| 12 | Amdahl | Ajuste T(N) = a + b/N: b = 2(2.34 − 1.45) = 1.78, a = 0.56 → predice T(4) = 1.005 (medido 1.00). f = 0.56/2.34 ≈ **0.24**; Amdahl da S(2) = 1.61 y S(4) = 2.33; techo ≈ 4.2, y con n = 4 nunca más de 4 |
| 13 | Little | Serie: λ = 20/4.04 = 4.95/s, W = 0.202 ⇒ L = 1.0. Hilos-32: λ = 20/0.23 = 87/s ⇒ L = 17.6 = S (con tareas iguales, speedup = concurrencia media). Tope 32, W = 0.2 ⇒ λ ≤ 160/s ⇒ 500 llamadas ≥ 3.13 s (medido 3.32 con hilos y 3.41 con asyncio); 100 llamadas ≥ 0.63, o ⌈100/32⌉·0.2 = 0.8 con duraciones iguales (medido 0.82 y 0.92) |

Advertencias:
- El ajuste de Amdahl tiene 3 puntos y 2 parámetros, así que sólo comprueba con un grado de libertad, y es una sola corrida. Que los 0.56 s sean arranque de procesos e IPC es una hipótesis.
- Medir C con `process_time` en procesos da ≈ 0, porque no cuenta a los hijos. Para ver paralelismo como CPU/reloj > 1 sirve con hilos o NumPy/BLAS; con procesos hay que usar `os.times()` (campos children).

Arquitectura en cada paso: ρ decide la estrategia (paso 3); el paso 8 es la regla «no calcules en el loop», el patrón de descargar el trabajo a otro proceso (*offload*); el paso 12 da el número de workers; el paso 13 dimensiona semáforos, pools y colas.

## 5. Leer cada propiedad en un Gantt

| Propiedad | Qué miras | Se cumple si |
|---|---|---|
| ρ / tipo de tarea | largo de las barras exec contra la vida, con la tarea sola | exec ≈ vida (CPU) o exec ≪ vida (I/O) |
| secuencial | proyecta cada vida sobre el eje | ningún par de vidas se traslapa (tocarse en un borde no cuenta) |
| concurrente | trazo vertical en algún t | corta ≥ 2 vidas |
| solapa esperas | trazo vertical | corta una barra wait de τᵢ y una exec de τⱼ |
| asíncrono | lo anterior + la fila de hilo | τᵢ y τⱼ están en el **mismo hilo** |
| paralelo | filas de CPU | dos filas de CPU ocupadas en el mismo t (≥ 2 barras exec en una vertical) |
| GIL | barras exec de hilos de un proceso | nunca se apilan; los huecos que dejan son ready |
| ready | tramo rayado entre el fin de un wait y la siguiente exec | aparece cuando \|tareas que quieren CPU\| > recursos (P, el GIL o el loop) |
| U | fila de CPU | área ocupada / (P·T) |
| Little L | trazo vertical | número promedio de vidas que corta |

Convención gráfica para `tools/gen_computo.py`: exec relleno, wait contorno, **ready rayado**, intervalos semiabiertos (la barra siguiente empieza en el mismo x), una fila por CPU y, cuando hay `asyncio`, una etiqueta con el hilo.
