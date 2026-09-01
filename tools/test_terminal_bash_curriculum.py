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


def test_orientacion_abre_con_meta_y_mision_pwd():
    texto = read(ORIENTATION)
    cuerpo = texto.split("# Entrar y orientarte\n", 1)[1]
    antes_mision = cuerpo.split("## Misión 1:", 1)[0].strip()
    assert antes_mision.startswith("Meta:")
    assert "\n\n" not in antes_mision

    posicion_mision = texto.find("## Misión 1:")
    posicion_plataforma = texto.find('title="Tarjeta: abre el entorno correcto"')
    assert 0 <= posicion_mision < posicion_plataforma

    mision = texto.split("## Misión 1:", 1)[1].split("## Misión 2:", 1)[0]
    bloque = mision.split("```bash\n", 1)[1].split("\n```", 1)[0]
    assert bloque.splitlines()[:2] == ["pwd", "ls"]


def test_orientacion_resumen_movil_da_siguiente_accion():
    texto = read(ORIENTATION)
    metadata = yaml.safe_load(texto.split("---", 2)[1])
    resumen = metadata["summary"]
    assert resumen.startswith("Ejecuta `pwd` y `ls`")
    assert len(resumen) <= 80


def test_orientacion_define_y_compara_rutas_antes_de_navegar():
    """Mantiene absoluta/relativa como la primera idea de rutas."""
    texto = read(ORIENTATION)
    assert "**Ruta absoluta:**" in texto
    assert "**Ruta relativa:**" in texto
    assert "La misma carpeta, dos rutas" in texto
    assert texto.index("**Ruta absoluta:**") < texto.index("## Misión 2:")
    assert "Cheat sheet: comandos de todos los días" in texto
    for comando in ("`pwd`", "`ls`", "`cd ruta`", "`touch archivo.txt`", "`cat`", "`cp -i`", "`mv -i`", "`rm -i archivo`", "`man comando`", "`history`"):
        assert comando in texto


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


def test_bandit_llega_exactamente_hasta_la_contrasena_del_nivel_7():
    """Evita mover el alcance de la misión o su fecha de entrega."""
    content = yaml.safe_load(read(BANDIT_ASSIGNMENT))["content"]
    instructions = content["instructions"]

    transiciones = ("0→1", "1→2", "2→3", "3→4", "4→5", "5→6", "6→7")
    assert all(paso in instructions for paso in transiciones)
    assert "7→8" not in instructions
    assert "bandit7" in instructions
    assert "nivel 8" in instructions
    assert content["due"] == "2026-09-01"

    pagina = read(FLOWS)
    assert "0→1 hasta 6→7" in pagina
    assert "contraseña del nivel 7" in pagina


def test_bandit_prohibe_llms_y_pide_buscar_comandos_no_soluciones():
    """Evita que la tarea deje de ejercitar el razonamiento que evalúa."""
    instructions = yaml.safe_load(read(BANDIT_ASSIGNMENT))["content"]["instructions"]
    pagina = read(FLOWS)

    for texto in (instructions, pagina):
        assert "no las soluciones" in texto or "no soluciones" in texto
        assert "LLM" in texto
        assert "IA generativa" in texto
        assert "walkthrough" in texto.lower()
    # El enlace de Canvas existia como pendiente; ahora la invariante util es
    # que la tarea diga a donde se entrega, no que siga sin decidirse.
    assert "itam.instructure.com" in instructions, (
        "la tarea debe nombrar su enlace de entrega en Canvas"
    )


def test_bandit_instructions_no_traen_markdown_sin_renderizar():
    """El renderer escapa content.instructions: el Markdown saldría literal."""
    instructions = yaml.safe_load(read(BANDIT_ASSIGNMENT))["content"]["instructions"]

    for marca in ("##", "**", "`", "```", "- ", "|"):
        assert marca not in instructions, f"Markdown crudo en instructions: {marca!r}"


def test_bandit_preflight_es_multiplataforma_y_no_pide_secretos():
    """Evita una preparación de Bash/SSH frágil o que solicite material sensible."""
    pagina = read(FLOWS)

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
        assert command in pagina
    for platform in ("Ubuntu", "WSL2", "macOS"):
        assert platform in pagina
    assert "no guarda contraseñas de Bandit" in pagina
    assert "llave privada" in pagina

    instructions = yaml.safe_load(read(BANDIT_ASSIGNMENT))["content"]["instructions"]
    assert "llaves privadas" in instructions
    assert "nunca incluyas contraseñas" in instructions


def test_bandit_busca_btop_antes_de_instalarlo_en_ubuntu_y_wsl2():
    """Evita instalar sin revisar primero el paquete disponible."""
    pagina = read(FLOWS)

    assert pagina.index("apt search btop") < pagina.index("sudo apt install btop")
    assert "WSL2 + Ubuntu" in pagina
    assert "apt search fastfetch" in pagina


def test_bandit_guia_shellenv_sin_hardcodear_homebrew():
    """Evita una posinstalación de Homebrew dependiente de la arquitectura."""
    pagina = read(FLOWS)

    assert pagina.index("command -v brew") < pagina.index("shellenv")
    assert pagina.index("shellenv") < pagina.index("brew install btop fastfetch")
    assert pagina.count("command -v brew") >= 2
    assert "/opt/homebrew" not in pagina
    assert "/usr/local" not in pagina
