"""Diagramas SVG de pools, recursos y arquitectura de la unidad 11 (Cómputo y concurrencia).

Viven aparte de tools/gen_computo.py para que dos autores no editen el mismo
diccionario: gen_computo.py importa DIAGRAMAS_B al final de su módulo y lo suma
a su catálogo, así que `python3 tools/gen_computo.py <id>` escribe también
estas figuras y tools/test_gen_computo.py las compara contra el disco.

Este módulo NO importa gen_computo: sólo la paleta y las primitivas de
tools/svg_base.py. Así no hay import circular (gen_computo importa este
archivo) y un cambio en los helpers privados de gen_computo no mueve estos
dibujos. Los pocos helpers de tiempo que se repiten (_rect, _linea, el eje)
son de una línea.

Las cifras de los esquemas son constantes y van rotuladas «esquema»; las
medidas (4.04 s, 3.32 s) son las de referencia del contrato de la unidad.
Sin letras griegas en el texto del SVG: la guarda de la unidad las prohíbe,
así que la tasa de la ley de Little se escribe «lambda».
"""
from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, ROJO, SUAVE, TEXTO, TINTE,
    VIOLETA, caja, cierre, flecha, marco, teclado, texto,
)

ANCHO = 1080
X0 = 190          # inicio del área de tiempo
X1 = 1040         # fin del área de tiempo

# Esquema del pool: 20 peticiones de 200 ms sobre 5 conexiones.
POOL_K = 5
POOL_N = 20
POOL_MS = 200

# Esquema de retener contra soltar: 6 tareas, pool de 3 conexiones.
SOLTAR_K = 3
SOLTAR_TAREAS = 6
CONSULTA_MS = 100
API_MS = 1000
ESCRIBE_MS = 100


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
    "vuelo": (PANEL, CIAN, 1.6, "6 4", CIAN),
    "espera_conexion": ("none", AMBAR, 1.6, "4 3", AMBAR),
    "bd": (ACENTO, "none", 0, None, FONDO),
    "ejecuta": (ACENTO, "none", 0, None, FONDO),
    "retenida": (PANEL, ROJO, 1.6, "6 4", ROJO),
    "calcula": (VIOLETA, "none", 0, None, FONDO),
    "libre": ("none", SUAVE, 1.2, "3 3", SUAVE),
}


def _barra(tipo, x, y, w, h, rotulo=None):
    relleno, borde, grosor, guiones, color = ESTILOS[tipo]
    p = [_rect(x + 1, y, w - 2, h, relleno, borde, grosor, guiones)]
    if rotulo and len(rotulo) * 7.4 + 10 <= w:
        peso = "600" if borde == "none" else "normal"
        p.append(texto(x + w / 2, y + h / 2 + 5, rotulo, color, 13, peso=peso))
    return "".join(p)


def _escala(eje_max):
    return lambda ms: X0 + ms * (X1 - X0) / eje_max


def _eje(xs, y, eje_max, paso, rotulo="tiempo (ms)"):
    p = [_linea(X0, y, X1, y, SUAVE, 1.4)]
    for ms in range(0, eje_max + 1, paso):
        p.append(_linea(xs(ms), y, xs(ms), y + 6, SUAVE, 1.4))
        p.append(texto(xs(ms), y + 24, str(ms), SUAVE, 13))
    p.append(texto(X0 - 16, y + 24, rotulo, SUAVE, 13, anclaje="end"))
    return "".join(p)


def _rejilla(xs, y0, y1, eje_max, paso):
    return "".join(_linea(xs(ms), y0, xs(ms), y1, LINEA, 0.6, "2 6")
                   for ms in range(0, eje_max + 1, paso))


def _leyenda(y, items, x=X0 - 150):
    p = []
    for tipo, rotulo in items:
        p.append(_barra(tipo, x, y - 13, 32, 16))
        p.append(texto(x + 40, y, rotulo, TEXTO, 13, anclaje="start"))
        x += 64 + len(rotulo) * 7.2
    return "".join(p)


def _total(xs, ms, y0, y1, rotulo, y_rotulo):
    xt = xs(ms)
    derecha = xt + 8 + len(rotulo) * 8 < ANCHO - 12
    return (_linea(xt, y0, xt, y1, AMBAR, 2, "6 4")
            + texto(xt + (8 if derecha else -8), y_rotulo, rotulo, AMBAR, 14,
                    anclaje="start" if derecha else "end", peso="600"))


# ---------------------------------------------------------------------------
# Página 5: pools y recursos
# ---------------------------------------------------------------------------

def cmp_roles_recursos():
    alto = 640
    aria = (
        "Cuatro columnas con cuatro roles distintos. Event loop: quién corre; "
        "planifica las tareas en un solo hilo y await libera ese hilo. "
        "Semáforo: quién entra; cuenta k permisos, no guarda objetos, y await "
        "no suelta el permiso. Pool: qué conexión usas; guarda conexiones "
        "reales, las abre, presta, recupera, cierra y reemplaza si se rompen, "
        "y await no devuelve la conexión. Servidor o base de datos: quién "
        "ejecuta, del otro lado de la red; el servidor de la clase usa un hilo "
        "por conexión. Abajo, una petición las recorre: corre hasta su await, "
        "toma un permiso con acquire, toma una conexión con get, el servidor "
        "ejecuta; al volver la respuesta, put devuelve la conexión, release "
        "suelta el permiso y el loop reanuda la tarea."
    )
    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42, "Cuatro roles distintos en una sola petición",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 70,
                   "loop, semáforo y pool viven en el cliente; el servidor o la BD, "
                   "del otro lado de la red", SUAVE, 14))

    columnas = (
        (ACENTO, "Event loop", "quién corre",
         ("planifica las tareas", "en un solo hilo", "una tarea cede en await",
          "y corre otra"),
         "asyncio.run(main())", "await libera el hilo: sí"),
        (AMBAR, "Semáforo", "quién entra",
         ("cuenta k permisos", "no guarda objetos", "sin permiso libre,",
          "la tarea espera"),
         "Semaphore(k)", "await libera el permiso: no"),
        (CIAN, "Pool", "qué conexión usas",
         ("guarda conexiones reales", "abre, presta, recupera,",
          "cierra y reemplaza rotas", "sin conexión libre, espera"),
         "Limits(max_connections=5)", "await libera la conexión: no"),
        (VIOLETA, "Servidor / BD", "quién ejecuta",
         ("recibe por la conexión", "y ejecuta la petición",
          "servidor de la clase:", "un hilo por conexión"),
         "ThreadingHTTPServer", "otro proceso, otra máquina"),
    )
    w, gap, x0 = 240, 20, 30
    centros = []
    for i, (color, nombre, rol, lineas, codigo, libera) in enumerate(columnas):
        x = x0 + i * (w + gap)
        cx = x + w / 2
        centros.append(cx)
        p.append(caja(x, 96, w, 280, PANEL, color, radio=10))
        p.append(texto(cx, 128, nombre, color, 18, peso="600"))
        p.append(texto(cx, 154, rol, TEXTO, 15, peso="600"))
        p.append(_linea(x + 20, 170, x + w - 20, 170, LINEA, 1))
        for k, linea in enumerate(lineas):
            p.append(texto(cx, 196 + k * 24, linea, TEXTO, 14))
        p.append(teclado(cx, 310, codigo, color, 13))
        p.append(texto(cx, 342, libera, SUAVE, 13))

    # Una petición de ida y vuelta.
    p.append(caja(30, 398, 1020, 172, TINTE, LINEA, radio=10))
    p.append(texto(50, 424, "una petición, de ida y de vuelta", TEXTO, 15,
                   anclaje="start", peso="600"))
    pasos = ("corre hasta su await", "acquire: toma permiso",
             "get: toma una conexión", "ejecuta y responde")
    for i, (cx, paso) in enumerate(zip(centros, pasos)):
        color = columnas[i][0]
        p.append(f'<circle cx="{cx}" cy="462" r="16" fill="{color}"/>')
        p.append(texto(cx, 467, str(i + 1), FONDO, 15, peso="600"))
        p.append(texto(cx, 500, paso, TEXTO, 14))
        if i < 3:
            p.append(flecha(cx + 22, 462, centros[i + 1] - 22, 462, LINEA, 2))
    p.append(flecha(centros[3], 520, centros[0], 520, ACENTO, 2))
    p.append(texto(ANCHO / 2, 550,
                   "5. vuelve la respuesta: put devuelve la conexión, release suelta "
                   "el permiso, el loop reanuda la tarea", ACENTO, 14))
    p.append(texto(ANCHO / 2, 606,
                   "un pool ≈ semáforo + objetos reales + ciclo de vida; el event loop "
                   "es opcional: un pool también sirve con hilos", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


def cmp_ciclo_conexion():
    alto = 620
    aria = (
        "Ciclo de vida de una conexión del pool en tres estados: sin abrir, "
        "libre en el pool y prestada en vuelo. Abrir cuesta TCP, TLS y "
        "autenticación. Prestar con get la entrega a una tarea; devolver con "
        "put la deja libre y se reutiliza sin abrir otra, eso es keep-alive. "
        "Se cierra si queda inactiva mucho tiempo o el servidor la cierra, y "
        "si se rompe en vuelo el pool la descarta y abre otra. Abajo: con 5 "
        "conexiones y 5 peticiones en vuelo, la petición 6 no puede usar "
        "ninguna; espera en la cola del pool y toma la primera que vuelve. "
        "HTTP/1.1 y una conexión de base de datos llevan una petición a la vez; "
        "HTTP/2 puede multiplexar varias."
    )
    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42, "Ciclo de una conexión del pool", TEXTO, 20,
                   peso="600"))
    p.append(texto(ANCHO / 2, 70,
                   "se abre una vez, se presta y se devuelve muchas veces", SUAVE, 14))

    estados = ((140, "sin abrir", "o cerrada", SUAVE),
               (540, "libre", "en el pool", ACENTO),
               (940, "prestada", "en vuelo: 1 petición", CIAN))
    y0, h, w = 170, 72, 200
    for cx, l1, l2, color in estados:
        p.append(caja(cx - w / 2, y0, w, h, PANEL, color, radio=12))
        p.append(texto(cx, y0 + 30, l1, color, 17, peso="600"))
        p.append(texto(cx, y0 + 54, l2, TEXTO, 14))

    # Rota en vuelo: arco por arriba, de prestada a sin abrir.
    p.append(f'<path d="M 920 {y0} C 760 70, 320 70, 160 {y0}" fill="none" '
             f'stroke="{ROJO}" stroke-width="2" marker-end="url(#f{ROJO[1:]})"/>')
    p.append(texto(540, 128, "rota en vuelo: el pool la descarta y abre otra", ROJO, 14))

    ym = y0 + h / 2
    p.append(flecha(244, ym - 6, 436, ym - 6, AMBAR, 2))
    p.append(texto(340, ym - 16, "abrir", AMBAR, 14, peso="600"))
    p.append(texto(340, ym + 14, "TCP + TLS + auth", SUAVE, 13))
    p.append(flecha(644, ym - 6, 836, ym - 6, CIAN, 2))
    p.append(texto(740, ym - 16, "prestar: get", CIAN, 14, peso="600"))
    p.append(texto(740, ym + 14, "a una tarea", SUAVE, 13))

    yb = y0 + h
    p.append(f'<path d="M 940 {yb} C 900 {yb + 70}, 620 {yb + 70}, 580 {yb + 2}" '
             f'fill="none" stroke="{ACENTO}" stroke-width="2" '
             f'marker-end="url(#f{ACENTO[1:]})"/>')
    p.append(texto(760, yb + 76, "devolver: put", ACENTO, 14, peso="600"))
    p.append(texto(760, yb + 96, "se reutiliza (keep-alive)", TEXTO, 13))
    p.append(f'<path d="M 500 {yb} C 460 {yb + 70}, 180 {yb + 70}, 140 {yb + 2}" '
             f'fill="none" stroke="{SUAVE}" stroke-width="2" '
             f'marker-end="url(#f{SUAVE[1:]})"/>')
    p.append(texto(320, yb + 76, "cerrar: inactiva mucho tiempo", SUAVE, 14, peso="600"))
    p.append(texto(320, yb + 96, "o el servidor la cerró", TEXTO, 13))

    # Cola del pool con 5 en vuelo.
    p.append(caja(30, 370, 1020, 160, TINTE, LINEA, radio=10))
    p.append(texto(50, 396, "pool de 5 conexiones, 5 peticiones en vuelo:", TEXTO, 15,
                   anclaje="start", peso="600"))
    p.append(caja(50, 414, 200, 60, FONDO, AMBAR, radio=8, grosor=2))
    p.append(texto(150, 440, "petición 6", AMBAR, 15, peso="600"))
    p.append(texto(150, 462, "en la cola del pool", TEXTO, 13))
    p.append(flecha(254, 444, 300, 444, AMBAR, 2))
    for k in range(5):
        x = 306 + k * 146
        p.append(caja(x, 414, 134, 60, PANEL, CIAN, radio=8))
        p.append(texto(x + 67, 440, f"conexión {k + 1}", CIAN, 14, peso="600"))
        p.append(texto(x + 67, 462, f"prestada a p{k + 1}", TEXTO, 13))
    p.append(texto(ANCHO / 2, 506,
                   "ninguna de las 5 le sirve mientras siga en vuelo; en cuanto una "
                   "vuelve (put), la petición 6 la toma", TEXTO, 14))

    p.append(texto(ANCHO / 2, 566,
                   "HTTP/1.1 y una conexión de BD llevan una petición a la vez; "
                   "HTTP/2 puede multiplexar varias", SUAVE, 14))
    p.append(texto(ANCHO / 2, 592,
                   "await no devuelve la conexión: sigue prestada hasta el put",
                   AMBAR, 14, peso="600"))
    p.append(cierre())
    return "".join(p)


def cmp_gantt_pool():
    eje_max, paso = 1000, 100
    xs = _escala(eje_max)
    olas = POOL_N // POOL_K
    total = olas * POOL_MS
    aria = (
        "Diagrama de Gantt con eje de tiempo en milisegundos de 0 a 1000. Un "
        "pool de 5 conexiones atiende 20 peticiones de 200 ms. Cada conexión "
        "es un carril y lleva una petición a la vez: la conexión 1 lleva p1, "
        "p6, p11 y p16, en cuatro olas de 200 ms. La petición 6 espera en la "
        "cola del pool de 0 a 200 ms, porque las 5 conexiones siguen en vuelo, "
        "y luego viaja por la conexión 1. La cola del pool tiene 15, 10, 5 y "
        "0 peticiones. Total del esquema 800 ms: 20 entre 5 son 4 olas por 0.2 s."
    )
    arriba, fila, barra = 126, 42, 26
    y_p6 = arriba + POOL_K * fila + 14
    y_cola = y_p6 + fila
    y_eje = y_cola + fila + 8
    alto = y_eje + 160

    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42,
                   "Un pool de 5 conexiones con 20 peticiones: cuatro olas",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 70,
                   "esquema: cada petición tarda 0.2 s y ocupa su conexión todo ese "
                   "tiempo; una conexión, una petición a la vez", SUAVE, 14))
    p.append(_rejilla(xs, arriba - 6, y_eje, eje_max, paso))
    for o in range(olas):
        p.append(texto(xs(o * POOL_MS + POOL_MS / 2), 108, f"ola {o + 1}", SUAVE, 13))

    for k in range(POOL_K):
        y = arriba + k * fila
        p.append(texto(X0 - 16, y + barra / 2 + 5, f"conexión {k + 1}", CIAN, 14,
                       anclaje="end", peso="600"))
        for o in range(olas):
            ini = o * POOL_MS
            p.append(_barra("vuelo", xs(ini), y, xs(ini + POOL_MS) - xs(ini), barra,
                            f"p{k + 1 + o * POOL_K}"))

    p.append(_linea(X0 - 170, y_p6 - 8, X1, y_p6 - 8, LINEA, 1))
    p.append(texto(X0 - 16, y_p6 + barra / 2 + 5, "petición 6", AMBAR, 14,
                   anclaje="end", peso="600"))
    p.append(_barra("espera_conexion", xs(0), y_p6, xs(POOL_MS) - xs(0), barra,
                    f"espera: {POOL_K} en vuelo"))
    p.append(_barra("vuelo", xs(POOL_MS), y_p6, xs(2 * POOL_MS) - xs(POOL_MS), barra,
                    "en la conexión 1"))

    p.append(texto(X0 - 16, y_cola + barra / 2 + 5, "cola del pool", TEXTO, 14,
                   anclaje="end"))
    for o in range(olas):
        esperan = POOL_N - (o + 1) * POOL_K
        ini = o * POOL_MS
        w = xs(ini + POOL_MS) - xs(ini)
        if esperan:
            p.append(_barra("espera_conexion", xs(ini), y_cola, w, barra,
                            f"{esperan} esperan conexión"))
        else:
            p.append(texto(xs(ini) + w / 2, y_cola + barra / 2 + 5, "vacía", SUAVE, 13))

    p.append(_eje(xs, y_eje, eje_max, paso))
    p.append(_total(xs, total, arriba - 30, y_eje, f"total {total} ms", 108))
    p.append(_leyenda(y_eje + 64, (
        ("vuelo", "en vuelo: espera la respuesta, CPU libre"),
        ("espera_conexion", "espera conexión: las 5 están prestadas"),
    )))
    p.append(texto(ANCHO / 2, y_eje + 104,
                   f"p16 a p20 toman conexión en {total - POOL_MS} ms y vuelven en {total}: "
                   f"{POOL_N} / {POOL_K} = {olas} olas × {POOL_MS} ms = {total} ms (esquema)",
                   AMBAR, 14, peso="600"))
    p.append(texto(ANCHO / 2, y_eje + 132,
                   "mientras p1 a p5 siguen en vuelo, p6 no puede usar ninguna de "
                   "sus conexiones", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


def _tramos_retener():
    """Carriles por conexión cuando cada tarea retiene la suya de principio a fin."""
    vida = CONSULTA_MS + API_MS + ESCRIBE_MS
    carriles = []
    for k in range(SOLTAR_K):
        tramos = []
        for ola in range(SOLTAR_TAREAS // SOLTAR_K):
            t = k + 1 + ola * SOLTAR_K
            t0 = ola * vida
            tramos += [
                ("bd", t0, t0 + CONSULTA_MS, f"t{t}"),
                ("retenida", t0 + CONSULTA_MS, t0 + CONSULTA_MS + API_MS,
                 f"t{t} espera la API con la conexión"),
                ("bd", t0 + CONSULTA_MS + API_MS, t0 + vida, f"t{t}"),
            ]
        carriles.append(tramos)
    return carriles, (SOLTAR_TAREAS // SOLTAR_K) * vida


def _tramos_soltar():
    """Cada tarea toma conexión sólo para consultar y para escribir."""
    olas = SOLTAR_TAREAS // SOLTAR_K
    carriles = []
    for k in range(SOLTAR_K):
        tramos = []
        for ola in range(olas):
            t0 = ola * CONSULTA_MS
            tramos.append(("bd", t0, t0 + CONSULTA_MS, f"t{k + 1 + ola * SOLTAR_K}"))
        for ola in range(olas):
            t0 = ola * CONSULTA_MS + CONSULTA_MS + API_MS
            tramos.append(("bd", t0, t0 + ESCRIBE_MS, f"t{k + 1 + ola * SOLTAR_K}"))
        carriles.append(tramos)
    total = (olas - 1) * CONSULTA_MS + CONSULTA_MS + API_MS + ESCRIBE_MS
    return carriles, total


def cmp_pool_soltar_antes():
    eje_max, paso = 2500, 250
    xs = _escala(eje_max)
    retener, total_r = _tramos_retener()
    soltar, total_s = _tramos_soltar()
    aria = (
        f"Dos diagramas de Gantt, esquema con eje de 0 a 2500 ms. Seis tareas "
        f"y un pool de 3 conexiones a la base de datos; cada tarea consulta la "
        f"BD 100 ms, llama a una API lenta 1000 ms y escribe en la BD 100 ms. "
        f"Arriba, retener: cada tarea guarda su conexión durante la llamada "
        f"lenta, cada conexión pasa 1000 de cada 1200 ms sin usarse y las "
        f"tareas 4 a 6 esperan en la cola del pool una ola entera, porque las 3 "
        f"conexiones están retenidas: total {total_r} ms. Abajo, soltar: la "
        f"tarea devuelve la conexión antes de llamar a la API y toma otra para "
        f"escribir; t4 a t6 esperan conexión solo 100 ms y las seis esperas a la "
        f"API se solapan sin ocupar conexión: total {total_s} ms."
    )
    fila, barra = 38, 24
    y_a = 132
    y_b = y_a + (SOLTAR_K + 1) * fila + 40
    y_eje = y_b + (SOLTAR_K + 3) * fila + 8
    alto = y_eje + 166

    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42, "Soltar la conexión antes de la espera larga",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 70,
                   "esquema: 6 tareas, pool de 3 conexiones; consulta la BD 100 ms, "
                   "llama a una API lenta 1000 ms, escribe 100 ms", SUAVE, 14))
    p.append(_rejilla(xs, y_a - 8, y_eje, eje_max, paso))

    p.append(texto(30, y_a - 14, "Retener: la tarea guarda su conexión mientras espera la API",
                   ROJO, 15, anclaje="start", peso="600"))
    for k, tramos in enumerate(retener):
        y = y_a + k * fila
        p.append(texto(X0 - 16, y + barra / 2 + 5, f"conexión {k + 1}", TEXTO, 14,
                       anclaje="end"))
        for tipo, ini, fin, rot in tramos:
            p.append(_barra(tipo, xs(ini), y, xs(fin) - xs(ini), barra, rot))
    vida = CONSULTA_MS + API_MS + ESCRIBE_MS
    y = y_a + SOLTAR_K * fila
    p.append(texto(X0 - 16, y + barra / 2 + 5, "cola del pool", AMBAR, 14, anclaje="end"))
    p.append(_barra("espera_conexion", xs(0), y, xs(vida) - xs(0), barra,
                    f"t4 a t6 esperan conexión: las {SOLTAR_K} están retenidas"))
    p.append(_total(xs, total_r, y_a - 8, y_a + (SOLTAR_K + 1) * fila - 10,
                    f"total {total_r} ms (esquema)", y_a - 14))

    p.append(_linea(20, y_b - 34, ANCHO - 20, y_b - 34, LINEA, 1))
    p.append(texto(30, y_b - 14, "Soltar: devuelve la conexión antes de llamar a la API",
                   ACENTO, 15, anclaje="start", peso="600"))
    for k, tramos in enumerate(soltar):
        y = y_b + k * fila
        p.append(texto(X0 - 16, y + barra / 2 + 5, f"conexión {k + 1}", TEXTO, 14,
                       anclaje="end"))
        for tipo, ini, fin, rot in tramos:
            p.append(_barra(tipo, xs(ini), y, xs(fin) - xs(ini), barra, rot))
        libre0, libre1 = 2 * CONSULTA_MS, CONSULTA_MS + API_MS
        p.append(_barra("libre", xs(libre0), y + 3, xs(libre1) - xs(libre0), barra - 6,
                        "libre: la BD atiende a otras"))
    y = y_b + SOLTAR_K * fila
    p.append(texto(X0 - 16, y + barra / 2 + 5, "cola del pool", AMBAR, 14, anclaje="end"))
    p.append(_barra("espera_conexion", xs(0), y, xs(CONSULTA_MS) - xs(0), barra))
    p.append(texto(xs(CONSULTA_MS) + 8, y + barra / 2 + 5,
                   "t4 a t6 esperan conexión 0–100 ms: t1 a t3 consultan",
                   AMBAR, 13, anclaje="start"))
    for j, (ini, rot) in enumerate(((CONSULTA_MS, "API: t1 a t3"),
                                    (2 * CONSULTA_MS, "API: t4 a t6"))):
        y = y_b + (SOLTAR_K + 1 + j) * fila
        p.append(texto(X0 - 16, y + barra / 2 + 5, rot, CIAN, 14, anclaje="end"))
        p.append(_barra("vuelo", xs(ini), y, xs(ini + API_MS) - xs(ini), barra,
                        "esperan la API sin retener conexión"))
    p.append(_total(xs, total_s, y_b - 8, y_b + (SOLTAR_K + 3) * fila - 10,
                    f"total {total_s} ms (esquema)", y_b - 14))

    p.append(_eje(xs, y_eje, eje_max, paso))
    p.append(_leyenda(y_eje + 64, (
        ("bd", "usa la BD con una conexión"),
        ("retenida", "conexión retenida sin uso"),
        ("vuelo", "espera la API, sin conexión"),
        ("espera_conexion", "espera conexión: pool lleno"),
    )))
    p.append(texto(ANCHO / 2, y_eje + 104,
                   f"retener: t4 a t6 esperan la ola 1 entera; 2 olas × (100 + 1000 + 100) "
                   f"= {total_r} ms", AMBAR, 14, peso="600"))
    p.append(texto(ANCHO / 2, y_eje + 130,
                   f"soltar: t4 a t6 consultan de 100 a 200 ms, la API vuelve en 1200 y "
                   f"escriben hasta {total_s}: total {total_s} ms", AMBAR, 14, peso="600"))
    p.append(cierre())
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 6: calcular en paralelo sin bloquear el loop
# ---------------------------------------------------------------------------

def cmp_run_in_executor():
    eje_max, paso = 2500, 250
    xs = _escala(eje_max)
    calc = 2000
    aria = (
        "Diagrama de Gantt con eje de 0 a 2500 ms y tres carriles. La "
        "corrutina ejecuta un instante, manda un cálculo de 2000 ms a un "
        "ProcessPoolExecutor con run_in_executor y espera el Future con await. "
        "El carril del hilo del loop muestra un latido cada 100 ms que sigue "
        "sin pausa durante los 2000 ms, porque el loop no calcula. El carril "
        "del proceso del pool calcula de 0 a 2000 ms en otra CPU con su propio "
        "GIL. En 2000 ms el Future queda listo, el resultado vuelve al loop y "
        "la corrutina se reanuda."
    )
    arriba, fila, barra = 120, 56, 26
    y_cor, y_loop, y_proc = arriba, arriba + fila, arriba + 2 * fila
    y_eje = y_proc + barra + 44
    alto = y_eje + 182

    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42, "run_in_executor: el cálculo sale del hilo del loop",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 70,
                   "una corrutina manda 2 s de cálculo a un pool de procesos; otra "
                   "late cada 100 ms en el mismo loop", SUAVE, 14))
    p.append(_rejilla(xs, arriba - 8, y_eje, eje_max, paso))

    p.append(texto(X0 - 16, y_cor + barra / 2 + 5, "corrutina", TEXTO, 14, anclaje="end"))
    p.append(texto(X0 - 16, y_loop - 8, "latido: otra corrutina", SUAVE, 13, anclaje="end"))
    p.append(_barra("ejecuta", xs(0), y_cor, xs(20) - xs(0), barra))
    p.append(_barra("vuelo", xs(20), y_cor, xs(calc) - xs(20), barra,
                    "await: espera el Future; el hilo del loop queda libre"))
    p.append(_barra("ejecuta", xs(calc), y_cor, xs(calc + 20) - xs(calc), barra))

    p.append(texto(X0 - 16, y_loop + barra / 2 + 5, "hilo del loop", ACENTO, 14,
                   anclaje="end", peso="600"))
    for ms in range(0, eje_max, 100):
        p.append(_rect(xs(ms), y_loop, 6, barra, ACENTO, radio=1))

    p.append(texto(X0 - 16, y_proc + barra / 2 + 5, "proceso del pool", VIOLETA, 14,
                   anclaje="end", peso="600"))
    p.append(_barra("calcula", xs(0), y_proc, xs(calc) - xs(0), barra,
                    "calcula 2000 ms en otro proceso, en otra CPU, con su propio GIL"))
    p.append(flecha(xs(10), y_cor + barra + 2, xs(10), y_proc - 3, CIAN, 2))
    p.append(texto(xs(0), y_proc + barra + 22,
                   "run_in_executor envía calcula(datos) al pool", CIAN, 13,
                   anclaje="start"))
    p.append(flecha(xs(calc) + 4, y_proc - 2, xs(calc) + 4, y_cor + barra + 3, AMBAR, 2))
    p.append(texto(xs(calc) + 12, y_proc + barra / 2 + 5, "Future listo", AMBAR, 14,
                   anclaje="start", peso="600"))

    p.append(_eje(xs, y_eje, eje_max, paso))
    p.append(_leyenda(y_eje + 64, (
        ("ejecuta", "corre en el hilo del loop"),
        ("vuelo", "espera el Future, CPU libre"),
        ("calcula", "calcula en otro proceso y otra CPU"),
    )))
    p.append(texto(ANCHO / 2, y_eje + 102,
                   f"la corrutina termina en {calc + 20} ms: {calc} de cálculo en el pool "
                   f"+ 20 suyos en el loop; mientras, el loop late {calc // 100} veces",
                   AMBAR, 14, peso="600"))
    p.append(texto(ANCHO / 2, y_eje + 128,
                   "los latidos siguen cada 100 ms durante los 2000 ms: el hilo del "
                   "loop sólo envía y recibe", TEXTO, 14))
    p.append(texto(ANCHO / 2, y_eje + 154,
                   "con el cálculo dentro del loop, ese carril quedaría vacío 2000 ms",
                   SUAVE, 14))
    p.append(cierre())
    return "".join(p)


def cmp_arq_offload():
    alto = 660
    aria = (
        "Arquitectura de offload. Los clientes llegan a un proceso principal "
        "con un event loop en un hilo, que atiende las conexiones y nunca "
        "calcula: el manejador hace await de loop.run_in_executor. El trabajo "
        "pasa por una cola interna, con los argumentos serializados con "
        "pickle, a un pool de P procesos, cada uno con su GIL y su CPU. El "
        "resultado vuelve serializado, completa un Future y la corrutina se "
        "reanuda. Cuántos procesos: min(k, P). Cuesta copiar datos entre "
        "procesos. Sí para cálculo de decenas de milisegundos o más; no para "
        "microsegundos. Abajo, la versión en varias máquinas: API, cola "
        "externa como Redis o RabbitMQ, workers y almacén de resultados."
    )
    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42, "Offload: el loop atiende, un pool de procesos calcula",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 70,
                   "el manejador no calcula: manda el trabajo por una cola a P "
                   "procesos y espera el resultado con await", SUAVE, 14))

    for k, y in enumerate((150, 220, 290)):
        p.append(caja(40, y, 110, 44, PANEL, LINEA, radio=8))
        p.append(texto(95, y + 28, f"cliente {k + 1}", TEXTO, 14))
        p.append(flecha(152, y + 22, 216, y + 22, LINEA, 2))

    p.append(caja(220, 120, 250, 240, PANEL, ACENTO, radio=10))
    p.append(texto(345, 150, "proceso principal", ACENTO, 16, peso="600"))
    p.append(texto(345, 174, "event loop · 1 hilo", TEXTO, 14))
    p.append(texto(345, 212, "atiende miles de conexiones", TEXTO, 14))
    p.append(texto(345, 236, "el manejador hace", SUAVE, 13))
    p.append(teclado(345, 262, "await loop.run_in_executor(", ACENTO, 13))
    p.append(teclado(345, 284, "    pool, calcula, datos)", ACENTO, 13))
    p.append(texto(345, 324, "nunca calcula dentro", AMBAR, 14, peso="600"))

    p.append(flecha(472, 200, 526, 200, CIAN, 2))
    p.append(caja(530, 150, 120, 100, PANEL, CIAN, radio=8))
    for k in range(4):
        p.append(_rect(545, 162 + k * 21, 90, 15, TINTE, CIAN, 1, radio=3))
    p.append(texto(590, 272, "cola interna", CIAN, 14, peso="600"))
    p.append(texto(590, 294, "argumentos", SUAVE, 13))
    p.append(texto(590, 312, "en pickle", SUAVE, 13))
    p.append(flecha(652, 200, 696, 200, CIAN, 2))

    p.append(caja(700, 120, 340, 240, PANEL, VIOLETA, radio=10))
    p.append(texto(870, 150, "pool de P procesos", VIOLETA, 16, peso="600"))
    p.append(texto(870, 172, "trabajadores reutilizables", SUAVE, 13))
    for k, (x, y) in enumerate(((715, 190), (875, 190), (715, 274), (875, 274))):
        p.append(caja(x, y, 150, 70, FONDO, VIOLETA, radio=8))
        p.append(texto(x + 75, y + 30, f"proceso {k + 1}", TEXTO, 14, peso="600"))
        p.append(texto(x + 75, y + 52, "su GIL · su CPU", SUAVE, 13))

    # Regreso del resultado.
    p.append(_linea(870, 362, 870, 396, AMBAR, 2))
    p.append(_linea(870, 396, 345, 396, AMBAR, 2))
    p.append(flecha(345, 396, 345, 364, AMBAR, 2))
    p.append(texto(607, 420, "resultado en pickle → Future → la corrutina se reanuda",
                   AMBAR, 14, peso="600"))

    p.append(texto(40, 460, "cuántos procesos: min(k, P), con k tareas de cálculo "
                   "listas y P CPU lógicas", TEXTO, 14, anclaje="start"))
    p.append(texto(40, 486, "qué cuesta: copiar argumentos y resultados entre procesos "
                   "(IPC); la función vive en un módulo, no en una lambda",
                   TEXTO, 14, anclaje="start"))
    p.append(texto(40, 512, "sí: cálculo de decenas de ms o más en un servicio async  ·  "
                   "no: cálculo de microsegundos (serializar cuesta más)",
                   SUAVE, 14, anclaje="start"))

    p.append(caja(30, 534, 1020, 106, TINTE, LINEA, radio=10))
    p.append(texto(50, 560, "en varias máquinas, el mismo patrón:", SUAVE, 14,
                   anclaje="start"))
    cajas = ((60, 120, "API"), (230, 250, "cola: Redis o RabbitMQ"),
             (530, 180, "workers (Celery)"), (760, 270, "almacén de resultados"))
    for i, (x, w, rot) in enumerate(cajas):
        p.append(caja(x, 576, w, 44, PANEL, LINEA, radio=8))
        p.append(texto(x + w / 2, 604, rot, TEXTO, 14))
        if i < len(cajas) - 1:
            sig = cajas[i + 1][0]
            p.append(flecha(x + w + 4, 598, sig - 4, 598, LINEA, 2))
    p.append(cierre())
    return "".join(p)


# ---------------------------------------------------------------------------
# Página 8: arquitectura y estrategia
# ---------------------------------------------------------------------------

def cmp_arq_servidores():
    alto = 560
    aria = (
        "Tres modelos de servidor lado a lado. Hilo por conexión: accept "
        "entrega cada conexión a un hilo, todos tocan un estado con un Lock; "
        "cuesta un hilo con su pila por conexión; sí para pocas conexiones y "
        "código bloqueante, no para miles de conexiones ociosas; ejemplo, el "
        "ThreadingHTTPServer de la clase. Event loop: un selector vigila los "
        "sockets, las listas pasan a una cola y un hilo las ejecuta una a la "
        "vez; sí para miles de conexiones que esperan, no para manejadores que "
        "calculan o bloquean; nginx, Node.js, Uvicorn. Prefork: un maestro "
        "crea K procesos que aceptan del mismo socket, cada uno con su GIL; sí "
        "para cálculo por petición y aislar fallos, no para estado compartido "
        "en memoria; Gunicorn, PostgreSQL. Abajo, el híbrido: un event loop "
        "por proceso."
    )
    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42, "Tres formas de atender muchas conexiones",
                   TEXTO, 20, peso="600"))
    p.append(texto(ANCHO / 2, 70, "qué consume cada conexión decide cuántas aguantas",
                   SUAVE, 14))

    w = 330
    cols = (
        (30, CIAN, "hilo por conexión", "por conexión: un hilo con su pila",
         "sí: pocas conexiones, código bloqueante",
         "no: miles de conexiones ociosas",
         "real: ThreadingHTTPServer, Apache"),
        (375, ACENTO, "event loop", "por conexión: un socket y una corrutina",
         "sí: miles de conexiones que esperan",
         "no: manejadores que calculan o bloquean",
         "real: nginx, Node.js, Uvicorn"),
        (720, VIOLETA, "prefork / multiproceso", "por worker: un proceso y su memoria",
         "sí: cálculo por petición, aislar fallos",
         "no: estado en memoria compartido",
         "real: Gunicorn, PostgreSQL"),
    )
    for x, color, nombre, consume, si, no, real in cols:
        c = x + w / 2
        p.append(caja(x, 92, w, 388, PANEL, color, radio=10))
        p.append(texto(c, 122, nombre, color, 18, peso="600"))
        p.append(texto(c, 146, consume, SUAVE, 13))
        p.append(texto(x + 18, 400, si, ACENTO, 13, anclaje="start"))
        p.append(texto(x + 18, 426, no, ROJO, 13, anclaje="start"))
        p.append(texto(x + 18, 456, real, TEXTO, 13, anclaje="start"))

    # Columna 1: hilo por conexión.
    c = 195
    p.append(caja(c - 70, 168, 140, 34, FONDO, LINEA, radio=6))
    p.append(teclado(c, 190, "accept", TEXTO, 14))
    for k, dx in enumerate((-105, 0, 105)):
        p.append(flecha(c + dx * 0.4, 204, c + dx, 232, LINEA, 1.6))
        p.append(caja(c + dx - 45, 236, 90, 34, TINTE, CIAN, radio=6))
        p.append(texto(c + dx, 258, f"hilo {k + 1}", TEXTO, 14))
        p.append(flecha(c + dx, 272, c + dx * 0.4, 296, LINEA, 1.6))
    p.append(caja(c - 90, 300, 180, 34, FONDO, AMBAR, radio=6))
    p.append(texto(c, 322, "estado + un Lock", AMBAR, 14))
    p.append(texto(c, 362, "sin tope: un pico abre miles", ROJO, 13))

    # Columna 2: event loop.
    c = 540
    p.append(caja(c - 110, 168, 220, 34, FONDO, LINEA, radio=6))
    p.append(texto(c, 190, "selector: sockets en espera", TEXTO, 14))
    p.append(flecha(c, 204, c, 232, LINEA, 1.6))
    p.append(caja(c - 110, 236, 220, 34, TINTE, ACENTO, radio=6))
    p.append(texto(c, 258, "cola de listas: A · B · C", TEXTO, 14))
    p.append(flecha(c, 272, c, 296, LINEA, 1.6))
    p.append(caja(c - 110, 300, 220, 34, FONDO, ACENTO, radio=6))
    p.append(texto(c, 322, "1 hilo ejecuta a una a la vez", ACENTO, 14))
    p.append(_linea(c - 112, 317, c - 146, 317, AMBAR, 1.6))
    p.append(_linea(c - 146, 317, c - 146, 185, AMBAR, 1.6))
    p.append(flecha(c - 146, 185, c - 114, 185, AMBAR, 1.6))
    p.append(texto(c - 141, 224, "await", AMBAR, 13, anclaje="start"))
    p.append(texto(c, 362, "algo bloqueante congela a todas", ROJO, 13))

    # Columna 3: prefork.
    c = 885
    p.append(caja(c - 70, 168, 140, 34, FONDO, LINEA, radio=6))
    p.append(texto(c, 190, "maestro", TEXTO, 14))
    for k, dx in enumerate((-105, 0, 105)):
        p.append(flecha(c + dx * 0.4, 204, c + dx, 230, LINEA, 1.6))
        p.append(caja(c + dx - 47, 234, 94, 44, TINTE, VIOLETA, radio=6))
        p.append(texto(c + dx, 253, f"proceso {k + 1}", TEXTO, 14))
        p.append(texto(c + dx, 271, "su GIL", SUAVE, 13))
        p.append(flecha(c + dx * 0.4, 300, c + dx, 282, LINEA, 1.6))
    p.append(caja(c - 100, 300, 200, 34, FONDO, LINEA, radio=6))
    p.append(texto(c, 322, "socket compartido", TEXTO, 14))
    p.append(texto(c, 362, "K procesos × memoria de cada uno", ROJO, 13))

    p.append(texto(ANCHO / 2, 520,
                   "híbrido en producción: K procesos, cada uno con su event loop "
                   "(Gunicorn con UvicornWorker; nginx)", AMBAR, 14, peso="600"))
    p.append(cierre())
    return "".join(p)


def cmp_arq_little():
    alto = 620
    en_vuelo, w_s, n = 32, 0.2, 500
    tandas = -(-n // en_vuelo)
    cota = tandas * w_s
    aria = (
        "Ley de Little: L igual a lambda por W, peticiones en vuelo igual a "
        "throughput por latencia. Un tubo con 32 peticiones en vuelo, cada una "
        "dentro 0.2 s, entran y salen 160 por segundo: 32 = 160 por 0.2. "
        "Debajo, 500 llamadas con 32 en vuelo son 16 tandas de 0.2 s: cota de "
        "3.2 s contra 3.32 s medidos, 151 por segundo. En serie, 20 llamadas "
        "con L = 1 dan 5 por segundo; medido 20 entre 4.04 s, 4.95 por "
        "segundo. Despejando, W = 32 / 151, unos 0.212 s: 12 ms de sobrecosto. "
        "El servidor de la clase con 151 por segundo y 0.2 s tiene unos 30 "
        "hilos ocupados; si W sube a 2 s, unos 300."
    )
    p = [marco(ANCHO, alto, aria)]
    p.append(texto(ANCHO / 2, 42, "Ley de Little: en vuelo = throughput × latencia",
                   TEXTO, 20, peso="600"))
    p.append(teclado(ANCHO / 2, 74, "L = lambda · W", ACENTO, 18))
    p.append(texto(ANCHO / 2, 98,
                   "L: peticiones en vuelo · lambda: peticiones por segundo · "
                   "W: segundos que pasa cada una dentro", SUAVE, 13))

    p.append(flecha(40, 172, 184, 172, CIAN, 2))
    p.append(texto(112, 160, "entran 160/s", CIAN, 14, peso="600"))
    p.append(caja(190, 122, 700, 100, PANEL, CIAN, radio=14))
    for k in range(en_vuelo):
        fila, col = divmod(k, 16)
        p.append(f'<circle cx="{228 + col * 42}" cy="{152 + fila * 40}" r="12" '
                 f'fill="{CIAN}"/>')
    p.append(flecha(894, 172, 1040, 172, CIAN, 2))
    p.append(texto(966, 160, "salen 160/s", CIAN, 14, peso="600"))
    p.append(texto(540, 246, "L = 32 en vuelo; cada una pasa W = 0.2 s dentro",
                   TEXTO, 14))
    p.append(teclado(540, 276, "32 = 160/s · 0.2 s", ACENTO, 16))

    # 500 llamadas en 16 tandas.
    eje_max = 3.5

    def xs(s):
        return X0 + s * (X1 - X0) / eje_max

    y = 322
    p.append(texto(X0 - 16, y + 20, f"{tandas} tandas de 32", TEXTO, 14, anclaje="end"))
    for k in range(tandas):
        x0, x1 = xs(k * w_s), xs((k + 1) * w_s)
        p.append(_barra("vuelo", x0, y, x1 - x0, 28, str(k + 1)))
    y_eje = y + 48
    p.append(_linea(X0, y_eje, X1, y_eje, SUAVE, 1.4))
    for k in range(8):
        s = k * 0.5
        p.append(_linea(xs(s), y_eje, xs(s), y_eje + 6, SUAVE, 1.4))
        p.append(texto(xs(s), y_eje + 24, f"{s:.1f}", SUAVE, 13))
    p.append(texto(X0 - 16, y_eje + 24, "tiempo (s)", SUAVE, 13, anclaje="end"))
    p.append(_linea(xs(cota), y - 16, xs(cota), y_eje, AMBAR, 2, "6 4"))
    p.append(texto(xs(cota) - 6, y - 22, f"cota {tandas} tandas × 0.2 s = {cota:.1f} s",
                   AMBAR, 14, anclaje="end", peso="600"))
    p.append(_linea(xs(3.32), y - 6, xs(3.32), y_eje + 30, ROJO, 2))
    p.append(texto(xs(3.32) + 4, y_eje + 48, "medido 3.32 s", ROJO, 14,
                   anclaje="end", peso="600"))

    lineas = (
        (TEXTO, "en serie, 20 llamadas: L = 1, W ≈ 0.2 s → 5/s; medido 20 / 4.04 s "
                "= 4.95/s"),
        (TEXTO, "500 llamadas con 32 en vuelo: 32 / 0.2 s = 160/s → cota 3.2 s; "
                "medido 3.32 s = 151/s"),
        (TEXTO, "latencia despejada: W = L / lambda = 32 / 151 ≈ 0.212 s, "
                "12 ms de sobrecosto por llamada"),
        (AMBAR, "servidor de la clase: 151/s × 0.2 s ≈ 30 hilos ocupados; si W "
                "sube a 2 s, ≈ 300 hilos"),
    )
    for k, (color, linea) in enumerate(lineas):
        p.append(texto(60, 466 + k * 28, linea, color, 14, anclaje="start"))
    p.append(texto(ANCHO / 2, 598,
                   "mediciones de una corrida en una máquina de 8 CPU lógicas; la "
                   "cota supone W = 0.2 s exactos y sin sobrecosto", SUAVE, 13))
    p.append(cierre())
    return "".join(p)


DIAGRAMAS_B = {
    "cmp-roles-recursos": cmp_roles_recursos,
    "cmp-ciclo-conexion": cmp_ciclo_conexion,
    "cmp-gantt-pool": cmp_gantt_pool,
    "cmp-pool-soltar-antes": cmp_pool_soltar_antes,
    "cmp-run-in-executor": cmp_run_in_executor,
    "cmp-arq-offload": cmp_arq_offload,
    "cmp-arq-servidores": cmp_arq_servidores,
    "cmp-arq-little": cmp_arq_little,
}
