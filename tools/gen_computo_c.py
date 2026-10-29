"""Diagramas SVG de las páginas 9 y 10 de la unidad 11 (Cómputo y concurrencia).

Relojes y causas de fallo (página 9: sistemas distribuidos) y capas y
planificaciones (página 10: máquina, proceso, hilo, tarea). Viven aparte de
tools/gen_computo.py, que importa DIAGRAMAS_C y lo suma a su catálogo, así que
`python3 tools/gen_computo.py <id>` también escribe estas figuras.

Este módulo NO importa gen_computo (sería un ciclo): sólo la paleta y las
primitivas de tools/svg_base.py. Estilos de barra, los de la 11.1: ejecuta
relleno, espera con contorno, lista rayada. Sin letras griegas: la tasa se
escribe «lambda», el desfase «Delta».
"""
from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, ROJO, SUAVE, TEXTO, TINTE,
    VIOLETA, caja, cierre, flecha, marco, texto,
)

ANCHO = 1080
X0 = 190          # inicio del área de tiempo
X1 = 1030         # fin del área de tiempo

# Parámetros del ejemplo de relojes (contrato §5), todos supuestos.
DESFASE_B = -40   # ms: reloj de B = reloj real + DESFASE_B
LATENCIA = 20     # ms reales entre envío y recepción
MARCA_A = 100     # ms en el reloj de A al enviar
MARCA_B = MARCA_A + LATENCIA + DESFASE_B   # 80 ms en el reloj de B al recibir

# Parámetros del Gantt de planificaciones: 4 tareas independientes de 100 ms.
TAREAS = 4
TAREA_MS = 100

RAYADO = (
    '<defs><pattern id="rayado" width="8" height="8" patternUnits="userSpaceOnUse" '
    'patternTransform="rotate(45)">'
    f'<rect x="0" y="0" width="8" height="8" fill="{PANEL}"/>'
    f'<line x1="0" y1="0" x2="0" y2="8" stroke="{VIOLETA}" stroke-width="3"/>'
    '</pattern></defs>'
)


def _n(v):
    return f"{v:.1f}"


def _ancho(s, tam=13, peso="normal"):
    return len(s) * tam * (0.58 if peso == "600" else 0.54)


def _rect(x, y, w, h, relleno, borde="none", grosor=0, guiones=None, radio=3):
    extra = f' stroke-dasharray="{guiones}"' if guiones else ""
    return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(max(w, 3))}" height="{_n(h)}" '
            f'rx="{radio}" fill="{relleno}" stroke="{borde}" '
            f'stroke-width="{grosor}"{extra}/>')


def _linea(x1, y1, x2, y2, color=LINEA, grosor=1.2, guiones=None):
    extra = f' stroke-dasharray="{guiones}"' if guiones else ""
    return (f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}" '
            f'stroke="{color}" stroke-width="{grosor}"{extra}/>')


def _t(x, y, s, color=TEXTO, tam=14, anclaje="middle", peso="normal"):
    return texto(_n(x), _n(y), s, color, tam, anclaje, peso)


# tipo: (relleno, borde, grosor, guiones, color del rótulo, peso)
ESTILOS = {
    "ejecuta": (ACENTO, "none", 0, None, FONDO, "600"),
    "espera": (PANEL, CIAN, 1.6, "6 4", CIAN, "normal"),
    "lista": ("url(#rayado)", VIOLETA, 1.4, None, TEXTO, "normal"),
    "inactiva": ("none", SUAVE, 1.2, "3 3", SUAVE, "normal"),
}


def _barra(tipo, x, y, w, h, rotulo=None):
    """Barra con rótulo; «|» parte el rótulo en dos renglones si no cabe en uno."""
    relleno, borde, grosor, guiones, color, peso = ESTILOS[tipo]
    p = [_rect(x + 1, y, w - 2, h, relleno, borde, grosor, guiones)]
    if rotulo:
        una = rotulo.replace("|", " ")
        if _ancho(una, 13, peso) + 16 <= w:
            lineas = [una]
        else:
            lineas = rotulo.split("|")
        asegura = max(_ancho(s, 13, peso) for s in lineas)
        assert asegura + 12 <= w, f"el rótulo {rotulo!r} no cabe en {w:.0f} px"
        paso = 16
        y0 = y + h / 2 - (len(lineas) - 1) * paso / 2 + 5
        for i, s in enumerate(lineas):
            if tipo == "lista":
                p.append(_rect(x + w / 2 - _ancho(s, 13) / 2 - 6, y0 + i * paso - 14,
                               _ancho(s, 13) + 12, 19, FONDO, radio=4))
            p.append(_t(x + w / 2, y0 + i * paso, s, color, 13, peso=peso))
    return "".join(p)


def _leyenda(y, items, x=40):
    p = []
    for tipo, rotulo in items:
        p.append(_barra(tipo, x, y - 14, 34, 18))
        p.append(_t(x + 44, y, rotulo, TEXTO, 14, "start"))
        x += 44 + _ancho(rotulo, 14) + 36
    return "".join(p)


def _encabezado(titulo, subtitulo):
    return (_t(ANCHO / 2, 42, titulo, TEXTO, 20, peso="600")
            + _t(ANCHO / 2, 70, subtitulo, SUAVE, 14))


# ---------------------------------------------------------------------------
# Página 9: relojes
# ---------------------------------------------------------------------------

def cmp_dist_relojes():
    alto = 600
    xs = lambda ms: X0 + ms * (X1 - X0) / 200
    aria = (
        "Diagrama de tiempo de dos componentes, A y B, con dos ejes alineados al "
        "mismo instante real. El reloj de B marca el reloj real menos 40 ms. A "
        "envía un mensaje cuando su reloj marca 100 ms; el mensaje tarda 20 ms "
        "reales y B lo recibe cuando su reloj marca 80 ms. Restar las marcas da "
        "80 menos 100, es decir menos 20 ms, que es 20 ms menos 40 ms: no es la "
        "tiempo de tránsito, porque mezcla dos relojes."
    )
    p = [marco(ANCHO, alto, aria), _encabezado(
        "Restar marcas de dos relojes distintos da −20 ms, un tiempo negativo",
        "Reloj de B = reloj real − 40 ms; un mensaje de A a B tarda 20 ms reales "
        "(supuestos del ejemplo)")]
    y_a, y_la, y_lb, y_b = 128, 148, 272, 338
    # guías del instante real de envío y de recepción
    for ms in (MARCA_A, MARCA_A + LATENCIA):
        p.append(_linea(xs(ms), y_a, xs(ms), y_b, LINEA, 1.2, "3 5"))
    # eje del reloj de A (arriba): marcas = reloj real
    p.append(_linea(X0, y_a, X1, y_a, SUAVE, 1.4))
    for ms in range(0, 201, 50):
        p.append(_linea(xs(ms), y_a - 6, xs(ms), y_a, SUAVE, 1.4))
        p.append(_t(xs(ms), y_a - 12, str(ms), SUAVE, 13))
    p.append(_t(X0 - 34, y_a - 12, "reloj de A (ms)", SUAVE, 13, "end"))
    # eje del reloj de B (abajo): marca = real − 40
    p.append(_linea(X0, y_b, X1, y_b, SUAVE, 1.4))
    for ms in range(0, 201, 50):
        p.append(_linea(xs(ms), y_b, xs(ms), y_b + 6, SUAVE, 1.4))
        p.append(_t(xs(ms), y_b + 26, str(ms + DESFASE_B).replace("-", "−"), SUAVE, 13))
    p.append(_t(X0 - 34, y_b + 26, "reloj de B (ms)", SUAVE, 13, "end"))
    p.append(_t(xs(MARCA_A + LATENCIA), y_b + 26, str(MARCA_B), AMBAR, 14, peso="600"))
    # carriles
    p.append(_t(X0 - 16, y_la + 25, "componente A", TEXTO, 14, "end", "600"))
    p.append(_barra("ejecuta", xs(40), y_la, xs(MARCA_A) - xs(40), 38, "A prepara y envía"))
    p.append(_t(X0 - 16, y_lb + 25, "componente B", TEXTO, 14, "end", "600"))
    p.append(_barra("espera", xs(40), y_lb, xs(MARCA_A + LATENCIA) - xs(40), 38,
                    "B espera el mensaje: CPU libre"))
    p.append(_barra("ejecuta", xs(MARCA_A + LATENCIA), y_lb,
                    xs(190) - xs(MARCA_A + LATENCIA), 38, "B recibe y procesa"))
    # flecha causal y marcas
    p.append(flecha(_n(xs(MARCA_A)), y_la + 38, _n(xs(MARCA_A + LATENCIA)), y_lb, AMBAR, 2.5))
    p.append(_t(xs(MARCA_A) - 14, y_la + 66, "A marca 100 ms al enviar", AMBAR, 14, "end", "600"))
    p.append(_t(xs(MARCA_A + LATENCIA) + 24, y_la + 66, "mensaje: tránsito real 20 ms",
                AMBAR, 14, "start", "600"))
    p.append(_t(xs(MARCA_A + LATENCIA) + 24, y_la + 90, "B marca 80 ms al recibir",
                AMBAR, 14, "start", "600"))
    # cuenta
    p.append(caja(40, 396, 1000, 148, TINTE, LINEA, 10, 1.6))
    p.append(_t(ANCHO / 2, 436, "B marca 80, A marcó 100: 80−100 = −20 ms = 20 ms − 40 ms",
                AMBAR, 20, peso="600"))
    p.append(_t(ANCHO / 2, 472, "20 ms es el tiempo de tránsito real del mensaje; −40 ms es el desfase "
                "del reloj de B.", TEXTO, 15))
    p.append(_t(ANCHO / 2, 500, "La resta mide el tránsito más el desfase, no el tránsito: dos "
                "relojes distintos no se restan como si fueran uno.", TEXTO, 15))
    p.append(_leyenda(574, [("ejecuta", "ejecuta: usa la CPU"),
                            ("espera", "espera: CPU libre")]))
    p.append(cierre())
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 9: tres causas de un tiempo agotado
# ---------------------------------------------------------------------------

def _carril_causa(y, numero, titulo, linea2, servidor, color_srv, peticion, respuesta):
    """peticion y respuesta: (estado, rotulo); estado 'llega' o 'pierde'."""
    xc, xs_, wc = 280, 600, 120
    p = [caja(24, y, 1032, 150, "none", LINEA, 10, 1)]
    partes = titulo.split("|")
    for i, parte in enumerate(partes):
        p.append(_t(40, y + 46 + i * 22, (f"{numero}. " if i == 0 else "   ") + parte,
                    TEXTO, 16, "start", "600"))
    p.append(_t(40, y + 52 + len(partes) * 22, linea2, SUAVE, 14, "start"))
    p.append(caja(xc, y + 28, wc, 94, PANEL, LINEA, 8, 2))
    p.append(_t(xc + wc / 2, y + 62, "cliente", TEXTO, 16, peso="600"))
    p.append(_t(xc + wc / 2, y + 86, "espera t_max", SUAVE, 14))
    p.append(caja(xs_, y + 28, 150, 94, color_srv[0], color_srv[1], 8, 2))
    p.append(_t(xs_ + 75, y + 62, "servidor", TEXTO, 16, peso="600"))
    for i, s in enumerate(servidor):
        p.append(_t(xs_ + 75, y + 84 + i * 18, s, color_srv[2], 14))
    x_ini, x_fin = xc + wc, xs_
    # petición, hacia el servidor
    y1 = y + 54
    if peticion[0] == "llega":
        p.append(flecha(x_ini, y1, x_fin, y1, ACENTO, 2.2))
        p.append(_t((x_ini + x_fin) / 2, y1 - 8, peticion[1], ACENTO, 14))
    else:
        corte = x_ini + 100
        p.append(_linea(x_ini, y1, corte, y1, ROJO, 2.2, "6 4"))
        p.append(_t(corte + 12, y1 + 6, "×", ROJO, 22, "middle", "600"))
        p.append(_t((x_ini + x_fin) / 2, y1 - 8, peticion[1], ROJO, 14))
    # respuesta, hacia el cliente
    y2 = y + 100
    if respuesta[0] == "llega":
        p.append(flecha(x_fin, y2, x_ini, y2, AMBAR, 2.2))
        p.append(_t((x_ini + x_fin) / 2, y2 + 20, respuesta[1], AMBAR, 14))
    elif respuesta[0] == "pierde":
        corte = x_fin - 100
        p.append(_linea(x_fin, y2, corte, y2, ROJO, 2.2, "6 4"))
        p.append(_t(corte - 12, y2 + 6, "×", ROJO, 22, "middle", "600"))
        p.append(_t((x_ini + x_fin) / 2, y2 + 20, respuesta[1], ROJO, 14))
    else:
        p.append(_t((x_ini + x_fin) / 2, y2 + 20, respuesta[1], SUAVE, 14))
    # lo que ve el cliente: igual en los tres carriles
    p.append(caja(800, y + 28, 240, 94, TINTE, ACENTO, 8, 1.6))
    p.append(_t(920, y + 56, "tras t_max, sin respuesta", TEXTO, 14, peso="600"))
    p.append(_t(920, y + 82, "espero t_max y no sé", AMBAR, 15, peso="600"))
    p.append(_t(920, y + 104, "cuál fue", AMBAR, 15, peso="600"))
    return "".join(p)


def cmp_dist_tres_causas():
    alto = 690
    aria = (
        "Tres carriles de la misma petición del cliente al servidor que no recibe "
        "respuesta antes de t_max. Primero, la ida se pierde y el servidor no se "
        "entera. Segundo, el servidor ejecuta la petición pero la respuesta se "
        "pierde. Tercero, el servidor tarda más que t_max y la respuesta llega "
        "tarde. En los tres casos el cliente observa lo mismo: espero t_max y no "
        "sé cuál fue."
    )
    p = [marco(ANCHO, alto, aria), _encabezado(
        "Tres causas distintas, una sola observación: sin respuesta tras t_max",
        "La misma petición, el mismo cliente; lo que pasó en la red y en el servidor "
        "no se ve desde el cliente")]
    p.append(_t(480, 106, "qué pasó", SUAVE, 14, peso="600"))
    p.append(_t(920, 106, "qué observa el cliente", SUAVE, 14, peso="600"))
    sombra = (PANEL, LINEA, SUAVE)
    p.append(_carril_causa(
        120, 1, "La ida se pierde", "el servidor nunca la recibe",
        ["no se entera:", "no ejecuta nada"], sombra,
        ("pierde", "la petición se pierde"), ("nada", "no hay respuesta")))
    p.append(_carril_causa(
        284, 2, "La respuesta|se pierde", "el servidor sí ejecutó",
        ["ejecutó:", "hubo efecto"], (TINTE, ACENTO, TEXTO),
        ("llega", "la petición llega"), ("pierde", "la respuesta se pierde")))
    p.append(_carril_causa(
        448, 3, "El servidor tarda|más que t_max", "ejecuta, pero despacio",
        ["ejecuta lento:", "responde tarde"], (TINTE, AMBAR, TEXTO),
        ("llega", "la petición llega"), ("llega", "llega tras t_max")))
    p.append(_t(ANCHO / 2, 642, "En la 2 el servidor ejecutó; en la 3 puede estar ejecutando todavía: "
                "reintentar sin más puede ejecutar dos veces.", AMBAR, 15, peso="600"))
    p.append(_t(ANCHO / 2, 668, "Desde el cliente el silencio es idéntico: sólo t_max lo "
                "delimita, ningún dato lo explica.", TEXTO, 14))
    p.append(cierre())
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 10: capas
# ---------------------------------------------------------------------------

def _caja_capa(x, y, w, nombre, detalle, borde=LINEA, relleno=PANEL):
    return (caja(x, y, w, 70, relleno, borde, 8, 2)
            + _t(x + w / 2, y + 30, nombre, TEXTO, 16, peso="600")
            + _t(x + w / 2, y + 54, detalle, SUAVE, 13))


def cmp_capas():
    alto = 720
    aria = (
        "Dos columnas. A la izquierda, pertenencia: una máquina contiene procesos, "
        "un proceso contiene hilos y un hilo recibe tareas. A la derecha, "
        "ejecución: el sistema operativo asigna hilos a CPU lógicas, el runtime "
        "reparte tareas entre hilos y una tarea puede migrar de un hilo a otro. "
        "Pertenecer no es ejecutar: planifican dos agentes distintos."
    )
    p = [marco(ANCHO, alto, aria), _encabezado(
        "Pertenecer no es ejecutar: dos planificadores, uno para hilos y otro para tareas",
        "Izquierda, qué contiene a qué; derecha, quién corre sobre quién y quién decide")]
    p.append(_linea(540, 92, 540, 700, LINEA, 1.2, "3 5"))
    p.append(_t(280, 112, "Pertenencia: qué contiene a qué", TEXTO, 16, peso="600"))
    p.append(_t(800, 112, "Ejecución: quién corre sobre quién", TEXTO, 16, peso="600"))
    ys = (132, 262, 392, 522)
    izq = (("máquina", "tiene CPU lógicas y memoria"),
           ("proceso", "tiene su espacio de memoria"),
           ("hilo", "comparte la memoria del proceso"),
           ("tarea", "trabajo que se pide ejecutar"))
    for y, (nombre, detalle) in zip(ys, izq):
        p.append(_caja_capa(100, y, 360, nombre, detalle))
    for y0, y1, rotulo in zip(ys, ys[1:], ("contiene procesos", "contiene hilos",
                                           "recibe tareas")):
        p.append(flecha(280, y0 + 70, 280, y1, LINEA, 2))
        p.append(_t(294, (y0 + 70 + y1) / 2 + 5, rotulo, SUAVE, 13, "start"))
    # derecha: CPU, hilos, tareas
    cpus = ((660, "CPU 1"), (900, "CPU 2"))
    hilos = ((660, "hilo A"), (900, "hilo B"))
    for x, e in cpus:
        p.append(_caja_capa(x - 70, ys[0], 140, e, "CPU lógica", ACENTO, TINTE))
    for x, e in hilos:
        p.append(_caja_capa(x - 70, ys[2], 140, e, "ejecuta código"))
    tareas = ((600, "T1", 660), (700, "T2", 660), (840, "T3", 900), (960, "T4", 900))
    for x, e, _ in tareas:
        p.append(_caja_capa(x - 50, ys[3], 100, e, "tarea"))
    # SO: hilo -> CPU
    for x, _ in hilos:
        p.append(flecha(x, ys[2], x, ys[0] + 70, ACENTO, 2.2))
    p.append(_t(780, 292, "el sistema operativo", AMBAR, 14, peso="600"))
    p.append(_t(780, 312, "asigna hilos a CPU lógicas", AMBAR, 14, peso="600"))
    p.append(_t(780, 338, "planifica: el SO", SUAVE, 13))
    # runtime: tarea -> hilo (la migración en cian)
    for x, _, h in tareas:
        if (x, h) != (700, 660):
            p.append(flecha(x, ys[3], h if h == 900 else x + 20, ys[2] + 70, LINEA, 1.6))
    p.append(flecha(700, ys[3], 676, ys[2] + 70, LINEA, 1.6))
    p.append(flecha(730, ys[3], 884, ys[2] + 70, CIAN, 2.6))
    p.append(_t(780, 612, "el runtime reparte tareas entre hilos", AMBAR, 14, peso="600"))
    p.append(_t(780, 636, "planifica: el runtime (event loop o pool)", SUAVE, 13))
    p.append(_t(780, 662, "flecha cian: T2 puede migrar de hilo (p. ej. en Go;", CIAN, 14, peso="600"))
    p.append(_t(780, 684, "en asyncio una tarea no cambia de hilo)", CIAN, 14, peso="600"))
    p.append(cierre())
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 10: el mismo trabajo en tres planificaciones
# ---------------------------------------------------------------------------

def _panel(p, y0, xs, titulo, filas, cuenta, nota=()):
    """filas: [(etiqueta, [(tipo, ini, fin, rotulo), ...])]; regresa el y de abajo."""
    alto_fila, alto_barra = 40, 34
    p.append(_t(40, y0 + 4, titulo, TEXTO, 16, "start", "600"))
    arriba = y0 + 22
    for ms in range(0, 401, 100):
        p.append(_linea(xs(ms), arriba - 4, xs(ms), arriba + len(filas) * alto_fila + 2,
                        LINEA, 0.6, "2 6"))
    for i, (etiqueta, barras) in enumerate(filas):
        y = arriba + i * alto_fila
        p.append(_t(X0 - 12, y + alto_barra / 2 + 5, etiqueta, TEXTO, 14, "end", "600"))
        for tipo, ini, fin, rotulo in barras:
            p.append(_barra(tipo, xs(ini), y, xs(fin) - xs(ini), alto_barra, rotulo))
    y_eje = arriba + len(filas) * alto_fila + 8
    p.append(_linea(X0, y_eje, X1, y_eje, SUAVE, 1.4))
    for ms in range(0, 401, 100):
        p.append(_linea(xs(ms), y_eje, xs(ms), y_eje + 6, SUAVE, 1.4))
        p.append(_t(xs(ms), y_eje + 24, str(ms), SUAVE, 13))
    p.append(_t(X0 - 12, y_eje + 24, "tiempo (ms)", SUAVE, 13, "end"))
    p.append(_t(X1, y_eje + 50, cuenta, AMBAR, 15, "end", "600"))
    for i, linea in enumerate(nota):
        p.append(_t(40, y_eje + 78 + i * 22, linea, SUAVE, 14, "start"))
    return y_eje + 50 + (4 + 22 * len(nota) if nota else 0)


def cmp_gantt_tres_planificaciones():
    xs = lambda ms: X0 + ms * (X1 - X0) / 400
    aria = (
        "Tres diagramas de Gantt del mismo trabajo: cuatro tareas independientes "
        "de 100 ms de cálculo, disponibles en 0 ms, en tiempos ideales. Panel a: "
        "tareas cooperativas en un solo hilo con cuatro CPU libres; las tareas "
        "se turnan y el total es 400 ms. Panel b: cuatro hilos con exclusión "
        "global; las listas esperan la exclusión y el total es 400 ms. Panel c: "
        "cuatro hilos en cuatro CPU; ejecutan a la vez y el total es 100 ms."
    )
    n = TAREAS
    t = TAREA_MS

    def una_a_la_vez(rotulos, motivos):
        filas = []
        for i in range(n):
            barras = []
            if i:
                barras.append(("lista", 0, i * t, motivos[i]))
            barras.append(("ejecuta", i * t, (i + 1) * t, rotulos[i]))
            filas.append((f"tarea T{i + 1}", barras))
        return filas

    cpu1_seguida = ("CPU 1", [("ejecuta", i * t, (i + 1) * t, f"T{i + 1} · hilo {h}")
                              for i, h in enumerate("ABCD")])
    cpu1_hilo = ("CPU 1", [("ejecuta", i * t, (i + 1) * t, f"T{i + 1} · hilo único")
                           for i in range(n)])
    fila_a = una_a_la_vez(
        [f"T{i + 1} · hilo único · CPU 1" for i in range(n)],
        {1: "lista: el hilo único|corre T1",
         2: "lista: el hilo único corre T1 y luego T2",
         3: "lista: el hilo único corre T1, T2 y luego T3"})
    fila_a += [cpu1_hilo, ("CPU 2, 3 y 4", [("inactiva", 0, n * t,
                                              "inactivas: no hay un segundo hilo al que darles trabajo")])]
    fila_b = una_a_la_vez(
        [f"T{i + 1} · hilo {h} · CPU 1" for i, h in enumerate("ABCD")],
        {1: "lista: espera la|exclusión global (T1)",
         2: "lista: espera la exclusión global (T1, luego T2)",
         3: "lista: espera la exclusión global (T1, T2, luego T3)"})
    fila_b += [cpu1_seguida, ("CPU 2, 3 y 4", [("inactiva", 0, n * t,
                                                 "inactivas: la exclusión global deja ejecutar a un solo hilo")])]
    fila_c = [(f"tarea T{i + 1}", [("ejecuta", 0, t, f"T{i + 1} · hilo {h} · CPU {i + 1}")])
              for i, h in enumerate("ABCD")]
    fila_c += [("CPU 1", [("ejecuta", 0, t, "T1 · hilo A"),
                          ("inactiva", t, n * t, "CPU libre: ya no hay tareas")]),
               ("CPU 2, 3 y 4", [("ejecuta", 0, t, "T2, T3 y T4|a la vez"),
                                 ("inactiva", t, n * t, "CPU libres: ya no hay tareas")])]
    p = [marco(ANCHO, 1280, aria) + RAYADO, _encabezado(
        "Mismo trabajo, tres planificaciones: cuentan las tareas que ejecutan a la vez",
        "4 tareas independientes de 100 ms de cálculo, disponibles en 0 ms, sin costos extra "
        "(tiempos ideales)")]
    y = 118
    y = _panel(p, y, xs, "(a) Tareas cooperativas en 1 hilo: 4 CPU libres no aceleran nada",
               fila_a, "una ejecución a la vez: ⌈4/1⌉·100 = 400 ms")
    y = _panel(p, y + 44, xs, "(b) 4 hilos con exclusión global: ejecuta uno solo a la vez",
               fila_b, "una ejecución a la vez: ⌈4/1⌉·100 = 400 ms",
               ("una intercalación posible: con exclusión global los hilos se turnan, "
                "cada uno corre solo cuando la tiene;",
                "el total sigue siendo 4 × 100 = 400 ms"))
    y = _panel(p, y + 44, xs, "(c) 4 hilos en 4 CPU, sin exclusión: ejecutan a la vez",
               fila_c, "cuatro ejecuciones a la vez: ⌈4/4⌉·100 = 100 ms")
    p.append(_leyenda(y + 40, [("ejecuta", "ejecuta: usa una CPU"),
                               ("lista", "lista: puede seguir, espera su turno"),
                               ("inactiva", "CPU sin trabajo")]))
    p.append(cierre())
    svg = "".join(p)
    return svg


DIAGRAMAS_C = {
    "cmp-dist-relojes": cmp_dist_relojes,
    "cmp-dist-tres-causas": cmp_dist_tres_causas,
    "cmp-capas": cmp_capas,
    "cmp-gantt-tres-planificaciones": cmp_gantt_tres_planificaciones,
}
