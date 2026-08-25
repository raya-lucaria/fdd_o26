# Unidad 5: recorrido cotidiano de Terminal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reordenar Terminal como una práctica cotidiana guiada y actualizar la tarea Bash/SSH/Bandit a niveles 0–3.

**Architecture:** Mantener IDs y activos; convertir las tres estaciones en una sola historia: ubicarse, construir una carpeta y encontrar/conectar información. Los flujos avanzados pasan al final. La tarea oficial concentra preflight de Bash/SSH, instalación opcional y Bandit sin secretos.

**Tech Stack:** Markdown CommonMark, directivas Raya, YAML oficial, pytest editorial y Raya build.

**Spec:** `docs/superpowers/specs/2026-08-25-unidad-5-terminal-bash-design.md`

## Global Constraints

- Todo ocurre bajo `~/fdd/terminal-lab`; sin Git, GitHub ni Docker.
- Cada misión usa “Haz → Deberías ver → Pausa” y no introduce más de dos comandos nuevos.
- Linux/Ubuntu es referencia; WSL2 y macOS son tarjetas compactas.
- Sólo `rm -i` y `rmdir` dentro del laboratorio; jamás `rm -rf` o borrado con `sudo`.
- No se entregan contraseñas ni llaves privadas. `ssh-agent` no gestiona contraseñas de Bandit.
- Bandit exige exclusivamente 0→1, 1→2, 2→3 y llegada a `bandit3`.

---

### Task 1: Orientación y navegación

**Files:**
- Modify: `course/5_terminal_y_bash/1_terminal/1_entrar_y_orientarte/0_index.md`
- Test: `tools/test_terminal_bash_curriculum.py`

**Interfaces:**
- Produces: `~/fdd/terminal-lab/notas/hoy/`, y dominio inicial de `pwd`, `ls`, `cd`, `~`, `.`, `..`, rutas relativas y absolutas.

- [ ] **Step 1: Escribir prueba editorial RED.**

```python
def test_orientacion_guia_pwd_y_rutas():
    texto = ORIENTACION.read_text(encoding="utf-8")
    assert texto.index("`pwd`") < texto.index("`touch`")
    assert all(token in texto for token in ("`~`", "`/`", "`.`", "`..`"))
    assert "Haz:" in texto and "Deberías ver:" in texto and "Pausa:" in texto
```

- [ ] **Step 2: Ejecutar RED.** `python3 -m pytest tools/test_terminal_bash_curriculum.py -q`; debe fallar por la secuencia actual.
- [ ] **Step 3: Implementar tres misiones.** Primero `pwd` y `ls`; luego `mkdir -p`, `cd`, `cd ..`, `cd ~/...`; después `ls -la`, rutas absolutas/relativas y `.`, `..`. Conservar terminal/shell/Bash, historia y atajos como tarjetas posteriores.
- [ ] **Step 4: Ejecutar GREEN.** Repetir la prueba y ejecutar los bloques de misión con `HOME` temporal; comprobar que todo queda bajo `$HOME/fdd/terminal-lab`.
- [ ] **Step 5: Commit.** `git commit -m "feat(unidad-5): guia navegacion cotidiana"`.

### Task 2: Crear y cuidar archivos

**Files:**
- Modify: `course/5_terminal_y_bash/1_terminal/2_archivos_y_comandos/0_index.md`
- Test: `tools/test_unidad_5_terminal.py`

**Interfaces:**
- Consumes: la carpeta de notas, pero el primer bloque puede recrearla.
- Produces: `touch`, `echo`, `>`, `>>`, `cat`, `head`, `tail`, ayuda, `cp -i`, `mv -i`, `rm -i` y `rmdir` en una mini carpeta real.

- [ ] **Step 1: Escribir prueba editorial RED.**

```python
def test_archivos_construye_una_nota_antes_de_copiar_o_borrar():
    texto = ARCHIVOS.read_text(encoding="utf-8")
    assert texto.index("`touch`") < texto.index("`cp -i`") < texto.index("`rm -i`")
    assert all(token in texto for token in ("`echo`", "`>`", "`>>`", "`cat`", "`head`", "`tail`"))
```

- [ ] **Step 2: Ejecutar RED.** `python3 -m pytest tools/test_unidad_5_terminal.py -q`; debe fallar por los datos artificiales actuales.
- [ ] **Step 3: Implementar tres misiones.** Crear `lista.txt` con `touch` y `echo >`; anexar con `>>`, observar con `cat`/`head`/`tail`, crear `.secreto` y verlo con `ls -la`; pedir ayuda con `man ls`/`--help`, copiar, renombrar y borrar sólo un nombre explícito.
- [ ] **Step 4: Ejecutar GREEN.** Repetir prueba y bloques con `HOME` temporal; comprobar contenido, copia y archivo oculto.
- [ ] **Step 5: Commit.** `git commit -m "feat(unidad-5): enseña archivos paso a paso"`.

### Task 3: Historial, extensiones y tarea SSH/Bandit

**Files:**
- Modify: `course/5_terminal_y_bash/1_terminal/3_flujos_procesos_y_herramientas/0_index.md`
- Modify: `course/5_terminal_y_bash/_official/assignments/1_bandit.yaml`
- Modify: `tools/test_terminal_bash_curriculum.py`

**Interfaces:**
- Produces: `history | grep`, `grep`, `wc -l`, redirección simple antes de flujos avanzados; assignment Bandit 0→3 con preflight seguro.

- [ ] **Step 1: Escribir pruebas RED.**

```python
def test_bandit_exige_solo_tres_transiciones():
    text = yaml.safe_load(BANDIT.read_text())["content"]["instructions"]
    assert all(step in text for step in ("0→1", "1→2", "2→3"))
    assert "3→4" not in text

def test_flujos_arranca_con_historial_y_grep():
    texto = FLUJOS.read_text(encoding="utf-8")
    assert texto.index("history") < texto.index("stdin")
    assert "history | grep" in texto
```

- [ ] **Step 2: Ejecutar RED.** `python3 -m pytest tools/test_terminal_bash_curriculum.py -q`; debe fallar con Bandit 0–5 y el orden actual.
- [ ] **Step 3: Implementar estación 3.** Empezar con `history`, flechas, `Ctrl-R` y `history | grep pwd`; explicar pipe como texto de izquierda a derecha. Añadir `grep`, `wc -l`, `>`/`>>`; dejar stdout/stderr, `2>`, `tee`, `pipefail`, `ps` y `Ctrl-C` como tarjeta final opcional.
- [ ] **Step 4: Implementar assignment.** Verificar Bash (`command -v bash`, `bash --version`, `echo "$SHELL"`); Ubuntu/WSL2: `sudo apt update`, buscar e instalar `btop`; macOS con Homebrew: `brew install btop fastfetch`; SSH: `ssh -V`, `ssh-add -l` y prompts por plataforma para investigar un agente/llave existente. Prohibir secretos, walkthroughs y LLM; exigir entrada a `bandit3`.
- [ ] **Step 5: Ejecutar GREEN y YAML.** `python3 -m pytest tools/test_terminal_bash_curriculum.py tools/test_unidad_5_terminal.py -q` y parse YAML con PyYAML.
- [ ] **Step 6: Commit.** `git commit -m "feat(unidad-5): prepara SSH y Bandit inicial"`.

### Task 4: Revisión y publicación

**Files:**
- Test/inspect: las tres estaciones, `1_bandit.yaml`, `tools/` y artefacto generado.

- [ ] **Step 1: Leer las tres estaciones en orden.** Todo comando aparece después de su propósito y ningún bloque usa estado implícito.
- [ ] **Step 2: Ejecutar CI.** `python3 -m pytest tools/ -q`; esperado: PASS.
- [ ] **Step 3: Construir con Raya fijado.** `uv run --directory ../raya_lucaria/.worktrees/navigation-first-course-rail raya build .`; esperado: `Course artifact build passed`.
- [ ] **Step 4: Revisar escritorio/móvil.** Primera pantalla con `pwd` antes de teoría; código y entornos con tema oscuro.
- [ ] **Step 5: Commit.** `git commit -m "chore(unidad-5): valida recorrido cotidiano"`.
