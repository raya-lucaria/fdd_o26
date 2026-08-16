"""Genera los ocho diagramas SVG de la unidad de Pipeline de Datos.

Deterministico y sin dependencias externas: el SVG se escribe a mano. Este
archivo es la unica fuente de verdad de esos diagramas — editar un .svg a mano
es un error que tools/test_diagramas.py detecta.

Colores tomados de skins/fdd-eva.yaml. Cada diagrama pinta su propio fondo y
usa `fill` explicito en todo texto, para que se lea igual en tema claro y en
tema oscuro.

El color aqui es semantico, no decorativo: cada diagrama lo usa para separar
las cosas que el lector tiene que distinguir (las ramas de un DAG, los cuatro
almacenamientos, ETL frente a ELT, las seis dimensiones de calidad). Por eso
cada diagrama elige su propia paleta dentro de la misma familia de tonos: el
conjunto se lee como una serie, pero ninguna lamina se confunde con otra.
"""
import colorsys
import math
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/2_pipeline_de_datos/_assets"

# Paleta fdd-eva.
FONDO = "#0b0f12"
PANEL = "#141b20"
CAJA = "#1b2730"
TEXTO = "#e8f0e8"
SUAVE = "#a7b8ad"
LINEA = "#4a7a63"
VERDE = "#7ef29d"
AMBAR = "#ffc857"
CIAN = "#6fd8e8"
VIOLETA = "#c9a7ff"
LIMA = "#b8e986"
NARANJA = "#ff9f6b"
TEAL = "#5fe0c0"
ROJO = "#ff6b6b"
MAGENTA = "#ff8ad4"
AZUL = "#7aa7ff"

# Rellenos tenues, para teñir una caja sin perder el contraste del texto.
TINTE_VERDE = "#16302a"
TINTE_ROJO = "#3a1c1c"
TINTE_VIOLETA = "#251d3a"
TINTE_CIAN = "#122a31"


def _rueda(n, inicio=140, luz=0.72, sat=0.72):
    """n colores repartidos por el circulo de tono, del mismo brillo.

    Sirve para una secuencia que avanza y cierra: el ultimo tono queda a un
    paso del primero, igual que la ultima etapa de un ciclo queda a un paso de
    la primera.
    """
    salida = []
    for i in range(n):
        tono = ((inicio + i * 360.0 / n) % 360.0) / 360.0
        r, g, b = colorsys.hls_to_rgb(tono, luz, sat)
        salida.append("#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255)))
    return tuple(salida)


# Gradiente del ciclo de vida: cuatro etapas que avanzan y vuelven al principio.
CICLO = _rueda(4)

# Rampa de latencia: de lo mas lento (azul frio) a lo mas fresco (rojo caliente).
LATENCIA = ("#5b83d6", "#4fd6c0", "#ffc857", "#ff7a5c")

FUENTE = "system-ui, -apple-system, Segoe UI, sans-serif"
ANCHO = 880
COLORES_FLECHA = (
    (LINEA, VERDE, AMBAR, CIAN, VIOLETA, NARANJA, TEAL, SUAVE, ROJO, MAGENTA, AZUL)
    + CICLO
    + LATENCIA
)

# Degradados con id propio: un nodo compartido por dos ramas lleva los dos
# colores en el mismo borde.
GRADIENTES = (("gRamaAB", CIAN, VIOLETA),)


# --------------------------------------------------------------------------
# Primitivas
# --------------------------------------------------------------------------
def _id_flecha(color):
    return "f" + color.lstrip("#")


def _defs():
    partes = ["<defs>"]
    vistos = []
    for color in COLORES_FLECHA:
        if color in vistos:
            continue
        vistos.append(color)
        partes.append(
            f'<marker id="{_id_flecha(color)}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
        )
    for nombre, desde, hasta in GRADIENTES:
        partes.append(
            f'<linearGradient id="{nombre}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{desde}"/>'
            f'<stop offset="1" stop-color="{hasta}"/></linearGradient>'
        )
    partes.append("</defs>")
    return "".join(partes)


def marco(alto, titulo):
    """Abre el SVG. width/height explicitos ademas del viewBox: sin ellos el
    navegador incrusta el <svg> con ~300x150 px y el diagrama se ve minusculo."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" height="{alto}" '
        f'viewBox="0 0 {ANCHO} {alto}" role="img" aria-label="{escape(titulo)}">'
        f"<title>{escape(titulo)}</title>"
        + _defs()
        + f'<rect x="0" y="0" width="{ANCHO}" height="{alto}" rx="16" fill="{FONDO}"/>'
    )


def txt(x, y, s, fill=TEXTO, size=13, anchor="start", weight="400", opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{FUENTE}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{op}>'
        f"{escape(s)}</text>"
    )


def rect(x, y, w, h, relleno, borde=None, rx=10, ancho_borde=1.5, opacidad=None):
    st = f' stroke="{borde}" stroke-width="{ancho_borde}"' if borde else ""
    op = f' opacity="{opacidad}"' if opacidad is not None else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
        f'fill="{relleno}"{st}{op}/>'
    )


def caja(x, y, w, h, lineas, borde, relleno=CAJA, size=13, weight="600", rx=10):
    """Caja con texto centrado horizontal y verticalmente."""
    p = [rect(x, y, w, h, relleno, borde, rx=rx)]
    lh = size + 5
    y0 = y + h / 2 - (len(lineas) - 1) * lh / 2 + size / 3
    for i, linea in enumerate(lineas):
        p.append(
            txt(x + w / 2, y0 + i * lh, linea, fill=TEXTO, size=size,
                anchor="middle", weight=weight)
        )
    return "".join(p)


def linea(x1, y1, x2, y2, color=LINEA, ancho=1.5, punteada=False, flecha=False,
          opacidad=None):
    d = ' stroke-dasharray="5 4"' if punteada else ""
    m = f' marker-end="url(#{_id_flecha(color)})"' if flecha else ""
    op = f' opacity="{opacidad}"' if opacidad is not None else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{ancho}"{d}{m}{op}/>'
    )


def curva(x1, y1, x2, y2, color=LINEA, ancho=1.6, flecha=True):
    dx = max((x2 - x1) * 0.45, 24)
    m = f' marker-end="url(#{_id_flecha(color)})"' if flecha else ""
    return (
        f'<path d="M{x1:.1f},{y1:.1f} C{x1 + dx:.1f},{y1:.1f} {x2 - dx:.1f},{y2:.1f} '
        f'{x2:.1f},{y2:.1f}" fill="none" stroke="{color}" stroke-width="{ancho}"{m}/>'
    )


def encabezado(titulo, subtitulo=None):
    p = [txt(30, 32, titulo, fill=TEXTO, size=17, weight="700")]
    if subtitulo:
        p.append(txt(30, 54, subtitulo, fill=SUAVE, size=12.5))
    return "".join(p)


def leyenda(x, y, entradas, size=11.5, color_texto=SUAVE):
    """Fila de fichas de color con su etiqueta.

    El ancho de cada etiqueta se estima por conteo de caracteres: basta para
    repartir las fichas sin encimarlas y mantiene la salida deterministica.
    """
    p = []
    cx = x
    for color, etiqueta in entradas:
        p.append(
            f'<rect x="{cx:.1f}" y="{y - 9:.1f}" width="13" height="13" rx="4" '
            f'fill="{color}"/>'
        )
        p.append(txt(cx + 19, y + 2, etiqueta, fill=color_texto, size=size))
        cx += 19 + len(etiqueta) * size * 0.53 + 20
    return "".join(p)


# --------------------------------------------------------------------------
# 1. El pipeline como DAG
# --------------------------------------------------------------------------
def dag():
    """El color separa las tres ramas y marca el nodo donde reconvergen."""
    alto = 452
    titulo = ("Un pipeline de datos es un grafo dirigido acíclico: las etapas se "
              "bifurcan y vuelven a converger")
    col = [22, 194, 366, 538, 710]
    w, h = 148, 48

    # Una rama por linaje de datos; ámbar reservado al punto de confluencia.
    RAMA_VENTAS, RAMA_CATALOGO, RAMA_CLICS = CIAN, VIOLETA, NARANJA
    CONFLUENCIA, CONSUMO = AMBAR, VERDE

    nodos = {
        "api": (0, 110, ["Ventas", "(API)"], RAMA_VENTAS),
        "csv": (0, 200, ["Catálogo", "(CSV)"], RAMA_CATALOGO),
        "clics": (0, 290, ["Clics", "(stream)"], RAMA_CLICS),
        # Nodo compartido por dos ramas: lleva los dos colores en el borde.
        "batch": (1, 135, ["Ingesta batch"], "url(#gRamaAB)"),
        "cont": (1, 265, ["Ingesta continua"], RAMA_CLICS),
        "limpieza": (2, 80, ["Limpieza"], RAMA_VENTAS),
        "dim": (2, 190, ["Dimensión", "producto"], RAMA_CATALOGO),
        "ses": (2, 300, ["Sesiones"], RAMA_CLICS),
        "hechos": (3, 190, ["Tabla de hechos"], CONFLUENCIA),
        "tablero": (4, 130, ["Tablero"], CONSUMO),
        "modelo": (4, 250, ["Modelo"], CONSUMO),
    }
    # Cada arista se pinta del color de la rama a la que pertenece.
    aristas = [
        ("api", "batch", RAMA_VENTAS), ("csv", "batch", RAMA_CATALOGO),
        ("clics", "cont", RAMA_CLICS),
        ("batch", "limpieza", RAMA_VENTAS), ("batch", "dim", RAMA_CATALOGO),
        ("cont", "ses", RAMA_CLICS),
        ("limpieza", "hechos", RAMA_VENTAS), ("dim", "hechos", RAMA_CATALOGO),
        ("ses", "hechos", RAMA_CLICS),
        ("hechos", "tablero", CONSUMO), ("hechos", "modelo", CONSUMO),
    ]

    p = [marco(alto, titulo)]
    p.append(encabezado("Un pipeline es un DAG, no una flecha",
                        "El orden lo imponen las dependencias."))

    for origen, destino, color in aristas:
        co, yo, _, _ = nodos[origen]
        cd, yd, _, _ = nodos[destino]
        p.append(curva(col[co] + w, yo + h / 2, col[cd], yd + h / 2, color=color))

    # Halo del nodo de confluencia: se ve antes que las cajas y no las tapa.
    hc, hy, _, _ = nodos["hechos"]
    p.append(rect(col[hc] - 9, hy - 9, w + 18, h + 18, CONFLUENCIA, None, rx=14,
                  opacidad="0.16"))

    for nombre, (c, y, lineas, color) in nodos.items():
        if nombre == "hechos":
            p.append(caja(col[c], y, w, h, lineas, color, relleno=TINTE_VERDE,
                          size=12.5))
            continue
        p.append(caja(col[c], y, w, h, lineas, color, size=12.5))

    p.append(txt(col[3] + w / 2, hy - 20, "reconvergen aquí", fill=CONFLUENCIA,
                 size=11.5, anchor="middle", weight="600"))

    etiquetas = ["Fuentes", "Ingesta", "Transformación", "Modelo", "Consumo"]
    for i, etq in enumerate(etiquetas):
        p.append(txt(col[i] + w / 2, 368, etq, fill=SUAVE, size=11.5, anchor="middle"))

    p.append(leyenda(30, 402, [
        (RAMA_VENTAS, "rama de ventas"),
        (RAMA_CATALOGO, "rama de catálogo"),
        (RAMA_CLICS, "rama de clics"),
        (CONFLUENCIA, "donde reconvergen"),
    ]))

    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 2. Schema-on-write vs schema-on-read
# --------------------------------------------------------------------------
def schema():
    alto = 500
    titulo = ("Schema-on-write frente a schema-on-read: base de datos, data lake, "
              "data warehouse y lakehouse")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "Dónde vive el esquema",
        "Antes de escribir, o al leer."))

    # Un color por almacenamiento: el mismo color identifica a cada uno en
    # todo el diagrama. Rojo queda reservado a lo que se paga, no a un almacén.
    C_BD, C_WAREHOUSE, C_LAKE, C_LAKEHOUSE = CIAN, VERDE, AMBAR, VIOLETA

    paneles = [
        (30, "Schema-on-write", "Valida antes de guardar.",
         [
             (C_BD, "Base de datos relacional",
              ["Esquema fijo y transacciones.",
               "Para la app, no el análisis."]),
             (C_WAREHOUSE, "Data warehouse",
              ["Esquema modelado para consultar.",
               "Entra dato ya limpio y conformado."]),
         ]),
        (460, "Schema-on-read", "Valida al leer, no antes.",
         [
             (C_LAKE, "Data lake",
              ["Archivos crudos, cualquier formato.",
               "Barato, flexible, sin promesas."]),
             (ROJO, "El costo de no tener contrato",
              ["Nadie garantiza la forma:",
               "Quien lee paga la limpieza."]),
         ]),
    ]

    for px, ptitulo, psub, cajas in paneles:
        p.append(rect(px, 76, 390, 262, PANEL, LINEA, rx=14, ancho_borde=1.2))
        p.append(txt(px + 18, 104, ptitulo, fill=TEXTO, size=15, weight="700"))
        p.append(txt(px + 18, 124, psub, fill=SUAVE, size=11.5))
        for i, (color, nombre, desc) in enumerate(cajas):
            by = 140 + i * 100
            p.append(rect(px + 18, by, 354, 88, CAJA, color, rx=10, ancho_borde=1.4))
            # Barra de color a la izquierda: identifica el almacén de un
            # vistazo. Va hundida en vertical para no salirse de la esquina
            # redondeada de la caja que la contiene.
            p.append(rect(px + 19, by + 12, 5, 64, color, None, rx=2.5))
            p.append(txt(px + 40, by + 28, nombre, fill=color, size=13.5, weight="600"))
            for j, d in enumerate(desc):
                p.append(txt(px + 40, by + 50 + j * 18, d, fill=SUAVE, size=11.5))

    # Las dos flechas llevan el color del destino: ambas apuntan al lakehouse.
    p.append(linea(225, 338, 320, 366, C_LAKEHOUSE, flecha=True))
    p.append(linea(655, 338, 560, 366, C_LAKEHOUSE, flecha=True))

    p.append(rect(30, 372, 820, 86, CAJA, C_LAKEHOUSE, rx=14, ancho_borde=1.5))
    p.append(rect(31, 386, 5, 58, C_LAKEHOUSE, None, rx=2.5))
    p.append(txt(50, 400, "Lakehouse", fill=C_LAKEHOUSE, size=15, weight="700"))
    p.append(txt(50, 422,
                 "Más tablas con transacciones y versiones.", fill=TEXTO, size=12))
    p.append(txt(50, 442,
                 "Ya no es una elección binaria.",
                 fill=SUAVE, size=11.5))

    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 3. ETL vs ELT + costo del almacenamiento
# --------------------------------------------------------------------------
def etl_elt():
    alto = 500
    titulo = ("ETL frente a ELT, y la caída del costo del almacenamiento que "
              "invirtió el orden")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "ETL y ELT: el mismo trabajo, otro orden",
        "Lo que cambió es el orden."))

    # ETL y ELT en dos colores francamente opuestos, y el paso que se mueve
    # —Transform— resaltado en ámbar en las dos filas, para que el ojo lo siga
    # cambiar de lugar.
    C_ETL, C_ELT, C_TRANSFORM, C_COSTO = CIAN, NARANJA, AMBAR, VIOLETA

    filas = [
        ("ETL", 84, C_ETL, ["Extract", "Transform", "Load"],
         "Se transforma antes: guardar era caro."),
        ("ELT", 194, C_ELT, ["Extract", "Load", "Transform"],
         "Carga cruda: guardar ya no cuesta."),
    ]
    xs = [150, 340, 530]
    for nombre, y, color, chips, nota in filas:
        p.append(txt(40, y + 32, nombre, fill=color, size=18, weight="700"))
        for i, chip in enumerate(chips):
            movido = chip == "Transform"
            p.append(caja(xs[i], y, 150, 52,
                          [chip], C_TRANSFORM if movido else color,
                          relleno=TINTE_VERDE if movido else CAJA, size=13.5))
            if i < len(chips) - 1:
                p.append(linea(xs[i] + 150, y + 26, xs[i + 1] - 6, y + 26,
                               color, flecha=True))
        p.append(txt(40, y + 90, nota, fill=SUAVE, size=11.5))

    # El paso que se mueve, dicho también con palabras, en el margen libre de
    # la derecha para no encimarse con las notas de cada fila.
    p.append(txt(850, 116, "Transform es el paso", fill=C_TRANSFORM, size=11.5,
                 anchor="end", weight="600"))
    p.append(txt(850, 133, "que cambia de lugar", fill=C_TRANSFORM, size=11.5,
                 anchor="end", weight="600"))
    p.append(linea(760, 142, 690, 210, C_TRANSFORM, ancho=1.2, punteada=True,
                   flecha=True))

    p.append(linea(30, 292, 850, 292, LINEA, ancho=1, punteada=True))
    p.append(txt(40, 320, "Costo del almacenamiento por GB", fill=C_COSTO,
                 size=14, weight="600"))

    # Costo por GB de almacenamiento en disco, ordenes de magnitud aproximados
    # a partir de las series historicas de precio de HDD. Es una curva de
    # magnitud, no una serie exacta: por eso el eje va en potencias de diez y
    # el pie declara de donde sale.
    anios = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2026]
    usd_gb = [9000.0, 900.0, 16.0, 1.2, 0.09, 0.04, 0.023, 0.015]

    x0, x1, base, tope = 150, 830, 440, 336
    p.append(linea(x0, tope, x0, base, SUAVE, ancho=1))
    p.append(linea(x0, base, x1, base, SUAVE, ancho=1))

    # Eje logaritmico: de 10^-2 a 10^4 USD/GB, una marca por decada.
    lo, hi = -2, 4

    def _y(v):
        return base - (math.log10(v) - lo) / (hi - lo) * (base - tope)

    for exp in range(lo, hi + 1):
        y = _y(10.0 ** exp)
        p.append(linea(x0 - 4, y, x0, y, SUAVE, ancho=1))
        etiqueta = {
            -2: "$0.01", -1: "$0.10", 0: "$1", 1: "$10",
            2: "$100", 3: "$1k", 4: "$10k",
        }[exp]
        p.append(txt(x0 - 8, y + 4, etiqueta, fill=SUAVE, size=10, anchor="end"))
    p.append(txt(x0 - 8, tope - 12, "USD / GB", fill=SUAVE, size=10, anchor="end"))

    puntos = []
    for i, v in enumerate(usd_gb):
        px = x0 + i * ((x1 - x0 - 20) / (len(usd_gb) - 1))
        puntos.append((px, _y(v)))
    # La curva de costo lleva su propio color, distinto del de ETL y del de ELT:
    # es la causa del cambio de orden, no una de las dos rutas.
    d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in puntos)
    p.append(f'<path d="{d}" fill="none" stroke="{C_COSTO}" stroke-width="2.5" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')
    for px, py in puntos:
        p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{C_COSTO}"/>')

    for i in (0, 2, 4, 6, 7):
        px = x0 + i * ((x1 - x0 - 20) / (len(usd_gb) - 1))
        p.append(txt(px, 458, str(anios[i]), fill=SUAVE, size=11, anchor="middle"))

    p.append(txt(470, 378, "La causa del cambio de orden",
                 fill=C_COSTO, size=12, weight="600"))
    p.append(linea(468, 384, 418, 402, C_COSTO, ancho=1.2, flecha=True))

    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 4. Tidy data
# --------------------------------------------------------------------------
def tidy():
    alto = 450
    titulo = ("Tidy data: cada variable es una columna, cada observación una fila "
              "y cada valor una celda")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "Tidy data",
        "Columna es variable; fila es observación."))

    tx, ty, cw, rh = 210, 130, 145, 46
    cabecera = ["país", "año", "casos", "población"]
    datos = [
        ["México", "2024", "1 240", "130.9 M"],
        ["México", "2025", "1 310", "131.5 M"],
        ["Chile", "2024", "240", "19.6 M"],
        ["Chile", "2025", "265", "19.7 M"],
    ]

    # Un color por concepto, y el mismo color en la parte de la tabla que lo
    # encarna: columnas en cian, filas en ámbar, la celda en violeta.
    C_VARIABLE, C_OBSERVACION, C_VALOR = CIAN, AMBAR, VIOLETA

    p.append(rect(tx, ty, cw * 4, rh, TINTE_CIAN, None, rx=0))
    for j, celda in enumerate(cabecera):
        p.append(txt(tx + j * cw + cw / 2, ty + 29, celda, fill=C_VARIABLE, size=13,
                     anchor="middle", weight="700"))
    for i, fila in enumerate(datos):
        fy = ty + rh * (i + 1)
        if i % 2 == 1:
            p.append(rect(tx, fy, cw * 4, rh, PANEL, None, rx=0))
        for j, celda in enumerate(fila):
            p.append(txt(tx + j * cw + cw / 2, fy + 29, celda, fill=TEXTO, size=12.5,
                         anchor="middle"))

    # Los cortes verticales separan variables; los horizontales, observaciones.
    for j in range(5):
        p.append(linea(tx + j * cw, ty, tx + j * cw, ty + rh * 5, C_VARIABLE,
                       ancho=1, opacidad="0.55"))
    for i in range(6):
        p.append(linea(tx, ty + i * rh, tx + cw * 4, ty + i * rh, C_OBSERVACION,
                       ancho=1, opacidad="0.45"))

    # Variables: llave horizontal encima de la tabla.
    p.append(linea(tx, 112, tx + cw * 4, 112, C_VARIABLE, ancho=1.5))
    p.append(linea(tx, 112, tx, 122, C_VARIABLE, ancho=1.5))
    p.append(linea(tx + cw * 4, 112, tx + cw * 4, 122, C_VARIABLE, ancho=1.5))
    p.append(txt(tx + cw * 2, 104, "Variables: una por columna", fill=C_VARIABLE,
                 size=12.5, anchor="middle", weight="600"))

    # Observaciones: llave vertical a la izquierda.
    p.append(linea(196, ty + rh, 196, ty + rh * 5, C_OBSERVACION, ancho=1.5))
    p.append(linea(186, ty + rh, 196, ty + rh, C_OBSERVACION, ancho=1.5))
    p.append(linea(186, ty + rh * 5, 196, ty + rh * 5, C_OBSERVACION, ancho=1.5))
    p.append(txt(176, 246, "Observaciones:", fill=C_OBSERVACION, size=12.5,
                 anchor="end", weight="600"))
    p.append(txt(176, 264, "una por fila", fill=C_OBSERVACION, size=12.5, anchor="end"))

    # Valores: celda resaltada.
    cx, cy = tx + cw * 2, ty + rh * 4
    p.append(rect(cx, cy, cw, rh, TINTE_VIOLETA, C_VALOR, rx=0, ancho_borde=2))
    p.append(txt(cx + cw / 2, cy + 29, "265", fill=TEXTO, size=12.5,
                 anchor="middle", weight="700"))
    p.append(linea(cx + cw / 2, cy + rh, cx + cw / 2, 388, C_VALOR, ancho=1.2,
                   flecha=True))
    p.append(txt(cx + cw / 2, 408, "Valores: uno por celda", fill=C_VALOR,
                 size=12.5, anchor="middle", weight="600"))

    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 5. Calidad de datos: seis dimensiones
# --------------------------------------------------------------------------
def calidad():
    alto = 380
    titulo = ("Las seis dimensiones de la calidad de los datos: completitud, "
              "unicidad, validez, consistencia, exactitud y oportunidad")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "Seis dimensiones de la calidad de los datos",
        "Cada una se revisa por separado."))

    tarjetas = [
        ("Completitud", AMBAR, "¿Faltan valores, o faltan filas enteras?",
         "Falla típica: columna casi vacía."),
        ("Unicidad", MAGENTA, "¿La misma entidad aparece dos veces?",
         "Falla típica: dos IDs, un cliente."),
        ("Validez", CIAN, "¿Respeta las reglas de su dominio?",
         "Falla típica: edad de 200 años."),
        ("Consistencia", VIOLETA, "¿Las fuentes dicen lo mismo?",
         "Falla típica: CRM y ERP distintos."),
        ("Exactitud", VERDE, "¿El valor corresponde a la realidad?",
         "Falla típica: un precio negativo."),
        ("Oportunidad", NARANJA, "¿Está disponible cuando se necesita?",
         "Falla típica: un tablero con retraso."),
    ]
    xs = [20, 305, 590]
    for i, (nombre, color, pregunta, falla) in enumerate(tarjetas):
        x = xs[i % 3]
        y = 92 + (i // 3) * 122
        p.append(rect(x, y, 270, 110, PANEL, color, rx=12, ancho_borde=1.3))
        # Franja superior del color de la dimensión: seis tarjetas, seis colores
        # que se distinguen aunque se mire el diagrama de lejos.
        p.append(rect(x + 12, y + 6, 246, 4, color, None, rx=2))
        p.append(f'<circle cx="{x + 24}" cy="{y + 32}" r="6" fill="{color}"/>')
        p.append(txt(x + 40, y + 37, nombre, fill=color, size=14, weight="700"))
        p.append(txt(x + 20, y + 66, pregunta, fill=TEXTO, size=11.5))
        p.append(txt(x + 20, y + 88, falla, fill=SUAVE, size=11))

    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 6. Idempotencia
# --------------------------------------------------------------------------
def idempotencia():
    alto = 450
    titulo = ("Idempotencia: correr dos veces el mismo paso deja el mismo "
              "resultado, o duplica las filas")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "La misma corrida, dos veces",
        "Uno se reintenta; el otro castiga."))

    # Verde es la corrida que se puede repetir; rojo es la que duplica. Nada
    # mas en el diagrama usa esos dos colores.
    C_BIEN, C_MAL = VERDE, ROJO

    def stack(x, y, n, color, resaltar_desde=None):
        """Filas escritas. Las que sobran —las duplicadas— van en rojo."""
        out = []
        for i in range(n):
            duplicada = resaltar_desde is not None and i >= resaltar_desde
            out.append(rect(
                x, y + i * 26, 140, 22,
                TINTE_ROJO if duplicada else TINTE_VERDE,
                C_MAL if duplicada else color,
                rx=5, ancho_borde=1.8 if duplicada else 1.2,
            ))
        return "".join(out)

    paneles = [
        (30, "Idempotente", C_BIEN,
         "Escribe reemplazando la partición del día.",
         3, None,
         "3 filas", "3 filas",
         "El resultado no cambia nunca."),
        (460, "No idempotente", C_MAL,
         "Inserta sin llave ni borrado.",
         6, 3,
         "3 filas", "6 filas (3 duplicadas)",
         "Duplica lo que no debía."),
    ]

    for px, nombre, color, metodo, n2, dup, c1, c2, veredicto in paneles:
        p.append(rect(px, 80, 390, 320, PANEL, color, rx=14, ancho_borde=1.3))
        p.append(txt(px + 20, 108, nombre, fill=color, size=15, weight="700"))
        p.append(txt(px + 20, 130, metodo, fill=SUAVE, size=11.5))
        p.append(txt(px + 35, 154, "Corrida 1", fill=TEXTO, size=12, weight="600"))
        p.append(txt(px + 215, 154, "Corrida 2", fill=TEXTO, size=12, weight="600"))
        # Las filas legítimas se pintan igual en los dos paneles: lo único que
        # cambia de color es lo que sobra tras el reintento.
        base = C_BIEN if dup is None else SUAVE
        p.append(stack(px + 35, 164, 3, base))
        p.append(stack(px + 215, 164, n2, base, resaltar_desde=dup))
        p.append(txt(px + 105, 344, c1, fill=SUAVE, size=11.5, anchor="middle"))
        p.append(txt(px + 285, 344, c2, fill=color, size=11.5, anchor="middle",
                     weight="600"))
        p.append(txt(px + 195, 378, veredicto, fill=TEXTO, size=12, anchor="middle"))

    p.append(txt(225, 208, "=", fill=C_BIEN, size=28, anchor="middle", weight="700"))
    p.append(txt(655, 250, "\u2260", fill=C_MAL, size=28, anchor="middle", weight="700"))

    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 7. Batch, micro-batch y streaming
# --------------------------------------------------------------------------
def tiempo():
    """Los carriles van en el orden del texto; el color, en orden de latencia.

    LATENCIA es una rampa de frío a caliente: azul es lo más lento y rojo lo
    más fresco. El carril de cada modo toma el tono que le corresponde por su
    latencia. CDC no aparece como carril: es una técnica de captura, no un
    régimen temporal, y se entrega por batch o por streaming (ver prosa).
    """
    alto = 470
    titulo = ("Batch, micro-batch y streaming sobre una línea de tiempo, "
              "con la latencia de cada uno")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "Cuando un dato se vuelve verdad",
        "Los tres separan cuánto tardan."))

    lento, medio, _, inmediato = LATENCIA
    x0, x1 = 230, 830
    carriles = [
        ("Batch", "latencia ~24 h", lento,
         [(250, 60), (560, 60)],
         "Una corrida al día."),
        ("Micro-batch", "latencia ~5 min", medio,
         [(248 + i * 72, 18) for i in range(9)],
         "Lotes pequeños y frecuentes."),
        ("Streaming", "latencia < 1 s", inmediato,
         [(240 + i * 24, 4) for i in range(25)],
         "Cada evento, al llegar."),
    ]

    # Tres carriles en vez de cuatro: el espacio que suelta CDC se reparte
    # entre los tres para que respiren, no para meter mas texto.
    for i, (nombre, latencia, color, marcas, nota) in enumerate(carriles):
        cy = 150 + i * 105
        p.append(txt(24, cy - 8, nombre, fill=color, size=15, weight="700"))
        p.append(txt(24, cy + 13, latencia, fill=SUAVE, size=12))
        p.append(txt(24, cy + 33, nota, fill=SUAVE, size=11, opacity="0.85"))
        p.append(rect(x0, cy - 19, x1 - x0, 38, PANEL, color, rx=8, ancho_borde=1,
                      opacidad="0.95"))
        for mx, mw in marcas:
            if mx + mw > x1 - 6:
                continue
            p.append(rect(mx, cy - 12, mw, 24, color, None, rx=3, opacidad="0.9"))

    p.append(linea(x0, 410, x1, 410, SUAVE, ancho=1.2, flecha=True))
    p.append(txt(x0, 430, "tiempo", fill=SUAVE, size=11.5))

    # La rampa, ya ordenada por latencia: es la lectura que los carriles no dan,
    # porque esos siguen el orden en que el texto los explica.
    p.append(txt(24, 456, "de más lento a más fresco:", fill=SUAVE, size=11.5))
    p.append(leyenda(196, 453, [
        (lento, "batch"),
        (medio, "micro-batch"),
        (inmediato, "streaming"),
    ]))

    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 8. Ciclo de vida de un proyecto de datos
# --------------------------------------------------------------------------
def ciclo():
    """Cuatro etapas en fila, con dos retornos explícitos.

    El lazo NO es estrictamente hacia adelante: EDA devuelve a ETL/ELT (faltan
    columnas) y Producción devuelve a ETL/ELT (degradación). Los retornos se
    dibujan en un color propio, punteados y curvos por debajo de la fila, para
    que no se confundan con las flechas de avance — son la idea central de la
    página, no un adorno.
    """
    alto = 440
    titulo = ("Ciclo de vida de un proyecto de datos: ETL/ELT, EDA, "
              "entrenamiento o análisis y producción, con dos retornos "
              "explícitos hacia ETL/ELT")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "Las cuatro etapas, con sus retornos",
        "No es una secuencia lineal."))

    # El color avanza con la etapa: cuatro pasos de un mismo recorrido de tono.
    nombres = ["ETL / ELT", "EDA", "Entrenamiento o análisis", "Producción"]
    etapas = list(zip(nombres, CICLO))
    bw, bh = 172, 66
    y = 140
    xs = [30, 246, 462, 678]
    centros = [(x + bw / 2, y + bh / 2) for x in xs]
    base_y = y + bh

    # Flechas de avance: cada etapa alimenta a la siguiente, coloreada por la
    # etapa de origen. Solo van hacia adelante — el retorno es otra cosa.
    for i in range(3):
        color = etapas[i][1]
        p.append(linea(xs[i] + bw, y + bh / 2, xs[i + 1], y + bh / 2, color,
                       ancho=2, flecha=True))

    for i, (nombre, color) in enumerate(zip(nombres, [c for _, c in etapas])):
        p.append(caja(xs[i], y, bw, bh, [nombre], color, size=12.5))
        p.append(f'<circle cx="{xs[i] + 24:.1f}" cy="{y + 20:.1f}" r="11" '
                 f'fill="{color}" opacity="0.9"/>')
        p.append(txt(xs[i] + 24, y + 24.5, str(i + 1), fill=FONDO, size=12,
                     anchor="middle", weight="700"))

    # Retornos: dos flechas hacia atrás, en su propio color, punteadas y
    # curvas por debajo de la fila. Llegan a puntos distintos del borde
    # inferior de ETL/ELT para que sus dos puntas no se encimen.
    C_RETORNO = AMBAR
    etl_cx, eda_cx, prod_cx = centros[0][0], centros[1][0], centros[3][0]

    def retorno(x1, x2, profundidad):
        d = (f'M{x1:.1f},{base_y:.1f} C{x1:.1f},{base_y + profundidad:.1f} '
             f'{x2:.1f},{base_y + profundidad:.1f} {x2:.1f},{base_y:.1f}')
        return (f'<path d="{d}" fill="none" stroke="{C_RETORNO}" stroke-width="2" '
                f'stroke-dasharray="6 5" marker-end="url(#{_id_flecha(C_RETORNO)})"/>')

    p.append(retorno(eda_cx, etl_cx + 16, 55))
    p.append(retorno(prod_cx, etl_cx - 16, 120))

    # Cada etiqueta va justo debajo de la cresta de SU curva (medida por bezier),
    # y no a medio camino entre las dos cajas: la curva profunda pasa por ahí.
    p.append(txt((eda_cx + etl_cx) / 2, base_y + 57, "EDA devuelve a extracción",
                 fill=C_RETORNO, size=11.5, anchor="middle", weight="600"))
    p.append(txt((prod_cx + etl_cx) / 2, base_y + 114,
                 "producción devuelve al principio", fill=C_RETORNO, size=11.5,
                 anchor="middle", weight="600"))

    p.append(leyenda(30, alto - 22, [
        (etapas[0][1], "avance"),
        (C_RETORNO, "retorno"),
    ]))

    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
DIAGRAMAS = {
    "d-dag": dag,
    "d-schema": schema,
    "d-etl-elt": etl_elt,
    "d-tidy": tidy,
    "d-calidad": calidad,
    "d-idempotencia": idempotencia,
    "d-tiempo": tiempo,
    "d-ciclo": ciclo,
}


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for slug, generador in DIAGRAMAS.items():
        destino = ASSETS / f"{slug}.svg"
        destino.write_text(generador(), encoding="utf-8")
        print(f"  {destino.name}")
    print(f"generados {len(DIAGRAMAS)} archivos en {ASSETS}")


if __name__ == "__main__":
    main()
