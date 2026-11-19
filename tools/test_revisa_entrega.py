"""Guardas de la revision automatica de entregas.

El script vive en .github/scripts/ y decide si un pull request de estudiante se
acepta. Un falso positivo aqui bloquea a alguien que hizo todo bien, asi que
las reglas se prueban en las dos direcciones.

Varias de estas pruebas existen por un hallazgo concreto de una revision
adversarial; cada una dice cual.
"""
import datetime
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / ".github/scripts/revisa_entrega.py"
WORKFLOW = RAIZ / ".github/workflows/entregas.yml"


def _cargar():
    assert SCRIPT.is_file(), "falta .github/scripts/revisa_entrega.py"
    spec = importlib.util.spec_from_file_location("revisa_entrega", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def mod():
    return _cargar()


@pytest.fixture
def wf():
    """El workflow parseado. `on:` se carga como el booleano True en YAML 1.1."""
    d = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return d


def _paso_de_forma(wf):
    """El paso que corre `revisa_entrega.py`, buscado por lo que corre.

    Antes esto era `steps[-1]`. Dejo de usar la posicion a proposito: el
    workflow ya tiene un segundo paso (`revisa_contenido.py`) y buscar por
    indice hizo que estas pruebas apuntaran al paso equivocado en cuanto se
    agrego. Si manana entra un tercero, esto sigue siendo correcto.
    """
    for paso in wf["jobs"]["revision"]["steps"]:
        if "revisa_entrega.py" in paso.get("run", ""):
            return paso
    raise AssertionError("el workflow ya no corre revisa_entrega.py")


def _f(path, status="added", previa=""):
    return {"path": path, "status": status, "previa": previa}


def _correr(mod, monkeypatch, archivos, autor="ana", rama="tarea-07-git",
            mantenedores="uumami", rama_default="main", declarado=None,
            estricta_desde="", nombre_estricto_desde="", tareas="",
            abierto=None):
    monkeypatch.setenv("AUTOR", autor)
    monkeypatch.setenv("RAMA", rama)
    monkeypatch.setenv("RAMA_DEFAULT", rama_default)
    monkeypatch.setenv("PR", "1")
    monkeypatch.setenv("MANTENEDORES", mantenedores)
    monkeypatch.setenv("BRANCH_ESTRICTA_DESDE", estricta_desde)
    monkeypatch.setenv("BRANCH_NOMBRE_ESTRICTO_DESDE", nombre_estricto_desde)
    monkeypatch.setenv("TAREAS", tareas)
    monkeypatch.setenv("GITHUB_REPOSITORY", "raya-lucaria/fdd_o26")
    monkeypatch.setattr(mod, "archivos_del_pr", lambda pr: archivos)
    n = len(archivos) if declarado is None else declarado
    monkeypatch.setattr(mod, "total_declarado", lambda pr: n)
    # La gracia se mide contra el dia en que se abrio el PR; por omision, hoy.
    monkeypatch.setattr(mod, "fecha_del_pr",
                        lambda pr: abierto or datetime.date.today())
    return mod.main()


# --- las cuatro reglas, en las dos direcciones -------------------------------

def test_entrega_correcta_pasa(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/07_git/bitacora.md"),
                _f("estudiantes/ana/07_git/ejemplo.sh")]
    assert _correr(mod, monkeypatch, archivos) == 0


def test_tocar_la_zona_roja_falla(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/07_git/bitacora.md"),
                _f("codigo/07_git/ejemplo.sh", "modified")]
    assert _correr(mod, monkeypatch, archivos) == 1


def test_tocar_la_carpeta_de_otro_falla(mod, monkeypatch):
    assert _correr(mod, monkeypatch, [_f("estudiantes/beto/07_git/a.md")]) == 1


def test_carpeta_con_mayusculas_distintas_falla(mod, monkeypatch):
    """Los logins de GitHub no distinguen mayusculas; las rutas si."""
    assert _correr(mod, monkeypatch, [_f("estudiantes/Ana/07_git/a.md")]) == 1


def test_basura_agregada_falla(mod, monkeypatch):
    for ruta in ("estudiantes/ana/07_git/.DS_Store",
                 "estudiantes/ana/07_git/__pycache__/x.pyc",
                 "estudiantes/ana/.env"):
        assert _correr(mod, monkeypatch, [_f(ruta)]) == 1, ruta


def test_borrar_basura_no_falla(mod, monkeypatch):
    """El falso positivo clasico: borrar un .DS_Store es la accion correcta."""
    archivos = [_f("estudiantes/ana/07_git/.DS_Store", "removed"),
                _f("estudiantes/ana/07_git/bitacora.md", "modified")]
    assert _correr(mod, monkeypatch, archivos) == 0


def test_pull_request_desde_main_falla(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="main") == 1


def test_la_regla_de_branch_avisa_antes_de_la_fecha_de_corte(mod, monkeypatch, capsys):
    """El grupo ya tenia pull requests abiertos desde main cuando la regla
    entro, asi que hay un periodo de gracia con fecha explicita."""
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="main",
                   estricta_desde="2099-01-01") == 0
    salida = capsys.readouterr().out
    assert "AVISO" in salida and "2099-01-01" in salida


def test_la_regla_de_branch_rechaza_pasada_la_fecha(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="main",
                   estricta_desde="2000-01-01") == 1


def test_sin_fecha_la_regla_es_estricta(mod, monkeypatch):
    """Borrar la variable del workflow endurece la regla, no la apaga."""
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="main",
                   estricta_desde="") == 1


def test_el_aviso_no_tapa_los_otros_fallos(mod, monkeypatch):
    """Estar en periodo de gracia no debe aprobar una entrega mal ubicada."""
    archivos = [_f("codigo/07_git/ejemplo.sh", "modified")]
    assert _correr(mod, monkeypatch, archivos, rama="main",
                   estricta_desde="2099-01-01") == 1


def test_el_workflow_declara_la_fecha_de_corte(wf):
    env = _paso_de_forma(wf)["env"]
    assert "BRANCH_ESTRICTA_DESDE" in env, (
        "sin la fecha la regla es estricta; si eso es lo que se quiere, "
        "borra tambien esta prueba"
    )


def test_el_workflow_declara_la_fecha_de_corte_del_nombre_de_branch(wf):
    """Es una variable propia, distinta de BRANCH_ESTRICTA_DESDE: las dos
    fechas se tienen que poder mover por separado."""
    env = _paso_de_forma(wf)["env"]
    assert "BRANCH_NOMBRE_ESTRICTO_DESDE" in env, (
        "sin la fecha la regla del nombre de la branch es estricta; si eso "
        "es lo que se quiere, borra tambien esta prueba"
    )
    assert env["BRANCH_NOMBRE_ESTRICTO_DESDE"] != env["BRANCH_ESTRICTA_DESDE"], (
        "las dos fechas de gracia deben poder moverse por separado"
    )


def test_el_mantenedor_queda_exento(mod, monkeypatch):
    archivos = [_f("course/7_git_y_github/2_github/1_github_en_corto.md", "modified"),
                _f("codigo/07_git/ejemplo.sh", "modified")]
    assert _correr(mod, monkeypatch, archivos, autor="uumami", rama="main") == 0


def test_un_archivo_llamado_env_no_es_dotenv(mod, monkeypatch):
    """`.env` es basura; `env.md` o `mi.env.example` no lo son."""
    for ok in ("estudiantes/ana/07_git/env.md",
               "estudiantes/ana/07_git/mi.env.example",
               "estudiantes/ana/07_git/notas__pycache__.txt",
               "estudiantes/ana/07_git/como-borrar-DS_Store.md"):
        assert _correr(mod, monkeypatch, [_f(ok)]) == 0, ok


# --- regla 5: el nombre de la branch ----------------------------------------

MAPA = ("tarea-08-datacamp-intro=docker,"
        "tarea-08-imagen=08_contenedores,"
        "tarea-08-datacamp-inter-1=docker,"
        "tarea-08-datacamp-inter-2=docker")


def test_branch_sin_nombre_de_tarea_falla(mod, monkeypatch):
    """Hoy una branch llamada 'x' pasa en verde: nadie mira el nombre."""
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="x", tareas=MAPA) == 1


def test_branch_con_nombre_de_tarea_pasa(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 0


def test_el_mensaje_de_branch_lista_los_nombres_validos(mod, monkeypatch, capsys):
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    _correr(mod, monkeypatch, archivos, rama="mi-branch", tareas=MAPA)
    salida = capsys.readouterr().out
    assert "tarea-08-imagen" in salida


def test_la_branch_de_la_unidad_7_sigue_pasando(mod, monkeypatch):
    """No romper hacia atras: tarea-07-git casa con el patron."""
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="tarea-07-git") == 0


def test_desde_main_no_reporta_dos_veces_la_branch(mod, monkeypatch, capsys):
    """La regla 1 ya cubre main; la 5 no debe duplicar el fallo."""
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    _correr(mod, monkeypatch, archivos, rama="main", tareas=MAPA)
    salida = capsys.readouterr().out
    assert salida.count("BRANCH:") == 1


def test_el_mensaje_separa_la_forma_del_catalogo(mod, monkeypatch, capsys):
    """Sin mapa (las tareas de la unidad 8 todavia no existen), el mensaje no
    puede prometer un nombre exacto: cae a la forma generica tarea-NN-nombre,
    no a una lista vacia."""
    archivos = [_f("estudiantes/ana/x/a.md")]
    _correr(mod, monkeypatch, archivos, rama="mi-branch", tareas="")
    salida = capsys.readouterr().out
    assert "tarea-NN-nombre" in salida


# --- regla 5: periodo de gracia del nombre de la branch ----------------------

def test_la_regla_de_nombre_avisa_antes_de_la_fecha_de_corte(mod, monkeypatch, capsys):
    """A las tareas de la unidad 7 nunca se les pidio un nombre de branch:
    hasta la fecha de corte, un nombre inventado solo avisa."""
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="mi-branch", tareas=MAPA,
                   nombre_estricto_desde="2099-01-01") == 0
    salida = capsys.readouterr().out
    assert "AVISO" in salida and "2099-01-01" in salida


def test_la_regla_de_nombre_rechaza_pasada_la_fecha(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="mi-branch", tareas=MAPA,
                   nombre_estricto_desde="2000-01-01") == 1


def test_sin_fecha_la_regla_de_nombre_es_estricta(mod, monkeypatch):
    """Borrar la variable del workflow endurece la regla, no la apaga."""
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="mi-branch", tareas=MAPA,
                   nombre_estricto_desde="") == 1


def test_las_dos_fechas_de_gracia_son_independientes(mod, monkeypatch, capsys):
    """BRANCH_ESTRICTA_DESDE gobierna la regla 1 (no entregar desde main) y
    BRANCH_NOMBRE_ESTRICTO_DESDE gobierna la regla 5 (nombre de la branch).
    Mover una no debe mover la otra."""
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]

    # Desde main: la regla 1 esta en gracia (pasa con aviso) sin importar que
    # la fecha de la regla 5 ya haya pasado, porque desde la branch default
    # la regla 5 ni se evalua.
    assert _correr(mod, monkeypatch, archivos, rama="main", tareas=MAPA,
                   estricta_desde="2099-01-01",
                   nombre_estricto_desde="2000-01-01") == 0

    # Con una branch propia sin nombre de tarea: la regla 5 esta en gracia
    # (pasa con aviso) sin importar que la fecha de la regla 1 ya haya
    # pasado, porque esa branch no es la default.
    assert _correr(mod, monkeypatch, archivos, rama="mi-branch", tareas=MAPA,
                   estricta_desde="2000-01-01",
                   nombre_estricto_desde="2099-01-01") == 0


def test_hoy_una_branch_inventada_solo_avisa(mod, monkeypatch, capsys):
    """La comprobacion de la revision final: con la fecha de hoy
    (2026-09-15), una branch inventada que toca una sola carpeta propia pasa
    con aviso, no con fallo. BRANCH_NOMBRE_ESTRICTO_DESDE = 2026-09-22, tal
    como lo declara entregas.yml."""
    # «Hoy» se congela: con el reloj real esta prueba se volvió roja el 22,
    # justo el día en que la regla dejó de estar en gracia.
    _congela_hoy(monkeypatch, datetime.date(2026, 9, 15))
    archivos = [_f("estudiantes/ana/docker/certificaciones.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="entrega-datacamp-git-intermedio", tareas=MAPA,
                   nombre_estricto_desde="2026-09-22") == 0
    salida = capsys.readouterr().out
    assert "AVISO" in salida


def test_desde_el_22_la_misma_branch_inventada_falla(mod, monkeypatch):
    """El otro lado de la fecha: vencida la gracia, la regla 5 bloquea."""
    _congela_hoy(monkeypatch, datetime.date(2026, 9, 22))
    archivos = [_f("estudiantes/ana/docker/certificaciones.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="entrega-datacamp-git-intermedio", tareas=MAPA,
                   nombre_estricto_desde="2026-09-22") == 1


def _congela_hoy(monkeypatch, dia):
    class _Fecha(datetime.date):
        @classmethod
        def today(cls):
            return dia
    monkeypatch.setattr(datetime, "date", _Fecha)


# --- regla 6: una entrega, una carpeta --------------------------------------

def test_dos_carpetas_en_un_pull_request_falla(mod, monkeypatch):
    """Las dos entregas del 22 en una sola branch salen hoy en verde."""
    archivos = [_f("estudiantes/ana/docker/certificaciones.md"),
                _f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 1


def test_una_sola_carpeta_pasa(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md"),
                _f("estudiantes/ana/08_contenedores/roto/Dockerfile")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 0


def test_archivo_suelto_en_la_raiz_no_cuenta_como_carpeta(mod, monkeypatch):
    """El .gitkeep de la primera entrega no debe invalidar nada."""
    archivos = [_f("estudiantes/ana/.gitkeep"),
                _f("estudiantes/ana/docker/certificaciones.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-datacamp-intro", tareas=MAPA) == 0


def test_la_carpeta_no_corresponde_a_la_branch_falla(mod, monkeypatch):
    """Branch de la imagen tocando la carpeta de DataCamp."""
    archivos = [_f("estudiantes/ana/docker/certificaciones.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 1


def test_el_mensaje_dice_que_carpeta_esperaba(mod, monkeypatch, capsys):
    archivos = [_f("estudiantes/ana/docker/certificaciones.md")]
    _correr(mod, monkeypatch, archivos, rama="tarea-08-imagen", tareas=MAPA)
    salida = capsys.readouterr().out
    assert "08_contenedores" in salida


def test_el_mensaje_de_carpeta_no_correspondida_explica_el_movimiento(
    mod, monkeypatch, capsys
):
    """Un archivo movido de una carpeta a otra sale rc=1 o rc=0 segun la
    heuristica de renames de GitHub, y eso no lo controla el alumno; el
    mensaje dice por que cuenta como dos carpetas y donde investigarlo, sin
    darle la receta."""
    archivos = [_f("estudiantes/ana/docker/certificaciones.md")]
    _correr(mod, monkeypatch, archivos, rama="tarea-08-imagen", tareas=MAPA)
    salida = capsys.readouterr().out
    assert "cuenta como tocar las dos" in salida
    assert "Donde investigar: " + mod.FLUJO in salida


def test_el_mensaje_de_dos_carpetas_sin_mapa_explica_el_movimiento(
    mod, monkeypatch, capsys
):
    """La otra mitad del mensaje de CARPETA: sin branch en el mapa, la
    variante que dispara es la de 'toca mas de una carpeta'."""
    archivos = [_f("estudiantes/ana/docker/certificaciones.md"),
                _f("estudiantes/ana/08_contenedores/bitacora.md")]
    _correr(mod, monkeypatch, archivos, rama="tarea-07-git")
    salida = capsys.readouterr().out
    assert "cuenta como tocar las dos" in salida
    assert "Donde investigar: " + mod.FLUJO in salida


def test_sin_mapa_basta_con_una_carpeta(mod, monkeypatch):
    """Una branch que el mapa no conoce solo tiene que tocar una carpeta."""
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="tarea-07-git") == 0


def test_un_rename_entre_carpetas_falla(mod, monkeypatch):
    """Mover de una entrega a otra toca dos carpetas y cuenta como dos."""
    archivos = [_f("estudiantes/ana/08_contenedores/notas.md",
                   status="renamed", previa="estudiantes/ana/docker/notas.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 1


def test_borrar_en_dos_carpetas_pasa(mod, monkeypatch):
    """Borrar es lo correcto: la regla de basura ya trata los borrados asi
    (ver test_borrar_basura_no_falla), y la de carpeta no debe penalizar a
    quien limpia sobras en docker/ y en 08_contenedores/ en el mismo pull
    request."""
    archivos = [_f("estudiantes/ana/docker/sobra.md", status="removed"),
                _f("estudiantes/ana/08_contenedores/vieja.md", status="removed")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 0


def test_un_valor_del_mapa_con_mas_de_un_nivel_se_normaliza(mod, monkeypatch):
    """subcarpeta() solo devuelve el primer segmento; si un futuro
    tarea-09-x=09_sql/ejercicios entrara tal cual al mapa, la comparacion no
    cerraria nunca y rechazaria toda entrega correcta de esa tarea."""
    tareas = "tarea-09-x=09_sql/ejercicios"
    archivos = [_f("estudiantes/ana/09_sql/ejercicios/consulta.sql")]
    assert _correr(mod, monkeypatch, archivos, rama="tarea-09-x",
                   tareas=tareas) == 0


# --- hallazgos de la revision adversarial ------------------------------------

def test_rename_que_saca_un_archivo_de_la_zona_roja_falla(mod, monkeypatch):
    """La API sólo pone la ruta destino en `filename`. Sin `previous_filename`,
    un git mv de course/ a la propia carpeta pasaba en verde y el merge
    borraba el archivo del curso."""
    archivos = [_f("estudiantes/ana/07_git/robado.md", "renamed",
                   previa="course/2_pipeline_de_datos/4_cuando_se_rompe.md")]
    assert _correr(mod, monkeypatch, archivos) == 1


def test_rename_dentro_de_la_propia_carpeta_pasa(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/07_git/nuevo.md", "renamed",
                   previa="estudiantes/ana/07_git/viejo.md")]
    assert _correr(mod, monkeypatch, archivos) == 0


def test_la_rama_default_no_es_siempre_main(mod, monkeypatch):
    """Un fork con rama default `master` entregaba desde su default sin que
    nadie se enterara."""
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="master", rama_default="master") == 1
    # y una branch de tarea sigue pasando aunque la default sea master
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-07-git", rama_default="master") == 0


def test_variantes_de_env_son_basura(mod, monkeypatch):
    """En un repositorio publico, .env.local con una llave es el caso grave."""
    for ruta in ("estudiantes/ana/.env.local", "estudiantes/ana/.env.production",
                 "estudiantes/ana/.envrc", "estudiantes/ana/id_rsa",
                 "estudiantes/ana/llave.pem"):
        assert _correr(mod, monkeypatch, [_f(ruta)]) == 1, ruta


def test_pull_request_vacio_no_es_una_entrega(mod, monkeypatch):
    assert _correr(mod, monkeypatch, []) == 1


def test_api_truncada_falla_cerrado(mod, monkeypatch):
    """La API corta en 3000 archivos. Si lo bajado no coincide con lo declarado,
    no podemos afirmar que revisamos la entrega completa."""
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, declarado=3001) == 1


def test_archivo_llamado_estudiantes_ana_va_a_ubicacion(mod, monkeypatch):
    """Antes producia el mensaje absurdo 'Esperaba estudiantes/ana/, encontre
    estudiantes/ana/'."""
    assert _correr(mod, monkeypatch, [_f("estudiantes/ana")]) == 1


def test_el_truncado_dice_cuantos_faltan(mod, monkeypatch, capsys):
    archivos = [_f(f"codigo/f{i}.md", "modified") for i in range(50)]
    assert _correr(mod, monkeypatch, archivos) == 1
    assert "y 30 mas." in capsys.readouterr().out


def test_prefijo_de_login_no_pasa(mod, monkeypatch):
    assert _correr(mod, monkeypatch, [_f("estudiantes/ana2/x.md")]) == 1
    assert _correr(mod, monkeypatch, [_f("estudiantes/ana/x.md")],
                   autor="ana2") == 1


# --- el workflow -------------------------------------------------------------

def test_el_workflow_usa_pull_request_target(wf):
    """Con `pull_request` el propio pull request reescribe este workflow y el
    script que lo juzga, y se aprueba solo."""
    disparador = wf.get("on", wf.get(True))
    assert list(disparador) == ["pull_request_target"], (
        "el disparador tiene que ser pull_request_target; con pull_request "
        "GitHub corre los archivos del fork"
    )


def test_el_checkout_va_fijado_a_la_base(wf):
    """`pull_request_target` sin esto trae el arbol del fork de todos modos."""
    pasos = wf["jobs"]["revision"]["steps"]
    checkout = [p for p in pasos if str(p.get("uses", "")).startswith("actions/checkout")]
    assert len(checkout) == 1, "se espera exactamente un checkout"
    assert checkout[0]["with"]["ref"] == "${{ github.event.pull_request.base.sha }}"
    assert checkout[0]["with"]["persist-credentials"] is False


def test_el_workflow_no_ejecuta_nada_del_pull_request(wf):
    """La regla que hace seguro a pull_request_target."""
    for paso in wf["jobs"]["revision"]["steps"]:
        run = paso.get("run", "")
        assert "head" not in run, f"un run no debe tocar el head del PR: {run}"


def test_permisos_de_solo_lectura(wf):
    assert wf["permissions"] == {"contents": "read", "pull-requests": "read"}


def test_el_workflow_exporta_lo_que_el_script_lee(wf, mod):
    env = _paso_de_forma(wf)["env"]
    for clave in ("GH_TOKEN", "PR", "AUTOR", "RAMA", "RAMA_DEFAULT", "MANTENEDORES",
                  "TAREAS"):
        assert clave in env, f"el workflow no exporta {clave}"


def test_los_bots_quedan_exentos(wf):
    assert "'Bot'" in wf["jobs"]["revision"]["if"]


# --- la gracia se mide contra la apertura del PR, no contra hoy -------------

def test_un_pr_abierto_en_la_gracia_sigue_en_gracia_al_corregir(mod, monkeypatch, capsys):
    """Hallazgo de la revision del 2026-09-22: con la fecha de hoy, un PR de
    la unidad 7 abierto el 17 se volvia rojo en cuanto el alumno hacia push
    a la misma branch para corregir, que es lo que se le pide."""
    _congela_hoy(monkeypatch, datetime.date(2026, 9, 30))
    archivos = [_f("estudiantes/ana/github/certificaciones.md")]
    assert _correr(mod, monkeypatch, archivos, rama="07_git_intermedio",
                   tareas=MAPA, nombre_estricto_desde="2026-09-22",
                   abierto=datetime.date(2026, 9, 17)) == 0
    assert "AVISO" in capsys.readouterr().out


def test_un_pr_abierto_despues_del_corte_falla_y_pide_branch_nueva(mod, monkeypatch, capsys):
    """Y el cierre no dice «no abras otro»: el nombre no se arregla ahi."""
    archivos = [_f("estudiantes/ana/github/certificaciones.md")]
    assert _correr(mod, monkeypatch, archivos, rama="07_git_intermedio",
                   tareas=MAPA, nombre_estricto_desde="2026-09-22",
                   abierto=datetime.date(2026, 9, 23)) == 1
    salida = capsys.readouterr().out
    assert "branch nueva" in salida and "No abras otro" not in salida



# --- inyeccion de comandos de Actions por el nombre de un archivo ------------

MALICIOSO = "x\n::error title=Aprobado::entrega aceptada\n.png"


def _comandos_colados(salida):
    """Lineas que Actions interpretaria como comando, fuera del par
    `::stop-commands::<token>` ... `::<token>::` que abre y cierra main()."""
    lineas = [l for l in salida.splitlines() if l.lstrip().startswith("::")]
    assert lineas and lineas[0].startswith("::stop-commands::")
    token = lineas[0].split("::")[2]
    assert lineas[-1].strip() == f"::{token}::"
    return lineas[1:-1]


@pytest.mark.parametrize("ruta", [
    f"codigo/{MALICIOSO}",                              # UBICACION
    f"estudiantes/ana/07_git/{MALICIOSO}/.DS_Store",    # BASURA
    f"estudiantes/Ana\n::error::x/07_git/a.md",         # fuera, con salto en el duenio
])
def test_un_nombre_con_saltos_de_linea_no_inyecta_comandos(mod, monkeypatch, capsys, ruta):
    """Git acepta `\\n` en un nombre de archivo. Antes, la lista de archivos
    del mensaje imprimia una linea `::error ...` que Actions tomaba como una
    anotacion real. Este problema existia antes de las fichas."""
    assert _correr(mod, monkeypatch, [_f(ruta)]) == 1
    assert _comandos_colados(capsys.readouterr().out) == []


def test_dos_carpetas_con_salto_de_linea_no_inyectan(mod, monkeypatch, capsys):
    archivos = [_f("estudiantes/ana/docker/a.md"),
                _f("estudiantes/ana/x\n::warning::y/b.md")]
    assert _correr(mod, monkeypatch, archivos) == 1
    assert _comandos_colados(capsys.readouterr().out) == []


# --- los mensajes dicen que, por que y donde; nunca el como -------------------

def _literales_de_mensaje(ruta):
    """Las cadenas del script que se ejecutan, sin comentarios ni docstrings."""
    import re
    texto = re.sub(r'"""(.*?)"""', "", ruta.read_text(encoding="utf-8"), flags=re.S)
    codigo = "\n".join(l.split("#", 1)[0] for l in texto.splitlines())
    return " ".join(re.findall(r'"([^"\n]*)"', codigo))


# Subcomandos concretos, no la palabra "git": decir que "para git son dos
# carpetas distintas" explica el por que, no da el como.
RECETAS = ("Arreglo", "haz push", "Commitea", "Ponte al dia", "vuelve a commitear",
           "rm --cached", "switch -c") + tuple(
    f"git {c}" for c in ("switch", "mv", "restore", "rm", "add", "commit",
                         "push", "checkout", "fetch", "merge", "reset"))


def test_los_mensajes_no_dan_el_como():
    """Regla del profesor: jamas como arreglarlo. Ni comandos ni recetas."""
    literales = _literales_de_mensaje(SCRIPT)
    for r in RECETAS:
        assert r not in literales, f"revisa_entrega.py todavia dice '{r}'"


@pytest.mark.parametrize("archivos, rama", [
    ([_f("codigo/x.md", "modified")], "tarea-07-git"),                 # UBICACION
    ([_f("estudiantes/Ana/07_git/a.md")], "tarea-07-git"),             # NOMBRE
    ([_f("estudiantes/ana/07_git/.DS_Store")], "tarea-07-git"),        # BASURA
    ([_f("estudiantes/ana/07_git/a.md")], "main"),                     # BRANCH
    ([_f("estudiantes/ana/07_git/a.md")], "mi-branch"),                # BRANCH
    ([_f("estudiantes/ana/docker/a.md"),
      _f("estudiantes/ana/07_git/b.md")], "tarea-07-git"),             # CARPETA
])
def test_cada_fallo_dice_donde_investigar(mod, monkeypatch, capsys, archivos, rama):
    assert _correr(mod, monkeypatch, archivos, rama=rama) == 1
    salida = capsys.readouterr().out
    bloques = [b for b in salida.split("\n- ")[1:]]
    assert bloques
    for b in bloques:
        assert "Donde investigar: " in b, b[:80]
