"""Genera los ocho diagramas SVG de la unidad de Pipeline de Datos.

Deterministico y sin dependencias externas: el SVG se escribe a mano. Este
archivo es la unica fuente de verdad de esos diagramas — editar un .svg a mano
es un error que tools/test_diagramas.py detecta.

Colores tomados de skins/fdd-eva.yaml. Cada diagrama pinta su propio fondo y
usa `fill` explicito en todo texto, para que se lea igual en tema claro y en
tema oscuro.
"""
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
ROJO = "#ff8a7a"

FUENTE = "system-ui, -apple-system, Segoe UI, sans-serif"
ANCHO = 880
COLORES_FLECHA = (LINEA, VERDE, AMBAR, CIAN, VIOLETA, NARANJA, TEAL, SUAVE)


# --------------------------------------------------------------------------
# Primitivas
# --------------------------------------------------------------------------
def _id_flecha(color):
    return "f" + color.lstrip("#")


def _defs():
    partes = ["<defs>"]
    for color in COLORES_FLECHA:
        partes.append(
            f'<marker id="{_id_flecha(color)}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
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


def linea(x1, y1, x2, y2, color=LINEA, ancho=1.5, punteada=False, flecha=False):
    d = ' stroke-dasharray="5 4"' if punteada else ""
    m = f' marker-end="url(#{_id_flecha(color)})"' if flecha else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{ancho}"{d}{m}/>'
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


def pie(alto, texto):
    return txt(30, alto - 18, texto, fill=SUAVE, size=11.5)


# --------------------------------------------------------------------------
# 1. El pipeline como DAG
# --------------------------------------------------------------------------
def dag():
    alto = 410
    titulo = ("Un pipeline de datos es un grafo dirigido acíclico: las etapas se "
              "bifurcan y vuelven a converger")
    col = [22, 194, 366, 538, 710]
    w, h = 148, 48

    nodos = {
        "api": (0, 110, ["Ventas", "(API)"], CIAN),
        "csv": (0, 200, ["Catálogo", "(CSV)"], CIAN),
        "clics": (0, 290, ["Clics", "(stream)"], CIAN),
        "batch": (1, 135, ["Ingesta batch"], VERDE),
        "cont": (1, 265, ["Ingesta continua"], VERDE),
        "limpieza": (2, 80, ["Limpieza"], AMBAR),
        "dim": (2, 190, ["Dimensión", "producto"], AMBAR),
        "ses": (2, 300, ["Sesiones"], AMBAR),
        "hechos": (3, 190, ["Tabla de hechos"], VIOLETA),
        "tablero": (4, 130, ["Tablero"], TEAL),
        "modelo": (4, 250, ["Modelo"], TEAL),
    }
    aristas = [
        ("api", "batch"), ("csv", "batch"), ("clics", "cont"),
        ("batch", "limpieza"), ("batch", "dim"), ("cont", "ses"),
        ("limpieza", "hechos"), ("dim", "hechos"), ("ses", "hechos"),
        ("hechos", "tablero"), ("hechos", "modelo"),
    ]

    p = [marco(alto, titulo)]
    p.append(encabezado("Un pipeline es un DAG, no una flecha",
                        "El orden no lo pone el autor: lo imponen las dependencias."))

    for origen, destino in aristas:
        co, yo, _, _ = nodos[origen]
        cd, yd, _, _ = nodos[destino]
        p.append(curva(col[co] + w, yo + h / 2, col[cd], yd + h / 2))

    for _, (c, y, lineas, color) in nodos.items():
        p.append(caja(col[c], y, w, h, lineas, color, size=12.5))

    etiquetas = ["Fuentes", "Ingesta", "Transformación", "Modelo", "Consumo"]
    for i, etq in enumerate(etiquetas):
        p.append(txt(col[i] + w / 2, 368, etq, fill=SUAVE, size=11.5, anchor="middle"))

    p.append(pie(alto, "Si una rama falla, solo se vuelve a correr esa rama: "
                       "no hace falta rehacer el pipeline entero."))
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
        "Schema-on-write valida al escribir; schema-on-read acepta todo y valida al leer."))

    paneles = [
        (30, "Schema-on-write", "El esquema se declara antes. Lo que no encaja, no entra.",
         VERDE, [
             (["Base de datos relacional"],
              ["Esquema fijo y transacciones.",
               "Sirve a la aplicación, no al análisis."]),
             (["Data warehouse"],
              ["Esquema modelado para consultar.",
               "Entra dato ya limpio y conformado."]),
         ]),
        (460, "Schema-on-read", "El dato se guarda tal cual llegó. La forma se impone al leerlo.",
         AMBAR, [
             (["Data lake"],
              ["Archivos crudos, cualquier formato.",
               "Barato, flexible, sin promesas."]),
             (["El costo de no tener contrato"],
              ["Nadie garantiza la forma:",
               "quien lee paga la limpieza, cada vez."]),
         ]),
    ]

    for px, ptitulo, psub, color, cajas in paneles:
        p.append(rect(px, 76, 390, 262, PANEL, LINEA, rx=14, ancho_borde=1.2))
        p.append(txt(px + 18, 104, ptitulo, fill=color, size=15, weight="700"))
        p.append(txt(px + 18, 124, psub, fill=SUAVE, size=11.5))
        for i, (nombre, desc) in enumerate(cajas):
            by = 140 + i * 100
            p.append(rect(px + 18, by, 354, 88, CAJA, color, rx=10, ancho_borde=1.2))
            p.append(txt(px + 34, by + 28, nombre[0], fill=TEXTO, size=13.5, weight="600"))
            for j, d in enumerate(desc):
                p.append(txt(px + 34, by + 50 + j * 18, d, fill=SUAVE, size=11.5))

    p.append(linea(225, 338, 320, 366, LINEA, flecha=True))
    p.append(linea(655, 338, 560, 366, LINEA, flecha=True))

    p.append(rect(30, 372, 820, 86, CAJA, VIOLETA, rx=14, ancho_borde=1.5))
    p.append(txt(50, 400, "Lakehouse", fill=VIOLETA, size=15, weight="700"))
    p.append(txt(50, 422,
                 "Los archivos crudos del lake, más una capa de tablas con esquema, "
                 "transacciones y versiones.", fill=TEXTO, size=12))
    p.append(txt(50, 442,
                 "La frontera entre lake y warehouse dejó de ser una elección binaria.",
                 fill=SUAVE, size=11.5))

    p.append(pie(alto, "La pregunta útil no es qué producto usar, sino en qué momento "
                       "alguien se compromete con la forma del dato."))
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
        "Extract, Transform y Load no cambiaron. Cambió cuando conviene transformar."))

    filas = [
        ("ETL", 84, VERDE, ["Extract", "Transform", "Load"],
         "Transformar antes de cargar: el almacenamiento era caro, "
         "así que solo entraba lo ya modelado."),
        ("ELT", 194, AMBAR, ["Extract", "Load", "Transform"],
         "Cargar crudo y transformar dentro del warehouse: el cómputo es elástico "
         "y guardar ya casi no cuesta."),
    ]
    xs = [150, 340, 530]
    for nombre, y, color, chips, nota in filas:
        p.append(txt(40, y + 32, nombre, fill=color, size=18, weight="700"))
        for i, chip in enumerate(chips):
            p.append(caja(xs[i], y, 150, 52, [chip], color, size=13.5))
            if i < len(chips) - 1:
                p.append(linea(xs[i] + 150, y + 26, xs[i + 1] - 6, y + 26,
                               color, flecha=True))
        p.append(txt(40, y + 90, nota, fill=SUAVE, size=11.5))

    p.append(linea(30, 292, 850, 292, LINEA, ancho=1, punteada=True))
    p.append(txt(40, 320, "Costo del almacenamiento por GB", fill=TEXTO,
                 size=14, weight="600"))

    x0, x1, base, tope = 120, 830, 440, 344
    p.append(linea(x0, tope, x0, base, SUAVE, ancho=1))
    p.append(linea(x0, base, x1, base, SUAVE, ancho=1))

    valores = [1.0, 0.42, 0.19, 0.09, 0.045, 0.022, 0.012]
    puntos = []
    for i, v in enumerate(valores):
        px = x0 + i * (700 / (len(valores) - 1))
        py = base - v * 88
        puntos.append((px, py))
    d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in puntos)
    p.append(f'<path d="{d}" fill="none" stroke="{CIAN}" stroke-width="2.5" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')
    for px, py in puntos:
        p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{CIAN}"/>')

    for px, etq in [(120, "1990"), (353, "2005"), (587, "2020"), (820, "hoy")]:
        p.append(txt(px, 458, etq, fill=SUAVE, size=11, anchor="middle"))

    p.append(txt(450, 378, "Esta caída es la causa del cambio de orden",
                 fill=AMBAR, size=12, weight="600"))
    p.append(linea(448, 384, 406, 420, AMBAR, ancho=1.2, flecha=True))

    p.append(pie(alto, "Guardar dejó de ser lo caro; lo caro pasó a ser el cómputo "
                       "y el tiempo de quien modela."))
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
        "Una variable por columna, una observación por fila, un valor por celda."))

    tx, ty, cw, rh = 210, 130, 145, 46
    cabecera = ["país", "año", "casos", "población"]
    datos = [
        ["México", "2024", "1 240", "130.9 M"],
        ["México", "2025", "1 310", "131.5 M"],
        ["Chile", "2024", "240", "19.6 M"],
        ["Chile", "2025", "265", "19.7 M"],
    ]

    p.append(rect(tx, ty, cw * 4, rh, CAJA, None, rx=0))
    for j, celda in enumerate(cabecera):
        p.append(txt(tx + j * cw + cw / 2, ty + 29, celda, fill=VERDE, size=13,
                     anchor="middle", weight="700"))
    for i, fila in enumerate(datos):
        fy = ty + rh * (i + 1)
        if i % 2 == 1:
            p.append(rect(tx, fy, cw * 4, rh, PANEL, None, rx=0))
        for j, celda in enumerate(fila):
            p.append(txt(tx + j * cw + cw / 2, fy + 29, celda, fill=TEXTO, size=12.5,
                         anchor="middle"))

    for j in range(5):
        p.append(linea(tx + j * cw, ty, tx + j * cw, ty + rh * 5, LINEA, ancho=1))
    for i in range(6):
        p.append(linea(tx, ty + i * rh, tx + cw * 4, ty + i * rh, LINEA, ancho=1))

    # Variables: llave horizontal encima de la tabla.
    p.append(linea(tx, 112, tx + cw * 4, 112, CIAN, ancho=1.5))
    p.append(linea(tx, 112, tx, 122, CIAN, ancho=1.5))
    p.append(linea(tx + cw * 4, 112, tx + cw * 4, 122, CIAN, ancho=1.5))
    p.append(txt(tx + cw * 2, 104, "Variables: una por columna", fill=CIAN,
                 size=12.5, anchor="middle", weight="600"))

    # Observaciones: llave vertical a la izquierda.
    p.append(linea(196, ty + rh, 196, ty + rh * 5, AMBAR, ancho=1.5))
    p.append(linea(186, ty + rh, 196, ty + rh, AMBAR, ancho=1.5))
    p.append(linea(186, ty + rh * 5, 196, ty + rh * 5, AMBAR, ancho=1.5))
    p.append(txt(176, 246, "Observaciones:", fill=AMBAR, size=12.5, anchor="end",
                 weight="600"))
    p.append(txt(176, 264, "una por fila", fill=AMBAR, size=12.5, anchor="end"))

    # Valores: celda resaltada.
    cx, cy = tx + cw * 2, ty + rh * 4
    p.append(rect(cx, cy, cw, rh, "#16302a", VIOLETA, rx=0, ancho_borde=2))
    p.append(txt(cx + cw / 2, cy + 29, "265", fill=TEXTO, size=12.5,
                 anchor="middle", weight="700"))
    p.append(linea(cx + cw / 2, cy + rh, cx + cw / 2, 388, VIOLETA, ancho=1.2,
                   flecha=True))
    p.append(txt(cx + cw / 2, 408, "Valores: uno por celda", fill=VIOLETA,
                 size=12.5, anchor="middle", weight="600"))

    p.append(pie(alto, "Si una celda guarda dos cosas, o una fila mezcla dos "
                       "observaciones, la tabla todavía no está lista."))
    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 5. Calidad de datos: seis dimensiones
# --------------------------------------------------------------------------
def calidad():
    alto = 380
    titulo = ("Las seis dimensiones de la calidad de los datos: exactitud, "
              "completitud, formato, consistencia, duplicación e integridad")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "Seis dimensiones de la calidad de los datos",
        "Cada dimensión se revisa con una pregunta distinta; ninguna cubre a las otras."))

    tarjetas = [
        ("Exactitud", VERDE, "¿El valor corresponde a la realidad?",
         "Falla típica: un precio negativo."),
        ("Completitud", AMBAR, "¿Faltan valores, o faltan filas enteras?",
         "Falla típica: 30% de la columna vacía."),
        ("Formato", CIAN, "¿La forma es la esperada?",
         "Falla típica: fechas en dos formatos."),
        ("Consistencia", VIOLETA, "¿Las fuentes dicen lo mismo?",
         "Falla típica: el CRM y el ERP no cuadran."),
        ("Duplicación", NARANJA, "¿La misma entidad aparece dos veces?",
         "Falla típica: dos IDs para un cliente."),
        ("Integridad", TEAL, "¿Las relaciones entre tablas se sostienen?",
         "Falla típica: una venta sin cliente."),
    ]
    xs = [20, 305, 590]
    for i, (nombre, color, pregunta, falla) in enumerate(tarjetas):
        x = xs[i % 3]
        y = 92 + (i // 3) * 122
        p.append(rect(x, y, 270, 110, PANEL, color, rx=12, ancho_borde=1.3))
        p.append(f'<circle cx="{x + 24}" cy="{y + 28}" r="6" fill="{color}"/>')
        p.append(txt(x + 40, y + 33, nombre, fill=color, size=14, weight="700"))
        p.append(txt(x + 20, y + 64, pregunta, fill=TEXTO, size=11.5))
        p.append(txt(x + 20, y + 86, falla, fill=SUAVE, size=11))

    p.append(pie(alto, "Un dato puede estar completo y bien formado y aún así "
                       "ser falso: las dimensiones no se sustituyen entre sí."))
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
        "Un paso idempotente se puede reintentar. Uno que no lo es, castiga cada reintento."))

    def stack(x, y, n, color, resaltar_desde=None):
        out = []
        for i in range(n):
            resaltado = resaltar_desde is not None and i >= resaltar_desde
            out.append(rect(x, y + i * 26, 140, 22,
                            "#16302a" if not resaltado else "#3a231c",
                            color, rx=5, ancho_borde=1.2))
        return "".join(out)

    paneles = [
        (30, "Idempotente", VERDE,
         "Escribe reemplazando la partición del día.",
         3, None,
         "3 filas", "3 filas",
         "El resultado no cambia: se puede reintentar sin miedo."),
        (460, "No idempotente", NARANJA,
         "Inserta filas sin llave ni borrado previo.",
         6, 3,
         "3 filas", "6 filas (3 duplicadas)",
         "Cada reintento inventa datos que nadie produjo."),
    ]

    for px, nombre, color, metodo, n2, dup, c1, c2, veredicto in paneles:
        p.append(rect(px, 80, 390, 320, PANEL, color, rx=14, ancho_borde=1.3))
        p.append(txt(px + 20, 108, nombre, fill=color, size=15, weight="700"))
        p.append(txt(px + 20, 130, metodo, fill=SUAVE, size=11.5))
        p.append(txt(px + 35, 154, "Corrida 1", fill=TEXTO, size=12, weight="600"))
        p.append(txt(px + 215, 154, "Corrida 2", fill=TEXTO, size=12, weight="600"))
        p.append(stack(px + 35, 164, 3, color))
        p.append(stack(px + 215, 164, n2, color, resaltar_desde=dup))
        p.append(txt(px + 105, 344, c1, fill=SUAVE, size=11.5, anchor="middle"))
        p.append(txt(px + 285, 344, c2, fill=color, size=11.5, anchor="middle",
                     weight="600"))
        p.append(txt(px + 195, 378, veredicto, fill=TEXTO, size=12, anchor="middle"))

    p.append(txt(225, 208, "=", fill=VERDE, size=28, anchor="middle", weight="700"))
    p.append(txt(655, 250, "\u2260", fill=NARANJA, size=28, anchor="middle", weight="700"))

    p.append(pie(alto, "El reintento no es un caso raro: es la operación normal de "
                       "cualquier orquestador."))
    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 7. Batch, micro-batch, streaming y CDC
# --------------------------------------------------------------------------
def tiempo():
    alto = 436
    titulo = ("Batch, micro-batch, streaming y CDC sobre una línea de tiempo, "
              "con la latencia de cada uno")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "Cuando un dato se vuelve verdad",
        "Los cuatro modos mueven los mismos datos; los separa cuánto tardan en estar disponibles."))

    x0, x1 = 230, 830
    carriles = [
        ("Batch", "latencia ~24 h", VERDE,
         [(250, 60), (560, 60)],
         "Una corrida al día sobre todo el período."),
        ("Micro-batch", "latencia ~5 min", AMBAR,
         [(248 + i * 72, 18) for i in range(9)],
         "Lotes pequeños y frecuentes; misma lógica que batch."),
        ("Streaming", "latencia < 1 s", CIAN,
         [(240 + i * 24, 4) for i in range(25)],
         "Cada evento se procesa al llegar."),
        ("CDC", "latencia de segundos", NARANJA,
         [(252, 10), (300, 10), (388, 10), (402, 10), (470, 10),
          (560, 10), (604, 10), (690, 10), (770, 10)],
         "Solo viaja lo que cambió en la fuente."),
    ]

    for i, (nombre, latencia, color, marcas, nota) in enumerate(carriles):
        cy = 120 + i * 74
        p.append(txt(24, cy - 6, nombre, fill=color, size=14, weight="700"))
        p.append(txt(24, cy + 12, latencia, fill=SUAVE, size=11.5))
        p.append(txt(24, cy + 30, nota, fill=SUAVE, size=10, opacity="0.85"))
        p.append(rect(x0, cy - 17, x1 - x0, 34, PANEL, LINEA, rx=8, ancho_borde=1))
        for mx, mw in marcas:
            if mx + mw > x1 - 6:
                continue
            p.append(rect(mx, cy - 11, mw, 22, color, None, rx=3, opacidad="0.9"))

    p.append(linea(x0, 384, x1, 384, SUAVE, ancho=1.2, flecha=True))
    p.append(txt(x0, 404, "tiempo", fill=SUAVE, size=11.5))

    p.append(pie(alto, "Elegir el modo es elegir cuánta frescura se paga: más "
                       "frescura, más maquinaria que sostener."))
    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# 8. Ciclo de vida de un proyecto de datos
# --------------------------------------------------------------------------
def ciclo():
    alto = 470
    titulo = ("Ciclo de vida de un proyecto de datos: un lazo de seis etapas que "
              "vuelve a empezar")
    p = [marco(alto, titulo)]
    p.append(encabezado(
        "Ciclo de vida de un proyecto de datos",
        "No es una lista de pasos que se terminan: es un lazo que vuelve a la pregunta."))

    cx, cy, rx, ry = 440, 250, 290, 145
    bw, bh = 210, 52
    etapas = [
        ("Pregunta y alcance", VERDE),
        ("Adquisición de datos", CIAN),
        ("Preparación y limpieza", AMBAR),
        ("Análisis y modelado", VIOLETA),
        ("Despliegue y entrega", TEAL),
        ("Monitoreo y aprendizaje", NARANJA),
    ]
    angulos = [-90, -30, 30, 90, 150, 210]
    centros = []
    for a in angulos:
        r = math.radians(a)
        centros.append((cx + rx * math.cos(r), cy + ry * math.sin(r)))

    def borde_caja(c, hacia):
        """Punto donde la recta c->hacia sale de la caja centrada en c."""
        dx, dy = hacia[0] - c[0], hacia[1] - c[1]
        hw, hh = bw / 2 + 8, bh / 2 + 8
        escalas = []
        if abs(dx) > 1e-6:
            escalas.append(hw / abs(dx))
        if abs(dy) > 1e-6:
            escalas.append(hh / abs(dy))
        t = min(escalas)
        return c[0] + dx * t, c[1] + dy * t

    for i in range(6):
        c1, c2 = centros[i], centros[(i + 1) % 6]
        inicio = borde_caja(c1, c2)
        fin = borde_caja(c2, c1)
        mx, my = (inicio[0] + fin[0]) / 2, (inicio[1] + fin[1]) / 2
        vx, vy = mx - cx, my - cy
        norma = math.hypot(vx, vy) or 1.0
        ctrl = (mx + vx / norma * 34, my + vy / norma * 34)
        color = etapas[i][1]
        p.append(
            f'<path d="M{inicio[0]:.1f},{inicio[1]:.1f} Q{ctrl[0]:.1f},{ctrl[1]:.1f} '
            f'{fin[0]:.1f},{fin[1]:.1f}" fill="none" stroke="{color}" '
            f'stroke-width="1.8" opacity="0.85" '
            f'marker-end="url(#{_id_flecha(color)})"/>'
        )

    for i, ((nombre, color), (px, py)) in enumerate(zip(etapas, centros)):
        bx, by = px - bw / 2, py - bh / 2
        p.append(rect(bx, by, bw, bh, CAJA, color, rx=12, ancho_borde=1.5))
        p.append(f'<circle cx="{bx + 26:.1f}" cy="{by + 26:.1f}" r="12" '
                 f'fill="{color}" opacity="0.9"/>')
        p.append(txt(bx + 26, by + 31, str(i + 1), fill=FONDO, size=13,
                     anchor="middle", weight="700"))
        p.append(txt(bx + 46, by + 31, nombre, fill=TEXTO, size=12, weight="600"))

    p.append(txt(cx, 240, "El ciclo se repite", fill=VERDE, size=15,
                 anchor="middle", weight="700"))
    p.append(txt(cx, 264, "cada vuelta cambia la pregunta", fill=SUAVE, size=12.5,
                 anchor="middle"))

    p.append(pie(alto, "El monitoreo no cierra el proyecto: es lo que produce la "
                       "siguiente pregunta."))
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
