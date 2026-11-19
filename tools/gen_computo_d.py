"""Figuras de las páginas 11 y 12 de la unidad 11: anclas del servidor, async contra def
y entrega de resultados (polling, long polling, SSE, WebSocket, webhook).

Importa sólo svg_base.py, igual que gen_computo_b.py, para no crear un ciclo con
gen_computo.py (que mezcla DIAGRAMAS_D en su catálogo). Estilo de barra de la
unidad: ejecuta relleno, espera con contorno discontinuo, lista rayada,
bloqueada en ámbar. Sin letras griegas: el intervalo de consulta se escribe
«cada 3 s» y la tasa «lambda». Las cifras son las del contrato de la unidad
(w = 0.5 s, 12 peticiones, evento en 10 s, consulta cada 3 s, R x N x k = 120).
"""
from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, ROJO, SUAVE, TEXTO, TINTE,
    VIOLETA, caja, cierre, flecha, marco, texto, teclado,
)

ANCHO = 1080
X0 = 190
X1 = 1040

W_S = 0.5          # espera bloqueante de cada petición (s)
PETICIONES = 4

EVENTO_S = 10      # instante del evento (s)
CADA_S = 3         # intervalo de consulta del polling (s)

RAYADO = (
    '<defs><pattern id="rayado" width="8" height="8" patternUnits="userSpaceOnUse" '
    'patternTransform="rotate(45)">'
    f'<rect x="0" y="0" width="8" height="8" fill="{PANEL}"/>'
    f'<line x1="0" y1="0" x2="0" y2="8" stroke="{VIOLETA}" stroke-width="3"/>'
    '</pattern></defs>'
)


def _marco(ancho, alto, aria):
    return marco(ancho, alto, aria) + RAYADO


def _rect(x, y, w, h, relleno, borde="none", grosor=0, guiones=None, radio=3):
    extra = f' stroke-dasharray="{guiones}"' if guiones else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 3):.1f}" height="{h}" '
            f'rx="{radio}" fill="{relleno}" stroke="{borde}" '
            f'stroke-width="{grosor}"{extra}/>')


def _linea(x1, y1, x2, y2, color=LINEA, grosor=1.2, guiones=None):
    extra = f' stroke-dasharray="{guiones}"' if guiones else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{grosor}"{extra}/>')


# tipo: (relleno, borde, grosor, guiones, color del rótulo)
ESTILOS = {
    "ejecuta": (ACENTO, "none", 0, None, FONDO),
    "espera": ("none", CIAN, 1.6, "6 4", CIAN),
    "lista": ("url(#rayado)", VIOLETA, 1.4, None, TEXTO),
    "bloqueada": (PANEL, AMBAR, 1.6, "4 3", AMBAR),
    "libre": ("none", SUAVE, 1.2, "3 3", SUAVE),
}


def _barra(tipo, x, y, w, h, rotulo=None):
    relleno, borde, grosor, guiones, color = ESTILOS[tipo]
    p = [_rect(x + 1, y, w - 2, h, relleno, borde, grosor, guiones)]
    if rotulo:
        peso = "600" if borde == "none" else "normal"
        p.append(texto(x + w / 2, y + h / 2 + 5, rotulo, color, 13, peso=peso))
    return "".join(p)


def _escala(eje_max):
    return lambda s: X0 + s * (X1 - X0) / eje_max


def _eje(xs, y, eje_max, paso=1, rotulo="tiempo (s)"):
    p = [_linea(X0, y, X1, y, SUAVE, 1.4)]
    for s in range(0, eje_max + 1, paso):
        p.append(_linea(xs(s), y, xs(s), y + 6, SUAVE, 1.4))
        p.append(texto(xs(s), y + 24, str(s), SUAVE, 13))
    p.append(texto(X0 - 16, y + 24, rotulo, SUAVE, 13, anclaje="end"))
    return "".join(p)


def _rejilla(xs, y0, y1, eje_max, paso=1):
    return "".join(_linea(xs(s), y0, xs(s), y1, LINEA, 0.6, "2 6")
                   for s in range(0, eje_max + 1, paso))


def _leyenda(y, items, x=40):
    p = []
    for tipo, rotulo in items:
        p.append(_barra(tipo, x, y - 13, 32, 16))
        p.append(texto(x + 40, y, rotulo, TEXTO, 13, anclaje="start"))
        x += 64 + len(rotulo) * 7.2
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 11: dónde vive cada conexión
# ---------------------------------------------------------------------------
R_REPLICAS, N_WORKERS, K_POOL = 3, 4, 10
MAX_CONEXIONES, RESERVADAS = 100, 3


def cmp_ancla_servidor():
    total = R_REPLICAS * N_WORKERS * K_POOL
    disponibles = MAX_CONEXIONES - RESERVADAS
    alto = 720
    aria = (
        "Ruta de una petición: el cliente llega al balanceador, que la manda a una "
        "de 3 réplicas; cada réplica tiene 4 workers y cada worker es un proceso "
        "con su propio loop y su propio pool local de 10 conexiones. Cada conexión "
        "de cada pool es un backend propio en Postgres, que admite 97 de 100 "
        "conexiones. Con 3 réplicas, 4 workers y 10 conexiones salen 120 "
        "conexiones, más de las 97 disponibles. Abajo, la variante con PgBouncer "
        "tiene dos poblaciones: 120 conexiones de cliente hacia PgBouncer y una "
        "población menor de conexiones de servidor hacia Postgres."
    )
    p = [_marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 40, "Cada conexión del pool de cada worker es un backend de Postgres",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 66,
                   "el límite del servidor se agota con réplicas × workers × pool, no con usuarios",
                   SUAVE, 14))

    # Cliente y balanceador.
    p.append(caja(24, 224, 100, 64, PANEL, SUAVE, radio=10))
    p.append(texto(74, 262, "cliente", TEXTO, 15, peso="600"))
    p.append(flecha(124, 256, 156, 256, CIAN, 2))
    p.append(caja(160, 224, 130, 64, PANEL, CIAN, radio=10))
    p.append(texto(225, 252, "balanceador", CIAN, 15, peso="600"))
    p.append(texto(225, 274, "elige una réplica", TEXTO, 13))
    p.append(flecha(290, 256, 322, 256, CIAN, 2))

    # Réplica con 4 workers.
    p.append(caja(326, 92, 470, 350, TINTE, LINEA, radio=12))
    p.append(texto(344, 116, "réplica 1 de 3", ACENTO, 15, anclaje="start", peso="600"))
    p.append(texto(780, 116, "N = 4 workers", SUAVE, 13, anclaje="end"))
    for i in range(N_WORKERS):
        y = 130 + i * 76
        p.append(caja(342, y, 438, 66, PANEL, LINEA, radio=8))
        p.append(texto(356, y + 28, f"worker {i + 1}", TEXTO, 14, anclaje="start", peso="600"))
        p.append(texto(356, y + 50, "proceso propio", SUAVE, 13, anclaje="start"))
        p.append(caja(458, y + 12, 112, 42, FONDO, VIOLETA, radio=6))
        p.append(texto(514, y + 29, "loop", VIOLETA, 14, peso="600"))
        p.append(texto(514, y + 46, "un hilo", TEXTO, 13))
        p.append(caja(584, y + 8, 186, 50, TINTE, ACENTO, radio=8, grosor=3))
        p.append(texto(677, y + 30, "pool local", ACENTO, 14, peso="600"))
        p.append(texto(677, y + 49, "k = 10 conexiones", TEXTO, 13))
    p.append(texto(561, 462, "réplicas 2 y 3: la misma estructura", SUAVE, 13))

    # Postgres.
    p.append(caja(868, 92, 190, 350, PANEL, ROJO, radio=12))
    p.append(texto(963, 118, "Postgres", ROJO, 16, peso="600"))
    p.append(texto(963, 138, "max_connections = 100", TEXTO, 13))
    for i in range(N_WORKERS):
        y = 130 + i * 76
        yc = y + 33
        p.append(flecha(770, yc, 860, yc, ACENTO, 2))
        if i == 0:
            p.append(texto(815, yc - 8, "una por", ACENTO, 13))
            p.append(texto(815, yc + 18, "conexión", ACENTO, 13))
    for i in range(N_WORKERS):
        y = 130 + i * 76
        p.append(caja(884, y + 14, 158, 40, FONDO, ROJO, radio=6))
        p.append(texto(963, y + 31, "10 backends", ROJO, 14, peso="600"))
        p.append(texto(963, y + 47, "de este worker", TEXTO, 13))

    # La cuenta.
    p.append(texto(ANCHO / 2, 500,
                   f"R × N × k = {R_REPLICAS} × {N_WORKERS} × {K_POOL} = {total} conexiones, "
                   f"contra {disponibles} disponibles ({MAX_CONEXIONES} menos {RESERVADAS} reservadas)",
                   AMBAR, 16, peso="600"))
    p.append(texto(ANCHO / 2, 524,
                   "el pool vive dentro de cada worker: los workers no se lo prestan entre sí",
                   TEXTO, 14))

    # Variante con PgBouncer.
    p.append(caja(24, 548, 1032, 156, PANEL, LINEA, radio=12))
    p.append(texto(44, 574, "Variante con PgBouncer: dos poblaciones de conexiones", AMBAR, 15,
                   anclaje="start", peso="600"))
    p.append(caja(44, 592, 310, 70, TINTE, ACENTO, radio=8, grosor=2))
    p.append(texto(199, 618, f"{total} conexiones de cliente", ACENTO, 15, peso="600"))
    p.append(texto(199, 642, "población 1: los pools de los workers", TEXTO, 13))
    p.append(flecha(354, 627, 416, 627, ACENTO, 2))
    p.append(caja(420, 592, 230, 70, FONDO, AMBAR, radio=8, grosor=2))
    p.append(texto(535, 618, "PgBouncer", AMBAR, 15, peso="600"))
    p.append(texto(535, 642, "pool_mode = transaction", TEXTO, 13))
    p.append(flecha(650, 627, 712, 627, ROJO, 2))
    p.append(caja(716, 592, 324, 70, PANEL, ROJO, radio=8, grosor=2))
    p.append(texto(878, 618, "conexiones de servidor", ROJO, 15, peso="600"))
    p.append(texto(878, 642, "población 2: un backend cada una", TEXTO, 13))
    p.append(texto(ANCHO / 2, 690,
                   "PgBouncer en modo transacción: 120 clientes comparten menos backends; "
                   "sujeto a max_client_conn", AMBAR, 14, peso="600"))
    p.append(cierre())
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 11: el loop durante la espera (cuatro peticiones, 0.5 s cada una)
# ---------------------------------------------------------------------------
ESPERA_MAX = 2     # eje de 0 a 2 s en los tres paneles


def _peticion(x, y, w, h, n):
    """La única clase de barra de la figura: espera de la petición n."""
    return (_rect(x + 1, y, w - 2, h, "none", CIAN, 1.8, "6 4")
            + texto(x + w / 2, y + h / 2 + 6, f"Petición {n}: espera", CIAN, 16))


def _ejes(xs, y0, y1, ya):
    """Cuadrícula cada 0.5 s desde y0 hasta el eje en ya, con su rótulo en segundos."""
    p = [_linea(X0, ya, X1, ya, SUAVE, 1.4)]
    for k in range(int(ESPERA_MAX / 0.5) + 1):
        t = k * 0.5
        etiqueta = f"{t:g}"
        p.append(_linea(xs(t), y0, xs(t), y1, LINEA, 0.8, "2 6"))
        p.append(_linea(xs(t), ya, xs(t), ya + 6, SUAVE, 1.4))
        p.append(texto(xs(t), ya + 26, etiqueta, SUAVE, 16))
    p.append(texto(X0 - 16, ya + 26, "tiempo (s)", SUAVE, 16, anclaje="end"))
    return "".join(p)


def _pie(y, que_pasa, total, color):
    return (texto(ANCHO / 2, y, que_pasa, TEXTO, 17)
            + texto(ANCHO / 2, y + 28, total, color, 18, peso="600"))


def cmp_async_vs_def():
    xs = _escala(ESPERA_MAX)
    w = xs(W_S) - X0
    n = PETICIONES
    alto = 1070
    aria = (
        "Tres paneles apilados con el mismo eje de 0 a 2 s y cuatro peticiones "
        "que llegan juntas y esperan 0.5 s cada una. Arriba, async def con "
        "time.sleep bloquea el loop, que es un solo hilo: las cuatro esperas van "
        "una tras otra en el mismo carril y suman 2 s. En medio, def con "
        "time.sleep da un hilo a cada petición y el loop queda libre: las cuatro "
        "esperas coinciden y el total es 0.5 s. Abajo, async def con await "
        "asyncio.sleep cede el turno: las cuatro esperas coinciden dentro del "
        "mismo loop, que queda libre mientras esperan, y el total es 0.5 s."
    )
    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 46, "El loop durante la espera", TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 78, "4 peticiones llegan juntas; cada una espera 0.5 s", SUAVE, 16))

    # a) una sola fila: las esperas se suman.
    y0 = 136
    p.append(texto(24, y0, "a) async def con time.sleep: bloquea el loop", AMBAR, 17,
                   anclaje="start", peso="600"))
    yb = y0 + 22
    p.append(texto(X0 - 16, yb + 24, "loop (1 hilo)", TEXTO, 15, anclaje="end", peso="600"))
    for i in range(n):
        p.append(_peticion(xs(i * W_S), yb, w, 36, i + 1))
    ya = yb + 62
    p.append(_ejes(xs, yb - 8, ya, ya))
    p.append(_pie(ya + 62, "las esperas se suman", "total: 2 s", AMBAR))

    # b) un hilo por petición y el loop libre.
    y0 = 350
    p.append(texto(24, y0, "b) def con time.sleep: un hilo por petición; el loop sigue libre",
                   CIAN, 17, anclaje="start", peso="600"))
    yl = y0 + 22
    p.append(texto(X0 - 16, yl + 24, "loop", TEXTO, 15, anclaje="end", peso="600"))
    p.append(_rect(xs(0), yl, xs(ESPERA_MAX) - X0, 36, "none", SUAVE, 1.4, "3 3"))
    p.append(texto((X0 + xs(ESPERA_MAX)) / 2, yl + 24, "libre", SUAVE, 16))
    for i in range(n):
        y = yl + 52 + i * 46
        p.append(texto(X0 - 16, y + 24, f"hilo {i + 1}", TEXTO, 15, anclaje="end", peso="600"))
        p.append(_peticion(xs(0), y, w, 36, i + 1))
    ya = yl + 52 + n * 46
    p.append(_ejes(xs, yl - 8, ya, ya))
    p.append(_pie(ya + 62, "las esperas coinciden: cada petición en su hilo", "total: 0.5 s",
                  CIAN))

    # c) todas dentro del mismo carril del loop.
    y0 = 736
    p.append(texto(24, y0, "c) async def con await asyncio.sleep: cede el turno", ACENTO, 17,
                   anclaje="start", peso="600"))
    yc = y0 + 22
    alto_caja = n * 40 + 12
    p.append(caja(X0, yc, xs(ESPERA_MAX) - X0, alto_caja, "none", SUAVE, radio=6, grosor=1.4))
    p.append(texto(X0 - 16, yc + alto_caja / 2 - 4, "loop (1 hilo)", TEXTO, 15,
                   anclaje="end", peso="600"))
    p.append(texto(X0 - 16, yc + alto_caja / 2 + 16, "un solo carril", SUAVE, 15, anclaje="end"))
    for i in range(n):
        p.append(_peticion(xs(0), yc + 6 + i * 40, w, 34, i + 1))
    p.append(texto(xs(0.5) + 24, yc + alto_caja / 2 + 6, "loop libre mientras esperan", ACENTO,
                   16, anclaje="start", peso="600"))
    ya = yc + alto_caja + 24
    p.append(_ejes(xs, yc - 8, ya, ya))
    p.append(_pie(ya + 62, "las esperas coinciden: await cede el loop", "total: 0.5 s", ACENTO))
    p.append(cierre())
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 12: cuándo se entera el cliente
# ---------------------------------------------------------------------------
def cmp_gantt_resultados():
    eje_max = 13
    xs = _escala(eje_max)
    alto = 640
    aria = (
        "Diagrama de tiempo de un evento que ocurre a los 10 s y tres formas de "
        "enterarse. Polling con consulta cada 3 s: consultas en 3, 6, 9 y 12 s; "
        "las tres primeras vuelven sin novedades y la cuarta trae el resultado, "
        "con 2 s de demora. Long polling: una consulta pendiente que el servidor "
        "retiene y responde en el evento. SSE: una respuesta abierta por la que "
        "el servidor escribe el evento en cuanto ocurre. Ámbar marca el evento."
    )
    p = [_marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 40,
                   "El polling se entera con demora; long polling y SSE, al ocurrir el evento",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 66, "un evento a los 10 s; el polling consulta cada 3 s",
                   SUAVE, 14))
    p.append(_leyenda(96, [("ejecuta", "petición o respuesta"),
                           ("espera", "conexión abierta, esperando")]))
    top, bottom = 124, 450
    p.append(_rejilla(xs, top, bottom, eje_max))

    # Evento.
    xe = xs(EVENTO_S)
    p.append(_linea(xe, top, xe, bottom, AMBAR, 2.4, "6 4"))
    p.append(texto(xe, top - 6, "evento: 10 s", AMBAR, 14, peso="600"))

    # Carril 1: polling.
    y1 = 158
    p.append(texto(X0 - 16, y1 + 14, "polling", TEXTO, 15, anclaje="end", peso="600"))
    p.append(texto(X0 - 16, y1 + 34, "consulta cada 3 s", SUAVE, 13, anclaje="end"))
    p.append(_linea(X0, y1 + 18, X1, y1 + 18, SUAVE, 1.2, "3 3"))
    for n, t in enumerate((3, 6, 9, 12), 1):
        con_resultado = t > EVENTO_S
        p.append(_barra("ejecuta", xs(t) - 8, y1 + 4, 16, 28))
        p.append(texto(xs(t), y1 + 54, f"consulta {n}", TEXTO, 13, peso="600"))
        p.append(texto(xs(t), y1 + 74, "trae el resultado" if con_resultado else "sin novedades",
                       ACENTO if con_resultado else SUAVE, 13,
                       peso="600" if con_resultado else "normal"))
    p.append(_linea(xe, y1 + 98, xs(12), y1 + 98, AMBAR, 2))
    p.append(texto((xe + xs(12)) / 2, y1 + 118, "demora de 2 s", AMBAR, 14, peso="600"))
    p.append(texto(xs(1.5), y1 + 118, "entre consultas no hay petición pendiente (con keep-alive el socket puede seguir abierto)", SUAVE, 13,
                   anclaje="start"))

    # Carril 2: long polling.
    y2 = 306
    p.append(texto(X0 - 16, y2 + 14, "long polling", TEXTO, 15, anclaje="end", peso="600"))
    p.append(texto(X0 - 16, y2 + 34, "una consulta pendiente", SUAVE, 13, anclaje="end"))
    p.append(_barra("espera", xs(0), y2, xe - xs(0), 34,
                    "consulta pendiente: el servidor no responde hasta que haya resultado"))
    p.append(_barra("ejecuta", xe - 8, y2, 16, 34))
    p.append(texto(xe - 8, y2 + 54, "responde en 10 s", ACENTO, 13, anclaje="start", peso="600"))
    p.append(_barra("espera", xe + 24, y2, xs(eje_max) - xe - 24, 34, "nueva consulta"))

    # Carril 3: SSE.
    y3 = 382
    p.append(texto(X0 - 16, y3 + 14, "SSE", TEXTO, 15, anclaje="end", peso="600"))
    p.append(texto(X0 - 16, y3 + 34, "una respuesta abierta", SUAVE, 13, anclaje="end"))
    p.append(_barra("espera", xs(0), y3, xs(eje_max) - xs(0), 34,
                    "respuesta abierta: el servidor escribe cuando ocurre algo"))
    p.append(_barra("ejecuta", xe - 8, y3, 16, 34))
    p.append(texto(xe + 14, y3 + 54, "el evento llega en 10 s", ACENTO, 13, anclaje="start",
                   peso="600"))

    p.append(_eje(xs, bottom, eje_max))

    # Resumen.
    p.append(caja(24, 500, 1032, 118, PANEL, LINEA, radio=12))
    cols = ((196, "polling", "2 s de demora", AMBAR,
             "4 consultas, 3 sin novedades"),
            (540, "long polling", "casi 0 s de demora", ACENTO,
             "una consulta pendiente por cliente"),
            (884, "SSE", "casi 0 s de demora", ACENTO,
             "una respuesta abierta por cliente"))
    for cx, nombre, demora, color, costo in cols:
        p.append(texto(cx, 530, nombre, TEXTO, 15, peso="600"))
        p.append(texto(cx, 556, demora, color, 15, peso="600"))
        p.append(texto(cx, 580, costo, SUAVE, 13))
    p.append(texto(ANCHO / 2, 606,
                   "con 20 clientes, el polling manda 80 consultas y 60 vuelven sin novedades",
                   AMBAR, 14, peso="600"))
    p.append(cierre())
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 12: quién inicia y qué queda abierto
# ---------------------------------------------------------------------------
def _secuencia(x, titulo, par, inicia, mensajes, abierto, queda, color_conexion):
    """Una columna: dos participantes, lifelines y mensajes (sentido, rótulo, color)."""
    ancho = 336
    xl, xr = x + 62, x + 274
    p = [caja(x, 92, ancho, 530, PANEL, LINEA, radio=12)]
    p.append(texto(x + ancho / 2, 120, titulo, TEXTO, 17, peso="600"))
    p.append(texto(x + ancho / 2, 144, f"inicia: {inicia}", AMBAR, 14, peso="600"))
    for cx, nombre in ((xl, par[0]), (xr, par[1])):
        p.append(caja(cx - 52, 160, 104, 36, FONDO, SUAVE, radio=8))
        p.append(texto(cx, 184, nombre, TEXTO, 14, peso="600"))
    y_ini = 214
    y_fin = y_ini + 52 * len(mensajes) + 6
    for cx in (xl, xr):
        p.append(_linea(cx, 196, cx, y_fin + 20, LINEA, 1.4, "5 4"))
        if abierto:
            p.append(_rect(cx - 7, y_ini + 6, 14, y_fin - y_ini - 16, "none", color_conexion,
                           1.6, "5 3", radio=3))
    for i, (sentido, rotulo, color) in enumerate(mensajes):
        y = y_ini + 52 * i + 40
        a, b = (xl, xr) if sentido == ">" else (xr, xl)
        d = 9 if sentido == ">" else -9
        p.append(flecha(a + d, y, b - d, y, color, 2))
        p.append(texto(x + ancho / 2, y - 8, rotulo, color, 13, peso="600"))
    yq = y_fin + 56
    p.append(_linea(x + 16, yq - 22, x + ancho - 16, yq - 22, LINEA, 1))
    p.append(texto(x + ancho / 2, yq, "queda abierto:", SUAVE, 13))
    for j, linea in enumerate(queda):
        p.append(texto(x + ancho / 2, yq + 24 + j * 22, linea, color_conexion if abierto else AMBAR,
                       14, peso="600"))
    return "".join(p)


def cmp_push_webhook():
    alto = 650
    aria = (
        "Tres diagramas de secuencia lado a lado. SSE: el cliente abre una "
        "petición GET y el servidor envía eventos por esa respuesta, que queda "
        "abierta y sólo va del servidor al cliente. WebSocket: el cliente abre "
        "con una petición de cambio de protocolo y después ambos lados envían "
        "mensajes por la misma conexión, que queda abierta en los dos sentidos. "
        "Webhook: el emisor llama con un POST a una URL del receptor y no queda "
        "ninguna petición pendiente entre eventos; inicia el emisor."
    )
    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 40,
                   "Quién inicia y qué queda abierto distingue SSE, WebSocket y webhook",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 66,
                   "las flechas van en el orden en que ocurren, de arriba hacia abajo", SUAVE, 14))
    p.append(_secuencia(
        12, "SSE", ("cliente", "servidor"), "el cliente",
        [(">", "GET /eventos", CIAN),
         ("<", "evento (servidor envía)", ACENTO),
         ("<", "evento (servidor envía)", ACENTO),
         ("<", "evento (servidor envía)", ACENTO)],
        True, ("una respuesta HTTP larga,", "sólo servidor → cliente"), CIAN))
    p.append(_secuencia(
        372, "WebSocket", ("cliente", "servidor"), "el cliente",
        [(">", "GET con Upgrade", CIAN),
         ("<", "101: cambia de protocolo", CIAN),
         (">", "mensaje (cliente envía)", ACENTO),
         ("<", "mensaje (servidor envía)", ACENTO)],
        True, ("una conexión, en", "los dos sentidos"), CIAN))
    p.append(_secuencia(
        732, "webhook", ("emisor", "receptor"), "el emisor",
        [(">", "POST /evento", CIAN),
         ("<", "200 OK", SUAVE)],
        False, ("no deja petición pendiente", "entre eventos"), AMBAR))
    # Nota del webhook: el receptor necesita una URL a la que el emisor llegue.
    p.append(texto(900, 510, "el receptor necesita una URL", AMBAR, 13))
    p.append(texto(900, 532, "a la que el emisor pueda llegar", AMBAR, 13))
    p.append(cierre())
    return "".join(p)


DIAGRAMAS_D = {
    "cmp-ancla-servidor": cmp_ancla_servidor,
    "cmp-async-vs-def": cmp_async_vs_def,
    "cmp-gantt-resultados": cmp_gantt_resultados,
    "cmp-push-webhook": cmp_push_webhook,
}
