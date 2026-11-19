# %% [markdown]
# ## 10.1 · Quién ejecuta: 4 hilos frente a 2 procesos
#
# **Qué se va a ver.** El mismo trabajo, **4 tareas** de cálculo puro de
# Python (cada una del orden de 100 ms, según tu CPU), se manda dos veces:
#
# 1. a un `ThreadPoolExecutor` de **4 hilos** (un solo proceso);
# 2. a un `ProcessPoolExecutor` de **2 procesos**, con un contexto de arranque
#    explícito (`spawn`) para que se comporte igual en cualquier sistema.
#
# Cada tarea devuelve **quién la ejecutó**: el PID del proceso y el nombre del
# hilo. La función vive en `trabajo_arq.py` (junto a este notebook) porque el
# proceso hijo la busca **importando** ese módulo; una función definida en una
# celda no es importable por un hijo `spawn`.
#
# Lo que la celda muestra es la **pertenencia**: con hilos, un PID y varios
# nombres de hilo; con procesos, varios PID. La celda también imprime el
# número de CPU lógicas de tu máquina, que es el tope de ejecución simultánea
# del hardware. **No promete aceleración**: en CPython con GIL, 4 hilos de
# cálculo puro no corren bytecode a la vez, y 2 procesos pagan el costo de
# arrancar. La celda no compara tiempos.

# %%
# celda 10.1
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import threading

from trabajo_arq import tarea

N_TAREAS = 4
cpus = getattr(os, "process_cpu_count", os.cpu_count)()
print(f"CPU lógicas disponibles para este proceso: {cpus}")

# 1. cuatro hilos, un proceso. La barrera hace que ninguna tarea empiece su
# cálculo hasta que las 4 estén dentro de un hilo distinto (si no, un hilo
# libre podría tomar dos tareas y verías 3 nombres de hilo)
barrera = threading.Barrier(N_TAREAS, timeout=30)


def tarea_con_barrera(i):
    barrera.wait()
    return tarea(i)


with ThreadPoolExecutor(max_workers=4, thread_name_prefix="hilo") as pool:
    con_hilos = list(pool.map(tarea_con_barrera, range(N_TAREAS)))

print("\n4 hilos:")
for r in con_hilos:
    print(f"  tarea {r['tarea']}: PID {r['pid']}  hilo {r['hilo']}")
pids_h = {r["pid"] for r in con_hilos}
hilos_h = {r["hilo"] for r in con_hilos}
print(f"  -> {len(pids_h)} PID y {len(hilos_h)} nombres de hilo distintos")

# 2. dos procesos (contexto explícito)
ctx = multiprocessing.get_context("spawn")
with ProcessPoolExecutor(max_workers=2, mp_context=ctx) as pool:
    con_procesos = list(pool.map(tarea, range(N_TAREAS)))

print("\n2 procesos:")
for r in con_procesos:
    print(f"  tarea {r['tarea']}: PID {r['pid']}  hilo {r['hilo']}")
pids_p = {r["pid"] for r in con_procesos}
print(f"  -> {len(pids_p)} PID distintos (y ninguno es el del kernel: {os.getpid()})")

assert len(pids_h) == 1 and len(hilos_h) == 4
assert 1 <= len(pids_p) <= 2 and os.getpid() not in pids_p

# %% [markdown]
# ### Salida esperada de la celda 10.1
#
# - Primero el número de CPU lógicas (un entero; en la máquina del profesor, 8).
# - **4 hilos:** las cuatro tareas muestran **el mismo PID** (el del kernel) y
#   cuatro nombres de hilo distintos (`hilo_0` a `hilo_3`). Cierra con
#   «1 PID y 4 nombres de hilo distintos».
# - **2 procesos:** las cuatro tareas muestran **PID distintos del kernel**:
#   normalmente dos PID, cada uno repetido (cada proceso atendió dos tareas), y
#   el nombre de hilo es `MainThread` en ambos (cada proceso hijo ejecuta en su
#   hilo principal). Cierra con «2 PID distintos».
#
# Los valores concretos de PID cambian en cada ejecución. Si ves un solo PID
# en la segunda parte, un proceso atendió las cuatro tareas (es posible, no es
# un error); repite la celda. **Lectura.** Hilos y procesos responden a
# «quién ejecuta»; cuántos de ellos corren a la vez lo deciden además el
# planificador del sistema operativo, las CPU y el GIL, no el tamaño del pool.

# %% [markdown]
# ## 10.2 · ¿Cuántas CPU usa cada herramienta?
#
# **Qué vamos a ver.** El **mismo cálculo** (Python puro, sin esperar nada),
# repartido en **4 tareas**, se ejecuta con tres herramientas y se mide cuántas
# CPU trabajaron a la vez en cada una:
#
# 1. **4 hilos** (`ThreadPoolExecutor(4)`): un proceso, cuatro hilos.
# 2. **4 procesos** (`ProcessPoolExecutor(4)` con contexto `spawn`): cuatro
#    intérpretes de Python, cada uno con su propio GIL.
# 3. **`joblib.Parallel(n_jobs=4)`** con el backend por omisión (`loky`): una
#    librería que reparte las tareas en procesos trabajadores.
#
# **Qué medimos, con estas variables.**
#
# - **reloj** (s): lo que pasó en tu reloj de pared, medido con
#   `time.monotonic()`, desde antes de crear el pool hasta tener los resultados
#   (incluye arrancar los procesos).
# - **CPU** (s): el tiempo que las CPU estuvieron **ejecutando** nuestro
#   código, sumado entre todos los hilos o procesos. Si dos CPU trabajan un
#   segundo cada una, son 2 s de CPU en 1 s de reloj.
# - **CPU efectivas** = CPU ÷ reloj: cuántas CPU, en promedio, estuvieron
#   trabajando a la vez. Vale 1 si sólo una trabajó a la vez; vale 4 si cuatro
#   trabajaron todo el tiempo.
# - **PID distintos**: cuántos procesos distintos ejecutaron las tareas.
#
# **Cómo se mide la CPU (y por qué no es la misma llamada en los tres).**
#
# - **Hilos:** todos viven en **este** proceso, así que basta
#   `time.process_time()` (CPU de este proceso, todos sus hilos).
# - **Procesos:** `process_time()` **no** ve a los hijos (marcaría casi 0).
#   Se usa `resource.getrusage(RUSAGE_CHILDREN)`, que suma los hijos que ya
#   **terminaron y fueron esperados**; por eso se lee **después** de cerrar el
#   pool. Incluye también el costo de arrancar cada proceso.
# - **joblib (loky):** sus trabajadores **no terminan** al acabar las tareas
#   (se quedan vivos para reutilizarse), así que `RUSAGE_CHILDREN` marca 0
#   mientras sigan vivos. Aquí cada tarea mide su propia CPU con
#   `time.thread_time()` (CPU del hilo que la ejecuta) y se suman. Al final la
#   celda cierra a los trabajadores y muestra que entonces `RUSAGE_CHILDREN`
#   sí los cuenta.
#
# **Qué esperamos.**
#
# - **Hilos: CPU efectivas cerca de 1.** Aunque haya 4 hilos, el **GIL** deja
#   que sólo uno ejecute bytecode de Python a la vez. Los demás esperan el
#   candado, y esperar no consume CPU.
# - **Procesos: CPU efectivas claramente mayores que 1** (hasta 4, si tu
#   máquina tiene al menos 4 CPU). Cada proceso tiene su propio GIL. Arrancar
#   los procesos cuesta reloj, así que no llega al máximo.
# - **joblib: parecido a los procesos**, porque usa procesos. Lo que hace
#   `loky` es mantener **trabajadores reutilizables**: la segunda llamada
#   reutiliza los mismos PID sin volver a arrancar procesos. La celda la hace
#   dos veces para que lo veas.

# %%
# celda 10.2
import multiprocessing
import os
import resource
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

import joblib
from joblib.externals.loky import get_reusable_executor

from trabajo_arq import tarea_cpu

N_TAREAS = 4
print(f"os.cpu_count() = {os.cpu_count()}  (CPU lógicas de la máquina)")


def cpu_hijos():
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


def mide(nombre, trabajo, cpu_de):
    """Corre `trabajo()` y devuelve (renglón, resultados). `cpu_de` dice cómo medir la CPU."""
    reloj0, cpu0, hijos0 = time.monotonic(), time.process_time(), cpu_hijos()
    resultados = trabajo()
    reloj = time.monotonic() - reloj0
    cpu = cpu_de(resultados, time.process_time() - cpu0, cpu_hijos() - hijos0)
    pids = {r["pid"] for r in resultados}
    return (nombre, reloj, cpu, cpu / reloj, len(pids)), resultados


def con_hilos():
    with ThreadPoolExecutor(max_workers=N_TAREAS) as pool:
        return list(pool.map(tarea_cpu, range(N_TAREAS)))


def con_procesos():
    ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=N_TAREAS, mp_context=ctx) as pool:
        return list(pool.map(tarea_cpu, range(N_TAREAS)))


def con_joblib():
    return joblib.Parallel(n_jobs=N_TAREAS)(
        joblib.delayed(tarea_cpu)(i) for i in range(N_TAREAS))


filas = []
f, _ = mide("4 hilos", con_hilos, lambda r, proc, hijos: proc)
filas.append(f)
f, res_proc = mide("4 procesos", con_procesos, lambda r, proc, hijos: hijos)
filas.append(f)
hijos_antes_jl = cpu_hijos()
f, res_jl1 = mide("joblib (1.a llamada)", con_joblib,
                  lambda r, proc, hijos: sum(x["cpu"] for x in r))
filas.append(f)
f, res_jl2 = mide("joblib (2.a llamada)", con_joblib,
                  lambda r, proc, hijos: sum(x["cpu"] for x in r))
filas.append(f)
hijos_con_loky_vivo = cpu_hijos() - hijos_antes_jl   # los trabajadores de loky siguen vivos

print(f"\n{'herramienta':<22} {'reloj (s)':>9} {'CPU (s)':>8} {'CPU efectivas':>14} {'PID distintos':>14}")
for nombre, reloj, cpu, efectivas, pids in filas:
    print(f"{nombre:<22} {reloj:>9.2f} {cpu:>8.2f} {efectivas:>14.2f} {pids:>14}")

pids_1 = {x["pid"] for x in res_jl1}
pids_2 = {x["pid"] for x in res_jl2}
print(f"\njoblib: PID de la 1.a llamada {sorted(pids_1)}")
print(f"        PID de la 2.a llamada {sorted(pids_2)}  -> mismos: {pids_1 == pids_2}")

# cerrar a los trabajadores de loky: sólo entonces RUSAGE_CHILDREN los cuenta
antes = cpu_hijos()
get_reusable_executor().shutdown(wait=True)
print(f"\nRUSAGE_CHILDREN durante las 2 llamadas de joblib (trabajadores vivos): +{hijos_con_loky_vivo:.2f} s")
print(f"RUSAGE_CHILDREN tras cerrar a los trabajadores de loky             : +{cpu_hijos() - antes:.2f} s")

efectivas = {f[0]: f[3] for f in filas}
assert hijos_con_loky_vivo < 0.05 and cpu_hijos() - antes > 0.5
assert efectivas["4 hilos"] < 1.5
assert len(pids_1) <= 4 and os.getpid() not in pids_1
if (os.cpu_count() or 1) >= 4:
    assert efectivas["4 procesos"] > 1.8 and efectivas["joblib (1.a llamada)"] > 1.5

# %% [markdown]
# ### Salida esperada de la celda 10.2
#
# Primero `os.cpu_count()` (en la máquina del profesor, 8). Después una tabla
# con cuatro renglones. Los números cambian en cada máquina; lo que se
# mantiene son estos rangos:
#
# - **4 hilos:** 1 PID distinto y **CPU efectivas entre 0.8 y 1.3**. El GIL
#   dejó trabajar a un hilo a la vez: la CPU total es casi igual al reloj.
# - **4 procesos:** 4 PID distintos y **CPU efectivas entre 2 y 4** (con 4 o más
#   CPU). Menos de 4 porque arrancar los procesos consume reloj.
# - **joblib, 1.a llamada:** 4 PID distintos y **CPU efectivas entre 1.5 y 3**,
#   algo menos que los procesos: `loky` arranca sus trabajadores e importa
#   `joblib` en cada uno, y eso es reloj sin cálculo.
# - **joblib, 2.a llamada:** los **mismos PID** que la primera, y un reloj
#   **menor o igual**, porque ya no hay que arrancar procesos.
# - Las dos últimas líneas: durante las dos llamadas de joblib
#   `RUSAGE_CHILDREN` sube **+0.00 s** (los trabajadores siguen vivos, así que
#   no cuentan), y tras cerrarlos sube varios segundos (en la máquina del
#   profesor, de 7 a 9 s): todo el trabajo de las **dos** llamadas más el
#   arranque de los 4 trabajadores, que se registra hasta que terminan.
#
# Si tu máquina tiene menos de 4 CPU, «CPU efectivas» no pasa de ese número
# (la celda omite entonces la comprobación de los procesos). **Lectura.** Los
# hilos comparten el GIL y suman casi una CPU; los procesos (con
# `ProcessPoolExecutor` o con `joblib`) tienen un GIL cada uno y suman varias.
# `joblib` no es otro mecanismo: es una forma cómoda de usar procesos que
# además los conserva entre llamadas.
