"""Figuras de la sección «Elegir el canal» de la página 12 de la unidad 11: los cinco
canales con los mismos tres eventos, dónde vive cada cosa y un árbol de decisión.

Importa sólo svg_base.py (igual que gen_computo_d.py) para no crear un ciclo con
gen_computo.py, que mezcla DIAGRAMAS_E en su catálogo. Reglas de lectura para
alumnos no técnicos: una pregunta por figura, rótulos de 16 px o más, pocos
elementos, un estilo por significado y sin letras griegas.
"""
from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, SUAVE, TEXTO, TINTE, VIOLETA,
    caja, cierre, flecha, marco, texto,
)

EVENTOS_S = (2, 5, 9)      # instantes en que el servidor genera un evento (s)
EJE_MAX = 12               # duración del caso (s)
CADA_S = 3                 # intervalo de consulta del polling (s)
REAPERTURA_S = 0.25        # hueco entre una consulta pendiente y la siguiente (s)

X0, X1 = 210, 1030


def _xs(s):
    return X0 + s * (X1 - X0) / EJE_MAX


def _linea(x1, y1, x2, y2, color=LINEA, grosor=1.2, guiones=None):
    extra = f' stroke-dasharray="{guiones}"' if guiones else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{grosor}"{extra}/>')


def _barra(x1, x2, y, alto=32):
    return (f'<rect x="{x1:.1f}" y="{y}" width="{max(x2 - x1, 3):.1f}" height="{alto}" '
            f'rx="5" fill="{TINTE}" stroke="{ACENTO}" stroke-width="1.6"/>')


def _rombo(x, y, r=10, color=AMBAR):
    return (f'<path d="M {x:.1f} {y - r} L {x + r:.1f} {y} L {x:.1f} {y + r} '
            f'L {x - r:.1f} {y} Z" fill="{color}"/>')


def _punto(x, y, lleno=True, r=8):
    if lleno:
        return (f'<circle cx="{x:.1f}" cy="{y}" r="{r}" fill="{TEXTO}" '
                f'stroke="{FONDO}" stroke-width="2"/>')
    return (f'<circle cx="{x:.1f}" cy="{y}" r="{r}" fill="{FONDO}" '
            f'stroke="{SUAVE}" stroke-width="2"/>')


def _candado(x, y, color=AMBAR, cerrado=True):
    """Candado de 20 x 24 px con la esquina superior izquierda en (x, y)."""
    asa = (f'M {x + 4} {y + 11} V {y + 7} a 6 6 0 0 1 12 0 V {y + 11}' if cerrado
           else f'M {x + 4} {y + 11} V {y + 7} a 6 6 0 0 1 12 0 V {y + 4}')
    return (f'<path d="{asa}" fill="none" stroke="{color}" stroke-width="2.4"/>'
            f'<rect x="{x}" y="{y + 11}" width="20" height="13" rx="3" fill="{color}"/>')


# --------------------------------------------------------------------------- 1
def cmp_canales_eventos():
    ancho, alto = 1080, 668
    aria = ("Cinco carriles con el mismo caso: el servidor genera tres eventos en 2, 5 y 9 "
            "segundos. El polling cada 3 segundos se entera en 3, 6 y 9 segundos; el long "
            "polling, el SSE y el WebSocket se enteran en 2, 5 y 9 segundos con una consulta "
            "o conexión abierta; el webhook recibe tres llamadas cortas sin dejar nada abierto.")
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 40, "Los cinco canales para los mismos tres eventos",
                   TEXTO, 22, peso="600"))
    # Eje común arriba.
    ye = 104
    p.append(_linea(X0, ye, X1, ye, SUAVE, 1.4))
    for s in range(0, EJE_MAX + 1, CADA_S):
        p.append(_linea(_xs(s), ye - 6, _xs(s), ye, SUAVE, 1.4))
        p.append(texto(_xs(s), ye - 14, f"{s} s", SUAVE, 16))
    p.append(texto(X0 - 18, ye - 14, "tiempo", SUAVE, 16, anclaje="end"))
    carriles = [130 + 92 * i for i in range(5)]
    fin = carriles[-1] + 78
    for s in EVENTOS_S:
        p.append(_linea(_xs(s), ye + 10, _xs(s), fin, AMBAR, 1.2, "2 5"))
        p.append(_rombo(_xs(s), ye))
    nombres = ("polling", "long polling", "SSE", "WebSocket", "webhook")
    rotulos = ("pregunta cada 3 s",
               "una consulta pendiente; al responder se vuelve a abrir",
               "una conexión abierta",
               "una conexión abierta, dos sentidos",
               "tres llamadas, nada abierto entre ellas")
    for ly, nombre, rotulo in zip(carriles, nombres, rotulos):
        p.append(texto(24, ly + 30, nombre, TEXTO, 18, anclaje="start", peso="600"))
        p.append(texto(X0, ly + 68, rotulo, SUAVE, 16, anclaje="start"))
        if ly != carriles[-1]:
            p.append(_linea(24, ly + 82, X1, ly + 82, LINEA, 0.8))
    cy = [ly + 24 for ly in carriles]
    # 1. polling: consultas cada 3 s; las que traen un evento y la que vuelve vacía.
    for s, demora in zip((3, 6, 9), (1, 1, 0)):
        evento = EVENTOS_S[(3, 6, 9).index(s)]
        if demora:
            p.append(_linea(_xs(evento), cy[0], _xs(s), cy[0], AMBAR, 4))
        if demora:
            p.append(texto(_xs(s) - (_xs(s) - _xs(evento)) / 2, cy[0] - 14,
                           f"{demora} s", AMBAR, 16))
        else:
            p.append(texto(_xs(s) + 14, cy[0] - 14, f"{demora} s", AMBAR, 16,
                           anclaje="start"))
        p.append(_punto(_xs(s), cy[0]))
    p.append(_punto(_xs(12), cy[0], lleno=False))
    p.append(texto(_xs(12) - 16, cy[0] - 14, "sin novedades", SUAVE, 16, anclaje="end"))
    # 2. long polling: una consulta tras otra, con un hueco breve al reabrir.
    corte = [0, *EVENTOS_S, EJE_MAX]
    for i in range(len(corte) - 1):
        a = corte[i] + (REAPERTURA_S if i else 0)
        p.append(_barra(_xs(a), _xs(corte[i + 1]), cy[1] - 16))
    for s in EVENTOS_S:
        p.append(_punto(_xs(s), cy[1]))
    # 3. SSE: una conexión de punta a punta.
    p.append(_barra(_xs(0), _xs(EJE_MAX), cy[2] - 16))
    for s in EVENTOS_S:
        p.append(_punto(_xs(s), cy[2]))
    # 4. WebSocket: igual, más un mensaje del cliente hacia el servidor.
    p.append(_barra(_xs(0), _xs(EJE_MAX), cy[3] - 16))
    for s in EVENTOS_S:
        p.append(_punto(_xs(s), cy[3]))
    p.append(flecha(_xs(8.1), cy[3], _xs(6.1), cy[3], CIAN, 2.4))
    p.append(texto(_xs(7.1), cy[3] - 24, "el cliente envía", CIAN, 16))
    # 5. webhook: tres llamadas breves, sin nada abierto entre ellas.
    for s in EVENTOS_S:
        p.append(_barra(_xs(s) - 11, _xs(s) + 11, cy[4] - 16))
        p.append(_punto(_xs(s), cy[4]))
    # Leyenda mínima.
    yl = fin + 38
    p.append(_rombo(40, yl, 9))
    p.append(texto(58, yl + 6, "evento del servidor", TEXTO, 16, anclaje="start"))
    p.append(_punto(330, yl))
    p.append(texto(348, yl + 6, "el cliente se entera", TEXTO, 16, anclaje="start"))
    p.append(_barra(615, 655, yl - 12, 24))
    p.append(texto(667, yl + 6, "algo abierto", TEXTO, 16, anclaje="start"))
    p.append(_linea(830, yl, 870, yl, AMBAR, 4))
    p.append(texto(882, yl + 6, "demora", TEXTO, 16, anclaje="start"))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------- 2
def _nodo(x, y, w, h, l1, l2=None, borde=LINEA, relleno=PANEL):
    p = [caja(x, y, w, h, relleno, borde, radio=10, grosor=2)]
    if l2:
        p.append(texto(x + w / 2, y + h / 2 - 4, l1, TEXTO, 17, peso="600"))
        p.append(texto(x + w / 2, y + h / 2 + 18, l2, SUAVE, 16))
    else:
        p.append(texto(x + w / 2, y + h / 2 + 6, l1, TEXTO, 17, peso="600"))
    return "".join(p)


def cmp_canales_arquitectura():
    ancho, alto = 1080, 700
    aria = ("Arquitectura en dos bandas. Arriba, navegadores y clientes pasan por un balanceador "
            "hacia dos servidores de aplicación; con SSE y WebSocket cada cliente deja una "
            "conexión abierta que el servidor retiene, y con polling el cliente solo pregunta. "
            "Abajo, un tercero llama al endpoint público, que pone el aviso en una cola para "
            "un trabajador y no retiene ninguna conexión abierta.")
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 40, "Quién conecta con quién y qué retiene el servidor",
                   TEXTO, 22, peso="600"))
    # Banda A: el cliente llama.
    p.append(texto(40, 94, "polling / long polling: el cliente pregunta al servidor",
                   CIAN, 16, anclaje="start"))
    p.append(f'<path d="M 140 168 V 124 H 700 V 140" fill="none" stroke="{CIAN}" '
             f'stroke-width="2.4" stroke-dasharray="8 6"/>')
    p.append(flecha(700, 124, 700, 150, CIAN, 2.4))
    p.append(_nodo(40, 170, 200, 90, "navegadores", "/ clientes"))
    p.append(_nodo(330, 170, 180, 90, "balanceador"))
    p.append(_nodo(600, 154, 250, 66, "servidor de aplicación"))
    p.append(_nodo(600, 240, 250, 66, "servidor de aplicación"))
    p.append(flecha(240, 215, 328, 215, ACENTO, 2.4))
    p.append(flecha(510, 200, 598, 187, ACENTO, 2.4))
    p.append(flecha(510, 230, 598, 273, ACENTO, 2.4))
    # Lo que retiene el servidor en la banda A.
    p.append(_candado(890, 196))
    p.append(texto(920, 214, "retiene", AMBAR, 16, anclaje="start", peso="600"))
    p.append(texto(890, 244, "una conexión abierta", AMBAR, 16, anclaje="start"))
    p.append(texto(890, 266, "por cliente", AMBAR, 16, anclaje="start"))
    p.append(texto(40, 338, "SSE y WebSocket: cada cliente deja UNA conexión abierta en un servidor",
                   TEXTO, 17, anclaje="start", peso="600"))
    p.append(texto(40, 364, "(memoria + un hilo o una tarea por sesión)", SUAVE, 16,
                   anclaje="start"))
    p.append(_linea(40, 400, 1040, 400, LINEA, 1))
    # Banda B: el tercero llama (webhook).
    y = 450
    p.append(_nodo(40, y, 210, 90, "tercero", "(pasarela de pagos)", borde=VIOLETA))
    p.append(_nodo(320, y, 220, 90, "tu endpoint", "público (webhook)", borde=VIOLETA))
    p.append(_nodo(610, y, 130, 90, "cola"))
    p.append(_nodo(810, y, 180, 90, "trabajador"))
    p.append(flecha(250, y + 45, 318, y + 45, VIOLETA, 2.4))
    p.append(flecha(540, y + 45, 608, y + 45, ACENTO, 2.4))
    p.append(flecha(740, y + 45, 808, y + 45, ACENTO, 2.4))
    p.append(texto(285, y + 32, "llama", VIOLETA, 16))
    p.append(texto(575, y + 32, "rápido", SUAVE, 16))
    p.append(texto(775, y + 32, "después", SUAVE, 16))
    p.append(_candado(330, y + 108, ACENTO, cerrado=False))
    p.append(texto(362, y + 126, "retiene: ninguna conexión abierta", ACENTO, 16,
                   anclaje="start", peso="600"))
    p.append(texto(40, 618, "webhook: el tercero te llama; respondes rápido y procesas después;",
                   TEXTO, 17, anclaje="start", peso="600"))
    p.append(texto(40, 644, "el mismo aviso puede llegar dos veces", SUAVE, 16, anclaje="start"))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------- 3
def _hoja(cx, y, nombre, sub, color, w=150, h=90):
    return (caja(cx - w / 2, y, w, h, color, color, radio=12, grosor=2)
            + texto(cx, y + 38, nombre, FONDO, 18, peso="600")
            + texto(cx, y + 64, sub, FONDO, 16))


def _pastilla(cx, cy, s, color=TEXTO):
    w = 11 * len(s) + 20
    return (f'<rect x="{cx - w / 2:.1f}" y="{cy - 14}" width="{w}" height="28" rx="14" '
            f'fill="{FONDO}" stroke="{color}" stroke-width="1.4"/>'
            + texto(cx, cy + 6, s, color, 16))


def cmp_canales_decision():
    ancho, alto = 1080, 610
    aria = ("Árbol de decisión de tres ramas. Si el servidor debe avisar a un navegador: con "
            "mensajes frecuentes del cliente se usa WebSocket, si no SSE. Si un tercero debe "
            "avisar a tu servidor: webhook, o polling al tercero si tu receptor no es accesible. "
            "Si el cliente puede preguntar: long polling cuando importa la demora, polling cuando "
            "la tolera y hay pocos eventos.")
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 40, "¿Qué canal uso? Tres preguntas", TEXTO, 22, peso="600"))
    cols = (190, 540, 890)
    p.append(caja(390, 70, 300, 56, TINTE, ACENTO, radio=10, grosor=2))
    p.append(texto(540, 105, "¿Quién tiene que empezar?", TEXTO, 18, peso="600"))
    ramas = (("el servidor avisa", "a un navegador"),
             ("otro servicio (un tercero)", "avisa a tu servidor"),
             ("el cliente puede", "preguntar"))
    preguntas = (("¿El cliente también envía", "mensajes seguido?"),
                 ("¿Tu receptor es accesible", "desde internet?"),
                 ("¿Importa la demora?", None))
    for cx, (r1, r2), (q1, q2) in zip(cols, ramas, preguntas):
        p.append(flecha(540, 126, cx, 178, LINEA, 2))
        p.append(caja(cx - 150, 180, 300, 70, PANEL, LINEA, radio=10, grosor=2))
        p.append(texto(cx, 210, r1, TEXTO, 17, peso="600"))
        p.append(texto(cx, 234, r2, TEXTO, 17, peso="600"))
        p.append(flecha(cx, 250, cx, 308, LINEA, 2))
        p.append(caja(cx - 150, 310, 300, 70, PANEL, SUAVE, radio=10, grosor=2))
        if q2:
            p.append(texto(cx, 339, q1, SUAVE, 17))
            p.append(texto(cx, 363, q2, SUAVE, 17))
        else:
            p.append(texto(cx, 351, q1, SUAVE, 17))
    hojas = (
        ((110, "WebSocket", "dos sentidos", ACENTO, "sí"),
         (270, "SSE", "un sentido", CIAN, "no")),
        ((450, "webhook", "el tercero llama", VIOLETA, "sí"),
         (630, "polling", "al tercero", SUAVE, "no")),
        ((810, "long polling", "poca demora", AMBAR, "poca"),
         (970, "polling", "pocos eventos", SUAVE, "tolera")),
    )
    for cx, par in zip(cols, hojas):
        for hx, nombre, sub, color, arista in par:
            p.append(flecha(cx, 380, hx, 478, color, 2.4))
            px = cx + (hx - cx) * 0.72
            p.append(_pastilla(px, 380 + 98 * 0.72, arista, color))
            p.append(_hoja(hx, 480, nombre, sub, color))
    p.append(cierre())
    return "".join(p)


DIAGRAMAS_E = {
    "cmp-canales-eventos": cmp_canales_eventos,
    "cmp-canales-arquitectura": cmp_canales_arquitectura,
    "cmp-canales-decision": cmp_canales_decision,
}
