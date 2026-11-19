---
id: elegir-el-stack
title: "Elegir el stack"
nav_title: "3. Elegir el stack"
summary: "Escribir código ya es barato; lo caro es decidir con qué. La IA elige lo que más vio, que suele ser lo viejo. Hoy se compara midiendo: contratos, motores de tablas y formatos, con números de tu máquina."
status: ready
tags: [python, polars, duckdb, pydantic, parquet, stack, ia, notebook]
prerequisites: [python-por-dentro]
---

# Elegir el stack

**Sección 3** · 4 páginas y 2 anexos · unos 90 min · sesión del jueves 8 de octubre, 19:00–20:30

Meta: elegir librerías y formatos para datos midiendo en tu máquina, y saber qué pedirle a la IA para que no elija lo viejo.

## En corto

- **Escribir código es barato; decidir el stack es caro.** El stack es el conjunto de librerías, formatos y herramientas de un proyecto.
- **La IA elige lo que más vio, que suele ser lo viejo**: Polars 2.0 salió el 2026-10-06, hace dos días, y ninguna IA lo conoce.
- **Hoy se compara midiendo**: las mismas opciones, la misma tarea, números de tu máquina.

## Paso 0 · ¿dónde estás?

Abre tu fork en VS Code y, en su terminal:

```bash
git status
echo "$GHUSER"
```

**Qué hace cada pieza:**

- `git status` — dice en qué branch estás y si tienes cambios sin commit.
- `echo "$GHUSER"` — imprime tu usuario de GitHub, guardado en tu shell desde la unidad de Git.

| Si `git status` dice… | Haces… |
|---|---|
| `On branch main`, sin cambios o sólo con `Untracked files` | Haz 1 |
| `On branch main` **con cambios** (`Changes not staged` o `Changes to be committed`) | Detente y pide ayuda: el Haz 1 no debe mezclarlos con lo del curso |
| `On branch tarea-09-por-dentro` **con cambios** | Commit y push con el ritual de entrega de [[entregas-por-dentro]], con *Clear All Outputs* antes; luego Haz 1 |
| Otra branch **con cambios** | Commit de **esa** entrega; si no sabes cuál es, pide ayuda. Luego Haz 1 |
| `On branch tarea-09-por-dentro` sin cambios, u otra branch sin cambios | Haz 1 |
| `On branch tarea-09-stack` | **Ya hiciste el ritual:** `cd {tu_fork_de_la_clase}` y salta al Haz 3 |

Si `echo "$GHUSER"` imprime una línea vacía, guárdalo como en [[el-ritual-del-curso]] y abre una terminal nueva.

Si al volver a `main` ves `por_dentro/` sólo con `.venv/` adentro, es normal: un ambiente no va a git y no se va al cambiar de branch.

## El ritual

`uv sync` descarga mientras explicamos lo demás: por eso va primero. En los comandos, `{tu_fork_de_la_clase}` es la carpeta de tu fork, **sin las llaves**.

**Haz 1 · trae lo nuevo:**

```bash
cd {tu_fork_de_la_clase}
git switch main && git fetch upstream && git merge --ff-only upstream/main
```

**Qué hace cada pieza:**

- `git switch main` — te pones en tu `main`.
- `git fetch upstream` — descarga lo nuevo del repo del curso, sin tocar tus archivos.
- `git merge --ff-only upstream/main` — avanza tu `main` hasta el del curso, sólo si no tiene commits propios.

**Deberías ver** `Fast-forward` y, en la lista, archivos de `codigo/09_python/stack/`.

Si dice `Not possible to fast-forward`, **detente y pide ayuda**.

**Haz 2a · la branch de la entrega:**

```bash
[ -n "$GHUSER" ] && git switch -c tarea-09-stack
```

**Qué hace cada pieza:**

- `[ -n "$GHUSER" ]` — comprueba que tu usuario no está vacío (`-n`: no vacío); si lo está, se detiene aquí.
- `git switch -c tarea-09-stack` — crea la branch de esta sección y te cambia a ella. En ella haces la clase y la tarea ([[entregas-stack]]).

**Deberías ver:**

```text
Switched to a new branch 'tarea-09-stack'
```

**Haz 2b · copia y commit de la plantilla:**

```bash
[ -n "$GHUSER" ] && mkdir -p estudiantes/$GHUSER/09_python \
  && cp -r codigo/09_python/stack estudiantes/$GHUSER/09_python/ \
  && git add estudiantes/$GHUSER/09_python/stack \
  && git commit -m "unidad 09: plantilla de stack"
```

**Qué hace cada pieza:**

- `\` al final de una línea — el comando sigue en la siguiente: las cuatro líneas son un solo comando.
- `cp -r codigo/09_python/stack estudiantes/$GHUSER/09_python/` — copia **la carpeta** `stack` dentro de tu `09_python/`, sin `/.` al final.
- `git add estudiantes/$GHUSER/09_python/stack` — prepara sólo `stack`, nunca `09_python` entero: ahí viven tus otras entregas.
- `git commit -m "…"` — guarda la plantilla antes de tocarla; tu pull request mostrará sólo lo que cambies.

**Deberías ver:**

```text
[tarea-09-stack 5929a93] unidad 09: plantilla de stack
 18 files changed, 4152 insertions(+)
 create mode 100644 estudiantes/ana/09_python/stack/.gitignore
 create mode 100644 estudiantes/ana/09_python/stack/.python-version
 …
```

- En lugar de `ana`, tu usuario; el `5929a93` es otro en tu máquina, y la cifra de `insertions` puede variar si la plantilla cambió.

> [!WARNING]
> **El Haz 3 descarga unos 195 MB** y deja un ambiente de unos 650 MB en disco. Si no tienes Python 3.14, uv lo descarga también (~30 MB más). Mientras descarga, sigue la explicación. Si tu red no da, trabaja en pareja y termina en casa.

**Haz 3 · crea el ambiente, actívalo e instala** (desde la raíz de tu fork, donde te dejó el Haz 2b):

```bash
uv venv .venv-stack --python 3.14
source .venv-stack/bin/activate
cd estudiantes/$GHUSER/09_python/stack && uv sync --active
```

**Qué hace cada pieza:**

- `uv venv .venv-stack --python 3.14` — crea un ambiente vacío **en la raíz de tu fork**, con el nombre `.venv-stack`. En la raíz porque ahí lo busca VS Code; en `stack/` no lo ve.
- `source .venv-stack/bin/activate` — lo activa en esta terminal: tu prompt empieza con `(.venv-stack)`. En Windows sin WSL: `.venv-stack\Scripts\activate`.
- `uv sync --active` — lee `pyproject.toml` y `uv.lock` de `stack/` e instala exactamente esas versiones **en el ambiente activo** ([[ambientes-python]]). Sin `--active`, uv crearía otro `.venv` dentro de `stack/`.

**Deberías ver:** (recortado)

```text
Using CPython 3.14.0
Creating virtual environment at: .venv-stack
Activate with: source .venv-stack/bin/activate
Resolved 54 packages in 1ms
Downloading polars-runtime-32 (52.0MiB)
…
Installed 48 packages in 212ms
 …
 + polars==2.0.0
 …
 + pydantic==2.14.0
 …
```

- Cifras de una corrida real: 54 paquetes resueltos, 48 instalados. Las versiones deben ser éstas: `polars==2.0.0`, no una 1.x. Los milisegundos cambian.
- uv deja un `.gitignore` dentro de `.venv-stack`: `git status` no lo muestra y nunca se sube.
- **Toda terminal nueva empieza sin ambiente.** Antes de un comando de la sección: `source .venv-stack/bin/activate` desde la raíz de tu fork. Los comandos de la sección van **sin** `uv run` (`pytest`, `mypy`, `ruff`): ya son los del ambiente activo.

**Haz 4 · elige el ambiente en el notebook:**

1. Usa la ventana de VS Code que tiene abierto **tu fork entero**, no sólo `stack/`.
2. En su terminal, `pwd`: después del Haz 3 ya estás en `stack/`.
3. Abre `estudiantes/<tu-login>/09_python/stack/a_contratos.ipynb` → *Select Kernel* → *Python Environments* → **`.venv-stack (3.14.0)`**. Si no aparece: `Ctrl+Shift+P` → *Developer: Reload Window*, y repite.
4. Corre la celda **A.0** (Shift+Enter).

**Deberías ver:**

- `pwd` termina en `09_python/stack`, y el prompt empieza con `(.venv-stack)`.
- Arriba a la derecha del notebook dice `.venv-stack`.
- A.0 imprime las versiones (`polars 2.0.0`, `duckdb 1.5.6`, `pandas 3.0.6`, `pydantic 2.14.0`…), una ruta que termina en `.venv-stack/bin/python3`, tu RAM y el `N` que te recomienda («Tienes … GB de RAM → te recomendamos N = …»).

A.0 **no cambia** `N`: lo cambias tú, dejando una sola línea sin `#`.

## Si algo sale mal

| Síntoma | Causa | Qué haces |
|---|---|---|
| `ModuleNotFoundError: No module named 'polars'` | El kernel es otro ambiente (p. ej. `.venv (3.12)` de la raíz) | Elige **`.venv-stack (3.14.0)`**; *Restart*; A.0 imprime qué Python corre |
| No aparece `.venv-stack` en la lista | VS Code no ha vuelto a buscar, o está abierto sólo en `stack/` | *Developer: Reload Window*; abre tu fork entero (Haz 4) |
| `command not found: pytest` (o `mypy`, `ruff`) | Terminal nueva, sin el ambiente activo | `source .venv-stack/bin/activate` desde la raíz de tu fork |
| Apareció un `.venv/` dentro de `stack/` | Corriste `uv sync` o `uv run` sin el ambiente activo o sin `--active` | Bórralo (`rm -rf .venv`); activa `.venv-stack` y usa los comandos sin `uv run` |
| `warning: VIRTUAL_ENV=… does not match the project environment` | Corriste `uv sync` o `uv run` sin `--active` | Usa `uv sync --active`, y los comandos sin `uv run` |
| `uv sync` lento | La red | Trabaja en pareja; termina en casa |
| `uv sync` compila algo por minutos | No hay rueda (paquete ya compilado) para tu plataforma | Pide ayuda |
| Polars avisa de una CPU sin AVX2 al importar | CPU vieja | Pide ayuda |
| No aparece `codigo/09_python/stack/` | El Haz 1 no corrió | Haz 1 |
| `Not possible to fast-forward` | Tu `main` tiene commits propios | Detente y pide ayuda |
| `fatal: a branch named 'tarea-09-stack' already exists` | Ya empezaste | `git switch tarea-09-stack`, `cd {tu_fork_de_la_clase}` y salta al Haz 3 |
| `nothing to commit` en el Haz 2b | La plantilla ya estaba en tu branch | Sigue con el Haz 3 |
| `No interpreter found for Python 3.14` | Tu uv no descarga Pythons solo | `uv python install 3.14` y repite el Haz 3 |

## Las marcas: dónde estás

Cada página y cada notebook dicen, en su propia línea, a dónde ir.

| Marca | Dónde | Qué haces | Cómo sé que estoy bien |
|---|---|---|---|
| `**📄 PÁGINA · <título>**` | El sitio | Lees el concepto y la tabla | Estás en la página que dice la marca |
| `**📓 NOTEBOOK · <archivo> · celdas X.n–X.m**` | VS Code, el notebook | Corres en orden y comparas con «Deberías ver» | Arriba a la derecha dice `.venv-stack` |
| `**💻 TERMINAL · en stack/ (comprueba con pwd)**` | La terminal de VS Code, parada en `stack/` | Un comando sobre un `.py` | `pwd` termina en `09_python/stack` y el prompt empieza con `(.venv-stack)` |

**¿Te perdiste?** Corre la celda X.0 del notebook (A.0, B.0 o C.0) y salta a la celda que vamos: X.0 deja todo listo.

Al terminar un notebook: *Restart* o *Shutdown* de su kernel antes de abrir el siguiente, para liberar la memoria.

## Cómo medir

| Eje | Regla |
|---|---|
| Tiempo | Repite y quédate con el mejor; compara **cuántas veces más lento**, no segundos |
| Memoria | Hay dos: la que ve Python (`tracemalloc`) y la del proceso entero (**RSS**: la memoria que el sistema le dio al proceso; `htop` la muestra en RES) |

Cada trampa de medir se explica en la celda donde aparece. Tus números serán otros; **lo que se mantiene es el patrón**.

## El mapa del stack

::: figure {#py-stack-mapa title="Las cuatro capas del stack de datos"}
![Cuatro capas de izquierda a derecha. Proyecto: uv, ruff y pytest, cómo se instala y se revisa. Contratos: tipos y Pydantic, quién revisa cada dato. Motor: Polars y DuckDB, dónde se hace el trabajo. Formato: Parquet, cómo se guarda. Debajo de cada capa, lo viejo que suele escribir la IA: pip y requirements.txt; sin tipos y Pydantic v1; pandas para todo; CSV y pickle. Al pie: cada capa se elige midiendo, no por costumbre.](../_assets/py-stack-mapa.svg)
:::

| Capa | Contesta | Lo ves en |
|---|---|---|
| Proyecto | Con qué se instala, se revisa y se prueba | [[ambientes-python]] y [[contratos]] (ruff, mypy, pytest) |
| Contratos | Quién revisa un dato y cuándo | [[contratos]] |
| Motor | Dónde se hace el trabajo | [[motores-de-tablas]] |
| Formato | Cómo se guarda y cuánto ocupa | [[archivos-y-memoria]] |

## Las páginas

| # | Página | Qué deja | Notebook |
|---:|---|---|---|
| 1 | [[contratos]] | Quién revisa un dato y cuándo; cuánto cuesta una garantía | `a_contratos.ipynb` |
| 2 | [[motores-de-tablas]] | Dónde se hace el trabajo; lazy; el tipo decide la memoria | `b_tablas.ipynb` |
| 3 | [[archivos-y-memoria]] | Cómo se guarda y cuánto ocupa | `c_archivos.ipynb` |
| 4 | [[patrones-del-stack]] | Los 8 patrones, cómo elegir una librería, `AGENTS.md` | — |

| Anexo | Qué es | Cuándo lo abres |
|---|---|---|
| [[entregas-stack]] | La tarea: DataCamp, la práctica y `AGENTS.md` | Antes de entregar |
| [[chuleta-del-stack]] | Todas las tecnologías en tablas: ★ con código en clase, ○ sólo para saber que existen | Cuando leas código ajeno o la IA te proponga algo |

Sigue con [[contratos]]: lo primero que entra a un proyecto es un dato, y alguien tiene que revisarlo.

> [!NOTE]
> **Si sólo recuerdas una cosa:** la IA elige lo que más vio; tú eliges midiendo, en tu máquina.
