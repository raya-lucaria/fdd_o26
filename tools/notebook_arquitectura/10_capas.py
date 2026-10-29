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
