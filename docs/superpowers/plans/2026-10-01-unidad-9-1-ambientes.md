# Unidad 9 · Python — 9.1 Ambientes · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar la sección 9.1 *Ambientes* de la nueva unidad 9 · Python —10 páginas de lección, cheatsheet, tablero de entregas, 8 figuras generadas, código de laboratorio— y sus dos entregas por pull request (`tarea-09-datacamp-python`, `tarea-09-uv-docker`), con la sesión de hoy (2026-10-01, 19:00–20:00) en el calendario.

**Architecture:** Repositorio de contenido. El Markdown de `course/` lo consume el CLI `raya` del repo hermano `~/itam/raya_lucaria`. Las figuras salen de un generador nuevo (`tools/gen_python.py`) que es su única fuente de verdad, protegido por `tools/test_gen_python.py`. La forma de las páginas la protege una guarda nueva (`tools/test_python_curriculum.py`). Las entregas son las seis piezas de la skill `crear_tarea` (ficha, YAML oficial, plantilla, `TAREAS`, tablero, tests). Toda salida de terminal que se publique sale de correr el comando de verdad (Fase 0), nunca de memoria.

**Tech Stack:** Markdown + YAML frontmatter, TOML (fichas), Python 3 stdlib (generador, scripts), pytest, Docker (para capturar salidas en limpio), uv, el CLI `raya`.

**Spec:** `docs/superpowers/specs/2026-10-01-unidad-9-1-ambientes-design.md`

## Global Constraints

- **Sin analogías.** Cada concepto: qué es (una línea) + el comando que lo demuestra + su salida. Prohibidas en prosa: «imagina», «es como», «como si», «analogía», «piensa en», «receta», «despensa». La guarda de la Task 6 lo comprueba.
- **Lectores con ADHD**: párrafos ≤ 3 líneas, tabla antes que prosa, **bold** sólo en lo que se rompe si no se lee.
- **Núcleo = uv y su `.venv`.** venv+pip: una página corta. conda, poetry, pdm, hatch, pixi, pyenv, pipx, pipenv, pip-tools: se comparan, no se practican.
- El anexo de comandos se llama **Cheatsheet**, no «chuleta».
- **Toda salida publicada sale de la Fase 0** (`.superpowers/salidas-9-1/`). Ninguna salida se escribe de memoria.
- **Todo `$` en code span o fence** (el renderizador carga `dollarmath`: dos `$` en una línea de prosa se vuelven MathJax sin error).
- **Todo `@` suelto en code span** (`@name` es referencia a objeto numerado y tumba el build).
- **Nada de HTML crudo, nada de mermaid.**
- **Comillas en todo valor de frontmatter que lleve `:`.**
- **IDs de objeto numerado con prefijo `py-`**, únicos en todo el curso. Una figura se numera una sola vez; si reaparece, va como imagen suelta sin directiva.
- **Español en prosa, inglés en identificadores.**
- **Fechas `AAAA-MM-DD`** en ficha, YAML y lo que escribe el alumno.
- **Mensajes de ficha: QUÉ / POR QUÉ / DÓNDE INVESTIGAR, nunca el cómo.** Ni backticks, ni `docker `, `uv `, `pip `, `git `, `cp `, `mkdir` (lo comprueba `test_los_mensajes_de_la_ficha_no_dan_el_como`; ojo: «Docker Hub» en minúsculas contiene `docker `, así que los mensajes dicen «el registro público»).
- **No tocar `tools/svg_base.py`.** Se importa.
- **Generadores: sólo biblioteca estándar.**
- **Calendario**: la sesión es `session-13`, 2026-10-01, 19:00–20:00, `page: ambientes-python`. Las fechas de entrega **no** se escriben en el calendario.
- **Fechas de entrega**: ambas abren `2026-10-01`, vencen `2026-10-06`, 10 puntos, `penalizacion_tarde = "1/dia"`, `ia = "permitida-revisada"`.
- **Commits** con forma `feat(unidad-9): …` / `feat(entregas): …`, `git add` de rutas explícitas. **`CLAUDE.md` ya tiene cambios sin commit del profesor**: la Task 15 lo edita pero **no lo commitea**; se le avisa.

## Prioridad: la clase es hoy a las 19:00

| Fase | Qué | Para cuándo |
|---|---|---|
| **0** | Salidas reales | antes de todo |
| **1** | Código de clase, figuras de clase, guarda de forma, índices, páginas 🎯 (1, 3, 7, 9), calendario, docs del horario | **antes de las 19:00** |
| **2** | Páginas 📖 (2, 4, 5, 6, 8, 10, 11) y sus figuras | después de clase, hoy |
| **3** | Las dos entregas (seis piezas c/u), tablero, revisión adversarial | antes de anunciar las entregas |
| **4** | Verificación final | al cerrar |

Si la Fase 1 no cabe antes de las 19:00, las páginas 📖 de la Fase 2 quedan fuera del índice (no enlazadas) y se publican después: **el índice nunca enlaza una página que no existe**.

## Review Focus

1. **Windows**: un alumno en PowerShell copia `source .venv/bin/activate` y no pasa nada. Cada comando de activación en las páginas 3, 8 y la Cheatsheet trae su línea de Windows (`.venv\Scripts\activate`), y la página 10 trae el error de ExecutionPolicy. → test en Task 6 (`test_toda_activacion_trae_su_linea_de_windows`).
2. **Apple Silicon + Docker Hub**: imagen construida sin `--platform linux/amd64` corre en su Mac y no en la del revisor. → tablero y YAML de T2 lo dicen; señal en la ficha; test en Task 13 (`test_el_tablero_de_uv_docker_menciona_platform`).
3. **`COPY . .` con `.venv` local**: la plantilla deja el hueco 3; si el alumno copia todo y no ignora `.venv`, la imagen trae binarios de su máquina. → patrón `.dockerignore` (falla) + test en las dos direcciones (Task 12).
4. **El lab de uv corre dentro de `~/fdd/fdd_o26/`** y el `git add` del ritual sube `.venv` o un `pyproject.toml` ajeno. → las páginas 3/7/8 trabajan en `~/lab-ambientes/` (fuera del repo); test en Task 6 (`test_los_labs_no_trabajan_dentro_del_repo`).
5. **Alumno con uv viejo** (instalado hace meses) y salidas que no coinciden. → la página 7 abre con `uv self update` y `uv --version`, y dice la versión con la que se capturaron las salidas; test en Task 6 (`test_el_lab_de_uv_dice_su_version`).

---

## Mapa de archivos

```
course/9_python/
├── 0_index.md                        # id: python            (Task 7)
├── _assets/
│   ├── CREDITOS.md                   # (Task 4, crece en Task 9)
│   └── py-*.svg                      # 8 figuras (Tasks 4 y 9)
├── _official/assignments/
│   ├── 1_datacamp_python.yaml        # id: datacamp-python-developers (Task 11)
│   └── 2_uv_en_docker.yaml           # id: uv-en-docker               (Task 12)
└── 1_ambientes/
    ├── 0_index.md                    # id: ambientes-python            (Task 7)
    ├── 1_el_problema.md              # el-problema-de-los-ambientes    (Task 7)  🎯
    ├── 2_las_piezas.md               # las-piezas-de-un-ambiente       (Task 10) 📖
    ├── 3_un_ambiente_por_dentro.md   # un-ambiente-por-dentro          (Task 7)  🎯
    ├── 4_los_archivos.md             # los-archivos-del-ambiente       (Task 10) 📖
    ├── 5_las_herramientas.md         # las-herramientas-de-ambientes   (Task 10) 📖
    ├── 6_ambiente_conda_docker.md    # ambiente-conda-docker           (Task 10) 📖
    ├── 7_lab_uv.md                   # lab-uv                          (Task 8)  🎯
    ├── 8_venv_y_pip.md               # lab-venv-y-pip                  (Task 10) 📖
    ├── 9_vs_code.md                  # ambientes-en-vs-code            (Task 8)  🎯
    ├── 10_las_trampas.md             # trampas-de-ambientes            (Task 10) 📖
    ├── 11_A_cheatsheet.md            # cheatsheet-ambientes            (Task 10) 📖
    └── 12_B_entregas.md              # entregas-ambientes              (Task 13)

codigo/09_python/
├── README.md                         # (Task 2; Task 12 agrega el ritual de uv_docker)
├── ambientes/                        # labs de clase; se copian FUERA del repo
│   ├── quien_soy.py  hola.py  script_autonomo.py  requirements.txt
└── uv_docker/                        # plantilla de tarea-09-uv-docker (Task 12)
    ├── reporte.py  pyproject.toml  Dockerfile  .dockerignore  bitacora.md
codigo/python/certificaciones.md      # plantilla de tarea-09-datacamp-python (Task 11)
codigo/README.md                      # dos filas nuevas (Tasks 2 y 11)

tools/gen_python.py  tools/test_gen_python.py          # Tasks 4, 9
tools/test_python_curriculum.py                         # Task 6
tools/test_codigo_python.py                             # Task 2, crece en Task 12
tools/test_revisa_ficha.py                              # Tasks 11, 12 (agrega casos)
.github/tareas/tarea-09-datacamp-python.toml            # Task 11
.github/tareas/tarea-09-uv-docker.toml                  # Task 12
.github/workflows/entregas.yml                          # TAREAS (Tasks 11, 12)
course/_official/calendar/1_2026-o26.yaml               # session-13 (Task 5)
course/0_index.md  README.md  CLAUDE.md  AGENTS.md      # Tasks 5 y 15
```

**Por qué `ambientes/` se copia fuera del repo:** los labs crean `.venv/`, `pyproject.toml` y `uv.lock`. Dentro de `estudiantes/<login>/` acabarían en un `git add`. Fuera (`~/lab-ambientes/`) nunca se suben y se pueden borrar sin miedo, que es parte de lo que se enseña.

**Por qué `uv_docker/` es una subcarpeta de `09_python/`:** la carpeta de la entrega (`TAREAS`) es `09_python`, espejo de `codigo/09_python/`; el ritual de la tarea copia y agrega **sólo** `uv_docker/`, así que `ambientes/` nunca viaja en el PR.

---

## FASE 0 · Salidas reales

### Task 1: Banco de salidas reales

Todo lo que las páginas muestran como «Deberías ver» sale de aquí. Se corre en contenedores limpios para no depender de la máquina del autor (que tiene uv 0.9.7 y Python 3.10).

**Files:**
- Create: `.superpowers/salidas-9-1/` (gitignored por `.superpowers/`) con un `.txt` por experimento y `VERSIONES.txt`.

**Interfaces:**
- Produces: `.superpowers/salidas-9-1/VERSIONES.txt` con tres líneas `uv=<x.y.z>`, `python=<3.13.n>`, `rich=<a.b.c>`; y los archivos `pep668.txt`, `venv_*.txt`, `uv_*.txt`, `quien_soy_*.txt` que citan las Tasks 7, 8, 10. La Task 12 usa `uv=<x.y>` para fijar la imagen de uv en el `Dockerfile`.

- [ ] **Step 1: Versiones**

```bash
mkdir -p .superpowers/salidas-9-1 && cd .superpowers/salidas-9-1
docker pull ghcr.io/astral-sh/uv:python3.13-bookworm-slim
docker run --rm ghcr.io/astral-sh/uv:python3.13-bookworm-slim sh -c \
  'echo uv=$(uv --version | cut -d" " -f2); echo python=$(python --version | cut -d" " -f2)' > VERSIONES.txt
docker run --rm ghcr.io/astral-sh/uv:python3.13-bookworm-slim sh -c \
  'cd /tmp && uv init -q x && cd x && uv add -q rich && uv pip show rich | grep ^Version' >> VERSIONES.txt
cat VERSIONES.txt
```

Expected: tres líneas con versiones concretas (al 2026-09-08 uv iba en 0.12.11). Reescribe la tercera como `rich=<versión>`.

- [ ] **Step 2: PEP 668 (página 1)**

```bash
docker run --rm ubuntu:24.04 bash -c \
  'apt-get update -qq >/dev/null && apt-get install -y -qq python3-pip >/dev/null 2>&1 && pip install rich' \
  > pep668.txt 2>&1; tail -20 pep668.txt
```

Expected: `error: externally-managed-environment` y el texto «This environment is externally managed».

- [ ] **Step 3: El lab de uv completo (página 7)** — un archivo por paso

Copia primero los archivos de `codigo/09_python/ambientes/` (Task 2 los crea; si aún no existen, corre este step después de la Task 2). Luego:

```bash
docker run --rm -v "$PWD/../../codigo/09_python/ambientes:/src:ro" \
  ghcr.io/astral-sh/uv:python3.13-bookworm-slim bash -c '
set -x
cd /root && uv python list 2>&1 | head -8
uv init hola 2>&1; cd hola; ls -a; cat pyproject.toml
uv add rich 2>&1; ls -a; cat pyproject.toml; head -30 uv.lock; grep -c "^\[\[package\]\]" uv.lock
uv tree 2>&1
cp /src/hola.py /src/quien_soy.py .
uv run hola.py; uv run quien_soy.py
python3 quien_soy.py || python quien_soy.py
rm -rf .venv; uv run hola.py 2>&1
uv add --dev pytest 2>&1 | tail -3; sed -n "/dependency-groups/,\$p" pyproject.toml
uv remove rich 2>&1 | tail -2; uv run hola.py 2>&1 | tail -2; uv add rich -q
uvx cowsay -t hola 2>&1
cp /src/script_autonomo.py /root/; cd /root; uv run script_autonomo.py 2>&1
cd hola; uv export --no-hashes 2>&1 | head -12
' > uv_lab.txt 2>&1; wc -l uv_lab.txt
```

Expected: el archivo trae, en orden, cada comando (por `set -x`, líneas con `+`) y su salida real. Divide a mano en `uv_*.txt` por paso si facilita citarlo.

- [ ] **Step 4: venv + pip y el experimento activo/no activo (páginas 3 y 8)**

```bash
docker run --rm -v "$PWD/../../codigo/09_python/ambientes:/src:ro" python:3.13-slim bash -c '
set -x
mkdir -p /root/lab && cd /root/lab && cp /src/*.py /src/requirements.txt .
python quien_soy.py
python -m venv .venv; ls .venv; cat .venv/pyvenv.cfg; ls .venv/bin | head
. .venv/bin/activate; which python; echo "$PATH" | tr ":" "\n" | head -3
python quien_soy.py
pip install -q rich; python hola.py; pip freeze
deactivate; which python; python hola.py 2>&1 | tail -2
pip install -q rich 2>&1 | tail -2; python quien_soy.py
rm -rf .venv; ls -a
' > venv_lab.txt 2>&1; wc -l venv_lab.txt
```

Expected: `quien_soy.py` dice «¿en un ambiente? : no» antes, «sí» activado; `hola.py` falla con `ModuleNotFoundError` fuera del ambiente; y el segundo `pip install` (sin activar, en la imagen oficial, que no es externally-managed) **sí** instala en el Python global: esa es la trampa que la página 8 muestra.

- [ ] **Step 5: Nota de versiones**

Agrega al final de `VERSIONES.txt` la fecha (`date -I`) y los digests (`docker images --digests | grep -E "astral-sh/uv|python|ubuntu"`). Sin commit: `.superpowers/` está en `.gitignore`.

---

## FASE 1 · Lo de la clase (antes de las 19:00)

### Task 2: Código de clase `codigo/09_python/ambientes/`

**Files:**
- Create: `codigo/09_python/README.md`, `codigo/09_python/ambientes/{quien_soy.py,hola.py,script_autonomo.py,requirements.txt}`
- Modify: `codigo/README.md` (tabla «Las carpetas»)
- Test: `tools/test_codigo_python.py`

**Interfaces:**
- Produces: `quien_soy.py` imprime exactamente seis líneas con estos rótulos, en este orden: `python que corre`, `versión`, `sys.prefix`, `¿en un ambiente?`, `'python' en PATH`, `rich`. Las Tasks 7, 8 y 10 citan esos rótulos.

- [ ] **Step 1: Test que falla**

```python
# tools/test_codigo_python.py
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
```

- [ ] **Step 2: Correr y ver que falla**

Run: `python3 -m pytest tools/test_codigo_python.py -q`
Expected: FAIL (no existen los archivos).

- [ ] **Step 3: Escribir el código**

`codigo/09_python/ambientes/quien_soy.py`:

```python
"""Dice qué Python está corriendo y si estás dentro de un ambiente.

Sólo usa la biblioteca estándar: corre igual dentro y fuera de un ambiente,
con rich instalado o sin él. Ésa es la idea: correrlo en cada situación y
comparar.
"""
import os
import shutil
import sys
from importlib import metadata

en_ambiente = sys.prefix != sys.base_prefix

try:
    rich = f"instalado, versión {metadata.version('rich')}"
except metadata.PackageNotFoundError:
    rich = "NO instalado en este Python"

print(f"python que corre  : {sys.executable}")
print(f"versión           : {sys.version.split()[0]}")
print(f"sys.prefix        : {sys.prefix}")
print(f"¿en un ambiente?  : {'sí' if en_ambiente else 'no'}")
print(f"'python' en PATH  : {shutil.which('python') or '(ninguno)'}")
print(f"rich              : {rich}")
```

Los rótulos llevan relleno hasta la columna 18; el test compara `split(":")[0].strip()` y la línea exacta `¿en un ambiente?  : sí` (dos espacios antes de `:`).

`codigo/09_python/ambientes/hola.py`:

```python
from rich import print

print("[bold green]Hola[/] desde un Python que [cyan]sí[/] tiene rich instalado.")
```

`codigo/09_python/ambientes/script_autonomo.py`:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["rich"]
# ///
"""Un script que declara sus dependencias dentro de sí mismo (PEP 723).

`uv run script_autonomo.py` lee el bloque de arriba, crea un ambiente
temporal con rich y lo corre. No hay pyproject.toml ni .venv en tu carpeta.
"""
import sys

from rich.console import Console
from rich.table import Table

tabla = Table(title="Corrido por uv run, sin proyecto")
tabla.add_column("Qué")
tabla.add_column("Valor")
tabla.add_row("Python", sys.version.split()[0])
tabla.add_row("Ambiente", sys.prefix)
Console().print(tabla)
```

`codigo/09_python/ambientes/requirements.txt` (versión de `VERSIONES.txt`, Task 1):

```text
# Lo que necesita hola.py. Formato de pip: un paquete por línea.
rich==<rich de VERSIONES.txt>
```

`codigo/09_python/README.md`:

````markdown
# 09_python

Dos carpetas, con dos destinos distintos:

| Carpeta | Para qué | Se copia a |
|---|---|---|
| `ambientes/` | Los laboratorios de clase | `~/lab-ambientes/` — **fuera** del repo |
| `uv_docker/` | La entrega `tarea-09-uv-docker` | `estudiantes/$GHUSER/09_python/uv_docker/` |

## Los laboratorios: fuera del repo

Los labs crean `.venv/`, `pyproject.toml` y `uv.lock`. Fuera del repo nunca
acaban en un `git add`, y se pueden borrar sin miedo.

```bash
mkdir -p ~/lab-ambientes
cp -r ~/fdd/fdd_o26/codigo/09_python/ambientes/. ~/lab-ambientes/
cd ~/lab-ambientes && ls
```

Fíjate en la barra y el punto al final del origen: sin ellos, `cp` copia la
carpeta en vez de su contenido.

- `quien_soy.py` — dice qué Python corre y si estás en un ambiente. Sólo
  biblioteca estándar: corre en cualquier situación.
- `hola.py` — hola mundo con `rich`. Si `rich` no está, truena: así se nota.
- `script_autonomo.py` — un script con sus dependencias escritas dentro.
- `requirements.txt` — para el lab clásico de `venv` + `pip`.
````

`codigo/README.md`, tabla «Las carpetas» — agrega:

```markdown
| `09_python/` | 09 — Python | `ambientes/` (labs de clase, se copian fuera del repo) y `uv_docker/` (entrega). Ojo: el nombre lleva el cero adelante. |
```

- [ ] **Step 4: Correr y ver que pasa**

Run: `python3 -m pytest tools/test_codigo_python.py -q`
Expected: PASS (6). Y a mano: `uv run codigo/09_python/ambientes/script_autonomo.py` imprime la tabla.

- [ ] **Step 5: Correr la Task 1, Steps 3–4** si se pospusieron.

- [ ] **Step 6: Commit**

```bash
git add codigo/09_python/README.md codigo/09_python/ambientes codigo/README.md tools/test_codigo_python.py
git commit -m "feat(unidad-9): código de laboratorio de ambientes"
```

### Task 3: Comprobar que los IDs nuevos no chocan

**Files:** ninguno (sólo verificación).

- [ ] **Step 1:**

```bash
for id in python ambientes-python el-problema-de-los-ambientes las-piezas-de-un-ambiente \
  un-ambiente-por-dentro los-archivos-del-ambiente las-herramientas-de-ambientes \
  ambiente-conda-docker lab-uv lab-venv-y-pip ambientes-en-vs-code trampas-de-ambientes \
  cheatsheet-ambientes entregas-ambientes datacamp-python-developers uv-en-docker; do
  grep -rlE "^id: $id$|^  - id: $id$" course/ && echo "CHOCA: $id"; done; echo listo
grep -rhoE "\{#py-[a-z0-9-]+" course/ | sort | uniq -d
```

Expected: sólo `listo`, nada de `CHOCA`, ningún `py-` duplicado. Si algo choca, renombra aquí y en todo el plan antes de seguir.

### Task 4: Generador `tools/gen_python.py` con las 4 figuras de clase

Figuras de Fase 1: `py-mapa`, `py-choque`, `py-path`, `py-venv-arbol`. Las otras cuatro entran en la Task 9.

**Files:**
- Create: `tools/gen_python.py`, `tools/test_gen_python.py`, `course/9_python/_assets/{py-mapa,py-choque,py-path,py-venv-arbol}.svg`, `course/9_python/_assets/CREDITOS.md`

**Interfaces:**
- Produces: `DIAGRAMAS: dict[str, Callable[[], str]]`, `escribir(nombre) -> Path`, `main(argv)`. Mismo contrato que `tools/gen_git.py:1069-1110`. `ASSETS = RAIZ / "course/9_python/_assets"`.

- [ ] **Step 1: Test que falla** — copia `tools/test_gen_git.py` a `tools/test_gen_python.py` y cambia:

```python
GENERADOR = RAIZ / "tools/gen_python.py"
ASSETS = RAIZ / "course/9_python/_assets"
UNIDAD = RAIZ / "course/9_python"
# en _cargar(): spec_from_file_location("gen_python", GENERADOR)
# en test_cada_diagrama_declarado_existe_y_lleva_prefijo: prefijo "py-"
# test_el_generador_rechaza_un_nombre_desconocido: "py-no-existe"
```

Reemplaza `test_el_diagrama_de_llaves_advierte_sobre_la_privada` por:

```python
def test_el_mapa_dice_que_va_a_git_y_que_no():
    """El error caro de esta seccion es subir .venv o no subir el lock."""
    svg = (ASSETS / "py-mapa.svg").read_text(encoding="utf-8")
    for pedazo in ("pyproject.toml", "uv.lock", ".venv/", "uv lock", "uv sync",
                   "uv run", "uv add", "PyPI", "no va a git"):
        assert pedazo in svg, f"py-mapa.svg no menciona {pedazo!r}"


def test_el_path_muestra_las_dos_busquedas():
    svg = (ASSETS / "py-path.svg").read_text(encoding="utf-8")
    assert ".venv/bin" in svg and "/usr/bin" in svg and "activate" in svg
```

`test_cada_svg_esta_referenciado_por_alguna_pagina` se queda: **falla hasta la Task 7/8**. Es esperado.

- [ ] **Step 2: Correr y ver que falla**

Run: `python3 -m pytest tools/test_gen_python.py -q`
Expected: FAIL «falta tools/gen_python.py».

- [ ] **Step 3: Escribir el generador.** Encabezado y cierre idénticos en forma a `gen_git.py`:

```python
"""Genera los diagramas SVG de la unidad 9 (Python), seccion de ambientes.

Las primitivas y la paleta salen de tools/svg_base.py. Este archivo es la
unica fuente de verdad de esos SVG: editar un .svg a mano lo detecta
tools/test_gen_python.py. Los ids llevan prefijo "py-" porque los ids de
objeto numerado de Raya son unicos en TODO el curso.
"""
import sys
from pathlib import Path

from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, ROJO, SUAVE, TEXTO, TINTE,
    VIOLETA, caja, chip, cierre, flecha, marco, teclado, texto,
)

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/9_python/_assets"
```

Las cuatro funciones. Lienzo 1080 de ancho; título arriba (`texto(ancho/2, 44, …, TEXTO, 21, peso="600")`); aria-label ≥ 80 caracteres que describe el diagrama en prosa sin acentos (convención de `gen_git.py`).

**`py_mapa()`** — 1080×520. «Qué produce qué en un proyecto uv».
- Tres cajas en fila, `y=110`, `h=150`, `w=280`, en `x=40, 400, 760`:
  1. borde AMBAR, título «lo que pides», `teclado` «pyproject.toml», texto «rangos: rich>=14», «lo escribes tú o uv add».
  2. borde CIAN, «lo que se resolvió», «uv.lock», «versión exacta + hash», «de cada paquete, también las transitivas».
  3. borde ACENTO, «lo que está instalado», «.venv/», «bin/python + site-packages/», «desechable».
- Flechas 1→2 con `chip` «uv lock», 2→3 con `chip` «uv sync».
- Bajo la caja 1, flecha hacia arriba desde «tú» con chip «uv add rich».
- Sobre la caja 2, caja chica VIOLETA «PyPI» con flecha a la caja 2 y texto «de dónde se bajan».
- Desde la caja 3 hacia abajo, flecha con chip «uv run hola.py» a la caja «tu programa».
- Caja chica SUAVE a la izquierda abajo: «uv python install» → «el intérprete también lo pone uv», flecha a la caja 3.
- Franja inferior (y≈470): `✓ pyproject.toml   ✓ uv.lock` en ACENTO y `✗ .venv/ no va a git: se borra y se recrea con uv sync` en ROJO.

**`py_choque()`** — 1080×420. «Dos proyectos, un solo Python».
- Izquierda: dos cajas `proyecto-a` (pide «pandas 1.5») y `proyecto-b` (pide «pandas 2.2»).
- Centro: una caja «Python del sistema», dentro `teclado` «site-packages/» con una sola ranura «pandas ==2.2» en ROJO.
- Flechas de ambos proyectos a la ranura; la de `proyecto-a` termina en ROJO con chip «roto: esperaba 1.5».
- Derecha: lo mismo con dos `.venv/` separados, cada uno con su pandas, ambas flechas ACENTO. Título de columna: «sin ambientes» / «con un .venv por proyecto».

**`py_path()`** — 1080×460. «Qué python gana: la shell busca en orden».
- Dos columnas. Izquierda «sin activar», derecha «después de source .venv/bin/activate».
- Cada columna: lista vertical de 3 cajas numeradas = carpetas del `PATH`, en orden. Izquierda: `/usr/local/bin`, `/usr/bin`, `/bin`; la segunda resaltada AMBAR con «aquí está python3 → gana». Derecha: `~/lab-ambientes/hola/.venv/bin` (primera, ACENTO, «gana»), `/usr/local/bin`, `/usr/bin`.
- Pie: «activate no instala nada: sólo pone .venv/bin al frente del PATH» y, más chico, «uv run no necesita activar: usa el .venv del proyecto directamente».

**`py_venv_arbol()`** — 1080×440. «Un ambiente es una carpeta».
- Árbol en `teclado`, columna izquierda: `.venv/`, `├── bin/` (Windows: `Scripts\`), `│   ├── python → …/python3.13`, `│   └── activate`, `├── lib/python3.13/site-packages/`, `│   └── rich/  pygments/  …`, `└── pyvenv.cfg`.
- Columna derecha, alineado a cada rama, la explicación en `texto` SUAVE: «el intérprete: un enlace al Python base», «lo que corre source», «los paquetes de este ambiente y de ningún otro», «de qué Python salió y su versión».
- Pie: «borrar el ambiente = borrar la carpeta: rm -rf .venv».

```python
DIAGRAMAS = {
    "py-mapa": py_mapa,
    "py-choque": py_choque,
    "py-path": py_path,
    "py-venv-arbol": py_venv_arbol,
}
```

Y `escribir`/`main` copiados de `tools/gen_git.py:1094-1110` sin cambios.

- [ ] **Step 4: Generar** — `python3 tools/gen_python.py` → cuatro líneas `py-*.svg (n KB)`. Abrir cada SVG en el navegador y revisar que nada se encime.

- [ ] **Step 5: CREDITOS.md** — `course/9_python/_assets/CREDITOS.md`, con la forma de `course/8_contenedores/_assets/CREDITOS.md`: título, párrafo «los SVG salen de `tools/gen_python.py`…», tabla `| Archivo | Descripción y prompt resumido | Autor / origen | Fecha | Licencia |` con una fila por SVG: descripción = la especificación de arriba en una oración, `Generado por tools/gen_python.py; obra propia`, `2026-10-01`, `Uso docente del curso`.

- [ ] **Step 6: Correr**

Run: `python3 -m pytest tools/test_gen_python.py tools/test_creditos.py tools/test_svg_tamano_intrinseco.py -q`
Expected: todo PASS salvo `test_cada_svg_esta_referenciado_por_alguna_pagina` (FAIL hasta la Task 8).

- [ ] **Step 7: Commit** (después de la Task 8, junto con las páginas, para no dejar `main` en rojo).

### Task 5: Calendario y horario

**Files:**
- Modify: `course/_official/calendar/1_2026-o26.yaml` (después de `session-12`, línea ~113)
- Modify: `course/0_index.md:22`, `README.md:23-24`

- [ ] **Step 1: La sesión**

```yaml
  - id: session-13
    kind: session
    date: "2026-10-01"
    start_time: "19:00"
    end_time: "20:00"
    title: "Python: ambientes con uv, y qué hay dentro de un .venv"
    page: ambientes-python
```

- [ ] **Step 2: La segunda excepción** — `course/0_index.md:22` pasa a:

```markdown
Hay dos excepciones en todo el semestre, las dos de una hora, de **19:00 a 20:00**: el **jueves 17 de septiembre**, la clase que abre la unidad de contenedores, sin computadora; y el **jueves 1 de octubre**, la clase de ambientes de Python.
```

`README.md:23-24` igual, en su registro: «Hay dos excepciones al horario en todo el semestre: el **jueves 17 de septiembre** y el **jueves 1 de octubre**, las dos de **19:00 a 20:00**.»

- [ ] **Step 3: Validar** — después de la Task 7 (la `page` tiene que resolver):

Run: `cd ~/itam/raya_lucaria && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26`
Expected: sin errores.

### Task 6: Guarda de forma `tools/test_python_curriculum.py`

Se escribe **antes** que las páginas; las páginas se escriben contra ella.

**Files:**
- Create: `tools/test_python_curriculum.py`

**Interfaces:**
- Consumes: las rutas del Mapa de archivos.
- Produces: la definición de «forma de lección» que obedecen las Tasks 7, 8, 10, 13.

**Forma de lección** (páginas 1–10):
1. Línea de posición: `**Página N de 10 · Ambientes**` (N = prefijo del archivo).
2. Línea `Meta: …` (una sola línea).
3. `## En corto` con **1 a 3** viñetas.
4. **Exactamente un** `::: problem {#py-…}` con su `::: hint {of=…}` y su `::: answer {of=…}`.
5. Cierre: penúltima línea no vacía `> [!NOTE]`, última `> **Si sólo recuerdas una cosa:** …`.
6. Puente: «Sigue con [[<id de la siguiente>]]» en las páginas 1–9; la 10 apunta a `[[cheatsheet-ambientes]]`.
7. Topes de líneas: 160; `las-herramientas-de-ambientes`, `lab-uv`, `entregas-ambientes` a 260; `cheatsheet-ambientes` a 320.

- [ ] **Step 1: Escribir la guarda**

```python
"""Guarda de forma de la seccion 9.1 Ambientes (unidad 9, Python).

Las paginas se escriben contra esta guarda: lectores con ADHD, sin analogias,
labs con Haz / Deberias ver, y los labs fuera del repo.
"""
import re
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/9_python"
SECCION = UNIDAD / "1_ambientes"

ORDEN = [  # (archivo, id) en orden de lectura
    ("1_el_problema.md", "el-problema-de-los-ambientes"),
    ("2_las_piezas.md", "las-piezas-de-un-ambiente"),
    ("3_un_ambiente_por_dentro.md", "un-ambiente-por-dentro"),
    ("4_los_archivos.md", "los-archivos-del-ambiente"),
    ("5_las_herramientas.md", "las-herramientas-de-ambientes"),
    ("6_ambiente_conda_docker.md", "ambiente-conda-docker"),
    ("7_lab_uv.md", "lab-uv"),
    ("8_venv_y_pip.md", "lab-venv-y-pip"),
    ("9_vs_code.md", "ambientes-en-vs-code"),
    ("10_las_trampas.md", "trampas-de-ambientes"),
]
ANEXOS = [("11_A_cheatsheet.md", "cheatsheet-ambientes"),
          ("12_B_entregas.md", "entregas-ambientes")]
LABS = {"un-ambiente-por-dentro", "lab-uv", "lab-venv-y-pip"}
TOPE = {"las-herramientas-de-ambientes": 260, "lab-uv": 260,
        "entregas-ambientes": 260, "cheatsheet-ambientes": 320}
ANALOGIAS = ("imagina", "es como", "como si", "analogía", "piensa en",
             "receta", "despensa")

_FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")


def _existentes(pares):
    return [(SECCION / a, i) for a, i in pares if (SECCION / a).is_file()]


LECCIONES = _existentes(ORDEN)
TODAS = LECCIONES + _existentes(ANEXOS)


def _front(p):
    texto = p.read_text(encoding="utf-8")
    return yaml.safe_load(texto.split("---", 2)[1]), texto.split("---", 2)[2]


def _prosa(cuerpo):
    """El cuerpo sin bloques de codigo ni code spans."""
    fuera, dentro = [], False
    for l in cuerpo.splitlines():
        if _FENCE.match(l):
            dentro = not dentro
            continue
        if not dentro:
            fuera.append(re.sub(r"`[^`\n]*`", "", l))
    return "\n".join(fuera)


def _bloques(cuerpo, lenguaje=("bash", "powershell", "text")):
    return re.findall(r"^```(?:%s)\n(.*?)^```" % "|".join(lenguaje),
                      cuerpo, flags=re.M | re.S)


def test_las_paginas_de_clase_existen():
    for a in ("1_el_problema.md", "3_un_ambiente_por_dentro.md",
              "7_lab_uv.md", "9_vs_code.md", "0_index.md"):
        assert (SECCION / a).is_file(), f"falta {a}"
    assert (UNIDAD / "0_index.md").is_file()


@pytest.mark.parametrize("ruta,ident", TODAS, ids=[i for _, i in TODAS])
def test_el_id_es_el_del_plan(ruta, ident):
    assert _front(ruta)[0]["id"] == ident


@pytest.mark.parametrize("ruta,ident", LECCIONES, ids=[i for _, i in LECCIONES])
def test_forma_de_leccion(ruta, ident):
    _, cuerpo = _front(ruta)
    n = int(ruta.name.split("_")[0])
    lineas = [l for l in cuerpo.splitlines() if l.strip()]
    assert f"**Página {n} de 10 · Ambientes**" in cuerpo
    assert any(l.startswith("Meta: ") for l in lineas)
    en_corto = cuerpo.split("## En corto", 1)[1].split("\n## ", 1)[0]
    vinetas = [l for l in en_corto.splitlines() if l.startswith("- ")]
    assert 1 <= len(vinetas) <= 3, f"{ident}: En corto con {len(vinetas)} viñetas"
    problemas = re.findall(r"^::: problem \{#(py-[a-z0-9-]+)", cuerpo, flags=re.M)
    assert len(problemas) == 1, f"{ident}: {len(problemas)} problemas"
    for k in ("hint", "answer"):
        assert f'::: {k} {{of="{problemas[0]}"}}' in cuerpo
    assert lineas[-2] == "> [!NOTE]"
    assert lineas[-1].startswith("> **Si sólo recuerdas una cosa:**")


@pytest.mark.parametrize("i", range(len(ORDEN)))
def test_el_puente_apunta_a_la_siguiente(i):
    ruta = SECCION / ORDEN[i][0]
    if not ruta.is_file():
        pytest.skip("pagina de fase 2 aun no escrita")
    siguiente = ORDEN[i + 1][1] if i + 1 < len(ORDEN) else "cheatsheet-ambientes"
    assert f"Sigue con [[{siguiente}" in ruta.read_text(encoding="utf-8")


@pytest.mark.parametrize("ruta,ident", TODAS, ids=[i for _, i in TODAS])
def test_tope_de_lineas(ruta, ident):
    n = len(ruta.read_text(encoding="utf-8").splitlines())
    assert n <= TOPE.get(ident, 160), f"{ident}: {n} líneas"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=[i for _, i in TODAS])
def test_sin_analogias(ruta, ident):
    prosa = _prosa(_front(ruta)[1]).lower()
    for a in ANALOGIAS:
        assert a not in prosa, f"{ident}: «{a}» — sin analogías: di qué es y muéstralo"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=[i for _, i in TODAS])
def test_sin_html_crudo_ni_dos_pesos_en_prosa(ruta, ident):
    prosa = _prosa(_front(ruta)[1])
    assert not re.search(r"<(?:div|br|iframe|details|span|img)\b", prosa, re.I)
    for l in prosa.splitlines():
        assert l.count("$") < 2, f"{ident}: dos $ en prosa: {l!r}"


@pytest.mark.parametrize("ruta,ident",
                         [(r, i) for r, i in LECCIONES if i in LABS],
                         ids=lambda x: getattr(x, "name", x))
def test_los_labs_alternan_haz_y_deberias_ver(ruta, ident):
    cuerpo = _front(ruta)[1]
    assert cuerpo.count("**Haz:**") >= 3
    assert cuerpo.count("**Deberías ver:**") >= cuerpo.count("**Haz:**")


@pytest.mark.parametrize("ruta,ident", TODAS, ids=[i for _, i in TODAS])
def test_los_labs_no_trabajan_dentro_del_repo(ruta, ident):
    cuerpo = _front(ruta)[1]
    for b in _bloques(cuerpo, ("bash",)):
        for l in b.splitlines():
            if re.search(r"\b(uv init|-m venv)\b", l):
                assert "fdd_o26" not in l and "estudiantes" not in l, (
                    f"{ident}: lab dentro del repo: {l}")
    if ident in LABS:
        assert "~/lab-ambientes" in cuerpo, f"{ident}: el lab no dice dónde trabajar"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=[i for _, i in TODAS])
def test_toda_activacion_trae_su_linea_de_windows(ruta, ident):
    cuerpo = _front(ruta)[1]
    if "source .venv/bin/activate" in cuerpo:
        assert ".venv\\Scripts\\activate" in cuerpo, (
            f"{ident}: activa en Linux/macOS sin decir cómo en Windows")


def test_el_lab_de_uv_dice_su_version():
    ruta = SECCION / "7_lab_uv.md"
    texto = ruta.read_text(encoding="utf-8")
    assert "uv self update" in texto and "uv --version" in texto
    assert re.search(r"uv \d+\.\d+", texto), "di con qué versión se capturaron las salidas"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=[i for _, i in TODAS])
def test_ningun_bloque_pide_sudo(ruta, ident):
    for b in _bloques(_front(ruta)[1]):
        assert not re.search(r"^\s*sudo\b", b, re.M), f"{ident}: sudo en un bloque"


def test_ids_numerados_con_prefijo_py():
    for ruta, ident in TODAS:
        for oid in re.findall(r"\{#([a-z0-9-]+)", ruta.read_text(encoding="utf-8")):
            assert oid.startswith("py-"), f"{ident}: {oid} sin prefijo py-"


def test_el_indice_de_la_seccion_enlaza_cada_pagina_existente():
    indice = (SECCION / "0_index.md").read_text(encoding="utf-8")
    for _, ident in TODAS:
        assert f"[[{ident}" in indice, f"el índice no enlaza {ident}"
```

- [ ] **Step 2: Correr** — `python3 -m pytest tools/test_python_curriculum.py -q` → FAIL (`test_las_paginas_de_clase_existen`). Es lo esperado.

### Task 7: Índices y páginas de clase 1 y 3

**Files:**
- Create: `course/9_python/0_index.md`, `course/9_python/1_ambientes/0_index.md`, `1_el_problema.md`, `3_un_ambiente_por_dentro.md`

**Interfaces:**
- Consumes: figuras `py-mapa`, `py-choque`, `py-path`, `py-venv-arbol` (Task 4); salidas `pep668.txt`, `venv_lab.txt`, `uv_lab.txt` (Task 1); rótulos de `quien_soy.py` (Task 2).

- [ ] **Step 1: `course/9_python/0_index.md`**

```yaml
---
id: python
title: "Python"
nav_title: "Python"
summary: "Python para trabajar con datos de forma profesional. Empieza por lo que todo proyecto necesita antes de su primera línea: un ambiente."
status: ready
estimated_time: 120m
tags: [python, uv, ambientes, venv, pip]
prerequisites: [contenedores]
---
```

Cuerpo: `# Python`; línea «**Una sección por ahora** · 12 páginas»; `## En corto` (3 viñetas: qué es la unidad; 9.1 enseña ambientes con uv; las demás secciones llegan con su clase); tabla `| # | Sección | Qué contesta | Sesión | Páginas | Min |` con una fila: `1 | [[ambientes-python]] | Dónde viven tus paquetes, y cómo hacer que tu proyecto corra igual en otra máquina | jueves 1 de octubre, 19:00–20:00 | 12 | ≈120`. Párrafo «Antes de empezar»: necesitas Docker de la unidad 8 (para la entrega) y **uv instalado antes de clase** — los dos comandos de instalación:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh                 # Linux y macOS
```

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

y `uv --version` como comprobación.

- [ ] **Step 2: `course/9_python/1_ambientes/0_index.md`** — `id: ambientes-python`, `title: "Ambientes"`, `nav_title: "1. Ambientes"`, `summary: "Qué es un ambiente de Python, qué herramientas existen y por qué usamos uv."`.

Cuerpo:
- `**Sección 1** · 12 páginas · unos 120 min · sesión del jueves 1 de octubre, 19:00–20:00`
- `Meta: que sepas en qué Python y con qué paquetes corre tu código, y cómo hacer que corra igual en otra máquina.`
- La figura del mapa:

```markdown
::: figure {#py-mapa title="Qué produce qué en un proyecto uv"}
![<alt largo: describe las tres cajas, los comandos de cada flecha, PyPI, uv python y la franja de git>](../_assets/py-mapa.svg)
:::
```

- `## En corto`: (1) **Un ambiente es una carpeta (`.venv/`) con su propio `python` y sus propios paquetes.** (2) **Usamos uv**: crea el ambiente, instala, fija versiones y pone el intérprete, con un solo programa. (3) A git van `pyproject.toml` y `uv.lock`; **`.venv/` nunca**.
- `## Las páginas` — tabla `| # | Página | Qué agrega | Min | Dónde |`, una fila por página **que exista** (en Fase 1: 1, 3, 7, 9 con «clase»; las 📖 se agregan en la Task 10). Minutos: 1→5, 2→8, 3→15, 4→8, 5→12, 6→6, 7→30, 8→10, 9→10, 10→8, A→5, B→8.
- `## La clase de hoy, en 60 minutos` — tabla: `1 · El problema · 5 min`, `3 · Un ambiente por dentro · 15`, `7 · Lab: uv · 30`, `9 · VS Code · 10`.
- `## Antes de clase` — uv instalado (`uv --version`) y `~/lab-ambientes/` creada con el `cp` de `codigo/09_python/README.md`.

- [ ] **Step 3: `1_el_problema.md`** — `id: el-problema-de-los-ambientes`, `title: "El problema: un solo Python para todo"`, `estimated_time: 5m`, `prerequisites: [ambientes-python]`.

Contenido, en este orden:
1. `**Página 1 de 10 · Ambientes**`
2. `Meta: ver los dos errores que hacen necesarios los ambientes.`
3. Figura `py-choque` («Dos proyectos, un solo Python»).
4. `## En corto`: (1) Sin ambientes, **todos tus proyectos comparten un solo `site-packages/`**: instalar una versión pisa la otra. (2) En Ubuntu 24.04 y en macOS con Homebrew, **el sistema ya no te deja** hacer `pip install` fuera de un ambiente (PEP 668). (3) La salida: un ambiente por proyecto.
5. `## Falla 1: una versión pisa a la otra` — tabla de 3 filas (`proyecto-a` pide `pandas==1.5` / `proyecto-b` pide `pandas==2.2` / en `site-packages` queda sólo la última que instalaste) y dos líneas: el que instaló primero se rompe sin haber cambiado nada.
6. `## Falla 2: el sistema te lo prohíbe` — el comando de la Task 1 Step 2 en un bloque `bash` y su salida real recortada (las líneas `error: externally-managed-environment` … `hint: See PEP 668`) en un bloque `text`. Dos líneas de explicación: el Python del sistema lo usa el propio sistema operativo; si le cambias paquetes puedes romper herramientas del sistema, por eso lo bloquea.
7. `## Lo que vas a usar` — tabla `| Problema | Lo resuelve |`: «versiones que chocan → un `.venv/` por proyecto», «"en mi máquina sí" → `uv.lock` con versiones exactas», «el Python del sistema bloqueado → ni lo tocas: uv trae el suyo».
8. `::: problem {#py-problema-pisa title="¿Quién se rompió?"}`: «Instalaste `pandas==1.5` para la tarea de lunes y el jueves `pandas==2.2` para otra, ambos con `pip install` sin ambiente. El lunes siguiente corres la primera y truena. ¿Qué pasó, si no tocaste su código?» `hint`: «¿Cuántos `site-packages/` hay?». `answer`: «Uno solo. El segundo `pip install` reemplazó 1.5 por 2.2; la tarea del lunes ahora corre con una versión que no conoce. Con un `.venv/` por proyecto, cada uno guarda la suya.»
9. `Sigue con [[las-piezas-de-un-ambiente]], …` — **en Fase 1 la página 2 no existe**: el puente apunta a `[[un-ambiente-por-dentro]]` y se corrige en la Task 10 (el test `test_el_puente_apunta_a_la_siguiente` lo exige al final).
10. Cierre: `> [!NOTE]` / `> **Si sólo recuerdas una cosa:** sin ambientes, todos tus proyectos comparten los mismos paquetes, y el último que instala gana.`

- [ ] **Step 4: `3_un_ambiente_por_dentro.md`** — `id: un-ambiente-por-dentro`, `title: "Un ambiente por dentro"`, `estimated_time: 15m`.

1. `**Página 3 de 10 · Ambientes**` / `Meta: comprobar con tres comandos qué es un ambiente y qué hace «activar».`
2. Figura `py-venv-arbol` («Un ambiente es una carpeta»).
3. `## En corto`: (1) **Un ambiente es una carpeta**, normalmente `.venv/`. (2) Trae **su propio `python` y su propio `site-packages/`**. (3) **Activar sólo cambia el `PATH`**; con `uv run` no hace falta activar.
4. `## Los tres hechos` — tabla:

| Hecho | Lo compruebas con |
|---|---|
| Es una carpeta | `ls -a .venv` y `cat .venv/pyvenv.cfg` |
| Trae su `python` y sus paquetes | `ls .venv/lib/python3.*/site-packages/` |
| Activar = `.venv/bin` al frente del `PATH` | `which python` antes y después de activar |

5. `## Prepara` — **Haz:** (bloque bash):

```bash
cd ~/lab-ambientes
uv init hola && cd hola
uv add rich
```

**Deberías ver:** las líneas reales de `uv_lab.txt` (`Initialized project`, `Resolved N packages`, `+ rich==…`) y una nota: «`uv add` creó `.venv/` sin que se lo pidieras».

6. `## Hecho 1 y 2: es una carpeta con su python` — **Haz:** `ls -a .venv`, `cat .venv/pyvenv.cfg`, `ls .venv/lib/python3.*/site-packages/ | head`. **Deberías ver:** salida real. Lista de 3 viñetas de qué es cada cosa (enlazando a la figura). Windows: `dir .venv\Lib\site-packages` en un bloque `powershell`.

7. `## Hecho 3: activar cambia el PATH` — figura `py-path` («Qué python gana»). **Haz:**

```bash
cp ../quien_soy.py .
python3 quien_soy.py                  # 1. sin activar
source .venv/bin/activate             # Linux / macOS
python quien_soy.py                   # 2. activado
deactivate
uv run quien_soy.py                   # 3. sin activar, con uv run
```

```powershell
.venv\Scripts\activate                # Windows (PowerShell)
```

**Deberías ver:** tabla de 3 filas con lo que cambia en `python que corre`, `sys.prefix`, `¿en un ambiente?` y `rich` — tomado de `uv_lab.txt` / `venv_lab.txt`. El renglón 1 dice `no` y `NO instalado`; 2 y 3 dicen `sí` e `instalado`.

8. `## Lo que de verdad hace activate` — **Haz:** `echo $PATH | tr ':' '\n' | head -3` antes y después de `source .venv/bin/activate`. **Deberías ver:** la primera línea pasa a ser `…/hola/.venv/bin`. Dos líneas: `activate` no instala ni copia nada; sólo cambia en qué orden la shell busca `python`. `uv run` hace lo mismo sin tocar tu shell.

9. `::: problem {#py-activado title="¿Dónde quedó rich?"}`: «Abres una terminal nueva, entras a `~/lab-ambientes/hola` y corres `python hola.py`. Sale `ModuleNotFoundError: No module named 'rich'`. Ayer funcionaba. ¿Qué pasó?» `hint`: «¿Qué te diría `quien_soy.py` en esa terminal?». `answer`: «La terminal nueva no está activada: `python` es el del sistema, que no tiene rich. `rich` sigue en `.venv/`. Arreglo: `uv run hola.py`, o activar primero.»

10. `Sigue con [[los-archivos-del-ambiente]]` — **en Fase 1** apunta a `[[lab-uv]]`; se corrige en la Task 10.
11. Cierre: `**Si sólo recuerdas una cosa:** un ambiente es una carpeta con su propio python; activar sólo cambia cuál python encuentra tu shell.`

- [ ] **Step 5:** `python3 -m pytest tools/test_python_curriculum.py -q -k "problema or por-dentro or indice or analog"` → PASS para las páginas existentes.

### Task 8: Páginas de clase 7 (lab uv) y 9 (VS Code)

**Files:**
- Create: `course/9_python/1_ambientes/7_lab_uv.md`, `9_vs_code.md`

- [ ] **Step 1: `7_lab_uv.md`** — `id: lab-uv`, `title: "Lab: uv de punta a punta"`, `estimated_time: 30m`.

1. `**Página 7 de 10 · Ambientes**` / `Meta: crear, usar, romper y recrear un proyecto uv, y ver en cada paso qué archivo cambió.`
2. Reaparece el mapa como imagen suelta (sin directiva): `![…](../_assets/py-mapa.svg)`.
3. `## En corto`: (1) **`uv add` escribe `pyproject.toml`, resuelve `uv.lock` e instala en `.venv/`**, todo junto. (2) **`uv run` nunca necesita activar**, y si falta `.venv/` lo recrea desde el lock. (3) A git van `pyproject.toml` y `uv.lock`.
4. `## Antes: tu uv` — **Haz:** `uv self update` y `uv --version`. **Deberías ver:** `uv <x.y.z>`. Línea: «Las salidas de esta página se capturaron con **uv <x.y>** y Python <3.13.n>» (de `VERSIONES.txt`). Si instalaste uv con otro gestor (brew, pipx), `uv self update` lo dice; actualiza con ese gestor.
5. Diez pasos `### N. …`, cada uno con **Haz:** (bloque `bash`), **Deberías ver:** (salida real de `uv_lab.txt`, recortada a ≤ 8 líneas en bloque `text`) y una línea **En el mapa:** que dice qué caja cambió:

| # | Título | Haz | En el mapa |
|---|---|---|---|
| 1 | El intérprete | `uv python list` · `uv python install 3.13` | uv pone el Python: no hace falta el del sistema |
| 2 | Un proyecto | `cd ~/lab-ambientes && uv init demo && cd demo && ls -a && cat pyproject.toml` | aparece `pyproject.toml`; no hay `.venv/` todavía |
| 3 | Un paquete | `uv add rich && ls -a && cat pyproject.toml` | `pyproject.toml` gana `rich>=…`; nacen `uv.lock` y `.venv/` |
| 4 | Correr | `cp ../hola.py . && uv run hola.py` | `uv run` usa `.venv/` sin activar |
| 5 | Leer el lock | `grep -c '^\[\[package\]\]' uv.lock && uv tree` | pediste 1 paquete y el lock trae N: las **transitivas** |
| 6 | Romperlo | `rm -rf .venv && uv run hola.py` | `.venv/` se recrea desde `uv.lock`: por eso no va a git |
| 7 | Dependencias de desarrollo | `uv add --dev pytest && tail -4 pyproject.toml` | `[dependency-groups]`: lo que sólo tú necesitas, no el programa |
| 8 | Quitar | `uv remove rich && uv run hola.py` | `ModuleNotFoundError`: se fue del toml, del lock y de `.venv/`. Luego `uv add rich` |
| 9 | Una herramienta sin instalarla | `uvx cowsay -t hola` | `uvx` corre un programa en un ambiente temporal; no toca tu proyecto |
| 10 | Un script con sus dependencias dentro | `cp ../script_autonomo.py ~/lab-ambientes/ && cd ~/lab-ambientes && uv run script_autonomo.py` | el bloque `# /// script` hace de `pyproject.toml` (PEP 723) |

6. `## Puente al mundo de pip` — dos comandos con una línea cada uno: `uv pip install rich` (la interfaz de pip, sobre el ambiente activo o `.venv/`) y `uv export --no-hashes > requirements.txt` (para quien sólo tiene pip). Salida real de `uv export` (3–6 líneas).
7. `## Qué subes a git` — tabla: `pyproject.toml ✅ · uv.lock ✅ · .venv/ ❌ (ya está en .gitignore del curso y la revisión lo rechaza)` · `.python-version ✅`.
8. `::: problem {#py-lab-uv-clon title="Lo clonaste en otra máquina"}`: «Tu compañero clona tu repo: trae `pyproject.toml` y `uv.lock`, sin `.venv/`. ¿Qué comando corre para tener exactamente tus versiones, y por qué no `uv add rich`?» `hint`: «¿Qué archivo tiene las versiones exactas?». `answer`: «`uv sync` (o directo `uv run hola.py`): instala lo que dice `uv.lock`. `uv add` volvería a resolver y podría escoger una versión más nueva.»
9. `Sigue con [[lab-venv-y-pip]]` — en Fase 1 apunta a `[[ambientes-en-vs-code]]`; se corrige en la Task 10.
10. Cierre: `**Si sólo recuerdas una cosa:** pyproject.toml dice lo que pides, uv.lock lo que exactamente se instaló, y .venv/ se tira y se recrea con uv sync.`

- [ ] **Step 2: `9_vs_code.md`** — `id: ambientes-en-vs-code`, `title: "Ambientes en VS Code"`, `estimated_time: 10m`. Página sin labs con `Haz` obligatorio pero con pasos:

1. Posición / `Meta: que VS Code use el .venv de tu proyecto, y saber verlo.`
2. `## En corto`: (1) **Ctrl+Shift+P** (macOS: **Cmd+Shift+P**) → *Python: Select Interpreter* → el `.venv` del proyecto. (2) **El intérprete activo se ve abajo a la derecha**, en la barra de estado. (3) La terminal integrada **se activa sola** con ese intérprete.
3. `## Requisito` — la extensión *Python* de Microsoft (`ms-python.python`). Una línea.
4. `## Elegir el ambiente que hizo uv` — lista numerada: abrir la carpeta del proyecto (`code ~/lab-ambientes/demo`), Ctrl+Shift+P, escribir `Python: Select Interpreter`, elegir la opción con `./.venv/bin/python` (Windows: `.\.venv\Scripts\python.exe`), comprobar en la barra de estado.
5. `## Crear uno desde VS Code` — *Python: Create Environment* → *Venv* → versión → (opcional) `requirements.txt`. Una línea: **crea un `.venv` con venv + pip, no con uv**; en este curso el proyecto lo hace uv y VS Code sólo lo **elige**.
6. `## Comprobar` — tabla `| Dónde | Qué ves si está bien |`: barra de estado → `3.13.x ('.venv': venv)`; terminal integrada nueva → `(demo)` al inicio del prompt; `quien_soy.py` con ▶ → `¿en un ambiente? : sí`; notebook → kernel *Select Kernel* → el mismo `.venv` (necesita `uv add --dev ipykernel`).
7. `::: problem {#py-vscode-rojo title="Subrayado en rojo"}`: «`import rich` sale subrayado en rojo en VS Code, pero `uv run hola.py` funciona. ¿Qué está mal?» `hint`: «¿Qué intérprete dice la barra de estado?». `answer`: «VS Code está usando otro Python (el del sistema). Select Interpreter → `.venv`. El código estaba bien.»
8. `Sigue con [[trampas-de-ambientes]]`. Cierre: `**Si sólo recuerdas una cosa:** VS Code no adivina tu ambiente: se lo dices con Select Interpreter y lo compruebas en la barra de estado.`

- [ ] **Step 3: Ajustar puentes de Fase 1** — mientras 2, 4, 5, 6, 8, 10 no existan: 1→3, 3→7, 7→9, 9→cheatsheet no existe: 9 cierra con `Sigue con [[ambientes-python|el índice de la sección]]`. `test_el_puente_apunta_a_la_siguiente` se queda en rojo para 1, 3, 7, 9 hasta la Task 10 — **márcalo `xfail` temporal** en la Task 6 con la condición `not (SECCION / ORDEN[i+1][0]).is_file()`:

```python
    if i + 1 < len(ORDEN) and not (SECCION / ORDEN[i + 1][0]).is_file():
        pytest.xfail("la siguiente pagina es de fase 2")
```

- [ ] **Step 4: Validar y construir**

```bash
python3 tools/gen_python.py
python3 -m pytest tools/ -q
cd ~/itam/raya_lucaria && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26
```

Expected: pytest todo verde (más los xfail de puentes); validate y build sin errores. Revisar `artifact/site/python/ambientes/` en `raya preview`: figuras visibles, tablas sin romper.

- [ ] **Step 5: Commit de Fase 1**

```bash
git add course/9_python tools/gen_python.py tools/test_gen_python.py tools/test_python_curriculum.py \
  course/_official/calendar/1_2026-o26.yaml course/0_index.md README.md
git commit -m "feat(unidad-9): sección 9.1 ambientes, páginas de clase y sesión del 1 de octubre"
```

**Avisar al profesor**: la clase está publicable. Push lo decide él.

---

## FASE 2 · Lectura (después de clase)

### Task 9: Las cuatro figuras restantes

**Files:**
- Modify: `tools/gen_python.py` (4 funciones + 4 entradas en `DIAGRAMAS`), `course/9_python/_assets/CREDITOS.md` (4 filas)
- Create: `course/9_python/_assets/{py-trabajos,py-cual-uso,py-aislamiento,py-uv-docker}.svg`

- [ ] **Step 1: Tests nuevos** en `tools/test_gen_python.py`:

```python
def test_la_matriz_nombra_las_herramientas_y_los_cinco_trabajos():
    svg = (ASSETS / "py-trabajos.svg").read_text(encoding="utf-8")
    for h in ("pip", "venv", "poetry", "pdm", "hatch", "conda", "pixi",
              "pyenv", "pipx", "uv"):
        assert h in svg, h
    for t in ("instalar paquetes", "aislar", "proyecto + lock",
              "versiones de Python", "herramientas de terminal"):
        assert t in svg, t


def test_el_dockerfile_copia_el_lock_antes_que_el_codigo():
    svg = (ASSETS / "py-uv-docker.svg").read_text(encoding="utf-8")
    assert svg.index("uv.lock") < svg.index("uv sync --locked") < svg.index("reporte.py")
```

- [ ] **Step 2:** `python3 -m pytest tools/test_gen_python.py -q` → FAIL.

- [ ] **Step 3: Las funciones**

**`py_trabajos()`** — 1080×560. Matriz: filas = `pip`, `venv`, `pip-tools`, `pipenv`, `poetry`, `pdm`, `hatch`, `conda`, `pixi`, `pyenv`, `pipx`, `uv`; columnas = «instalar paquetes», «aislar», «proyecto + lock», «versiones de Python», «herramientas de terminal». Celda llena (`celda(..., "●", ACENTO)`) donde la herramienta hace ese trabajo, vacía donde no. Valores:

| | instalar | aislar | proyecto+lock | versiones Py | CLIs |
|---|---|---|---|---|---|
| pip | ● | | | | |
| venv | | ● | | | |
| pip-tools | | | ● (sólo lock) | | |
| pipenv | ● | ● | ● | | |
| poetry | ● | ● | ● | | |
| pdm | ● | ● | ● | ● | |
| hatch | ● | ● | ● | ● | |
| conda | ● | ● | ◐ | ● | |
| pixi | ● | ● | ● | ● | ● |
| pyenv | | | | ● | |
| pipx | ● | ● | | | ● |
| uv | ● | ● | ● | ● | ● |

La fila `uv` con fondo TINTE. Pie: «conda y pixi instalan además paquetes que no son de Python (CUDA, GDAL); uv no».

**`py_cual_uso()`** — 1080×460. Árbol de decisión de tres preguntas en rombos/cajas: «¿necesitas paquetes que no son de Python (CUDA, GDAL)?» sí → «pixi (o conda)»; no → «¿el proyecto ya usa poetry / pdm / hatch?» sí → «usa esa: lee su pyproject.toml»; no → «¿es un script suelto?» sí → «uv run script.py (PEP 723)»; no → caja ACENTO «uv init + uv add».

**`py_aislamiento()`** — 1080×460. Cuatro capas apiladas de abajo arriba: «kernel», «librerías y programas del sistema», «intérprete de Python», «paquetes de Python». Tres columnas a la derecha (`.venv` de uv, `conda / pixi`, `Docker`) con una barra vertical que cubre las capas que aísla: `.venv` sólo paquetes (y el intérprete si uv lo instaló: rayado), conda/pixi paquetes + intérprete + parte de las librerías, Docker todo menos el kernel. Pie: «ninguno aísla el kernel: eso es una máquina virtual».

**`py_uv_docker()`** — 1080×480. El Dockerfile de la tarea como cinco cajas apiladas, una por instrucción, en `teclado`: `FROM python:3.13-slim`, `COPY --from=ghcr.io/astral-sh/uv:<x.y> /uv /usr/local/bin/uv`, `COPY pyproject.toml uv.lock ./`, `RUN uv sync --locked`, `COPY reporte.py ./`. A la derecha de las cajas 3–4 una llave AMBAR «capa cacheada: sólo se rehace si cambia el lock»; a la derecha de la 5 «cambia cada vez que editas el código». Abajo, caja ROJA: «.venv/ de tu máquina: fuera (.dockerignore)».

```python
DIAGRAMAS.update({
    "py-trabajos": py_trabajos,
    "py-cual-uso": py_cual_uso,
    "py-aislamiento": py_aislamiento,
    "py-uv-docker": py_uv_docker,
})
```

(o agregarlas en el literal del dict, que es la forma de `gen_git.py` — preferible).

- [ ] **Step 4:** `python3 tools/gen_python.py` y 4 filas en `CREDITOS.md`.
- [ ] **Step 5:** `python3 -m pytest tools/test_gen_python.py tools/test_creditos.py -q` → PASS salvo «referenciado por alguna página» (se arregla en las Tasks 10 y 13).

### Task 10: Páginas de lectura 2, 4, 5, 6, 8, 10 y la Cheatsheet

**Files:**
- Create: `course/9_python/1_ambientes/{2_las_piezas,4_los_archivos,5_las_herramientas,6_ambiente_conda_docker,8_venv_y_pip,10_las_trampas,11_A_cheatsheet}.md`
- Modify: `1_ambientes/0_index.md` (filas), puentes de `1_el_problema.md`, `3_un_ambiente_por_dentro.md`, `7_lab_uv.md`, `9_vs_code.md`; quitar el `xfail` de la Task 8 Step 3.

Cada página: forma de lección (Task 6). Lo que va en cada una:

- [ ] **Step 1: `2_las_piezas.md`** — `las-piezas-de-un-ambiente`, 8 min. `Meta: nombrar cada pieza y saber dónde verla en tu máquina.` Sin figura numerada propia. `## En corto`: (1) Nueve palabras y dónde ver cada una. (2) **Un paquete es código de otros instalado en `site-packages/`**. (3) **Un lockfile fija la versión exacta de cada paquete**, también los que no pediste. Tabla principal `::: table {#py-tabla-piezas title="Las piezas"}`:

| Término | Qué es | Lo ves con |
|---|---|---|
| Intérprete | El programa `python` que ejecuta tu código | `which python` · `python --version` |
| Paquete | Código de otros, instalado como carpeta en `site-packages/` | `ls .venv/lib/python3.*/site-packages/` |
| PyPI | El registro público de paquetes de Python (pypi.org) | `uv add rich` lo baja de ahí |
| pip | El instalador que viene con Python | `pip --version` |
| Dependencia transitiva | Un paquete que no pediste, pero que pide uno que sí | `uv tree` |
| Ambiente | Una carpeta con su intérprete y sus paquetes, aparte del sistema | `ls .venv` |
| Resolver | La parte del gestor que escoge versiones compatibles entre sí | `uv lock` |
| Lockfile | Archivo con la versión exacta y el hash de cada paquete | `cat uv.lock` |
| TOML | Formato de texto de configuración (`clave = valor`, `[secciones]`) | `cat pyproject.toml` |

Después: `## pip y uv, frente a frente` (tabla de 4 filas: instalar, crear ambiente, fijar versiones, poner Python — pip: sí/no (venv)/no (freeze aproximado)/no; uv: sí/sí/sí/sí). Problem `py-piezas-transitiva`: «Pediste sólo `rich`. ¿Por qué `uv.lock` tiene `pygments`?» Cierre: «paquete, ambiente y lockfile son tres cosas distintas: código, carpeta y lista exacta».

- [ ] **Step 2: `4_los_archivos.md`** — `los-archivos-del-ambiente`, 8 min. `## En corto`: (1) **`pyproject.toml` es el estándar** (PEP 621): lo leen uv, poetry, pdm y hatch. (2) **El lock lo escribe la herramienta, nunca tú.** (3) `requirements.txt` es el formato viejo de pip, y sigue en todos lados. Tabla `::: table {#py-tabla-archivos title="Los archivos de un proyecto de Python"}`:

| Archivo | Qué es | Lo escribe | ¿Versiones exactas? | ¿A git? |
|---|---|---|---|---|
| `requirements.txt` | Lista de paquetes, uno por línea; formato de pip | tú, o `pip freeze` | sólo si usas `==` | ✅ |
| `pyproject.toml` | Nombre, versión de Python y dependencias del proyecto (PEP 621) | tú o `uv add` | ❌ rangos | ✅ |
| `uv.lock` · `poetry.lock` · `pdm.lock` | Lock propio de cada herramienta | la herramienta | ✅ con hash | ✅ |
| `pylock.toml` | Lock **estándar** (PEP 751, aceptado en 2025); uv lo exporta | la herramienta | ✅ con hash | ✅ |
| `environment.yml` | Lo mismo para conda | tú o `conda env export` | depende | ✅ |
| `.python-version` | Qué versión de Python usa el proyecto | `uv python pin` | ✅ | ✅ |

Luego `## Un pyproject.toml, línea por línea` — el `pyproject.toml` real de la Task 1 Step 3 (después de `uv add rich` y `uv add --dev pytest`) en bloque `toml`, y debajo una tabla `| Línea | Qué dice |`. Luego `## [tool.*]: lo que no es estándar` — 3 líneas: `[project]` y `[dependency-groups]` son estándar; `[tool.uv]`, `[tool.poetry]`, `[tool.ruff]` son configuración propia de cada herramienta; y un ejemplo de 6 líneas de cómo se ve un `pyproject.toml` de **poetry** (sección `[tool.poetry]` + `[build-system]`) para reconocerlo. Luego `## requirements.txt, ida y vuelta` — `uv export --no-hashes > requirements.txt` y `uv add -r requirements.txt`. Problem `py-archivos-lock`: «¿Por qué no basta `rich>=14` en `pyproject.toml` para que dos máquinas tengan lo mismo?» Cierre: «pyproject.toml pide rangos; el lock fija versiones exactas; a git van los dos».

- [ ] **Step 3: `5_las_herramientas.md`** — `las-herramientas-de-ambientes`, 12 min, tope 260. Figuras `py-trabajos` y `py-cual-uso`. `## En corto`: (1) Cada herramienta resuelve **uno o varios de cinco trabajos**. (2) **uv hace los cinco, y rápido**; no instala paquetes que no son de Python. (3) Las vas a ver todas en proyectos ajenos: hay que reconocerlas, no dominarlas. Tabla grande `::: table {#py-tabla-herramientas title="Las herramientas, con pros y contras"}`, columnas `Herramienta | Desde | Qué hace | 👍 | 👎 | Dónde la vas a ver`:

| Herramienta | Desde | Qué hace | 👍 | 👎 | Dónde la vas a ver |
|---|---|---|---|---|---|
| pip | 2008 | Instala paquetes de PyPI | Viene con Python | No aísla, no fija versiones transitivas | Todos los tutoriales |
| venv | 2012 (Python 3.3) | Crea ambientes | Viene con Python | Sólo aísla; lo demás lo haces tú | READMEs, Dockerfiles |
| pip-tools | 2012 | `requirements.in` → `requirements.txt` fijado | Simple, sobre pip | Sólo hace eso | Proyectos maduros |
| pipenv | 2017 | pip + venv + lock (`Pipfile`) | Fue el primer todo-en-uno | Lento; perdió impulso | Proyectos de 2018–2020 |
| poetry | 2018 | Proyecto, lock, publicar paquetes | Maduro, muy usado | Más lento; formato propio antes de la v2 (2025) | Muchas empresas |
| pdm | 2019 | Proyecto + lock, apegado al estándar | Muy estándar | Comunidad chica | Librerías |
| hatch | 2017 | Proyecto, ambientes de prueba, publicar | El mejor para publicar librerías | Menos para apps | Librerías open source |
| conda / mamba | 2012 | Paquetes de Python **y no-Python**, con su propio Python | CUDA, GDAL, R | Pesado; otro ecosistema; la distribución Anaconda cobra licencia a organizaciones grandes (términos de 2024) | Ciencia, academia |
| pixi | 2023 | Paquetes conda, rápido, con lockfile | Lo de conda con flujo moderno | Joven | GPU, geoespacial |
| pyenv | 2012 | Instala versiones de Python | Hace bien una cosa | uv ya lo hace | Máquinas de devs |
| pipx | 2017 | Instala programas de terminal aislados | Sencillo | uv tiene `uvx` | `pipx install ruff` |
| **uv** | 2024 | **Los cinco trabajos** | 10–100× más rápido que pip; un binario; sigue los estándares | De una empresa (Astral), que OpenAI anunció comprar el 2026-03-19; no instala paquetes no-Python | **Este curso** |

`## Por qué uv` (3 viñetas, cada una con su dato: velocidad, un solo programa, estándares `pyproject.toml`/`pylock.toml`) y `## Lo que uv no te da` (2 viñetas: paquetes no-Python → pixi; el riesgo de depender de una empresa → los archivos son estándar: si mañana cambias de herramienta, `pyproject.toml` se queda). Una línea: «rye existió (2023) y se fundió en uv». Luego `py-cual-uso`. Fuentes al pie: pydevtools handbook, el anuncio de OpenAI, docs de uv (URLs del spec). Problem `py-herramientas-elige`: tres proyectos (un notebook con CUDA, un repo con `poetry.lock`, tu tarea) → ¿qué herramienta en cada uno? Cierre: «las herramientas cambian; pyproject.toml se queda».

- [ ] **Step 4: `6_ambiente_conda_docker.md`** — `ambiente-conda-docker`, 6 min. Figura `py-aislamiento`. `## En corto`: (1) **Un `.venv` aísla paquetes de Python; nada más.** (2) conda/pixi agregan el intérprete y librerías del sistema. (3) **Docker aísla todo menos el kernel**, y adentro también se usa uv. Una línea que remite a la tabla de la unidad 8: «La comparación con `venv` ya apareció en [[en-mi-maquina-si-funciona]]; aquí se agrega uv y pixi.» Tabla `::: table {#py-tabla-aislamiento title="Qué aísla cada uno"}`:

| Qué queda aislado | `.venv` (uv) | conda / pixi | Docker |
|---|---|---|---|
| Paquetes de Python | ✅ | ✅ | ✅ |
| Versión del intérprete | ✅ si la instaló uv | ✅ | ✅ |
| Librerías del sistema (`libc`, CUDA) | ❌ | ✅ las que empaqueta | ✅ |
| Programas (`bash`, `grep`) y sistema de archivos | ❌ | ❌ | ✅ |
| Procesos y red | ❌ | ❌ | ✅ |
| Kernel | ❌ | ❌ | ❌ |

`## Se combinan` — 3 líneas: en Docker se crea un `.venv` con uv dentro de la imagen; eso es la entrega `tarea-09-uv-docker` ([[entregas-ambientes]] — en Fase 2 el tablero aún no existe: enlazar en la Task 13). Problem `py-aislamiento-libc`: «Tu código usa una librería que necesita `libgdal` del sistema. ¿Te basta con `uv.lock`?» Cierre: «cada herramienta aísla una capa más; elige la que cubre lo que se te rompe».

- [ ] **Step 5: `8_venv_y_pip.md`** — `lab-venv-y-pip`, 10 min. Lab con ≥ 3 Haz/Deberías ver, salidas de `venv_lab.txt`. `## En corto`: (1) **`python -m venv` + `pip` es la forma clásica**: la vas a ver en casi todo README. (2) **`pip` instala en el Python que esté primero en el `PATH`**, activado o no. (3) uv hace lo mismo con menos pasos. Tramos: `### 1. Crear y activar` (`cd ~/lab-ambientes && python3 -m venv .venv && source .venv/bin/activate` + bloque `powershell` con `.venv\Scripts\activate`; deberías ver `(.venv)` en el prompt y `quien_soy.py` → `sí`). `### 2. Instalar y congelar` (`pip install -r requirements.txt`, `python hola.py`, `pip freeze`). `### 3. El experimento: pip sin activar` — **Predice** en una línea antes de correr: «¿dónde va a instalar?». Haz: `deactivate`, `python3 -m pip install rich`. Deberías ver dos casos, tabla: en Ubuntu/Homebrew → `externally-managed-environment` (página 1); en otros sistemas o en Windows → **instala en el Python global**, y `quien_soy.py` lo confirma (`¿en un ambiente? : no`, `rich : instalado`). Esa es la trampa. `### 4. Desactivar y borrar` (`deactivate`, `rm -rf .venv`; Windows `Remove-Item -Recurse .venv`). Tabla final `| Paso | venv + pip | uv |` con 5 filas (crear, activar, instalar, fijar, recrear). Problem `py-pip-global`. Cierre: «pip instala donde apunta tu PATH; si no sabes dónde es, corre quien_soy.py antes».

- [ ] **Step 6: `10_las_trampas.md`** — `trampas-de-ambientes`, 8 min. `## En corto`: (1) Casi todo error de ambientes es **«corriste otro Python del que crees»**. (2) `quien_soy.py` lo diagnostica en un segundo. (3) La tabla dice síntoma → causa → dónde mirar. Tabla `::: table {#py-tabla-trampas title="Síntoma, causa y dónde mirar"}` con estas 9 filas:

| Síntoma | Causa | Dónde mirar |
|---|---|---|
| `ModuleNotFoundError` con el paquete «instalado» | Corres otro Python: terminal sin activar, o VS Code con otro intérprete | `quien_soy.py`; barra de estado de VS Code |
| `error: externally-managed-environment` | `pip install` sobre el Python del sistema (PEP 668) | [[el-problema-de-los-ambientes]] |
| `pip install` «funcionó» pero el programa no lo ve | `pip` y `python` son de Pythons distintos | `python -m pip --version` |
| `python: command not found` | En tu sistema se llama `python3`, o no hay ambiente activo | `which python3` |
| PowerShell: «la ejecución de scripts está deshabilitada» al activar | ExecutionPolicy de Windows | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| La revisión rechaza tu PR por `.venv` | Subiste el ambiente al repo | [[lab-uv]], «Qué subes a git» |
| La imagen Docker trae un `.venv` que no corre | `COPY . .` copió tu `.venv` de tu máquina | `.dockerignore`; [[entregas-ambientes]] |
| `uv sync --locked` falla: «lockfile needs to be updated» | Cambiaste `pyproject.toml` y no regeneraste `uv.lock` | `uv lock` |
| Dos proyectos y las versiones «se mezclan» | Los dos usan el mismo ambiente (o ninguno) | `ls` en cada proyecto: ¿cada uno tiene su `.venv/`? |

La fila de `.venv` en Docker enlaza al tablero (Task 13); en Fase 2, sin enlace. Problem `py-trampa-diagnostico`. Puente: `Sigue con [[cheatsheet-ambientes]]`. Cierre: «antes de reinstalar nada, pregunta qué Python está corriendo».

- [ ] **Step 7: `11_A_cheatsheet.md`** — `cheatsheet-ambientes`, `title: "Cheatsheet de ambientes"`, `nav_title: "A. Cheatsheet"`, 5 min. **No** es lección (sin forma, sin problem). Una línea de propósito, y `::: table {#py-cheatsheet title="La misma tarea en cada herramienta"}`:

| Tarea | uv | venv + pip | poetry | conda |
|---|---|---|---|---|
| Instalar Python | `uv python install 3.13` | (instalador del sistema) | (externo) | `conda create -n x python=3.13` |
| Nuevo proyecto | `uv init` | `mkdir x && cd x` | `poetry new x` | — |
| Crear ambiente | (automático) / `uv venv` | `python -m venv .venv` | (automático) | `conda create -n x` |
| Activar | no hace falta: `uv run` | `source .venv/bin/activate` · Windows `.venv\Scripts\activate` | `poetry shell` (plugin en v2) | `conda activate x` |
| Agregar paquete | `uv add rich` | `pip install rich` | `poetry add rich` | `conda install rich` |
| Quitar | `uv remove rich` | `pip uninstall rich` | `poetry remove rich` | `conda remove rich` |
| Dependencia de desarrollo | `uv add --dev pytest` | (otro requirements) | `poetry add --group dev pytest` | — |
| Instalar desde el lock | `uv sync` | `pip install -r requirements.txt` | `poetry install` | `conda env create -f environment.yml` |
| Correr | `uv run x.py` | `python x.py` (activado) | `poetry run python x.py` | `python x.py` (activado) |
| Ver el árbol | `uv tree` | `pip list` | `poetry show --tree` | `conda list` |
| Exportar requirements | `uv export > requirements.txt` | `pip freeze > requirements.txt` | `poetry export` (plugin) | `conda env export` |
| Herramienta suelta | `uvx ruff` | `pipx run ruff` | — | — |
| Borrar el ambiente | `rm -rf .venv` | `deactivate && rm -rf .venv` | `poetry env remove --all` | `conda env remove -n x` |

Cada comando de poetry/conda en esta tabla se verifica contra su documentación actual en la Task 14 (el agente «IA sin leer» lo revisa); si uno cambió, se corrige.

- [ ] **Step 8: Índice y puentes** — agrega las filas de 2, 4, 5, 6, 8, 10, A al índice de la sección, corrige los puentes 1→2, 3→4, 7→8, 9→10, y borra el `xfail` de la Task 8 Step 3.

- [ ] **Step 9: Verificar**

```bash
python3 -m pytest tools/ -q
cd ~/itam/raya_lucaria && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

Expected: verde, salvo `py-uv-docker` no referenciado (se arregla en la Task 13). Si molesta, mover `py-uv-docker` a la Task 13.

- [ ] **Step 10: Commit**

```bash
git add course/9_python tools/gen_python.py tools/test_gen_python.py tools/test_python_curriculum.py
git commit -m "feat(unidad-9): páginas de lectura de ambientes, cheatsheet y figuras"
```

---

## FASE 3 · Las entregas (skill `crear_tarea`)

### Task 11: `tarea-09-datacamp-python` (las seis piezas menos el tablero)

**Files:**
- Create: `codigo/python/certificaciones.md`, `course/9_python/_official/assignments/1_datacamp_python.yaml`, `.github/tareas/tarea-09-datacamp-python.toml`
- Modify: `.github/workflows/entregas.yml` (`TAREAS`), `codigo/README.md` (fila `python/`), `tools/test_revisa_ficha.py`

- [ ] **Step 1: Tests que fallan** — al final de `tools/test_revisa_ficha.py`:

```python
# --------------------------------------------------------------------------
# tarea-09-datacamp-python
# --------------------------------------------------------------------------

PLANTILLA_PY = (RAIZ / "codigo/python/certificaciones.md").read_text(encoding="utf-8")
URL_SOA = "https://www.datacamp.com/completed/statement-of-accomplishment/course/abc123"


def _py_bien(fecha="2026-10-04", url=URL_SOA, aprendi="Que un dict conserva el orden de inserción."):
    t = PLANTILLA_PY.replace(
        "Fecha en que lo terminaste (AAAA-MM-DD):",
        f"Fecha en que lo terminaste (AAAA-MM-DD): {fecha}")
    t = t.replace("URL del Statement of Accomplishment:",
                  f"URL del Statement of Accomplishment: {url}")
    t = t.replace("- Nombre:", "- Nombre: Ana")
    return t.replace("Se llena en esta entrega. Dos o tres líneas", aprendi + "\n\nSe llena en esta entrega. Dos o tres líneas")


def test_py_bien_entregada_pasa(monkeypatch, capsys):
    assert _main(monkeypatch, "tarea-09-datacamp-python", {
        "estudiantes/ana/python/certificaciones.md": _py_bien(),
        "estudiantes/ana/python/introduccion-python-developers.png": PNG,
    }) == 0


def test_py_plantilla_sin_tocar_falla(monkeypatch, capsys):
    assert _main(monkeypatch, "tarea-09-datacamp-python", {
        "estudiantes/ana/python/certificaciones.md": PLANTILLA_PY,
        "estudiantes/ana/python/introduccion-python-developers.png": PNG,
    }) == 1


def test_py_fecha_no_iso_falla(monkeypatch, capsys):
    assert _main(monkeypatch, "tarea-09-datacamp-python", {
        "estudiantes/ana/python/certificaciones.md": _py_bien(fecha="4 de octubre"),
        "estudiantes/ana/python/introduccion-python-developers.png": PNG,
    }) == 1


def test_py_sin_url_falla(monkeypatch, capsys):
    assert _main(monkeypatch, "tarea-09-datacamp-python", {
        "estudiantes/ana/python/certificaciones.md": _py_bien(url=""),
        "estudiantes/ana/python/introduccion-python-developers.png": PNG,
    }) == 1


def test_py_sin_captura_falla(monkeypatch, capsys):
    assert _main(monkeypatch, "tarea-09-datacamp-python", {
        "estudiantes/ana/python/certificaciones.md": _py_bien(),
    }) == 1
```

`_main` usa `HOY` implícito del script (fecha real). Para que ningún test dependa del día, fija la fecha: si `rf.main()` lee `datetime.date.today()`, agrega en `_main` `monkeypatch.setattr(rf, "_hoy", lambda: datetime.date(2026, 10, 5))` **sólo si** el script expone `_hoy`; si no, la fecha `2026-10-04` de `_py_bien` nunca es futura después del 2026-10-05 y basta. Verifícalo leyendo `revisa_ficha.py:747-822` antes de escribir.

Y agrega `"uv "` a `PALABRAS_DE_RECETA`.

- [ ] **Step 2:** `python3 -m pytest tools/test_revisa_ficha.py -q` → FAIL (no existe la plantilla).

- [ ] **Step 3: Plantilla `codigo/python/certificaciones.md`**

```markdown
# Certificaciones de Python

Llena este archivo en **tu copia**, dentro de `estudiantes/<tu-login>/python/`.

## Quién soy

- Nombre:
- Usuario de GitHub:
- Correo con el que entraste a DataCamp:

## Introduction to Python for Developers

Fecha en que lo terminaste (AAAA-MM-DD):

URL del Statement of Accomplishment:

![Captura del curso Introduction to Python for Developers terminado](./introduccion-python-developers.png)

## Una cosa que aprendiste y no sabías

Se llena en esta entrega. Dos o tres líneas: algo concreto del curso que no
sabías, o que tenías a medias y ahí se te acomodó.
```

Fila en `codigo/README.md`: `| \`python/\` | 09 — Python | Certificaciones de Python, de acumulación por entrega. |`

- [ ] **Step 4: YAML `course/9_python/_official/assignments/1_datacamp_python.yaml`** — misma forma que `course/8_contenedores/_official/assignments/1_datacamp_intro_docker.yaml`:

```yaml
id: datacamp-python-developers
type: assignment
authority: official
content:
  title: "DataCamp: Introduction to Python for Developers"
  instructions: >-
    <ocho párrafos en este orden, prosa sin listas ni tablas, deletreando
    nombres de archivo y branch como en la unidad 8:>
    (1) Qué: terminar el curso y subir la evidencia; para qué: la unidad 9 da
    por sabida la sintaxis básica que el curso entrena.
    (2) Carpeta: python, dentro de tu carpeta de estudiante, espejo de la que
    está en codigo; se copia con la barra y el punto al final del origen; ojo:
    es python, no nueve guion bajo python, que es la de la otra entrega.
    (3) Qué entregar: certificaciones punto md con las tres secciones llenas
    (quién soy; la fecha en formato año guion mes guion día y la URL del
    Statement of Accomplishment; una cosa que aprendiste), y la captura
    introduccion guion python guion developers punto png, con ese nombre exacto
    porque la plantilla ya la enlaza; si sale en jpg, corrige el enlace.
    (4) Qué no: nada más; la captura es la página del curso terminado con tu
    nombre y el cien por ciento, no un certificado suelto ni un ejercicio.
    (5) Branch: tarea guion cero nueve guion datacamp guion python, nacida de
    main actualizado; un pull request, una carpeta; es distinta de la de la
    otra entrega aunque venzan el mismo día.
    (6) Fecha: año guion mes guion día, por ejemplo dos mil veintiséis guion
    diez guion cero cuatro; otra forma la rechaza la revisión.
    (7) IA permitida, pero debes poder explicar sin ayuda lo que la ficha pide
    (lista de debe_explicar en prosa).
    (8) Sabrás que terminaste cuando el PR esté abierto y en verde; qué
    comprueba el verde (archivos, captura, secciones llenas, fecha y URL) y qué
    no (que la captura sea tuya y del curso: eso lo reviso yo). Si no lo
    terminaste, súbelo y dilo: reportar el pendiente cuenta como entrega.
  resources:
    - title: "Unidad — Las entregas de ambientes"
      url: "https://rayalucaria.org/fdd_o26/python/ambientes/b-entregas/"
      note: "El tablero de la sección. Ésta es la entrega 1: branch tarea-09-datacamp-python, carpeta python/, con el ritual listo para copiar."
    - title: "DataCamp — Introduction to Python for Developers"
      url: "https://app.datacamp.com/learn/courses/introduction-to-python-for-developers"
      note: "El curso de esta entrega. Entra con la cuenta del grupo del ITAM."
    - title: "Unidad — El ritual"
      url: "https://rayalucaria.org/fdd_o26/git-y-github/github/el-ritual/"
      note: "Los tres bloques del flujo, con sus comandos exactos."
    - title: "Unidad — El flujo del curso"
      url: "https://rayalucaria.org/fdd_o26/git-y-github/github/el-flujo-del-curso/"
      note: "La regla del mirror y qué revisa, y qué no revisa, el check verde."
  available: "2026-10-01"
  due: "2026-10-06"
  points: 10
  status: published
  tags: [python, datacamp, certificacion, evidencia, entrega]
```

El bloque `instructions` final **es prosa escrita** (los `(1)…(8)` de arriba son el guion, no el texto). Debe contener literal `introduccion guion python guion developers` (lo exige `test_las_capturas_se_nombran_en_su_objeto_oficial`).

- [ ] **Step 5: Ficha `.github/tareas/tarea-09-datacamp-python.toml`**

```toml
# Ficha de la entrega 1 de la sección 9.1: DataCamp, Introduction to Python
# for Developers. El esquema está en .github/tareas/README.md.

[tarea]
branch = "tarea-09-datacamp-python"
asignacion = "datacamp-python-developers"
carpeta = "python"
available = "2026-10-01"
due = "2026-10-06"
penalizacion_tarde = "1/dia"
ia = "permitida-revisada"
debe_explicar = [
  "qué diferencia hay entre una lista y un diccionario, y cuándo usar cada uno",
  "qué recorre un for sobre un diccionario, y cómo recorrer llaves y valores a la vez",
  "qué hace una función con return y qué pasa si no lo lleva",
  "la cosa que escribió en «Una cosa que aprendiste»: debe poder contarla sin leerla",
]
pagina = "Página «Las entregas de ambientes» (https://rayalucaria.org/fdd_o26/python/ambientes/b-entregas/)"

[entregables]
requeridos = ["certificaciones.md"]
prohibidos = []

[[capturas]]
nombre = "introduccion-python-developers"
extensiones = [".png", ".jpg", ".jpeg", ".pdf"]
minimo_bytes = 5000

[[secciones]]
archivo = "certificaciones.md"
aguja = "Quién soy"
pide = []

[[secciones]]
archivo = "certificaciones.md"
aguja = "Introduction to Python for Developers"
pide = ["fecha-iso", "url"]

[[secciones]]
archivo = "certificaciones.md"
aguja = "Una cosa que aprendiste"
pide = []

[[patrones]]
archivo = "certificaciones.md"
seccion = "Introduction to Python for Developers"
debe = 'datacamp\.com/(completed|statement)'
que = "la URL de la sección del curso no es de un Statement of Accomplishment de DataCamp"
porque = "quien revisa verifica el curso en un clic con esa URL; otra dirección no prueba nada"
investiga = "Página «Las entregas de ambientes», entrega 1: ¿qué URL te da DataCamp al terminar, y cuál pegaste?"
nivel = "aviso"

[revision]
foco = [
  "que la captura sea la página del curso terminado, con el nombre del alumno y el 100 %",
  "que la URL abra un Statement of Accomplishment de este curso y no de otro",
  "que la fecha sea verosímil: no futura, no anterior al 2026-10-01 sin explicación",
  "que «Una cosa que aprendiste» sea concreta y del curso",
]
igual_es_normal = [
  "el texto de la plantilla de certificaciones.md: rótulos y enlace a la captura",
  "la composición de la captura: todos fotografían la misma página de DataCamp",
  "fechas iguales entre entregas: casi todos terminan el fin de semana",
]
debe_ser_propio = [
  "la captura y el nombre visible",
  "la sección «Una cosa que aprendiste»",
]
senales = [
  "captura de un ejercicio suelto o del dashboard en vez de la página del curso",
  "captura sin nombre visible, o con otro nombre",
  "captura idéntica en bytes a la de otra entrega",
  "URL de Statement of Accomplishment de otro curso",
  "«Una cosa que aprendiste» con texto que no aparece en el temario del curso",
]
donde_investigar = [
  "https://rayalucaria.org/fdd_o26/python/ambientes/b-entregas/",
  "https://app.datacamp.com/learn/courses/introduction-to-python-for-developers",
  "https://rayalucaria.org/fdd_o26/git-y-github/github/el-flujo-del-curso/",
]
```

`igual_es_normal` va sólo en prosa a propósito: una entrada que fuera la ruta `certificaciones.md` excluiría el archivo entero de `compara.py`, y «Una cosa que aprendiste» sí debe compararse entre entregas.

- [ ] **Step 6: `TAREAS`** en `.github/workflows/entregas.yml:51-55` — agrega `tarea-09-datacamp-python=python,` (con coma en la línea anterior).

- [ ] **Step 7:** `python3 -m pytest tools/test_revisa_ficha.py -q` → PASS (los parametrizados por ficha incluyen la nueva). Si `test_las_secciones_existen_en_la_plantilla_y_la_url_concuerda` falla en «Quién soy» o «aprendiste» por contener «url»: no deben contenerla.

- [ ] **Step 8: Commit**

```bash
git add codigo/python codigo/README.md course/9_python/_official/assignments/1_datacamp_python.yaml \
  .github/tareas/tarea-09-datacamp-python.toml .github/workflows/entregas.yml tools/test_revisa_ficha.py
git commit -m "feat(entregas): tarea-09-datacamp-python con su ficha"
```

### Task 12: `tarea-09-uv-docker` (las seis piezas menos el tablero)

**Files:**
- Create: `codigo/09_python/uv_docker/{reporte.py,pyproject.toml,Dockerfile,.dockerignore,bitacora.md}`, `course/9_python/_official/assignments/2_uv_en_docker.yaml`, `.github/tareas/tarea-09-uv-docker.toml`
- Modify: `.github/workflows/entregas.yml` (`TAREAS`), `codigo/09_python/README.md` (ritual de la entrega), `tools/test_revisa_ficha.py`, `tools/test_codigo_python.py`

**Interfaces:**
- Consumes: `uv=<x.y>` de `VERSIONES.txt` (Task 1) para la imagen de uv.

- [ ] **Step 1: La solución, fuera del repo, y que funcione**

En `.superpowers/uv_docker_resuelto/` escribe la versión **resuelta** de la plantilla (Step 3) con: la fila propia usando `humanize` (`humanize.naturalsize(...)` del tamaño de `sys.prefix`), los tres huecos llenos y `.venv` en `.dockerignore`. Luego:

```bash
cd .superpowers/uv_docker_resuelto
uv add humanize                      # genera uv.lock con rich + humanize
uv run reporte.py > local.txt
docker build -t reporte-prueba .
docker run --rm reporte-prueba > contenedor.txt
diff <(grep -E '^│ (rich|humanize|pygments)' local.txt) <(grep -E '^│ (rich|humanize|pygments)' contenedor.txt) && echo MISMAS_VERSIONES
grep -c "/app/.venv" contenedor.txt
# La trampa: COPY . . sin .dockerignore
sed -i 's#^COPY reporte.py ./#COPY . .#' Dockerfile && mv .dockerignore /tmp/di
docker build -t reporte-trampa . && docker run --rm reporte-trampa | head -5; mv /tmp/di .dockerignore
```

Expected: `MISMAS_VERSIONES`; `/app/.venv` ≥ 1; la imagen trampa falla o muestra un intérprete roto **si la máquina del autor no es Linux x86_64 con el mismo Python**. En Linux con el mismo Python puede **funcionar por casualidad**: la página de trampas y el `debe_explicar` dicen «se rompe cuando tu sistema o tu Python no son los de la imagen», no «siempre se rompe». Guarda las salidas para el tablero.

- [ ] **Step 2: Tests que fallan** — en `tools/test_codigo_python.py`:

```python
UVD = RAIZ / "codigo/09_python/uv_docker"


def test_la_plantilla_trae_los_tres_huecos_y_la_fila_por_llenar():
    df = (UVD / "Dockerfile").read_text(encoding="utf-8")
    assert [l for l in df.splitlines() if "HUECO" in l] and df.count("HUECO") == 3
    assert "<tu fila>" in (UVD / "reporte.py").read_text(encoding="utf-8")


def test_la_plantilla_no_trae_lock_ni_venv():
    assert not (UVD / "uv.lock").exists() and not (UVD / ".venv").exists()


def test_dockerignore_de_la_plantilla_no_trae_venv():
    """Agregarlo es parte de la tarea."""
    lineas = (UVD / ".dockerignore").read_text(encoding="utf-8").splitlines()
    assert not any(l.strip().strip("/") == ".venv" for l in lineas)


def test_reporte_es_python_valido():
    r = subprocess.run([sys.executable, "-c", "import ast,sys;ast.parse(open(sys.argv[1]).read())",
                        str(UVD / "reporte.py")], capture_output=True, text=True)
    assert r.returncode == 0
```

Y en `tools/test_revisa_ficha.py`, casos de la ficha con **textos realistas** tomados de la solución del Step 1:

```python
# --------------------------------------------------------------------------
# tarea-09-uv-docker
# --------------------------------------------------------------------------

UVD = RAIZ / "codigo/09_python/uv_docker"
B = "estudiantes/ana/09_python/uv_docker/"
DF_BIEN = (UVD / "Dockerfile").read_text(encoding="utf-8").replace(
    "# HUECO 1: copia aquí los dos archivos que describen el ambiente.",
    "COPY pyproject.toml uv.lock ./").replace(
    "# HUECO 2: crea el ambiente desde el lock, sin dejar que cambie.",
    "RUN uv sync --locked").replace(
    "# HUECO 3: copia el programa.", "COPY reporte.py ./")
DI_BIEN = (UVD / ".dockerignore").read_text(encoding="utf-8") + ".venv\n"
PY_BIEN = (UVD / "reporte.py").read_text(encoding="utf-8").replace(
    'return ("<tu fila>", "<tu valor>")',
    'return ("Tamaño del ambiente", humanize.naturalsize(tamano(sys.prefix)))')
TOML_BIEN = (UVD / "pyproject.toml").read_text(encoding="utf-8").replace(
    '"rich>=14",', '"humanize>=4.12",\n    "rich>=14",')
LOCK_BIEN = 'version = 1\n\n[[package]]\nname = "humanize"\n\n[[package]]\nname = "rich"\n'
BIT_BIEN = (UVD / "bitacora.md").read_text(encoding="utf-8")  # se llena abajo


def _bitacora(url="https://hub.docker.com/r/ana/reporte", pull=True, login=False):
    t = BIT_BIEN
    t = t.replace("- Usuario de GitHub:", "- Usuario de GitHub: ana")
    t = t.replace("- Usuario de Docker Hub:", "- Usuario de Docker Hub: ana")
    t = t.replace("Paquete:", "Paquete: humanize")
    t = t.replace("Para qué lo usa tu fila:", "Para qué lo usa tu fila: muestra el tamaño del ambiente")
    t = t.replace("<!-- salida local -->", "│ rich │ 14.1.0 │\n│ sys.prefix │ /home/ana/x/.venv │")
    t = t.replace("<!-- salida contenedor -->", "│ rich │ 14.1.0 │\n│ sys.prefix │ /app/.venv │")
    t = t.replace("<!-- que cambio -->", "Las versiones son iguales por el lock; cambia sys.prefix.")
    t = t.replace("URL pública:", f"URL pública: {url}")
    t = t.replace("Digest:", "Digest: sha256:" + "a" * 64)
    t = t.replace("Comando para correrla:", "Comando para correrla: docker run --rm ana/reporte")
    prueba = ("Unable to find image 'ana/reporte:latest' locally\nlatest: Pulling from ana/reporte\n"
              if pull else "│ rich │ 14.1.0 │\n")
    if login:
        prueba = "Login Succeeded\n" + prueba
    return t.replace("<!-- prueba de pull -->", prueba)


def _uvd(**cambios):
    archivos = {B + "Dockerfile": DF_BIEN, B + ".dockerignore": DI_BIEN,
                B + "reporte.py": PY_BIEN, B + "pyproject.toml": TOML_BIEN,
                B + "uv.lock": LOCK_BIEN, B + "bitacora.md": _bitacora()}
    archivos.update({B + k: v for k, v in cambios.items()})
    return {k: v for k, v in archivos.items() if v is not None}


def test_uvd_bien_entregada_pasa(monkeypatch, capsys):
    assert _main(monkeypatch, "tarea-09-uv-docker", _uvd()) == 0, capsys.readouterr().out


@pytest.mark.parametrize("cambio", [
    {"Dockerfile": (UVD / "Dockerfile").read_text(encoding="utf-8")},   # huecos sin llenar
    {"Dockerfile": DF_BIEN.replace("uv sync --locked", "uv sync")},     # sin --locked
    {".dockerignore": (UVD / ".dockerignore").read_text(encoding="utf-8") + "# nada\n"},  # sin .venv
    {"reporte.py": (UVD / "reporte.py").read_text(encoding="utf-8") + "\n# toque\n"},  # fila sin llenar
    {"pyproject.toml": (UVD / "pyproject.toml").read_text(encoding="utf-8") + "\n"},  # una sola dependencia
    {"uv.lock": None},                                                  # sin lock
    {"uv.lock": 'version = 1\n'},                                       # lock sin rich
    {"bitacora.md": _bitacora(url="https://hub.docker.com/repository/docker/ana/reporte")},
    {"bitacora.md": _bitacora(pull=False)},
    {"bitacora.md": _bitacora(login=True)},
], ids=["huecos", "sin-locked", "sin-venv", "fila", "una-dep", "sin-lock",
        "lock-sin-rich", "url-privada", "sin-pull", "login"])
def test_uvd_cada_falla_se_atrapa(monkeypatch, capsys, cambio):
    assert _main(monkeypatch, "tarea-09-uv-docker", _uvd(**cambio)) == 1


def test_uvd_copy_todo_solo_avisa(monkeypatch, capsys):
    df = DF_BIEN.replace("COPY reporte.py ./", "COPY . .")
    assert _main(monkeypatch, "tarea-09-uv-docker", _uvd(Dockerfile=df)) == 0
    assert "AVISO" in capsys.readouterr().out
```

La plantilla de `bitacora.md` (Step 3) lleva los marcadores `<!-- salida local -->`, `<!-- salida contenedor -->`, `<!-- que cambio -->`, `<!-- prueba de pull -->` **dentro de** sus bloques `text`, para que los tests (y el alumno) sepan dónde va cada cosa. Comprueba antes que `_lineas_utiles` ignora líneas `<!--` (sí: `revisa_ficha.py:380-384`), así que una sección con sólo el marcador cuenta como sin tocar.

- [ ] **Step 3: La plantilla `codigo/09_python/uv_docker/`**

`reporte.py`:

```python
"""Reporta el ambiente en el que corre este programa.

Córrelo en tu máquina con uv run y dentro del contenedor, y compara.
"""
import os
import platform
import sys
from importlib.metadata import distributions

from rich.console import Console
from rich.table import Table


def tamano(carpeta):
    """Bytes que ocupa una carpeta, contando todo lo que hay dentro."""
    total = 0
    for raiz, _, archivos in os.walk(carpeta):
        for a in archivos:
            ruta = os.path.join(raiz, a)
            if not os.path.islink(ruta):
                total += os.path.getsize(ruta)
    return total


def filas_del_ambiente():
    return [
        ("Python", platform.python_version()),
        ("Intérprete", sys.executable),
        ("sys.prefix", sys.prefix),
        ("¿En un ambiente?", "sí" if sys.prefix != sys.base_prefix else "no"),
        ("Sistema", f"{platform.system()} {platform.machine()}"),
    ]


def fila_propia():
    # Usa aquí el paquete que agregaste con uv add (además de rich).
    # Importa ese paquete arriba, con los demás imports.
    return ("<tu fila>", "<tu valor>")


def paquetes():
    return sorted((d.metadata["Name"], d.version) for d in distributions())


def main():
    consola = Console()
    ambiente = Table(title="Mi ambiente")
    ambiente.add_column("Qué")
    ambiente.add_column("Valor")
    for que, valor in filas_del_ambiente() + [fila_propia()]:
        ambiente.add_row(que, str(valor))
    consola.print(ambiente)

    instalados = Table(title="Paquetes instalados")
    instalados.add_column("Paquete")
    instalados.add_column("Versión")
    for nombre, version in paquetes():
        instalados.add_row(nombre, version)
    consola.print(instalados)


if __name__ == "__main__":
    main()
```

`pyproject.toml`:

```toml
[project]
name = "reporte"
version = "0.1.0"
description = "Reporta el ambiente en el que corre"
requires-python = ">=3.13"
dependencies = [
    "rich>=14",
]
```

`Dockerfile` (con `<x.y>` = uv de `VERSIONES.txt`):

```dockerfile
FROM python:3.13-slim

# uv no viene en la imagen de Python: se copia su binario de la imagen oficial.
COPY --from=ghcr.io/astral-sh/uv:<x.y> /uv /usr/local/bin/uv

WORKDIR /app

# HUECO 1: copia aquí los dos archivos que describen el ambiente.
# HUECO 2: crea el ambiente desde el lock, sin dejar que cambie.
# HUECO 3: copia el programa.

CMD ["uv", "run", "--no-sync", "reporte.py"]
```

`.dockerignore`:

```text
# Lo que nunca entra a la imagen.
__pycache__/
*.pyc
```

`bitacora.md`:

````markdown
# Bitácora — uv dentro de Docker

## Quién soy

- Usuario de GitHub:
- Usuario de Docker Hub:

## El paquete que agregaste

Paquete:

Para qué lo usa tu fila:

## Salida en tu máquina

La salida completa del reporte corrido con uv en tu máquina.

```text
<!-- salida local -->
```

## Salida en el contenedor

La salida completa del reporte corrido desde tu imagen.

```text
<!-- salida contenedor -->
```

## Qué cambió y qué no

Tres líneas, con los valores de arriba: qué salió igual en las dos, qué salió
distinto, y por qué.

<!-- que cambio -->

## Tu imagen en Docker Hub

URL pública:

Digest:

Comando para correrla:

## Prueba de que se baja del registro

La salida completa, en este orden, de cerrar sesión en el registro, borrar
tu imagen local con la bandera de forzar, y correrla otra vez.

```text
<!-- prueba de pull -->
```
````

Comprobar: las secciones sin «URL pública» no contienen la palabra «url» (`test_las_secciones_existen_en_la_plantilla_y_la_url_concuerda`).

`codigo/09_python/README.md` — agrega `## La entrega: uv_docker/` con el ritual:

```bash
cd ~/fdd/fdd_o26
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-09-uv-docker
mkdir -p estudiantes/$GHUSER/09_python/uv_docker
cp -r codigo/09_python/uv_docker/. estudiantes/$GHUSER/09_python/uv_docker/
cd estudiantes/$GHUSER/09_python/uv_docker
# ... la tarea ...
cd ~/fdd/fdd_o26
git add estudiantes/$GHUSER/09_python/uv_docker
git status        # .venv/ NO debe aparecer
```

(Copiar del ritual exacto de `course/8_contenedores/7_D_entregas.md` para `tarea-08-imagen`, que ya pasó por revisión adversarial; ajustar nombres.)

- [ ] **Step 4: YAML `2_uv_en_docker.yaml`** — `id: uv-en-docker`, `title: "Tu ambiente uv dentro de Docker"`, `available: "2026-10-01"`, `due: "2026-10-06"`, `points: 10`, `tags: [python, uv, docker, docker-hub, ambiente, entrega]`. `instructions`, prosa en el orden de la skill:
1. Qué y para qué: una app que reporta su propio ambiente, corrida en tu máquina y dentro de un contenedor, publicada en Docker Hub; el punto es ver qué fija el lock y qué no.
2. Carpeta: `uv_docker`, dentro de `09_python` (con el cero), espejo de `codigo`; **sólo** esa subcarpeta; los labs de `ambientes` se copiaron fuera del repo y no se suben.
3. Qué entregar, seis archivos: `reporte.py` con tu fila (usando tu paquete), `pyproject.toml` con `rich` y tu paquete agregados con uv, `uv.lock` generado por uv (no a mano), `Dockerfile` con los tres huecos llenos, `.dockerignore` que deja fuera tu ambiente local, `bitacora.md` llena.
4. La bitácora: la URL pública (la de `hub.docker.com/r/…`, no la de `/repository`, que da 404 a los demás; ábrela en ventana privada), digest, comando, y la prueba de pull con *Unable to find image locally* y *Pulling from*.
5. Qué no: `.venv`, `__pycache__`, la imagen como archivo, la salida de `docker login`.
6. Branch `tarea-09-uv-docker`, nacida de main actualizado; distinta de la de DataCamp aunque venzan el mismo día; un PR, una carpeta.
7. Tres cosas que se rompen: Apple Silicon → construir con `--platform linux/amd64`; si copias todo el proyecto a la imagen, tu `.venv` local viaja con él si no lo excluyes; `--locked` falla si cambiaste `pyproject.toml` y no regeneraste el lock.
8. IA `permitida-revisada` + lo que debes poder explicar (debe_explicar en prosa) + qué comprueba el verde (archivos, huecos llenos, `--locked`, `.venv` excluido, URL pública, prueba de pull) y qué no (que la imagen exista y corra: eso lo reviso yo bajándola).

Resources: tablero (nota «branch tarea-09-uv-docker, carpeta 09_python/…»), [[lab-uv]] (`https://rayalucaria.org/fdd_o26/python/ambientes/lab-uv/`), la entrega de imagen de la unidad 8 (`https://rayalucaria.org/fdd_o26/contenedores/d-entregas/`), docs de uv en Docker (`https://docs.astral.sh/uv/guides/integration/docker/`).

- [ ] **Step 5: Ficha `.github/tareas/tarea-09-uv-docker.toml`**

```toml
# Ficha de la entrega 2 de la sección 9.1: tu ambiente uv dentro de Docker.
# El esquema está en .github/tareas/README.md.

[tarea]
branch = "tarea-09-uv-docker"
asignacion = "uv-en-docker"
carpeta = "09_python"
available = "2026-10-01"
due = "2026-10-06"
penalizacion_tarde = "1/dia"
ia = "permitida-revisada"
debe_explicar = [
  "qué fija uv.lock que pyproject.toml no fija",
  "por qué el Dockerfile copia pyproject.toml y uv.lock antes que el código, y qué se reusa de la caché cuando sólo cambia reporte.py",
  "qué hace --locked y qué pasa si el lock no coincide con pyproject.toml",
  "por qué el .venv de su máquina no debe entrar a la imagen, y cuándo se rompe si entra",
  "por qué las versiones de los paquetes salen iguales dentro y fuera del contenedor, pero sys.prefix no",
  "qué hace la fila que agregó y con qué paquete",
]
pagina = "Página «Las entregas de ambientes» (https://rayalucaria.org/fdd_o26/python/ambientes/b-entregas/)"

[entregables]
requeridos = ["uv_docker/reporte.py", "uv_docker/pyproject.toml", "uv_docker/uv.lock",
              "uv_docker/Dockerfile", "uv_docker/.dockerignore", "uv_docker/bitacora.md"]
prohibidos = []

[[secciones]]
archivo = "uv_docker/bitacora.md"
aguja = "Quién soy"
pide = []

[[secciones]]
archivo = "uv_docker/bitacora.md"
aguja = "El paquete que agregaste"
pide = []

[[secciones]]
archivo = "uv_docker/bitacora.md"
aguja = "Salida en tu máquina"
pide = []

[[secciones]]
archivo = "uv_docker/bitacora.md"
aguja = "Salida en el contenedor"
pide = []

[[secciones]]
archivo = "uv_docker/bitacora.md"
aguja = "Qué cambió y qué no"
pide = []

[[secciones]]
archivo = "uv_docker/bitacora.md"
aguja = "Tu imagen en Docker Hub"
pide = ["url"]

[[secciones]]
archivo = "uv_docker/bitacora.md"
aguja = "Prueba de que se baja"
pide = []

[[patrones]]
archivo = "uv_docker/Dockerfile"
no_debe = 'HUECO'
que = "el Dockerfile todavía trae al menos un hueco marcado de la plantilla"
porque = "un hueco sin llenar es una instrucción que no existe: la imagen no tiene el ambiente o no tiene el programa"
investiga = "Página «Las entregas de ambientes», entrega 2: ¿qué tiene que pasar en cada uno de los tres huecos, y en qué orden?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/Dockerfile"
debe = 'uv\s+sync[^\n]*--locked'
que = "el Dockerfile crea el ambiente sin exigir que el lock coincida"
porque = "sin esa exigencia, la construcción puede resolver otras versiones y la imagen deja de ser lo que dice tu lock"
investiga = "Página «Lab: uv», paso del lock: ¿qué garantiza uv.lock, y qué pasa si se permite reescribirlo al construir?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/Dockerfile"
debe = 'COPY[^\n]*uv\.lock[\s\S]*RUN[^\n]*sync[\s\S]*COPY[^\n]*reporte\.py'
que = "el Dockerfile no copia el lock, crea el ambiente y copia el programa, en ese orden"
porque = "con otro orden, cada cambio al programa vuelve a instalar todos los paquetes, o el programa entra con archivos que no debía"
investiga = "Página «Capas y caché» de la unidad 8: ¿qué capas se reusan cuando sólo cambia reporte.py?"
nivel = "aviso"

[[patrones]]
archivo = "uv_docker/.dockerignore"
debe = '^\s*/?\.venv/?\s*$'
que = ".dockerignore no deja fuera el ambiente de tu máquina"
porque = "si tu ambiente local entra a la imagen, trae un intérprete y paquetes de tu sistema, que no son los de la imagen"
investiga = "Página «Las trampas»: ¿qué carpeta de tu proyecto existe sólo en tu máquina?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/reporte.py"
no_debe = '<tu fila>|<tu valor>'
que = "reporte.py todavía devuelve la fila de ejemplo de la plantilla"
porque = "la fila propia es la prueba de que tu paquete quedó instalado y se usa, dentro y fuera del contenedor"
investiga = "Página «Las entregas de ambientes», entrega 2: ¿qué muestra tu fila y de qué paquete sale?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/pyproject.toml"
debe = '^dependencies\s*=\s*\[[^\]]*"[^"]+"[^\]]*"[^"]+"'
que = "pyproject.toml declara una sola dependencia"
porque = "la tarea pide rich y un paquete elegido por ti; sin el segundo no hay fila propia que lo use"
investiga = "Página «Lab: uv», paso de agregar un paquete: ¿qué cambia en pyproject.toml cuando agregas una dependencia?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/uv.lock"
debe = '^name = "rich"$'
que = "uv.lock no trae rich"
porque = "un lock sin las dependencias del proyecto no lo generó la herramienta a partir de tu pyproject.toml"
investiga = "Página «Los archivos»: ¿quién escribe el lock, y a partir de qué?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/bitacora.md"
seccion = "Tu imagen en Docker Hub"
debe = 'hub\.docker\.com/r/[^/\s]+/[^/\s]+'
que = "la URL de tu imagen no es la pública del registro"
porque = "la dirección de tu panel sólo la ve tu sesión; a quien revisa le da error 404"
investiga = "Página «Las entregas de ambientes», entrega 2: ¿qué ve alguien sin tu sesión cuando abre tu URL?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/bitacora.md"
seccion = "Prueba de que se baja"
debe = 'Unable to find image[\s\S]*Pulling from'
que = "la prueba no muestra que la imagen se bajó del registro"
porque = "sin esas dos líneas, la imagen pudo haber corrido desde tu disco y no hay prueba de que esté publicada"
investiga = "Página «Las cinco entregas» de la unidad 8, entrega 3: ¿qué tiene que pasar con tu copia local antes de correrla?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/bitacora.md"
no_debe = 'Login Succeeded'
que = "la bitácora trae la salida de iniciar sesión en el registro"
porque = "esa salida puede revelar dónde guardas tu credencial, y la tarea no la pide"
investiga = "Página «Las entregas de ambientes», entrega 2: ¿qué salidas pide la prueba, y cuáles no?"
nivel = "falla"

[[patrones]]
archivo = "uv_docker/bitacora.md"
seccion = "Salida en el contenedor"
debe = '/app/\.venv'
que = "la salida del contenedor no muestra el ambiente dentro de la imagen"
porque = "con el Dockerfile de la tarea, el reporte dentro del contenedor corre desde el ambiente que uv creó en la imagen"
investiga = "Página «Un ambiente por dentro»: ¿qué es sys.prefix, y dónde creó uv el ambiente en tu imagen?"
nivel = "aviso"

[revision]
foco = [
  "bajar la imagen de la URL pública y correrla: que la tabla salga y la fila propia funcione",
  "que las versiones de paquetes de la salida local y la del contenedor coincidan, y coincidan con uv.lock",
  "que «Qué cambió y qué no» explique con los valores reales: versiones iguales por el lock, sys.prefix e intérprete distintos",
  "que la imagen esté construida para linux/amd64",
]
igual_es_normal = [
  "el resto de reporte.py fuera de fila_propia y su import: viene de la plantilla",
  "uv_docker/Dockerfile",
  "uv_docker/.dockerignore",
  "el texto de la plantilla de bitacora.md",
  "las versiones de rich y sus transitivas: todos resuelven el mismo día",
]
debe_ser_propio = [
  "el paquete elegido y la fila que lo usa",
  "las salidas: rutas de su máquina, su usuario, su digest",
  "«Qué cambió y qué no»",
]
senales = [
  "versiones en la salida pegada que no son las de uv.lock",
  "salida del contenedor con un sys.prefix que no es /app/.venv",
  "digest que no coincide con el de la imagen publicada",
  "salida local con rutas de otra persona, o idéntica a la de otra entrega",
  "uv.lock con formato que la herramienta no produce (sin version, paquetes sin source)",
  "el paquete elegido no aparece en uv.lock",
  "imagen publicada sólo para arm64",
]
donde_investigar = [
  "https://rayalucaria.org/fdd_o26/python/ambientes/b-entregas/",
  "https://rayalucaria.org/fdd_o26/python/ambientes/lab-uv/",
  "https://rayalucaria.org/fdd_o26/contenedores/d-entregas/",
  "https://docs.astral.sh/uv/guides/integration/docker/",
]
```

**Revisa contra `PALABRAS_DE_RECETA`**: ningún `que/porque/investiga` contiene `docker `, `uv `, `pip `, `git `, `cp `, `mkdir`, `sudo`, `chmod`, backtick, «cambia la linea», «escribe ». (`uv.lock` y `uv_docker` no contienen `uv ` con espacio; «Lab: uv», sí: **`"lab: uv»"` no tiene espacio tras `uv`** — comprobar con el test, y si choca, decir «Página «Lab» de ambientes».)

- [ ] **Step 6: `TAREAS`** — agrega `tarea-09-uv-docker=09_python`.

- [ ] **Step 7:** `python3 -m pytest tools/test_revisa_ficha.py tools/test_codigo_python.py -q` → PASS. Si un caso de `test_uvd_cada_falla_se_atrapa` pasa en verde, el patrón está mal: arreglar el patrón, no el test.

- [ ] **Step 8: Commit**

```bash
git add codigo/09_python/uv_docker codigo/09_python/README.md \
  course/9_python/_official/assignments/2_uv_en_docker.yaml \
  .github/tareas/tarea-09-uv-docker.toml .github/workflows/entregas.yml \
  tools/test_revisa_ficha.py tools/test_codigo_python.py
git commit -m "feat(entregas): tarea-09-uv-docker con su ficha y plantilla"
```

### Task 13: El tablero `12_B_entregas.md`

**Files:**
- Create: `course/9_python/1_ambientes/12_B_entregas.md`
- Modify: `1_ambientes/0_index.md` (fila B), `6_ambiente_conda_docker.md` y `10_las_trampas.md` (enlaces a `[[entregas-ambientes]]`)
- Test: `tools/test_python_curriculum.py`

- [ ] **Step 1: Tests** en `tools/test_python_curriculum.py`:

```python
TABLERO = SECCION / "12_B_entregas.md"


def test_el_tablero_nombra_branch_carpeta_y_fecha_de_cada_entrega():
    t = TABLERO.read_text(encoding="utf-8")
    for b, c in (("tarea-09-datacamp-python", "python/"),
                 ("tarea-09-uv-docker", "09_python/")):
        assert f"`{b}`" in t and f"`{c}`" in t
    assert t.count("2026-10-06") >= 2


def test_el_tablero_de_uv_docker_menciona_platform():
    assert "--platform linux/amd64" in TABLERO.read_text(encoding="utf-8")


def test_el_tablero_dice_que_no_se_entrega_y_acabaste_cuando():
    t = TABLERO.read_text(encoding="utf-8")
    assert t.count("**Acabaste cuando**") == 2 and ".venv" in t
```

- [ ] **Step 2:** FAIL.
- [ ] **Step 3: El tablero** — `id: entregas-ambientes`, `title: "Las entregas de ambientes"`, `nav_title: "B. Entregas"`, `estimated_time: 8m`, `prerequisites: [el-flujo-del-curso]`. Forma de `course/8_contenedores/7_D_entregas.md`:
  - Una línea: «**el contrato manda**: esto es su versión en tabla».
  - `::: table {#py-entregas-resumen title="Las dos entregas de ambientes"}` — `| # | Entrega | Vence | Vale | Branch | Carpeta |`: `1 | DataCamp: Introduction to Python for Developers | 2026-10-06 | 10 | \`tarea-09-datacamp-python\` | \`python/\``; `2 | Tu ambiente uv dentro de Docker | 2026-10-06 | 10 | \`tarea-09-uv-docker\` | \`09_python/\``.
  - **Dos carpetas, dos branches, dos PRs**, ninguna nacida de la otra. Nombra el error antes de que ocurra: «es `python/`, no `09_python/`» y al revés.
  - `## 1 · DataCamp` — tabla Vence/Vale/Branch/Carpeta; «Entregas dos archivos» (lista); el ritual (bloque bash, mismo de `tarea-08-datacamp-intro` con nombres cambiados: `mkdir -p estudiantes/$GHUSER/python`, `cp -r codigo/python/. estudiantes/$GHUSER/python/`, `git add estudiantes/$GHUSER/python`, commit, push, PR); qué no se entrega; **Acabaste cuando**.
  - `## 2 · Tu ambiente uv dentro de Docker` — tabla; figura `py-uv-docker` (`::: figure {#py-uv-docker …}`); «Entregas seis archivos» (lista, cada uno con lo que debe tener); los pasos en orden, cada uno una línea con su comando: copiar (ritual de `codigo/09_python/README.md`), `uv add <tu paquete>`, escribir tu fila, `uv run reporte.py`, llenar huecos y `.dockerignore`, `docker build --platform linux/amd64 -t <usuario>/reporte .`, `docker run --rm <usuario>/reporte`, `docker push`, la prueba (`docker logout`, `docker rmi -f`, `docker run`); **qué no** (`.venv/`, `__pycache__/`, la salida de `docker login`); «Tres cosas que se rompen» (platform, `.venv` por `COPY . .`, `--locked` con lock viejo) con la salida real de la Task 12 Step 1; **Acabaste cuando**.
  - `## Qué revisa la revisión automática` — tabla `| Revisa | No revisa |` con lo de la ficha (archivos, captura, secciones llenas, fecha ISO, URL, huecos, `--locked`, `.venv` en `.dockerignore`, fila propia, dos dependencias, `rich` en el lock, URL pública, prueba de pull, sin `Login Succeeded`) contra lo que revisa el profesor (que la imagen exista y corra, que la captura sea del alumno, que las salidas sean reales). Una línea: «Los mensajes dicen qué está mal, por qué y dónde investigar; no dicen cómo arreglarlo».
- [ ] **Step 4:** fila B en el índice; enlaces en 6 y 10.
- [ ] **Step 5:** `python3 -m pytest tools/ -q` → **todo verde**, incluido `test_cada_svg_esta_referenciado_por_alguna_pagina`.
- [ ] **Step 6: Commit**

```bash
git add course/9_python tools/test_python_curriculum.py
git commit -m "feat(unidad-9): tablero de las entregas de ambientes"
```

### Task 14: Revisión adversarial (skill `crear_tarea` § 7)

**Files:** los que el parche toque.

- [ ] **Step 1: Checklist mecánico de la skill**

```bash
for b in tarea-09-datacamp-python tarea-09-uv-docker; do echo "== $b"; grep -rn "$b" .github/ course/ codigo/ | sort; done
ls -a codigo/python codigo/09_python/uv_docker
grep -n "HUECO\|<tu fila>" codigo/09_python/uv_docker/*
python3 -m pytest tools/ -q
cd ~/itam/raya_lucaria && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

Expected: cada branch aparece en ficha, workflow, YAML y tablero; los huecos y la fila existen en la plantilla; todo verde.

- [ ] **Step 2: Tres agentes en paralelo, sólo lectura** (`Agent`, `subagent_type: general-purpose`), cada uno con las rutas de las seis piezas de **las dos** tareas, las páginas 3, 7, 10, B y la Cheatsheet:

| Agente | Prompt (resumen) |
|---|---|
| Alumno literal | «Haz exactamente lo que dice cada palabra, en orden, en Linux, macOS Apple Silicon y Windows. Reporta: dónde una pieza choca con otra, qué sube el ritual que no debía, qué pide tocar que no existe, qué comando no corre en Windows.» |
| Alumno flojo | «Busca el mínimo que pasa en verde en cada tarea. Reporta cada entrega vacía, a medias o inventada que pasa el CI, y si `[revision]` la atrapa.» |
| IA sin leer | «Pega cada tarea en un modelo y entrega lo que salga sin correr nada. Reporta incoherencias que dejaría (versiones inventadas, `uv.lock` escrito a mano, salidas imposibles) y si están en `senales`. Verifica además contra la documentación actual cada comando de poetry y conda de la Cheatsheet y la lista de capítulos del curso de DataCamp (para `debe_explicar`).» |

Cada hallazgo con **pieza, línea y consecuencia**.

- [ ] **Step 3: Un parche consolidado** — agrupar hallazgos, descartar los que no se sostienen (decirlo), aplicar el resto, agregar un test por cada falso verde encontrado. Correr `python3 -m pytest tools/ -q` y `raya validate`.

- [ ] **Step 4:** Si el parche cambió algo grande (una regla de la ficha, un archivo requerido), repetir Step 2 sólo con el agente que lo encontró.

- [ ] **Step 5: Commit**

```bash
git add <rutas tocadas>
git commit -m "fix(entregas): hallazgos de la revisión adversarial de las entregas 9.1"
```

---

## FASE 4 · Cierre

### Task 15: Documentación del repo

**Files:**
- Modify: `CLAUDE.md` (§ The calendar, § Images, § CI), `AGENTS.md` (lo equivalente), `course/1_introduccion/1_el_curso/0_index.md` (sólo si la fila 13 deja de ser cierta)

- [ ] **Step 1: `CLAUDE.md`**
  - «The calendar»: dos excepciones de 60 min (`session-10` 2026-09-17 y `session-13` 2026-10-01, la clase de ambientes de Python); sesiones listadas `session-01`…`session-13`, terminando el 2026-10-01; agregar `ambientes-python` a la lista de `page`s.
  - «Images»: `gen_python.py` en la lista de generadores.
  - «Per-task CI»: el tablero de 9.1 es `course/9_python/1_ambientes/12_B_entregas.md` y también describe lo que revisa la ficha.
- [ ] **Step 2: `AGENTS.md`** — mismos tres puntos, en su versión corta.
- [ ] **Step 3: `course/1_introduccion/1_el_curso/0_index.md`** — leer la fila 13 «Gestión de dependencias»; si la unidad 9 la adelanta, no se toca (el temario general es intención, no calendario). Por defecto: **no tocar**.
- [ ] **Step 4:** **No commitear `CLAUDE.md`**: ya tenía cambios del profesor sin commit. Commitear sólo `AGENTS.md` (y el temario si cambió) y avisarle que `CLAUDE.md` queda modificado para que lo revise con sus propios cambios.

```bash
git add AGENTS.md
git commit -m "docs: la unidad 9 en las guías para agentes"
```

### Task 16: Verificación final

- [ ] **Step 1:** `python3 -m pytest tools/ -q` → todo verde. Si `test_diagramas.py`/`test_ai_dashboard_*` salen *skipped*, decirlo: no se ejercitaron.
- [ ] **Step 2:** `cd ~/itam/raya_lucaria && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26 && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya artifacts inspect ~/itam/fdd_o26/artifact` → sin errores.
- [ ] **Step 3:** `raya preview` y revisar a ojo en `http://127.0.0.1:8000/index.html`: la unidad Python en la navegación; 9.1 con sus 12 páginas; las 8 figuras; las tablas grandes (5, Cheatsheet) en ancho de teléfono; el calendario con la sesión del 1 de octubre de 19:00 a 20:00 y las dos entregas el 6 de octubre.
- [ ] **Step 4:** `git status` — sólo quedan `CLAUDE.md` (a propósito) y lo que ya estaba antes (`estudiantes/uumami/vscode/example.ipynb`). `git log --oneline -8` muestra los commits del plan.
- [ ] **Step 5:** Reportar al profesor: qué se publicó, qué quedó sin commit y por qué, y que el push lo decide él.
