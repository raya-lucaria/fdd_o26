"""Guardas focales para la cobertura esencial de Terminal y Bash."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
UNIT = ROOT / "course/5_terminal_y_bash"
ORIENTATION = UNIT / "1_terminal/1_entrar_y_orientarte/0_index.md"
TERMINAL_INDEX = UNIT / "1_terminal/0_index.md"
BASH_INDEX = UNIT / "2_bash_scripting/0_index.md"
SCRIPT = UNIT / "2_bash_scripting/3_de_pasos_a_script/0_index.md"
INSTALL_ASSIGNMENT = (
    ROOT
    / "course/4_software_libre_y_sistemas_operativos/_official/assignments/1_instalar_linux.yaml"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
