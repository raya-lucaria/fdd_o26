"""Genera los diagramas SVG de la unidad 9 (Python): 9.1 ambientes, 9.2 Python por dentro y 9.3 Elegir el stack.

Las primitivas y la paleta salen de tools/svg_base.py: un solo lugar declara
los colores de skins/fdd-eva.yaml.

Este archivo es la unica fuente de verdad de esos SVG. Editar un .svg a mano es
un error que tools/test_gen_python.py detecta.

Los ids llevan prefijo "py-" a proposito: los ids de objeto numerado de Raya
son unicos en TODO el curso, no por pagina.
"""
import sys
from pathlib import Path

from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, ROJO, SUAVE, TEXTO, TINTE,
    VIOLETA, caja, chip, cierre, flecha, marco, teclado, texto,
)

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/9_python/_assets"


def _punteada(x, y, w, h, color=SUAVE):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" '
            f'stroke="{color}" stroke-width="1.6" stroke-dasharray="8 6"/>')


def py_mapa():
    """Que produce que en un proyecto uv, y que va a git."""
    ancho, alto = 1080, 560
    aria = (
        "Tres cajas en fila. La primera, lo que pides: pyproject.toml, con "
        "rangos como rich mayor o igual a 15, que escribes tu o uv add. Una "
        "flecha rotulada uv lock lleva a la segunda, lo que se resolvio: "
        "uv.lock, con version exacta y hash de cada paquete, tambien las "
        "transitivas, que se bajan de PyPI. Una flecha rotulada uv sync lleva a "
        "la tercera, lo que esta instalado: la carpeta .venv con su python y "
        "su site-packages, desechable. De .venv sale una flecha uv run hacia tu "
        "programa, y uv python install pone el interprete. Abajo: "
        "pyproject.toml y uv.lock van a git; .venv no va a git, se borra y se "
        "recrea con uv sync"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué produce qué en un proyecto uv", TEXTO, 21, peso="600"))

    # PyPI, arriba de la caja del lock.
    p.append(caja(440, 70, 200, 40, PANEL, VIOLETA, radio=8))
    p.append(teclado(540, 96, "PyPI", VIOLETA, 16))
    p.append(flecha(540, 112, 540, 136, VIOLETA, 2))
    p.append(texto(700, 96, "de dónde se bajan", SUAVE, 13, anclaje="start"))

    cajas = (
        (40, AMBAR, "lo que pides", "pyproject.toml", "rangos: rich>=15", "lo escribes tú o uv add"),
        (400, CIAN, "lo que se resolvió", "uv.lock", "versión exacta + hash", "de cada paquete, también las transitivas"),
        (760, ACENTO, "lo que está instalado", ".venv/", "bin/python + site-packages/", "desechable"),
    )
    for x, color, titulo, archivo, linea1, linea2 in cajas:
        p.append(caja(x, 140, 280, 150, PANEL, color))
        p.append(texto(x + 140, 170, titulo, color, 15, peso="600"))
        p.append(teclado(x + 140, 206, archivo, color, 19))
        p.append(texto(x + 140, 240, linea1, TEXTO, 13.5))
        p.append(texto(x + 140, 264, linea2, SUAVE, 12.5))

    p.append(flecha(324, 215, 394, 215, CIAN, 2.5))
    p.append(chip(359, 190, "uv lock", CIAN, tam=13))
    p.append(flecha(684, 215, 754, 215, ACENTO, 2.5))
    p.append(chip(719, 190, "uv sync", ACENTO, tam=13))

    # Tu entrada: uv add escribe el toml (y de paso lock + sync).
    p.append(caja(110, 360, 140, 44, FONDO, AMBAR, radio=8))
    p.append(texto(180, 388, "tú", AMBAR, 15, peso="600"))
    p.append(flecha(180, 356, 180, 296, AMBAR, 2.5))
    p.append(chip(268, 330, "uv add rich", AMBAR, tam=13))

    # El interprete tambien lo pone uv.
    p.append(caja(400, 360, 280, 44, FONDO, SUAVE, radio=8))
    p.append(teclado(540, 387, "uv python install", SUAVE, 14))
    p.append(texto(540, 424, "el intérprete también lo pone uv", SUAVE, 12.5))
    p.append(flecha(684, 382, 790, 296, SUAVE, 1.8))

    # Correr.
    p.append(flecha(900, 296, 900, 356, ACENTO, 2.5))
    p.append(chip(800, 326, "uv run hola.py", ACENTO, tam=13))
    p.append(caja(820, 360, 160, 44, FONDO, ACENTO, radio=8))
    p.append(texto(900, 388, "tu programa", ACENTO, 15, peso="600"))

    # Que va a git.
    p.append(caja(40, 462, 1000, 70, TINTE, LINEA, radio=10))
    p.append(texto(60, 492, "a git:", TEXTO, 15, anclaje="start", peso="600"))
    p.append(teclado(130, 492, "✓ pyproject.toml   ✓ uv.lock", ACENTO, 15, anclaje="start"))
    p.append(teclado(470, 492, "✗ .venv/", ROJO, 15, anclaje="start"))
    p.append(texto(560, 492, "no va a git: se borra y se recrea con uv sync", ROJO, 14, anclaje="start"))
    p.append(texto(60, 518, "Los dos archivos bastan para que otra máquina tenga exactamente tus versiones.", SUAVE, 13, anclaje="start"))
    p.append(cierre())
    return "".join(p)


def py_choque():
    """Dos proyectos, un solo site-packages: el ultimo que instala gana."""
    ancho, alto = 1080, 400
    aria = (
        "Dos columnas. A la izquierda, sin ambientes: proyecto-a pide pandas "
        "1.5 y proyecto-b pide pandas 2.2, y los dos apuntan al unico "
        "site-packages del Python del sistema, donde solo cabe una version, la "
        "2.2; la flecha de proyecto-a termina en rojo porque esperaba 1.5. A la "
        "derecha, con un .venv por proyecto: cada proyecto tiene su propio "
        "site-packages con su version, y las dos flechas terminan en verde"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Dos proyectos, un solo Python", TEXTO, 21, peso="600"))
    p.append(texto(270, 86, "sin ambientes", ROJO, 16, peso="600"))
    p.append(texto(810, 86, "con un .venv/ por proyecto", ACENTO, 16, peso="600"))
    p.append(f'<line x1="540" y1="70" x2="540" y2="380" stroke="{LINEA}" stroke-width="1.5" stroke-dasharray="6 6"/>')

    # Izquierda.
    for y, nombre, pide in ((110, "proyecto-a", "pide pandas==1.5"), (200, "proyecto-b", "pide pandas==2.2")):
        p.append(caja(40, y, 190, 64, PANEL, LINEA))
        p.append(teclado(135, y + 28, nombre, TEXTO, 15))
        p.append(texto(135, y + 50, pide, SUAVE, 12.5))
    p.append(caja(300, 120, 210, 150, PANEL, AMBAR))
    p.append(texto(405, 146, "Python del sistema", AMBAR, 14, peso="600"))
    p.append(teclado(405, 176, "site-packages/", SUAVE, 14, peso="normal"))
    p.append(caja(325, 196, 160, 46, FONDO, ROJO, radio=8))
    p.append(teclado(405, 225, "pandas 2.2", ROJO, 15))
    p.append(flecha(234, 142, 320, 210, ROJO, 2.2))
    p.append(flecha(234, 232, 320, 226, ACENTO, 2.2))
    p.append(texto(270, 320, "una sola ranura: el último que instala gana", ROJO, 14))
    p.append(texto(270, 346, "proyecto-a truena sin que nadie tocara su código", SUAVE, 13))

    # Derecha.
    for y, nombre, version in ((110, "proyecto-a", "pandas 1.5"), (230, "proyecto-b", "pandas 2.2")):
        p.append(caja(580, y, 190, 90, PANEL, LINEA))
        p.append(teclado(675, y + 38, nombre, TEXTO, 15))
        p.append(texto(675, y + 62, f"pide pandas=={version.split()[1]}", SUAVE, 12.5))
        p.append(caja(800, y, 230, 90, PANEL, ACENTO))
        p.append(teclado(915, y + 30, ".venv/site-packages/", SUAVE, 13, peso="normal"))
        p.append(teclado(915, y + 62, version, ACENTO, 15))
        p.append(flecha(774, y + 45, 794, y + 45, ACENTO, 2.2))
    p.append(texto(810, 360, "cada proyecto con sus versiones, sin tocarse", ACENTO, 14))
    p.append(cierre())
    return "".join(p)


def py_path():
    """Que python gana: la shell busca en el PATH, en orden."""
    ancho, alto = 1080, 480
    aria = (
        "Dos columnas con las carpetas del PATH en el orden en que la shell "
        "las recorre buscando python. Sin activar: /usr/local/bin, /usr/bin y "
        "/bin; el python3 de /usr/bin gana. Despues de source .venv/bin/activate: "
        "la carpeta .venv/bin del proyecto queda primero y su python gana, "
        "antes que /usr/local/bin y /usr/bin. Al pie: activate no instala nada, "
        "solo pone .venv/bin al frente del PATH, y uv run no necesita activar"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué python gana: la shell busca en orden", TEXTO, 21, peso="600"))
    p.append(texto(270, 90, "sin activar", SUAVE, 16, peso="600"))
    p.append(teclado(810, 90, "source .venv/bin/activate", ACENTO, 15))

    izquierda = (("/usr/local/bin", "no hay python", SUAVE, LINEA),
                 ("/usr/bin", "aquí está python3 → gana", AMBAR, AMBAR),
                 ("/bin", "ya no se busca", SUAVE, LINEA))
    derecha = (("…/09_python/ambientes/demo/.venv/bin", "aquí está python → gana", ACENTO, ACENTO),
               ("/usr/local/bin", "ya no se busca", SUAVE, LINEA),
               ("/usr/bin", "ya no se busca", SUAVE, LINEA))
    for x0, filas in ((50, izquierda), (590, derecha)):
        for i, (carpeta, nota, color, borde) in enumerate(filas):
            y = 116 + i * 82
            p.append(caja(x0, y, 440, 64, PANEL, borde))
            p.append(texto(x0 + 26, y + 39, str(i + 1), SUAVE, 16, peso="600"))
            p.append(teclado(x0 + 50, y + 30, carpeta, color, 15, anclaje="start"))
            p.append(texto(x0 + 50, y + 52, nota, color if borde != LINEA else SUAVE, 12.5, anclaje="start"))
            if i < 2:
                p.append(flecha(x0 + 26, y + 66, x0 + 26, y + 80, LINEA, 1.5))
    p.append(texto(ancho / 2, 400, "activate no instala nada: sólo pone .venv/bin al frente del PATH", TEXTO, 15))
    p.append(texto(ancho / 2, 430, "uv run no necesita activar: usa el .venv del proyecto directamente", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def py_venv_arbol():
    """Un ambiente es una carpeta: el arbol de .venv/ y que es cada cosa."""
    ancho, alto = 1080, 460
    aria = (
        "El arbol de la carpeta .venv a la izquierda y, a la derecha de cada "
        "rama, que es: bin/python es el interprete, un enlace al Python base; "
        "bin/activate es lo que corre source; lib/python3.13/site-packages "
        "guarda los paquetes de este ambiente y de ningun otro, como rich y "
        "pygments; pyvenv.cfg dice de que Python salio y su version. Al pie: "
        "borrar el ambiente es borrar la carpeta"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Un ambiente es una carpeta", TEXTO, 21, peso="600"))
    p.append(caja(40, 76, 1000, 300, PANEL, LINEA))
    ramas = (
        (".venv/", "", ACENTO),
        ("├── bin/", "los programas del ambiente", TEXTO),
        ("│   ├── python", "el intérprete: un enlace al Python base", CIAN),
        ("│   └── activate", "lo que corre source (sólo cambia el PATH)", CIAN),
        ("├── lib/python3.13/site-packages/", "los paquetes de este ambiente y de ningún otro", AMBAR),
        ("│   └── rich/  pygments/  …", "lo que instaló uv add", AMBAR),
        ("└── pyvenv.cfg", "de qué Python salió y su versión", VIOLETA),
    )
    for i, (rama, nota, color) in enumerate(ramas):
        y = 116 + i * 38
        p.append(teclado(70, y, rama, color, 16, anclaje="start", peso="600" if i == 0 else "normal"))
        if nota:
            p.append(texto(560, y, nota, SUAVE, 14, anclaje="start"))
    p.append(texto(ancho / 2, 414, "borrar el ambiente = borrar la carpeta: rm -rf .venv", TEXTO, 15))
    p.append(texto(ancho / 2, 440, "nada fuera de .venv/ cambia; uv sync la vuelve a crear", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


HERRAMIENTAS = (
    # nombre, (instalar, aislar, proyecto+lock, versiones Py, CLIs); 2 = a medias
    ("pip", (1, 0, 0, 0, 0)),
    ("venv", (0, 1, 0, 0, 0)),
    ("pip-tools", (0, 0, 2, 0, 0)),
    ("pipenv", (1, 1, 1, 0, 0)),
    ("poetry", (1, 1, 1, 0, 0)),
    ("pdm", (1, 1, 1, 1, 0)),
    ("hatch", (1, 1, 1, 1, 0)),
    ("conda", (1, 1, 2, 1, 0)),
    ("pixi", (1, 1, 1, 1, 1)),
    ("pyenv", (0, 0, 0, 1, 0)),
    ("pipx", (1, 1, 0, 0, 1)),
    ("uv", (1, 1, 1, 1, 1)),
)
TRABAJOS = ("instalar paquetes", "aislar", "proyecto + lock",
            "versiones de Python", "herramientas de terminal")


def py_trabajos():
    """Matriz: que trabajos hace cada herramienta."""
    ancho, alto = 1080, 640
    aria = (
        "Matriz de herramientas contra cinco trabajos: instalar paquetes, "
        "aislar, proyecto + lock, versiones de Python y herramientas de "
        "terminal. pip solo instala; venv solo aisla; pip-tools solo fija "
        "versiones; pipenv y poetry instalan, aislan y manejan proyecto con "
        "lock; pdm y hatch ademas instalan versiones de Python; conda hace "
        "casi todo y su lock es a medias; pixi y uv hacen los cinco; pyenv solo "
        "versiones de Python; pipx instala herramientas de terminal aisladas. "
        "La fila de uv esta resaltada. Al pie: conda y pixi instalan ademas "
        "paquetes que no son de Python"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Cinco trabajos, doce herramientas", TEXTO, 21, peso="600"))
    x0, y0, col, fila = 200, 110, 172, 38
    for j, trabajo in enumerate(TRABAJOS):
        cx = x0 + j * col + col / 2
        palabras = trabajo.split(" ", 1) if len(trabajo) > 14 else [trabajo]
        for k, w in enumerate(palabras):
            p.append(texto(cx, y0 - 22 + k * 17 - (8 if len(palabras) > 1 else 0), w, SUAVE, 13.5, peso="600"))
    for i, (nombre, hace) in enumerate(HERRAMIENTAS):
        y = y0 + i * fila
        if nombre == "uv":
            p.append(caja(40, y - 2, 1000, fila - 2, TINTE, ACENTO, radio=6, grosor=1.5))
        p.append(teclado(60, y + 22, nombre, ACENTO if nombre == "uv" else TEXTO, 15, anclaje="start"))
        for j, v in enumerate(hace):
            cx = x0 + j * col + col / 2
            if v == 1:
                p.append(f'<circle cx="{cx}" cy="{y + 17}" r="8" fill="{ACENTO}"/>')
            elif v == 2:
                p.append(f'<circle cx="{cx}" cy="{y + 17}" r="8" fill="none" stroke="{AMBAR}" stroke-width="2"/>')
            else:
                p.append(f'<circle cx="{cx}" cy="{y + 17}" r="3" fill="{LINEA}"/>')
    yp = y0 + len(HERRAMIENTAS) * fila + 24
    p.append(f'<circle cx="60" cy="{yp - 5}" r="7" fill="{ACENTO}"/>')
    p.append(texto(74, yp, "lo hace", SUAVE, 13, anclaje="start"))
    p.append(f'<circle cx="160" cy="{yp - 5}" r="7" fill="none" stroke="{AMBAR}" stroke-width="2"/>')
    p.append(texto(174, yp, "a medias", SUAVE, 13, anclaje="start"))
    p.append(texto(280, yp, "conda y pixi instalan además paquetes que no son de Python (CUDA, GDAL); uv no.", SUAVE, 13, anclaje="start"))
    p.append(cierre())
    return "".join(p)


def py_cual_uso():
    """Arbol de decision: que herramienta usar."""
    ancho, alto = 1080, 470
    aria = (
        "Arbol de decision de tres preguntas. Necesitas paquetes que no son de "
        "Python, como CUDA o GDAL? Si: pixi, o conda. No: el proyecto ya usa "
        "poetry, pdm o hatch? Si: usa esa y lee su pyproject.toml. No: es un "
        "script suelto? Si: uv run script.py con sus dependencias dentro, PEP "
        "723. No: uv init y uv add, que es el caso de este curso"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "¿Cuál uso?", TEXTO, 21, peso="600"))
    preguntas = (
        "¿Necesitas paquetes que no son de Python (CUDA, GDAL)?",
        "¿El proyecto ya usa poetry, pdm o hatch?",
        "¿Es un script suelto, de un solo archivo?",
    )
    respuestas = ("pixi (o conda)", "usa esa: lee su pyproject.toml", "uv run script.py (PEP 723)")
    for i, (preg, resp) in enumerate(zip(preguntas, respuestas)):
        y = 84 + i * 110
        p.append(caja(40, y, 560, 60, PANEL, CIAN))
        p.append(texto(320, y + 36, preg, TEXTO, 15))
        p.append(flecha(604, y + 30, 690, y + 30, AMBAR, 2.2))
        p.append(chip(647, y + 10, "sí", AMBAR, tam=13))
        p.append(caja(694, y + 8, 346, 44, FONDO, AMBAR, radio=8))
        p.append(teclado(867, y + 36, resp, AMBAR, 14))
        p.append(flecha(320, y + 64, 320, y + 104, SUAVE, 2))
        p.append(chip(356, y + 84, "no", SUAVE, tam=13))
    p.append(caja(170, 414, 300, 44, TINTE, ACENTO, radio=8, grosor=2.5))
    p.append(teclado(320, 442, "uv init + uv add", ACENTO, 16))
    p.append(texto(500, 442, "← el caso de este curso", ACENTO, 14, anclaje="start"))
    p.append(cierre())
    return "".join(p)


def py_aislamiento():
    """Que capa aisla cada herramienta."""
    ancho, alto = 1080, 480
    aria = (
        "Cuatro capas apiladas de abajo hacia arriba: kernel, librerias y "
        "programas del sistema, interprete de Python y paquetes de Python. A "
        "la derecha, tres barras verticales muestran que cubre cada "
        "herramienta: el .venv de uv cubre los paquetes y el interprete si uv "
        "lo instalo; conda y pixi cubren paquetes, interprete y parte de las "
        "librerias del sistema; Docker cubre todo menos el kernel. Al pie: "
        "ninguno aisla el kernel, eso es una maquina virtual"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué capa aísla cada uno", TEXTO, 21, peso="600"))
    capas = ("paquetes de Python", "intérprete de Python",
             "librerías y programas del sistema", "kernel")
    y0, h = 90, 70
    for i, c in enumerate(capas):
        y = y0 + i * (h + 8)
        p.append(caja(40, y, 420, h, PANEL, LINEA))
        p.append(texto(250, y + h / 2 + 6, c, TEXTO, 15))
    columnas = (
        (".venv (uv)", ACENTO, 0, 1.5),
        ("conda / pixi", CIAN, 0, 2.5),
        ("Docker", VIOLETA, 0, 3.0),
    )
    for k, (nombre, color, desde, hasta) in enumerate(columnas):
        x = 520 + k * 180
        p.append(texto(x + 60, y0 - 14, nombre, color, 14, peso="600"))
        top = y0 + desde * (h + 8)
        alto_barra = hasta * (h + 8) - 8
        p.append(f'<rect x="{x + 30}" y="{top}" width="60" height="{alto_barra}" rx="8" fill="{color}" fill-opacity="0.35" stroke="{color}" stroke-width="2"/>')
    p.append(texto(616, y0 + 1.5 * (h + 8) - 14, "el intérprete,", SUAVE, 11.5, anclaje="start"))
    p.append(texto(616, y0 + 1.5 * (h + 8) + 2, "si uv lo instaló", SUAVE, 11.5, anclaje="start"))
    p.append(texto(796, y0 + 2.5 * (h + 8) - 14, "sólo las que", SUAVE, 11.5, anclaje="start"))
    p.append(texto(796, y0 + 2.5 * (h + 8) + 2, "empaqueta", SUAVE, 11.5, anclaje="start"))
    p.append(texto(ancho / 2, 440, "Ninguno aísla el kernel: eso lo hace una máquina virtual.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


def py_uv_docker():
    """El orden del Dockerfile de la tarea, sin dar los comandos."""
    ancho, alto = 1080, 520
    aria = (
        "Las cinco etapas del Dockerfile de la entrega, apiladas en orden: una "
        "imagen base que ya trae Python; el binario de uv, copiado de su imagen "
        "oficial; los dos archivos que describen el ambiente; crear el ambiente "
        "desde el lock, sin dejar que cambie; y al final el programa. Una llave "
        "junto a la tercera y la cuarta dice que esa capa queda en cache y solo "
        "se rehace si cambia el lock; junto a la quinta, que cambia cada vez que "
        "editas el codigo. Abajo, en rojo: el .venv de tu maquina se queda "
        "fuera de la imagen"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "El ambiente primero, el código al final", TEXTO, 21, peso="600"))
    pasos = (
        ("1 · una imagen base que ya trae Python", SUAVE),
        ("2 · el binario de uv, de su imagen oficial", SUAVE),
        ("3 · los dos archivos que describen el ambiente", CIAN),
        ("4 · crear el ambiente desde el lock, sin dejar que cambie", CIAN),
        ("5 · el programa", AMBAR),
    )
    for i, (linea, color) in enumerate(pasos):
        y = 80 + i * 66
        p.append(caja(40, y, 640, 52, PANEL, color))
        p.append(texto(60, y + 32, linea, color, 15, anclaje="start"))
    p.append(f'<path d="M 700 214 Q 716 214 716 230 L 716 316 Q 716 332 700 332" fill="none" stroke="{CIAN}" stroke-width="2"/>')
    p.append(texto(732, 262, "capa en caché:", CIAN, 14, anclaje="start", peso="600"))
    p.append(texto(732, 284, "sólo se rehace si cambia el lock", CIAN, 13.5, anclaje="start"))
    p.append(texto(700, 380, "← cambia cada vez que editas el código", AMBAR, 13.5, anclaje="start"))
    p.append(caja(40, 430, 1000, 56, FONDO, ROJO, radio=10))
    p.append(teclado(60, 464, ".venv/", ROJO, 15, anclaje="start"))
    p.append(texto(130, 464, "de tu máquina: nunca entra a la imagen", ROJO, 14, anclaje="start"))
    p.append(cierre())
    return "".join(p)

def py_interprete():
    """Que hace Python con tu script: compila a bytecode y lo corre en la VM."""
    ancho, alto = 1080, 340
    aria = (
        "Una fila de cuatro cajas unidas por flechas. tu_script.py pasa por el "
        "paso compila, que traduce a bytecode, y produce el bytecode; el "
        "bytecode entra a la maquina virtual, que produce el resultado. Bajo "
        "compila, una etiqueta ambar: errores de sintaxis, aqui, antes de que "
        "corra nada. Bajo la maquina virtual, una etiqueta roja: errores de "
        "tipo, aqui, al correr"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué hace Python con tu script", TEXTO, 21, peso="600"))
    for x, w, nombre, color in ((30, 180, "tu_script.py", TEXTO), (440, 180, "bytecode", CIAN), (850, 190, "resultado", ACENTO)):
        p.append(caja(x, 110, w, 70, PANEL, LINEA if color == TEXTO else color))
        p.append(teclado(x + w / 2, 153, nombre, color, 18))
    # Pasos (flechas con chip): compila y maquina virtual.
    p.append(flecha(214, 145, 436, 145, AMBAR, 2.5))
    p.append(chip(325, 118, "compila", AMBAR, tam=14))
    p.append(texto(325, 172, "traduce a bytecode", SUAVE, 12.5))
    p.append(flecha(624, 145, 846, 145, ROJO, 2.5))
    p.append(chip(735, 118, "máquina virtual", ROJO, tam=14))
    p.append(texto(735, 172, "ejecuta el bytecode", SUAVE, 12.5))
    # Donde ocurre cada familia de errores.
    p.append(flecha(325, 214, 325, 240, AMBAR, 1.8))
    p.append(chip(325, 262, "errores de sintaxis: aquí", AMBAR, tam=14))
    p.append(texto(325, 300, "antes de que corra una sola línea", SUAVE, 13))
    p.append(flecha(735, 214, 735, 240, ROJO, 1.8))
    p.append(chip(735, 262, "errores de tipo: aquí, al correr", ROJO, tam=14))
    p.append(texto(735, 300, "sólo si esa línea llega a ejecutarse", SUAVE, 13))
    p.append(cierre())
    return "".join(p)


def py_nombres():
    """Nombres y objetos: dos nombres un objeto; la copia de un nivel."""
    ancho, alto = 1080, 440
    aria = (
        "Dos paneles. Panel uno: los nombres a y b tienen cada uno una flecha a "
        "la misma caja con la lista 1, 2, 3, 4; el nombre c, creado con c = "
        "a.copy(), apunta a otra caja distinta con otra lista igual. Panel dos: "
        "los nombres datos y copia apuntan a dos diccionarios distintos, pero "
        "la llave ventas de los dos apunta a una sola caja con la lista 10, 20, "
        "30. Al pie: .copy() copia un nivel, lo de adentro se comparte"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Nombres y objetos", TEXTO, 21, peso="600"))
    p.append(f'<line x1="540" y1="66" x2="540" y2="370" stroke="{LINEA}" stroke-width="1.5" stroke-dasharray="6 6"/>')
    p.append(texto(270, 84, "dos nombres, un objeto", SUAVE, 15, peso="600"))
    p.append(texto(810, 84, "copia de un nivel", SUAVE, 15, peso="600"))

    # Panel 1.
    for y, nombre in ((120, "a"), (176, "b")):
        p.append(caja(40, y, 70, 40, FONDO, AMBAR, radio=8))
        p.append(teclado(75, y + 27, nombre, AMBAR, 17))
        p.append(flecha(114, y + 20, 296, 168, AMBAR, 2.2))
    p.append(caja(300, 138, 200, 56, PANEL, ACENTO))
    p.append(teclado(400, 173, "[1, 2, 3, 4]", ACENTO, 17))
    p.append(caja(40, 270, 70, 40, FONDO, CIAN, radio=8))
    p.append(teclado(75, 297, "c", CIAN, 17))
    p.append(flecha(114, 290, 296, 290, CIAN, 2.2))
    p.append(chip(205, 262, "c = a.copy()", CIAN, tam=13))
    p.append(caja(300, 262, 200, 56, PANEL, CIAN))
    p.append(teclado(400, 297, "[1, 2, 3, 4]", CIAN, 17))

    # Panel 2.
    p.append(caja(580, 120, 90, 40, FONDO, AMBAR, radio=8))
    p.append(teclado(625, 147, "datos", AMBAR, 16))
    p.append(caja(580, 250, 90, 40, FONDO, CIAN, radio=8))
    p.append(teclado(625, 277, "copia", CIAN, 16))
    p.append(flecha(674, 140, 716, 140, AMBAR, 2.2))
    p.append(flecha(674, 270, 716, 270, CIAN, 2.2))
    p.append(caja(720, 110, 150, 60, PANEL, AMBAR))
    p.append(teclado(795, 134, "dict", AMBAR, 13, peso="normal"))
    p.append(teclado(795, 156, '"ventas": •', AMBAR, 14))
    p.append(caja(720, 240, 150, 60, PANEL, CIAN))
    p.append(teclado(795, 264, "dict", CIAN, 13, peso="normal"))
    p.append(teclado(795, 286, '"ventas": •', CIAN, 14))
    p.append(flecha(870, 152, 918, 190, AMBAR, 2.2))
    p.append(flecha(870, 282, 918, 214, CIAN, 2.2))
    p.append(caja(900, 180, 150, 46, PANEL, ACENTO))
    p.append(teclado(975, 210, "[10, 20, 30]", ACENTO, 15))
    p.append(texto(975, 246, "una sola lista", ACENTO, 12.5))

    p.append(caja(40, 372, 1000, 50, TINTE, LINEA, radio=10))
    p.append(teclado(70, 403, ".copy()", ACENTO, 15, anclaje="start"))
    p.append(texto(150, 403, "copia un nivel: lo de adentro se comparte", TEXTO, 15, anclaje="start"))
    p.append(cierre())
    return "".join(p)


def py_gil():
    """Tres carriles en el tiempo: hilos con GIL, sin GIL, procesos."""
    ancho, alto = 1080, 480
    aria = (
        "Tres carriles horizontales a lo largo del tiempo. Cuatro hilos con "
        "GIL: los cuatro bloques de trabajo se turnan, uno despues de otro, "
        "nunca dos a la vez. Cuatro hilos sin GIL, en Python 3.14t: los cuatro "
        "bloques corren al mismo tiempo, uno encima del otro. Cuatro procesos: "
        "cuatro bloques simultaneos, cada proceso con su propio GIL"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "El mismo trabajo, tres maneras de repartirlo", TEXTO, 21, peso="600"))
    x0, x1 = 290, 1030
    colores = (CIAN, AMBAR, ACENTO, VIOLETA)
    carriles = (
        ("4 hilos con GIL", AMBAR, 96, "uno a la vez: se turnan"),
        ("4 hilos sin GIL (3.14t)", CIAN, 214, "los cuatro a la vez"),
        ("4 procesos", ACENTO, 332, "los cuatro a la vez, cada uno con su GIL"),
    )
    for k, (nombre, color, y, nota) in enumerate(carriles):
        p.append(caja(40, y, 1000, 100, PANEL, LINEA))
        p.append(texto(60, y + 44, nombre, color, 16, anclaje="start", peso="600"))
        p.append(texto(60, y + 70, nota, SUAVE, 12.5, anclaje="start"))
        if k == 0:
            w = (x1 - x0 - 20) / 4
            for i in range(4):
                bx = x0 + i * (w + 6)
                p.append(caja(bx, y + 30, w, 40, FONDO, colores[i], radio=6))
                p.append(texto(bx + w / 2, y + 56, f"hilo {i + 1}", colores[i], 14))
        else:
            for i in range(4):
                by = y + 8 + i * 22
                p.append(caja(x0 + 10, by, x1 - x0 - 30, 18, FONDO, colores[i], radio=4, grosor=1.6))
                p.append(texto(x0 + 20, by + 13, f"{'hilo' if k == 1 else 'proceso'} {i + 1}", colores[i], 11.5, anclaje="start"))
    p.append(flecha(x0, 458, x1, 458, SUAVE, 1.8))
    p.append(texto(x0 - 10, 463, "tiempo", SUAVE, 13, anclaje="end"))
    p.append(cierre())
    return "".join(p)


# Salida real de revisa_esto.py, abreviada; columnas de lineas (texto, resalte).
_SINTOMAS_COL1 = (
    "== centro ==", "Total con IVA: $503.82", "Clientes:", "  - Fátima López",
    "  - Gael Muñoz", "  - Beto Peña", "",
    "== norte ==", "Total con IVA: $325.12", "Clientes:", "  - Fátima López",
    "  - Gael Muñoz", "  - Beto Peña", "  - Ana Núñez",
)
_SINTOMAS_COL2 = (
    "== sur ==", "Total con IVA: $559.31", "Clientes:", "  - Fátima López",
    "  - Gael Muñoz", "  - Beto Peña", "  - Ana Núñez", "  - Dana Ibáñez",
    "  - Emilio Sáenz",
)
_SINTOMAS_COL3 = (
    "== Puntaje ==", "  Ana Núñez: 8999997", "  Beto Peña: 8999997",
    "  Dana Ibáñez: 8999996", "  …", "puntaje con hilos: 2.51 s",
    "puntaje sin hilos: 1.76 s", "", "== Conciliación ==",
    "Total con IVA:     $1,388.26", "Contabilidad:      $2,722.27",
    "La contabilidad NO cuadra",
)


def _marca(x, y, w, h, n, color=AMBAR, derecha=False):
    """Recuadro numerado sobre una zona de la salida."""
    return (
        caja(x, y, w, h, "none", color, radio=5, grosor=2)
        + f'<circle cx="{x + (w if derecha else 0)}" cy="{y}" r="11" fill="{FONDO}" stroke="{color}" stroke-width="2"/>'
        + texto(x + (w if derecha else 0), y + 5, str(n), color, 14, peso="600")
    )


def py_sintomas():
    """La salida de revisa_esto.py con cinco sintomas numerados."""
    ancho, alto = 1080, 470
    aria = (
        "La salida de revisa_esto.py en tres columnas de texto monoespaciado: "
        "los bloques centro, norte y sur con su total con IVA y su lista de "
        "clientes; el puntaje por cliente con los tiempos con hilos y sin "
        "hilos; y la conciliacion. Cinco recuadros numerados marcan lo que "
        "llama la atencion: uno, el bloque norte con su total; dos, las listas "
        "de clientes de norte y sur con clientes de otras regiones; tres, "
        "puntaje con hilos 2.51 s contra puntaje sin hilos 1.76 s; cuatro, el "
        "total de norte, 325.12; cinco, la linea La contabilidad NO cuadra"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Lo que imprime revisa_esto.py", TEXTO, 21, peso="600"))
    p.append(caja(30, 70, 1020, 340, PANEL, LINEA))
    yb, dy, cw = 106, 22, 7.8
    cols = ((50, _SINTOMAS_COL1), (385, _SINTOMAS_COL2), (720, _SINTOMAS_COL3))
    for x, lineas in cols:
        for i, s in enumerate(lineas):
            if s:
                titulo = s.startswith("==")
                p.append(teclado(x, yb + i * dy, s.replace(" ", "\u00a0"), TEXTO if titulo else SUAVE, 13,
                                 anclaje="start", peso="600" if titulo else "normal"))
    y = lambda i: yb + i * dy - 16
    # 1: bloque norte (encabezado y total).
    p.append(_marca(40, y(7) - 2, 226, 2 * dy + 4, 1))
    # 4: el numero de norte.
    p.append(_marca(50 + 15 * cw - 4, y(8), 7 * cw + 8, 22, 4, ROJO, derecha=True))
    # 2: clientes de norte y sur.
    p.append(_marca(40, y(10) - 2, 170, 4 * dy + 4, 2, CIAN))
    p.append(_marca(375, y(3) - 2, 170, 6 * dy + 4, 2, CIAN))
    # 3: tiempos.
    p.append(_marca(710, y(5) - 2, 220, 2 * dy + 4, 3, VIOLETA))
    # 5: no cuadra.
    p.append(_marca(710, y(11) - 2, 220, dy + 2, 5, ROJO))
    leyenda = (
        (1, AMBAR, "el bloque norte"),
        (2, CIAN, "las listas de clientes"),
        (3, VIOLETA, "los dos tiempos"),
        (4, ROJO, "un total"),
        (5, ROJO, "la última línea"),
    )
    for i, (n, color, s) in enumerate(leyenda):
        x = 50 + i * 200
        p.append(f'<circle cx="{x}" cy="440" r="11" fill="{FONDO}" stroke="{color}" stroke-width="2"/>')
        p.append(texto(x, 445, str(n), color, 14, peso="600"))
        p.append(texto(x + 20, 445, s, SUAVE, 13.5, anclaje="start"))
    p.append(cierre())
    return "".join(p)



def py_import():
    """Donde busca Python lo que importa el notebook: sys.path, en orden."""
    ancho, alto = 1080, 520
    aria = (
        "Arriba, la celda from trabajo import calcula. Debajo, dos columnas con "
        "las carpetas de sys.path en el orden en que Python las recorre buscando "
        "trabajo.py. Izquierda, el kernel corre en por_dentro: la libreria "
        "estandar no lo tiene, la carpeta de trabajo, que es por_dentro, si lo "
        "tiene y gana. Derecha, el kernel corre en la raiz del fork: ni la "
        "libreria estandar, ni la carpeta de trabajo, ni los paquetes del .venv "
        "lo tienen, y sale ModuleNotFoundError. Al pie: os.getcwd dice cual es "
        "la carpeta de trabajo, y un nombre sin ruta se busca ahi"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Dónde busca Python lo que importas", TEXTO, 21, peso="600"))
    p.append(caja(340, 64, 400, 44, PANEL, ACENTO, radio=8))
    p.append(teclado(540, 92, "from trabajo import calcula", ACENTO, 16))
    p.append(texto(270, 140, "kernel en por_dentro/", ACENTO, 16, peso="600"))
    p.append(texto(810, 140, "kernel en la raíz del fork", ROJO, 16, peso="600"))

    izquierda = (("librería estándar", "no está trabajo.py", SUAVE, LINEA),
                 ("carpeta de trabajo: por_dentro/", "aquí está trabajo.py → gana", ACENTO, ACENTO),
                 (".venv/…/site-packages", "ya no se busca", SUAVE, LINEA))
    derecha = (("librería estándar", "no está trabajo.py", SUAVE, LINEA),
               ("carpeta de trabajo: raíz del fork", "no está trabajo.py", SUAVE, LINEA),
               (".venv/…/site-packages", "tampoco → ModuleNotFoundError", ROJO, ROJO))
    for x0, filas in ((50, izquierda), (590, derecha)):
        for i, (carpeta, nota, color, borde) in enumerate(filas):
            y = 160 + i * 82
            p.append(caja(x0, y, 440, 64, PANEL, borde))
            p.append(texto(x0 + 26, y + 39, str(i + 1), SUAVE, 16, peso="600"))
            p.append(teclado(x0 + 50, y + 30, carpeta, color, 14, anclaje="start"))
            p.append(texto(x0 + 50, y + 52, nota, color if borde != LINEA else SUAVE, 12.5, anclaje="start"))
            if i < 2:
                p.append(flecha(x0 + 26, y + 66, x0 + 26, y + 80, LINEA, 1.5))
    p.append(texto(ancho / 2, 440, "os.getcwd() dice cuál es la carpeta de trabajo", TEXTO, 15))
    p.append(texto(ancho / 2, 470, "trabajo.py, revisa_esto.py y ventas.csv se buscan ahí: un nombre sin ruta es relativo a ella", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --- 9.3 Elegir el stack -------------------------------------------------


def _tablita(x, y, cols, filas, color, celda=10, hueco=3):
    """Una tabla en miniatura: cols x filas celdas, para mostrar cuanto se materializa."""
    return "".join(
        f'<rect x="{x + c * (celda + hueco)}" y="{y + f * (celda + hueco)}" '
        f'width="{celda}" height="{celda}" rx="2" fill="{color}" fill-opacity="0.55"/>'
        for f in range(filas) for c in range(cols)
    )


def py_stack_mapa():
    """Las cuatro capas del stack y lo viejo que escribe la IA en cada una."""
    ancho, alto = 1080, 420
    aria = (
        "Cuatro capas en fila unidas por flechas. Proyecto: uv, ruff y pytest, "
        "como se instala y se revisa. Contratos: tipos y Pydantic, quien revisa "
        "cada dato. Motor: Polars y DuckDB, donde se hace el trabajo. Formato: "
        "Parquet, como se guarda. Debajo de cada capa, en gris, lo viejo que "
        "suele escribir la IA en su lugar: pip y requirements.txt; sin tipos o "
        "Pydantic v1; pandas para todo; CSV o pickle"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "El stack en cuatro capas", TEXTO, 21, peso="600"))
    capas = (
        ("proyecto", "uv · ruff · pytest", "cómo se instala y se revisa", AMBAR,
         ("pip", "requirements.txt")),
        ("contratos", "tipos · Pydantic", "quién revisa cada dato", CIAN,
         ("sin tipos", "Pydantic v1")),
        ("motor", "Polars · DuckDB", "dónde se hace el trabajo", ACENTO,
         ("pandas para todo", "")),
        ("formato", "Parquet", "cómo se guarda", VIOLETA,
         ("CSV", "pickle")),
    )
    w, hueco = 220, 40
    for i, (capa, piezas, que, color, viejo) in enumerate(capas):
        x = 40 + i * (w + hueco)
        p.append(caja(x, 90, w, 140, PANEL, color))
        p.append(texto(x + w / 2, 122, capa, color, 16, peso="600"))
        p.append(teclado(x + w / 2, 166, piezas, color, 16))
        p.append(texto(x + w / 2, 206, que, SUAVE, 13))
        if i < len(capas) - 1:
            p.append(flecha(x + w + 4, 160, x + w + hueco - 4, 160, LINEA, 2.2))
        p.append(_punteada(x + 20, 296, w - 40, 70))
        for k, s in enumerate(v for v in viejo if v):
            dy = 336 if not viejo[1] else 324 + k * 24
            p.append(teclado(x + w / 2, dy, s, SUAVE, 13.5, peso="normal"))
    p.append(texto(40, 280, "lo viejo que suele escribir la IA en cada capa:", SUAVE, 13.5, anclaje="start"))
    p.append(texto(ancho / 2, 400, "Cada capa se elige midiendo, no por costumbre.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def py_stack_frontera():
    """Valida en la frontera, confia adentro."""
    ancho, alto = 1080, 460
    aria = (
        "Cuatro zonas de izquierda a derecha. Afuera: un CSV, una API y un "
        "formulario, datos en los que no confias. Una flecha entra a la "
        "frontera, donde Pydantic valida cada dato. Las filas validas pasan "
        "adentro, donde una dataclass o un TypedDict las lleva sin revisarlas "
        "de nuevo, y de ahi a tu codigo, que confia. Debajo de la frontera, una "
        "fila sucia con precio igual a abc sale rechazada con ValidationError "
        "y nunca entra"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Valida en la frontera, confía adentro", TEXTO, 21, peso="600"))
    # Afuera.
    p.append(texto(140, 92, "afuera: no confías", SUAVE, 14, peso="600"))
    for k, fuente in enumerate(("CSV", "API", "formulario")):
        y = 112 + k * 62
        p.append(caja(50, y, 180, 46, PANEL, LINEA, radio=8))
        p.append(teclado(140, y + 29, fuente, TEXTO, 15))
    p.append(flecha(234, 205, 300, 205, SUAVE, 2.2))
    # Frontera.
    p.append(caja(304, 100, 200, 210, TINTE, CIAN, grosor=2.5))
    p.append(texto(404, 92, "la frontera", CIAN, 14, peso="600"))
    p.append(teclado(404, 196, "Pydantic", CIAN, 18))
    p.append(texto(404, 222, "valida cada dato", TEXTO, 14))
    p.append(texto(404, 244, "una vez", SUAVE, 13))
    p.append(flecha(508, 205, 576, 205, ACENTO, 2.2))
    p.append(texto(542, 190, "válida", ACENTO, 12.5))
    # Adentro.
    p.append(texto(690, 92, "adentro: confías", ACENTO, 14, peso="600"))
    p.append(caja(580, 100, 220, 210, PANEL, ACENTO))
    p.append(teclado(690, 186, "dataclass", ACENTO, 17))
    p.append(teclado(690, 212, "TypedDict", ACENTO, 17))
    p.append(texto(690, 244, "no revisa de nuevo", SUAVE, 13))
    p.append(flecha(804, 205, 856, 205, ACENTO, 2.2))
    p.append(caja(860, 170, 180, 70, PANEL, LINEA))
    p.append(texto(950, 211, "tu código", TEXTO, 16, peso="600"))
    # Fila sucia.
    p.append(flecha(404, 314, 404, 362, ROJO, 2.2))
    p.append(caja(294, 366, 220, 46, FONDO, ROJO, radio=8))
    p.append(teclado(404, 395, "ValidationError", ROJO, 16))
    p.append(teclado(540, 386, 'precio = "abc"', ROJO, 14, anclaje="start", peso="normal"))
    p.append(texto(540, 408, "la fila sucia se rechaza aquí y nunca entra", SUAVE, 13, anclaje="start"))
    p.append(cierre())
    return "".join(p)


def py_stack_lazy():
    """Eager materializa cada paso; lazy arma un plan y empuja filtro y columnas a la lectura."""
    ancho, alto = 1080, 540
    aria = (
        "Dos columnas. Eager, a la izquierda: cuatro pasos en orden, leer todo "
        "con 5 columnas y N filas, filtrar cantidad mayor que 0, seleccionar 3 "
        "columnas y agrupar por tienda; junto a cada paso, la tabla que "
        "materializa en memoria, de mas grande a mas chica. Lazy, a la derecha: "
        "un plan donde nada corre todavia; el filtro y la seleccion de 3 "
        "columnas bajan a la lectura, pushdown, que lee solo esas columnas y "
        "esas filas; luego agrupar por tienda, y collect corre el plan una sola "
        "vez"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Eager hace cada paso; lazy arma un plan", TEXTO, 21, peso="600"))
    p.append(f'<line x1="540" y1="70" x2="540" y2="470" stroke="{LINEA}" stroke-width="1.5" stroke-dasharray="6 6"/>')
    p.append(texto(280, 84, "eager", AMBAR, 16, peso="600"))
    p.append(texto(800, 84, "lazy", ACENTO, 16, peso="600"))

    pasos = (
        ("1 · leer todo: 5 columnas, N filas", 5, 4),
        ("2 · filtrar cantidad > 0", 5, 3),
        ("3 · seleccionar 3 columnas", 3, 3),
        ("4 · agrupar por tienda", 2, 1),
    )
    for i, (paso, cols, filas) in enumerate(pasos):
        y = 104 + i * 82
        p.append(caja(40, y, 480, 64, PANEL, AMBAR if i == 0 else LINEA))
        p.append(texto(60, y + 38, paso, TEXTO, 14.5, anclaje="start"))
        p.append(_tablita(430, y + 32 - (filas * 13 - 3) / 2, cols, filas, AMBAR))
        if i < len(pasos) - 1:
            p.append(flecha(280, y + 66, 280, y + 80, LINEA, 1.5))
    p.append(texto(280, 452, "cada paso crea una tabla entera en memoria", AMBAR, 14))

    # Lazy: el plan.
    p.append(_punteada(560, 96, 480, 280))
    p.append(texto(580, 120, "un plan: nada corre todavía", SUAVE, 13, anclaje="start"))
    p.append(caja(580, 134, 440, 64, PANEL, ACENTO))
    p.append(texto(600, 160, "leer sólo 3 columnas", TEXTO, 14.5, anclaje="start"))
    p.append(texto(600, 182, "y sólo las filas con cantidad > 0", TEXTO, 14.5, anclaje="start"))
    p.append(_tablita(950, 166 - (2 * 13 - 3) / 2, 3, 2, ACENTO))
    for x, s in ((700, "filtrar"), (870, "seleccionar")):
        p.append(_punteada(x, 246, 140, 40))
        p.append(texto(x + 70, 271, s, SUAVE, 13.5))
        p.append(flecha(x + 70, 244, x + 70, 202, ACENTO, 2))
    p.append(texto(855, 228, "pushdown", ACENTO, 13, peso="600"))
    p.append(flecha(620, 202, 620, 306, LINEA, 1.8))
    p.append(caja(580, 310, 440, 50, PANEL, LINEA))
    p.append(texto(600, 340, "agrupar por tienda", TEXTO, 14.5, anclaje="start"))
    p.append(_tablita(964, 330, 2, 1, ACENTO))
    p.append(flecha(800, 380, 800, 400, ACENTO, 2))
    p.append(caja(620, 404, 360, 50, TINTE, ACENTO, radio=8))
    p.append(teclado(800, 435, "collect(): corre una vez", ACENTO, 15))
    p.append(texto(ancho / 2, 506, "El motor ve el plan entero y lee menos: menos memoria y menos tiempo.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


def _columnas(x, y, w, h, color, nombres=("tienda", "cantidad", "precio")):
    """Un bloque de memoria guardado por columnas: una franja por columna."""
    p = [caja(x, y, w, h, PANEL, color)]
    franja = (w - 20 - 8 * (len(nombres) - 1)) / len(nombres)
    for k, n in enumerate(nombres):
        fx = x + 10 + k * (franja + 8)
        p.append(f'<rect x="{fx}" y="{y + 30}" width="{franja}" height="{h - 40}" rx="4" '
                 f'fill="{color}" fill-opacity="0.3" stroke="{color}" stroke-width="1.2"/>')
        p.append(texto(fx + franja / 2, y + 22, n, SUAVE, 11.5))
    return "".join(p)


def py_stack_arrow():
    """Compartir la memoria en columnas (Arrow) contra copiarla con to_pandas()."""
    ancho, alto = 1080, 440
    aria = (
        "Dos paneles. Compartir: Polars y DuckDB apuntan con una flecha cada "
        "uno al mismo bloque de memoria guardado por columnas, tienda, cantidad "
        "y precio, en formato Arrow; hay una sola copia. Copiar: un DataFrame "
        "de Polars pasa por to_pandas y aparece un segundo bloque, el DataFrame "
        "de pandas, con arreglos de NumPy por dentro; los datos quedan dos "
        "veces en memoria, y el camino de pandas de regreso tambien convierte"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Compartir la memoria o copiarla", TEXTO, 21, peso="600"))
    p.append(f'<line x1="540" y1="66" x2="540" y2="380" stroke="{LINEA}" stroke-width="1.5" stroke-dasharray="6 6"/>')
    p.append(texto(280, 84, "compartir", ACENTO, 16, peso="600"))
    p.append(texto(810, 84, "copiar", ROJO, 16, peso="600"))

    for cx, nombre in ((170, "Polars"), (390, "DuckDB")):
        p.append(caja(cx - 70, 104, 140, 42, PANEL, CIAN, radio=8))
        p.append(teclado(cx, 131, nombre, CIAN, 15))
        p.append(flecha(cx, 150, 280 + (cx - 280) * 0.6, 206, CIAN, 2))
    p.append(_columnas(90, 210, 380, 120, ACENTO))
    p.append(texto(280, 356, "memoria en columnas (Arrow): una sola copia", ACENTO, 14))

    p.append(texto(650, 150, "Polars", CIAN, 14, peso="600"))
    p.append(_columnas(570, 160, 160, 170, CIAN))
    p.append(flecha(736, 230, 864, 230, ROJO, 2.2))
    p.append(chip(800, 204, "to_pandas()", ROJO, ancho=116, tam=12))
    p.append(flecha(864, 270, 736, 270, ROJO, 2.2))
    p.append(chip(800, 296, "pl.from_pandas()", ROJO, ancho=124, tam=11))
    p.append(texto(950, 132, "pandas", ROJO, 14, peso="600"))
    p.append(texto(950, 150, "NumPy por dentro", SUAVE, 12))
    p.append(_columnas(870, 160, 160, 170, ROJO))
    p.append(texto(800, 356, "cada paso convierte: los datos, dos veces en memoria", ROJO, 14))
    p.append(texto(ancho / 2, 414, "Arrow es un formato de columnas en memoria: Polars y DuckDB lo leen sin convertir; pandas no.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def py_stack_generador():
    """Lista: todo en memoria a la vez. Generador: uno a la vez con yield."""
    ancho, alto = 1080, 450
    aria = (
        "Dos paneles con la memoria como una barra vertical sobre la misma "
        "linea base. Lista: los doce elementos del archivo se apilan en la "
        "barra, que queda alta, y despues van a sum; la memoria crece con el "
        "archivo. Generador: los elementos siguen en el archivo, yield entrega "
        "uno, la barra tiene un solo elemento y ese va a sum; la memoria queda "
        "fija"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Todo a la vez o uno a la vez", TEXTO, 21, peso="600"))
    p.append(f'<line x1="540" y1="66" x2="540" y2="430" stroke="{LINEA}" stroke-width="1.5" stroke-dasharray="6 6"/>')
    p.append(texto(280, 84, "lista", AMBAR, 16, peso="600"))
    p.append(texto(810, 84, "generador", ACENTO, 16, peso="600"))
    p.append(teclado(280, 112, "[float(p) for p in precios]", AMBAR, 14, peso="normal"))
    p.append(teclado(810, 112, "yield float(p)", ACENTO, 14, peso="normal"))

    base = 380
    for x0 in (40, 570):
        p.append(f'<line x1="{x0 + 40}" y1="{base + 2}" x2="{x0 + 430}" y2="{base + 2}" stroke="{SUAVE}" stroke-width="1.5"/>')
        p.append(texto(x0 + 430, base + 20, "memoria", SUAVE, 12, anclaje="end"))
    # Lista: doce celdas apiladas.
    for k in range(12):
        p.append(caja(160, base - 20 * (k + 1), 120, 18, AMBAR, AMBAR, radio=3, grosor=1))
    p.append(flecha(284, 360, 356, 360, AMBAR, 2.2))
    p.append(caja(360, 340, 130, 40, PANEL, AMBAR, radio=8))
    p.append(teclado(425, 366, "sum()", AMBAR, 15))
    p.append(texto(90, 230, "12 de 12", AMBAR, 13.5, anclaje="start"))
    p.append(texto(90, 248, "a la vez", AMBAR, 13.5, anclaje="start"))
    p.append(texto(280, 414, "la memoria crece con el archivo", AMBAR, 14))
    # Generador: pendientes punteados, yield, una celda.
    for k in range(6):
        p.append(f'<rect x="700" y="{150 + k * 20}" width="120" height="18" rx="3" fill="none" '
                 f'stroke="{SUAVE}" stroke-width="1.2" stroke-dasharray="4 3"/>')
    p.append(texto(690, 196, "aún en", SUAVE, 13, anclaje="end"))
    p.append(texto(690, 214, "el archivo", SUAVE, 13, anclaje="end"))
    p.append(flecha(760, 274, 760, 356, ACENTO, 2.2))
    p.append(chip(760, 316, "yield", ACENTO, tam=13))
    p.append(caja(700, base - 20, 120, 18, ACENTO, ACENTO, radio=3, grosor=1))
    p.append(flecha(824, 360, 886, 360, ACENTO, 2.2))
    p.append(caja(890, 340, 130, 40, PANEL, ACENTO, radio=8))
    p.append(teclado(955, 366, "sum()", ACENTO, 15))
    p.append(texto(810, 414, "uno a la vez: la memoria queda fija", ACENTO, 14))
    p.append(cierre())
    return "".join(p)

DIAGRAMAS = {
    "py-import": py_import,
    "py-mapa": py_mapa,
    "py-choque": py_choque,
    "py-path": py_path,
    "py-venv-arbol": py_venv_arbol,
    "py-trabajos": py_trabajos,
    "py-cual-uso": py_cual_uso,
    "py-aislamiento": py_aislamiento,
    "py-uv-docker": py_uv_docker,
    "py-interprete": py_interprete,
    "py-nombres": py_nombres,
    "py-gil": py_gil,
    "py-sintomas": py_sintomas,
    "py-stack-mapa": py_stack_mapa,
    "py-stack-frontera": py_stack_frontera,
    "py-stack-lazy": py_stack_lazy,
    "py-stack-arrow": py_stack_arrow,
    "py-stack-generador": py_stack_generador,
}


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
