# %% [markdown]
# # Tema 1 · Dónde pasa el tiempo
#
# **Pregunta.** Una llamada a una API tarda 0.2 s: ¿cuánto de eso trabaja tu
# CPU? **Meta.** Medir, con dos relojes, que el tiempo de un cliente de red es
# casi todo espera, y construir la **v1** del cliente (un `for` con `requests`)
# midiéndola con un Gantt real.
#
# Vocabulario de la página 1: una **tarea** pasa por estados; en `exec` usa CPU,
# en `espera` aguarda algo de fuera (aquí, al servidor) y en `lista` podría
# ejecutar pero no tiene CPU. `ρ = exec / vida` es la fracción de la vida que
# la tarea de verdad trabaja.

# %% [markdown]
# ## Paso 1 · Dos relojes
#
# Python tiene dos relojes para un mismo programa:
#
# - `time.perf_counter()`: el reloj de pared, segundos reales transcurridos.
# - `time.process_time()`: segundos de CPU que **tu proceso** usó (excluye el
#   tiempo que está dormido o esperando red).
#
# Si el segundo es mucho menor que el primero, la tarea pasó casi todo su
# tiempo en `espera`. La celda mide una llamada al servidor con
# `?lento=0.2` (el servidor duerme 0.2 s antes de contestar) y, de contraste,
# un bucle puro de Python que nunca espera nada.
#
# **Qué esperar.** La llamada: reloj ≈ 0.2 s, CPU de unos milisegundos, CPU/reloj
# de un solo dígito de por ciento. El bucle: reloj y CPU casi iguales, ≈ 100 %.

# %%
# celda 1.1
import time, requests
from cable import URL

def cuenta(n=3_000_000):
    suma = 0
    for i in range(n): suma += i * i      # bucle puro: nunca espera
def mide(nombre, tarea):
    r0, c0 = time.perf_counter(), time.process_time()   # pared y CPU
    tarea()
    r, c = time.perf_counter() - r0, time.process_time() - c0
    print(f"{nombre:22} reloj {r:5.2f} s   CPU {c:5.2f} s   CPU/reloj {c / r:5.0%}")
mide("llamada ?lento=0.2", lambda: requests.get(f"{URL}/ventas?lento=0.2", timeout=5))
mide("bucle puro de Python", cuenta)

# %% [markdown]
# Lee el resultado como estados: la llamada fue `espera` casi toda su vida
# (ρ ≈ 0); el bucle fue `exec` toda la suya (ρ ≈ 1). Esa diferencia decide
# todo lo demás de la unidad: lo que **espera** se puede solapar con otra cosa;
# lo que **ejecuta** sólo se acelera con más CPU.

# %% [markdown]
# ## Paso 2 · Presupuesto de latencia de un endpoint
#
# Antes de medir más, la misma idea con cifras de un endpoint típico (cifras
# **supuestas**, no medidas, para practicar la cuenta): consulta a la BD 50 ms,
# llamada a otra API 1.5 s, procesar el resultado 1 ms de CPU. La latencia es la
# suma, y la pregunta útil es qué parte es CPU.

# %%
presupuesto = [("consulta a la BD", 0.050, "espera"),
               ("llamada a otra API", 1.500, "espera"),
               ("procesar el resultado", 0.001, "exec")]
total = sum(d for _, d, _ in presupuesto)
print(f"{'paso':24} {'segundos':>9} {'% de la latencia':>17}  estado")
for nombre, d, estado in presupuesto:
    print(f"{nombre:24} {d:9.3f} {d / total:17.1%}  {estado}")
print(f"{'total':24} {total:9.3f}")
assert abs(sum(d for _, d, e in presupuesto if e == "espera") / total - 0.9994) < 1e-3

# %% [markdown]
# **Qué esperar.** El 99.9 % de la latencia es `espera`. Hacer el CPU 10 veces
# más rápido ahorra menos de un milisegundo; solapar la espera de la API con
# otra cosa es lo que mueve la aguja. «Mide antes de elegir.»

# %% [markdown]
# ## Paso 3 · Veinte llamadas en secuencia
#
# La celda 1.2 de la página repite la llamada 20 veces con un `for` y reparte el
# tiempo entre CPU y espera con los mismos dos relojes. Un `for` que espera la
# respuesta de una llamada antes de hacer la siguiente es **secuencial**: la
# vida de una tarea empieza justo donde acaba la anterior. Predicción antes de
# correr: 20 × 0.2 s = 4 s de sueño pedido, más algo de sobrecarga de red.

# %%
# celda 1.2
import time, requests
from cable import URL

N = 20
r0, c0 = time.perf_counter(), time.process_time()
for _ in range(N):                          # una llamada tras otra: secuencial
    requests.get(f"{URL}/ventas?lento=0.2", timeout=5)
r, c = time.perf_counter() - r0, time.process_time() - c0
print(f"{N} llamadas en serie: {r:.2f} s  ({r / N:.3f} s por llamada)")
print(f"ejecuta (CPU):  {c:.2f} s  ({c / r:.1%})")
print(f"espera:         {r - c:.2f} s  ({(r - c) / r:.1%})")
print(f"sueño pedido al servidor: {N * 0.2:.1f} s")

# %% [markdown]
# **Qué pasó.** `espera` ≈ 99 % del reloj; `ejecuta (CPU)` ≈ 1 %. El reloj es
# un poco mayor que 4.0 s: cada llamada paga además unos milisegundos de red,
# armar la petición y leer la respuesta.

# %% [markdown]
# ## Paso 4 · v1 del cliente, medida con un Gantt real
#
# Esta es la **v1** del cliente que la unidad va a mejorar en cada tema. Es el
# mismo `for` de la celda anterior, con una línea marcada `# NUEVO:` que anota
# en `gantt` cuándo empezó y cuándo terminó cada llamada. Anotamos cada llamada
# completa como `espera`: desde que sale la petición hasta que llega la
# respuesta, el cliente no trabaja (CPU ≈ 1 %, lo medido arriba). Cada llamada
# es una tarea (una fila).

# %%
# v1: un for con requests, una llamada tras otra
import time, requests
from cable import URL
import gantt                                          # NUEVO: el Gantt medido

def cliente_v1(n, lento=0.2):
    gantt.reinicia()                                  # NUEVO: dibujo limpio
    codigos = []
    inicio = time.perf_counter()
    for i in range(n):                                # una llamada tras otra
        a = time.perf_counter()                       # NUEVO: cuándo sale la petición
        r = requests.get(f"{URL}/ventas?lento={lento}", timeout=5)
        b = time.perf_counter()                       # NUEVO: cuándo llega la respuesta
        gantt.registra(f"llamada {i:02d}", a, b, "espera")   # NUEVO: anota el intervalo
        codigos.append(r.status_code)
    return codigos, time.perf_counter() - inicio

codigos, t_v1 = cliente_v1(20)
gantt.dibuja("v1 · 20 llamadas en serie (for + requests)")

# %% [markdown]
# **Qué esperar.** Una escalera: 20 filas, cada barra de contorno (espera)
# empieza donde termina la anterior y a ningún instante hay dos barras
# abiertas a la vez. La anchura total del dibujo es `T`, la suma de las 20
# duraciones. Eso es lo que significa **secuencial**.

# %% [markdown]
# ## Paso 5 · Resultados del tema 1
#
# `assert`s: todas las respuestas fueron `200`, no hubo solapamiento (cada
# llamada empieza donde o después de donde acaba la anterior) y el tiempo total
# cubre el sueño pedido. Después, una pequeña tabla que irá creciendo versión
# por versión en los temas siguientes.

# %%
regs = sorted(gantt.registros(), key=lambda d: d[1])
assert set(codigos) == {200}
assert all(regs[k + 1][1] >= regs[k][2] for k in range(len(regs) - 1)), "hay solape: no es secuencial"
assert t_v1 >= 20 * 0.2

print(f"{'versión':30} {'llamadas':>8} {'tiempo (s)':>11} {'llam/s':>8}")
print(f"{'v1 for + requests':30} {20:8d} {t_v1:11.2f} {20 / t_v1:8.1f}")
print(f"predicción para 500 llamadas en serie: {500 * t_v1 / 20:6.0f} s (no se corre: {500 * 0.2:.0f} s de pura espera)")
