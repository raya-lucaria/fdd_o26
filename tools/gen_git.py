"""Genera los diagramas SVG de la unidad de Git y GitHub.

Las primitivas y la paleta salen de tools/svg_base.py, compartido con
gen_regex.py: un solo lugar declara los colores de skins/fdd-eva.yaml.

Este archivo es la unica fuente de verdad de esos SVG. Editar un .svg a mano es
un error que tools/test_gen_git.py detecta.

Los ids llevan prefijo "git-" a proposito: los ids de objeto numerado de Raya
son unicos en TODO el curso, no por pagina.
"""
import sys
from pathlib import Path

from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, ROJO, SUAVE, TEXTO, TINTE,
    VIOLETA, arco, caja, chip, cierre, cima_arco, flecha, marco, teclado,
    texto,
)

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/7_git_y_github/_assets"


def git_llaves():
    """El par de llaves: una se queda en casa, la otra viaja."""
    ancho, alto = 1080, 500
    aria = (
        "A la izquierda, la carpeta punto ssh de tu computadora con dos "
        "archivos: la llave privada, que nunca sale de ahi, y la publica. A la "
        "derecha, GitHub. Una flecha lleva solo la llave publica hacia GitHub, "
        "y otra de vuelta representa la comprobacion con ssh -T"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Dos llaves: una se queda, la otra viaja", TEXTO, 21, peso="600"))

    # Tu computadora.
    p.append(caja(40, 96, 400, 236, PANEL, CIAN))
    p.append(texto(240, 128, "tu computadora", CIAN, 16, peso="600"))
    p.append(teclado(240, 154, "~/.ssh/", SUAVE, 14, peso="normal"))

    p.append(caja(66, 176, 348, 66, TINTE, AMBAR, radio=8))
    p.append(teclado(240, 204, "id_ed25519", AMBAR, 17))
    p.append(texto(240, 226, "la privada — nunca sale de aquí", AMBAR, 13))

    p.append(caja(66, 252, 348, 62, FONDO, ACENTO, radio=8))
    p.append(teclado(240, 279, "id_ed25519.pub", ACENTO, 17))
    p.append(texto(240, 301, "la pública — ésta sí se comparte", ACENTO, 13))

    # GitHub.
    p.append(caja(640, 96, 400, 236, PANEL, ACENTO))
    p.append(texto(840, 128, "GitHub", ACENTO, 16, peso="600"))
    p.append(texto(840, 152, "Settings → SSH and GPG keys", SUAVE, 13))
    p.append(caja(666, 190, 348, 62, FONDO, ACENTO, radio=8))
    p.append(teclado(840, 217, "id_ed25519.pub", ACENTO, 17))
    p.append(texto(840, 239, "pegada en tu cuenta", SUAVE, 13))
    p.append(texto(840, 292, "reconoce tu computadora", SUAVE, 13))
    p.append(texto(840, 312, "sin volver a pedirte nada", SUAVE, 13))

    # Solo la publica cruza.
    p.append(flecha(448, 200, 632, 200, ACENTO, 2.5))
    p.append(chip(540, 176, "copiar y pegar", ACENTO, tam=13))

    # El apreton de manos.
    p.append(arco(632, 288, 448, 288, 60, CIAN))
    p.append(chip(540, cima_arco(288, 60), "ssh -T", CIAN, tam=13))

    p.append(texto(ancho / 2, 412, "La privada se queda en tu disco y nunca se manda, ni por correo, ni por mensaje, ni en una captura de pantalla.", ROJO, 14))
    p.append(texto(ancho / 2, 442, "Si reseteas la computadora la pierdes, y eso está bien: se genera otra y se agrega. Una cuenta admite varias.", SUAVE, 14))
    p.append(texto(ancho / 2, 470, "El archivo que termina en .pub es el único que se copia a algún lado.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


def git_flujo():
    """De clonar a subir tu rama. Lo que pase despues llega mas adelante."""
    ancho, alto = 1080, 470
    aria = (
        "Cuatro pasos encadenados: clonar una vez, crear una rama, hacer "
        "commits y subir la rama. Debajo, la rama main aparece aparte y marcada "
        "como intocable porque publica el sitio, con una flecha roja que "
        "muestra que no se hace push directo a ella"
    )
    pasos = (
        ("git clone", "una sola vez", CIAN),
        ("git switch -c", "tu rama", ACENTO),
        ("git commit", "las veces que haga falta", ACENTO),
        ("git push", "tu rama queda en GitHub", ACENTO),
    )
    w, sep, y0, h = 224, 26, 118, 92
    x0 = (ancho - (len(pasos) * w + (len(pasos) - 1) * sep)) / 2
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Tu trabajo vive en tu rama", TEXTO, 21, peso="600"))

    centros = []
    for i, (titulo, glosa, color) in enumerate(pasos):
        x = x0 + i * (w + sep)
        p.append(caja(x, y0, w, h, PANEL, color))
        p.append(teclado(x + w / 2, y0 + 40, titulo, color, 15))
        p.append(texto(x + w / 2, y0 + 66, glosa, SUAVE, 12.5))
        centros.append(x + w / 2)
        if i:
            p.append(flecha(x - sep + 2, y0 + h / 2, x - 6, y0 + h / 2, SUAVE))

    # main queda aparte y sin flecha que llegue: nadie empuja ahi.
    ancho_main, x_main = 300, (ancho - 300) / 2
    p.append(caja(x_main, 300, ancho_main, 86, TINTE, AMBAR))
    p.append(teclado(x_main + ancho_main / 2, 334, "main", AMBAR, 18))
    p.append(texto(x_main + ancho_main / 2, 360, "publica el sitio — no la toques", AMBAR, 13))

    p.append(arco(centros[1], y0 + h + 6, x_main + ancho_main / 2, 296, 62, ROJO))
    p.append(chip((centros[1] + x_main + ancho_main / 2) / 2, cima_arco(230, 62), "push directo: no", ROJO, tam=13))

    p.append(texto(ancho / 2, 424, "Al terminar el push, tu rama ya está en GitHub y ahí se queda. Cómo se incorpora a main lo vemos más adelante.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)



DIAGRAMAS = {
    "git-llaves": git_llaves,
    "git-flujo": git_flujo,
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
