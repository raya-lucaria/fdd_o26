"""Genera los diagramas SVG de la unidad 11 (Computo y concurrencia).

Las primitivas y la paleta salen de tools/svg_base.py: un solo lugar declara
los colores de skins/fdd-eva.yaml.

Este archivo es la unica fuente de verdad de esos SVG. Editar un .svg a mano es
un error que tools/test_gen_computo.py detecta.

Los esquemas se reconstruyen desde fdd_p26/clase/16_computo/scripts/
generar_graficas.py con tiempos constantes, no medidos: no dependen de ninguna
maquina. Las cinco Gantt de comparacion usan las MISMAS tres tareas (ejecuta
20 ms, espera 200 ms, ejecuta 20 ms) y la misma escala de 0 a 800 ms, para que
se comparen a simple vista.

Convencion grafica de todas las Gantt (la fija A_notacion.md): ejecuta (exec)
relleno, espera (wait) contorno, lista (ready) rayado, intervalos semiabiertos
(el tramo siguiente empieza en el mismo x en que acaba el anterior) y una fila
por CPU. La espera de un permiso de semaforo es una espera (wait) con su propio
contorno ambar, distinto del cian de la red.

Los ids llevan prefijo "cmp-" a proposito: los ids de objeto numerado de Raya
son unicos en TODO el curso, no por pagina.
"""
import sys
from collections import deque
from pathlib import Path

from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, ROJO, SUAVE, TEXTO, TINTE,
    VIOLETA, caja, cierre, flecha, marco, teclado, texto,
)

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/11_computo_y_concurrencia/_assets"

# Las tres tareas de todas las Gantt: ejecuta, espera la red, ejecuta.
EJECUTA_MS = 20
ESPERA_MS = 200

ANCHO = 1080
X0 = 190          # inicio del area de tiempo
X1 = 1040         # fin del area de tiempo

# Relleno rayado del estado «lista» (ready): puede avanzar, no tiene CPU.
RAYADO = (
    '<defs><pattern id="rayado" width="8" height="8" patternUnits="userSpaceOnUse" '
    'patternTransform="rotate(45)">'
    f'<rect x="0" y="0" width="8" height="8" fill="{PANEL}"/>'
    f'<line x1="0" y1="0" x2="0" y2="8" stroke="{VIOLETA}" stroke-width="3"/>'
    '</pattern></defs>'
)


def _marco(ancho, alto, aria):
    """marco() de svg_base mas el patron rayado de «lista»."""
    return marco(ancho, alto, aria) + RAYADO


def _ancho(s, tam=13):
    """Ancho aproximado de un texto en system-ui."""
    return len(s) * tam * 0.56


def _rect(x, y, w, h, relleno, borde="none", grosor=0, guiones=None, radio=3):
    extra = f' stroke-dasharray="{guiones}"' if guiones else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 3):.1f}" height="{h}" '
            f'rx="{radio}" fill="{relleno}" stroke="{borde}" '
            f'stroke-width="{grosor}"{extra}/>')


def _linea(x1, y1, x2, y2, color=LINEA, grosor=1.2, guiones=None):
    extra = f' stroke-dasharray="{guiones}"' if guiones else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{grosor}"{extra}/>')


def _segmento(tipo, x, y, w, h, rotulo=None, rotular=True):
    """Un tramo de una fila de la Gantt, con su texto si cabe."""
    p = []
    medio = y + h / 2 + 5

    def pon(defecto, minimo, color, respaldo=False, tam=13, peso="normal"):
        s = rotulo or defecto
        if rotular and w > max(minimo, _ancho(s, tam) + 16):
            if respaldo:
                ancho = _ancho(s, tam) + 12
                p.append(_rect(x + (w - ancho) / 2, y + 4, ancho, h - 8, FONDO, radio=4))
            p.append(texto(x + w / 2, medio, s, color, tam, peso=peso))

    if tipo == "ejecuta":
        p.append(_rect(x, y, w, h, ACENTO))
        if rotulo:
            pon(rotulo, 0, FONDO, peso="600")
    elif tipo == "espera":
        p.append(_rect(x, y, w, h, PANEL, CIAN, 1.6, "6 4"))
        pon("espera la red: CPU libre", 120, CIAN)
    elif tipo == "permiso":
        p.append(_rect(x, y, w, h, PANEL, AMBAR, 2, "2 3"))
        pon("espera permiso", 120, AMBAR)
    elif tipo == "lista":
        p.append(_rect(x, y, w, h, "url(#rayado)", VIOLETA, 1.4))
        if rotulo:
            pon(rotulo, 60, TEXTO, respaldo=True)
    elif tipo == "bloquea":
        p.append(_rect(x, y, w, h, ROJO))
        pon("calcula 2000 ms sin await", 200, FONDO, tam=14, peso="600")
    elif tipo == "inerte":
        p.append(_rect(x, y, w, h, "none", SUAVE, 1.4, "3 3"))
        pon("", 0, SUAVE)
    return "".join(p)


LEYENDA = [
    ("ejecuta", "ejecuta: usa la CPU"),
    ("espera", "espera: red o disco, CPU libre"),
    ("lista", "lista: puede seguir, espera turno"),
    ("inactiva", "CPU inactiva"),
]


def _leyenda(y, items):
    """Leyenda en renglones; regresa (svg, numero de renglones)."""
    p, x, renglones = [], X0 - 150, 1
    for tipo, rotulo in items:
        paso = 48 + len(rotulo) * 7.2
        if x + paso > ANCHO - 20:
            x, y, renglones = X0 - 150, y + 28, renglones + 1
        if tipo == "inactiva":
            p.append(_rect(x, y - 13, 30, 16, "none", SUAVE, 1.4, "3 3"))
        else:
            p.append(_segmento(tipo, x, y - 13, 30, 16))
        p.append(texto(x + 40, y, rotulo, TEXTO, 13, anclaje="start"))
        x += paso
    return "".join(p), renglones


def _nota_fila(p, segmentos, nota, y, xs, alto_barra=26, x_notas=None):
    """El porqué de una fila, en texto junto a sus tramos.

    nota: texto a la derecha del último tramo (o en la columna x_notas), o
    ("izq", texto) a la izquierda del primero. Falla si el texto no cabe:
    un rótulo que se sale del viewBox no se lee.
    """
    if not nota:
        return
    medio = y + alto_barra / 2 + 5
    if isinstance(nota, tuple):
        _, s = nota
        x = xs(min(ini for _, ini, *_ in segmentos)) - 10
        assert x - _ancho(s) >= X0, f"nota izquierda no cabe: {s!r}"
        p.append(_rect(x - _ancho(s) - 4, y + 4, _ancho(s) + 8, alto_barra - 8, FONDO, radio=2))
        p.append(texto(x, medio, s, SUAVE, 13, anclaje="end"))
        return
    x = x_notas if x_notas is not None else xs(max(fin for _, _, fin, *_ in segmentos)) + 12
    assert x + _ancho(nota) <= ANCHO - 16, f"nota derecha no cabe: {nota!r}"
    # Fondo bajo el texto: la rejilla y la marca del total no lo cruzan.
    p.append(_rect(x - 4, y + 4, _ancho(nota) + 8, alto_barra - 8, FONDO, radio=2))
    p.append(texto(x, medio, nota, SUAVE, 13, anclaje="start"))


def _filas(p, filas, arriba, xs, escala, alto_fila=42, alto_barra=26, x_notas=None):
    """Filas de tareas: [(etiqueta, [(tipo, ini, fin[, rotulo]), ...][, nota])]."""
    for i, (etiqueta, segmentos, *nota) in enumerate(filas):
        y = arriba + i * alto_fila
        assert _ancho(etiqueta, 14) <= X0 - 36, f"etiqueta larga: {etiqueta!r}"
        p.append(texto(X0 - 16, y + alto_barra / 2 + 5, etiqueta, TEXTO, 14,
                       anclaje="end"))
        for tipo, ini, fin, *rotulo in segmentos:
            p.append(_segmento(tipo, xs(ini), y, (fin - ini) * escala, alto_barra,
                               rotulo[0] if rotulo else None))
        _nota_fila(p, segmentos, nota[0] if nota else None, y, xs, alto_barra, x_notas)


def _fila_cpu(p, y, etiqueta, ocupados, total, xs, escala, bloqueo=False,
              alto_barra=26):
    """Fila de una CPU: tramos ocupados (ini, fin, rotulo) e inactiva el resto.

    El rótulo de cada tramo nombra a la tarea con su prefijo (T1, P1, main):
    nunca un dígito suelto, que se confunde con el número de la CPU. Si no
    cabe dentro de la barra va debajo de ella.
    """
    p.append(texto(X0 - 16, y + alto_barra / 2 + 5, etiqueta, ACENTO, 14,
                   anclaje="end", peso="600"))
    cursor = 0
    for ini, fin, rotulo in sorted(ocupados) + [(total, total, None)]:
        if ini > cursor:
            w = (ini - cursor) * escala
            p.append(_rect(xs(cursor), y + 3, w, alto_barra - 6, "none",
                           SUAVE, 1.4, "3 3"))
            if w > 90:
                p.append(texto(xs(cursor) + w / 2, y + alto_barra / 2 + 5,
                               "inactiva", SUAVE, 13))
        if rotulo is not None:
            assert not rotulo.isdigit(), f"rótulo de CPU sin prefijo: {rotulo!r}"
            color = ROJO if rotulo.startswith("T3") and bloqueo else ACENTO
            w = (fin - ini) * escala
            p.append(_rect(xs(ini), y, w, alto_barra, color))
            if w >= max(18, len(rotulo) * 8 + 4):
                p.append(texto(xs(ini) + w / 2, y + alto_barra / 2 + 5,
                               rotulo, FONDO, 13, peso="600"))
            elif rotulo:
                p.append(texto(xs(ini) + w / 2, y + alto_barra + 14,
                               rotulo, ACENTO, 13, peso="600"))
        cursor = max(cursor, fin)


def _eje(p, y_eje, eje_max, paso, xs):
    p.append(_linea(X0, y_eje, X1, y_eje, SUAVE, 1.4))
    for ms in range(0, eje_max + 1, paso):
        p.append(_linea(xs(ms), y_eje, xs(ms), y_eje + 6, SUAVE, 1.4))
        p.append(texto(xs(ms), y_eje + 24, str(ms), SUAVE, 13))
    p.append(texto(X0 - 16, y_eje + 24, "tiempo (ms)", SUAVE, 13, anclaje="end"))


def _marca_total(p, total, xs, arriba, y_eje, rotulo=None):
    xt = xs(total)
    s = rotulo or f"total {total} ms"
    p.append(_linea(xt, arriba - 16, xt, y_eje, AMBAR, 2, "6 4"))
    a_la_derecha = xt + _ancho(s, 14) + 16 < ANCHO - 16
    p.append(texto(xt + (8 if a_la_derecha else -8), arriba - 6, s,
                   AMBAR, 14, anclaje="start" if a_la_derecha else "end", peso="600"))


def _gantt(titulo, subtitulo, aria, filas, cpus, total, nota, cuenta=None,
           eje_max=800, paso=100, bloqueo=False, leyenda=None, extra=None,
           x_notas=None):
    """Gantt comun: filas de tareas, filas de CPU, eje en ms, leyenda y nota.

    filas: [(etiqueta, [(tipo, ini_ms, fin_ms[, rotulo]), ...][, nota])]
    cpus:  [(etiqueta, [(ini_ms, fin_ms, rotulo), ...])]
    cuenta: la linea que explica el total, en ambar como la marca del total.
    extra: funcion (xs, y_fila) -> svg que se dibuja encima (flechas, notas).
    """
    for s, tam in ((titulo, 20), (subtitulo, 14), (nota, 14), (cuenta or "", 14)):
        assert _ancho(s, tam) <= ANCHO - 40, f"no cabe en {ANCHO}: {s!r}"
    escala = (X1 - X0) / eje_max

    def xs(ms):
        return X0 + ms * escala

    alto_fila, alto_barra = 42, 26
    arriba = 112
    y_cpu = arriba + len(filas) * alto_fila + 14
    y_eje = y_cpu + len(cpus) * alto_fila + 8
    y_ley = y_eje + 64
    if leyenda is None:
        leyenda = list(LEYENDA)
        if bloqueo:
            leyenda[3] = ("bloquea", "calcula dentro del loop")
    svg_ley, renglones = _leyenda(y_ley, leyenda)
    y_cuenta = y_ley + (renglones - 1) * 28 + 36
    y_nota = y_cuenta + (28 if cuenta else 0)
    alto = y_nota + (24 if nota else -6)

    p = [_marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42, titulo, TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 70, subtitulo, SUAVE, 14))

    # Rejilla vertical de fondo.
    for ms in range(0, eje_max + 1, paso):
        p.append(_linea(xs(ms), arriba - 6, xs(ms), y_eje, LINEA, 0.6, "2 6"))

    if x_notas is None:
        # Columna comun de notas despues de la marca del total, si caben.
        derechas = [f[2] for f in filas if len(f) > 2 and isinstance(f[2], str)]
        if derechas and xs(total) + 14 + max(map(_ancho, derechas)) <= ANCHO - 16:
            x_notas = xs(total) + 14
    _filas(p, filas, arriba, xs, escala, alto_fila, alto_barra, x_notas)

    p.append(_linea(X0 - 170, y_cpu - 8, X1, y_cpu - 8, LINEA, 1))
    for j, (etiqueta, ocupados) in enumerate(cpus):
        _fila_cpu(p, y_cpu + j * alto_fila, etiqueta, ocupados, total, xs, escala,
                  bloqueo, alto_barra)

    _eje(p, y_eje, eje_max, paso, xs)
    _marca_total(p, total, xs, arriba, y_eje)
    if extra:
        p.append(extra(xs, lambda i: arriba + i * alto_fila))

    p.append(svg_ley)
    if cuenta:
        p.append(texto(ANCHO / 2, y_cuenta, cuenta, AMBAR, 14, peso="600"))
    if nota:
        p.append(texto(ANCHO / 2, y_nota, nota, TEXTO, 14))
    p.append(cierre())
    return "".join(p)


def _tarea(inicio_ejecuta, espera_desde=None, lista=None, segunda=None):
    """Tramos de una tarea: ejecuta 20, espera 200, (lista), ejecuta 20."""
    e1 = (inicio_ejecuta, inicio_ejecuta + EJECUTA_MS)
    w0 = e1[1] if espera_desde is None else espera_desde
    w1 = w0 + ESPERA_MS
    s0 = w1 if segunda is None else segunda
    tramos = [("ejecuta", *e1), ("espera", w0, w1)]
    if s0 > w1:
        tramos.append(("lista", w1, s0))
    tramos.append(("ejecuta", s0, s0 + EJECUTA_MS))
    if lista:
        tramos.insert(0, ("lista", *lista))
    return tramos


SUBTITULO = "las mismas 3 tareas: ejecuta 20 ms, espera 200 ms la red, ejecuta 20 ms"


def _leyenda_de(ejecuta, espera, lista, inactiva="CPU inactiva: nadie la usa"):
    """Leyenda de las Gantt de comparacion, con el porque de cada estado."""
    return [("ejecuta", ejecuta), ("espera", espera), ("lista", lista),
            ("inactiva", inactiva)]


def _secuenciales(etiqueta):
    """Tres tareas en serie; la fila de CPU nombra a cada tarea con su prefijo."""
    filas, cpu = [], []
    for i in range(3):
        t0 = i * (2 * EJECUTA_MS + ESPERA_MS)
        nota = ("izq", f"empieza cuando T{i} termina") if i else None
        filas.append((etiqueta(i + 1), _tarea(t0), nota))
        cpu += [(t0, t0 + EJECUTA_MS, f"T{i + 1}"),
                (t0 + EJECUTA_MS + ESPERA_MS, t0 + 2 * EJECUTA_MS + ESPERA_MS, f"T{i + 1}")]
    return filas, cpu


def _intercaladas(etiqueta, notas):
    """Tres tareas que se turnan una CPU: el patron de hilos y de asyncio."""
    filas, cpu = [], []
    for i in range(3):
        t0 = i * EJECUTA_MS
        lista = (0, t0) if t0 else None
        filas.append((etiqueta(i + 1), _tarea(t0, lista=lista), notas[i]))
        s0 = t0 + EJECUTA_MS + ESPERA_MS
        cpu += [(t0, t0 + EJECUTA_MS, f"T{i + 1}"), (s0, s0 + EJECUTA_MS, f"T{i + 1}")]
    return filas, cpu


def cmp_gantt_secuencial():
    filas, cpu = _secuenciales(lambda k: f"T{k}")
    aria = (
        "Diagrama de Gantt con eje de tiempo en milisegundos de 0 a 800. Tres "
        "tareas en serie, T1, T2 y T3: cada una ejecuta 20 ms, espera 200 ms "
        "la red y ejecuta 20 ms; T2 no empieza hasta que T1 termina, en 240 "
        "ms, y T3 hasta que termina T2, en 480 ms. La unica CPU rotula cada "
        "tramo con la tarea que la usa y queda inactiva durante las tres "
        "esperas. Total 720 ms: 3 por (20 + 200 + 20)."
    )
    return _gantt(
        "Secuencial: una tarea termina antes de que empiece la siguiente",
        SUBTITULO, aria, filas, [("CPU", cpu)], 720,
        "La CPU trabaja 120 ms de 720: el resto del tiempo nadie la usa.",
        cuenta="T3 empieza cuando T2 termina: 3 × (20 + 200 + 20) = 720 ms.",
        leyenda=_leyenda_de("ejecuta: la tarea usa la única CPU",
                            "espera: la red, CPU libre",
                            "lista: puede seguir, espera turno (aquí no hay)"),
    )


def cmp_gantt_hilos():
    filas, cpu = _intercaladas(lambda k: f"T{k} · hilo {k}", (
        "toma el GIL primero; al esperar la red lo suelta",
        "lista 0–20 ms: el hilo 1 tiene el GIL",
        "lista 0–40 ms: el GIL lo tienen el hilo 1 y luego el 2",
    ))
    aria = (
        "Diagrama de Gantt con eje de tiempo en milisegundos de 0 a 800. Las "
        "mismas tres tareas, T1 a T3, una por hilo. Las tres esperas de 200 ms "
        "se solapan. La ejecucion se turna por el GIL: T2 queda lista, en "
        "rayado, de 0 a 20 ms porque el hilo 1 tiene el GIL, y T3 de 0 a 40 "
        "ms. La fila de CPU rotula T1, T2 o T3 segun que hilo tiene el GIL y "
        "nunca tiene dos tramos a la vez. Total 280 ms: 40 + 20 + 200 + 20."
    )
    return _gantt(
        "Hilos: las esperas se solapan, la ejecución se turna por el GIL",
        SUBTITULO, aria, filas, [("CPU (GIL)", cpu)], 280,
        "280 ms contra 720: se gana porque se espera a la vez, no porque se calcule a la vez.",
        cuenta="T3 espera el GIL 40 ms y luego ejecuta, espera y ejecuta: 40 + 20 + 200 + 20 = 280 ms.",
        leyenda=_leyenda_de("ejecuta: el hilo tiene el GIL y usa la CPU",
                            "espera: la red; el hilo suelta el GIL",
                            "lista: puede seguir; otro hilo tiene el GIL"),
    )


def cmp_gantt_asyncio():
    filas, cpu = _intercaladas(lambda k: f"T{k} · corrutina", (
        "corre primero; su await cede el loop",
        "lista 0–20 ms: el loop atiende a T1",
        "lista 0–40 ms: el loop atiende a T1 y luego a T2",
    ))
    aria = (
        "Diagrama de Gantt con eje de tiempo en milisegundos de 0 a 800. Las "
        "mismas tres tareas, T1 a T3, como corrutinas en el hilo del loop, "
        "lanzadas juntas con gather. Cada corrutina ejecuta 20 ms hasta su "
        "await y cede el loop; T2 queda lista, en rayado, de 0 a 20 ms "
        "mientras el loop atiende a T1, y T3 de 0 a 40 ms. Las tres esperas "
        "de 200 ms se solapan. Total 280 ms, igual que con hilos y sin ningun "
        "hilo extra."
    )
    return _gantt(
        "asyncio con gather: un hilo, cada await cede el turno",
        SUBTITULO, aria, filas, [("hilo del loop", cpu)], 280,
        "Mismo total que con hilos. La diferencia es quién decide el turno: el await, no el sistema.",
        cuenta="T3 espera su turno 40 ms y luego ejecuta, espera y ejecuta: 40 + 20 + 200 + 20 = 280 ms.",
        leyenda=_leyenda_de("ejecuta: corre en el hilo del loop (usa la CPU)",
                            "espera: la red; cedió el loop con await",
                            "lista: puede seguir; el loop atiende a otra"),
    )


def cmp_gantt_await_en_serie():
    filas, cpu = _secuenciales(lambda k: f"T{k} · corrutina")
    aria = (
        "Diagrama de Gantt con eje de tiempo en milisegundos de 0 a 800. El "
        "anti patron: tres corrutinas, T1 a T3, con await una tras otra, sin "
        "gather. Cada await espera su respuesta completa antes de lanzar la "
        "siguiente llamada: T2 no empieza hasta que T1 termina y el dibujo es "
        "identico al secuencial. El hilo del loop queda inactivo durante las "
        "tres esperas de 200 ms. Total 720 ms: 3 por (20 + 200 + 20)."
    )
    return _gantt(
        "await uno tras otro: async en el código, secuencial en el reloj",
        SUBTITULO, aria, filas, [("hilo del loop", cpu)], 720,
        "Mientras T1 espera, nadie más está lanzado: el loop no tiene a quién dar el turno.",
        cuenta="Cada await espera la respuesta completa: 3 × (20 + 200 + 20) = 720 ms.",
        leyenda=_leyenda_de("ejecuta: corre en el hilo del loop (usa la CPU)",
                            "espera: la red; nadie más está lanzado",
                            "lista: puede seguir, espera turno (aquí no hay)",
                            "inactiva: el loop no tiene a quién correr"),
    )


def cmp_gantt_procesos():
    # Tres procesos sobre dos CPU: el tercero espera una CPU libre.
    filas = [
        ("P1 · CPU 1", _tarea(0), "ejecuta en la CPU 1"),
        ("P2 · CPU 2", _tarea(0), "ejecuta en la CPU 2, a la vez que P1"),
        ("P3 · CPU 1", _tarea(20, lista=(0, 20), segunda=240),
         "lista 0–20 ms: CPU 1 y 2 ocupadas; luego usa la CPU 1"),
    ]
    cpu1 = [(0, 20, "P1"), (20, 40, "P3"), (220, 240, "P1"), (240, 260, "P3")]
    cpu2 = [(0, 20, "P2"), (220, 240, "P2")]
    aria = (
        "Diagrama de Gantt con eje de tiempo en milisegundos de 0 a 800. Las "
        "mismas tres tareas en tres procesos, P1, P2 y P3, sobre dos CPU. P1 "
        "ejecuta en la CPU 1 y P2 en la CPU 2 al mismo tiempo; P3 queda lista, "
        "en rayado, de 0 a 20 ms porque las dos CPU estan ocupadas, y luego "
        "ejecuta en la CPU 1. Las filas de CPU rotulan cada tramo con P1, P2 "
        "o P3. Total 260 ms: 20 + 20 + 200 + 20."
    )
    return _gantt(
        "Procesos: dos CPU ejecutan al mismo tiempo",
        SUBTITULO, aria, filas, [("CPU 1", cpu1), ("CPU 2", cpu2)], 260,
        "260 ms contra 280 de hilos: con tareas que esperan, el paralelismo casi no rinde.",
        cuenta="P3 espera 20 ms una CPU libre y ejecuta en la CPU 1: 20 + 20 + 200 + 20 = 260 ms.",
        leyenda=_leyenda_de("ejecuta: el proceso usa la CPU de su fila",
                            "espera: la red, CPU libre",
                            "lista: puede seguir; las 2 CPU están ocupadas"),
    )


# ── Página 1: estados e intervalos ─────────────────────────────────────────

def _estado_caja(cx, cy, w, nombre, simbolo, estilo, borde):
    """Caja de un estado con una muestra del relleno que usa en la Gantt."""
    h = 76
    p = [caja(cx - w / 2, cy - h / 2, w, h, PANEL, borde, radio=12)]
    p.append(texto(cx, cy - 8, nombre, borde, 17, peso="600"))
    if estilo:
        p.append(_segmento(estilo, cx - 44, cy + 8, 30, 16, rotular=False))
        p.append(teclado(cx - 6, cy + 22, simbolo, SUAVE, 14, anclaje="start",
                         peso="normal"))
    else:
        p.append(texto(cx, cy + 22, simbolo, SUAVE, 13))
    return "".join(p)


def cmp_estados_tarea():
    ancho, alto = ANCHO, 530
    aria = (
        "Diagrama de estados de una tarea. Nueva pasa a lista cuando se crea "
        "y se agenda. De lista pasa a ejecutando cuando le dan la CPU, y de "
        "ejecutando puede volver a lista si pierde el turno. De ejecutando "
        "pasa a esperando cuando pide red, disco o un sleep con await, y de "
        "esperando vuelve a lista cuando llega el dato o vence el temporizador. "
        "De ejecutando pasa a terminada con return. Cada estado lleva la "
        "muestra de su relleno en la Gantt: ejecuta relleno, espera contorno, "
        "lista rayado."
    )
    p = [_marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Los estados de una tarea: quién avanza, quién espera y quién no tiene turno",
                   TEXTO, 20, peso="600"))
    p.append(texto(ancho / 2, 70,
                   "una tarea vive en uno solo a la vez; la Gantt pinta cada estado con su relleno",
                   SUAVE, 14))
    cy = 180
    p.append(_estado_caja(105, cy, 150, "nueva", "aún sin agendar", None, SUAVE))
    p.append(_estado_caja(360, cy, 170, "lista", "ready", "lista", VIOLETA))
    p.append(_estado_caja(660, cy, 190, "ejecutando", "exec", "ejecuta", ACENTO))
    p.append(_estado_caja(955, cy, 150, "terminada", "end: fin de la vida", None, SUAVE))
    cy2 = 380
    p.append(_estado_caja(510, cy2, 200, "esperando", "wait", "espera", CIAN))

    # nueva -> lista
    p.append(flecha(180, cy, 275, cy, LINEA, 2))
    p.append(texto(228, cy - 10, "se agenda", SUAVE, 13))
    # lista <-> ejecutando
    p.append(flecha(445, cy - 14, 565, cy - 14, ACENTO, 2))
    p.append(texto(505, cy - 24, "le dan CPU", ACENTO, 13))
    p.append(flecha(565, cy + 14, 445, cy + 14, VIOLETA, 2))
    p.append(texto(505, cy + 36, "pierde el turno", VIOLETA, 13))
    # ejecutando -> terminada
    p.append(flecha(755, cy, 880, cy, LINEA, 2))
    p.append(teclado(818, cy - 10, "return", SUAVE, 14, peso="normal"))
    # ejecutando -> esperando
    p.append(flecha(650, cy + 38, 575, cy2 - 38, CIAN, 2))
    p.append(texto(628, 290, "await: pide red,", CIAN, 13, anclaje="start"))
    p.append(texto(628, 308, "disco o un sleep", CIAN, 13, anclaje="start"))
    # esperando -> lista
    p.append(flecha(445, cy2 - 38, 370, cy + 38, VIOLETA, 2))
    p.append(texto(392, 290, "llega el dato o", VIOLETA, 13, anclaje="end"))
    p.append(texto(392, 308, "vence el timer", VIOLETA, 13, anclaje="end"))

    p.append(caja(40, 446, ancho - 80, 66, TINTE, AMBAR, radio=8))
    p.append(texto(ancho / 2, 472,
                   "La prueba: si ahora le das una CPU libre, ¿avanza? Sí: está lista. No: está esperando.",
                   AMBAR, 15, peso="600"))
    p.append(texto(ancho / 2, 496,
                   "Pierde el turno por el GIL o el sistema; en asyncio solo cede en un await, nunca a la fuerza.",
                   TEXTO, 14))
    p.append(cierre())
    return "".join(p)


def _punto(x, y, cerrado, color):
    relleno = color if cerrado else FONDO
    return (f'<circle cx="{x:.1f}" cy="{y}" r="6" fill="{relleno}" '
            f'stroke="{color}" stroke-width="2.5"/>')


def cmp_intervalos():
    ancho, alto = ANCHO, 566
    eje_max, paso = 480, 40
    escala = (X1 - X0) / eje_max

    def xs(ms):
        return X0 + ms * escala

    aria = (
        "Dos tareas en serie sobre un eje de 0 a 480 ms. La vida de T1 es el "
        "intervalo semiabierto de 0 a 240, cerrado en 0 y abierto en 240; la de "
        "T2 va de 240 a 480. En 240 T1 tiene un punto hueco y T2 un punto "
        "lleno: el instante 240 pertenece solo a T2, asi que las dos vidas se "
        "tocan pero no se solapan y la traza es secuencial. Cada vida se parte "
        "en ejecuta 20, espera 200 y ejecuta 20 ms, sin tramo lista."
    )
    p = [_marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Intervalos semiabiertos: dos vidas que se tocan no se solapan",
                   TEXTO, 20, peso="600"))
    p.append(texto(ancho / 2, 70, "[a, b) incluye a y excluye b; el tramo siguiente empieza en el mismo x",
                   SUAVE, 14))
    arriba, alto_fila = 150, 74
    y_eje = arriba + 2 * alto_fila + 4
    for ms in range(0, eje_max + 1, paso):
        p.append(_linea(xs(ms), arriba - 40, xs(ms), y_eje, LINEA, 0.6, "2 6"))
    for i, (nombre, t0, color) in enumerate((("T1", 0, ACENTO), ("T2", 240, CIAN))):
        y = arriba + i * alto_fila
        _filas(p, [(nombre, _tarea(t0))], y, xs, escala)
        # La vida arriba de la fila: corchete con punto lleno al inicio, hueco al fin.
        yv = y - 14
        p.append(_linea(xs(t0), yv, xs(t0 + 240), yv, color, 2.5))
        p.append(_punto(xs(t0), yv, True, color))
        p.append(_punto(xs(t0 + 240), yv, False, color))
        rotulo = f"vida({nombre}) = [{t0}, {t0 + 240})"
        p.append(teclado(xs(t0 + 120), yv - 10, rotulo, color, 14))
    _eje(p, y_eje, eje_max, paso, xs)

    # El instante del borde.
    xb = xs(240)
    p.append(_linea(xb, arriba - 46, xb, y_eje, AMBAR, 2, "6 4"))
    p.append(texto(xb, arriba - 52, "t = 240", AMBAR, 14, peso="600"))

    p.append(caja(40, 356, ancho - 80, 186, PANEL, LINEA, radio=8))
    lineas = (
        (AMBAR, "600", "En t = 240: 240 no está en [0, 240) y sí en [240, 480). Corta una sola vida."),
        (TEXTO, "normal", "La traza es secuencial: ningún instante pertenece a las dos vidas."),
        (TEXTO, "normal", "Con intervalos cerrados, [0, 240] y [240, 480] compartirían t = 240"),
        (TEXTO, "normal", "y dos tareas en serie contarían como concurrentes."),
        (ACENTO, "600", "vida(T1) = exec ∪ wait ∪ ready, disjuntos: 20 + 200 + 20 = 240 ms (ready vacío)."),
    )
    for k, (color, peso, s) in enumerate(lineas):
        p.append(texto(ancho / 2, 390 + k * 34, s, color, 15, peso=peso))
    p.append(cierre())
    return "".join(p)


# ── Página 2: conjuntos y el servidor de la clase ─────────────────────────

def _mini(p, x, y, filas, escala, etiquetas=True):
    """Gantt diminuta sin texto en las barras, para ilustrar una region."""
    for i, (nombre, segmentos) in enumerate(filas):
        yy = y + i * 22
        if etiquetas:
            p.append(texto(x - 8, yy + 13, nombre, SUAVE, 13, anclaje="end"))
        for tipo, ini, fin in segmentos:
            p.append(_segmento(tipo, x + ini * escala, yy, (fin - ini) * escala, 16,
                               rotular=False))


def cmp_conjuntos():
    ancho, alto = ANCHO, 580
    aria = (
        "Diagrama de conjuntos de trazas de un mismo grupo de tareas. A la "
        "izquierda, secuencial: ningun par de vidas se solapa, con una mini "
        "Gantt de T1 y luego T2. A la derecha, concurrente: algun par de vidas "
        "se solapa, con T1 y T2 intercaladas en una CPU como hilos con GIL o "
        "asyncio. Dentro de concurrente, la region paralelo: dos tareas "
        "ejecutan en el mismo instante en dos CPU, como procesos. Secuencial y "
        "concurrente no se tocan; paralelo implica concurrente."
    )
    p = [_marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Secuencial o concurrente; lo paralelo es una parte de lo concurrente",
                   TEXTO, 20, peso="600"))
    p.append(texto(ancho / 2, 70, "las mismas tareas, la misma granularidad: cada traza cae en una sola región",
                   SUAVE, 14))
    p.append(caja(30, 92, ancho - 60, 352, "none", LINEA, radio=14))
    p.append(texto(50, 116, "todas las trazas posibles", SUAVE, 13, anclaje="start"))

    # Secuencial.
    p.append(caja(50, 132, 330, 296, PANEL, SUAVE, radio=12))
    p.append(texto(215, 168, "secuencial", TEXTO, 19, peso="600"))
    p.append(texto(215, 194, "ningún par de vidas se solapa", SUAVE, 13))
    _mini(p, 100, 230, [
        ("T1", [("ejecuta", 0, 10), ("espera", 10, 50), ("ejecuta", 50, 60)]),
        ("T2", [("ejecuta", 60, 70), ("espera", 70, 110), ("ejecuta", 110, 120)]),
    ], 2.2)
    p.append(texto(215, 320, "un for con requests", TEXTO, 14))
    p.append(texto(215, 342, "await uno tras otro", TEXTO, 14))

    # Concurrente.
    p.append(caja(410, 132, 620, 296, PANEL, CIAN, radio=12))
    p.append(texto(560, 168, "concurrente", CIAN, 19, peso="600"))
    p.append(texto(560, 194, "algún par de vidas se solapa", SUAVE, 13))
    _mini(p, 470, 230, [
        ("T1", [("ejecuta", 0, 10), ("espera", 10, 50), ("ejecuta", 50, 60)]),
        ("T2", [("lista", 0, 10), ("ejecuta", 10, 20), ("espera", 20, 60), ("ejecuta", 60, 70)]),
    ], 2.4)
    p.append(texto(560, 320, "hilos con GIL", TEXTO, 14))
    p.append(texto(560, 342, "asyncio con gather", TEXTO, 14))
    p.append(texto(560, 372, "se turnan una CPU", SUAVE, 13))

    # Paralelo, dentro de concurrente.
    p.append(caja(720, 152, 290, 256, TINTE, ACENTO, radio=12))
    p.append(texto(865, 186, "paralelo", ACENTO, 19, peso="600"))
    p.append(texto(865, 210, "dos tareas ejecutan", SUAVE, 13))
    p.append(texto(865, 228, "en el mismo instante", SUAVE, 13))
    _mini(p, 820, 250, [
        ("CPU 1", [("ejecuta", 0, 10), ("espera", 10, 50), ("ejecuta", 50, 60)]),
        ("CPU 2", [("ejecuta", 0, 10), ("espera", 10, 50), ("ejecuta", 50, 60)]),
    ], 2.4)
    p.append(texto(865, 330, "procesos en 2 o más CPU", TEXTO, 14))
    p.append(texto(865, 352, "una CPU por tarea", SUAVE, 13))

    p.append(caja(30, 462, ancho - 60, 96, TINTE, AMBAR, radio=8))
    p.append(texto(ancho / 2, 490,
                   "Paralelo ⇒ concurrente: si T1 y T2 ejecutan en el mismo t, ese t está en las dos vidas.",
                   AMBAR, 15, peso="600"))
    p.append(texto(ancho / 2, 516,
                   "«Paralelo sin concurrente» no existe con las mismas tareas: es un cambio de granularidad.",
                   TEXTO, 14))
    p.append(texto(ancho / 2, 540,
                   "Asíncrono no es una región de este dibujo: es cómo cede el hilo quien espera.",
                   TEXTO, 14))
    p.append(cierre())
    return "".join(p)


def cmp_arq_servidor_clase():
    ancho, alto = ANCHO, 600
    aria = (
        "Arquitectura del servidor de la clase, un ThreadingHTTPServer en el "
        "puerto 8026. A la izquierda n clientes, cada uno con su conexion TCP. "
        "Llegan a un socket que escucha con una cola listen de 1024 conexiones "
        "pendientes, que por omision serian 5. El hilo principal hace accept "
        "en serve_forever y crea un hilo por conexion, sin tope. Todos los "
        "hilos comparten el diccionario de ventas y lo tocan solo dentro de "
        "with candado, un unico Lock: esa region critica corre de a un hilo."
    )
    p = [_marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "El servidor de la clase: un hilo por conexión y un solo candado",
                   TEXTO, 20, peso="600"))
    p.append(teclado(ancho / 2, 70, "servidor.py · ThreadingHTTPServer · puerto 8026", SUAVE, 14,
                     peso="normal"))

    ys = (120, 178, 236, None, 330)     # None: los puntos suspensivos
    # Clientes.
    p.append(texto(100, 106, "clientes", SUAVE, 13))
    for k, y in enumerate(ys):
        if y is None:
            p.append(texto(100, 300, "…", SUAVE, 18))
            continue
        nombre = f"cliente {k + 1}" if k < 3 else "cliente n"
        p.append(caja(30, y, 140, 44, PANEL, LINEA, radio=8))
        p.append(texto(100, y + 27, nombre, TEXTO, 14))
        p.append(flecha(170, y + 22, 220, y + 22, LINEA, 1.6))
    p.append(texto(100, 400, "una conexión TCP", SUAVE, 13))
    p.append(texto(100, 418, "cada uno", SUAVE, 13))

    # Socket que escucha con su cola.
    p.append(caja(222, 110, 216, 270, PANEL, CIAN, radio=10))
    p.append(texto(330, 136, "socket que escucha", CIAN, 14, peso="600"))
    for k in range(6):
        p.append(_rect(285, 156 + k * 30, 90, 22, FONDO, CIAN, 1.2, radio=4))
    p.append(texto(330, 172, "pendiente", SUAVE, 13))
    p.append(texto(330, 352, "cola listen", TEXTO, 14))
    p.append(teclado(330, 372, "request_queue_size = 1024", CIAN, 13, peso="normal"))
    p.append(texto(330, 400, "por omisión serían 5", SUAVE, 13))

    # Hilo principal.
    p.append(flecha(438, 245, 470, 245, LINEA, 2))
    p.append(caja(472, 200, 170, 90, PANEL, AMBAR, radio=10))
    p.append(texto(557, 226, "hilo principal", AMBAR, 15, peso="600"))
    p.append(teclado(557, 252, "serve_forever()", TEXTO, 14, peso="normal"))
    p.append(teclado(557, 274, "accept()", TEXTO, 14, peso="normal"))

    # Un hilo por conexión.
    p.append(texto(790, 106, "un hilo por conexión, sin tope", ACENTO, 14, peso="600"))
    for k, y in enumerate(ys):
        if y is None:
            p.append(texto(790, 300, "…", SUAVE, 18))
            continue
        nombre = f"hilo {k + 1}" if k < 3 else "hilo n"
        p.append(flecha(642, 245, 718, y + 22, AMBAR, 1.6))
        p.append(caja(720, y, 140, 44, TINTE, ACENTO, radio=8))
        p.append(texto(732, y + 27, nombre, ACENTO, 14, anclaje="start", peso="600"))
        p.append(teclado(850, y + 27, "do_GET", TEXTO, 13, anclaje="end", peso="normal"))
        p.append(flecha(860, y + 22, 918, 236, VIOLETA, 1.4))
    p.append(texto(600, 330, "crea uno", AMBAR, 13))
    p.append(texto(600, 348, "por conexión", AMBAR, 13))

    # El candado y el estado compartido.
    p.append(teclado(985, 170, "with candado:", VIOLETA, 13, peso="normal"))
    p.append(caja(920, 186, 130, 100, PANEL, VIOLETA, radio=10))
    p.append(texto(985, 214, "candado", VIOLETA, 15, peso="600"))
    p.append(teclado(985, 240, "Lock()", TEXTO, 14, peso="normal"))
    p.append(texto(985, 266, "uno solo", SUAVE, 13))
    p.append(flecha(985, 286, 985, 318, VIOLETA, 2))
    p.append(caja(920, 320, 130, 60, PANEL, LINEA, radio=10))
    p.append(teclado(985, 346, "ventas", TEXTO, 14, peso="normal"))
    p.append(texto(985, 368, "dict compartido", SUAVE, 13))

    p.append(caja(30, 446, ancho - 60, 130, TINTE, AMBAR, radio=8))
    notas = (
        (AMBAR, "600", "Conexiones abiertas del cliente = hilos ocupados del servidor."),
        (TEXTO, "normal", "?lento=0.2 duerme fuera del candado: las esperas de varios hilos se solapan."),
        (TEXTO, "normal", "Dentro de with candado entra un hilo a la vez: región crítica, serialización deliberada."),
        (SUAVE, "normal", "Memoria compartida: todos los hilos ven el mismo dict; por eso el candado."),
    )
    for k, (color, peso, s) in enumerate(notas):
        p.append(texto(ancho / 2, 474 + k * 28, s, color, 15 if k == 0 else 14, peso=peso))
    p.append(cierre())
    return "".join(p)


# ── Página 3: asíncrono, event loop, create_task ───────────────────────────

def cmp_matriz_asincrono():
    ancho, alto = 1080, 620
    aria = (
        "Matriz de dos por dos. Filas: modelo de escritura bloqueante, con "
        "requests o time.sleep, o asincrono, con async y await. Columnas: la "
        "traza no es concurrente o si lo es. Bloqueante y no concurrente: "
        "secuencial, 720 ms. Bloqueante y concurrente: hilos, 280 ms. "
        "Asincrono y no concurrente: await uno tras otro, 720 ms. Asincrono y "
        "concurrente: gather en un hilo, 280 ms. Las cuatro celdas existen: "
        "asincrono describe el codigo, concurrente describe la traza."
    )
    p = [_marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Asíncrono y concurrente son dos preguntas distintas",
                   TEXTO, 20, peso="600"))
    x0, y0, w, h = 320, 136, 350, 170
    p.append(texto(x0 + w, 88, "¿la traza es concurrente? (alguna vida se solapa)", SUAVE, 14))
    p.append(texto(x0 + w / 2, 120, "no", TEXTO, 15, peso="600"))
    p.append(texto(x0 + w * 1.5, 120, "sí", TEXTO, 15, peso="600"))
    p.append(texto(170, y0 - 20, "¿cómo está escrito", SUAVE, 14))
    p.append(texto(170, y0 - 2, "el código?", SUAVE, 14))
    for fila, (nombre, ejemplo) in enumerate((("bloqueante", "requests, time.sleep"),
                                              ("asíncrono", "async def, await"))):
        yc = y0 + h * (fila + 0.5)
        p.append(texto(300, yc - 4, nombre, TEXTO, 15, anclaje="end", peso="600"))
        p.append(teclado(300, yc + 18, ejemplo, SUAVE, 13, anclaje="end", peso="normal"))

    celdas = (
        (0, 0, SUAVE, "secuencial", ["un for: una llamada", "tras otra"], "720 ms"),
        (1, 0, CIAN, "hilos", ["ThreadPoolExecutor:", "el sistema reparte el turno"], "280 ms"),
        (0, 1, AMBAR, "await en serie", ["async en el código,", "un await tras otro"], "720 ms"),
        (1, 1, ACENTO, "gather", ["un hilo; quien espera", "cede con await"], "280 ms"),
    )
    for col, fila, color, nombre, lineas, total in celdas:
        x, y = x0 + col * w, y0 + fila * h
        p.append(caja(x + 6, y + 6, w - 12, h - 12, PANEL, color))
        p.append(texto(x + w / 2, y + 46, nombre, color, 20, peso="600"))
        for k, linea in enumerate(lineas):
            p.append(texto(x + w / 2, y + 80 + k * 22, linea, TEXTO, 14))
        p.append(texto(x + w / 2, y + 144, f"3 tareas: {total}", SUAVE, 13))

    p.append(caja(60, y0 + 2 * h + 22, ancho - 120, 100, TINTE, AMBAR, radio=8))
    p.append(texto(ancho / 2, y0 + 2 * h + 52,
                   "Asíncrono: la llamada regresa antes del resultado y quien espera cede el hilo.",
                   AMBAR, 15, peso="600"))
    p.append(texto(ancho / 2, y0 + 2 * h + 78,
                   "Es propiedad del código. Concurrente es propiedad de la traza: se ve en el Gantt.",
                   TEXTO, 14))
    p.append(texto(ancho / 2, y0 + 2 * h + 102,
                   "Escribir async no basta: sin gather ni create_task, las esperas no se solapan.",
                   TEXTO, 14))
    p.append(cierre())
    return "".join(p)


# Traza de gather(A, B, C): cada una ejecuta 10 ms, duerme d y ejecuta 10 ms.
DUERME_MS = {"A": 300, "B": 100, "C": 200}


def _traza_ticks():
    """Columnas de la traza (anexo C §4), derivadas de DUERME_MS."""
    vence = {}
    t = 0
    for nombre in "ABC":            # tick 1: cada una hasta su sleep
        t += 10
        vence[nombre] = t + DUERME_MS[nombre]
    orden = sorted(vence, key=vence.get)        # B, C, A
    fin = vence[orden[-1]] + 10
    esperan = [(n, vence[n]) for n in "ABC"]
    cols = [
        dict(tick="tick 0", t="0 ms", listas=["main"], corre=["main"],
             espera=[], main=True, nota=("gather crea", "A, B, C")),
        dict(tick="tick 1", t=f"0–{t} ms", listas=list("ABC"), corre=list("ABC"),
             espera=esperan, main=True, nota=("cada una corre", "hasta su sleep")),
        dict(tick="select", t=f"{t}–{vence[orden[0]]} ms", listas=[], corre=[],
             espera=[e for e in esperan if e[0] != orden[0]], main=True,
             nota=("CPU libre:", f"duerme {vence[orden[0]] - t} ms")),
    ]
    quedan = [e for e in esperan if e[0] != orden[0]]
    for k, nombre in enumerate(orden):
        quedan = [e for e in quedan if e[0] != nombre]
        ultima = k == len(orden) - 1
        cols.append(dict(
            tick=f"tick {k + 2}", t=f"{vence[nombre]} ms", listas=[nombre], corre=[nombre],
            espera=quedan, main=not ultima,
            nota=(f"{nombre} termina" + (":" if ultima else ""),
                  "gather listo" if ultima else "")))
    cols.append(dict(tick=f"tick {len(orden) + 2}", t=f"{fin} ms", listas=["main"],
                     corre=["main"], espera=[], main=False,
                     nota=("recibe", "[rA, rB, rC]")))
    cpu = [(0, 10, "A"), (10, 20, "B"), (20, 30, "C")]
    cpu += [(vence[n], vence[n] + 10, n) for n in orden]
    cpu.append((fin, fin + 2, ""))
    return cols, cpu, fin


def _ficha(x, y, nombre, estilo):
    """Ficha de una tarea en un carril: regresa (svg, ancho)."""
    w = 28 if len(nombre) == 1 else 52
    if estilo == "ejecuta":
        r = _rect(x, y, w, 26, ACENTO, radio=6)
        color = FONDO
    elif estilo == "lista":
        r = _rect(x, y, w, 26, FONDO, VIOLETA, 2, radio=6)
        color = VIOLETA
    else:
        r = _rect(x, y, w, 26, PANEL, CIAN, 1.6, "4 3", radio=6)
        color = CIAN
    return r + texto(x + w / 2, y + 18, nombre, color, 15, peso="600"), w


def _fichas(cx, y, nombres, estilo, flechas=False):
    anchos = [28 if len(n) == 1 else 52 for n in nombres]
    hueco = 18 if flechas else 6
    total = sum(anchos) + hueco * (len(nombres) - 1)
    x = cx - total / 2
    p = []
    for k, n in enumerate(nombres):
        svg, w = _ficha(x, y, n, estilo)
        p.append(svg)
        x += w
        if flechas and k < len(nombres) - 1:
            p.append(texto(x + hueco / 2, y + 18, "→", TEXTO, 13))
        x += hueco
    return "".join(p)


def cmp_event_loop_ticks():
    ancho, alto = ANCHO, 656
    cols, cpu, fin = _traza_ticks()
    aria = (
        "Traza del event loop, tick por tick, de gather con tres tareas A, B "
        "y C: cada una ejecuta 10 ms, duerme con await asyncio.sleep y "
        "ejecuta 10 ms; A duerme 300 ms, B 100 y C 200. Tres carriles: "
        "ejecutando, cola de listas y esperando con su vencimiento. En el tick "
        "1 corren A, B y C hasta su sleep; de 30 a 120 ms el loop duerme en "
        "select con la CPU libre; en 120 termina B, en 230 C y en 310 A; en "
        "320 main recibe los resultados en el orden de los argumentos. Abajo, "
        "el hilo del loop en tiempo real; A fija el total: 10 + 300 + 10 = 320 ms."
    )
    p = [_marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "El event loop, tick por tick: quién corre, quién está lista, quién espera",
                   TEXTO, 20, peso="600"))
    p.append(texto(ancho / 2, 70,
                   "gather(A, B, C): cada una ejecuta 10 ms, await asyncio.sleep(d), ejecuta 10 ms; "
                   "dA = 300, dB = 100, dC = 200 ms", SUAVE, 14))
    xc0, xc1 = 210, 1060
    cw = (xc1 - xc0) / len(cols)
    carriles = (
        ("ejecutando", ("en el hilo del loop,", "de a una, en orden"), "ejecuta", 142, 52),
        ("cola de listas", ("al abrir el tick;", "esperan turno del loop"), "lista", 200, 52),
        ("esperando", ("timer: vence en (ms)", "main: espera a gather"), "espera", 258, 104),
    )
    y_top, y_bot = 92, 404
    for k, c in enumerate(cols):
        x = xc0 + k * cw
        if c["tick"] == "select":
            p.append(_rect(x + 2, y_top, cw - 4, y_bot - y_top, PANEL, radio=6))
        if k:
            p.append(_linea(x, y_top, x, y_bot, LINEA, 0.8, "2 5"))
        p.append(texto(x + cw / 2, 110, c["tick"], TEXTO if c["tick"] != "select" else SUAVE,
                       15, peso="600"))
        p.append(texto(x + cw / 2, 130, c["t"], SUAVE, 13))
    for nombre, sub, estilo, y, h in carriles:
        p.append(_linea(20, y - 3, xc1, y - 3, LINEA, 0.8))
        p.append(_segmento(estilo, 20, y + 6, 18, 16, rotular=False))
        p.append(texto(46, y + 19, nombre, TEXTO, 15, anclaje="start", peso="600"))
        for j, s in enumerate(sub):
            assert 46 + _ancho(s) <= xc0, s
            p.append(texto(46, y + 35 + j * 15, s, SUAVE, 13, anclaje="start"))

    for k, c in enumerate(cols):
        cx = xc0 + (k + 0.5) * cw
        # Ejecutando.
        if c["corre"]:
            p.append(_fichas(cx, 154, c["corre"], "ejecuta", flechas=True))
        else:
            p.append(texto(cx, 172, "nadie", SUAVE, 13))
        # Cola de listas.
        if c["listas"]:
            p.append(_fichas(cx, 212, c["listas"], "lista"))
        else:
            p.append(texto(cx, 230, "vacía", SUAVE, 13))
        # Esperando: tareas con su vencimiento y main debajo.
        if c["espera"]:
            nombres = [n for n, _ in c["espera"]]
            p.append(_fichas(cx, 266, nombres, "espera"))
            total = len(nombres) * 28 + 6 * (len(nombres) - 1)
            x = cx - total / 2
            for _, v in c["espera"]:
                p.append(texto(x + 14, 308, str(v), SUAVE, 13))
                x += 34
        if c["main"]:
            p.append(_fichas(cx, 322, ["main"], "espera"))
        if not c["espera"] and not c["main"]:
            p.append(texto(cx, 290, "nadie", SUAVE, 13))
        # Qué pasó.
        for j, s in enumerate(c["nota"]):
            if s:
                p.append(texto(cx, 376 + j * 18, s, TEXTO, 13))

    # Fila de CPU en tiempo real.
    eje_max, paso = 350, 50
    escala = (X1 - X0) / eje_max

    def xs(ms):
        return X0 + ms * escala

    y_cpu = 452
    for ms in range(0, eje_max + 1, paso):
        p.append(_linea(xs(ms), y_cpu - 24, xs(ms), y_cpu + 44, LINEA, 0.6, "2 6"))
    _fila_cpu(p, y_cpu, "hilo del loop", cpu, fin + 2, xs, escala)
    rotulos = ((15, "ticks 0, 1"), (125, "tick 2"), (235, "tick 3"), (316, "ticks 4, 5"))
    for ms, s in rotulos:
        p.append(texto(xs(ms), y_cpu - 8, s, ACENTO, 13))
    _eje(p, y_cpu + 44, eje_max, paso, xs)

    p.append(caja(40, 540, ancho - 80, 98, TINTE, AMBAR, radio=8))
    p.append(texto(ancho / 2, 568,
                   f"gather devuelve [rA, rB, rC] en {fin} ms: el orden de los argumentos, no el de llegada (B, C, A).",
                   AMBAR, 15, peso="600"))
    p.append(texto(ancho / 2, 594,
                   f"A, la que más duerme, fija el total: corre 10 ms, duerme {DUERME_MS['A']} y corre 10: "
                   f"10 + {DUERME_MS['A']} + 10 = {fin} ms.",
                   AMBAR, 14, peso="600"))
    p.append(texto(ancho / 2, 620,
                   f"La CPU trabaja 60 ms de {fin}: entre ticks el loop duerme en select hasta el próximo vencimiento.",
                   TEXTO, 14))
    p.append(cierre())
    return "".join(p)


def cmp_create_task():
    ancho = ANCHO
    eje_max, paso = 140, 20
    escala = (X1 - X0) / eje_max

    def xs(ms):
        return X0 + ms * escala

    aria = (
        "Dos Gantt en un hilo, eje de 0 a 140 ms. En ambas main ejecuta de 0 a "
        "20 ms, crea f en 10 ms, cede con await asyncio.sleep de 20 a 120 ms y "
        "ejecuta de 120 a 130. Arriba, c igual a f sin create_task: la "
        "corrutina es un objeto inerte que nunca corre ni entra a la cola de "
        "listas. Abajo, create_task de f: f queda lista, en rayado, de 10 a "
        "20 ms, ejecuta de 20 a 30, espera 50 ms y ejecuta de 80 a 90, aunque "
        "main nunca la espera con await."
    )
    main = [("ejecuta", 0, 20), ("espera", 20, 120, "await asyncio.sleep(0.1): espera un timer, cede el hilo"),
            ("ejecuta", 120, 130)]
    paneles = (
        ("c = f()", "crea el objeto corrutina: no entra a la cola de listas",
         [("main", main), ("f()", [("inerte", 10, 140,
                                     "objeto inerte: nunca corre (al final Python avisa «never awaited»)")])],
         [(0, 20, "main"), (120, 130, "main")]),
        ("t = asyncio.create_task(f())", "f queda lista de 10 a 20 ms (el loop corre main) y corre cuando main cede",
         [("main", main), ("f()", [("lista", 10, 20), ("ejecuta", 20, 30),
                                   ("espera", 30, 80, "espera un timer de 50 ms"), ("ejecuta", 80, 90)])],
         [(0, 20, "main"), (20, 30, "f"), (80, 90, "f"), (120, 130, "main")]),
    )
    y_eje = 112 + 2 * 170 + 4
    leyenda = _leyenda_de("ejecuta: corre en el hilo del loop (usa la CPU)",
                          "espera: un timer o la red, CPU libre",
                          "lista: puede seguir; el loop corre a otra")
    svg_ley, renglones = _leyenda(y_eje + 64, leyenda)
    y_cuenta = y_eje + 100 + (renglones - 1) * 28
    alto = y_cuenta + 28 + 24
    p = [_marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "create_task agenda la corrutina; llamarla sola no la corre",
                   TEXTO, 20, peso="600"))
    p.append(texto(ancho / 2, 70,
                   "main crea f en 10 ms y cede en 20 ms; f ejecuta 10 ms, espera 50 ms, ejecuta 10 ms",
                   SUAVE, 14))
    for ms in range(0, eje_max + 1, paso):
        p.append(_linea(xs(ms), 100, xs(ms), y_eje, LINEA, 0.6, "2 6"))
    for k, (codigo, explica, filas, cpu) in enumerate(paneles):
        arriba = 112 + k * 170
        p.append(teclado(40, arriba + 4, codigo, ACENTO if k else AMBAR, 16, anclaje="start"))
        p.append(texto(40 + _ancho(codigo, 16) * 1.1 + 24, arriba + 4, explica, TEXTO, 14,
                       anclaje="start"))
        _filas(p, filas, arriba + 18, xs, escala)
        p.append(_linea(X0 - 170, arriba + 18 + 2 * 42 + 4, X1, arriba + 18 + 2 * 42 + 4, LINEA, 1))
        _fila_cpu(p, arriba + 18 + 2 * 42 + 12, "hilo del loop", cpu, eje_max, xs, escala)
        if k:
            p.append(texto(xs(90) + 12, arriba + 18 + 42 + 18, "aunque nadie haga await t",
                           ACENTO, 13, anclaje="start"))
    _eje(p, y_eje, eje_max, paso, xs)
    p.append(svg_ley)
    p.append(texto(ancho / 2, y_cuenta,
                   "main termina en 130 ms: 20 + 100 de sleep + 10; f corre entera dentro del sleep de main.",
                   AMBAR, 14, peso="600"))
    p.append(texto(ancho / 2, y_cuenta + 28,
                   "Sin create_task, gather ni await, una corrutina no corre: crearla no la agenda.",
                   TEXTO, 14))
    p.append(cierre())
    return "".join(p)


# ── Página 4: gather y Semaphore ───────────────────────────────────────────

def cmp_gantt_gather():
    # main crea las tres Task en 10 ms y espera; cada T ejecuta 20, espera 200, ejecuta 20.
    filas = [
        ("main", [("ejecuta", 0, 10), ("espera", 10, 290, "espera a gather: no ocupa CPU"),
                  ("ejecuta", 290, 300)], "fan-in: termina T3 (290 ms)"),
        ("T1", [("ejecuta", 10, 30), ("espera", 30, 230), ("ejecuta", 230, 250)],
         "corre primero"),
        ("T2", [("lista", 10, 30), ("ejecuta", 30, 50), ("espera", 50, 250), ("ejecuta", 250, 270)],
         "lista: el loop corre T1"),
        ("T3", [("lista", 10, 50), ("ejecuta", 50, 70), ("espera", 70, 270), ("ejecuta", 270, 290)],
         "lista: corre T1, luego T2"),
    ]
    cpu = [(0, 10, "main"), (10, 30, "T1"), (30, 50, "T2"), (50, 70, "T3"),
           (230, 250, "T1"), (250, 270, "T2"), (270, 290, "T3"), (290, 300, "main")]
    aria = (
        "Diagrama de Gantt de gather con tres tareas, eje de 0 a 400 ms. Main "
        "ejecuta 10 ms y crea T1, T2 y T3 en un solo tick: fan out. Cada tarea "
        "ejecuta 20 ms, espera 200 ms la red y ejecuta 20 ms; T2 queda lista "
        "mientras el loop corre T1, y T3 mientras corren T1 y T2. Las tres "
        "esperas se solapan. Main espera sin CPU hasta que termina T3, la "
        "ultima, en 290 ms: fan in. Recibe los resultados y termina en 300 ms."
    )

    def extra(xs, y_fila):
        p = [flecha(xs(10), y_fila(0) + 26, xs(10), y_fila(3) - 2, TEXTO, 2),
             texto(xs(10) + 8, y_fila(0) + 40, "fan-out", TEXTO, 13, anclaje="start", peso="600"),
             flecha(xs(290), y_fila(3), xs(290), y_fila(0) + 28, TEXTO, 2)]
        return "".join(p)

    return _gantt(
        "gather: fan-out en un tick, esperas solapadas, fan-in al terminar la última",
        "main y 3 tareas: cada una ejecuta 20 ms, espera 200 ms la red, ejecuta 20 ms",
        aria, filas, [("hilo del loop", cpu)], 300,
        "El total lo pone la vida más larga, no la suma: 300 ms contra 720 en serie.",
        cuenta="T3 empieza en 50 ms (tras main, T1 y T2): 50 + 20 + 200 + 20 = 290; "
               "main recibe y termina en 300 ms.",
        eje_max=400, paso=50, extra=extra, x_notas=X0 + 300 * (X1 - X0) / 400 + 16,
        leyenda=_leyenda_de("ejecuta: corre en el hilo del loop (usa la CPU)",
                            "espera: la red; cedió el loop con await",
                            "lista: puede seguir; el loop corre a otra"),
    )


SEM_N, SEM_K = 8, 3


def _simula_semaforo(n=SEM_N, k=SEM_K):
    """Un event loop con Semaphore(k): n tareas que ejecutan 20, esperan 200, ejecutan 20.

    Reglas de asyncio: la cola de listas es FIFO; release() despierta a la
    primera en la cola del semaforo durante el mismo paso; los temporizadores
    vencidos entran a listas despues, en orden de vencimiento.
    Regresa (filas, cpu, total).
    """
    tramos = {i: [] for i in range(n)}
    listas = deque((i, 0) for i in range(n))     # (tarea, desde cuando esta lista)
    fase = {i: 0 for i in range(n)}               # 0: primer exec, 1: segundo exec
    tiene = set()
    cola_sem = deque()
    libres = k
    timers = []
    cpu = []
    t = 0
    while listas or timers:
        if not listas:
            t = max(t, min(v for v, _ in timers))
        else:
            i, desde = listas.popleft()
            if desde < t:
                tramos[i].append(("lista", desde, t))
            if i not in tiene:
                if libres == 0:
                    cola_sem.append((i, t))
                    continue
                libres -= 1
                tiene.add(i)
            tramos[i].append(("ejecuta", t, t + EJECUTA_MS))
            cpu.append((t, t + EJECUTA_MS, f"T{i + 1}"))
            t += EJECUTA_MS
            if fase[i] == 0:
                fase[i] = 1
                tramos[i].append(("espera", t, t + ESPERA_MS))
                timers.append((t + ESPERA_MS, i))
            else:
                if cola_sem:
                    j, desde_j = cola_sem.popleft()
                    tramos[j].append(("permiso", desde_j, t, f"espera que T{i + 1} salga"))
                    tiene.add(j)
                    listas.append((j, t))
                else:
                    libres += 1
        for v, j in sorted(x for x in timers if x[0] <= t):
            timers.remove((v, j))
            listas.append((j, v))
    filas = [(f"T{i + 1}", tramos[i]) for i in range(n)]
    return filas, cpu, t


def cmp_gantt_semaforo():
    filas, cpu, total = _simula_semaforo()
    cota = -(-SEM_N // SEM_K) * (2 * EJECUTA_MS + ESPERA_MS)
    aria = (
        f"Diagrama de Gantt de {SEM_N} tareas con Semaphore({SEM_K}) en un event loop, "
        "eje de 0 a 800 ms. Cada tarea ejecuta 20 ms, espera 200 ms la red y "
        "ejecuta 20 ms. T1, T2 y T3 toman los tres permisos; T4 a T8 quedan "
        "listas hasta su turno y luego en espera de permiso, un contorno ambar "
        "distinto de la espera de red en cian. Cada vez que una tarea sale "
        "suelta su permiso y entra la siguiente de la cola. Nunca hay mas de "
        f"tres esperas de red a la vez. Total {total} ms."
    )
    leyenda = [
        ("ejecuta", "ejecuta: corre en el hilo del loop"),
        ("espera", "espera: la red, CPU libre"),
        ("permiso", f"espera permiso del semáforo: los {SEM_K} están tomados"),
        ("lista", "lista: puede seguir; el loop corre a otra"),
        ("inactiva", "CPU inactiva: nadie la usa"),
    ]
    # El porqué de cada fila (las cifras salen de la simulación con 8 y 3).
    notas = {
        "T1": "toma el primer permiso",
        "T2": "lista: el loop corre T1; en 240, T4",
        "T3": "lista: corre T1 y T2; en 260, T2",
        "T4": "T4 a T8 listas 0–60: corren T1 a T3",
        "T5": "lista en 280: el loop corre T3",
        "T6": "lista: corre T5, luego T8",
    }
    filas = [(n, tramos, notas.get(n)) for n, tramos in filas]
    ultima, (_, tramos_ultima) = SEM_N, filas[-1][:2]
    entra = next(ini for tipo, ini, *_ in tramos_ultima if tipo == "ejecuta")
    sale = next(r[0] for tipo, _, _, *r in tramos_ultima if tipo == "permiso").split()[2]
    return _gantt(
        f"Semaphore({SEM_K}): a lo más {SEM_K} tareas dentro; las demás esperan permiso",
        f"{SEM_N} tareas: ejecuta 20 ms, espera 200 ms la red, ejecuta 20 ms; un solo hilo",
        aria, filas, [("hilo del loop", cpu)], total,
        f"⌈{SEM_N}/{SEM_K}⌉ · (20 + 200 + 20) = {cota} ms de estimación; "
        f"los turnos del único hilo suman {total - cota}: total {total} ms.",
        cuenta=f"T{ultima} entra cuando {sale} sale, en {entra} ms: "
               f"{entra} + 20 + 200 + 20 = {total} ms.",
        leyenda=leyenda,
    )


def cmp_flujo_semaforo():
    ancho, alto = ANCHO, 560
    aria = (
        "Diagrama de flujo de async with sem con un Semaphore de k permisos. "
        "La tarea llega y pregunta si el contador es mayor que cero. Si si, "
        "resta uno y entra; dentro hace su await de la peticion sin soltar el "
        "permiso; al salir suma uno y, si hay cola, despierta a la primera. Si "
        "no, se forma en la cola de espera FIFO hasta que la despiertan. A la "
        "derecha, un ejemplo con k igual a 3: el contador baja a 0 y T4 espera "
        "en la cola hasta que T1 sale."
    )
    p = [_marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Semaphore(k): un contador de permisos y una cola de espera",
                   TEXTO, 20, peso="600"))
    p.append(teclado(ancho / 2, 72, "async with sem:  await cliente.get(url)", SUAVE, 15,
                     peso="normal"))

    def nodo(x, y, w, h, borde, l1, l2=None, mono=False, relleno=PANEL):
        out = [caja(x, y, w, h, relleno, borde, radio=10)]
        titulo = TEXTO if borde == LINEA else borde
        out.append(texto(x + w / 2, y + (26 if l2 else h / 2 + 6), l1, titulo, 15, peso="600"))
        if l2:
            f = teclado if mono else texto
            out.append(f(x + w / 2, y + 48, l2, TEXTO, 13, peso="normal"))
        return "".join(out)

    p.append(nodo(30, 120, 190, 64, LINEA, "la tarea llega", "async with sem:", mono=True))
    p.append(flecha(220, 152, 288, 152, LINEA, 2))
    p.append(nodo(290, 120, 200, 64, AMBAR, "¿contador > 0?"))
    p.append(flecha(490, 152, 568, 152, ACENTO, 2))
    p.append(texto(529, 142, "sí", ACENTO, 14, peso="600"))
    p.append(nodo(570, 120, 250, 64, ACENTO, "entra", "contador −= 1 (toma un permiso)"))
    p.append(flecha(695, 184, 695, 238, LINEA, 2))
    p.append(nodo(570, 240, 250, 64, CIAN, "dentro: await la petición", "el permiso sigue tomado"))
    p.append(flecha(695, 304, 695, 358, LINEA, 2))
    p.append(nodo(570, 360, 250, 84, ACENTO, "sale del bloque", "contador += 1 y despierta"))
    p.append(texto(695, 68 + 360, "a la primera de la cola", TEXTO, 13))

    # No: a la cola, y de la cola de vuelta a la pregunta.
    p.append(flecha(350, 184, 350, 268, AMBAR, 2))
    p.append(texto(340, 232, "no", AMBAR, 14, anclaje="end", peso="600"))
    p.append(caja(260, 270, 250, 100, PANEL, AMBAR, radio=10))
    p.append(texto(385, 294, "cola de espera (FIFO)", AMBAR, 15, peso="600"))
    for j, nombre in enumerate(("T4", "T5", "T6")):
        p.append(_segmento("permiso", 300 + j * 60, 308, 50, 26, rotular=False))
        p.append(texto(325 + j * 60, 326, nombre, AMBAR, 14, peso="600"))
    p.append(texto(385, 358, "esperan permiso, sin CPU", SUAVE, 13))
    p.append(flecha(440, 270, 440, 186, VIOLETA, 2))
    p.append(texto(450, 232, "la despiertan", VIOLETA, 13, anclaje="start"))
    p.append(flecha(570, 396, 512, 352, VIOLETA, 2))

    # Ejemplo con k = 3.
    p.append(caja(860, 110, 190, 330, PANEL, LINEA, radio=10))
    p.append(texto(955, 136, "ejemplo: k = 3", TEXTO, 15, peso="600"))
    pasos = (
        ("T1 entra", "3 → 2"), ("T2 entra", "2 → 1"), ("T3 entra", "1 → 0"),
        ("T4 llega", "cola [T4]"), ("T1 sale", "T4 entra"), ("contador", "sigue en 0"),
    )
    for j, (a, b) in enumerate(pasos):
        y = 172 + j * 44
        p.append(texto(876, y, a, TEXTO, 14, anclaje="start"))
        p.append(teclado(1034, y, b, AMBAR if "cola" in b else ACENTO, 13, anclaje="end",
                         peso="normal"))

    p.append(caja(30, 462, ancho - 60, 76, TINTE, AMBAR, radio=8))
    p.append(texto(ancho / 2, 490,
                   "El semáforo solo cuenta permisos: no guarda conexiones ni ningún otro objeto.",
                   AMBAR, 15, peso="600"))
    p.append(texto(ancho / 2, 516,
                   "Un await dentro del bloque suelta el hilo del loop, no el permiso: sigue tomado hasta salir.",
                   TEXTO, 14))
    p.append(cierre())
    return "".join(p)


# ── Las de siempre ─────────────────────────────────────────────────────────

def cmp_bloqueo_del_loop():
    filas = [
        ("T1 · petición", [("ejecuta", 0, 20), ("espera", 20, 220),
                           ("lista", 220, 2040, "lista: llegó la respuesta, pero el loop calcula T3"),
                           ("ejecuta", 2040, 2060)]),
        ("T2 · petición", [("lista", 0, 20), ("ejecuta", 20, 40), ("espera", 40, 240),
                           ("lista", 240, 2060, "lista: llegó la respuesta; el loop sigue en T3"),
                           ("ejecuta", 2060, 2080)]),
        ("T3 · cálculo", [("lista", 0, 40), ("bloquea", 40, 2040)]),
    ]
    # Los tramos de 20 ms miden 8 px: un rótulo para cada par, debajo.
    cpu = [(0, 20, "T1, T2"), (20, 40, ""),
           (40, 2040, "T3 calcula: el loop no atiende a nadie más"),
           (2040, 2060, "T1, T2"), (2060, 2080, "")]
    aria = (
        "Diagrama de Gantt con eje de tiempo en milisegundos de 0 a 2200. T1 y "
        "T2 lanzan una peticion y esperan 200 ms; T3 hace un calculo de 2000 "
        "ms dentro del loop sin ningun await. Las respuestas llegan en 220 y "
        "240 ms, pero T1 y T2 quedan listas, en rayado, hasta 2040 y 2060 ms, "
        "porque el hilo del loop calcula T3 y no recupera el control hasta que "
        "el calculo termina. Total 2080 ms: 2040 + 20 + 20. Sin T3, ambas "
        "peticiones terminarian a los 260 ms."
    )
    return _gantt(
        "Un cálculo de 2 s dentro del loop detiene a todas las demás",
        "dos peticiones de 200 ms y un cálculo de 2000 ms sin await, en el mismo loop",
        aria, filas, [("hilo del loop", cpu)], 2080,
        "Las respuestas llegaron a los 220 y 240 ms; nadie las atendió hasta que el cálculo soltó el loop.",
        cuenta="El loop vuelve en 2040 ms (40 + 2000 de T3) y corre T1 y T2: 2040 + 20 + 20 = 2080 ms.",
        eje_max=2200, paso=200, bloqueo=True,
        leyenda=[("ejecuta", "ejecuta: corre en el hilo del loop"),
                 ("espera", "espera: la red, CPU libre"),
                 ("lista", "lista: puede seguir; el loop está ocupado"),
                 ("bloquea", "T3 calcula dentro del loop, sin await")],
    )


def cmp_vectorizar():
    ancho, alto = 1080, 600
    aria = (
        "Dos paneles. Arriba, un bucle de Python sobre ocho numeros: por cada "
        "elemento el interprete lee el objeto, revisa su tipo, busca la "
        "operacion y crea un objeto nuevo con el resultado; ocho vueltas, "
        "ocho veces ese trabajo. Abajo, NumPy: los ocho numeros float64 "
        "contiguos en un solo bloque de memoria y una sola llamada desde "
        "Python; un bucle compilado recorre el bloque sin pasar por el "
        "interprete, y como factor secundario las instrucciones SIMD procesan "
        "varios elementos por instruccion."
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Vectorizar: sacar el bucle del intérprete",
                   TEXTO, 20, peso="600"))

    # Panel del bucle.
    p.append(caja(30, 66, ancho - 60, 236, PANEL, AMBAR))
    p.append(teclado(60, 100, "for x in datos: total += x * x", AMBAR, 16, anclaje="start"))
    p.append(texto(ancho - 60, 100, "Python, elemento por elemento", AMBAR, 15,
                   anclaje="end", peso="600"))
    cw, gap = 92, 22
    x0 = (ancho - 8 * cw - 7 * gap) / 2
    for k in range(8):
        x = x0 + k * (cw + gap)
        p.append(caja(x, 124, cw, 40, FONDO, LINEA, radio=6))
        p.append(teclado(x + cw / 2, 150, f"{k + 1}.0", TEXTO, 14))
        p.append(flecha(x + cw / 2, 166, x + cw / 2, 196, AMBAR, 1.6))
        p.append(caja(x, 200, cw, 40, TINTE, AMBAR, radio=6))
        p.append(texto(x + cw / 2, 225, "intérprete", AMBAR, 13))
    p.append(texto(ancho / 2, 270,
                   "en cada vuelta: leer el objeto, revisar su tipo, buscar la operación, crear un objeto nuevo",
                   TEXTO, 14))
    p.append(texto(ancho / 2, 292, "8 elementos = 8 veces ese trabajo de más", SUAVE, 13))

    # Panel de NumPy.
    p.append(caja(30, 322, ancho - 60, 248, PANEL, ACENTO))
    p.append(teclado(60, 356, "total = (datos * datos).sum()", ACENTO, 16, anclaje="start"))
    p.append(texto(ancho - 60, 356, "NumPy, el arreglo en bloque", ACENTO, 15,
                   anclaje="end", peso="600"))
    bw = 100
    xb = (ancho - 8 * bw) / 2
    p.append(caja(xb - 6, 374, 8 * bw + 12, 52, TINTE, ACENTO, radio=8))
    for k in range(8):
        x = xb + k * bw
        if k:
            p.append(_linea(x, 380, x, 420, LINEA, 1))
        p.append(teclado(x + bw / 2, 406, f"{k + 1}.0", TEXTO, 14))
    p.append(texto(ancho / 2, 446, "8 float64 contiguos en memoria: sin objetos de Python por elemento",
                   SUAVE, 13))
    p.append(flecha(ancho / 2, 452, ancho / 2, 478, ACENTO, 2))
    p.append(caja(220, 482, 640, 44, FONDO, ACENTO, radio=8))
    p.append(texto(ancho / 2, 510, "una llamada: un bucle compilado (C) recorre todo el bloque",
                   ACENTO, 15, peso="600"))
    p.append(texto(ancho / 2, 552,
                   "SIMD procesa varios elementos por instrucción: ayuda, pero es factor secundario",
                   SUAVE, 13))
    p.append(cierre())
    return "".join(p)


def cmp_amdahl():
    ancho, alto = 1080, 640
    aria = (
        "Grafica de la ley de Amdahl. Eje horizontal: N, numero de procesos, "
        "uno por CPU, de 1 a 16. Eje vertical: aceleracion S de N, tiempo con "
        "1 entre tiempo con N, de 0 a 16. Una diagonal punteada marca la "
        "aceleracion ideal igual a N. Tres curvas teoricas 1 entre f mas 1 "
        "menos f sobre N, con f la fraccion serial: con f igual a 0.1 llega a "
        "6.4 en N 16 y su techo es 10; con f 0.25 llega a 3.4 y su techo es 4; "
        "con f 0.5 llega a 1.9 y su techo es 2. Modelo ideal: carga fija, "
        "fraccion serial constante y sin costos adicionales."
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Ley de Amdahl: la parte serial pone el techo",
                   TEXTO, 20, peso="600"))
    p.append(teclado(ancho / 2, 72, "S(N) = 1 / (f + (1 − f) / N)", ACENTO, 16))
    gx0, gx1, gy0, gy1 = 130, 860, 540, 100   # gy0 abajo, gy1 arriba
    pmax, amax = 16, 16

    def gx(pp):
        return gx0 + (pp - 1) / (pmax - 1) * (gx1 - gx0)

    def gy(a):
        return gy0 - a / amax * (gy0 - gy1)

    for a in range(0, amax + 1, 2):
        p.append(_linea(gx0, gy(a), gx1, gy(a), LINEA, 0.6, "2 6"))
        p.append(texto(gx0 - 12, gy(a) + 5, str(a), SUAVE, 13, anclaje="end"))
    for pp in (1, 2, 4, 6, 8, 10, 12, 14, 16):
        p.append(_linea(gx(pp), gy0, gx(pp), gy0 + 6, SUAVE, 1.4))
        p.append(texto(gx(pp), gy0 + 24, str(pp), SUAVE, 13))
    p.append(_linea(gx0, gy0, gx1, gy0, SUAVE, 1.4))
    p.append(_linea(gx0, gy0, gx0, gy1, SUAVE, 1.4))
    p.append(texto((gx0 + gx1) / 2, gy0 + 52, "N: procesos (una CPU cada uno)", TEXTO, 14))
    p.append(f'<text x="58" y="{(gy0 + gy1) / 2}" fill="{TEXTO}" font-family="system-ui, sans-serif" '
             f'font-size="14" text-anchor="middle" transform="rotate(-90 58 {(gy0 + gy1) / 2})">'
             f'S(N): aceleración (veces más rápido)</text>')

    # Ideal.
    p.append(f'<line x1="{gx(1):.1f}" y1="{gy(1):.1f}" x2="{gx(16):.1f}" y2="{gy(16):.1f}" '
             f'stroke="{SUAVE}" stroke-width="1.6" stroke-dasharray="6 5"/>')
    p.append(texto(gx(11.6) - 8, gy(12.6), "ideal: N", SUAVE, 13, anclaje="end"))

    for f, color in ((0.1, ACENTO), (0.25, CIAN), (0.5, AMBAR)):
        pts = []
        for k in range(0, 151):
            pp = 1 + k * (pmax - 1) / 150
            pts.append(f"{gx(pp):.1f},{gy(1 / (f + (1 - f) / pp)):.1f}")
        p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
                 f'stroke-width="3"/>')
        techo = 1 / f
        p.append(_linea(gx0, gy(techo), gx1, gy(techo), color, 1, "3 5"))
        fin = 1 / (f + (1 - f) / pmax)
        p.append(f'<circle cx="{gx(16):.1f}" cy="{gy(fin):.1f}" r="5" fill="{color}"/>')
        p.append(texto(gx1 + 16, gy(fin) + 5, f"f = {f}: {fin:.1f}× en N = 16",
                       color, 14, anclaje="start", peso="600"))
        p.append(texto(gx0 + 10, gy(techo) - 6, f"techo {techo:g}×", color, 13,
                       anclaje="start"))

    p.append(texto(ancho / 2, 620,
                   "f = fracción serial. Modelo ideal: carga fija, fracción serial constante y sin costos adicionales.",
                   SUAVE, 13))
    p.append(cierre())
    return "".join(p)


def cmp_arbol_decision():
    ancho, alto = 1080, 640
    aria = (
        "Arbol de decision. Primera pregunta: el tiempo se va en esperar red "
        "o disco, o en calcular; se decide midiendo. Si espera: hay "
        "libreria async como httpx, entonces asyncio con gather y un "
        "Semaphore; si no, hilos con ThreadPoolExecutor. Si calcula: opera "
        "sobre arreglos o columnas de numeros, entonces vectoriza con NumPy o "
        "Polars; si no, cada pedazo es independiente y tarda mas que arrancar "
        "un proceso, entonces procesos con ProcessPoolExecutor hasta el numero "
        "de CPU; si no, secuencial y mejora el algoritmo."
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Elegir la estrategia: primero mide dónde se va el tiempo",
                   TEXTO, 20, peso="600"))

    def pregunta(cx, cy, w, l1, l2=None):
        h = 64 if l2 else 46
        out = [caja(cx - w / 2, cy - h / 2, w, h, PANEL, TEXTO, radio=10)]
        if l2:
            out.append(texto(cx, cy - 4, l1, TEXTO, 15, peso="600"))
            out.append(texto(cx, cy + 18, l2, SUAVE, 13))
        else:
            out.append(texto(cx, cy + 6, l1, TEXTO, 15, peso="600"))
        return "".join(out)

    def hoja(cx, cy, color, nombre, l1, l2):
        w, h = 200, 92
        return "".join([
            caja(cx - w / 2, cy - h / 2, w, h, TINTE, color, radio=10),
            texto(cx, cy - 16, nombre, color, 17, peso="600"),
            teclado(cx, cy + 8, l1, TEXTO, 13, peso="normal"),
            texto(cx, cy + 30, l2, SUAVE, 13),
        ])

    def rama(x1, y1, x2, y2, rotulo, color=SUAVE):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        return flecha(x1, y1, x2, y2, LINEA, 2) + texto(
            mx + (10 if x2 >= x1 else -10), my - 4, rotulo, color, 14,
            anclaje="start" if x2 >= x1 else "end", peso="600")

    p.append(pregunta(540, 110, 520, "¿El tiempo se va en esperar o en calcular?",
                      "mídelo: tiempo de reloj contra tiempo de CPU"))
    p.append(rama(420, 142, 270, 214, "espera (red, disco)", CIAN))
    p.append(rama(660, 142, 810, 214, "calcula", AMBAR))

    p.append(pregunta(270, 244, 400, "¿La librería tiene versión async?",
                      "httpx, asyncpg, aiofiles…"))
    p.append(rama(200, 276, 150, 400, "sí", CIAN))
    p.append(rama(340, 276, 390, 400, "no", CIAN))
    p.append(hoja(150, 450, CIAN, "asyncio", "gather + Semaphore", "miles de esperas, 1 hilo"))
    p.append(hoja(390, 450, CIAN, "hilos", "ThreadPoolExecutor", "decenas o cientos"))

    p.append(pregunta(810, 244, 400, "¿Opera sobre arreglos de números?",
                      "columnas, vectores, matrices"))
    p.append(rama(890, 276, 940, 400, "sí", AMBAR))
    p.append(rama(730, 276, 680, 334, "no", AMBAR))
    p.append(hoja(940, 450, AMBAR, "vectoriza", "NumPy, Polars", "el bucle sale de Python"))
    p.append(pregunta(660, 366, 300, "¿Pedazos independientes", "y más largos que arrancar un proceso?"))
    p.append(flecha(700, 398, 700, 520, LINEA, 2))
    p.append(texto(712, 470, "sí", AMBAR, 14, anclaje="start", peso="600"))
    p.append(hoja(700, 566, ACENTO, "procesos", "ProcessPoolExecutor", "hasta el número de CPU"))
    p.append(flecha(610, 398, 500, 520, LINEA, 2))
    p.append(texto(530, 470, "no", AMBAR, 14, anclaje="end", peso="600"))
    p.append(hoja(460, 566, SUAVE, "secuencial", "un for", "mejora el algoritmo"))
    p.append(texto(150, 548, "¿esperas y cálculo juntos?", SUAVE, 13))
    p.append(texto(150, 570, "asyncio para la red,", SUAVE, 13))
    p.append(texto(150, 592, "procesos para el cálculo", SUAVE, 13))
    p.append(cierre())
    return "".join(p)


DIAGRAMAS = {
    # Página 1
    "cmp-estados-tarea": cmp_estados_tarea,
    "cmp-intervalos": cmp_intervalos,
    "cmp-gantt-secuencial": cmp_gantt_secuencial,
    # Página 2
    "cmp-conjuntos": cmp_conjuntos,
    "cmp-gantt-hilos": cmp_gantt_hilos,
    "cmp-gantt-procesos": cmp_gantt_procesos,
    "cmp-arq-servidor-clase": cmp_arq_servidor_clase,
    # Página 3
    "cmp-matriz-asincrono": cmp_matriz_asincrono,
    "cmp-event-loop-ticks": cmp_event_loop_ticks,
    "cmp-create-task": cmp_create_task,
    "cmp-gantt-asyncio": cmp_gantt_asyncio,
    "cmp-gantt-await-en-serie": cmp_gantt_await_en_serie,
    # Página 4
    "cmp-gantt-gather": cmp_gantt_gather,
    "cmp-flujo-semaforo": cmp_flujo_semaforo,
    "cmp-gantt-semaforo": cmp_gantt_semaforo,
    # Páginas 6 a 8
    "cmp-bloqueo-del-loop": cmp_bloqueo_del_loop,
    "cmp-vectorizar": cmp_vectorizar,
    "cmp-amdahl": cmp_amdahl,
    "cmp-arbol-decision": cmp_arbol_decision,
}


# Las figuras de pools y recursos viven en gen_computo_b.py (otro archivo para
# que dos autores no editen el mismo diccionario); se suman al catálogo aquí.
try:
    from gen_computo_b import DIAGRAMAS_B
except ImportError:      # el módulo aún no existe
    DIAGRAMAS_B = {}
DIAGRAMAS.update(DIAGRAMAS_B)

# Bloques 11.2 y 11.3: páginas 9-10 en gen_computo_c.py y 11-12 en
# gen_computo_d.py, cada uno con su catálogo; se suman igual.
for _modulo, _nombre in (("gen_computo_c", "DIAGRAMAS_C"), ("gen_computo_d", "DIAGRAMAS_D")):
    try:
        DIAGRAMAS.update(getattr(__import__(_modulo), _nombre))
    except ImportError:      # el módulo aún no existe
        pass


def escribir(nombre):
    ASSETS.mkdir(parents=True, exist_ok=True)
    destino = ASSETS / f"{nombre}.svg"
    destino.write_text(DIAGRAMAS[nombre](), encoding="utf-8")
    return destino


def main(argv):
    for nombre in argv[1:] or list(DIAGRAMAS):
        if nombre not in DIAGRAMAS:
            raise SystemExit(f"diagrama desconocido: {nombre}")
        destino = escribir(nombre)
        print(f"{destino.name}  ({destino.stat().st_size / 1000:.1f} KB)")


if __name__ == "__main__":
    main(sys.argv)
