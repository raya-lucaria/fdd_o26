# %% [markdown]
# # Tema 8 · Elegir la estrategia: una tabla de decisión que se ejecuta
#
# **Pregunta.** Dado un trabajo —cuántas tareas, cuánto de cada una es CPU y cuánto es espera, qué tipo de
# operación—, ¿qué estrategia se elige, y qué tiempo se predice para ella?
#
# La página 8 resume la unidad en una tabla. Aquí la tabla es **código**: una función `decide` recibe los datos del
# trabajo y devuelve la estrategia, y otra, `predice`, devuelve el tiempo que la teoría espera. Se alimentan con
# **tus mediciones** (no con las de la página) y se comparan con una corrida real. Tres partes:
#
# | parte | qué hace |
# |---|---|
# | 1 · Little | $L=\lambda\cdot W$ aplicada a tus 500 llamadas: cuántas hay en vuelo, cuántos hilos ocupa el servidor |
# | 2 · la decisión | medir $\rho=e/d$ de dos trabajos, escribir `decide` y probarla en una tabla de casos |
# | 3 · la `lambda` | por qué la herramienta que parecía bastar no puede viajar a un proceso, y tres formas de arreglarlo |
#
# **Notación (la fija la página `A_notacion`).** $e$ = tiempo de CPU que la tarea ejecuta; $d$ = duración total de su
# vida (de que empieza a que termina); $\rho=e/d$ ∈ [0, 1]. $\rho\approx0$: casi todo es espera. $\rho\approx1$:
# casi todo es cálculo. $W$ = tiempo que pasa una petición en el sistema; $\lambda$ = peticiones terminadas por
# segundo; $L$ = cuántas hay dentro, en promedio.
#
# Cargas: 500 llamadas y 4 procesos como máximo. El servidor de la clase debe estar prendido.

# %%
# Preparación del tema.
import asyncio, math, os, pickle, time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import httpx, requests
from cable import URL
from trabajo_computo import calcula

CIFRAS = {}
P = os.cpu_count()                  # CPU lógicas de esta máquina
print("P =", P, "CPU lógicas")

# %% [markdown]
# ## 8.1 · Little con las cifras de la página
#
# La Ley de Little dice que, en régimen estable, $L=\lambda\cdot W$. Con $k=32$ llamadas en vuelo
# ($L=k$) y $W=0.2$ s, el sistema no puede terminar más de $\lambda=k/W=160$ por segundo. De ahí salen la **cota**
# $\lceil n/k\rceil\cdot W$ y, despejando, la $W$ *efectiva* que midió tu corrida:
# $W_{\text{ef}}=L/\lambda=k/\lambda_{\text{medido}}$.
#
# La celda 8.1 usa los **3.32 s** de la corrida de referencia. En la ampliación se reemplazan por los tuyos.
#
# **Qué esperar.** $\lambda$ ideal 160/s, cota 3.20 s, $\lambda$ medido 151/s, $W\le0.212$ s (una cota: $L\le32$) y unos 30
# hilos del servidor; si cada llamada tardara 2 s, 301.

# %%
# celda 8.1
import math

k, W = 32, 0.2                  # tope en vuelo y segundos que tarda cada llamada
n, medido = 500, 3.32           # llamadas y segundos medidos (pon los tuyos)

lam_ideal = k / W               # Little con L = k: λ ≤ k / W
cota = math.ceil(n / k) * W     # ⌈n/k⌉ tandas de W segundos
lam_medido = n / medido         # peticiones terminadas por segundo
W_max = k / lam_medido          # L ≤ k, así que W = L / λ ≤ k / λ: una cota, no una medida

print(f"λ ideal  {lam_ideal:.0f}/s   cota  {cota:.2f} s")
print(f"λ medido {lam_medido:.0f}/s   W ≤ {W_max:.3f} s")
print(f"hilos del servidor: {lam_medido * W:.0f}; con W = 2 s: {lam_medido * 2:.0f}")

# %% [markdown]
# ### 8.1 ampliada: tus 500 llamadas, y los hilos del servidor **contados**
#
# En lugar de suponer 3.32 s se corre el lote de 500 llamadas con $k=32$ (`Semaphore(32)` +
# `Limits(32)`, como en el tema 4) y se usa `GET /quien`, que responde **el puerto de la conexión y el hilo del
# servidor** que la atiende. Contar los hilos distintos es contar cuántos hilos del servidor usó el cliente: la
# predicción de Little ($\lambda\cdot W\approx30$) es un promedio; el máximo observable es $k=32$ (una conexión por
# llamada en vuelo, un hilo por conexión).
#
# **Qué esperar.** Un tiempo cercano a la cota, una $W_{\text{ef}}$ entre 0.20 y 0.23 s, y a lo más 32 hilos del
# servidor distintos.

# %%
# NUEVO: tu propia medición de 500 llamadas, con /quien para contar hilos del servidor.
async def lote_little(n, k):
    sem = asyncio.Semaphore(k)
    async def una(cliente):
        async with sem:
            return (await cliente.get(f"{URL}/quien?lento=0.2")).json()
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=k), timeout=30) as cliente:
        t0 = time.perf_counter()
        vistos = await asyncio.gather(*(una(cliente) for _ in range(n)))
        return time.perf_counter() - t0, vistos

k, W, n = 32, 0.2, 500
medido, vistos = await lote_little(n, k)                    # NUEVO: tu medido, no el de la página
hilos_distintos = len({v["hilo"] for v in vistos})
lam_ideal, cota = k / W, math.ceil(n / k) * W
lam_medido = n / medido
W_efectiva = k / lam_medido
print(f"medido {medido:.2f} s · cota {cota:.2f} s")
print(f"λ ideal {lam_ideal:.0f}/s · λ medido {lam_medido:.0f}/s · W efectiva {W_efectiva:.3f} s")
print(f"hilos del servidor por Little: {lam_medido * W:.0f} · contados con /quien: {hilos_distintos} (máximo posible {k})")
print(f"con W = 2 s la predicción sería {lam_medido * 2:.0f} hilos: una dependencia 10 veces más lenta ocupa 10 veces más")
CIFRAS.update(medido_s=medido, lam_medido=lam_medido, W_ef=W_efectiva, hilos=hilos_distintos)
assert cota * 0.98 <= medido < cota * 1.5
assert W <= W_efectiva < W * 1.25, "la W efectiva no puede ser menor que la W del servidor"
assert 1 <= hilos_distintos <= k

# %% [markdown]
# ## 8.2 · Una `lambda` a un proceso
#
# `pool.submit(f, x)` **no** ejecuta `f` en tu línea: la mete en una cola, un hilo auxiliar del pool la serializa con
# `pickle` y la manda a un proceso hijo. `pickle` serializa una función **por nombre** (módulo + nombre) y el hijo
# la busca importando ese módulo. Una `lambda` se llama `<lambda>` y no es atributo de ningún módulo: no hay nombre
# que mandar. El error aparece en `futuro.result()`, no en `submit`.
#
# **Qué esperar.** Un `PicklingError` («Can't pickle … it's not found as `__main__.<lambda>`»), y la tabla de
# la página: `submit` pone la llamada en la cola, el envío falla, `result` relanza.

# %%
# celda 8.2
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=2) as pool:
    futuro = pool.submit(lambda x: x * 2, 21)   # la función viaja serializada con pickle
    try:
        print(futuro.result())                  # relanza aquí el error del envío
    except Exception as e:
        print(f"{type(e).__name__} · {e}")

# %% [markdown]
# ### 8.2 ampliada: la `lambda` falla, tres formas de arreglarla
#
# Se prueba cada forma con el **mismo** pool y el mismo cálculo, y se verifica el resultado:
#
# | forma | por qué viaja |
# |---|---|
# | `lambda x: x * 2` | no viaja: sin nombre importable |
# | `calcula` (función de `trabajo_computo.py`) | viaja: módulo `trabajo_computo` + nombre `calcula` |
# | `partial(calcula, 1000)` | viaja: `partial` se serializa como la función por nombre + los argumentos fijos |
# | `partial(operator.mul, 2)` | viaja: `operator.mul` es una función de la librería estándar, con nombre |
#
# La regla práctica: **lo que se manda a un proceso vive en un módulo con nombre**. Un `def` dentro de otra función
# (una *clausura*) tampoco viaja, por la misma razón. Y los argumentos también se serializan: un archivo abierto o
# una conexión de red no.

# %%
import operator
resultados = {}
with ProcessPoolExecutor(max_workers=2) as pool:
    casos = {
        "lambda": (lambda x: x * 2, (21,)),
        "función de módulo": (calcula, (1000,)),
        "partial(calcula, 1000)": (partial(calcula, 1000), ()),            # NUEVO: argumentos fijos con partial
        "partial(operator.mul, 2)": (partial(operator.mul, 2), (21,)),     # NUEVO: función de la librería estándar
    }
    for nombre, (f, args) in casos.items():
        futuro = pool.submit(f, *args)
        try:
            resultados[nombre] = futuro.result()
        except Exception as e:
            resultados[nombre] = e
print(f"{'forma':<28}resultado")
for nombre, r in resultados.items():
    texto = f"{type(r).__name__}" if isinstance(r, Exception) else str(r)
    print(f"{nombre:<28}{texto}")
CIFRAS["lambda_error"] = type(resultados["lambda"]).__name__ == "PicklingError"
assert isinstance(resultados["lambda"], (pickle.PicklingError, AttributeError))
assert resultados["función de módulo"] == calcula(1000) == resultados["partial(calcula, 1000)"]
assert resultados["partial(operator.mul, 2)"] == 42

# %% [markdown]
# ## 8.3 · ρ medida: ¿de qué es el trabajo?
#
# El primer paso para decidir es **medir** $\rho=e/d$ del trabajo. Se aproxima $e$ con el tiempo de CPU del proceso
# (`time.process_time()`) y $d$ con el de pared (`time.perf_counter()`), mientras el trabajo corre solo:
#
# - **A · 20 llamadas** con `requests` a `lento=0.2` (4 s de pared).
# - **B · un cálculo** `calcula(5_000_000)` (menos de 1 s).
#
# La ρ de A debe quedar por debajo de 0.05 (el cliente casi no usa CPU: 99 % de su vida es espera) y la de B cerca
# de 1. Con esas dos cifras se alimenta la tabla de decisión.
#
# **Qué esperar.** $\rho_A\approx0.01$ y $\rho_B\approx1.0$.

# %%
def mide_rho(trabajo):
    cpu0, t0 = time.process_time(), time.perf_counter()
    trabajo()
    cpu, pared = time.process_time() - cpu0, time.perf_counter() - t0
    return cpu / pared, cpu, pared

rho_A, cpu_A, d_A = mide_rho(lambda: [requests.get(f"{URL}/ventas?lento=0.2", timeout=30) for _ in range(20)])
rho_B, cpu_B, d_B = mide_rho(lambda: calcula(5_000_000))
print(f"{'trabajo':<22}{'e = CPU (s)':>12}{'d = pared (s)':>15}{'ρ = e/d':>9}")
print(f"{'A · 20 llamadas':<22}{cpu_A:>12.3f}{d_A:>15.2f}{rho_A:>9.3f}")
print(f"{'B · calcula(5 M)':<22}{cpu_B:>12.3f}{d_B:>15.2f}{rho_B:>9.3f}")
CIFRAS.update(rho_A=rho_A, rho_B=rho_B)
assert rho_A < 0.05, "20 llamadas: casi toda su vida es espera"
assert rho_B > 0.9, "un bucle de Python puro: casi toda su vida es CPU"

# %% [markdown]
# ## 8.4 · La tabla de decisión como función
#
# `decide` recibe lo que se midió y devuelve una estrategia. Las ramas son las filas de la tabla de la página 8:
#
# | $\rho$ | tipo de trabajo | $n$ | estrategia |
# |---|---|---|---|
# | cualquiera | arreglo numérico con operación vectorizable | cualquiera | **vectorizar** (NumPy / Polars / SQL), antes que repartir |
# | cualquiera | cualquiera | 1 | **secuencial**: nada que repartir |
# | $<0.1$ (espera) | librería asíncrona disponible | acotada | **`asyncio` + `Semaphore(k)`**, con $k$ del destino |
# | $<0.1$ | sólo librería bloqueante | acotada | **hilos** (`ThreadPoolExecutor(k)`) |
# | $<0.1$ | cualquiera | sin cota | **cola acotada + $k$ consumidores** (no `gather`) |
# | $>0.9$ (CPU) | Python puro | $\ge2$ | **procesos** $\min(n,P)$; medir $f$ antes |
# | intermedia | cualquiera | $\ge2$ | **separar las fases**: espera con `asyncio`, cálculo en procesos |
#
# **Una advertencia sobre los umbrales.** 0.1 y 0.9 son los de este curso, no leyes de la naturaleza: sirven para
# elegir con una medición y se revisan con la siguiente. La función los deja como parámetros.

# %%
def decide(rho, tipo, n, *, async_disponible=True, sin_cota=False, umbral_espera=0.1, umbral_cpu=0.9):
    """Devuelve la estrategia para un trabajo con ρ = e/d, tipo ('vectorizable' | 'python'), n tareas."""
    if tipo == "vectorizable":
        return "vectorizar (NumPy / Polars / SQL)"
    if n <= 1:
        return "secuencial"
    if rho < umbral_espera:                                  # casi todo es espera
        if sin_cota:
            return "cola acotada + k consumidores"
        return "asyncio + Semaphore(k)" if async_disponible else "hilos (ThreadPoolExecutor)"
    if rho > umbral_cpu:                                     # casi todo es CPU
        return "procesos (min(n, P))"
    return "separar fases: asyncio para esperar, procesos para calcular"

def predice(estrategia, n, e, w, k=32, P=P):
    """Segundos que la teoría espera: e = CPU por tarea, w = espera por tarea (las dos en s)."""
    if estrategia == "secuencial" or n <= 1:
        return n * (e + w)
    if estrategia.startswith(("asyncio", "hilos", "cola")):
        return math.ceil(n / k) * (e + w)                    # tandas de k
    if estrategia.startswith("procesos"):
        return math.ceil(n / min(n, P)) * e                  # tandas de min(n, P)
    return float("nan")

casos = [  # (descripción, ρ, tipo, n, extras)
    ("20 llamadas a una API",               rho_A, "python",       20,   {}),
    ("500 llamadas, librería async",        rho_A, "python",       500,  {}),
    ("500 llamadas, sólo requests",         rho_A, "python",       500,  {"async_disponible": False}),
    ("10 000 URLs, sin cota",               rho_A, "python",       10_000, {"sin_cota": True}),
    ("4 cálculos de Python puro",           rho_B, "python",       4,    {}),
    ("1 cálculo",                           rho_B, "python",       1,    {}),
    ("suma de cuadrados de 5 M",            rho_B, "vectorizable", 1,    {}),
    ("descarga + cálculo por tarea",        0.5,   "python",       50,   {}),
]
print(f"{'caso':<34}{'ρ':>6}{'n':>8}  estrategia")
decisiones = {}
for desc, rho, tipo, n_caso, extra in casos:
    decisiones[desc] = decide(rho, tipo, n_caso, **extra)
    print(f"{desc:<34}{rho:>6.2f}{n_caso:>8}  {decisiones[desc]}")

assert decisiones["20 llamadas a una API"].startswith("asyncio")
assert decisiones["500 llamadas, sólo requests"].startswith("hilos")
assert decisiones["10 000 URLs, sin cota"].startswith("cola")
assert decisiones["4 cálculos de Python puro"].startswith("procesos")
assert decisiones["1 cálculo"] == "secuencial"
assert decisiones["suma de cuadrados de 5 M"].startswith("vectorizar")
assert decisiones["descarga + cálculo por tarea"].startswith("separar")

# %% [markdown]
# ## 8.5 · La predicción contra una corrida real
#
# Una tabla de decisión que no se contrasta con la realidad es una opinión. Se toman dos casos, se piden la
# estrategia a `decide` y el tiempo a `predice`, y se **corre esa estrategia** para comparar:
#
# | caso | estrategia elegida | predicción | medición |
# |---|---|---|---|
# | 500 llamadas, $e\approx0$, $w=0.2$ s | `asyncio + Semaphore(32)` | $\lceil500/32\rceil\cdot0.2=3.2$ s | la `medido` de la ampliación 8.1 |
# | 4 cálculos de 5 M | `procesos` | $\lceil4/\min(4,P)\rceil\cdot e$ | 4 procesos reales |
#
# La predicción es una **cota inferior**: ignora el arranque de los procesos y la latencia de cada llamada fuera del
# `sleep` del servidor. La medición debe quedar *por encima* y cerca.
#
# **Qué esperar.** Un cociente medido/predicho cerca de 1.1 para las llamadas y entre 1.5 y 3 para los procesos: con un
# cálculo de ≈ 0.3 s en total, arrancar los procesos hijo pesa tanto como el cálculo mismo.

# %%
est_red = decide(rho_A, "python", 500)
pred_red = predice(est_red, 500, e=0.0, w=0.2)
est_cpu = decide(rho_B, "python", 4)
e_tarea = cpu_B                                                    # CPU de una tarea, medida en 8.3
pred_cpu = predice(est_cpu, 4, e=e_tarea, w=0.0)

t0 = time.perf_counter()
with ProcessPoolExecutor(max_workers=min(4, P)) as pool:           # ≤ 4 procesos
    sumas = list(pool.map(calcula, [5_000_000] * 4))
medido_cpu = time.perf_counter() - t0
assert len(set(sumas)) == 1

print(f"{'caso':<26}{'estrategia':<26}{'predicho':>9}{'medido':>9}{'medido/pred':>12}")
print(f"{'500 llamadas':<26}{est_red:<26}{pred_red:>8.2f}s{medido:>8.2f}s{medido / pred_red:>12.2f}")
print(f"{'4 cálculos de 5 M':<26}{est_cpu:<26}{pred_cpu:>8.2f}s{medido_cpu:>8.2f}s{medido_cpu / pred_cpu:>12.2f}")
CIFRAS.update(pred_red=pred_red, pred_cpu=pred_cpu, medido_cpu=medido_cpu)
assert pred_red * 0.98 <= medido < pred_red * 1.6
assert pred_cpu * 0.9 <= medido_cpu < pred_cpu * 5.0, "el arranque de procesos explica la diferencia"

# %% [markdown]
# ## Cierre del tema: la tabla de lo medido
#
# | pregunta | respuesta medida |
# |---|---|
# | ¿cuántas llamadas hay en vuelo y cuántos hilos ocupa el servidor? | $L=k=32$; hilos ≤ 32 (Little da ≈ 30 en promedio) |
# | ¿qué $W$ efectiva tuvo cada llamada? | un poco más que 0.2 s: el costo de ir y volver |
# | ¿qué le pasa a una `lambda` en un proceso? | `PicklingError`: sin nombre importable |
# | ¿$\rho$ de 20 llamadas? ¿de un bucle? | ≈ 0 y ≈ 1 |
# | ¿qué estrategia sale de la función? | la de la tabla, y su predicción queda bajo la medición |

# %%
print(f"{'cifra':<14}{'valor':>10}")
for nombre, valor in CIFRAS.items():
    print(f"{nombre:<14}{valor:>10.3f}" if isinstance(valor, float) else f"{nombre:<14}{str(valor):>10}")
assert CIFRAS["rho_A"] < 0.05 < 0.9 < CIFRAS["rho_B"]
assert CIFRAS["lambda_error"]
print("tema 8: todas las comprobaciones pasan")
