"""Guardas focales para la cobertura esencial de Terminal y Bash."""

from pathlib import Path
import re
import subprocess

import yaml


ROOT = Path(__file__).resolve().parent.parent
UNIT = ROOT / "course/5_terminal_y_bash"
ORIENTATION = UNIT / "1_terminal/1_entrar_y_orientarte/0_index.md"
FLOWS = UNIT / "1_terminal/3_flujos_procesos_y_herramientas/0_index.md"
TERMINAL_INDEX = UNIT / "1_terminal/0_index.md"
BASH_INDEX = UNIT / "2_bash_scripting/0_index.md"
SCRIPT = UNIT / "2_bash_scripting/3_de_pasos_a_script/0_index.md"
BANDIT_ASSIGNMENT = UNIT / "_official/assignments/1_bandit.yaml"
INSTALL_ASSIGNMENT = (
    ROOT
    / "course/4_software_libre_y_sistemas_operativos/_official/assignments/1_instalar_linux.yaml"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def bash_block_with_title(path: Path, title: str) -> str:
    page = read(path)
    match = re.search(
        rf'title="{re.escape(title)}".*?```bash\n(.*?)```', page, re.S
    )
    assert match, f"No se encontró el bloque {title!r}"
    return match.group(1)


def run_bash(script: str, home: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", script],
        cwd=home,
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        check=False,
        text=True,
    )


def test_orientation_covers_shell_history_and_daily_shortcuts():
    """Catches dropping the historical context or daily interaction basics."""
    page = read(ORIENTATION)
    for name in ("Thompson", "Bourne", "GNU", "Bash"):
        assert name in page
    for shortcut in ("Ctrl-R", "Ctrl-D", "Ctrl-Shift-C", "Cmd-C"):
        assert shortcut in page
    for platform in ("Ubuntu", "WSL2", "macOS"):
        assert platform in page


def test_orientacion_guia_comandos_en_orden_sin_crear_archivos():
    texto = read(ORIENTATION)
    secuencia = ("`pwd`", "`ls`", "`mkdir -p`", "`cd`", "**ruta absoluta**")
    posiciones = [texto.index(token) for token in secuencia]
    assert posiciones == sorted(posiciones)
    assert "`touch`" not in texto


def test_orientacion_distingue_tokens_exactos_de_ruta():
    texto = read(ORIENTATION)
    assert all(token in texto for token in ("`~`", "`/`", "`.`", "`..`", "`...`"))
    assert "`...` no es una ruta ni una sintaxis especial en Bash" in texto


def test_orientacion_explica_ls_y_mantiene_ritmo_de_mision():
    texto = read(ORIENTATION)
    assert "`ls` muestra el contenido de la carpeta actual; no imprime su nombre" in texto
    assert "Haz:" in texto and "Deberías ver:" in texto and "Pausa:" in texto


def test_orientacion_mision_tres_fija_directorio_antes_de_listar():
    texto = read(ORIENTATION)
    mision = texto.split("## Misión 3:", 1)[1].split("::: definition", 1)[0]
    bloque = mision.split("```bash\n", 1)[1].split("\n```", 1)[0]
    secuencia = (
        "mkdir -p ~/fdd/terminal-lab/notas/hoy",
        "cd ~/fdd/terminal-lab/notas/hoy",
        "ls -la",
    )
    posiciones = [bloque.find(paso) for paso in secuencia]
    assert all(posicion >= 0 for posicion in posiciones)
    assert posiciones == sorted(posiciones)


def test_route_is_scannable_and_includes_daily_tools_by_platform():
    """Catches losing the compact action/check/pause rhythm or tool routes."""
    route = read(TERMINAL_INDEX) + read(BASH_INDEX)
    for label in ("Haz", "Comprueba", "Pausa"):
        assert label in route
    for command in ("history", "clear", "date", "ps", "htop", "fastfetch"):
        assert f"`{command}`" in route
    assert "sudo apt install htop fastfetch" in route
    assert "brew install htop fastfetch" in route


def test_script_uses_unset_variable_guard_without_teaching_heredoc():
    """Catches reintroducing a second shell construct before the first script."""
    page = read(SCRIPT)
    assert "set -u" in page
    assert "<<'EOF'" not in page
    assert "heredoc" not in page.lower()


def test_install_assignment_uses_fastfetch_and_no_old_terminal_video():
    """Catches restoring obsolete evidence or duplicated terminal preparation."""
    assignment = yaml.safe_load(read(INSTALL_ASSIGNMENT))
    content = assignment["content"]
    assert "fastfetch" in content["instructions"]
    assert "neofetch" not in content["instructions"].lower()
    assert not any("terminal" in resource["title"].lower() for resource in content["resources"])
    assert "video" not in content["tags"]


def test_flujos_arranca_con_historial_antes_de_los_flows_avanzados():
    """Evita volver a abrir la estación con teoría de stdin/stdout/stderr."""
    page = read(FLOWS)

    assert page.index("`history`") < page.index("stdin")
    assert "history | grep pwd" in page
    assert "Haz:" in page and "Deberías ver:" in page and "Pausa:" in page


def test_flujos_prepara_su_laboratorio_desde_un_home_vacio(tmp_path):
    """Evita que la tercera estación falle si no se ejecutaron las anteriores."""
    result = run_bash(bash_block_with_title(FLOWS, "Mira y recupera tu historial"), tmp_path)

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "fdd/terminal-lab/notas").is_dir()


def test_flujos_limita_cada_bloque_a_cinco_comandos():
    """Evita paredes de comandos incluso en las ampliaciones opcionales."""
    page = read(FLOWS)
    blocks = re.findall(r"```bash\n(.*?)```", page, re.S)

    assert blocks
    assert all(len([line for line in block.splitlines() if line.strip()]) <= 5 for block in blocks)


def test_ejemplo_de_stderr_crea_su_entrada_antes_de_listarla(tmp_path):
    """Evita que el ejemplo opcional dependa de carpetas creadas en otra página."""
    result = run_bash(
        bash_block_with_title(FLOWS, "Opcional: separa salida y diagnóstico"),
        tmp_path,
    )
    reports = tmp_path / "fdd/terminal-lab/reportes"

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "fdd/terminal-lab/notas").is_dir()
    assert (reports / "listado-vacio.txt").read_text(encoding="utf-8") == ""
    assert (reports / "error.txt").read_text(encoding="utf-8")


def test_ejemplo_de_pipefail_es_autonomo_desde_un_home_vacio(tmp_path):
    """Evita que la ampliación B dependa del bloque opcional anterior."""
    result = run_bash(
        bash_block_with_title(FLOWS, "Transforma una entrada preparada"),
        tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "fdd/terminal-lab/nombres.txt").read_text(
        encoding="utf-8"
    ) == "Ana\nBeto\nAna\n"
    assert (tmp_path / "fdd/terminal-lab/reportes/conteos.txt").is_file()


def test_filtro_de_history_advierte_que_puede_encontrarse_a_si_mismo():
    """Evita atribuir cada coincidencia del historial a un pwd previo."""
    page = read(FLOWS)

    assert "puede incluir la propia línea del filtro" in page


def test_bandit_exige_exactamente_las_tres_transiciones_iniciales():
    """Evita asignar niveles posteriores al ingreso comprobable a bandit3."""
    content = yaml.safe_load(read(BANDIT_ASSIGNMENT))["content"]
    instructions = content["instructions"]

    assert all(step in instructions for step in ("0→1", "1→2", "2→3"))
    assert all(step not in instructions for step in ("3→4", "4→5", "5→6"))
    assert "bandit3" in instructions
    assert content["due"] == "2026-08-27"


def test_bandit_preflight_es_multiplataforma_y_no_pide_secretos():
    """Evita una tarea de SSH frágil o que solicite material sensible."""
    instructions = yaml.safe_load(read(BANDIT_ASSIGNMENT))["content"]["instructions"]

    for command in (
        "command -v bash",
        "bash --version",
        'echo "$SHELL"',
        "sudo apt update",
        "sudo apt install btop",
        "brew install btop fastfetch",
        "ssh -V",
        "ssh-add -l",
    ):
        assert command in instructions
    for platform in ("Ubuntu", "WSL2", "macOS"):
        assert platform in instructions
    assert "ssh-agent no guarda contraseñas de Bandit" in instructions
    assert "llave privada" in instructions


def test_bandit_busca_btop_antes_de_instalarlo_en_ubuntu_y_wsl2():
    """Evita instalar sin revisar primero el paquete disponible."""
    instructions = yaml.safe_load(read(BANDIT_ASSIGNMENT))["content"]["instructions"]

    assert instructions.index("apt search btop") < instructions.index(
        "sudo apt install btop"
    )
    assert "WSL2 con Ubuntu" in instructions
    assert "mismos comandos" in instructions


def test_bandit_guia_shellenv_sin_hardcodear_homebrew():
    """Evita una posinstalación de Homebrew dependiente de la arquitectura."""
    instructions = yaml.safe_load(read(BANDIT_ASSIGNMENT))["content"]["instructions"]

    assert instructions.index("command -v brew") < instructions.index("shellenv")
    assert instructions.index("shellenv") < instructions.index(
        "brew install btop fastfetch"
    )
    assert instructions.count("command -v brew") >= 2
    assert "/opt/homebrew" not in instructions
    assert "/usr/local" not in instructions
