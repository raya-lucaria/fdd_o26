# %% [markdown]
# # Tema 6 · Calcular en paralelo: el loop bloqueado, los procesos y la curva de Amdahl
#
# **Pregunta.** Dentro de un servicio `async` hay un cálculo de 2 s en Python puro. ¿Qué le pasa a las otras
# tareas? ¿Se arregla con un hilo? ¿Con un proceso? ¿Cuánto se gana con 1, 2 y 4 procesos, y por qué no se gana
# lo que dice el número de procesos?
#
# Este tema es la versión verbosa de la página 6. Todo el cálculo es **local**: no necesita el servidor de la
# clase. `calcula` vive en `trabajo_computo.py` y no en una celda, porque un proceso hijo recibe de `pickle` el
# *nombre* de la función (módulo + nombre) y la busca importando ese módulo; una función definida en la celda
# pertenece a `__main__` del kernel, que el hijo no puede importar.
#
# **Lo que se mide en este tema**
#
# | medición | celda | qué prueba |
# |---|---|---|
# | latido con el cálculo **en** el loop | 6.1 | un cálculo sin `await` detiene a todas las tareas del loop |
# | latido con el cálculo en un **hilo** | 6.1 ampliada | el loop no se detiene, pero el cálculo no se acelera (GIL) |
# | latido con el cálculo en un **proceso** | 6.2 | el loop sigue y el cálculo corre en otra CPU |
# | 4 tareas con 1, 2 y 4 procesos | 6.3 ampliada | speedup, eficiencia y la fracción serial $f$ |
# | una `lambda` a un proceso | cierre | `pickle` manda funciones por nombre |
#
# Cargas del tema: **a lo más 4 procesos** y cálculos de 0.3 a 2 s.

# %%
# Preparación del tema: imports y la tabla donde se acumulan las cifras.
import asyncio, math, pickle, time
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
from trabajo_computo import calcula, calcula_medido
from gantt import registra, dibuja, reinicia

CIFRAS = {}
print("calcula(1000) =", calcula(1000), "· determinista: mismo n, mismo resultado")

# %% [markdown]
# ## 6.1 · Un latido y un cálculo en el mismo loop
#
# `latido` imprime una línea cada 0.1 s con `await asyncio.sleep(0.1)`: cada `await` cede el hilo. `calculo`
# espera 0.15 s (para que salgan dos latidos) y después llama a `calcula()`, **sin ningún `await`**. Mientras
# `calcula()` ejecuta, el hilo del loop está ocupado y *nadie más corre*. Cuando `latido` despierta de su `sleep`,
# queda en estado `lista`: puede ejecutar, pero no tiene el hilo.
#
# **Qué esperar.** Los latidos 0 y 1 salen a 0.00 y 0.10 s; el cálculo dura entre 1 y 2 s según la CPU; el latido 2 sale con ese mismo
# retraso en lugar de 0.1 s. No hay error ni aviso: un loop bloqueado sólo se nota en la latencia.

# %%
# celda 6.1
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

# %% [markdown]
# ### 6.1 ampliada: tres dónde-corre-el-cálculo, con la misma medición
#
# El latido de la celda 6.1 imprime; para **comparar** hace falta un número. `latido_g` anota el instante de
# cada latido y el Gantt de lo que pasó: el latido es una fila con tres tipos de barra —`espera` (el `sleep`),
# `lista` (el `sleep` ya venció pero no hay hilo) y una marca `exec` muy corta cuando imprime—. El número que
# resume la corrida es el **mayor intervalo entre latidos consecutivos**: ideal, 0.1 s.
#
# Se comparan tres sitios para el mismo `calcula()`:
#
# | sitio | cómo | qué se espera |
# |---|---|---|
# | en el loop | `calcula()` directo | intervalo máximo ≈ duración del cálculo |
# | en un hilo | `await asyncio.to_thread(calcula)` | el loop no se detiene (el intérprete cede el GIL cada ≈ 5 ms), pero el cálculo y el latido **comparten un GIL** |
# | en un proceso | `await loop.run_in_executor(pool, calcula)` | el loop no nota nada; el cálculo corre en otra CPU con otro GIL |
#
# **Qué esperar.** Intervalo máximo ≈ la duración del cálculo en el loop, ≈ 0.1 s en el hilo y en el proceso. La diferencia entre
# hilo y proceso no se ve en el latido sino en el **cálculo**: en un hilo no se acelera ni se reparte entre CPU.

# %%
# Misma medición para tres sitios. NUEVO: latido_g anota cada latido y el Gantt.
async def latido_g(duracion, marcas):
    inicio = time.perf_counter()
    while time.perf_counter() - inicio < duracion:
        antes = time.perf_counter()
        await asyncio.sleep(0.1)                               # cede el loop
        ahora = time.perf_counter()
        marcas.append(ahora)                                   # NUEVO: instante de cada latido
        registra("latido", antes, antes + 0.1, "espera")       # NUEVO: el sleep
        if ahora - antes - 0.1 > 0.01:
            registra("latido", antes + 0.1, ahora, "lista")   # NUEVO: venció y no tiene hilo
        registra("latido", ahora, ahora + 0.004, "exec")       # NUEVO: imprime

async def en_el_loop():
    await asyncio.sleep(0.15)
    ini = time.perf_counter()
    calcula()                                                  # sin await: el loop queda ocupado
    registra("cálculo", ini, time.perf_counter(), "exec")
    return time.perf_counter() - ini

async def en_un_hilo():
    await asyncio.sleep(0.15)
    ini = time.perf_counter()
    await asyncio.to_thread(calcula)                           # NUEVO: otro hilo del mismo proceso (mismo GIL)
    registra("cálculo", ini, time.perf_counter(), "exec")
    return time.perf_counter() - ini

async def en_un_proceso(pool):
    await asyncio.sleep(0.15)
    ini = time.perf_counter()
    await asyncio.get_running_loop().run_in_executor(pool, calcula)    # NUEVO: otro proceso (otro GIL)
    registra("cálculo", ini, time.perf_counter(), "exec")
    return time.perf_counter() - ini

async def corrida(nombre, trabajo, duracion=3.2):
    reinicia()
    marcas = []
    _, dur = await asyncio.gather(latido_g(duracion, marcas), trabajo)
    huecos = [b - a for a, b in zip(marcas, marcas[1:])]
    dibuja(f"{nombre} · intervalo máximo entre latidos {max(huecos):.2f} s")
    return dur, max(huecos)

with ProcessPoolExecutor(max_workers=1) as pool:
    pool.submit(calcula, 1).result()                           # NUEVO: arranca el proceso antes de medir
    filas = [("en el loop",) + await corrida("cálculo EN EL LOOP", en_el_loop()),
             ("en un hilo",) + await corrida("cálculo en un HILO", en_un_hilo()),
             ("en un proceso",) + await corrida("cálculo en un PROCESO", en_un_proceso(pool))]
print(f"{'dónde corre':<15}{'cálculo (s)':>12}{'mayor hueco entre latidos (s)':>32}")
for nombre, dur, hueco in filas:
    print(f"{nombre:<15}{dur:>12.2f}{hueco:>32.2f}")
CIFRAS.update(hueco_loop=filas[0][2], hueco_hilo=filas[1][2], hueco_proceso=filas[2][2], calc_s=filas[0][1])
assert filas[0][2] > 0.8 * filas[0][1], "con el cálculo en el loop, el hueco es casi todo el cálculo"
assert filas[1][2] < 0.5 and filas[2][2] < 0.3, "en un hilo o un proceso el loop sigue latiendo"

# %% [markdown]
# ## 6.2 · El mismo latido, con el cálculo en un proceso
#
# `run_in_executor(pool, calcula)` manda `calcula` (por nombre, con `pickle`) a un proceso hijo y devuelve un
# futuro; el `await` suspende a `calculo_fuera` y **libera el hilo del loop**, así que `latido` sigue. Se pasa
# `calcula`, no `calcula()`: con paréntesis se ejecutaría aquí, en el loop.
#
# La celda reutiliza `latido` y `t0` de la 6.1.
#
# **Qué esperar.** Los cinco latidos cada 0.1 s; el cálculo tarda un poco más que en el loop porque incluye
# arrancar el proceso (el pool lo crea en el primer envío), mandar la tarea y traer el resultado.

# %%
# celda 6.2
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

# %% [markdown]
# ## 6.3 · Amdahl: lo que dice la fórmula
#
# Con una fracción serial $f$ (lo que no se puede repartir) y $N$ trabajadores, el speedup máximo es
# $S(N)=\dfrac{1}{f+(1-f)/N}$ y tiene techo $1/f$. La celda 6.3 es la fórmula tal cual: no mide nada.

# %%
# celda 6.3
def amdahl(f, N):
    """Speedup con fracción serial f y N trabajadores (reparto perfecto)."""
    return 1 / (f + (1 - f) / N)

for f in (0.10, 0.25, 0.50):
    fila = [f"{amdahl(f, N):.2f}" for N in (2, 4, 8)]     # S(2), S(4), S(8)
    print(f"f={f:.2f} {fila} techo: {1 / f:.1f}")
print("f=0.25, de 4 a 8 trabajadores:", round(amdahl(0.25, 8) / amdahl(0.25, 4), 2), "veces más")

# %% [markdown]
# ### 6.3 ampliada: medir 1, 2 y 4 procesos, y ajustar $f$
#
# **Qué se mide.** Cuatro tareas independientes, cada una `calcula(5_000_000)` (≈ 0.3 s), repartidas con
# `ProcessPoolExecutor(max_workers=N)` para $N=1,2,4$. El tiempo **incluye** crear el pool y arrancar los
# procesos hijo, y eso es parte de la fracción serial: nadie reparte el arranque.
#
# **Qué se calcula.**
#
# - Speedup $S(N)=T_1/T_N$ y eficiencia $E(N)=S(N)/N$.
# - $f$ **ajustada**: de $S=\dfrac{1}{f+(1-f)/N}$ se despeja $f=\dfrac{1/S-1/N}{1-1/N}$ para cada $N>1$ y se promedia.
# - La curva $S(N)$ con esa $f$, contra los puntos medidos.
#
# **Por qué no pasar de 4.** Hay sólo 4 tareas: con más de 4 trabajadores, los demás no tienen qué hacer. Es un
# techo distinto del de Amdahl (reparto, no parte serial) y la fórmula no lo sabe. Tampoco conviene tener más
# procesos que CPU lógicas $P$ (esta máquina tiene 8).
#
# **Qué esperar.** $S(2)$ cerca de 1.6–1.9, $S(4)$ cerca de 2.3–3.3 (el arranque de los procesos es una fracción
# fija; mientras menos dure el cálculo, más pesa). La $f$ ajustada es de unas décimas.

# %%
# Cuatro tareas con 1, 2 y 4 procesos: tiempo, speedup, eficiencia, f ajustada y la curva.
N_TAREAS, N_CALC = 4, 5_000_000

def corre_procesos(N):
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=N) as pool:           # el pool nace aquí: su arranque cuenta
        resultados = list(pool.map(calcula, [N_CALC] * N_TAREAS))   # NUEVO: 4 tareas repartidas entre N procesos
    return time.perf_counter() - t0, resultados

T = {}
for N in (1, 2, 4):
    T[N], res = corre_procesos(N)
    assert len(set(res)) == 1                                  # las 4 tareas dan el mismo resultado

S = {N: T[1] / T[N] for N in T}                                # NUEVO: speedup medido
E = {N: S[N] / N for N in T}                                   # NUEVO: eficiencia
fs = [(1 / S[N] - 1 / N) / (1 - 1 / N) for N in (2, 4)]        # NUEVO: f despejada de cada medición
f_ajustada = sum(fs) / len(fs)
print(f"{'N':>3}{'T (s)':>8}{'S medido':>10}{'S(N) con f':>12}{'E':>7}")
for N in T:
    print(f"{N:>3}{T[N]:>8.2f}{S[N]:>10.2f}{amdahl(f_ajustada, N):>12.2f}{E[N]:>7.2f}")
print(f"f ajustada = {f_ajustada:.2f}  (de N=2: {fs[0]:.2f}, de N=4: {fs[1]:.2f}) · techo 1/f = {1 / f_ajustada:.1f}")

xs = range(1, 9)
fig, ax = plt.subplots(figsize=(6.5, 3.8))
ax.plot(xs, list(xs), "--", color="#999999", label="ideal S = N")
ax.plot(xs, [amdahl(f_ajustada, n) for n in xs], color="#1f4e8c", label=f"Amdahl con f = {f_ajustada:.2f}")
ax.axhline(1 / f_ajustada, color="#8a5a00", linestyle=":", label=f"techo 1/f = {1 / f_ajustada:.1f}")
ax.plot(list(S), list(S.values()), "o", color="#c0392b", label="medido (4 tareas)")
ax.set_xlabel("procesos N"); ax.set_ylabel("speedup"); ax.set_title("La curva de Amdahl con la f de esta máquina")
ax.legend(); fig.tight_layout(); plt.show()
CIFRAS.update(T1=T[1], T2=T[2], T4=T[4], S2=S[2], S4=S[4], f=f_ajustada)
assert S[2] > 1.3 and S[4] > S[2], "más procesos deben acelerar"
assert S[4] < 4.0, "el speedup de 4 procesos no puede ser el ideal: el arranque es serial"
assert 0 < f_ajustada < 0.7

# %% [markdown]
# ### Dónde corrió cada tarea: el Gantt de 4 tareas con 2 procesos
#
# `calcula_medido` devuelve cuándo empezó y terminó **dentro del proceso hijo**, con `time.time()` (el reloj de
# pared del sistema; los dos procesos lo comparten, el `perf_counter` de uno no es el del otro). El Gantt tiene
# una fila por tarea: `lista` (rayado) de que se envió al pool hasta que algún trabajador la tomó, y `exec`
# mientras calcula. Con 2 procesos y 4 tareas hay dos olas; la primera empieza **después** del envío porque
# primero hay que arrancar los procesos.
#
# **Qué esperar.** Las tareas 0 y 1 con `lista` corto (el arranque del proceso) y `exec` de ≈ 0.3 s; las tareas 2 y 3
# con un `lista` largo (esperan a que termine la ola anterior).

# %%
reinicia()
with ProcessPoolExecutor(max_workers=2) as pool:
    envio = time.time()
    futuros = [pool.submit(calcula_medido, N_CALC) for _ in range(N_TAREAS)]   # las 4 salen a la vez
    medidas = [f.result() for f in futuros]
for i, (ini, fin, _) in enumerate(medidas):
    registra(f"tarea {i}", envio, ini, "lista")                # esperó trabajador (o arranque del proceso)
    registra(f"tarea {i}", ini, fin, "exec")                   # calculó en un proceso hijo
dibuja("4 tareas, 2 procesos · rayado = en la cola del pool, relleno = calculando")
esperas = [ini - envio for ini, _, _ in medidas]
print("espera en la cola (s):", [round(e, 2) for e in esperas])
assert max(esperas[:2]) < min(esperas[2:]), "las dos primeras tareas arrancan antes que las dos últimas"

# %% [markdown]
# ## Una `lambda` a un proceso
#
# `pickle` serializa una función **por nombre**: módulo + nombre. `trabajo_computo.calcula` tiene uno que el hijo
# puede importar. Una `lambda` se llama `<lambda>` y no es atributo de ningún módulo, así que no hay nombre que
# mandar. El error se ve al serializar; aquí se ve **sin pool**, con `pickle.dumps`, para no depender del
# momento en que el pool lo reporta (el tema 8 lo hace con el pool).

# %%
bytes_calcula = pickle.dumps(calcula)
print("pickle.dumps(calcula):", len(bytes_calcula), "bytes · contiene el módulo:", b"trabajo_computo" in bytes_calcula)
try:
    pickle.dumps(lambda x: x * 2)
except Exception as e:
    print(f"pickle.dumps(lambda) -> {type(e).__name__}: {str(e)[:80]}")
    error = e
assert b"trabajo_computo" in bytes_calcula and b"calcula" in bytes_calcula
assert isinstance(error, (pickle.PicklingError, AttributeError))

# %% [markdown]
# ## Cierre del tema: la tabla
#
# | pregunta | respuesta medida |
# |---|---|
# | ¿un cálculo en el loop detiene las otras tareas? | sí: el mayor hueco entre latidos es casi toda la duración del cálculo |
# | ¿un hilo lo arregla? | el loop sigue, pero el cálculo en Python puro no se acelera (mismo GIL) |
# | ¿un proceso lo arregla? | sí: el loop sigue y el cálculo usa otra CPU |
# | ¿cuánto acelera repartir entre 2 y 4 procesos? | menos que el ideal; la diferencia es la fracción serial $f$ |
# | ¿cómo viaja la función a otro proceso? | por nombre: una `lambda` no tiene uno |

# %%
print(f"{'cifra':<16}{'valor':>8}")
for nombre, valor in CIFRAS.items():
    print(f"{nombre:<16}{valor:>8.2f}")
assert CIFRAS["hueco_loop"] > 10 * CIFRAS["hueco_proceso"]
assert CIFRAS["T4"] < CIFRAS["T2"] < CIFRAS["T1"]
print("tema 6: todas las comprobaciones pasan")
