"""Genera los ocho diagramas SVG de la unidad de Expresiones regulares.

Mismo patron que gen_diagramas.py de este repo y que gen_computabilidad.py de
ia_o26: paleta en constantes, una funcion por diagrama que devuelve una cadena
SVG completa, y un catalogo DIAGRAMAS que el generador y su prueba comparten
como unica fuente de "que diagramas existen".

Este archivo es la unica fuente de verdad de esos ocho SVG. Editar un .svg a
mano es un error que tools/test_gen_regex.py detecta.

Los ids llevan prefijo "rx-" a proposito: los ids de objeto numerado de Raya
son unicos en TODO el curso, no por pagina.

Cada SVG hornea su propio fondo y usa `fill` explicito en todo texto, para que
se lea igual en tema claro y en tema oscuro. La raiz <svg> lleva width y height
propios ademas de viewBox: el sitio incrusta estos diagramas con <img>, y sin
tamano intrinseco el navegador cae al tamano por omision de un elemento
reemplazado (~300x150 CSS px) en vez de llenar el contenedor de la figura.
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/6_expresiones_regulares/_assets"

# Paleta de skins/fdd-eva.yaml.
FONDO = "#0b0f12"          # color.page
PANEL = "#141b20"          # color.surface
TEXTO = "#e8f0e8"          # color.text
SUAVE = "#a7b8ad"          # color.muted
LINEA = "#4a7a63"          # color.border
ACENTO = "#7ef29d"         # color.accent
TINTE = "#16302a"          # color.accent_soft
AMBAR = "#ffc857"          # graph.group_2
CIAN = "#6fd8e8"           # graph.group_3
VIOLETA = "#c9a7ff"        # graph.group_4
ROJO = "#ff8a7a"           # color.danger

FUENTE = "system-ui, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"

# Todo color que pueda terminar una flecha necesita su propio marker.
COLORES_FLECHA = (LINEA, ACENTO, AMBAR, CIAN, VIOLETA, ROJO, SUAVE, TEXTO)


def _marca(color):
    """Id determinista del marker de punta de flecha para un color."""
    return "f" + color.lstrip("#")


def marco(ancho, alto, aria):
    """Etiqueta <svg> raiz, fondo horneado y un marker por color de flecha."""
    defs = "".join(
        f'<marker id="{_marca(c)}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>'
        for c in COLORES_FLECHA
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
        f'viewBox="0 0 {ancho} {alto}" role="img" aria-label="{escape(aria)}">'
        f'<rect x="0" y="0" width="{ancho}" height="{alto}" rx="16" fill="{FONDO}"/>'
        f"<defs>{defs}</defs>"
    )


def cierre():
    return "</svg>"


def texto(x, y, s, color=TEXTO, tam=15, anclaje="middle", peso="normal"):
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-family="{FUENTE}" '
        f'font-size="{tam}" font-weight="{peso}" text-anchor="{anclaje}">'
        f"{escape(s)}</text>"
    )


def teclado(x, y, s, color=ACENTO, tam=17, anclaje="middle", peso="600"):
    """Texto monoespaciado: patrones, cadenas y todo lo que se teclea."""
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-family="{MONO}" '
        f'font-size="{tam}" font-weight="{peso}" text-anchor="{anclaje}">'
        f"{escape(s)}</text>"
    )


def caja(x, y, w, h, relleno="none", borde=LINEA, radio=10, grosor=2):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radio}" '
        f'fill="{relleno}" stroke="{borde}" stroke-width="{grosor}"/>'
    )


def flecha(x1, y1, x2, y2, color=ACENTO, grosor=2):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{grosor}" marker-end="url(#{_marca(color)})"/>'
    )


def curva(x1, y1, x2, y2, comba=40, color=LINEA, grosor=2):
    """Arista curva entre dos puntos, con punta de flecha."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    largo = max((dx * dx + dy * dy) ** 0.5, 1)
    cx, cy = mx - dy / largo * comba, my + dx / largo * comba
    return (
        f'<path d="M {x1} {y1} Q {cx} {cy} {x2} {y2}" fill="none" '
        f'stroke="{color}" stroke-width="{grosor}" '
        f'marker-end="url(#{_marca(color)})"/>'
    )


def estado(x, y, etiqueta, r=32, borde=LINEA, color_texto=TEXTO, doble=False):
    """Un estado del automata: circulo con su nombre dentro."""
    p = [
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{FONDO}" stroke="{borde}" '
        f'stroke-width="2"/>'
    ]
    if doble:
        p.append(
            f'<circle cx="{x}" cy="{y}" r="{r - 6}" fill="none" stroke="{borde}" '
            f'stroke-width="2"/>'
        )
    p.append(texto(x, y + 6, etiqueta, color_texto, 16, peso="600"))
    return "".join(p)


def arco(x1, y1, x2, y2, prof=60, color=LINEA, grosor=2):
    """Arco entre dos puntos con comba vertical explicita.

    `prof` positivo comba hacia abajo y negativo hacia arriba. A diferencia de
    curva(), la direccion no depende del sentido en que se recorra la arista:
    dos aristas opuestas entre los mismos estados no se cruzan.
    """
    dx = x2 - x1
    return (
        f'<path d="M {x1} {y1} C {x1 + dx * 0.28} {y1 + prof}, '
        f'{x2 - dx * 0.28} {y2 + prof}, {x2} {y2}" fill="none" '
        f'stroke="{color}" stroke-width="{grosor}" '
        f'marker-end="url(#{_marca(color)})"/>'
    )


def cima_arco(y, prof):
    """Ordenada aproximada del punto medio de un arco, para colgarle su chip."""
    return y + prof * 0.75


def bucle(x, y, r=32, color=LINEA):
    """Bucle sobre si mismo, dibujado arriba del estado."""
    return (
        f'<path d="M {x - 14} {y - r + 4} C {x - 42} {y - r - 48}, '
        f'{x + 42} {y - r - 48}, {x + 14} {y - r + 4}" fill="none" '
        f'stroke="{color}" stroke-width="2" marker-end="url(#{_marca(color)})"/>'
    )


def celda(x, y, w, h, simbolo, borde=LINEA, color=TEXTO, relleno=FONDO, tam=20):
    """Una celda de cinta: cuadro con un caracter dentro."""
    return (
        caja(x, y, w, h, relleno, borde, radio=6, grosor=2)
        + teclado(x + w / 2, y + h / 2 + tam / 3, simbolo, color, tam)
    )


def chip(x, y, etiqueta, color=ACENTO, ancho=None, tam=15):
    """Etiqueta de transicion: recuadro pequeno sobre una arista."""
    ancho = ancho if ancho is not None else max(30, 11 * len(etiqueta) + 16)
    return (
        f'<rect x="{x - ancho / 2}" y="{y - 14}" width="{ancho}" height="28" '
        f'rx="6" fill="{FONDO}" stroke="{color}" stroke-width="1.2"/>'
        + teclado(x, y + 5, etiqueta, color, tam)
    )


# --------------------------------------------------------------------------
# Pagina 1: que es una regex
# --------------------------------------------------------------------------

def rx_que_es():
    """Patron y texto entran; el motor decide que lineas salen."""
    ancho, alto = 980, 366
    aria = (
        "Un patron y un archivo de texto entran a un motor de expresiones "
        "regulares; el motor recorre el texto linea por linea y deja salir "
        "solo las lineas donde encontro el patron"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Qué hace una expresión regular", TEXTO, 21, peso="600"))

    p.append(caja(40, 82, 240, 62, PANEL, ACENTO))
    p.append(texto(160, 105, "el patrón", SUAVE, 14))
    p.append(teclado(160, 131, "ana", ACENTO, 19))

    p.append(caja(40, 172, 240, 108, PANEL, CIAN))
    p.append(texto(160, 195, "el texto", SUAVE, 14))
    for i, linea in enumerate(("Ana Ruiz", "Mariana Solís", "Beto Lara")):
        p.append(teclado(160, 220 + i * 22, linea, TEXTO, 15, peso="normal"))

    p.append(flecha(284, 113, 388, 165, ACENTO))
    p.append(flecha(284, 226, 388, 196, CIAN))

    p.append(caja(392, 140, 220, 82, TINTE, ACENTO))
    p.append(texto(502, 168, "el motor", TEXTO, 16, peso="600"))
    p.append(texto(502, 191, "lee de izquierda a derecha,", SUAVE, 13))
    p.append(texto(502, 208, "una línea a la vez", SUAVE, 13))

    p.append(flecha(616, 181, 700, 181, ACENTO))

    p.append(caja(704, 140, 236, 82, PANEL, ACENTO))
    p.append(texto(822, 165, "las líneas que coinciden", SUAVE, 13))
    p.append(teclado(822, 191, "Ana Ruiz", ACENTO, 15, peso="normal"))
    p.append(teclado(822, 211, "Mariana Solís", ACENTO, 15, peso="normal"))

    p.append(texto(ancho / 2, 320, "«Mariana» también pasa: la regex busca una subcadena, no una palabra completa.", SUAVE, 14))
    p.append(texto(ancho / 2, 344, "grep imprime la línea entera; la coincidencia fue sólo el pedazo «ana».", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Pagina 2: la cabeza lectora y el automata de `ana`
# --------------------------------------------------------------------------

def rx_cabeza():
    """La cabeza intenta desde cada posicion y nunca retrocede."""
    ancho, alto = 980, 460
    aria = (
        "La palabra Mariana en una cinta de siete celdas. Debajo, cinco "
        "intentos del patron ana empezando cada uno una celda mas a la "
        "derecha: los cuatro primeros fallan y el quinto acierta"
    )
    letras = "Mariana"
    w, x0, y0 = 74, 210, 84
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "La cabeza avanza; nunca regresa", TEXTO, 21, peso="600"))
    p.append(texto(ancho / 2, 66, "patrón ana sobre el texto Mariana", SUAVE, 14))

    for i, ch in enumerate(letras):
        p.append(celda(x0 + i * w, y0, w - 6, 52, ch, LINEA, TEXTO))
        p.append(texto(x0 + i * w + (w - 6) / 2, y0 + 70, str(i), SUAVE, 12))

    # Cinco intentos: el patron empieza en 0,1,2,3,4.
    intentos = (
        (0, False, "a ≠ M"),
        (1, False, "a ✓ · n ≠ r"),
        (2, False, "a ≠ r"),
        (3, False, "a ≠ i"),
        (4, True, "a ✓ n ✓ a ✓"),
    )
    for fila, (inicio, exito, nota) in enumerate(intentos):
        y = 172 + fila * 46
        color = ACENTO if exito else ROJO
        p.append(texto(150, y + 22, f"intento {fila + 1}", SUAVE, 13, anclaje="end"))
        for j, ch in enumerate("ana"):
            x = x0 + (inicio + j) * w
            p.append(celda(x, y, w - 6, 34, ch, color, color, FONDO, 16))
        etiqueta = "✓ encontró «ana»" if exito else f"✗ {nota}"
        p.append(texto(x0 + (inicio + 3) * w + 12, y + 23, etiqueta, color, 14, anclaje="start"))

    p.append(texto(ancho / 2, 434, "Cada intento empieza una celda más a la derecha. Lo que ya pasó no se vuelve a mirar.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


def rx_automata_ana():
    """El automata que reconoce `ana` como subcadena."""
    ancho, alto = 980, 450
    aria = (
        "Automata de cuatro estados que reconoce la subcadena ana: q0 avanza a "
        "q1 al leer a, q1 avanza a q2 al leer n, q2 avanza al estado de "
        "aceptacion al leer a; cualquier otro caracter devuelve la maquina a q0"
    )
    y = 202
    xs = (170, 400, 630, 860)
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "El mismo patrón, como autómata: ana", TEXTO, 21, peso="600"))

    p.append(flecha(84, y, 132, y, TEXTO))
    p.append(texto(84, y - 32, "empieza aquí", TEXTO, 12.5, anclaje="start"))

    # Aristas de avance: a, n, a.
    for i, simbolo in enumerate("ana"):
        p.append(flecha(xs[i] + 34, y, xs[i + 1] - 36, y, ACENTO))
        p.append(chip((xs[i] + xs[i + 1]) / 2, y - 32, simbolo, ACENTO))

    # Bucles: cualquier otro caracter en q0; otra `a` mantiene a q1 en q1.
    p.append(bucle(xs[0], y, 32, SUAVE))
    p.append(chip(xs[0], y - 88, "otro", SUAVE))
    p.append(bucle(xs[1], y, 32, AMBAR))
    p.append(chip(xs[1], y - 88, "otra a", AMBAR))

    # Regresos a q0, por debajo y sin cruzar las aristas de avance.
    for origen, prof in ((xs[1], 76), (xs[2], 140)):
        p.append(arco(origen, y + 33, xs[0], y + 33, prof, ROJO))
        p.append(chip((xs[0] + origen) / 2, cima_arco(y + 33, prof), "otro", ROJO))

    etiquetas = ("q0", "q1", "q2", "acc")
    for i, x in enumerate(xs):
        final = i == 3
        p.append(estado(x, y, etiquetas[i], 32, ACENTO if final else LINEA,
                        ACENTO if final else TEXTO, doble=final))

    p.append(texto(ancho / 2, 404, "q0 nada visto  ·  q1 vi «a»  ·  q2 vi «an»  ·  acc coincide", SUAVE, 14))
    p.append(texto(ancho / 2, 430, "Fíjate en el bucle ámbar: si en q1 llega otra a, la máquina no vuelve a q0 — esa a puede empezar la coincidencia buena.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Pagina 3: cuantificadores y el caso goloso
# --------------------------------------------------------------------------

def rx_cuantificadores():
    """?, * y + como tres automatas diminutos."""
    ancho, alto = 980, 400
    aria = (
        "Tres automatas pequenos lado a lado: a con interrogacion acepta cero "
        "o una a, a con asterisco acepta cero o mas y su estado inicial ya es "
        "de aceptacion, a con mas exige al menos una a antes de aceptar"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Los tres cuantificadores, dibujados", TEXTO, 21, peso="600"))

    y = 226
    paneles = (
        (30, "a?", "cero o una", CIAN),
        (338, "a*", "cero o más", ACENTO),
        (646, "a+", "una o más", VIOLETA),
    )
    for x0, patron, glosa, color in paneles:
        p.append(caja(x0, 72, 304, 272, PANEL, color))
        p.append(teclado(x0 + 152, 100, patron, color, 22))
        p.append(texto(x0 + 152, 124, glosa, SUAVE, 14))

        izq, der = x0 + 84, x0 + 222
        p.append(flecha(x0 + 24, y, izq - 34, y, TEXTO))

        if patron == "a*":
            # Un solo estado: ya acepta, y el bucle consume cada `a`.
            p.append(bucle(izq, y, 30, color))
            p.append(chip(izq, y - 84, "a", color))
            p.append(estado(izq, y, "q0", 30, color, color, doble=True))
            p.append(texto(x0 + 152, 302, "acepta antes de leer nada:", SUAVE, 13))
            p.append(texto(x0 + 152, 322, "por eso casa la cadena vacía", SUAVE, 13))
        else:
            p.append(flecha(izq + 32, y, der - 34, y, color))
            p.append(chip((izq + der) / 2, y - 32, "a", color))
            p.append(estado(izq, y, "q0", 30, color, TEXTO))
            p.append(estado(der, y, "acc", 30, color, color, doble=True))
            if patron == "a?":
                p.append(arco(izq, y + 31, der, y + 31, 46, SUAVE))
                p.append(chip((izq + der) / 2, cima_arco(y + 31, 46), "ε", SUAVE))
                p.append(texto(x0 + 152, 322, "el salto ε es «cero veces»", SUAVE, 13))
            else:
                p.append(bucle(der, y, 30, color))
                p.append(chip(der, y - 84, "a", color))
                p.append(texto(x0 + 152, 322, "hay que leer una para aceptar", SUAVE, 13))

    p.append(texto(ancho / 2, 376, "El cuantificador aplica al elemento inmediatamente anterior: ab* repite la b, no ab.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)

def rx_goloso():
    """`.*` se come todo; `[^>]*` se detiene en el primer cierre."""
    ancho, alto = 1060, 340
    aria = (
        "El texto menor a mayor que sobre el mismo renglon con dos patrones: "
        "punto asterisco marca una sola coincidencia que abarca todo el "
        "renglon, mientras que corchete negado marca dos coincidencias cortas"
    )
    cadena = "<a>␣y␣<b>"
    w, x0, y0 = 58, 190, 96
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Goloso: hasta dónde llega la repetición", TEXTO, 21, peso="600"))
    p.append(texto(ancho / 2, 68, "el mismo texto, dos patrones — «␣» es un espacio", SUAVE, 14))

    for i, ch in enumerate(cadena):
        p.append(celda(x0 + i * w, y0, w - 6, 52, ch, LINEA, TEXTO))

    # Barra golosa: cubre las nueve celdas.
    p.append(caja(x0, 176, len(cadena) * w - 6, 34, "none", AMBAR, radio=8, grosor=3))
    p.append(teclado(x0 - 16, 199, "<.*>", AMBAR, 17, anclaje="end"))
    p.append(texto(x0 + len(cadena) * w + 12, 199, "1 coincidencia: se comió todo", AMBAR, 14, anclaje="start"))

    # Barras acotadas: `<a>` y `<b>`.
    for inicio in (0, 6):
        p.append(caja(x0 + inicio * w, 238, 3 * w - 6, 34, "none", ACENTO, radio=8, grosor=3))
    p.append(teclado(x0 - 16, 261, "<[^>]*>", ACENTO, 17, anclaje="end"))
    p.append(texto(x0 + len(cadena) * w + 12, 261, "2 coincidencias", ACENTO, 14, anclaje="start"))

    p.append(texto(ancho / 2, 316, "«.» también casa el «>». Negar el carácter de cierre es lo que detiene la repetición a tiempo.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)

# --------------------------------------------------------------------------
# Pagina 4: las clases de Perl sobre una tira de caracteres
# --------------------------------------------------------------------------

def rx_clases():
    """Que cubre cada clase sobre los mismos ocho caracteres."""
    ancho, alto = 1120, 452
    aria = (
        "Ocho caracteres en fila y tres bandas debajo que marcan cuales cubre "
        "cada clase: barra d solo el digito, barra w las letras el digito y el "
        "guion bajo, barra s solo el espacio; la columna de la ene con tilde "
        "queda marcada como dudosa porque depende del locale del sistema"
    )
    fila = ("a", "Z", "7", "_", "ñ", "␣", ".", "-")
    NINA = 4  # la columna que depende del locale
    clases = (
        (r"\d", {2}, AMBAR, "[[:digit:]]", "no la conoce grep -E"),
        (r"\w", {0, 1, 2, 3}, CIAN, "[[:alnum:]_]", ""),
        (r"\s", {5}, VIOLETA, "[[:space:]]", ""),
    )
    w, x0, y0 = 74, 290, 92
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Qué cubre cada clase", TEXTO, 21, peso="600"))
    p.append(texto(ancho / 2, 68, "los mismos ocho caracteres, tres clases", SUAVE, 14))

    for i, ch in enumerate(fila):
        p.append(celda(x0 + i * w, y0, w - 6, 54, ch, LINEA, TEXTO, PANEL))

    for k, (clase, indices, color, posix, aviso) in enumerate(clases):
        y = 180 + k * 66
        p.append(teclado(x0 - 24, y + 20, clase, color, 20, anclaje="end"))
        p.append(teclado(x0 - 24, y + 42, posix, SUAVE, 13, anclaje="end", peso="normal"))
        for i in range(len(fila)):
            # La ñ con \w es el caso dudoso: entra en UTF-8 y no entra con LC_ALL=C.
            dudoso = i == NINA and clase == r"\w"
            if dudoso:
                p.append(caja(x0 + i * w, y, w - 6, 44, FONDO, AMBAR, radio=6, grosor=2.5))
                p.append(teclado(x0 + i * w + (w - 6) / 2, y + 30, "?", AMBAR, 20))
            elif i in indices:
                p.append(caja(x0 + i * w, y, w - 6, 44, TINTE, color, radio=6, grosor=2.5))
                p.append(teclado(x0 + i * w + (w - 6) / 2, y + 30, "✓", color, 20))
            else:
                p.append(caja(x0 + i * w, y, w - 6, 44, "none", "#232c31", radio=6, grosor=1.5))
        if aviso:
            # El texto de la pagina dice que \\d no sirve en grep -E; sin marcarlo
            # aqui, el ancla visual ensena justo lo contrario.
            p.append(chip(x0 + len(fila) * w + 106, y + 22, aviso, ROJO, tam=13))

    p.append(texto(ancho / 2, 404, "La ñ depende del locale: en UTF-8 entra en \\w, con LC_ALL=C no entra.", AMBAR, 14))
    p.append(texto(ancho / 2, 428, "El mismo patrón puede dar respuestas distintas en dos máquinas. Las clases POSIX no arreglan eso: lo hacen visible.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Pagina 5: precedencia de la alternancia y el automata del correo
# --------------------------------------------------------------------------

def rx_alternancia():
    """Donde caen los anclajes cambia por completo el patron."""
    ancho, alto = 980, 420
    aria = (
        "Dos patrones comparados: sin parentesis los anclajes se reparten uno "
        "a cada rama, con parentesis los anclajes encierran ambas ramas"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Dónde cae el anclaje", TEXTO, 21, peso="600"))
    p.append(texto(ancho / 2, 68, "«|» parte la expresión completa, no sólo lo que tiene al lado", SUAVE, 14))

    bloques = (
        (30, "^ana|beto$", ROJO, "^ana", "beto$",
         "«empieza con ana» O «termina con beto»",
         "anaconda ✓   ·   yo soy beto ✓   ·   ana ✓"),
        (510, "^(ana|beto)$", ACENTO, "^ana$", "^beto$",
         "la línea entera es ana, o es beto",
         "anaconda ✗   ·   yo soy beto ✗   ·   ana ✓"),
    )
    for x0, patron, color, rama_a, rama_b, glosa, ejemplos in bloques:
        p.append(caja(x0, 92, 440, 266, PANEL, color))
        p.append(teclado(x0 + 220, 128, patron, color, 22))
        p.append(texto(x0 + 220, 152, glosa, SUAVE, 13.5))

        izq, der, y = x0 + 74, x0 + 366, 244
        p.append(arco(izq + 28, y, der - 30, y, -58, color))
        p.append(arco(izq + 28, y, der - 30, y, 58, color))
        p.append(chip((izq + der) / 2, cima_arco(y, -58), rama_a, color, tam=14))
        p.append(chip((izq + der) / 2, cima_arco(y, 58), rama_b, color, tam=14))
        p.append(estado(izq, y, "ini", 28, color, TEXTO))
        p.append(estado(der, y, "acc", 28, color, color, doble=True))
        p.append(texto(x0 + 220, 336, ejemplos, TEXTO, 13.5))

    p.append(texto(ancho / 2, 394, "Si dudas, pon paréntesis: cuestan un carácter y quitan la ambigüedad.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)

def rx_automata_email():
    """El patron de correo, estado por estado."""
    ancho, alto = 1060, 560
    aria = (
        "Automata de cinco estados para un patron de correo: una o mas "
        "caracteres de la parte local, la arroba, una o mas del dominio, un "
        "punto literal y al menos dos letras de terminacion; debajo, cuatro "
        "cadenas de prueba con su resultado"
    )
    y = 214
    xs = (120, 340, 520, 720, 940)
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Un patrón de correo, estado por estado", TEXTO, 21, peso="600"))
    p.append(teclado(ancho / 2, 76, "^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$", ACENTO, 19))

    p.append(flecha(40, y, 84, y, TEXTO))
    p.append(texto(36, y - 32, "empieza aquí", TEXTO, 12.5, anclaje="start"))

    transiciones = (
        ("[a-z0-9._%+-]", CIAN, True),
        ("@", AMBAR, False),
        ("[a-z0-9.-]", CIAN, True),
        ("\\.", AMBAR, False),
    )
    for i, (etiqueta, color, repite) in enumerate(transiciones):
        p.append(flecha(xs[i] + 34, y, xs[i + 1] - 36, y, color))
        p.append(chip((xs[i] + xs[i + 1]) / 2, y - 34, etiqueta, color, tam=14))
        if repite:
            p.append(bucle(xs[i + 1], y, 32, color))
            p.append(chip(xs[i + 1], y - 96, "una más", color, tam=13))

    etiquetas = ("ini", "local", "@", "dom", "acc")
    for i, x in enumerate(xs):
        final = i == 4
        p.append(estado(x, y, etiquetas[i], 32, ACENTO if final else LINEA,
                        ACENTO if final else TEXTO, doble=final))

    p.append(texto(xs[1], y + 62, "parte local", SUAVE, 13))
    p.append(texto(xs[2], y + 62, "la arroba", SUAVE, 13))
    p.append(texto(xs[3], y + 62, "dominio", SUAVE, 13))
    p.append(texto(xs[4], y + 62, "[a-z]{2,}", ACENTO, 13))

    p.append(caja(120, 316, 820, 168, PANEL, LINEA))
    p.append(texto(530, 344, "contra los datos sucios del laboratorio", SUAVE, 14))
    pruebas = (
        ("ana@itam.mx", True, "el caso normal"),
        ("ana+tareas@itam.mx", True, "el + está dentro de la clase local"),
        ("ana@itam.mx.", False, "el punto final no puede seguir a [a-z]{2,}"),
        ("@itam.mx", False, "la parte local exige al menos un carácter"),
    )
    for i, (cadena, ok, nota) in enumerate(pruebas):
        yy = 376 + i * 28
        color = ACENTO if ok else ROJO
        p.append(texto(160, yy, "✓" if ok else "✗", color, 16, anclaje="start", peso="600"))
        p.append(teclado(190, yy, cadena, color, 15, anclaje="start", peso="normal"))
        p.append(texto(520, yy, nota, SUAVE, 13.5, anclaje="start"))

    p.append(texto(ancho / 2, 522, "Ninguna regex valida un correo de verdad: esto filtra bien, no demuestra nada.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Pagina 6: la limpieza como tuberia
# --------------------------------------------------------------------------

def rx_tuberia():
    """El reparto de trabajo: la regex encuentra, la tuberia limpia."""
    ancho, alto = 1060, 352
    aria = (
        "Cinco cajas encadenadas de izquierda a derecha: el archivo de "
        "contactos con diez lineas, grep que extrae ocho coincidencias, tr que "
        "las pasa a minusculas, sort menos u que deja cinco unicas y el "
        "archivo de salida; solo la primera caja usa una expresion regular"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Una limpieza es una cadena de pasos pequeños", TEXTO, 21, peso="600"))

    etapas = (
        ("contactos.txt", "10 líneas", "el archivo sucio", CIAN),
        ("grep -Eoih", "8 coincidencias", "encuentra", ACENTO),
        ("tr A-Z a-z", "8, normalizadas", "unifica", AMBAR),
        ("sort -u", "5 únicas", "ordena y depura", VIOLETA),
        ("correos.txt", "5 líneas", "el resultado", CIAN),
    )
    w, sep, y0 = 178, 30, 96
    x0 = (ancho - (len(etapas) * w + (len(etapas) - 1) * sep)) / 2
    for i, (titulo, cifra, glosa, color) in enumerate(etapas):
        x = x0 + i * (w + sep)
        p.append(caja(x, y0, w, 108, PANEL, color))
        p.append(teclado(x + w / 2, y0 + 36, titulo, color, 16))
        p.append(texto(x + w / 2, y0 + 64, cifra, TEXTO, 15, peso="600"))
        p.append(texto(x + w / 2, y0 + 88, glosa, SUAVE, 13))
        if i:
            p.append(flecha(x - sep + 3, y0 + 54, x - 5, y0 + 54, SUAVE))

    # El senalador cuelga del segundo eslabon: ahi, y solo ahi, hay una regex.
    centro = x0 + (w + sep) + w / 2
    p.append(flecha(centro, 234, centro, 210, ACENTO))
    p.append(caja(centro - 140, 238, 280, 40, TINTE, ACENTO, radio=8))
    p.append(texto(centro, 263, "aquí, y sólo aquí, hay una regex", ACENTO, 14))

    p.append(texto(ancho / 2, 306, "Los otros tres pasos son herramientas de texto corrientes: la regex encuentra, la tubería limpia.", SUAVE, 14))
    p.append(texto(ancho / 2, 330, "Cada eslabón hace una cosa y se puede probar solo: corre la tubería recortada hasta el paso que dudes.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Pagina 3: las piezas de un patron y el contexto de cada simbolo
# --------------------------------------------------------------------------

def rx_piezas():
    """Un patron real, partido en piezas y anclas, con el alcance de cada
    cuantificador y el texto que consume cada pieza."""
    ancho, alto = 1080, 500
    aria = (
        "Un patron de telefono partido en cinco partes: dos anclas que no "
        "consumen ningun caracter y tres piezas que si; debajo, el texto 55 "
        "1234 con cada caracter coloreado segun la pieza que lo consumio"
    )
    # (etiqueta, cuantificador, glosa, ancho, es_pieza, color, consume)
    partes = (
        ("^", "", "ancla", 78, False, SUAVE, ""),
        ("[0-9]", "{2}", "×2", 200, True, CIAN, "55"),
        ("[ -]", "?", "×0 o 1", 176, True, AMBAR, " "),
        ("[0-9]", "{4}", "×4", 200, True, VIOLETA, "1234"),
        ("$", "", "ancla", 78, False, SUAVE, ""),
    )
    sep, y0, h = 18, 118, 76
    total = sum(p[3] for p in partes) + sep * (len(partes) - 1)
    x0 = (ancho - total) / 2

    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Un patrón es una fila de piezas", TEXTO, 21, peso="600"))
    p.append(teclado(ancho / 2, 82, "^[0-9]{2}[ -]?[0-9]{4}$", ACENTO, 20))

    x = x0
    centros = []
    for etiqueta, cuant, glosa, w, es_pieza, color, _ in partes:
        relleno = PANEL if es_pieza else FONDO
        p.append(caja(x, y0, w, h, relleno, color, radio=10,
                      grosor=2.5 if es_pieza else 1.5))
        p.append(teclado(x + w / 2, y0 + 34, etiqueta, color, 18))
        p.append(teclado(x + w / 2, y0 + 60, cuant or "—", SUAVE, 14, peso="normal"))
        p.append(texto(x + w / 2, y0 + h + 24, glosa, color, 13.5))
        p.append(texto(x + w / 2, y0 + h + 44,
                       "consume" if es_pieza else "no consume", SUAVE, 12.5))
        centros.append((x + w / 2, w, color, es_pieza))
        x += w + sep

    # La cadena que casa, con cada caracter tenido por la pieza que lo consumio.
    cadena = "55 1234"
    cw, cy = 62, 336
    cx0 = (ancho - len(cadena) * cw) / 2
    tintes = [CIAN, CIAN, AMBAR, VIOLETA, VIOLETA, VIOLETA, VIOLETA]
    for i, ch in enumerate(cadena):
        visible = "␣" if ch == " " else ch
        p.append(celda(cx0 + i * cw, cy, cw - 6, 52, visible, tintes[i], tintes[i]))

    # Las anclas se marcan como un corte sin ancho a los lados de la cadena.
    for borde in (cx0 - 14, cx0 + len(cadena) * cw - 6 + 14):
        p.append(f'<line x1="{borde}" y1="{cy - 10}" x2="{borde}" y2="{cy + 62}" '
                 f'stroke="{SUAVE}" stroke-width="3" stroke-dasharray="6 5"/>')

    for centro, w, color, es_pieza in centros:
        destino = cx0 + {CIAN: 62, AMBAR: 155, VIOLETA: 310}.get(color, 0)
        if es_pieza:
            p.append(arco(centro, y0 + h + 56, destino, cy - 8, 26, color, 1.8))

    p.append(texto(ancho / 2, 434, "Las anclas de los extremos no se llevan ningún carácter: sólo exigen estar al principio y al final.", SUAVE, 14))
    p.append(texto(ancho / 2, 462, "El cuantificador se pega a la pieza que tiene justo a su izquierda. A ninguna otra.", ACENTO, 14))
    p.append(cierre())
    return "".join(p)


def rx_contexto():
    """El mismo simbolo significa tres cosas segun donde este."""
    ancho, alto = 1080, 484
    aria = (
        "Tabla de seis simbolos y tres columnas: que significa cada uno suelto "
        "en el patron, dentro de unos corchetes y precedido de barra invertida; "
        "dentro de los corchetes casi todos pierden su poder"
    )
    filas = (
        (".", "cualquier carácter", "un punto literal", "un punto literal"),
        ("*", "repite lo anterior", "un asterisco literal", "un asterisco literal"),
        ("+", "una o más veces", "un signo más literal", "un signo más literal"),
        ("^", "inicio de línea", "niega, sólo si va primero", "un circunflejo literal"),
        ("-", "un guion literal", "rango, salvo en los extremos", "un guion literal"),
        ("]", "un corchete literal", "cierra, salvo si va primero", "un corchete literal"),
    )
    cols = (200, 296, 302, 242)
    x0, y0, hf = 20, 132, 50
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "El mismo símbolo, tres significados", TEXTO, 21, peso="600"))
    p.append(texto(ancho / 2, 68, "lo que decide no es el símbolo: es dónde está", SUAVE, 14))

    encabezados = ("símbolo", "suelto en el patrón", "dentro de [ … ]", "escapado con \\")
    colores = (TEXTO, ACENTO, AMBAR, CIAN)
    x = x0
    for i, cab in enumerate(encabezados):
        p.append(texto(x + cols[i] / 2, y0 - 16, cab, colores[i], 15, peso="600"))
        x += cols[i]
    p.append(f'<line x1="{x0}" y1="{y0 - 2}" x2="{x0 + sum(cols)}" y2="{y0 - 2}" '
             f'stroke="{LINEA}" stroke-width="2"/>')

    for k, fila in enumerate(filas):
        y = y0 + k * hf
        if k % 2:
            p.append(caja(x0, y, sum(cols), hf, PANEL, "none", radio=6, grosor=0))
        x = x0
        for i, celda_texto in enumerate(fila):
            cx = x + cols[i] / 2
            if i == 0:
                p.append(teclado(cx, y + 31, celda_texto, TEXTO, 19))
            else:
                especial = "literal" not in celda_texto
                p.append(texto(cx, y + 31, celda_texto,
                               colores[i] if especial else SUAVE, 14,
                               peso="600" if especial else "normal"))
            x += cols[i]

    p.append(texto(ancho / 2, 448, "Dentro de los corchetes casi todo pierde su poder: por eso [.] es un punto y [a+b] casa una a, un + o una b.", AMBAR, 14))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Pagina 4: el goloso, paso a paso
# --------------------------------------------------------------------------

def rx_backtracking():
    """La repeticion toma de mas y despues cede, hasta que el resto encaja."""
    ancho, alto = 1080, 560
    aria = (
        "Sobre el texto menor a mayor que, el punto asterisco toma ocho "
        "caracteres y falla porque despues no queda ningun mayor que; cede uno "
        "y entonces si encaja, dejando una sola coincidencia que abarca todo el "
        "renglon; debajo, la clase negada se detiene sola y da dos "
        "coincidencias cortas"
    )
    cadena = "<a>␣y␣<b>"
    w, x0, y0 = 56, 150, 108
    fin_cinta = x0 + len(cadena) * w
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "El goloso toma de más y después cede", TEXTO, 21, peso="600"))
    p.append(texto(ancho / 2, 68, "patrón <.*> sobre este renglón — «␣» es un espacio", SUAVE, 14))

    for i, ch in enumerate(cadena):
        p.append(celda(x0 + i * w, y0, w - 6, 50, ch, LINEA, TEXTO))

    def barra(y, desde, hasta, color, etiqueta):
        p.append(caja(x0 + desde * w, y, (hasta - desde) * w - 6, 36, "none",
                      color, radio=8, grosor=3))
        p.append(teclado(x0 + desde * w + ((hasta - desde) * w - 6) / 2, y + 24,
                         etiqueta, color, 15, peso="normal"))

    # `<` casa la celda 0; `.*` empieza en la 1. Toma hasta el final, falla, y
    # cede exactamente un caracter: entonces la celda 8 es el `>` que faltaba.
    pasos = (
        (190, 1, 9, ROJO, "a>␣y␣<b>", ".* toma los ocho", "y después no queda ningún >"),
        (256, 1, 8, ACENTO, "a>␣y␣<b", "cede uno", "el siguiente sí es > → encaja"),
    )
    for y, desde, hasta, color, etiqueta, que, porque in pasos:
        barra(y, desde, hasta, color, etiqueta)
        p.append(texto(fin_cinta + 18, y + 16, que, color, 13.5, anclaje="start"))
        p.append(texto(fin_cinta + 18, y + 36, porque, SUAVE, 12.5, anclaje="start"))

    barra(322, 0, 9, ACENTO, "<a>␣y␣<b>")
    p.append(texto(fin_cinta + 18, 346, "una sola coincidencia", ACENTO, 13.5, anclaje="start"))

    p.append(texto(ancho / 2, 406, "Ese ceder es lo único que retrocede. La cabeza sigue sin volver atrás: lo que se mueve es hasta dónde llega la repetición", SUAVE, 13.5))
    p.append(texto(ancho / 2, 428, "dentro de un mismo intento.", SUAVE, 13.5))

    p.append(teclado(ancho / 2, 470, "<[^>]*>", ACENTO, 18))
    barra(492, 0, 3, ACENTO, "<a>")
    barra(492, 6, 9, ACENTO, "<b>")
    p.append(texto(fin_cinta + 18, 516, "no cede nada:", ACENTO, 13.5, anclaje="start"))
    p.append(texto(fin_cinta + 18, 536, "se detiene sola en el primer >", SUAVE, 12.5, anclaje="start"))
    p.append(cierre())
    return "".join(p)



DIAGRAMAS = {
    "rx-que-es": rx_que_es,
    "rx-cabeza": rx_cabeza,
    "rx-automata-ana": rx_automata_ana,
    "rx-piezas": rx_piezas,
    "rx-contexto": rx_contexto,
    "rx-cuantificadores": rx_cuantificadores,
    "rx-backtracking": rx_backtracking,
    "rx-clases": rx_clases,
    "rx-alternancia": rx_alternancia,
    "rx-automata-email": rx_automata_email,
    "rx-tuberia": rx_tuberia,
}


def escribir(nombre):
    ASSETS.mkdir(parents=True, exist_ok=True)
    destino = ASSETS / f"{nombre}.svg"
    destino.write_text(DIAGRAMAS[nombre](), encoding="utf-8")
    return destino


def main(argv):
    nombres = argv[1:] or list(DIAGRAMAS)
    for nombre in nombres:
        if nombre not in DIAGRAMAS:
            raise SystemExit(f"diagrama desconocido: {nombre}")
        destino = escribir(nombre)
        print(f"{destino.name}  ({destino.stat().st_size / 1000:.1f} KB)")


if __name__ == "__main__":
    main(sys.argv)
