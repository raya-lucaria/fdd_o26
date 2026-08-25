# Unidad 5 Terminal y Bash Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear una unidad breve y escaneable de terminal directa y Bash scripting, con ejemplos locales autocontenidos, Bandit para el 27 de agosto y un examen escrito separado.

**Architecture:** Añadir una unidad `course/5_terminal_y_bash/` con una portada, dos mapas de subtema y seis estaciones cortas. Mantener tareas y examen como objetos oficiales separados, actualizar sólo los eventos de calendario afectados y conservar la unidad existente de instalación Linux como prerrequisito.

**Tech Stack:** Markdown CommonMark + directivas estáticas Raya, YAML oficial de assignments/exams, SVG local, calendario YAML, pytest editorial y Raya `validate`/`build`.

**Spec:** `docs/superpowers/specs/2026-08-25-unidad-5-terminal-bash-design.md`

## Global Constraints

- Todo ocurre en `~/fdd/terminal-lab`, sin repositorio, Git, GitHub, Docker ni dependencias de desarrollo.
- Linux/Ubuntu es el caso base; macOS y WSL2 aparecen en tarjetas de diferencias, no como tres cursos paralelos.
- Cada estación usa el ritmo “Haz esto ahora → modelo mínimo → ejemplo → predice → ejecuta → punto de parada”.
- `hint` y `answer` se asocian con `of="id"` y quedan cerrados; no hay scoring, progreso, formularios ni flashcards.
- No usar `rm -rf` como receta; enseñar `rm -i`, `rmdir` y `rm -r` sólo dentro del laboratorio.
- Usar `fastfetch`, no `neofetch`; enseñar `apt` interactivo y Homebrew para macOS.
- Escribir texto estudiantil en español; conservar IDs, nombres de archivos, comandos y tokens técnicos en inglés.
- No editar ni versionar `artifact/`; registrar cada asset en `_assets/CREDITOS.md`.

---

### Task 1: Crear la navegación y portada de la unidad

**Files:**
- Create: `course/5_terminal_y_bash/0_index.md`
- Create: `course/5_terminal_y_bash/1_terminal/0_index.md`
- Create: `course/5_terminal_y_bash/2_bash_scripting/0_index.md`

**Interfaces:**
- Consumes: prerrequisito `software-libre-y-sistemas-operativos` y los seis slugs de estaciones definidos en la spec.
- Produces: wikilinks estables `terminal-y-bash`, `terminal-directa` y `bash-scripting` para las estaciones, tareas y calendario.

- [ ] **Step 1: Escribir el frontmatter y resumen de la portada** con título en español, `status: ready`, tiempo estimado breve, tags `terminal`, `bash`, `shell`, `linux`, `wsl2`, `macos` y el prerrequisito de unidad 4.
- [ ] **Step 2: Añadir un mapa de dos subtemas** con seis enlaces y una barra de progreso textual “1–6 estaciones”. Explicar que la carpeta de práctica es local y no es repositorio.
- [ ] **Step 3: Escribir los dos índices de subtema** con meta visible, tiempo de cada estación, criterio “terminas cuando…” y enlaces sólo a sus tres estaciones.
- [ ] **Step 4: Ejecutar la guardia de wikilinks y validar frontmatter** con `python3 -m pytest tools/ -q`.
- [ ] **Step 5: Commit** `feat(unidad-5): añade mapa de terminal y Bash`.

### Task 2: Escribir las tres estaciones de terminal

**Files:**
- Create: `course/5_terminal_y_bash/1_terminal/1_entrar_y_orientarte/0_index.md`
- Create: `course/5_terminal_y_bash/1_terminal/2_archivos_y_comandos/0_index.md`
- Create: `course/5_terminal_y_bash/1_terminal/3_flujos_procesos_y_herramientas/0_index.md`

**Interfaces:**
- Consumes: índice `terminal-directa`, assets de Task 5, directivas Raya existentes (`definition`, `example`, `activity`, `problem`, `hint`, `answer`).
- Produces: seis o más problemas con IDs únicos, laboratorio local reproducible y enlace a la tarea Bandit.

- [ ] **Step 1: Escribir “Entrar y orientarte”** con terminal/shell/Bash, historia de una línea, diferencias Ubuntu/WSL2/macOS, `whoami`, `pwd`, `uname -s`, `bash --version`, atajos cotidianos y creación de `~/fdd/terminal-lab`.
- [ ] **Step 2: Añadir dos problemas autocontenidos**: identificar el prompt y distinguir `echo "$SHELL"` de `bash --version`; cada uno con `hint` y `answer` cerrados.
- [ ] **Step 3: Escribir “Archivos y comandos”** con árbol, rutas, archivos ocultos, forma `command [options] [arguments]`, flags cortos/largos/con valor, `--`, `man`, `--help`, `type -a`, `command -v`, comandos de archivo y borrado seguro.
- [ ] **Step 4: Hacer que cada ejemplo cree sus archivos** (`nombres.txt`, `errores.txt`, `dos palabras.txt`, `reportes/`) antes de leerlos; incluir vista previa con `printf '%s\n' -- *` antes de cualquier borrado.
- [ ] **Step 5: Escribir “Flujos, procesos y herramientas”** con stdin/stdout/stderr, `>`, `>>`, `2>`, `2>&1`, `|`, `tee`, `&&`, `||`, `$?`, `ps`, `htop`, `fastfetch`, `apt` y `brew` como tarjetas por plataforma.
- [ ] **Step 6: Añadir predicciones** sobre `ls inexistente > salida 2> errores`, `ls inexistente | wc -l`, `sort | uniq -c` y el efecto de `Ctrl-C`.
- [ ] **Step 7: Revisar que ninguna instrucción dependa de Git, un editor instalado o estado de una estación anterior.**
- [ ] **Step 8: Ejecutar `python3 -m pytest tools/ -q` y `raya validate ../fdd_o26`.**
- [ ] **Step 9: Commit** `feat(unidad-5): enseña terminal con laboratorio local`.

### Task 3: Escribir las tres estaciones de Bash scripting

**Files:**
- Create: `course/5_terminal_y_bash/2_bash_scripting/1_como_lee_bash/0_index.md`
- Create: `course/5_terminal_y_bash/2_bash_scripting/2_variables_comillas_y_salida/0_index.md`
- Create: `course/5_terminal_y_bash/2_bash_scripting/3_de_pasos_a_script/0_index.md`

**Interfaces:**
- Consumes: índice `bash-scripting`, archivos de práctica creados localmente y el diagrama de Task 5.
- Produces: script final `inventario.sh` descrito en la página, sin requerir que el estudiante cree un repositorio.

- [ ] **Step 1: Escribir “Cómo lee Bash”** con shell interactiva/script, Bash/Zsh/Fish, espacios, globbing, `;`, `&&`, `||` y `(...)` como subshell.
- [ ] **Step 2: Añadir problemas de expansión de argumentos** con `printf '%s\n' -- *` y nombres con espacios; explicar que Bash expande antes de invocar al programa.
- [ ] **Step 3: Escribir “Variables, comillas y salida”** con asignación sin espacios, `$var`, `${var}`, `$HOME`, `$PATH`, comillas simples/dobles/sin comillas, `$(command)`, `$((...))`, `{a,b}` y stdout/stderr.
- [ ] **Step 4: Añadir exactamente estas predicciones:** `$archivo` vs `"$archivo"`; `echo '$HOME'`/`echo "$HOME"`/`echo $HOME`; `x${n}z` vs `x$n z`; `echo "$(pwd)"` vs `(cd /; pwd); pwd`.
- [ ] **Step 5: Escribir “De pasos a script”** con `bash archivo.sh`, `#!/usr/bin/env bash`, `chmod +x`, `./archivo.sh`, `$1`, `"$@"`, `read -r`, `printf`, `if [[ -d ... ]]`, `exit 1` y `bash -x`.
- [ ] **Step 6: Construir el ejemplo final `inventario.sh`** para validar un directorio, listar `.txt`, contar líneas y escribir `reporte.txt`; incluir caso correcto y caso de error.
- [ ] **Step 7: Revisar que loops, funciones, `set -e`, `eval`, `source`, RC files y permisos octales queden fuera de alcance.**
- [ ] **Step 8: Ejecutar `python3 -m pytest tools/ -q` y `raya validate ../fdd_o26`.**
- [ ] **Step 9: Commit** `feat(unidad-5): introduce Bash scripting con ejemplos`.

### Task 4: Añadir Bandit y el examen escrito

**Files:**
- Create: `course/5_terminal_y_bash/_official/assignments/1_bandit.yaml`
- Create: `course/5_terminal_y_bash/_official/exams/1_examen-unidad-inicial.yaml`

**Interfaces:**
- Consumes: URLs oficiales de OverTheWire y el esquema de objetos oficiales de Raya.
- Produces: una assignment con due `2026-08-27`, y un exam separado sin entrega de Canvas.

- [ ] **Step 1: Escribir la assignment Bandit** con niveles 0–5, entrada al nivel 6 como evidencia, bitácora de hipótesis/documentación/comandos/ajustes, prohibición de walkthroughs y contraseñas en archivos o capturas, y recursos `man`, `--help` y pistas oficiales.
- [ ] **Step 2: Escribir el exam oficial** con título “Examen escrito: arquitectura, sistemas operativos y pipeline de datos”, fecha `2026-08-27`, duración corta indicada por el docente, modalidad presencial escrita y sin URL de entrega.
- [ ] **Step 3: Ejecutar la guardia YAML y confirmar que ambos objetos aparecen en el workspace oficial por separado.**
- [ ] **Step 4: Commit** `feat(unidad-5): añade Bandit y examen escrito`.

### Task 5: Crear y acreditar los diagramas mínimos

**Files:**
- Create: `course/5_terminal_y_bash/_assets/d-shell-flujo.svg`
- Create: `course/5_terminal_y_bash/_assets/d-terminal-lab.svg`
- Create: `course/5_terminal_y_bash/_assets/hero-terminal-original.png`
- Create: `course/5_terminal_y_bash/_assets/hero-bash-original.png`
- Create: `course/5_terminal_y_bash/_assets/CREDITOS.md`
- Modify: `course/5_terminal_y_bash/0_index.md`
- Modify: `course/5_terminal_y_bash/1_terminal/0_index.md`
- Modify: `course/5_terminal_y_bash/2_bash_scripting/0_index.md`

**Interfaces:**
- Consumes: tokens visuales existentes de `fdd-eva` y el contrato de créditos del curso.
- Produces: dos SVG con alt text y enlaces desde la portada; no se copia una imagen de P26 sin licencia/crédito verificable.

- [ ] **Step 1: Conservar los dos PNG originales generados** `hero-terminal-original.png` y `hero-bash-original.png`; no añadir texto técnico encima de la imagen y mantener espacio negativo para títulos.
- [ ] **Step 2: Dibujar `d-shell-flujo.svg`** como flujo estático `tecla → Bash → expansión → programa → stdout/stderr`, con texto legible en móvil.
- [ ] **Step 3: Dibujar `d-terminal-lab.svg`** como árbol de `~/fdd/terminal-lab` con `nombres.txt`, `dos palabras.txt` y `reportes/`.
- [ ] **Step 4: Añadir ambos PNG, ambos SVG y sus prompts resumidos a `CREDITOS.md`**; los PNG se acreditan como generados con OpenAI Image Generation el 2026-08-25, sin personajes, logos ni texto legible.
- [ ] **Step 5: Añadir alt text descriptivo y usar un PNG sólo en cada portada de subtema; los diagramas se reservan para las estaciones conceptuales.**
- [ ] **Step 6: Construir y verificar que ningún SVG contiene texto ilegible o overflow y que los PNG recortan bien en móvil.**
- [ ] **Step 7: Commit** `feat(unidad-5): añade visuales originales del laboratorio`.

### Task 6: Actualizar calendario y retirar duplicados de preparación

**Files:**
- Modify: `course/_official/calendar/1_2026-o26.yaml`
- Delete: `course/4_software_libre_y_sistemas_operativos/_official/assignments/2_video_bash_scripting.yaml`
- Modify: `course/4_software_libre_y_sistemas_operativos/_official/assignments/1_instalar_linux.yaml`

**Interfaces:**
- Consumes: IDs de páginas y objetos de Tasks 1 y 4.
- Produces: sesiones 25/27 de agosto enlazadas a la unidad nueva; ninguna preparación Bash duplicada en la unidad de instalación.

- [ ] **Step 1: Cambiar `session-05`** a “Terminal: uso directo” y enlazarlo a `terminal-directa`.
- [ ] **Step 2: Cambiar `session-06`** a “Bash scripting y examen” y enlazarlo a `bash-scripting`.
- [ ] **Step 3: Añadir un evento `kind: exam` el 2026-08-27** para el examen escrito, separado del evento de sesión y de Bandit.
- [ ] **Step 4: Eliminar la assignment antigua de video Bash** para que no aparezca como trabajo duplicado el 25 de agosto; la nueva unidad será la única fuente de preparación Bash.
- [ ] **Step 5: Mantener la assignment de instalación Linux** como prerrequisito y actualizar sólo sus enlaces si apuntan al video viejo de terminal.
- [ ] **Step 6: Ejecutar `python3 -m pytest tools/ -q` y `raya validate ../fdd_o26`.**
- [ ] **Step 7: Commit** `feat(unidad-5): conecta sesiones y evaluaciones al calendario`.

### Task 7: Verificación editorial y visual

**Files:**
- Test/inspect: `tools/`, todas las páginas y YAML de Tasks 1–6.

- [ ] **Step 1: Ejecutar `python3 -m pytest tools/ -q`** y resolver errores de IDs, créditos, YAML o vocabulario.
- [ ] **Step 2: Ejecutar `UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ../fdd_o26`.**
- [ ] **Step 3: Ejecutar `UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ../fdd_o26`.**
- [ ] **Step 4: Previsualizar desktop y móvil** con `raya preview` y revisar que cada estación muestra primero la acción, que el código no desborda, que `hint`/`answer` inicia cerrado y que las tablas de plataforma se escanean.
- [ ] **Step 5: Confirmar manualmente los cinco ejemplos críticos:** comillas, `$(pwd)`, subshell, stdout/stderr y borrado con vista previa.
- [ ] **Step 6: Commit** `chore(unidad-5): valida contenido y render de terminal`.
