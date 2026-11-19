"""Guardas del codigo de la unidad 9 que copian los alumnos.

quien_soy.py es la herramienta de diagnostico de todos los labs: tiene que
correr con la biblioteca estandar sola, en cualquier Python 3.9+, dentro y
fuera de un ambiente, con rich instalado o no.
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AMB = RAIZ / "codigo/09_python/ambientes"
ROTULOS = ("python que corre", "versión", "sys.prefix",
           "¿en un ambiente?", "'python' en PATH", "rich")


def _correr(archivo):
    return subprocess.run([sys.executable, str(AMB / archivo)],
                          capture_output=True, text=True, timeout=30)


def test_quien_soy_corre_con_la_biblioteca_estandar():
    r = _correr("quien_soy.py")
    assert r.returncode == 0, r.stderr
    lineas = r.stdout.splitlines()
    assert [l.split(":")[0].strip() for l in lineas] == list(ROTULOS)


def test_quien_soy_dice_si_esta_en_un_ambiente():
    r = _correr("quien_soy.py")
    en = sys.prefix != sys.base_prefix
    assert ("¿en un ambiente?  : sí" in r.stdout) == en


def test_hola_solo_importa_rich():
    texto = (AMB / "hola.py").read_text(encoding="utf-8")
    imports = [l for l in texto.splitlines() if l.startswith(("import ", "from "))]
    assert imports == ["from rich import print"]


def test_el_script_autonomo_declara_sus_dependencias_en_linea():
    texto = (AMB / "script_autonomo.py").read_text(encoding="utf-8")
    assert texto.startswith("# /// script\n")
    cabecera = texto.split("# ///\n", 1)[0]
    assert '# dependencies = ["rich"]' in cabecera


def test_requirements_fija_rich_con_doble_igual():
    lineas = [l for l in (AMB / "requirements.txt").read_text().splitlines()
              if l.strip() and not l.startswith("#")]
    assert len(lineas) == 1 and lineas[0].startswith("rich==")


def test_codigo_readme_lista_09_python():
    assert "`09_python/`" in (RAIZ / "codigo/README.md").read_text(encoding="utf-8")


UVD = RAIZ / "codigo/09_python/uv_docker"


def test_la_plantilla_trae_los_tres_huecos_y_la_fila_por_llenar():
    df = (UVD / "Dockerfile").read_text(encoding="utf-8")
    assert df.count("HUECO") == 3
    assert "<tu fila>" in (UVD / "reporte.py").read_text(encoding="utf-8")


def test_la_plantilla_no_trae_lock_ni_venv():
    assert not (UVD / "uv.lock").exists() and not (UVD / ".venv").exists()


def test_dockerignore_de_la_plantilla_no_trae_venv():
    """Agregarlo es parte de la tarea."""
    lineas = (UVD / ".dockerignore").read_text(encoding="utf-8").splitlines()
    assert not any(l.strip().strip("/") == ".venv" for l in lineas)


def test_reporte_es_python_valido():
    import ast
    ast.parse((UVD / "reporte.py").read_text(encoding="utf-8"))


def test_la_imagen_de_uv_esta_fijada_a_una_version_menor():
    df = (UVD / "Dockerfile").read_text(encoding="utf-8")
    assert "ghcr.io/astral-sh/uv:0.12 " in df, "fija la imagen de uv: latest cambia sin aviso"


def test_el_readme_manda_los_labs_a_la_carpeta_del_alumno():
    t = (RAIZ / "codigo/09_python/README.md").read_text(encoding="utf-8")
    assert "lab-ambientes" not in t and "fuera del repo" not in t.lower()
    assert "estudiantes/$GHUSER/09_python/" in t


def test_el_readme_usa_el_marcador_del_fork():
    t = (RAIZ / "codigo/09_python/README.md").read_text(encoding="utf-8")
    assert "~/fdd/fdd_o26" not in t and "{tu_fork_de_la_clase}" in t
