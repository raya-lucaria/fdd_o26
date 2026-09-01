"""Primitivas compartidas de los diagramas SVG escritos a mano del curso.

La paleta sale de skins/fdd-eva.yaml y vive aqui una sola vez: un generador por
unidad —gen_regex.py, gen_git.py— importa de este modulo en vez de repetirla.

Cada SVG hornea su propio fondo y usa `fill` explicito en todo texto, para que
se lea igual en tema claro y en tema oscuro. La raiz <svg> lleva width y height
propios ademas de viewBox: el sitio incrusta los diagramas con <img>, y sin
tamano intrinseco el navegador cae al tamano por omision de un elemento
reemplazado (~300x150 CSS px) en vez de llenar el contenedor de la figura.
"""
from xml.sax.saxutils import escape

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
