---
id: vectorizar
title: "Vectorizar: sacar el bucle del intérprete"
nav_title: "Vectorizar"
summary: "Hilos y asyncio reparten esperas, los procesos reparten cálculo; antes de repartir, conviene empujar el cálculo a un motor que recorra el arreglo en C. Definición, costo por elemento, límites, interacción con el GIL y los hilos de BLAS, y el patrón de arquitectura."
status: ready
estimated_time: 8m
tags: [vectorizacion, numpy, simd, cpu-bound, arquitectura]
prerequisites: [calcular-en-paralelo]
---

# Vectorizar: sacar el bucle del intérprete

**Página 7 de 8 · Cómputo y concurrencia** · Pregunta: si el trabajo es calcular la misma operación sobre millones de números, ¿hay que repartirlo entre procesos o hay algo que probar antes? · Meta: definir vectorizar, calcular de dónde viene la ganancia, saber cuándo no sirve y dónde se coloca en un servicio.

| Término | Definición de una línea | Símbolo |
|---|---|---|
| vectorización | Aplicar una operación a un arreglo completo en una llamada; el bucle corre en C | $c_{\text{py}}$, $c_{\text{C}}$ |
| arreglo contiguo | Valores del mismo `dtype` guardados uno junto a otro en memoria | `dtype`, `nbytes` |
| SIMD | Una instrucción de CPU opera sobre varios valores a la vez | factor secundario |
| costo fijo | Lo que cuesta llamar a la operación aunque el arreglo sea pequeño | $c_0$ |

## En corto

- **Vectorizar mueve el bucle del intérprete a un bucle en C.** No reparte entre CPU: es otra implementación en el mismo núcleo, no un $S(N)$ de [[notacion-computo]].
- **La ganancia combina** sacar el despacho por elemento, tipos homogéneos y acceso contiguo a memoria; SIMD es un factor secundario y la medición de esta página no lo separa.
- **Primero el motor, luego los procesos.** Si el cálculo cabe en NumPy, Polars o SQL, empújalo ahí antes de repartir; si no cabe (ramas por elemento, objetos), entonces procesos ([[calcular-en-paralelo]]).

## Vectorización

::: definition {#cmp-def-vectorizacion title="Vectorización"}
**Vectorizar** es expresar un cálculo como una operación sobre un arreglo completo (`arr * arr`, `np.sum(arr)`) en lugar de un bucle de Python que toca un elemento por vez. El recorrido lo hace código compilado sobre los valores crudos, sin pasar por el intérprete en cada elemento.
:::

**Otro ángulo.** La figura compara los dos recorridos de la misma suma de cuadrados.

::: figure {#cmp-vectorizar title="Un bucle elemento a elemento contra una operación sobre el arreglo completo"}
![Dos carriles comparados. Arriba, un bucle de Python que toma un elemento por vez de una lista de referencias, revisa su tipo, multiplica y suma, y repite cinco millones de veces dentro del intérprete. Abajo, un arreglo contiguo de float64 que una sola llamada recorre en un bucle de C, procesando varios valores por instrucción en carriles SIMD.](_assets/cmp-vectorizar.svg)
:::

::: definition {#cmp-def-costo-elemento title="Costo por elemento"}
**En palabras.** El costo por elemento es lo que cuesta procesar un elemento más del arreglo; el costo fijo es lo que cuesta llamar a la operación aunque el arreglo sea pequeño. Vectorizar cambia el costo por elemento, no el número de trabajadores.

**Formalmente.** Sobre $N$ elementos, $T_{\text{bucle}}\approx N\cdot c_{\text{py}}$ y $T_{\text{vec}}\approx c_0+N\cdot c_{\text{C}}$; la ganancia $T_{\text{bucle}}/T_{\text{vec}}$ tiende a $c_{\text{py}}/c_{\text{C}}$ cuando $N\to\infty$. Es una comparación entre implementaciones, no un $S(N)$. Modelo completo en [[notacion-computo]].
:::

**Matemática.** El tiempo de cada versión sobre $N$ elementos:

$$T_{\text{bucle}}\approx N\cdot c_{\text{py}}\qquad T_{\text{vec}}\approx c_0+N\cdot c_{\text{C}}$$

$$\text{ganancia}=\frac{T_{\text{bucle}}}{T_{\text{vec}}}\xrightarrow[N\to\infty]{}\frac{c_{\text{py}}}{c_{\text{C}}}$$

- **Con $N$ grande** la ganancia es la razón de costos por elemento.
- **Con $N$ pequeño** manda $c_0$: si $N\,c_{\text{py}}<c_0$, vectorizar pierde.
- Es un modelo de dos parámetros: dice qué cambia al variar $N$, no predice la ganancia de otra máquina.

**Ejemplo.** Suma de cuadrados de $N=5\,000\,000$ números `float64`, medida en esta máquina (una corrida, referencia): bucle 0.141 s, NumPy 0.0091 s, ganancia 16×.

| Versión | $T$ | Costo por elemento ($T/N$) |
|---|---:|---:|
| bucle de Python | 0.141 s | $c_{\text{py}}\approx 28$ ns |
| NumPy (`arr * arr` y `np.sum`) | 0.0091 s | $c_{\text{C}}\approx 1.8$ ns |

- Los costos por elemento son la división de las medidas de referencia (0.141 s y 0.0091 s) entre $5\times10^{6}$; incluyen las dos pasadas de NumPy, y $c_0$ aquí es despreciable.
- **No se atribuye a SIMD.** La ganancia combina bucle fuera del intérprete, tipos homogéneos y memoria contigua. Para separar SIMD harían falta mediciones que cambien una sola cosa a la vez.
- Es una comparación entre dos implementaciones en un núcleo: no demuestra paralelismo.

**Arquitectura.** Vectorizar en el borde: al recibir datos de N respuestas, convertirlos **una vez** a un arreglo o `DataFrame` y calcular con operaciones de columna.

| Aspecto | Detalle |
|---|---|
| **Qué es** | N registros JSON entran, se convierten a un arreglo, una operación vectorizada produce el resultado |
| **Cuándo sí** | Transformación numérica sobre muchos registros con la misma operación |
| **Cuándo no** | Lógica por registro con ramas y llamadas externas (eso es espera, no cálculo) |
| **Qué cuesta** | Convertir una vez a arreglo (la conversión no es gratis); fijar el `dtype` |
| **Riesgo** | `apply` o `iterrows` de pandas: un bucle de Python con otro nombre |
| **Sistema real** | NumPy, pandas, Polars: la API se parece a un bucle, la ejecución no |

## Arreglo contiguo, `dtype` y vistas

::: definition {#cmp-def-arreglo-contiguo title="Arreglo contiguo y dtype"}
Una **lista** de Python guarda referencias a objetos: cada `float` es un objeto aparte con cabecera, y para operar el intérprete sigue la referencia, revisa el tipo y despacha. El **`dtype`** fija cómo se representa cada elemento (`float64`: 8 bytes de punto flotante; `int64`: 8 bytes de entero con signo). Un **arreglo** de NumPy guarda los valores crudos, todos del mismo `dtype`, en un bloque contiguo. Una **vista** (`a[::2]`) comparte esa memoria y puede no ser contigua; sigue admitiendo operaciones vectorizadas.
:::

**Otro ángulo.**

| | `list` de `float` | `np.ndarray` `float64` |
|---|---|---|
| Qué guarda | referencias a objetos | valores crudos |
| Tipo por elemento | se revisa en cada operación | uno solo, conocido de antemano |
| Memoria | objetos dispersos | un bloque contiguo |
| Bytes por elemento | cabecera de objeto más la referencia | 8 (`itemsize`) |

**Matemática.** El tamaño es determinista: $\text{nbytes}=N\cdot\text{itemsize}=5\,000\,000\cdot 8=40\,000\,000$ bytes (40 MB). Crear el arreglo cuesta tiempo aparte, y por eso **no** entra dentro de la comparación de arriba: se mide por separado.

**Ejemplo.** Cada operación `arr * arr` **crea otro arreglo** de 40 MB. Una expresión encadenada como `((a * a) + b) * c` crea temporales intermedios: la memoria máxima sube aunque el resultado sea pequeño.

**Arquitectura.** Copias y temporales de memoria.

| Aspecto | Detalle |
|---|---|
| **Qué es** | Cada operación vectorizada reserva un arreglo nuevo del tamaño de la entrada |
| **Cuándo sí** | Datos que caben en memoria varias veces |
| **Cuándo no** | Datos cercanos al tamaño de la RAM: procesar por bloques, o una herramienta lazy como Polars (9.3) |
| **Qué cuesta** | Memoria pico $\approx$ entrada más temporales; copiar entre procesos la multiplica |
| **Sistema real** | Polars lazy; consultas SQL que no materializan resultados intermedios |

## `float64` o `int64`, y el desborde

::: definition {#cmp-def-desborde title="Desborde de entero con tamaño fijo"}
Un `np.int64` tiene 64 bits con signo (máximo $2^{63}-1=9\,223\,372\,036\,854\,775\,807$) y **no crece**: si el resultado no cabe, da la vuelta sin avisar. Un `int` de Python no tiene tope.
:::

**Matemática.** La suma de cuadrados exacta es $\sum_{i=0}^{N-1} i^2=\frac{(N-1)\,N\,(2N-1)}{6}$. Con $N=5\times10^{6}$ da $\approx4.17\times10^{19}$, mayor que $9.2\times10^{18}$: en `int64` no cabe. En `float64` cabe la magnitud, a cambio de perder dígitos finales.

**Ejemplo.** La celda 7.3 compara tres resultados: exacto con enteros de Python, `int64` (otro número, sin error) y `float64` (magnitud correcta, últimos dígitos inexactos).

## Cuándo vectorizar no sirve

| Caso | Datos | Dependencias | Memoria | Estrategia | Riesgo |
|---|---|---|---|---|---|
| Lógica distinta por elemento | ramas por elemento | cada uno decide su camino | sin problema | máscaras (`np.where`) si la lógica lo permite; si no, procesos | reescribir y perder claridad |
| Objetos de Python (cadenas, diccionarios) | arreglo de referencias, sin tipos crudos | ninguna | referencias otra vez | convertir a `dtype` numérico, o procesos | cero ganancia |
| Cada elemento depende del anterior | numéricos | serie dependiente | sin problema | reformular (`cumsum`) o aceptar el bucle | resultado erróneo si se fuerza |
| Pocos elementos | cualquiera | ninguna | sin problema | bucle normal | $c_0$ pesa más que el bucle |
| Datos que no caben en memoria | numéricos | ninguna | `arr * arr` duplica | bloques o Polars lazy | `MemoryError` |

## NumPy, el GIL y los hilos internos

::: definition {#cmp-def-hilos-internos title="Hilos internos de una operación"}
**NumPy libera el GIL** durante las operaciones grandes sobre arreglos: mientras C recorre los datos, otro hilo de Python puede correr. Algunas operaciones (multiplicación de matrices con BLAS) además **crean hilos propios**: por dentro son paralelas y concurrentes a su escala, aunque para tu programa sean una sola llamada.
:::

**Otro ángulo.** Tres niveles distintos:

| Nivel | Qué ocurre | Efecto en $\operatorname{card}(\operatorname{ExecutingAt}(t))$ |
|---|---|---|
| SIMD | una instrucción opera sobre varios datos en un núcleo | sigue en 1: paralelismo de datos, no de tareas |
| `arr * arr` | una ufunc corre en un núcleo, sin GIL | 1 |
| matmul con BLAS | hilos propios de BLAS | puede ser mayor que 1 |

**Matemática.** Si lanzas $W$ procesos de cálculo y cada uno usa $h$ hilos de BLAS, el sistema pide $W\cdot h$ hilos de cálculo sobre $P$ CPU lógicas. Con $W\cdot h>P$ hay sobreasignación: los hilos compiten y el tiempo puede empeorar. Con $P=8$ (esta máquina): $W=4$ y $h=8$ piden $32$ hilos.

**Ejemplo.** Con 4 procesos de [[calcular-en-paralelo]], cada uno llamando a una matmul grande: si cada proceso abre 8 hilos de BLAS, son 32 hilos sobre 8 CPU lógicas. Se controla fijando los hilos por proceso (variables como `OMP_NUM_THREADS` o `OPENBLAS_NUM_THREADS`) para que $W\cdot h\le P$.

**Arquitectura.** Empujar el cálculo al motor antes de repartir con procesos.

| Aspecto | Petición a operación vectorizada | Petición a cola o pool de procesos |
|---|---|---|
| Qué es | el manejador llama a una función NumPy, Polars o SQL | el manejador encola el trabajo y un worker lo calcula |
| Cuándo sí | el cálculo es la misma operación sobre un arreglo | lógica por elemento, objetos, o ya vectorizado y sigue dominando el cálculo |
| Cuándo no | datos casi del tamaño de la RAM; hilos de BLAS sin controlar | cálculo de microsegundos: serializar cuesta más |
| Qué cuesta | memoria de temporales; ocupa el hilo del loop mientras corre | serializar y copiar datos entre procesos; arranque del pool |
| Sistema real | NumPy y Polars dentro de un servicio; SQL en la base | Celery con Redis o RabbitMQ; `ProcessPoolExecutor` |

Una operación vectorizada larga **sigue ocupando el hilo del event loop** si corre en él: desde [[asincrono-y-el-event-loop]], se manda a un executor.

## La decisión hasta aquí

| Página | Pregunta | Regla |
|---|---|---|
| 1 | ¿dónde pasa el tiempo? | medir $\operatorname{exec}$ contra $\operatorname{wait}$ |
| 2 a 5 | ¿es espera? | solapar esperas: hilos o `asyncio`, con tope y pool |
| 6 | ¿es cálculo en Python? | procesos; el techo lo da $f$ (Amdahl) |
| **7** | **¿es la misma operación sobre un arreglo?** | **vectorizar primero; luego, si sigue dominando, procesos con hilos de BLAS controlados** |

## Código

Cada celda hace una pregunta y la contesta con una medición.

**Haz (celda 7.1):** crea un arreglo de cinco millones de `float64`, mira qué ocupa y mide aparte lo que cuesta crearlo.

```python
import time
import numpy as np

n = 5_000_000
t0 = time.perf_counter()
a = np.arange(n, dtype=np.float64)   # crea los valores ya como decimales de 64 bits
crear_s = time.perf_counter() - t0   # la creación se mide aparte

print("dtype:", a.dtype, "| bytes por elemento:", a.itemsize)
print("bytes totales:", a.nbytes)
print("contiguo:", a.flags["C_CONTIGUOUS"])
print(f"crear el arreglo: {crear_s:.4f} s")
```

**Python que quizá no has visto**

| Qué | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `dtype=np.float64` | fija el tipo de todos los elementos | sin tipo único no hay valores crudos |
| `perf_counter()` | reloj monotónico de alta resolución | mide sin saltos del reloj del sistema |
| `a.flags["C_CONTIGUOUS"]` | pregunta si el bloque es contiguo | verifica la propiedad que da el acceso en orden |

**Qué pasó.** $\text{nbytes}=5\,000\,000\cdot8=40\,000\,000$; el tiempo de crear es de esta ejecución.

**Deberías ver:**

```text
dtype: float64 | bytes por elemento: 8
bytes totales: 40000000
contiguo: True
crear el arreglo: 0.0065 s
```

**Haz (celda 7.2):** mide el bucle de Python sobre una lista y la operación vectorizada sobre el arreglo, y verifica que coinciden.

```python
import time
import numpy as np

a = np.arange(5_000_000, dtype=np.float64)
lista = a.tolist()  # la conversión queda fuera de la medición

def bucle(xs):
    total = 0.0
    for x in xs:
        total += x * x
    return total

def vec(arr):
    return float(np.sum(arr * arr))

vec(a)  # calentamiento: la primera corrida se descarta
t0 = time.perf_counter(); r1 = bucle(lista); bucle_s = time.perf_counter() - t0
t0 = time.perf_counter(); r2 = vec(a); numpy_s = time.perf_counter() - t0
print(f"bucle {bucle_s:.3f} s | NumPy {numpy_s:.4f} s | {bucle_s/numpy_s:.0f}x")
print("coinciden:", np.isclose(r1, r2, rtol=1e-9))
```

**Python que quizá no has visto**

| Qué | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `a.tolist()` | convierte el arreglo en lista de `float` | el bucle necesita su entrada; se prepara fuera del cronómetro |
| `np.isclose(..., rtol=1e-9)` | compara con tolerancia relativa | las dos versiones suman en distinto orden y los decimales no son asociativos |
| varias sentencias con `;` | dos sentencias en una línea | sólo para que cada cronómetro quepa en una línea |

**Qué pasó.**

| Medición | Valor |
|---|---:|
| bucle de Python | 0.141 s |
| NumPy | 0.0091 s |
| ganancia | 16× |

Los tiempos son de la máquina del profesor; los tuyos cambian, y la proporción también.

**Deberías ver:**

```text
bucle 0.141 s | NumPy 0.0091 s | 16x
coinciden: True
```

**Haz (celda 7.3):** suma los mismos cuadrados con `int64` y compara con el valor exacto.

```python
import numpy as np

n = 5_000_000
enteros = np.arange(n, dtype=np.int64)
con_int64 = int(np.sum(enteros * enteros))           # se desborda sin avisar
exacto = (n - 1) * n * (2 * n - 1) // 6              # fórmula cerrada, enteros de Python
con_float64 = float(np.sum(np.arange(n, dtype=np.float64) ** 2))

print("máximo de int64:", np.iinfo(np.int64).max)
print("exacto (Python):", exacto)
print("int64 (NumPy):  ", con_int64)
print("float64 (NumPy):", f"{con_float64:.6e}")
```

**Python que quizá no has visto**

| Qué | Qué hace | Por qué hace falta aquí |
|---|---|---|
| `//` | división entera | la fórmula cerrada debe dar un entero exacto |
| `np.iinfo(np.int64).max` | mayor valor que cabe en el tipo | muestra el tope que se rebasa |
| `int` de Python | entero sin tope | sirve de referencia exacta |

**Qué pasó.** El valor exacto ($\approx4.17\times10^{19}$) supera el máximo de `int64` ($9.2\times10^{18}$): `int64` devuelve otro número y no lanza error; `float64` conserva la magnitud y pierde los últimos dígitos.

**Deberías ver:**

```text
máximo de int64: 9223372036854775807
exacto (Python): 41666654166667500000
int64 (NumPy):   4773166019248396768
float64 (NumPy): 4.166665e+19
```

La versión larga y paso a paso está en el notebook, tema 7.

## Al diseñar / al revisar código de IA, busca…

- **Un `for` de Python sobre un arreglo o una columna** para sumar, multiplicar o filtrar: casi siempre es una operación vectorizable. Un `apply` o `iterrows` es el mismo bucle.
- **Hilos para acelerar un cálculo numérico:** con bucles de Python, el GIL lo impide ([[el-gil]]). Muchas operaciones de NumPy liberan el GIL y BLAS puede usar hilos internos: controla los hilos por proceso para que $W\cdot h\le P$.
- **Procesos antes de preguntarse si el cálculo se puede vectorizar:** repartir un bucle lento cuesta serialización; vectorizar primero cambia $T(1)$.
- **Acumuladores en `int64` o `int32` sobre sumas grandes:** desbordan sin aviso. Revisa el `dtype`.
- **Una medición que incluye crear el arreglo o convertir la lista, o que no descarta la primera corrida:** infla o desinfla la ganancia.
- **Una operación vectorizada larga dentro de un manejador `async`:** ocupa el hilo del loop mientras corre.

Sigue con [[arquitectura-y-estrategia]].
