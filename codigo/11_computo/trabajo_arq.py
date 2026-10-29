"""El cálculo de la celda 10.1 (clase 11.2), en un archivo aparte.

Mismo motivo que `trabajo_computo.py`: un ProcessPoolExecutor manda al hijo el
*nombre* de la función, y el hijo la busca importando este módulo. Una función
definida en una celda pertenece al `__main__` del kernel, que el hijo no puede
importar con spawn. Sólo usa la librería estándar.
"""
import os
import threading

N_TAREA = 1_000_000   # ~100 ms de cálculo en una CPU actual (depende de la máquina)


def tarea(i, n=N_TAREA):
    """Suma de cuadrados con un bucle de Python puro; devuelve quién la ejecutó."""
    suma = 0
    for k in range(n):
        suma += k * k
    return {"tarea": i, "pid": os.getpid(),
            "hilo": threading.current_thread().name, "suma": suma}


N_TAREA_CPU = 4_000_000   # ~0.5 s de cálculo por tarea en una CPU actual


def tarea_cpu(i, n=N_TAREA_CPU):
    """El mismo cálculo puro de `tarea`, más lo que consumió el hilo que lo ejecutó.

    `time.thread_time()` es el tiempo de CPU del hilo que la llama (en Linux,
    CLOCK_THREAD_CPUTIME_ID); la diferencia antes/después es la CPU de ESTA
    tarea, esté en un hilo, en un proceso o en un trabajador de joblib.
    """
    import time
    c0 = time.thread_time()
    suma = 0
    for k in range(n):
        suma += k * k
    return {"tarea": i, "pid": os.getpid(), "suma": suma,
            "cpu": time.thread_time() - c0}
