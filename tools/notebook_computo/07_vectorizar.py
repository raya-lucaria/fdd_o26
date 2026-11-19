# %% [markdown]
# # Tema 7 · Vectorizar: empujar el cálculo al motor
#
# **Pregunta.** Antes de repartir un cálculo entre procesos, ¿se puede hacer que cada operación cueste menos?
#
# Un bucle de Python hace, por cada elemento, trabajo de intérprete: busca el objeto, comprueba su tipo, llama a
# `__mul__`, crea otro objeto `float`. **Vectorizar** es entregar el arreglo completo a una función compilada que
# hace esa misma cuenta sobre valores crudos y contiguos en memoria. El cálculo sigue en **una** CPU, con **un**
# proceso: no hay paralelismo ni concurrencia, y aun así es 10 a 100 veces más rápido. Por eso es lo primero que
# se prueba, antes de los procesos del tema 6.
#
# Lo que este tema agrega a la página 7:
#
# | bloque | qué enseña |
# |---|---|
# | 7.1 y ampliación | qué ocupa un arreglo y por qué un tipo único lo hace barato |
# | 7.2 y ampliación | cuánto gana NumPy según el tamaño, y qué cuesta un temporal |
# | 7.3 y ampliación | `int64` se desborda **sin avisar**; qué tipo usar |
# | vistas | qué copia NumPy y qué comparte: cortes, vistas no contiguas, transpuestas |
#
# Todo el tema es local: no usa el servidor. Cargas: arreglos de hasta 5 millones de elementos (40 MB).

# %%
# Preparación del tema.
import sys, time, tracemalloc
import numpy as np

CIFRAS = {}
print("numpy", np.__version__)

# %% [markdown]
# ## 7.1 · Un arreglo de `float64`
#
# Un `ndarray` guarda **un tipo único** (`dtype`) y los valores crudos uno detrás de otro. Por eso su tamaño es
# `nbytes = n · itemsize`: 5 000 000 × 8 = 40 000 000 bytes. Una lista de Python con 5 millones de `float` guarda
# **punteros** (8 bytes cada uno) a objetos `float` sueltos (24 bytes cada uno), repartidos por toda la memoria.
#
# **Qué esperar.** `float64`, 8 bytes por elemento, 40 000 000 bytes, contiguo (`True`), y el tiempo de crear el
# arreglo (unas pocas decenas de milisegundos).

# %%
# celda 7.1
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

# %% [markdown]
# ### 7.1 ampliada: el mismo arreglo en cuatro tipos, y contra una lista
#
# El tipo decide cuánto ocupa y cuánto cabe sin perder precisión. Se compara el mismo `arange` en `int32`,
# `int64`, `float32` y `float64`, y se mide qué ocupa la lista equivalente: `sys.getsizeof(lista)` cuenta los
# punteros, y cada `float` cuenta 24 bytes aparte (`sys.getsizeof(1.0)`).
#
# **Qué esperar.** `int32`/`float32` ocupan la mitad que los de 64 bits. La lista ocupa **unas cuatro veces**
# lo que ocupa el arreglo de `float64`: 8 bytes de puntero + 24 de objeto por elemento contra 8.

# %%
# Mismo arreglo en cuatro tipos, y la lista equivalente.
filas = []
for tipo in (np.int32, np.int64, np.float32, np.float64):
    arr = np.arange(n, dtype=tipo)                                 # NUEVO: variar el dtype
    filas.append((np.dtype(tipo).name, arr.itemsize, arr.nbytes))
print(f"{'dtype':<10}{'bytes/elem':>12}{'MB':>10}")
for nombre, ib, nb in filas:
    print(f"{nombre:<10}{ib:>12}{nb / 1e6:>10.1f}")

lista = a.tolist()                                                 # NUEVO: la lista equivalente
bytes_lista = sys.getsizeof(lista) + len(lista) * sys.getsizeof(1.0)
print(f"{'lista':<10}{'8 + 24':>12}{bytes_lista / 1e6:>10.1f}   (punteros + objetos float)")
print(f"la lista ocupa {bytes_lista / a.nbytes:.1f} veces lo que el arreglo float64")
CIFRAS.update(mb_float64=a.nbytes / 1e6, mb_lista=bytes_lista / 1e6)
assert a.nbytes == n * 8 == 40_000_000 and a.flags["C_CONTIGUOUS"]
assert bytes_lista > 3 * a.nbytes

# %% [markdown]
# ## 7.2 · El bucle contra la operación vectorizada
#
# Las dos funciones calculan $\sum x_i^2$. `bucle` recorre la lista elemento por elemento; `vec` eleva al
# cuadrado todo el arreglo y lo suma, en dos llamadas a código compilado. Las dos suman en **distinto orden**,
# y los decimales no son asociativos, por eso se comparan con `np.isclose` y tolerancia relativa, no con `==`.
#
# Detalles de medición: `tolist()` queda **fuera** del cronómetro (el bucle necesita su entrada) y `vec(a)` se corre
# una vez antes de medir, porque la primera llamada paga costos de arranque.
#
# **Qué esperar.** El bucle tarda decenas o cientos de milisegundos; NumPy, unos cuantos milisegundos. La
# ganancia en esta máquina fue de ≈ 16× en la corrida de referencia; la tuya cambia.

# %%
# celda 7.2
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

# %% [markdown]
# ### 7.2 ampliada: la ganancia según el tamaño, y lo que cuesta un temporal
#
# **1. Barrido de tamaños.** Se repite la medición con $n=10^5, 10^6, 5\times10^6$, tomando el **mejor de 3** para
# NumPy (reduce ruido; el bucle es lo bastante lento como para medirse una vez). La ganancia **baja** al crecer $n$: con
# pocos elementos todo cabe en la caché de la CPU; con millones, el arreglo la rebasa y la memoria pasa a ser el límite (explicación probable; esta celda no la mide).
#
# **2. El temporal.** `arr * arr` crea un arreglo nuevo de 40 MB antes de que `np.sum` lo recorra: la expresión
# necesita memoria extra del tamaño de los datos. `np.dot(arr, arr)` calcula la misma suma de cuadrados sin
# temporal. Se mide el **pico de memoria** de cada forma con `tracemalloc` (NumPy informa sus asignaciones).
#
# **Qué esperar.** La ganancia va de ≈ 30× con $10^5$ elementos a ≈ 15× con $5\times10^6$ (en cualquier caso, muy por encima de 1). Pico de `np.sum(arr * arr)` ≈ 40 MB; pico de
# `np.dot` ≈ 0 MB.

# %%
# Barrido de tamaños (ganancia) y pico de memoria con y sin temporal.
def mejor_de(f, veces=3):
    mejor = float("inf")
    for _ in range(veces):
        t0 = time.perf_counter(); f(); mejor = min(mejor, time.perf_counter() - t0)
    return mejor

print(f"{'n':>10}{'bucle (s)':>11}{'NumPy (s)':>11}{'ganancia':>10}")
ganancias = []
for m in (100_000, 1_000_000, 5_000_000):                           # NUEVO: tres tamaños
    arr_m = np.arange(m, dtype=np.float64)
    lista_m = arr_m.tolist()
    t_bucle = mejor_de(lambda: bucle(lista_m), veces=1)
    t_vec = mejor_de(lambda: vec(arr_m))
    ganancias.append(t_bucle / t_vec)
    print(f"{m:>10,}{t_bucle:>11.4f}{t_vec:>11.5f}{t_bucle / t_vec:>9.0f}x")

def pico(f):
    tracemalloc.start()
    f()
    _, pico_bytes = tracemalloc.get_traced_memory()                 # NUEVO: el máximo de memoria asignada
    tracemalloc.stop()
    return pico_bytes

pico_temporal = pico(lambda: np.sum(a * a))                         # a*a crea un arreglo de 40 MB
pico_dot = pico(lambda: np.dot(a, a))                               # sin temporal
print(f"pico de memoria: np.sum(a*a) = {pico_temporal / 1e6:.1f} MB · np.dot(a, a) = {pico_dot / 1e6:.3f} MB")
print("mismo resultado:", np.isclose(np.sum(a * a), np.dot(a, a), rtol=1e-9))
CIFRAS.update(ganancia_5M=ganancias[-1], pico_temporal_mb=pico_temporal / 1e6, pico_dot_mb=pico_dot / 1e6)
assert np.isclose(r1, r2, rtol=1e-9)
assert all(g > 3 for g in ganancias), "NumPy debe ganar en los tres tamaños"
assert pico_temporal > 30e6 and pico_dot < 1e6

# %% [markdown]
# ## 7.3 · `int64` se desborda sin avisar
#
# Un `int64` guarda enteros de $-2^{63}$ a $2^{63}-1$ ($\approx9.2\times10^{18}$). La suma exacta de los
# cuadrados de 0 a $n-1$ es $\dfrac{(n-1)\,n\,(2n-1)}{6}$; con $n=5\,000\,000$ vale $\approx4.17\times10^{19}$,
# más de cuatro veces el máximo. NumPy **no lanza error**: el resultado «da la vuelta» y es otro número. `float64`
# conserva la magnitud pero pierde los últimos dígitos (tiene 53 bits de mantisa). El `int` de Python no tiene
# tope y sirve de referencia exacta.
#
# **Qué esperar.** El exacto de Python, un `int64` con otro valor (posiblemente negativo) y un `float64` con
# el orden de magnitud correcto en notación científica.

# %%
# celda 7.3
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

# %% [markdown]
# ### 7.3 ampliada: dónde empieza el desborde y qué hace el `float64`
#
# Se barren valores de $n$ y se compara cada suma con la exacta. El primer $n$ que desborda es el que cumple
# $(n-1)\,n\,(2n-1)/6 > 2^{63}-1$, alrededor de $3.04\times10^6$. Además, dos formas de ver el **mismo** problema
# con un solo elemento: el escalar avisa (`RuntimeWarning`), el arreglo no.
#
# **Qué esperar.** Para $n\le3\times10^6$ el `int64` coincide con el exacto; para $n\ge4\times10^6$ no. El
# `float64` queda a menos de $10^{-12}$ del exacto (error relativo); en este rango la columna sale en 0 o casi.

# %%
# Barrido de n: ¿desde dónde se desborda int64? ¿cuánto se equivoca float64?
tope = np.iinfo(np.int64).max
print(f"{'n':>12}{'exacto > tope':>15}{'int64 coincide':>16}{'error relativo float64':>26}")
desborda_en = None
for m in (1_000_000, 3_000_000, 4_000_000, 5_000_000):
    exacto_m = (m - 1) * m * (2 * m - 1) // 6
    s_int = int(np.sum(np.arange(m, dtype=np.int64) ** 2))
    s_flt = float(np.sum(np.arange(m, dtype=np.float64) ** 2))
    rel = abs(s_flt - exacto_m) / exacto_m
    print(f"{m:>12,}{str(exacto_m > tope):>15}{str(s_int == exacto_m):>16}{rel:>26.1e}")
    if desborda_en is None and s_int != exacto_m:
        desborda_en = m
    assert (s_int == exacto_m) == (exacto_m <= tope), "int64 coincide exactamente cuando el exacto cabe"
    assert rel < 1e-12

import warnings
with warnings.catch_warnings(record=True) as avisos:
    warnings.simplefilter("always")
    escalar = np.int64(tope) + np.int64(1)                          # NUEVO: el escalar avisa
    arreglo = np.array([tope], dtype=np.int64) + 1                  # NUEVO: el arreglo no avisa
print(f"escalar: {escalar} · avisos: {len(avisos)} ({avisos[0].category.__name__ if avisos else '-'})")
print(f"arreglo: {arreglo[0]} · da la vuelta al mínimo de int64: {arreglo[0] == np.iinfo(np.int64).min}")
CIFRAS["n_primer_desborde"] = desborda_en
assert desborda_en == 4_000_000
assert arreglo[0] == np.iinfo(np.int64).min, "el arreglo se desborda en silencio"
assert con_int64 != exacto and con_float64 > 4e19

# %% [markdown]
# ## Vistas, copias y memoria no contigua
#
# NumPy tiene dos formas de entregar «una parte» de un arreglo:
#
# | operación | qué devuelve | cuesta |
# |---|---|---|
# | `a[100:200]` (corte simple) | **vista**: mismos datos, otros límites | casi nada |
# | `a[::8]` (corte con paso) | **vista no contigua**: salta de 8 en 8 elementos (`strides`) | casi nada, pero recorrerla es más lento |
# | `a[[1, 5, 9]]` (índices) | **copia** | O(tamaño) |
# | `a.T` de una matriz | **vista** con `strides` invertidos (ya no es contigua por filas) | casi nada |
# | `a.ravel()` | vista si es contigua; **copia** si no | depende |
#
# Una vista comparte memoria con el original: **escribir en ella escribe en él**. Y una vista no contigua rompe la
# propiedad que hacía rápido a NumPy (valores consecutivos en memoria, que la CPU trae en bloque): se pagan más
# fallos de caché.
#
# **Qué esperar.** `shares_memory` verdadero para las vistas y falso para la copia; `C_CONTIGUOUS` falso para
# `a[::8]` y `.T`; modificar la vista cambia el original; sumar la vista `[::8]` (un octavo de los
# datos) cuesta bastante más que un octavo del tiempo de sumar todo, porque cada línea de caché de 64 bytes trae 8 `float64` y la
# vista usa uno solo por línea; la copia contigua del mismo octavo es la más rápida.

# %%
# Vistas, copias y contigüidad.
b = np.arange(1_000_000, dtype=np.float64)
corte = b[100:200]                                  # vista contigua
paso = b[::8]                                       # vista NO contigua: una de cada 8
copia = b[[1, 5, 9]]                                # copia
print("corte  → comparte memoria:", np.shares_memory(b, corte), "· contiguo:", corte.flags["C_CONTIGUOUS"], "· base es b:", corte.base is b)
print("paso   → comparte memoria:", np.shares_memory(b, paso), "· contiguo:", paso.flags["C_CONTIGUOUS"], "· strides:", paso.strides)
print("copia  → comparte memoria:", np.shares_memory(b, copia), "· contiguo:", copia.flags["C_CONTIGUOUS"])

corte[0] = -1.0                                     # escribir en la vista
print("b[100] después de escribir en la vista:", b[100])

m = np.arange(3000 * 3000, dtype=np.float64).reshape(3000, 3000)
t = m.T                                             # transpuesta: vista con los strides invertidos
print("m.T → comparte memoria:", np.shares_memory(m, t), "· contiguo por filas:", t.flags["C_CONTIGUOUS"], "· strides:", t.strides)
print("m.ravel() comparte memoria:", np.shares_memory(m, m.ravel()), "· t.ravel() comparte memoria:", np.shares_memory(m, t.ravel()))

# Costo de recorrer: todo b, un octavo de b con paso 8 (vista), y ese octavo ya copiado contiguo.
grande = np.arange(40_000_000, dtype=np.float64)    # 320 MB: bastante más que la caché
vista8 = grande[::8]
contiguo8 = vista8.copy()
t_todo = mejor_de(lambda: grande.sum())
t_vista = mejor_de(lambda: vista8.sum())
t_cont = mejor_de(lambda: contiguo8.sum())
print(f"sumar los 40 M:                    {t_todo * 1000:7.1f} ms")
print(f"sumar 1/8 por la vista no contigua: {t_vista * 1000:7.1f} ms")
print(f"sumar ese 1/8 ya copiado contiguo:  {t_cont * 1000:7.1f} ms")
del grande, vista8, contiguo8
CIFRAS.update(t_todo_ms=t_todo * 1000, t_vista8_ms=t_vista * 1000, t_cont8_ms=t_cont * 1000)
assert np.shares_memory(b, corte) and np.shares_memory(b, paso) and not np.shares_memory(b, copia)
assert not paso.flags["C_CONTIGUOUS"] and not t.flags["C_CONTIGUOUS"] and b[100] == -1.0
assert np.shares_memory(m, m.ravel()) and not np.shares_memory(m, t.ravel())
assert t_cont < t_vista, "la misma suma sobre memoria contigua es más rápida que sobre la vista"

# %% [markdown]
# ## Cierre del tema: la tabla
#
# | pregunta | respuesta medida |
# |---|---|
# | ¿cuánto ocupa un `float64` de 5 M? | 40 MB; la lista equivalente, cuatro veces más |
# | ¿cuánto gana NumPy contra el bucle? | de 10× a 30× en esta máquina; baja al crecer $n$ porque el arreglo rebasa la caché |
# | ¿qué cuesta una expresión como `a * a`? | un temporal del tamaño de los datos; `np.dot` no lo necesita |
# | ¿cuándo se desborda `int64` en la suma de cuadrados? | desde $n=4\times10^6$; sin error ni aviso en arreglos |
# | ¿una vista copia? | no: comparte memoria y escribir en ella cambia el original |
# | ¿una vista con paso es tan rápida? | no: pierde contigüidad |

# %%
print(f"{'cifra':<20}{'valor':>12}")
for nombre, valor in CIFRAS.items():
    print(f"{nombre:<20}{valor:>12.2f}")
assert CIFRAS["ganancia_5M"] > 5 and CIFRAS["mb_lista"] > 3 * CIFRAS["mb_float64"]
print("tema 7: todas las comprobaciones pasan")
