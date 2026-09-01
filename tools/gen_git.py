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
    """Este repositorio se lee, no se escribe: clone una vez, pull cada vez."""
    ancho, alto = 1080, 470
    aria = (
        "A la izquierda el repositorio del curso en GitHub; a la derecha tu "
        "copia local. Una flecha baja el codigo con git clone la primera vez y "
        "otra lo actualiza con git pull cada vez que hay algo nuevo. Una "
        "tercera flecha, en rojo y de vuelta hacia GitHub, aparece marcada como "
        "que no aplica: en este repositorio no escribes. Abajo, una caja "
        "punteada anuncia que el trabajo se hara sobre un fork propio, mas "
        "adelante"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Este repositorio lo lees; no escribes en él", TEXTO, 21, peso="600"))

    p.append(caja(56, 100, 384, 130, PANEL, ACENTO))
    p.append(texto(248, 134, "GitHub", ACENTO, 16, peso="600"))
    p.append(teclado(248, 164, "raya-lucaria/fdd_o26", ACENTO, 15))
    p.append(texto(248, 192, "el repositorio del curso", SUAVE, 13))
    p.append(texto(248, 212, "público: cualquiera puede leerlo", SUAVE, 13))

    p.append(caja(640, 100, 384, 130, PANEL, CIAN))
    p.append(texto(832, 134, "tu computadora", CIAN, 16, peso="600"))
    p.append(teclado(832, 164, "~/fdd/fdd_o26", CIAN, 15))
    p.append(texto(832, 192, "tu copia, para leer y consultar", SUAVE, 13))
    p.append(texto(832, 212, "y para correr lo que trae dentro", SUAVE, 13))

    # Lo que si se hace: bajar una vez y actualizar siempre. Cada flecha lleva
    # su chip arriba y su glosa abajo, para que no se lean cruzadas.
    p.append(flecha(448, 140, 632, 140, ACENTO, 2.5))
    p.append(chip(540, 118, "git clone", ACENTO, tam=13))
    p.append(texto(540, 162, "la primera vez", SUAVE, 12.5))

    p.append(flecha(448, 210, 632, 210, ACENTO, 2.5))
    p.append(chip(540, 188, "git pull", ACENTO, tam=13))
    p.append(texto(540, 232, "cada vez que haya algo nuevo", SUAVE, 12.5))

    # Lo que no: escribir de vuelta.
    p.append(arco(632, 268, 448, 268, 56, ROJO))
    p.append(chip(540, cima_arco(268, 56), "git push: no", ROJO, tam=13))
    p.append(texto(540, 344, "no tienes permiso de escritura, y no lo necesitas", ROJO, 13))

    # El futuro, sin entrar en detalle.
    p.append(f'<rect x="290" y="372" width="500" height="52" rx="10" fill="none" '
             f'stroke="{SUAVE}" stroke-width="1.6" stroke-dasharray="8 6"/>')
    p.append(texto(540, 396, "Cuando toque trabajar será sobre un fork tuyo,", SUAVE, 13.5))
    p.append(texto(540, 415, "una copia del repositorio en tu propia cuenta. Eso lo vemos en clase.", SUAVE, 13.5))
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
