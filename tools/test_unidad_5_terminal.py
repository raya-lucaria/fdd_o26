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


def test_archivos_construye_una_nota_antes_de_copiar_o_borrar():
    """Evita volver a presentar operaciones destructivas antes de crear y leer."""
    texto = TERMINAL_ARCHIVOS.read_text(encoding="utf-8")

    posiciones = [texto.index(token) for token in ("`touch`", "`cp -i`", "`rm -i`")]
    assert posiciones == sorted(posiciones)
    assert all(
        token in texto
        for token in ("`echo`", "`>`", "`>>`", "`cat`", "`head`", "`tail`")
    )


def test_la_primera_mision_crea_una_nota_reproducible(tmp_path):
    """Un HOME nuevo basta para producir la primera nota con contenido verificable."""
    resultado = ejecutar(
        bloque_despues_de_encabezado(TERMINAL_ARCHIVOS, "Misión 1: crea una nota"),
        tmp_path,
    )
    nota = tmp_path / "fdd/terminal-lab/notas/hoy/lista.txt"

    assert resultado.returncode == 0, resultado.stderr
    assert nota.read_text(encoding="utf-8") == "practicar rutas\n"


def test_el_ejemplo_crea_un_archivo_cuyo_nombre_empieza_con_guion(tmp_path):
    """Evita redirigir accidentalmente stdout al archivo literal ``--``."""
    resultado = ejecutar(
        bloque_despues_de_encabezado(TERMINAL_ARCHIVOS, "Opciones y ayuda"),
        tmp_path,
    )
    archivo = tmp_path / "fdd/terminal-lab/notas/hoy/-borrador.txt"

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


def test_la_pregunta_de_globbing_usa_el_mismo_formato_que_su_respuesta():
    """La predicción debe mostrar los delimitadores que luego explica."""
    texto = BASH_LECTURA.read_text(encoding="utf-8")

    problema = re.search(
        r'::: problem \{#espacios-y-expansion.*?```bash\n(.*?)```', texto, re.S
    )
    assert problema
    assert "printf '<%s>\\n' -- *" in problema.group(1)


def test_la_estacion_dirige_a_bandit_sin_un_wikilink_de_objeto_oficial():
    """Los objetos oficiales no son páginas y Raya no puede resolverlos como wikilinks."""
    texto = TERMINAL_FLUJOS.read_text(encoding="utf-8")

    assert "[[bandit-terminal" not in texto
    assert "https://overthewire.org/wargames/bandit/" in texto


def test_pipefail_esta_acotado_a_la_tuberia_opcional():
    """La ampliación activa pipefail antes de la tubería y lo apaga después."""
    ejemplo = bloque(TERMINAL_FLUJOS, "Transforma una entrada preparada")

    assert re.search(
        r'set -o pipefail\nsort "\$HOME/fdd/terminal-lab/nombres\.txt" '
        r'\| uniq -c \| tee "\$HOME/fdd/terminal-lab/reportes/conteos\.txt"\n'
        r"set \+o pipefail",
        ejemplo,
    )


def test_copiar_y_mover_terminan_las_opciones_antes_de_las_rutas():
    """Los ejemplos de mutación tratan sus rutas como datos, no como opciones."""
    ejemplo = bloque_despues_de_encabezado(
        TERMINAL_ARCHIVOS, "Misión 5: copia y renombra"
    )

    assert "cp -i -- lista.txt lista-copia.txt" in ejemplo
    assert "mv -i -- lista-copia.txt lista-renombrada.txt" in ejemplo


def test_borrado_principiante_no_es_recursivo_ni_elevado():
    """La primera práctica de borrado se limita a un archivo y una carpeta vacía."""
    texto = TERMINAL_ARCHIVOS.read_text(encoding="utf-8")

    assert "rm -r" not in texto
    assert "rm -f" not in texto
    assert "sudo rm" not in texto
