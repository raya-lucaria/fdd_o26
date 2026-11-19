"""Guardas de la revision de contenido minimo.

Dos familias. Las estructurales protegen la propiedad de seguridad que hace
sano a `pull_request_target`: el script no puede leer ni ejecutar nada del
arbol de trabajo, porque bajo ese disparador el arbol podria venir del fork.
Las de logica protegen que los mensajes sigan siendo accionables y que el
catalogo concuerde con lo que los objetos oficiales prometen.
"""
import importlib.util
import re
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / ".github/scripts/revisa_contenido.py"
WORKFLOW = RAIZ / ".github/workflows/entregas.yml"
OFICIALES = RAIZ / "course/8_contenedores/_official/assignments"


def _modulo():
    spec = importlib.util.spec_from_file_location("revisa_contenido", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rc = _modulo()


# --------------------------------------------------------------------------
# Estructurales: la propiedad de seguridad de pull_request_target
# --------------------------------------------------------------------------

def test_el_script_no_lee_el_arbol_de_trabajo():
    """Nada de open() ni Path.read_text(): todo entra por la API o el entorno.

    Con `pull_request_target` el checkout esta fijado a base.sha, pero un
    descuido futuro que moviera esa fijacion convertiria cualquier lectura de
    disco en una via para que el pull request se juzgue a si mismo. La unica
    excepcion es el propio modulo base64, que no toca disco.
    """
    texto = SCRIPT.read_text(encoding="utf-8")
    codigo = "\n".join(
        l for l in texto.splitlines() if not l.strip().startswith("#")
    )
    for prohibido in ("open(", "read_text", "read_bytes", "Path(", "os.walk",
                      "glob", "importlib"):
        assert prohibido not in codigo, (
            f"revisa_contenido.py usa '{prohibido}': bajo pull_request_target "
            "no puede leer del arbol de trabajo, solo de la API y del entorno"
        )


def test_el_script_no_ejecuta_nada_del_pull_request():
    """El unico subproceso permitido es `gh api`, que solo consulta."""
    texto = SCRIPT.read_text(encoding="utf-8")
    llamadas = re.findall(r"subprocess\.\w+\(\s*\n?\s*\[([^\]]*)\]", texto)
    assert llamadas, "no encontre ninguna llamada a subprocess: revisa el patron"
    for args in llamadas:
        assert '"gh"' in args and '"api"' in args, (
            f"subprocess con algo que no es `gh api`: {args}"
        )


def test_el_catalogo_vive_en_el_script_y_no_en_un_archivo():
    """Si el catalogo fuera un archivo del repo, un fork podria reescribirlo."""
    assert isinstance(rc.CATALOGO, dict) and rc.CATALOGO
    texto = SCRIPT.read_text(encoding="utf-8")
    assert "CATALOGO = {" in texto


def test_el_workflow_corre_el_script_despues_del_de_forma():
    datos = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    pasos = datos["jobs"]["revision"]["steps"]
    corridas = [p.get("run", "") for p in pasos]
    i_forma = next(i for i, c in enumerate(corridas) if "revisa_entrega.py" in c)
    i_cont = next(i for i, c in enumerate(corridas) if "revisa_contenido.py" in c)
    assert i_forma < i_cont, (
        "el contenido se revisa despues de la forma: no tiene sentido exigir "
        "un archivo dentro de una carpeta que todavia no sabemos si es la suya"
    )


def test_el_workflow_sigue_fijado_a_base_sha():
    """La fijacion es lo que hace seguro leer contenido por la API."""
    datos = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    # PyYAML lee la llave `on:` como el booleano True.
    assert list(datos[True]) == ["pull_request_target"]
    checkout = datos["jobs"]["revision"]["steps"][0]
    assert checkout["with"]["ref"] == "${{ github.event.pull_request.base.sha }}"
    assert checkout["with"]["persist-credentials"] is False


# --------------------------------------------------------------------------
# El catalogo contra lo que los objetos oficiales prometen
# --------------------------------------------------------------------------

def test_cada_branch_del_catalogo_existe_en_el_workflow():
    """El mapa de carpetas y el catalogo de contenido no pueden discrepar."""
    datos = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    env = datos["jobs"]["revision"]["steps"][1]["env"]
    mapa = {}
    for par in env["TAREAS"].split(","):
        if "=" in par:
            rama, carpeta = par.split("=", 1)
            mapa[rama.strip()] = carpeta.strip()
    for rama, tarea in rc.CATALOGO.items():
        assert rama in mapa, f"'{rama}' esta en el catalogo pero no en TAREAS"
        assert mapa[rama] == tarea["carpeta"], (
            f"'{rama}': el catalogo dice '{tarea['carpeta']}' y TAREAS dice "
            f"'{mapa[rama]}'"
        )


def test_las_capturas_del_catalogo_se_nombran_en_su_objeto_oficial():
    """Un nombre de archivo inventado aqui rechazaria entregas correctas."""
    prosa = " ".join(
        " ".join(yaml.safe_load(f.read_text(encoding="utf-8"))
                 ["content"]["instructions"].split())
        for f in sorted(OFICIALES.glob("*.yaml"))
    ).lower()
    # Los objetos deletrean los nombres en palabras porque el campo se escapa
    # a texto plano: "intermedio guion 1 guion 2 punto png".
    for tarea in rc.CATALOGO.values():
        if "captura" not in tarea:
            continue
        deletreado = tarea["captura"].replace("-", " guion ")
        assert deletreado in prosa, (
            f"la captura '{tarea['captura']}' del catalogo no aparece "
            f"deletreada ('{deletreado}') en ningun objeto oficial"
        )


# --------------------------------------------------------------------------
# Logica: secciones de certificaciones.md
# --------------------------------------------------------------------------

PLANTILLA = """# Certificaciones de Docker

## Introduction to Docker

Se llena en la **primera** entrega.

Fecha en que lo terminaste:

URL del Statement of Accomplishment:

![Captura](./introduccion-a-docker.png)

## Intermediate Docker · capítulos 1 y 2

Fecha:
"""


def test_la_plantilla_sin_llenar_se_detecta():
    cuerpo = rc.cuerpo_de_seccion(PLANTILLA, "Introduction to Docker")
    assert cuerpo is not None
    assert rc._sin_llenar(cuerpo), "la plantilla tal como viene debe contar como vacia"


def test_una_seccion_llena_pasa():
    lleno = PLANTILLA.replace(
        "Fecha en que lo terminaste:",
        "Fecha en que lo terminaste: 2026-09-21",
    ).replace(
        "URL del Statement of Accomplishment:",
        "URL del Statement of Accomplishment: https://www.datacamp.com/completed/statement-of-accomplishment/course/abc123",
    )
    cuerpo = rc.cuerpo_de_seccion(lleno, "Introduction to Docker")
    assert not rc._sin_llenar(cuerpo)
    assert rc._tiene_fecha(cuerpo)
    assert rc._tiene_url(cuerpo)


@pytest.mark.parametrize("fecha", [
    "2026-09-21", "21/09/2026", "21 de septiembre de 2026",
])
def test_los_tres_formatos_de_fecha_valen(fecha):
    assert rc._tiene_fecha(f"Fecha: {fecha}"), (
        "rechazar un formato de fecha legible seria rechazar una entrega buena"
    )


def test_la_seccion_se_encuentra_aunque_cambie_la_puntuacion():
    """El titulo trae un separador raro; nadie pierde puntos por teclearlo mal."""
    variante = PLANTILLA.replace("capítulos 1 y 2", "Capitulos 1 y 2")
    assert rc.cuerpo_de_seccion(variante, "capítulos 1 y 2") is None
    assert rc.cuerpo_de_seccion(variante, "apitulos 1 y 2") is not None


def test_una_seccion_ausente_se_distingue_de_una_vacia():
    """Son dos fallos distintos y dan dos mensajes distintos."""
    assert rc.cuerpo_de_seccion(PLANTILLA, "capítulos 3 y 4") is None


# --------------------------------------------------------------------------
# Logica: los defectos del Dockerfile
# --------------------------------------------------------------------------

ROTO = "FROM python:latest\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"python\", \"app.py\"]\n"
ARREGLADO = (
    "FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\n"
    "RUN pip install -r requirements.txt\nCOPY . .\n"
    "RUN useradd -m app\nUSER app\nCMD [\"python\", \"app.py\"]\n"
)


def _fallos_dockerfile(texto_df, texto_sh="echo hola"):
    return rc.revisa_imagen(
        set(), lambda r: texto_df if "Dockerfile" in r else texto_sh, "base"
    )


def test_el_dockerfile_sin_arreglar_falla_por_los_dos_defectos():
    fallos = _fallos_dockerfile(ROTO)
    assert len(fallos) == 2
    assert any("latest" in f for f in fallos)
    assert any("USER" in f for f in fallos)


def test_el_dockerfile_arreglado_pasa():
    assert _fallos_dockerfile(ARREGLADO) == []


def test_el_echo_de_depuracion_se_detecta():
    fallos = _fallos_dockerfile(ARREGLADO, 'echo "=== Discooooooooooo ==="')
    assert len(fallos) == 1 and "depuracion" in fallos[0]


def test_el_encabezado_legitimo_de_disco_no_dispara():
    """`=== Disco ===` es del original y se queda; el de las oes es el que sale."""
    assert _fallos_dockerfile(ARREGLADO, 'echo "=== Disco ==="') == []


# --------------------------------------------------------------------------
# Los mensajes
# --------------------------------------------------------------------------

def test_todo_mensaje_de_fallo_dice_donde_investigar():
    """Un mensaje que solo dice 'incorrecto' obliga a adivinar; uno que da el
    comando le quita al alumno lo que tenia que entender. Cada fallo dice
    que, por que y donde investigar."""
    texto = SCRIPT.read_text(encoding="utf-8")
    bloques = re.findall(r'fallos\.append\(\s*(.*?)\s*\)\n', texto, re.S)
    assert len(bloques) >= 6, "esperaba mas mensajes de fallo; revisa el patron"
    for b in bloques:
        assert "Donde investigar: " in b, f"mensaje sin donde investigar: {b[:60]}"


def test_los_mensajes_no_dan_el_como():
    """Regla del profesor: jamas como arreglarlo. Ni comandos ni recetas."""
    texto = re.sub(r'"""(.*?)"""', "", SCRIPT.read_text(encoding="utf-8"), flags=re.S)
    codigo = "\n".join(l.split("#", 1)[0] for l in texto.splitlines())
    literales = " ".join(re.findall(r'"([^"\n]*)"', codigo))
    for r in ("Arreglo", "git ", "haz push", "Vuelve a subir", "vuelve a copiar",
              "Llena esa", "fija una version", "comando del ritual", "Escribela"):
        assert r not in literales, f"revisa_contenido.py todavia dice '{r}'"


def test_el_catalogo_ya_no_crece():
    """Las tareas nuevas van en una ficha (.github/tareas/) y las revisa
    revisa_ficha.py. Aqui se quedan solo las dos que tenian entregas en curso
    cuando entraron las fichas; inter-1 e inter-2 migraron."""
    assert set(rc.CATALOGO) == {"tarea-08-datacamp-intro", "tarea-08-imagen"}


def test_una_branch_fuera_del_catalogo_no_se_revisa():
    """Las tareas de la unidad 7 no declararon branch: no hay que adivinar."""
    assert rc.CATALOGO.get("tarea-07-git") is None
    assert rc.CATALOGO.get("entrega2") is None


# --------------------------------------------------------------------------
# El catalogo contra la plantilla que el estudiante copia
# --------------------------------------------------------------------------

PLANTILLA_DOCKER = RAIZ / "codigo/docker/certificaciones.md"


def test_pide_url_concuerda_con_la_plantilla():
    """Exigir una URL que la plantilla no pide rechaza entregas correctas.

    Esta prueba existe por un susto real: probando el script contra una
    entrega de la unidad 7 lo configure con pide_url=True, salio en rojo, y
    la entrega estaba bien — la plantilla de esa unidad nunca pidio URL. El
    alumno habria tenido que adivinar que inventarse. La plantilla es la
    autoridad: si ella no pide la URL, el robot tampoco.
    """
    texto = PLANTILLA_DOCKER.read_text(encoding="utf-8")
    for rama, tarea in rc.CATALOGO.items():
        if "seccion" not in tarea:
            continue
        cuerpo = rc.cuerpo_de_seccion(texto, tarea["seccion"])
        assert cuerpo is not None, (
            f"'{rama}': la seccion «{tarea['seccion']}» no existe en "
            f"{PLANTILLA_DOCKER.relative_to(RAIZ)}"
        )
        pide = "url" in cuerpo.lower()
        assert pide == bool(tarea.get("pide_url")), (
            f"'{rama}': el catalogo dice pide_url={bool(tarea.get('pide_url'))} "
            f"pero la plantilla {'si' if pide else 'no'} pide la URL en la "
            f"seccion «{tarea['seccion']}»"
        )


def test_la_seccion_extra_existe_en_la_plantilla():
    texto = PLANTILLA_DOCKER.read_text(encoding="utf-8")
    for rama, tarea in rc.CATALOGO.items():
        extra = tarea.get("seccion_extra")
        if extra:
            assert rc.cuerpo_de_seccion(texto, extra) is not None, (
                f"'{rama}': la seccion extra «{extra}» no existe en la plantilla"
            )


# --------------------------------------------------------------------------
# Inyeccion de comandos de Actions por el nombre de un archivo
# --------------------------------------------------------------------------

MALICIOSO = "x\n::error title=Aprobado::entrega aceptada\n.png"


def test_un_nombre_con_saltos_de_linea_no_inyecta_comandos(monkeypatch, capsys):
    """Git acepta `\\n` en un nombre de archivo. La pista «Encontre esto en su
    lugar» imprimia el nombre tal cual, y Actions tomaba la linea
    `::error ...` como una anotacion real."""
    lleno = PLANTILLA.replace(
        "Fecha en que lo terminaste:", "Fecha en que lo terminaste: 2026-09-21"
    ).replace(
        "URL del Statement of Accomplishment:",
        "URL del Statement of Accomplishment: https://www.datacamp.com/x/abc123abc",
    )
    datos = {
        "estudiantes/ana/docker/certificaciones.md": lleno.encode(),
        f"estudiantes/ana/docker/{MALICIOSO}": b"x" * 20_000,
    }
    monkeypatch.setenv("RAMA", "tarea-08-datacamp-intro")
    monkeypatch.setenv("AUTOR", "ana")
    monkeypatch.setenv("PR", "1")
    monkeypatch.setenv("MANTENEDORES", "uumami")
    monkeypatch.setattr(rc, "_pr_json", lambda pr: {
        "head": {"repo": {"full_name": "ana/fdd_o26"}, "sha": "abc"}})
    monkeypatch.setattr(rc, "archivos_del_pr", lambda pr: [
        {"path": p, "status": "added"} for p in datos])
    monkeypatch.setattr(rc, "contenido", lambda repo, sha, ruta: (
        datos[ruta].decode("utf-8", "replace"), len(datos[ruta])))
    assert rc.main() == 1
    salida = capsys.readouterr().out
    assert "x?::error" in salida, "la pista debe mostrar el nombre, neutralizado"
    lineas = [l for l in salida.splitlines() if l.lstrip().startswith("::")]
    token = lineas[0].removeprefix("::stop-commands::")
    assert lineas == [f"::stop-commands::{token}", f"::{token}::"], lineas
