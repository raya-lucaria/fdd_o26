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
    VIOLETA, arco, caja, chip, cierre, cima_arco, estado, flecha, marco,
    teclado, texto,
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



def git_linea_del_tiempo():
    """Treinta anos de control de versiones: local, centralizado, distribuido."""
    ancho, alto = 1080, 340
    aria = (
        "Seis sistemas de control de versiones en orden cronologico, de SCCS en "
        "1972 a Git en 2005, cada uno coloreado segun su modelo: ambar para los "
        "locales que trabajan un archivo a la vez, violeta para los "
        "centralizados que dependen de un servidor, y verde para los "
        "distribuidos donde cada copia es completa. Una flecha al pie marca el "
        "paso del tiempo"
    )
    sistemas = [
        ("1972", "SCCS", "local", AMBAR),
        ("1982", "RCS", "local", AMBAR),
        ("1986", "CVS", "centralizado", VIOLETA),
        ("2000", "Subversion", "centralizado", VIOLETA),
        ("2000", "BitKeeper", "distribuido", ACENTO),
        ("2005", "Git", "distribuido", ACENTO),
    ]
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Antes de Git: de un archivo a la vez a una copia completa por persona", TEXTO, 20, peso="600"))

    x = 40
    w, hueco = 156, 12
    for anio, nombre, modelo, color in sistemas:
        cx = x + w / 2
        p.append(caja(x, 86, w, 118, PANEL, color))
        p.append(texto(cx, 116, anio, SUAVE, 14))
        p.append(teclado(cx, 148, nombre, color, 18))
        p.append(texto(cx, 178, modelo, color, 13))
        x += w + hueco

    p.append(flecha(40, 236, 1040, 236, SUAVE, 2))
    p.append(texto(ancho / 2, 266, "El tiempo. Cada modelo aparece porque el anterior no daba: primero compartir, luego trabajar en paralelo, al final no depender de nadie.", SUAVE, 13.5))
    p.append(texto(ancho / 2, 296, "Mercurial nace el mismo mes que Git y por la misma razón. El kernel de Linux eligió Git.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def git_tres_zonas():
    """Las tres zonas de Git y los comandos que mueven cosas entre ellas."""
    ancho, alto = 1080, 540
    aria = (
        "Tres cajas en fila: el working directory donde editas, el staging area "
        "donde apartas lo que va a entrar, y el repositorio local donde queda "
        "guardado. Por arriba, dos arcos verdes avanzan con git add y git "
        "commit. Por abajo, dos arcos ambar regresan con git restore --staged y "
        "git reset. A la derecha, una caja punteada representa GitHub, todavia "
        "fuera de alcance porque nada de esto toca internet"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Las tres zonas: nada avanza solo", TEXTO, 21, peso="600"))

    zonas = [
        (40, CIAN, "working directory", "donde editas", "lo que ves con ls"),
        (400, AMBAR, "staging area", "lo que va a entrar", "el index"),
        (760, ACENTO, "repositorio local", "guardado para siempre", ".git/"),
    ]
    for x, color, titulo, glosa, extra in zonas:
        p.append(caja(x, 176, 280, 116, PANEL, color))
        p.append(texto(x + 140, 210, titulo, color, 17, peso="600"))
        p.append(texto(x + 140, 238, glosa, SUAVE, 13.5))
        p.append(teclado(x + 140, 266, extra, SUAVE, 13, peso="normal"))

    # Ida: arcos por encima de las cajas, donde no estorban.
    for x1, x2, etiqueta in ((250, 470, "git add"), (610, 830, "git commit")):
        p.append(arco(x1, 176, x2, 176, -62, ACENTO))
        p.append(chip((x1 + x2) / 2, cima_arco(176, -62), etiqueta, ACENTO, tam=13))

    # Vuelta: arcos por debajo.
    for x1, x2, etiqueta in ((470, 250, "restore --staged"), (830, 610, "reset")):
        p.append(arco(x1, 292, x2, 292, 62, AMBAR))
        p.append(chip((x1 + x2) / 2, cima_arco(292, 62), etiqueta, AMBAR, tam=12))

    p.append(caja(40, 396, 280, 68, FONDO, CIAN, radio=9, grosor=1.4))
    p.append(teclado(180, 422, "git restore <archivo>", CIAN, 13))
    p.append(texto(180, 446, "descarta aquí lo que editaste", SUAVE, 12.5))

    p.append(f'<rect x="760" y="396" width="280" height="68" rx="9" fill="none" '
             f'stroke="{SUAVE}" stroke-width="1.6" stroke-dasharray="8 6"/>')
    p.append(texto(900, 424, "GitHub", SUAVE, 15, peso="600"))
    p.append(texto(900, 448, "todavía no existe para ti", SUAVE, 12.5))

    p.append(texto(ancho / 2, 500, "Un commit no sube nada. Puedes hacer cien en un avión sin wifi: el repositorio completo está en tu disco.", SUAVE, 13.5))
    p.append(texto(ancho / 2, 524, "Nada de lo que hay en este diagrama toca internet.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def git_objetos():
    """Commit, tree y blob: el hash es la direccion del contenido."""
    ancho, alto = 1080, 470
    aria = (
        "Tres tipos de objeto encadenados. Un commit apunta a un tree y a su "
        "commit padre, y guarda autor, fecha y mensaje. El tree lista nombres de "
        "archivo y apunta a los blobs. Cada blob es el contenido de un archivo "
        "sin su nombre. Al pie se indica que el hash se calcula sobre el "
        "contenido, asi que dos archivos iguales son el mismo blob"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Un commit apunta a un árbol; el árbol apunta al contenido", TEXTO, 20, peso="600"))

    p.append(caja(40, 86, 292, 190, PANEL, VIOLETA))
    p.append(texto(186, 116, "commit", VIOLETA, 17, peso="600"))
    p.append(teclado(186, 146, "a1b2c3d", VIOLETA, 16))
    p.append(texto(186, 176, "tree:   9f8e7d6", SUAVE, 13))
    p.append(texto(186, 198, "parent: 4c5d6e7", SUAVE, 13))
    p.append(texto(186, 220, "autor y fecha", SUAVE, 13))
    p.append(texto(186, 242, '"agrego el ejemplo"', SUAVE, 13))
    p.append(texto(186, 264, "qué, quién, cuándo y de dónde viene", SUAVE, 12.5))

    p.append(caja(394, 86, 292, 190, PANEL, CIAN))
    p.append(texto(540, 116, "tree", CIAN, 17, peso="600"))
    p.append(teclado(540, 146, "9f8e7d6", CIAN, 16))
    p.append(texto(540, 180, "una carpeta: nombres y a qué apuntan", SUAVE, 12.5))
    p.append(texto(540, 210, "ejemplo.sh  →  1111aaa", SUAVE, 13))
    p.append(texto(540, 232, "notas.md    →  2222bbb", SUAVE, 13))
    p.append(texto(540, 262, "aquí viven los nombres", SUAVE, 12.5))

    p.append(caja(748, 86, 292, 88, PANEL, ACENTO))
    p.append(texto(894, 114, "blob", ACENTO, 17, peso="600"))
    p.append(teclado(894, 142, "1111aaa", ACENTO, 16))
    p.append(texto(894, 164, "el contenido, sin nombre", SUAVE, 12.5))

    p.append(caja(748, 188, 292, 88, PANEL, ACENTO))
    p.append(texto(894, 216, "blob", ACENTO, 17, peso="600"))
    p.append(teclado(894, 244, "2222bbb", ACENTO, 16))
    p.append(texto(894, 266, "el contenido, sin nombre", SUAVE, 12.5))

    p.append(flecha(340, 152, 386, 152, VIOLETA, 2.5))
    p.append(flecha(694, 130, 740, 130, CIAN, 2.5))
    p.append(flecha(694, 232, 740, 232, CIAN, 2.5))

    p.append(texto(ancho / 2, 336, "El hash no es un número de serie: se calcula sobre el contenido.", TEXTO, 15, peso="600"))
    p.append(texto(ancho / 2, 362, "Cambia una coma y cambia el hash. Dos archivos con el mismo contenido, aunque se llamen distinto", SUAVE, 13.5))
    p.append(texto(ancho / 2, 384, "y vivan en carpetas distintas, son el mismo blob guardado una sola vez.", SUAVE, 13.5))
    p.append(texto(ancho / 2, 420, "Fíjate en que el nombre del archivo vive en el tree, no en el blob.", AMBAR, 13.5))
    p.append(texto(ancho / 2, 442, "Por eso Git rastrea archivos y no carpetas: un tree vacío no existe.", AMBAR, 13.5))
    p.append(cierre())
    return "".join(p)


def git_lo_que_no_se_sube():
    """git add . barre lo que no miraste; una ruta con nombre no."""
    ancho, alto = 1080, 470
    aria = (
        "Dos columnas comparadas. A la izquierda, git add punto recoge todo lo "
        "que hay en el repositorio, incluida la basura del sistema operativo "
        "como punto DS Store, la carpeta pycache y un archivo punto env con "
        "credenciales. A la derecha, git add seguido de una ruta con nombre "
        "recoge unicamente lo que pediste"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "El mismo montón, dos maneras de recogerlo", TEXTO, 20, peso="600"))

    monton = [
        ("ejemplo.sh", ACENTO, "lo escribiste tú"),
        ("notas.md", ACENTO, "lo escribiste tú"),
        (".DS_Store", ROJO, "lo puso el Finder"),
        ("__pycache__/", ROJO, "lo puso Python"),
        (".env", ROJO, "tus credenciales"),
    ]

    p.append(caja(40, 78, 480, 340, PANEL, ROJO))
    p.append(teclado(280, 112, "git add .", ROJO, 19))
    p.append(texto(280, 136, "se lleva las cinco", ROJO, 13.5))
    y = 164
    for nombre, color, glosa in monton:
        p.append(caja(70, y, 420, 42, FONDO, color, radio=8, grosor=1.6))
        p.append(teclado(150, y + 27, nombre, color, 14, anclaje="middle"))
        p.append(texto(370, y + 26, glosa, SUAVE, 12.5))
        y += 50

    p.append(caja(560, 78, 480, 340, PANEL, ACENTO))
    p.append(teclado(800, 112, "git add ejemplo.sh notas.md", ACENTO, 15))
    p.append(texto(800, 136, "se lleva las dos que nombraste", ACENTO, 13.5))
    y = 164
    for nombre, color, glosa in monton:
        entra = color is ACENTO
        borde = ACENTO if entra else SUAVE
        p.append(caja(590, y, 420, 42, FONDO, borde, radio=8, grosor=1.6))
        p.append(teclado(670, y + 27, nombre, borde, 14, anclaje="middle"))
        p.append(texto(890, y + 26, "entra" if entra else "se queda fuera", borde, 12.5))
        y += 50

    p.append(texto(ancho / 2, 446, "La regla no es teclear más: es agregar una ruta que puedas nombrar y que acabes de ver en git status.", TEXTO, 14))
    p.append(cierre())
    return "".join(p)


def git_deshacer():
    """Que comando deshace depende de donde este el cambio, no de que quieras."""
    ancho, alto = 1080, 480
    aria = (
        "Un arbol de decision. La pregunta de arriba es donde esta el cambio que "
        "quieres deshacer, y de ella bajan cuatro ramas: en el working "
        "directory, en el staging area, en el ultimo commit sin compartir, y a "
        "medias cuando necesitas guardarlo para despues. Cada rama termina en su "
        "comando. Una franja al pie separa lo que reescribe la historia de lo "
        "que no"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "No preguntes qué comando quieres; pregunta dónde está el cambio", TEXTO, 20, peso="600"))

    p.append(caja(340, 70, 400, 54, TINTE, TEXTO, radio=10))
    p.append(texto(540, 104, "¿dónde está el cambio?", TEXTO, 17, peso="600"))

    ramas = [
        (40, CIAN, "en el working directory", "lo editaste y ya", "git restore <archivo>", "sólo si ya estaba rastreado"),
        (300, AMBAR, "en el staging area", "le hiciste add", "git restore --staged <archivo>", "lo saca, no lo borra"),
        (560, VIOLETA, "en el último commit", "y no lo has compartido", "git reset --soft HEAD~1", "--hard además tira tu trabajo"),
        (820, ACENTO, "a medias, y estorba", "quieres volver luego", "git stash / git stash pop", "revisa git stash list al final"),
    ]
    for x, color, cuando, glosa, comando, nota in ramas:
        cx = x + 110
        p.append(flecha(540, 130, cx, 176, color, 2))
        p.append(caja(x, 182, 220, 150, PANEL, color))
        p.append(texto(cx, 210, cuando, color, 14.5, peso="600"))
        p.append(texto(cx, 232, glosa, SUAVE, 12.5))
        p.append(caja(x + 12, 248, 196, 40, FONDO, color, radio=7, grosor=1.4))
        p.append(teclado(cx, 273, comando, color, 12))
        p.append(texto(cx, 312, nota, SUAVE, 12))

    p.append(caja(40, 366, 480, 82, FONDO, ACENTO, radio=10, grosor=1.6))
    p.append(texto(280, 396, "No reescribe la historia", ACENTO, 15, peso="600"))
    p.append(texto(280, 422, "restore, stash. Seguros siempre.", SUAVE, 13))

    p.append(caja(560, 366, 480, 82, FONDO, ROJO, radio=10, grosor=1.6))
    p.append(texto(800, 396, "Reescribe la historia", ROJO, 15, peso="600"))
    p.append(texto(800, 422, "reset. Barato en lo tuyo, caro en lo compartido.", SUAVE, 13))
    p.append(cierre())
    return "".join(p)


def git_branches():
    """Una branch es una etiqueta que apunta a un commit, no una copia."""
    ancho, alto = 1080, 560
    aria = (
        "Una cadena de commits con dos etiquetas. La linea de abajo es main con "
        "tres commits; de la segunda se desprende hacia arriba una branch de "
        "tarea con dos commits propios. Las etiquetas main y tarea son chips que "
        "apuntan al ultimo commit de cada linea, y HEAD marca en cual estas "
        "parado. Abajo, dos paneles comparan el merge fast-forward con el que "
        "crea un commit nuevo de dos padres"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Una branch no copia archivos: es una etiqueta que apunta a un commit", TEXTO, 20, peso="600"))

    y_main, y_rama = 236, 140
    xs_main = [120, 260, 400]
    xs_rama = [400, 540]

    for a, b in zip(xs_main, xs_main[1:]):
        p.append(flecha(a + 24, y_main, b - 24, y_main, LINEA, 2))
    p.append(flecha(278, y_main - 18, 382, y_rama + 16, LINEA, 2))
    p.append(flecha(xs_rama[0] + 24, y_rama, xs_rama[1] - 24, y_rama, LINEA, 2))

    for x in xs_main:
        p.append(estado(x, y_main, "", r=22, borde=SUAVE))
    for x in xs_rama:
        p.append(estado(x, y_rama, "", r=22, borde=VIOLETA))

    p.append(chip(400, y_main + 60, "main", ACENTO, tam=13))
    p.append(flecha(400, y_main + 44, 400, y_main + 26, ACENTO, 2))
    p.append(chip(540, y_rama - 60, "tarea-07-git", VIOLETA, tam=13))
    p.append(flecha(540, y_rama - 44, 540, y_rama - 26, VIOLETA, 2))
    p.append(chip(662, y_rama, "HEAD", AMBAR, tam=13))
    p.append(flecha(624, y_rama, 572, y_rama, AMBAR, 2))

    p.append(caja(720, 120, 320, 148, PANEL, SUAVE, radio=10, grosor=1.4))
    p.append(texto(880, 150, "Qué hay en el disco", TEXTO, 15, peso="600"))
    p.append(teclado(880, 180, ".git/refs/heads/main", SUAVE, 13, peso="normal"))
    p.append(texto(880, 204, "41 bytes: un hash y un salto de línea", SUAVE, 12))
    p.append(texto(880, 232, "Eso es toda la branch.", ACENTO, 13.5))
    p.append(texto(880, 254, "Por eso crearla es instantánea.", ACENTO, 13.5))

    p.append(caja(40, 340, 480, 190, PANEL, ACENTO))
    p.append(texto(280, 372, "merge fast-forward", ACENTO, 16, peso="600"))
    p.append(texto(280, 398, "nadie tocó main mientras trabajabas", SUAVE, 13))
    for k, x in enumerate((150, 250, 350)):
        p.append(estado(x, 448, "", r=17, borde=SUAVE if k < 2 else ACENTO))
    p.append(flecha(167, 448, 233, 448, LINEA, 1.8))
    p.append(flecha(267, 448, 333, 448, LINEA, 1.8))
    p.append(texto(280, 502, "la etiqueta main sólo se desliza hacia adelante", SUAVE, 12.5))

    p.append(caja(560, 340, 480, 190, PANEL, AMBAR))
    p.append(texto(800, 372, "merge con commit nuevo", AMBAR, 16, peso="600"))
    p.append(texto(800, 398, "las dos líneas avanzaron por separado", SUAVE, 13))
    p.append(estado(660, 448, "", r=17, borde=SUAVE))
    p.append(estado(770, 420, "", r=17, borde=VIOLETA))
    p.append(estado(770, 476, "", r=17, borde=SUAVE))
    p.append(estado(890, 448, "", r=17, borde=AMBAR))
    p.append(flecha(674, 440, 754, 425, LINEA, 1.8))
    p.append(flecha(674, 456, 754, 471, LINEA, 1.8))
    p.append(flecha(786, 425, 876, 440, LINEA, 1.8))
    p.append(flecha(786, 471, 876, 456, LINEA, 1.8))
    p.append(texto(800, 512, "nace un commit con dos padres", SUAVE, 12.5))
    p.append(cierre())
    return "".join(p)


def git_conflicto():
    """Como se lee un conflicto: que mitad es tuya y que mitad viene de fuera."""
    ancho, alto = 1080, 470
    aria = (
        "El contenido de un archivo en conflicto, con sus tres marcadores. Entre "
        "el primero y la linea de iguales esta la version de la branch en la que "
        "estas parado; entre la linea de iguales y el ultimo marcador esta la "
        "version que trae la otra branch. Etiquetas laterales identifican cada "
        "mitad, y al pie estan los pasos para resolver y la salida de emergencia"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Un conflicto no es un error: es Git preguntándote cuál de las dos quieres", TEXTO, 20, peso="600"))

    p.append(caja(40, 76, 600, 250, PANEL, SUAVE, radio=10, grosor=1.4))
    lineas = [
        ('saludo = "hola"', SUAVE),
        ("<<<<<<< HEAD", AMBAR),
        ('mensaje = "buenos días"', AMBAR),
        ("=======", TEXTO),
        ('mensaje = "qué tal"', VIOLETA),
        (">>>>>>> otra-branch", VIOLETA),
        ('despedida = "adiós"', SUAVE),
    ]
    y = 112
    for linea, color in lineas:
        p.append(teclado(64, y, linea, color, 15, anclaje="start", peso="normal"))
        y += 32

    p.append(caja(760, 106, 280, 76, FONDO, AMBAR, radio=9, grosor=1.4))
    p.append(texto(900, 134, "lo que ya tenías", AMBAR, 14.5, peso="600"))
    p.append(texto(900, 158, "la branch donde estás parado", SUAVE, 12.5))
    p.append(flecha(752, 144, 652, 144, AMBAR, 2))

    p.append(caja(760, 222, 280, 76, FONDO, VIOLETA, radio=9, grosor=1.4))
    p.append(texto(900, 250, "lo que trae la otra", VIOLETA, 14.5, peso="600"))
    p.append(texto(900, 274, "la branch que estás mergeando", SUAVE, 12.5))
    p.append(flecha(752, 260, 652, 260, VIOLETA, 2))

    p.append(texto(ancho / 2, 366, "Se resuelve a mano: borra los tres marcadores y deja el archivo como lo quieres.", TEXTO, 15, peso="600"))
    p.append(texto(ancho / 2, 394, "Puede quedarse una mitad, la otra, o algo nuevo. Después git add al archivo, que es como le dices a Git que ya, y git commit.", SUAVE, 13.5))
    p.append(texto(ancho / 2, 430, "¿Se complicó? git merge --abort deja todo como estaba antes de empezar. Nunca es tarde para eso.", ACENTO, 14))
    p.append(cierre())
    return "".join(p)


def git_tres_repos():
    """upstream, origin y tu disco: quien manda a quien y con que comando."""
    ancho, alto = 1080, 560
    aria = (
        "Tres repositorios y las flechas entre ellos. Arriba a la izquierda el "
        "del curso, llamado upstream, que solo se lee. Arriba a la derecha tu "
        "fork en tu cuenta, llamado origin, donde si escribes. Abajo al centro "
        "tu copia en el disco. Una flecha baja lo nuevo del curso con git fetch "
        "upstream, otra sube tu trabajo con git push origin, y una tercera "
        "punteada va de tu fork al curso: el pull request, que es un boton y no "
        "un comando"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Tres repositorios, y sólo en dos puedes escribir", TEXTO, 21, peso="600"))

    p.append(caja(60, 86, 400, 128, PANEL, ROJO))
    p.append(teclado(260, 122, "upstream", ROJO, 19))
    p.append(texto(260, 150, "raya-lucaria/fdd_o26", SUAVE, 13.5))
    p.append(texto(260, 174, "el repositorio del curso", SUAVE, 13))
    p.append(texto(260, 196, "sólo lectura: aquí no escribes nunca", ROJO, 13))

    p.append(caja(620, 86, 400, 128, PANEL, ACENTO))
    p.append(teclado(820, 122, "origin", ACENTO, 19))
    p.append(texto(820, 150, "tu-login/fdd_o26", SUAVE, 13.5))
    p.append(texto(820, 174, "tu fork, en tu propia cuenta", SUAVE, 13))
    p.append(texto(820, 196, "aquí sí escribes", ACENTO, 13))

    p.append(caja(340, 330, 400, 128, PANEL, CIAN))
    p.append(teclado(540, 366, "tu disco", CIAN, 19))
    p.append(texto(540, 394, "~/fdd/fdd_o26", SUAVE, 13.5))
    p.append(texto(540, 418, "donde de verdad trabajas", SUAVE, 13))
    p.append(texto(540, 440, "commits, branches, todo lo de la clase 1", CIAN, 12.5))

    p.append(flecha(214, 220, 420, 322, ROJO, 2.5))
    p.append(chip(268, 268, "git fetch upstream", ROJO, tam=12))

    p.append(flecha(668, 322, 862, 220, ACENTO, 2.5))
    p.append(chip(800, 274, "git push origin", ACENTO, tam=12))

    p.append(f'<path d="M 612 118 L 476 118" fill="none" stroke="{VIOLETA}" '
             f'stroke-width="2.5" stroke-dasharray="9 6" marker-end="url(#f' + VIOLETA.lstrip("#") + ')"/>')
    p.append(chip(544, 92, "pull request", VIOLETA, tam=12))
    p.append(texto(544, 148, "un botón, no un comando", VIOLETA, 12.5))

    p.append(texto(ancho / 2, 500, "El fork se hace una sola vez, desde el navegador. Después tu disco habla con los dos: baja del curso, sube a tu fork.", SUAVE, 13.5))
    p.append(texto(ancho / 2, 526, "Ojo: al clonar quedaste apuntando al repositorio del curso. Hay que renombrar ese remote antes de que nada de esto funcione.", AMBAR, 13.5))
    p.append(cierre())
    return "".join(p)


def git_race():
    """Tres escenarios cuando dos personas tocan el mismo repositorio."""
    ancho, alto = 1080, 460
    aria = (
        "Tres columnas con tres escenarios. En el primero cada persona toca un "
        "archivo distinto y todo funciona. En el segundo tocan el mismo archivo "
        "pero en lineas separadas y tambien funciona, porque Git compara por "
        "bloques. En el tercero tocan la misma linea y hay conflicto: el primer "
        "push entra y el segundo es rechazado"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Dos personas, un repositorio: qué pasa según qué toquen", TEXTO, 20, peso="600"))

    casos = [
        (40, ACENTO, "A", "archivos distintos",
         ["ana  toca  main.py", "beto toca  app.py"],
         "Funciona.", ["Git junta los dos cambios", "sin preguntarte nada."]),
        (373, ACENTO, "B", "mismo archivo, lejos",
         ["ana  toca  línea 3", "beto toca  línea 60"],
         "También funciona.", ["Git compara por bloques con", "contexto, no línea por línea."]),
        (706, ROJO, "C", "misma línea",
         ["ana  toca  línea 12", "beto toca  línea 12"],
         "Conflicto.", ["Gana quien pushea primero;", "el segundo es rechazado."]),
    ]
    for x, color, letra, titulo, toques, veredicto, glosa in casos:
        cx = x + 167
        p.append(caja(x, 80, 334, 316, PANEL, color))
        p.append(estado(cx, 116, letra, r=22, borde=color, color_texto=color))
        p.append(texto(cx, 166, titulo, color, 16, peso="600"))
        y = 202
        for linea in toques:
            p.append(caja(x + 26, y, 282, 36, FONDO, SUAVE, radio=7, grosor=1.2))
            p.append(teclado(cx, y + 24, linea, SUAVE, 13, peso="normal"))
            y += 44
        p.append(texto(cx, y + 32, veredicto, color, 17, peso="600"))
        for k, linea in enumerate(glosa):
            p.append(texto(cx, y + 60 + k * 20, linea, SUAVE, 12.5))

    p.append(texto(ancho / 2, 430, "El rechazo no es un castigo: Git se niega a tirar trabajo que todavía no ha visto. La salida es git pull, resolver, y volver a pushear.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def git_el_mirror():
    """Tu carpeta es un espejo de codigo: misma ruta, mismo nombre."""
    ancho, alto = 1080, 500
    aria = (
        "Dos arboles de archivos lado a lado. A la izquierda, en rojo, la "
        "carpeta codigo del curso, que es de solo lectura. A la derecha, en "
        "verde, tu carpeta dentro de estudiantes, con tu nombre de usuario de "
        "GitHub. Los nombres de subcarpeta y de archivo son identicos en los "
        "dos lados, y una flecha los une con el comando de copia"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "Tu carpeta es un espejo: misma ruta, mismo nombre", TEXTO, 21, peso="600"))

    # La sangria va en la x, no en espacios: SVG los colapsa.
    def arbol(x0, y0, color, filas):
        salida = []
        y = y0
        for nivel, nombre, fuerte in filas:
            salida.append(teclado(x0 + nivel * 22, y, nombre, color, 15,
                                  anclaje="start", peso="600" if fuerte else "normal"))
            y += 34
        return salida

    p.append(caja(40, 82, 420, 236, PANEL, ROJO))
    p.append(texto(250, 112, "zona roja — sólo lectura", ROJO, 15, peso="600"))
    p.extend(arbol(70, 152, ROJO, [
        (0, "codigo/", False), (1, "07_git/", True),
        (2, "ejemplo.sh", False), (2, "notas.md", False),
    ]))
    p.append(texto(250, 300, "lo que yo publico. No lo edites.", SUAVE, 12.5))

    p.append(caja(620, 82, 420, 236, PANEL, ACENTO))
    p.append(texto(830, 112, "zona verde — tuya", ACENTO, 15, peso="600"))
    p.extend(arbol(650, 152, ACENTO, [
        (0, "estudiantes/", False), (1, "tu-login/", False),
        (2, "07_git/", True), (3, "ejemplo.sh", False),
    ]))
    p.append(texto(830, 300, "aquí trabajas. Sólo aquí.", SUAVE, 12.5))

    p.append(flecha(468, 196, 612, 196, ACENTO, 2.5))
    p.append(chip(540, 168, "copiar", ACENTO, tam=13))

    p.append(caja(120, 350, 840, 64, FONDO, ACENTO, radio=10, grosor=1.6))
    p.append(teclado(540, 378, "cp -r codigo/07_git/. estudiantes/$U/07_git/", ACENTO, 16))
    p.append(texto(540, 402, "la barra y el punto copian el contenido, no la carpeta: sin ellos acabas con 07_git dentro de 07_git", SUAVE, 12))

    p.append(texto(ancho / 2, 448, "El nombre 07_git no se inventa ni se traduce: es el mismo de los dos lados, y el robot lo compara.", SUAVE, 13.5))
    p.append(texto(ancho / 2, 474, "Tu carpeta se llama exactamente como tu usuario de GitHub, que sale de un comando y no del teclado.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def git_el_ritual():
    """Los doce pasos, en tres bloques con nombre."""
    ancho, alto = 1080, 560
    aria = (
        "Tres carriles verticales con el flujo completo. El primero, ponte al "
        "dia, sincroniza main con el repositorio del curso y actualiza tu fork. "
        "El segundo, abre tu espacio, crea la branch de la tarea y copia el "
        "codigo a tu carpeta. El tercero, entrega, revisa el estado, agrega por "
        "ruta, commitea, sube la branch y abre el pull request"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, "El ritual: tres bloques, siempre en este orden", TEXTO, 21, peso="600"))

    bloques = [
        (40, ACENTO, "A", "Ponte al día",
         ["cd ~/fdd/fdd_o26", "git switch main", "git fetch upstream",
          "git merge upstream/main", "git push origin main"],
         "Tu main queda idéntico al del curso."),
        (373, AMBAR, "B", "Abre tu espacio",
         ["git switch -c tarea-07-git", "mkdir -p estudiantes/$U/07_git",
          "cp -r codigo/07_git/. \u2192 tu carpeta", "", "y trabaja sólo ahí dentro"],
         "Nunca en main. Nunca fuera de tu carpeta."),
        (706, CIAN, "C", "Entrega",
         ["git status", "git add estudiantes/$U/07_git", "git status",
          "git commit -m \"...\"", "git push -u origin tarea-07-git"],
         "Y abre el pull request en el navegador."),
    ]
    for x, color, letra, titulo, pasos, cierre_txt in bloques:
        cx = x + 167
        p.append(caja(x, 80, 334, 372, PANEL, color))
        p.append(estado(cx, 118, letra, r=24, borde=color, color_texto=color))
        p.append(texto(cx, 168, titulo, color, 18, peso="600"))
        y = 200
        for paso in pasos:
            if paso:
                p.append(caja(x + 20, y, 294, 36, FONDO, color, radio=7, grosor=1.2))
                p.append(teclado(cx, y + 24, paso, color, 12.5, peso="normal"))
            y += 44
        p.append(texto(cx, 428, cierre_txt, SUAVE, 12.5))

    p.append(flecha(384, 266, 364, 266, SUAVE, 2))
    p.append(flecha(717, 266, 697, 266, SUAVE, 2))

    p.append(texto(ancho / 2, 494, "Los dos git status del bloque C no son adorno: son el hábito que evita subir basura. Míralos de verdad.", TEXTO, 14, peso="600"))
    p.append(texto(ancho / 2, 522, "El último paso es comprobar que el robot quedó en verde. Sin eso no entregaste, aunque el pull request exista.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def git_tres_vias():
    """El merge de tres vias: Git compara las dos versiones contra el ancestro."""
    ancho, alto = 1080, 560
    aria = (
        "El mecanismo del merge. Arriba, tres columnas con el mismo archivo: la "
        "version base que es el ancestro comun, la version tuya y la version de "
        "la otra branch. Cada linea esta marcada segun quien la cambio respecto "
        "de la base. Abajo, el resultado: donde solo uno cambio, Git toma ese "
        "cambio sin preguntar; donde cambiaron los dos, marca conflicto"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 40, "Git no compara tu versión con la otra: compara las dos contra el ancestro", TEXTO, 20, peso="600"))

    cols = [
        (40, SUAVE, "base", "el último commit que", "las dos compartían",
         [("línea 3", "hola", SUAVE), ("línea 12", "buenos días", SUAVE), ("línea 60", "adiós", SUAVE)]),
        (390, CIAN, "tu versión", "lo que hiciste", "en tu branch",
         [("línea 3", "hola", SUAVE), ("línea 12", "qué tal", CIAN), ("línea 60", "adiós", SUAVE)]),
        (740, VIOLETA, "la otra versión", "lo que hicieron", "en la otra branch",
         [("línea 3", "buenas", VIOLETA), ("línea 12", "buenas tardes", VIOLETA), ("línea 60", "adiós", SUAVE)]),
    ]
    for x, color, titulo, g1, g2, filas in cols:
        cx = x + 150
        p.append(caja(x, 76, 300, 210, PANEL, color))
        p.append(texto(cx, 106, titulo, color, 17, peso="600"))
        p.append(texto(cx, 128, g1, SUAVE, 12))
        p.append(texto(cx, 146, g2, SUAVE, 12))
        y = 168
        for etiqueta, valor, c in filas:
            p.append(caja(x + 18, y, 264, 34, FONDO, c, radio=6, grosor=1.2))
            p.append(texto(x + 46, y + 22, etiqueta, SUAVE, 11.5, anclaje="start"))
            p.append(teclado(x + 200, y + 22, valor, c, 13, anclaje="middle", peso="normal"))
            y += 40

    p.append(caja(240, 366, 600, 128, PANEL, ACENTO))
    p.append(texto(540, 396, "resultado del merge", ACENTO, 17, peso="600"))
    res = [
        ("línea 3", "buenas", "sólo la otra la tocó", ACENTO),
        ("línea 12", "CONFLICTO", "las dos la tocaron", ROJO),
        ("línea 60", "adiós", "nadie la tocó", ACENTO),
    ]
    y = 414
    for etiqueta, valor, nota, c in res:
        p.append(texto(288, y + 16, etiqueta, SUAVE, 11.5, anclaje="start"))
        p.append(teclado(430, y + 16, valor, c, 13, anclaje="middle", peso="600" if c is ROJO else "normal"))
        p.append(texto(660, y + 16, nota, SUAVE, 11.5, anclaje="start"))
        y += 26

    p.append(flecha(190, 296, 400, 358, CIAN, 2))
    p.append(flecha(540, 296, 540, 358, SUAVE, 2))
    p.append(flecha(890, 296, 680, 358, VIOLETA, 2))

    p.append(texto(ancho / 2, 526, "La regla es una sola: si un cambio viene de un solo lado, Git lo toma. Si viene de los dos, te pregunta a ti.", TEXTO, 14, peso="600"))
    p.append(cierre())
    return "".join(p)


def git_hunks():
    """Por que 'lineas distintas' no basta: Git compara bloques con contexto."""
    ancho, alto = 1080, 540
    aria = (
        "Dos casos del mismo archivo de setenta lineas. En el primero, las dos "
        "personas editan lineas muy separadas y los bloques de contexto que Git "
        "toma alrededor de cada cambio no se tocan, asi que el merge sale solo. "
        "En el segundo editan lineas vecinas, los bloques se traslapan y hay "
        "conflicto aunque las lineas sean distintas"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 40, "«Líneas distintas» no basta: Git compara bloques, no líneas sueltas", TEXTO, 20, peso="600"))

    TOP, REG = 138, 240

    def columna(x0, titulo, color, ediciones, veredicto, nota, colv):
        s = [caja(x0, 74, 470, 356, PANEL, color)]
        s.append(texto(x0 + 235, 104, titulo, color, 16, peso="600"))
        xr = x0 + 40
        s.append(caja(xr, TOP, 44, REG, FONDO, SUAVE, radio=6, grosor=1.2))
        for n in (1, 20, 40, 70):
            yy = TOP + (n - 1) / 69 * REG
            s.append(texto(xr - 12, yy + 5, str(n), SUAVE, 10.5, anclaje="end"))
        # Las etiquetas van en ranuras fijas: si dos ediciones caen juntas, sus
        # textos se encimarian al colgarlos de la banda.
        for linea, quien, c, ranura in ediciones:
            yy = TOP + (linea - 1) / 69 * REG
            s.append(f'<rect x="{xr}" y="{yy - 11}" width="44" height="22" rx="4" '
                     f'fill="{c}" fill-opacity="0.3" stroke="{c}" stroke-width="1.3"/>')
            s.append(f'<line x1="{xr + 44}" y1="{yy}" x2="{x0 + 128}" y2="{ranura}" '
                     f'stroke="{c}" stroke-width="1.2" stroke-dasharray="4 3"/>')
            s.append(texto(x0 + 136, ranura - 4, f"{quien} edita la línea {linea}", c, 13, anclaje="start"))
            s.append(texto(x0 + 136, ranura + 15, "y su bloque de contexto", SUAVE, 11.5, anclaje="start"))
        s.append(texto(x0 + 235, 402, veredicto, colv, 17, peso="600"))
        s.append(texto(x0 + 235, 456, nota, SUAVE, 13))
        return s

    p.extend(columna(40, "lejos: los bloques no se tocan", ACENTO,
                     [(8, "ana", CIAN, 178), (62, "beto", VIOLETA, 336)],
                     "Merge automático", "Git aplica los dos cambios sin preguntar.", ACENTO))
    p.extend(columna(570, "pegados: los bloques se traslapan", ROJO,
                     [(33, "ana", CIAN, 200), (37, "beto", VIOLETA, 300)],
                     "Conflicto", "Aunque las líneas sean distintas.", ROJO))

    p.append(texto(ancho / 2, 502, "No hay un número mágico de líneas de separación: depende de cuánto contexto tome Git alrededor de cada cambio.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def git_paralelo_matriz():
    """Que hace Git segun que hayan tocado los dos lados."""
    ancho, alto = 1080, 500
    aria = (
        "Una tabla de seis escenarios de trabajo simultaneo. Cada fila dice que "
        "toco cada persona y que hace Git: en los tres primeros resuelve solo, y "
        "en los tres ultimos marca conflicto y pide que alguien decida. Los "
        "casos van de archivos distintos hasta uno que borra mientras el otro "
        "edita el mismo archivo"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 40, "Qué hace Git según lo que haya tocado cada quien", TEXTO, 20, peso="600"))

    filas = [
        ("archivos distintos", "toca main.py", "toca app.py", "resuelve solo", ACENTO),
        ("mismo archivo, lejos", "línea 3", "línea 60", "resuelve solo", ACENTO),
        ("una branch no avanzó", "3 commits", "nada", "fast-forward", ACENTO),
        ("mismo archivo, pegados", "línea 33", "línea 37", "conflicto", ROJO),
        ("la misma línea", "línea 12", "línea 12", "conflicto", ROJO),
        ("uno borra, otro edita", "borra notas.md", "edita notas.md", "conflicto", ROJO),
    ]
    encabezados = ("el escenario", "ana", "beto", "qué hace Git")
    xs = (60, 380, 620, 860)
    p.append(texto(xs[0], 90, encabezados[0], SUAVE, 12.5, anclaje="start"))
    for k in (1, 2, 3):
        p.append(texto(xs[k], 90, encabezados[k], SUAVE, 12.5, anclaje="middle"))

    y = 108
    for escenario, a, b, resultado, color in filas:
        p.append(caja(40, y, 1000, 52, PANEL, color, radio=8, grosor=1.4))
        p.append(texto(xs[0], y + 32, escenario, TEXTO, 14, anclaje="start"))
        p.append(teclado(xs[1], y + 32, a, CIAN, 12.5, peso="normal"))
        p.append(teclado(xs[2], y + 32, b, VIOLETA, 12.5, peso="normal"))
        p.append(texto(xs[3], y + 32, resultado, color, 14, peso="600"))
        y += 60

    p.append(texto(ancho / 2, 484, "Conflicto no significa que algo se rompió: significa que Git no puede decidir por ti y se detiene antes de tirar trabajo.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def git_paralelo_raros():
    """Tres conflictos que no son de contenido y confunden la primera vez."""
    ancho, alto = 1080, 430
    aria = (
        "Tres casos de conflicto que no son de contenido. En el primero uno "
        "borra un archivo mientras el otro lo edita. En el segundo los dos crean "
        "un archivo con el mismo nombre y distinto contenido. En el tercero uno "
        "renombra el archivo mientras el otro lo edita, y Git suele seguir el "
        "contenido y aplicar la edicion sobre el nombre nuevo"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 40, "Tres conflictos que no son de contenido", TEXTO, 20, peso="600"))

    casos = [
        (40, ROJO, "borrar contra editar", "ana borra notas.md",
         "beto edita notas.md", "Git no adivina si el archivo",
         "debe existir. Tú decides."),
        (375, ROJO, "los dos lo crean", "ana crea guia.md",
         "beto crea guia.md", "Mismo nombre, distinto contenido.",
         "Conflicto desde la primera línea."),
        (710, AMBAR, "renombrar contra editar", "ana lo llama apuntes.md",
         "beto edita notas.md", "Git sigue el contenido y suele",
         "aplicar la edición al nombre nuevo."),
    ]
    for x, color, titulo, a, b, n1, n2 in casos:
        cx = x + 165
        p.append(caja(x, 76, 330, 280, PANEL, color))
        p.append(texto(cx, 108, titulo, color, 15.5, peso="600"))
        p.append(caja(x + 22, 132, 286, 38, FONDO, CIAN, radio=7, grosor=1.2))
        p.append(teclado(cx, 156, a, CIAN, 12.5, peso="normal"))
        p.append(caja(x + 22, 180, 286, 38, FONDO, VIOLETA, radio=7, grosor=1.2))
        p.append(teclado(cx, 204, b, VIOLETA, 12.5, peso="normal"))
        p.append(texto(cx, 254, n1, SUAVE, 12.5))
        p.append(texto(cx, 274, n2, SUAVE, 12.5))
        p.append(texto(cx, 324, "git status te dice cuál es", color, 12.5))

    p.append(texto(ancho / 2, 396, "En los tres, la salida es la misma que ya conoces: git merge --abort para volver atrás, o resolver y hacer git add.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


DIAGRAMAS = {
    "git-llaves": git_llaves,
    "git-flujo": git_flujo,
    "git-linea-del-tiempo": git_linea_del_tiempo,
    "git-tres-zonas": git_tres_zonas,
    "git-objetos": git_objetos,
    "git-lo-que-no-se-sube": git_lo_que_no_se_sube,
    "git-deshacer": git_deshacer,
    "git-branches": git_branches,
    "git-conflicto": git_conflicto,
    "git-tres-repos": git_tres_repos,
    "git-race": git_race,
    "git-el-mirror": git_el_mirror,
    "git-el-ritual": git_el_ritual,
    "git-tres-vias": git_tres_vias,
    "git-hunks": git_hunks,
    "git-paralelo-matriz": git_paralelo_matriz,
    "git-paralelo-raros": git_paralelo_raros,
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
