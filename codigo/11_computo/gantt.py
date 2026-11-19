"""Un Gantt medido de verdad, para las celdas del notebook de la unidad 11.

Uso: cada vez que una tarea cambia de estado, anota el intervalo con
`registra(nombre, inicio, fin, tipo)` (los tiempos son segundos de CUALQUIER
reloj, pero el mismo en todas las anotaciones de un dibujo: `time.perf_counter()`
o `loop.time()`). Al final, `dibuja(titulo)` pinta una fila por tarea.

Convención de la notación de la unidad (A_notacion):

    exec     relleno      la tarea ejecuta instrucciones en una CPU
    espera   contorno     espera algo de fuera del programa (red, disco, reloj)
    lista    rayado       puede ejecutar, pero no tiene hilo/CPU todavía
    permiso  ámbar        espera un permiso de otra tarea del programa
                          (Semaphore, Lock, conexión del pool)

Los intervalos son semiabiertos [inicio, fin): dos barras que se tocan no se
solapan. Sólo depende de matplotlib.
"""
import threading

_TIPOS = ("exec", "espera", "lista", "permiso")
_AZUL = "#1f4e8c"
_AMBAR = "#f2b134"
_GRIS = "#555555"

_registros = []
_candado = threading.Lock()      # los hilos del notebook registran a la vez


def reinicia():
    """Borra todo lo registrado: empieza un dibujo nuevo."""
    with _candado:
        _registros.clear()


def registra(nombre, inicio, fin, tipo):
    """Anota que la tarea `nombre` estuvo en el estado `tipo` en [inicio, fin)."""
    if tipo not in _TIPOS:
        raise ValueError(f"tipo {tipo!r}: debe ser uno de {_TIPOS}")
    if fin < inicio:
        raise ValueError(f"fin {fin} < inicio {inicio} en {nombre!r}")
    with _candado:
        _registros.append((str(nombre), float(inicio), float(fin), tipo))


def registros():
    """Copia de lo registrado: lista de (nombre, inicio, fin, tipo)."""
    with _candado:
        return list(_registros)


def dibuja(titulo=""):
    """Pinta el Gantt de lo registrado (una fila por nombre, en orden de aparición)."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    datos = registros()
    if not datos:
        raise ValueError("no hay nada registrado: llama a registra() primero")
    t0 = min(d[1] for d in datos)
    filas = []
    for nombre, *_ in sorted(datos, key=lambda d: d[1]):
        if nombre not in filas:
            filas.append(nombre)
    fig, ax = plt.subplots(figsize=(9, 0.32 * len(filas) + 1.6))
    for nombre, ini, fin, tipo in datos:
        y = filas.index(nombre)
        ancho = max(fin - ini, 1e-4)             # una barra de 0 s no se vería
        estilo = {
            "exec": dict(facecolor=_AZUL, edgecolor=_AZUL),
            "espera": dict(facecolor="white", edgecolor=_AZUL, linewidth=1.2),
            "lista": dict(facecolor="white", edgecolor=_GRIS, hatch="////"),
            "permiso": dict(facecolor=_AMBAR, edgecolor="#8a5a00"),
        }[tipo]
        ax.barh(y, ancho, left=ini - t0, height=0.7, **estilo)
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels(filas, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("segundos desde el primer evento")
    ax.set_title(titulo)
    ax.legend(handles=[
        Patch(facecolor=_AZUL, edgecolor=_AZUL, label="exec"),
        Patch(facecolor="white", edgecolor=_AZUL, label="espera"),
        Patch(facecolor="white", edgecolor=_GRIS, hatch="////", label="lista"),
        Patch(facecolor=_AMBAR, edgecolor="#8a5a00", label="permiso"),
    ], loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=4, frameon=False)
    fig.tight_layout()
    plt.show()
    return fig
