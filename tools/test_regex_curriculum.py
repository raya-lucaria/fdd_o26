"""Guardas focales de la unidad de Expresiones regulares.

Dos cosas distintas se vigilan aqui:

1. **Que los comandos corran.** Cada pagina prepara su propia entrada, asi que
   los bloques ```bash de una pagina se ejecutan seguidos en un HOME temporal
   sembrado con el laboratorio de la pagina 1. No se exige codigo de salida 0
   —varios ejemplos existen justamente para no encontrar nada— pero si se exige
   que ningun comando escriba en stderr: eso es lo que delata un patron mal
   escrito, una bandera inexistente o un archivo que nadie creo.

2. **La forma de la pagina.** La unidad se escribio con reglas explicitas para
   que se pueda leer con la atencion dispersa: una meta de una linea, un
   diagrama arriba, un "En corto" de tres vinetas, un solo ejercicio y un
   cierre de una frase. Sin guarda, esas reglas se erosionan en la primera
   edicion apurada.
"""
import re
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/6_expresiones_regulares"
INDICE = UNIDAD / "0_index.md"
CHULETA = UNIDAD / "A_chuleta.md"

# Las seis paginas de leccion, en el orden en que se leen.
LECCIONES = [
    UNIDAD / "1_que_es_una_regex.md",
    UNIDAD / "2_leer_izquierda_derecha.md",
    UNIDAD / "3_piezas_de_un_patron.md",
    UNIDAD / "4_cuantas_veces.md",
    UNIDAD / "5_taquigrafia_perl.md",
    UNIDAD / "6_grupos_y_captura.md",
    UNIDAD / "7_grep_awk_en_serio.md",
]
IDS = [p.stem for p in LECCIONES]

# Techo de longitud: unas tres pantallas. La unidad 5 llego a 268 lineas en una
# sola pagina y ahi es donde se pierde el lector al que apunta esta unidad.
MAX_LINEAS = 160


def lee(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def bloques_bash(texto: str):
    return re.findall(r"```bash\n(.*?)```", texto, re.S)


@pytest.fixture(scope="module")
def home(tmp_path_factory):
    """Un HOME desechable con el laboratorio de la pagina 1 ya montado."""
    raiz = tmp_path_factory.mktemp("regex-home")
    guion = "\n".join(bloques_bash(lee(LECCIONES[0])))
    resultado = corre(guion, raiz)
    assert resultado.returncode == 0, resultado.stderr
    return raiz


def corre(guion: str, home: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-c", guion],
        cwd=home,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin", "LANG": "en_US.UTF-8"},
        capture_output=True,
        check=False,
        text=True,
    )


# --------------------------------------------------------------------------
# Los comandos corren
# --------------------------------------------------------------------------

def test_la_pagina_1_deja_los_tres_archivos_del_laboratorio(home):
    lab = home / "fdd/regex-lab"
    for nombre in ("contactos.txt", "bitacora.log", "precios.csv"):
        assert (lab / nombre).is_file(), f"la pagina 1 no creo {nombre}"


def test_el_laboratorio_conserva_las_trampas_plantadas(home):
    """Los edge cases de las paginas 2 a 6 viven en los datos, no en el texto.

    Si alguien 'limpia' el laboratorio, media unidad deja de tener ejemplos.
    """
    contactos = (home / "fdd/regex-lab/contactos.txt").read_text(encoding="utf-8")
    for trampa, porque in (
        ("Mariana", "la subcadena que sorprende en la pagina 2"),
        ("raul@@itam.mx", "las dos arrobas que rechaza el patron de correo"),
        ("Muñoz", "el acento del caso de locale de la pagina 4"),
        ("Equipo 3:", "la linea con dos correos, para el caso goloso"),
    ):
        assert trampa in contactos, f"falta {trampa!r} en contactos.txt: {porque}"

    bitacora = (home / "fdd/regex-lab/bitacora.log").read_text(encoding="utf-8")
    assert "el el archivo" in bitacora, "falta la palabra repetida para la retro-referencia"

    precios = (home / "fdd/regex-lab/precios.csv").read_text(encoding="utf-8")
    assert '"cable, 2 metros"' in precios, "falta la coma entre comillas que rompe a awk"


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS)
def test_los_bloques_de_la_pagina_corren_sin_diagnosticos(pagina, home):
    """Ningun comando de la unidad debe escribir en stderr.

    No se exige returncode 0: `grep` sale con 1 cuando no encuentra nada, y
    varios ejemplos existen precisamente para no encontrar nada. Lo que si
    delata un error real es un diagnostico: patron invalido, bandera que no
    existe, archivo que nadie creo.
    """
    guion = "\n".join(bloques_bash(lee(pagina)))
    assert guion.strip(), f"{pagina.name} no tiene ningun bloque bash"
    resultado = corre(guion, home)
    assert not resultado.stderr.strip(), (
        f"{pagina.name} produjo diagnosticos:\n{resultado.stderr}"
    )


def test_la_tuberia_de_limpieza_deja_cinco_correos_unicos(home):
    """La cifra del diagrama rx-tuberia tiene que ser la de verdad."""
    guion = "\n".join(bloques_bash(lee(LECCIONES[5])))
    corre(guion, home)
    correos = (home / "fdd/regex-lab/correos.txt").read_text(encoding="utf-8")
    lineas = [l for l in correos.splitlines() if l.strip()]
    assert len(lineas) == 5, f"la tuberia dejo {len(lineas)} correos, no 5: {lineas}"
    assert lineas == sorted(lineas), "sort -u deberia dejarlos ordenados"
    assert all(l == l.lower() for l in lineas), "tr deberia haberlos pasado a minusculas"


# --------------------------------------------------------------------------
# La forma de la pagina
# --------------------------------------------------------------------------

@pytest.mark.parametrize("pagina", LECCIONES + [INDICE, CHULETA],
                         ids=IDS + ["0_index", "A_chuleta"])
def test_ninguna_pagina_pasa_el_techo_de_longitud(pagina):
    lineas = len(lee(pagina).splitlines())
    assert lineas <= MAX_LINEAS, (
        f"{pagina.name} tiene {lineas} lineas y el techo es {MAX_LINEAS}: "
        "parte la pagina o manda la referencia larga a A_chuleta.md"
    )


@pytest.mark.parametrize("i,pagina", list(enumerate(LECCIONES, 1)), ids=IDS)
def test_cada_pagina_abre_con_su_posicion_meta_y_diagrama(i, pagina):
    """Meta de una linea, diagrama, y despues el texto. En ese orden."""
    texto = lee(pagina)
    cuerpo = texto.split("\n# ", 1)[1]

    assert f"**Página {i} de 7**" in cuerpo, (
        f"{pagina.name} no dice en que punto de la unidad estas"
    )
    meta = re.search(r"^Meta: (.+)$", cuerpo, re.M)
    assert meta, f"{pagina.name} no abre con una linea 'Meta:'"
    assert len(meta.group(1)) <= 120, "la meta debe caber en una linea"

    pos_meta = cuerpo.index("Meta:")
    pos_figura = cuerpo.index("::: figure")
    pos_corto = cuerpo.index("## En corto")
    assert pos_meta < pos_figura < pos_corto, (
        f"{pagina.name}: el orden tiene que ser meta, diagrama y despues "
        "'En corto'; el ancla visual va antes del texto"
    )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS)
def test_el_en_corto_cabe_en_tres_vinetas(pagina):
    seccion = lee(pagina).split("## En corto", 1)[1].split("\n## ", 1)[0]
    vinetas = [l for l in seccion.splitlines() if l.startswith("- ")]
    assert 1 <= len(vinetas) <= 3, (
        f"{pagina.name}: 'En corto' tiene {len(vinetas)} vinetas; el maximo es 3"
    )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS)
def test_cada_pagina_trae_un_solo_ejercicio_completo(pagina):
    """Uno, con su pista y su respuesta. Dos seguidos rompen el ritmo."""
    texto = lee(pagina)
    problemas = re.findall(r'::: problem \{#([\w-]+)', texto)
    assert len(problemas) == 1, (
        f"{pagina.name} tiene {len(problemas)} ejercicios; debe tener exactamente 1"
    )
    for directiva in ("hint", "answer"):
        assert f'::: {directiva} {{of="{problemas[0]}"}}' in texto, (
            f"{pagina.name}: al ejercicio {problemas[0]} le falta su {directiva}"
        )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS)
def test_cada_pagina_cierra_con_una_sola_frase(pagina):
    """El cierre va como callout, no como objeto numerado.

    `note` no es una familia de objeto numerado de Raya —el build falla con
    "Unknown numbered object family"— y ademas una nota numerada no es lo que
    se quiere aqui: es un recordatorio, no una pieza a la que se referencie.
    """
    texto = lee(pagina)
    nota = re.search(r"^> \[!NOTE\]\n> \*\*Si sólo recuerdas una cosa:\*\* (.+)$",
                     texto, re.M)
    assert nota, f"{pagina.name} no cierra con el callout 'Si sólo recuerdas una cosa'"
    assert "::: note" not in texto, (
        f"{pagina.name}: `note` no es una familia valida de objeto numerado"
    )


# --------------------------------------------------------------------------
# El orden de los conceptos
# --------------------------------------------------------------------------

def test_grep_o_llega_antes_que_los_cuantificadores():
    """Sin `-o` no se ve que encontro el patron, y todo lo demas confunde."""
    pagina = lee(LECCIONES[1])
    assert pagina.index("Meta:") < pagina.index("grep -o"), (
        "grep -o se presenta en la pagina 2"
    )


def test_la_pieza_se_define_antes_de_cuantificarla():
    """El orden que hacia opaca a la unidad: se cuantificaba sin decir sobre que.

    «Pieza» es el concepto del que cuelga todo lo demas —a que se pega un
    cuantificador, por que una clase o un grupo cuentan como una sola cosa, por
    que una ancla no admite repeticion—. Tiene que estar definido antes de que
    aparezca el primer cuantificador de la unidad.
    """
    piezas, cuantos = lee(LECCIONES[2]), lee(LECCIONES[3])
    assert "::: definition {#rx-def-pieza" in piezas, (
        "la pagina 3 debe definir que es una pieza"
    )
    for termino in ("concatenaci", "ancla"):
        assert termino in piezas.lower(), f"falta '{termino}' en la pagina 3"
    assert "prerequisites: [piezas-de-un-patron]" in cuantos, (
        "cuantificar sin haber definido la pieza deja el concepto en el aire"
    )


def test_epsilon_se_define_donde_se_usa():
    """`ε` aparecia solo dentro de un diagrama, sin definirse en ninguna parte."""
    cuantos = lee(LECCIONES[3])
    assert "::: definition {#rx-def-epsilon" in cuantos, (
        "la pagina 4 debe definir ε antes de que el diagrama la muestre"
    )
    assert "cadena vac" in cuantos.lower()
    assert cuantos.index("ε") < cuantos.index("rx-backtracking"), (
        "ε se define antes de usarla"
    )


def test_el_backtracking_se_reconcilia_con_la_cabeza_que_no_regresa():
    """La unidad afirmaba las dos cosas sin decir que hablan de niveles distintos.

    Pagina 2: la cabeza no vuelve a una posicion descartada. Pagina 4: el
    cuantificador goloso cede caracteres. Sin la aclaracion, la segunda parece
    desmentir a la primera.
    """
    cuantos = lee(LECCIONES[3])
    assert "no** contradice la página 2" in cuantos or "no contradice la página 2" in cuantos, (
        "la pagina 4 debe explicar por que ceder no contradice a la pagina 2"
    )


def test_la_tabla_de_contexto_existe_como_diagrama_y_como_texto():
    """Que significa cada simbolo suelto, dentro de corchetes y escapado."""
    piezas = lee(LECCIONES[2])
    assert "rx-contexto.svg" in piezas
    for caso in ("[]]", "[a+b]", "[a-]"):
        assert caso in piezas, f"falta el caso {caso} en la tabla de contexto"


def test_la_unidad_no_ensena_grep_P_como_solucion():
    """-P no existe en macOS: la unidad vive en -E y en las clases POSIX."""
    for pagina in LECCIONES:
        for bloque in bloques_bash(lee(pagina)):
            assert "grep -P" not in bloque and "-Po" not in bloque, (
                f"{pagina.name} usa grep -P en un bloque ejecutable; no esta en macOS"
            )


def test_la_chuleta_apunta_a_todas_las_paginas():
    texto = lee(CHULETA)
    for pagina in LECCIONES:
        ident = re.search(r"^id: ([\w-]+)$", lee(pagina), re.M).group(1)
        assert f"[[{ident}" in texto, f"la chuleta no enlaza a {ident}"


def test_el_indice_lista_las_seis_paginas_y_la_chuleta():
    texto = lee(INDICE)
    for pagina in LECCIONES + [CHULETA]:
        ident = re.search(r"^id: ([\w-]+)$", lee(pagina), re.M).group(1)
        assert f"[[{ident}" in texto, f"el indice no enlaza a {ident}"


def test_el_calendario_apunta_a_la_unidad():
    calendario = lee(RAIZ / "course/_official/calendar/1_2026-o26.yaml")
    assert "page: expresiones-regulares" in calendario, (
        "falta la sesion de la unidad en el calendario"
    )


# --------------------------------------------------------------------------
# La colision con la sintaxis de footnote
# --------------------------------------------------------------------------

_FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")
_FOOTNOTE_REF = re.compile(r"(?<!\\)\[\^([^\]\s]+)\]")


@pytest.mark.parametrize("pagina", LECCIONES + [INDICE, CHULETA],
                         ids=IDS + ["0_index", "A_chuleta"])
def test_ninguna_clase_negada_vive_fuera_de_un_bloque_cercado(pagina):
    """`[^X]` en prosa es, para el validador, una referencia a nota al pie.

    Raya busca footnotes con `(?<!\\\\)\\[\\^([^\\]\\s]+)\\]` sobre el cuerpo al que
    solo le quito los bloques cercados: un code span en linea NO lo protege.
    Como la clase negada es la construccion mas util de la unidad, colisiona
    en cada pagina y tumba el build entero con "Missing footnote definition".

    La regla, entonces: las clases negadas se muestran dentro de un bloque
    ```bash, y en prosa y en tablas se nombran en palabras.
    """
    dentro, ofensas = False, []
    for numero, linea in enumerate(lee(pagina).splitlines(), 1):
        if _FENCE.match(linea):
            dentro = not dentro
            continue
        if dentro:
            continue
        encontradas = _FOOTNOTE_REF.findall(linea)
        if encontradas:
            ofensas.append(f"  linea {numero}: {encontradas} -> {linea.strip()[:80]}")
    assert not ofensas, (
        f"{pagina.name} escribe una clase negada fuera de un bloque cercado; "
        "raya la lee como referencia a nota al pie y falla el build:\n"
        + "\n".join(ofensas)
    )


# --------------------------------------------------------------------------
# Cadenas inline
# --------------------------------------------------------------------------

_INLINE = re.compile(r"printf .*\|\s*(?:LC_ALL=\S+ )?grep")


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS)
def test_cada_pagina_prueba_con_cadenas_en_vivo(pagina):
    """Un archivo de por medio aleja el patron de su resultado.

    La unidad empezo apoyandose casi solo en archivos: para ver que hacia un
    cuantificador habia que crear un .txt, acordarse de su contenido y correr
    grep contra el. Con las cadenas en la propia linea, el patron y las cadenas
    que casan —y las que no— caben en el mismo bloque de tres renglones.

    Los archivos del laboratorio se quedan donde el dato sucio es el punto:
    correos con dos arrobas, la bitacora, el CSV con la coma entre comillas.
    """
    inline = [b for b in bloques_bash(lee(pagina)) if _INLINE.search(b)]
    assert inline, (
        f"{pagina.name} no prueba ningun patron con cadenas en vivo; "
        "usa printf '%s\\n' 'una' 'otra' | grep -nE '...'"
    )


def test_las_paginas_de_sintaxis_no_dependen_de_archivos_de_juguete(home):
    """Paginas 2 a 4: la sintaxis se ensena con cadenas, no con .txt desechables.

    Antes cada una creaba su propio archivo de tres palabras. Si alguien vuelve
    a hacerlo, el ejemplo deja de leerse de un vistazo.
    """
    redirige = re.compile(r">\s*[\w./~-]+\.(?:txt|log|csv)\b")
    for pagina in LECCIONES[1:4]:
        for bloque in bloques_bash(lee(pagina)):
            escrito = redirige.search(bloque)
            assert not escrito, (
                f"{pagina.name} vuelve a escribir el archivo de juguete "
                f"{escrito.group()!r}; estas paginas se prueban con cadenas "
                "en vivo, que se leen de un vistazo"
            )
