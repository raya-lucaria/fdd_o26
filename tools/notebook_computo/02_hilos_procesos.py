# %% [markdown]
# # Tema 2 · Secuencial, concurrente, paralelo
#
# **Pregunta.** ¿Cómo bajar las 4 s de la v1? Dos respuestas distintas según
# dónde se va el tiempo: si **espera**, se solapan las esperas (hilos); si
# **ejecuta**, hacen falta más CPU (procesos). **Meta.** La v2 del cliente con
# `ThreadPoolExecutor`, el cálculo con 1, 2 y 4 procesos con su gráfica de
# speedup, y la carrera de datos paso a paso.
#
# Definiciones de la página 2, sobre la traza (el Gantt):
#
# - **secuencial:** nunca hay dos tareas con vida simultánea.
# - **concurrente:** hay dos tareas cuyas vidas se solapan.
# - **paralelo:** hay dos tareas **ejecutando** a la vez (necesita `P ≥ 2` CPU).
#   Todo lo paralelo es concurrente, no al revés.

# %% [markdown]
# ## Paso 1 · Las 20 llamadas con 32 hilos
#
# `ThreadPoolExecutor(max_workers=32)` crea hasta 32 hilos del mismo proceso.
# `hilos.map(pide, range(20))` entrega las 20 llamadas al pool: cada hilo que
# queda libre toma la siguiente. Mientras un hilo está dentro de
# `requests.get` esperando red, **suelta el GIL** (el candado del intérprete) y
# otro hilo puede correr. Con 20 llamadas y 32 hilos, todas empiezan casi a la
# vez y la espera es la de **una** llamada.
#
# **Qué esperar.** Un resultado de ≈ 0.25 s en lugar de ≈ 4 s, con `status {200}`.
# Es concurrente (las vidas se solapan) pero no es paralelo: nadie ejecuta a la
# vez con nadie, sólo esperan a la vez.

# %%
# celda 2.1
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

# %% [markdown]
# `codigos` es la lista de los 20 status; `set(codigos)` los colapsa a los
# valores distintos y debe ser `{200}`.

# %%
assert set(codigos) == {200}
t_celda_21 = time.perf_counter() - inicio
print(f"tiempo de la celda 2.1: {t_celda_21:.2f} s")

# %% [markdown]
# ## Paso 2 · v2 del cliente, medida: dónde espera cada llamada
#
# La v2 toma el cliente v1 completo y cambia sólo el bucle: ahora cada llamada
# es una función que se **envía** al pool con `submit`. Lo nuevo para el Gantt:
# además de `espera` (dentro de `requests.get`), registramos `lista` desde que
# la llamada se envía hasta que un hilo la empieza a correr. Con 32 hilos esa
# franja es casi cero; con **4** hilos, 20 llamadas hacen cinco olas y las
# llamadas de la segunda ola en adelante pasan antes un rato en `lista`
# (rayado). Predicción para `k` hilos: `⌈20/k⌉ × 0.2 s`.

# %%
# v2: el cliente v1, con un ThreadPoolExecutor
import time, requests
from concurrent.futures import ThreadPoolExecutor      # NUEVO: el pool de hilos
from cable import URL
import gantt

def pide_v2(i, enviada, lento=0.2):                    # NUEVO: la llamada es una función
    empieza = time.perf_counter()                      # NUEVO: cuándo un hilo la toma
    gantt.registra(f"llamada {i:02d}", enviada, empieza, "lista")   # NUEVO: esperó turno
    r = requests.get(f"{URL}/ventas?lento={lento}", timeout=5)
    gantt.registra(f"llamada {i:02d}", empieza, time.perf_counter(), "espera")
    return r.status_code

def cliente_v2(n, hilos, lento=0.2):
    gantt.reinicia()
    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=hilos) as pool:      # NUEVO: hasta `hilos` a la vez
        futuros = [pool.submit(pide_v2, i, time.perf_counter(), lento)   # NUEVO: submit, no map
                   for i in range(n)]
        codigos = [f.result() for f in futuros]              # f.result() espera a ese futuro
    return codigos, time.perf_counter() - inicio

codigos4, t_h4 = cliente_v2(20, 4)
gantt.dibuja("v2 · 20 llamadas, 4 hilos")
codigos32, t_h32 = cliente_v2(20, 32)
gantt.dibuja("v2 · 20 llamadas, 32 hilos")

# %% [markdown]
# **Qué esperar.** Con 4 hilos: cinco olas de 4 barras de contorno, y las
# filas de las olas 2 a 5 empiezan con un trazo rayado (esperaron turno). Con 32:
# 20 barras casi alineadas arriba y abajo, sin rayado: todas arrancaron a la
# vez. Cada barra dura lo mismo (0.2 s): el hilo no hizo la llamada más rápida,
# la **solapó** con las otras.

# %%
assert set(codigos4) == set(codigos32) == {200}
assert t_h32 < t_h4 < 20 * 0.2          # más hilos, menos tiempo; ambos mejor que la v1
print(f"{'versión':30} {'llamadas':>8} {'tiempo (s)':>11} {'predicción (s)':>15} {'vs v1':>7}")
print(f"{'v1 for + requests':30} {20:8d} {t_v1:11.2f} {20 * 0.2:15.2f} {'1.0x':>7}")
for nombre, t, k in (("v2 hilos (k=4)", t_h4, 4), ("v2 hilos (k=32)", t_h32, 32)):
    pred = -(-20 // k) * 0.2
    print(f"{nombre:30} {20:8d} {t:11.2f} {pred:15.2f} {t_v1 / t:6.1f}x")

# %% [markdown]
# ## Paso 3 · Cálculo: 4 tareas con 1, 2 y 4 procesos
#
# Un cálculo puro de CPU es lo opuesto: no hay espera que solapar. Con hilos
# no ayudaría (el GIL deja ejecutar **un** hilo de Python a la vez por
# intérprete). Los **procesos** sí: cada uno tiene su propio intérprete y su
# propio GIL, y el sistema operativo los reparte entre las CPU.
#
# `ProcessPoolExecutor` manda a cada hijo el *nombre* de la función (módulo +
# nombre), no su código; por eso `calcula` vive en `trabajo_computo.py` y no en
# la celda. `mide(n)` incluye arrancar los procesos, que es parte del costo real.
#
# **Qué esperar.** 4 tareas idénticas: con 1 proceso T₁, con 2 aproximadamente
# T₁/2, con 4 aproximadamente T₁/4 (menos si tu máquina tiene menos de 4 CPU o
# está ocupada). Cuanto más cerca de la mitad y el cuarto, menos serial hay.

# %%
# celda 2.2
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

# %% [markdown]
# ## Paso 4 · Los mismos procesos, con Gantt y gráfica de speedup
#
# Repetimos el cálculo con `calcula_medido` (una función nueva en
# `trabajo_computo.py`, que devuelve cuándo empezó y terminó con `time.time()`:
# los procesos necesitan un reloj común). Cada tarea se dibuja como `exec`; con
# menos procesos que tareas, las que esperan una CPU libre salen como `lista`
# (desde el `submit` hasta que un proceso la toma).
#
# El **speedup** es `S(N) = T₁ / T_N` y la **eficiencia** `E(N) = S(N) / N`.
# Con `E` cerca de 1 los procesos se reparten el trabajo sin estorbarse.

# %%
# v2b: el cálculo en procesos, medido por tarea
import time
from concurrent.futures import ProcessPoolExecutor
from trabajo_computo import calcula_medido             # NUEVO: la versión que devuelve sus tiempos
import gantt

def mide_procesos(n_procesos, tareas=4, n=5_000_000):
    gantt.reinicia()
    inicio = time.perf_counter()
    with ProcessPoolExecutor(max_workers=n_procesos) as procesos:
        enviada = time.time()                                       # NUEVO: reloj común (pared)
        futuros = [procesos.submit(calcula_medido, n) for _ in range(tareas)]
        tiempos = [f.result() for f in futuros]                     # (inicio, fin, resultado)
    total = time.perf_counter() - inicio
    for i, (a, b, _) in enumerate(tiempos):                         # NUEVO: una fila por tarea
        gantt.registra(f"tarea {i}", enviada, a, "lista")
        gantt.registra(f"tarea {i}", a, b, "exec")
    return total, tiempos

tiempos_n = {}
for k in (1, 2, 4):
    tiempos_n[k], _ = mide_procesos(k)
    gantt.dibuja(f"4 tareas de cálculo con {k} proceso(s)")

# %% [markdown]
# **Qué esperar.** Con 1 proceso: una escalera de 4 barras rellenas, con las
# tres últimas precedidas de un trazo rayado (lista: esperando que el único
# proceso quede libre). Con 4 procesos: cuatro barras rellenas casi alineadas.
# Esas cuatro barras alineadas son lo que hace **paralelo** a un Gantt: dos
# `exec` en el mismo instante.

# %%
import matplotlib.pyplot as plt
Ns = (1, 2, 4)
S = {k: tiempos_n[1] / tiempos_n[k] for k in Ns}
fig, ax = plt.subplots(figsize=(5, 3.4))
ax.plot(Ns, [S[k] for k in Ns], "o-", color="#1f4e8c", label="medido")
ax.plot(Ns, Ns, "--", color="#555555", label="ideal S(N) = N")
ax.set_xticks(Ns); ax.set_xlabel("procesos N"); ax.set_ylabel("speedup S(N)")
ax.set_title("Speedup del cálculo en procesos"); ax.legend(); fig.tight_layout(); plt.show()

print(f"{'procesos N':>10} {'T_N (s)':>9} {'S(N)':>6} {'E(N)':>6}")
for k in Ns:
    print(f"{k:10d} {tiempos_n[k]:9.2f} {S[k]:6.2f} {S[k] / k:6.2f}")
assert tiempos_n[4] < tiempos_n[1], "4 procesos deberían ganarle a 1 si tienes ≥ 2 CPU libres"
assert all(0 < S[k] <= k * 1.15 for k in Ns), "el speedup no puede pasar de N (con margen de ruido)"

# %% [markdown]
# **Cómo leer la tabla.** `S(N)` casi siempre queda un poco debajo de `N`: arrancar
# procesos, mandar argumentos y recoger resultados es trabajo que no se
# reparte (la fracción serial `f` de la ley de Amdahl, página 6). Con
# `E(N)` bajando a medida que sube `N`, agregar procesos rinde cada vez menos.

# %% [markdown]
# ## Paso 5 · La carrera de datos, paso a paso (determinista)
#
# `contador += 1` no es una operación indivisible: son tres pasos
# (**leer**, **sumar**, **escribir**) y el intérprete puede cambiar de hilo
# entre dos cualesquiera. Si A y B leen el mismo valor antes de que alguno
# escriba, las dos suman sobre el valor viejo y una actualización se pierde.
#
# Para verlo sin esperar a que ocurra por azar, esta celda simula dos hilos con
# generadores (cada `yield` es un posible cambio de hilo) y fija a mano el
# orden: A lee, B lee, A escribe, B escribe.

# %%
def hilo_sim(nombre, memoria):                       # un "hilo" con 3 pasos, cada yield es un cambio posible
    actual = memoria["contador"];  yield f"{nombre} lee {actual}"
    nuevo = actual + 1;            yield f"{nombre} calcula {nuevo}"
    memoria["contador"] = nuevo;   yield f"{nombre} escribe {nuevo}"

memoria = {"contador": 0}
a, b = hilo_sim("A", memoria), hilo_sim("B", memoria)
orden = [a, b, a, b, a, b]                           # A1 B1 A2 B2 A3 B3: el peor entrelazado
print(f"{'paso':>4}  {'qué pasa':20} {'contador en memoria':>20}")
for k, g in enumerate(orden, 1):
    texto = next(g)
    print(f"{k:4d}  {texto:20} {memoria['contador']:20d}")
print("dos incrementos, resultado:", memoria["contador"])
assert memoria["contador"] == 1, "con este entrelazado se pierde una actualización"

# %% [markdown]
# **Qué pasó.** A y B leyeron `0`; A escribió `1`; B también escribió `1`. Se
# hicieron dos incrementos y el contador subió una vez. Con `sys.setswitchinterval`
# muy pequeño, la celda siguiente fuerza ese mismo tipo de entrelazado con hilos
# reales: 4 hilos × 100 000 incrementos deberían dar 400 000.

# %%
# celda 2.3
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

# %% [markdown]
# El resultado **cambia entre corridas** (es no determinista): depende de
# cuándo el intérprete cambia de hilo. Repítelo y verás otro `obtenido`, casi
# siempre menor que `esperado`. Ahora se mide cuántas actualizaciones se
# pierden en varias repeticiones, y se repite con el candado de la celda 2.4.
# Un `Lock` hace la **región crítica** (leer + escribir) indivisible: los hilos
# hacen fila para entrar, y se pierde paralelismo a propósito, pero no datos.

# %%
perdidas_sin = 400_000 - contador
print("perdidas en la corrida de la celda 2.3:", f"{perdidas_sin:,}")

# %%
# celda 2.4
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

# %% [markdown]
# **Qué esperar.** `esperado 400,000, obtenido 400,000`. Siempre. El candado no
# cuesta casi nada aquí porque la región crítica es corta; si la región crítica
# fuera todo el trabajo, los hilos quedarían secuenciales.

# %%
assert contador == 4 * 100_000
print(f"{'caso':26} {'esperado':>10} {'obtenido':>10} {'perdidas':>9}")
print(f"{'sin candado (celda 2.3)':26} {400_000:10,} {400_000 - perdidas_sin:10,} {perdidas_sin:9,}")
print(f"{'con Lock (celda 2.4)':26} {400_000:10,} {contador:10,} {400_000 - contador:9,}")
