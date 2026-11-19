---
id: cheatsheet-ambientes
title: "Cheatsheet de ambientes"
nav_title: "A. Cheatsheet"
summary: "La misma tarea en uv, venv + pip, poetry y conda, en una sola tabla. uv es la columna que se usa en este curso; las otras son para leer repos ajenos."
status: ready
estimated_time: 5m
tags: [cheatsheet, uv, pip, venv, poetry, conda]
prerequisites: [trampas-de-ambientes]
---

# Cheatsheet de ambientes

**Anexo A** · para tener abierto

La columna **uv** es la del curso. Las otras tres sirven para traducir el README de un repo ajeno. Todos los comandos se probaron con uv 0.12.21, poetry 2.5.1 y conda 26.7.2.

::: table {#py-cheatsheet title="La misma tarea en cada herramienta"}

| Tarea | uv | venv + pip | poetry | conda |
|---|---|---|---|---|
| Instalar Python | `uv python install 3.13` | el instalador de tu sistema | `poetry python install 3.13` (experimental desde 2.1) | `conda create -n x python=3.13` |
| Nuevo proyecto | `uv init --no-package x` | `mkdir x && cd x` | `poetry new x` | — |
| Crear el ambiente | automático; o `uv venv` | `python3 -m venv .venv` | automático | `conda create -n x` |
| Activar | no hace falta: `uv run` | `source .venv/bin/activate` | `eval $(poetry env activate)` | `conda activate x` |
| Agregar un paquete | `uv add rich` | `pip install rich` | `poetry add rich` | `conda install rich` |
| Quitarlo | `uv remove rich` | `pip uninstall rich` | `poetry remove rich` | `conda remove rich` |
| Dependencia de desarrollo | `uv add --dev pytest` | un segundo `requirements-dev.txt` | `poetry add --group dev pytest` | — |
| Instalar desde el lock | `uv sync` | `pip install -r requirements.txt` | `poetry install` | `conda env create -f environment.yml` |
| Correr | `uv run x.py` | `python x.py`, activado | `poetry run python x.py` | `python x.py`, activado |
| Ver qué hay | `uv tree` | `pip list` | `poetry show --tree` | `conda list` |
| Exportar a requirements | `uv export --no-dev > requirements.txt` | `pip freeze > requirements.txt` | requiere el plugin `poetry-plugin-export` | `conda env export > environment.yml` |
| Una herramienta suelta | `uvx ruff` | `pipx run ruff` | — | — |
| Borrar el ambiente | `rm -rf .venv` | `deactivate && rm -rf .venv` | `poetry env remove --all` | `conda env remove -n x` |

:::

## Qué hace cada fila (columna uv)

- **Instalar Python** — `uv python install 3.13` descarga un Python 3.13 que uv guarda aparte; no toca el Python del sistema.
- **Nuevo proyecto** — `uv init x` crea la carpeta `x/` con `pyproject.toml` y un `main.py`.
- **Crear el ambiente** — `uv run`, `uv add` y `uv sync` crean `.venv/` solos si falta; `uv venv` lo crea vacío a mano.
- **Activar** — con uv no se activa: `uv run` ya usa el `.venv/`. Activar sólo hace falta con venv, poetry y conda.
- **Agregar un paquete** — `uv add rich` lo anota en `pyproject.toml`, fija su versión en `uv.lock` y lo instala en `.venv/`.
- **Quitarlo** — `uv remove rich` lo borra de los tres lugares.
- **Dependencia de desarrollo** — un paquete que usas al trabajar (pruebas, notebooks) pero tu programa no importa.
- **Instalar desde el lock** — `uv sync` deja `.venv/` con exactamente lo que dice `uv.lock`: instala lo que falta y quita lo que sobra.
- **Correr** — `uv run x.py` corre `x.py` con el Python del `.venv/`, después de comprobar que esté al día con el lock.
- **Ver qué hay** — `uv tree` dibuja tus paquetes y, debajo de cada uno, los paquetes que él necesita.
- **Exportar a requirements** — `uv export` imprime el lock en formato `requirements.txt`, para quien usa pip.
- **Una herramienta suelta** — `uvx ruff` corre `ruff` en un ambiente temporal, sin agregarlo a tu proyecto.
- **Borrar el ambiente** — `rm -rf .venv` borra la carpeta; `pyproject.toml` y `uv.lock` siguen, así que `uv sync` lo recrea igual.

## Las banderas y símbolos de la tabla

- `--no-package` — el proyecto sólo corre scripts; no es una librería para publicar en PyPI.
- `--dev` — agrega el paquete al grupo de desarrollo (`[dependency-groups]` en `pyproject.toml`), no a las dependencias del programa.
- `--no-dev` — deja fuera ese grupo de desarrollo; sirve para Docker y para exportar.
- `> requirements.txt` — manda lo que el comando imprime a ese archivo, en vez de a la pantalla; si existía, lo reescribe.
- `uvx` — abreviatura de `uv tool run`.
- `rm -rf` — `-r` borra la carpeta con todo su contenido; `-f` no pregunta ni se queja si no existe.
- `mkdir x && cd x` — crea la carpeta; `&&` corre el `cd` sólo si `mkdir` salió bien.
- `source .venv/bin/activate` — corre el script `activate` en tu shell actual: pone `.venv/bin` primero en tu PATH.
- `deactivate` — deshace la activación.
- `-r requirements.txt` (pip) — instala todo lo que lista ese archivo, en vez de un paquete por nombre.
- `pip freeze` — imprime cada paquete instalado con su versión exacta.
- `eval $(poetry env activate)` — `poetry env activate` imprime el comando de activación; `$(…)` captura ese texto y `eval` lo ejecuta.
- `--group dev` (poetry) — lo mismo que `--dev` de uv.
- `-n x` (conda) — el nombre del ambiente; conda los guarda en su propia carpeta, no en el proyecto.
- `python=3.13` (conda) — instala esa versión de Python dentro del ambiente.
- `-f environment.yml` (conda) — lee del archivo la lista de paquetes.
- `pipx run` — lo mismo que `uvx`, con pipx.

## Los cinco que más vas a usar

```bash
uv add rich
uv run hola.py
uv sync
uv tree
rm -rf .venv
```

**Qué hace cada pieza:**

- `uv add rich` — agrega `rich` al proyecto: `pyproject.toml`, `uv.lock` y `.venv/`.
- `uv run hola.py` — corre `hola.py` con el Python del `.venv/`, sin activar nada.
- `uv sync` — recrea o pone al día `.venv/` según `uv.lock`; es lo primero tras clonar o tras un `git pull`.
- `uv tree` — muestra qué paquetes hay y quién necesita a quién.
- `rm -rf .venv` — borra el ambiente; el siguiente `uv sync` o `uv run` lo recrea.

## Diagnóstico

```bash
which python3
python3 -m pip --version
uv run quien_soy.py
```

**Qué hace cada pieza:**

- `which python3` — la ruta del `python3` que tu shell encuentra primero.
- `python3 -m pip --version` — `-m pip` corre el pip de ese mismo `python3`; `--version` dice en qué carpeta instala.
- `uv run quien_soy.py` — dice qué Python usa tu proyecto y si está en un ambiente.

Los errores frecuentes, con su causa, están en [[trampas-de-ambientes]].
