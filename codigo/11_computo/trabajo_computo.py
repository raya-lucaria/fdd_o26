"""El cálculo de la unidad 11 (cómputo y concurrencia), en un archivo aparte.

¿Por qué no vive en una celda del notebook? Porque un ProcessPoolExecutor
manda a cada proceso hijo el *nombre* de la función (módulo + nombre, con
pickle), no su código. El hijo la busca importando ese módulo. Una función
definida en una celda pertenece a `__main__` del kernel, que el hijo no puede
importar cuando arranca con spawn o forkserver (macOS, Windows, y Linux desde
Python 3.14): la llamada truena (ver `BrokenProcessPool` en la página del GIL,
9.2). Con fork (Linux hasta 3.13) el hijo hereda la memoria y sí funciona,
pero eso depende del sistema y de la versión. Desde este archivo, el hijo hace
`import trabajo_computo` y la encuentra con cualquier método de arranque.

Sólo usa la librería estándar: no toca la red ni el disco, sólo calcula.
"""

N_POR_OMISION = 20_000_000   # ~2 s en la máquina del profesor


def calcula(n=N_POR_OMISION):
    """Suma los cuadrados de 0 a n - 1 con un bucle de Python puro.

    Es determinista (mismo n, mismo resultado) y todo su tiempo es CPU: el
    bucle corre dentro del intérprete. El bucle bloquea el event loop, pero el
    intérprete permite que otros hilos adquieran el GIL.
    """
    suma = 0
    for i in range(n):
        suma += i * i
    return suma


def calcula_medido(n=N_POR_OMISION):
    """Como `calcula`, pero también devuelve cuándo empezó y terminó.

    Usa `time.time()` (reloj de pared del sistema) porque el proceso hijo y el
    notebook son procesos distintos y necesitan un reloj común para dibujar el
    mismo Gantt. Devuelve (inicio, fin, resultado).
    """
    import time
    inicio = time.time()
    resultado = calcula(n)
    return inicio, time.time(), resultado
