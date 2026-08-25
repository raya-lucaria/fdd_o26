"""Guardas ejecutables para los ejemplos de seguridad de la Unidad 5."""

from pathlib import Path
import re
import subprocess


RAIZ = Path(__file__).resolve().parent.parent
TERMINAL_ARCHIVOS = (
    RAIZ / "course/5_terminal_y_bash/1_terminal/2_archivos_y_comandos/0_index.md"
)
TERMINAL_FLUJOS = (
    RAIZ / "course/5_terminal_y_bash/1_terminal/3_flujos_procesos_y_herramientas/0_index.md"
)
BASH_LECTURA = (
    RAIZ / "course/5_terminal_y_bash/2_bash_scripting/1_como_lee_bash/0_index.md"
)


def bloque(ruta: Path, titulo: str) -> str:
    texto = ruta.read_text(encoding="utf-8")
    patron = rf'title="{re.escape(titulo)}".*?```bash\n(.*?)```'
    encontrado = re.search(patron, texto, re.S)
    assert encontrado, f"no se encontro el ejemplo {titulo!r} en {ruta}"
    return encontrado.group(1)


def bloque_despues_de_encabezado(ruta: Path, encabezado: str) -> str:
    texto = ruta.read_text(encoding="utf-8")
    patron = rf"^## {re.escape(encabezado)}\n.*?```bash\n(.*?)```"
    encontrado = re.search(patron, texto, re.S | re.M)
    assert encontrado, f"no se encontro el bloque de {encabezado!r} en {ruta}"
    return encontrado.group(1)


def ejecutar(script: str, home: Path) -> subprocess.CompletedProcess[str]:
    entorno = {"HOME": str(home), "PATH": "/usr/bin:/bin"}
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        check=False,
        cwd=home,
        env=entorno,
        text=True,
    )


def test_el_ejemplo_crea_un_archivo_cuyo_nombre_empieza_con_guion(tmp_path):
    """Evita redirigir accidentalmente stdout al archivo literal ``--``."""
    resultado = ejecutar(
        bloque_despues_de_encabezado(TERMINAL_ARCHIVOS, "Opciones y ayuda"),
        tmp_path,
    )
    archivo = tmp_path / "fdd/terminal-lab/-borrador.txt"

    assert resultado.returncode == 0, resultado.stderr
    assert archivo.read_text(encoding="utf-8") == "archivo que empieza con guion\n"
    assert not (archivo.parent / "--").exists()


def test_el_ejemplo_de_globbing_muestra_el_argumento_doble_guion(tmp_path):
    """El resultado visible distingue el marcador ``--`` de los nombres expandidos."""
    resultado = ejecutar(
        bloque_despues_de_encabezado(
            BASH_LECTURA,
            "Globbing: Bash busca nombres antes de llamar al programa",
        ),
        tmp_path,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.splitlines() == [
        "<-->",
        "<nota de hoy.txt>",
        "<resumen.txt>",
    ]


def test_el_enlace_de_bandit_apunta_al_objeto_oficial():
    """Evita que la estación final dirija a la portada de la unidad."""
    texto = TERMINAL_FLUJOS.read_text(encoding="utf-8")

    assert "[[bandit-terminal|tarea oficial Bandit]]" in texto


def test_el_estado_de_la_tuberia_usa_pipefail_antes_de_consultar_dollar_question():
    """Una falla en ``sort`` o ``uniq`` no debe parecer éxito solo porque ``tee`` terminó."""
    ejemplo = bloque(TERMINAL_FLUJOS, "Transforma una entrada preparada")

    assert re.search(
        r"set -o pipefail\nsort nombres\.txt \| uniq -c \| tee reportes/conteos\.txt\nestado=\$\?",
        ejemplo,
    )


def test_copiar_y_mover_terminan_las_opciones_antes_de_las_rutas():
    """Los ejemplos de mutación tratan sus rutas como datos, no como opciones."""
    ejemplo = bloque(TERMINAL_ARCHIVOS, "Opera sobre un laboratorio recién creado")

    assert "cp -- nombres.txt reportes/nombres-copia.txt" in ejemplo
    assert "mv -- errores.txt reportes/errores.txt" in ejemplo
