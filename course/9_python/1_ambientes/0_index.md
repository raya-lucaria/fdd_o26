---
id: ambientes-python
title: "Ambientes"
nav_title: "1. Ambientes"
summary: "Qué es un ambiente de Python, qué herramientas existen y por qué usamos uv."
status: ready
tags: [python, uv, venv, pip, pyproject, lockfile, ambiente]
---

# Ambientes

**Sección 1** · 12 páginas · unos 120 min · sesión del jueves 1 de octubre, 19:00–20:00

Meta: que sepas en qué Python y con qué paquetes corre tu código, y cómo hacer que corra igual en otra máquina.

::: figure {#py-mapa title="Qué produce qué en un proyecto uv"}
![Tres cajas en fila. Lo que pides, pyproject.toml, con rangos como rich>=15, que escribes tú o uv add. Una flecha uv lock lleva a lo que se resolvió, uv.lock, con versión exacta y hash de cada paquete, también las transitivas, que se bajan de PyPI. Una flecha uv sync lleva a lo que está instalado, la carpeta .venv con su python y su site-packages, desechable. De .venv sale uv run hacia tu programa, y uv python install pone el intérprete. Abajo: pyproject.toml y uv.lock van a git; .venv no va a git, se borra y se recrea con uv sync.](../_assets/py-mapa.svg)
:::

**Los comandos del mapa**, en el orden en que los vas a usar:

- `uv add rich` — anota `rich` en `pyproject.toml` y, sin que lo pidas, corre `uv lock` y `uv sync`.
- `uv lock` — escoge una versión de cada paquete que encaje con todas las demás y la escribe en `uv.lock`.
- `uv sync` — instala en `.venv/` exactamente lo que dice `uv.lock`; si `.venv/` no existe, lo crea.
- `uv run main.py` — corre tu programa con el `python` de `.venv/`, sin activar nada.
- `uv python install` — descarga un intérprete de Python propio de uv, aparte del que trae tu sistema.

**PyPI** (`pypi.org`) es el registro público de donde se bajan los paquetes. El **hash** es una huella del archivo descargado: si cambia un byte, la huella no coincide y uv no lo instala.

## En corto

- **Un ambiente es una carpeta (`.venv/`) con su propio `python` y sus propios paquetes.**
- **Usamos uv**: un solo programa crea el ambiente, instala, fija versiones y pone el intérprete.
- A git van `pyproject.toml` y `uv.lock`; **`.venv/` nunca**.

## Las páginas

| # | Página | Qué agrega | Min | Dónde |
|---:|---|---|---:|---|
| 1 | [[el-problema-de-los-ambientes]] | Los dos errores que hacen necesarios los ambientes | 5 | clase |
| 2 | [[las-piezas-de-un-ambiente]] | Nueve palabras y el comando que muestra cada una | 8 | lectura |
| 3 | [[un-ambiente-por-dentro]] | Tres comandos que muestran qué es un ambiente y qué hace «activar» | 15 | clase |
| 4 | [[los-archivos-del-ambiente]] | `requirements.txt`, `pyproject.toml` y los locks: quién escribe cada uno | 8 | lectura |
| 5 | [[las-herramientas-de-ambientes]] | Doce herramientas con pros y contras, y por qué uv | 12 | lectura |
| 6 | [[ambiente-conda-docker]] | Qué aísla un `.venv`, conda y Docker | 6 | lectura |
| 7 | [[lab-uv]] | Un proyecto uv de punta a punta: crear, usar, romper y recrear | 30 | clase |
| 8 | [[lab-venv-y-pip]] | La forma clásica, y dónde instala `pip` sin ambiente activo | 10 | lectura |
| 9 | [[ambientes-en-vs-code]] | Que VS Code use el `.venv` de tu proyecto | 10 | clase |
| 10 | [[trampas-de-ambientes]] | Nueve errores con su causa y dónde mirar | 8 | lectura |

## Los anexos

| Anexo | Qué es | Cuándo lo abres | Min |
|---|---|---|---:|
| [[cheatsheet-ambientes]] | La misma tarea en uv, venv + pip, poetry y conda | En clase, y cada vez que leas un README ajeno | 5 |
| [[entregas-ambientes]] | Las dos entregas: qué vence, con qué branch y en qué carpeta | Antes de cada entrega | 8 |

## La clase de hoy, en 60 minutos

| Página | Min |
|---|---:|
| 1 · El problema | 5 |
| 3 · Un ambiente por dentro | 15 |
| 7 · Lab: uv | 30 |
| 9 · VS Code | 10 |

## Antes de clase

1. **uv instalado**: `uv --version` responde (instrucciones en [[python]]).
2. **Tu carpeta lista**: abre tu fork en VS Code y, en su terminal, el ritual de la unidad, que deja la branch de la entrega y copia tus dos carpetas:

```bash
cd {tu_fork_de_la_clase}
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-09-uv-docker
mkdir -p estudiantes/$GHUSER/09_python
cp -r codigo/09_python/ambientes codigo/09_python/uv_docker estudiantes/$GHUSER/09_python/
ls estudiantes/$GHUSER/09_python/ambientes
```

**Qué hace cada pieza:**

- `cd {tu_fork_de_la_clase}` — entras a la carpeta donde clonaste tu fork. Cada quien la tiene en otro lado: escribe la tuya, **sin las llaves**. Si no la recuerdas, `pwd` en la terminal de VS Code con tu fork abierto te la dice.
- `git switch main` — te pones en tu branch `main`.
- `&&` — corre el comando siguiente sólo si el anterior salió bien.
- `git fetch upstream` — descarga lo nuevo del repo del curso (`upstream`, el remoto que agregaste en la unidad de Git) sin tocar tus archivos.
- `git merge upstream/main` — mete eso nuevo en tu `main`.
- `git switch -c tarea-09-uv-docker` — `-c` crea la branch de la entrega y te cambia a ella. Ahí trabajas labs y entrega.
- `mkdir -p estudiantes/$GHUSER/09_python` — creas tu carpeta de la unidad; `-p` crea también las carpetas intermedias y no falla si ya existe. `$GHUSER` es tu usuario de GitHub, guardado en tu shell desde la unidad de Git.
- `cp -r codigo/09_python/ambientes codigo/09_python/uv_docker estudiantes/$GHUSER/09_python/` — copias las dos carpetas por nombre (`-r`: con subcarpetas) dentro de tu `09_python/`. `por_dentro/` es de otra entrega y no se copia aquí.
- `ls estudiantes/$GHUSER/09_python/ambientes` — lista la carpeta: compruebas que llegaron los archivos de los labs.

**Deberías ver** `hola.py`, `quien_soy.py`, `requirements.txt` y `script_autonomo.py`.

**Todo se trabaja en tu carpeta de estudiante**, como el resto del curso: los labs en `09_python/ambientes/` y la entrega en `09_python/uv_docker/`. Los dos se suben juntos, en el pull request de `tarea-09-uv-docker`. Los `.venv/` que creen los labs no se suben: el `.gitignore` del curso los deja fuera.

Los comandos son para la terminal de **Linux, WSL2 o macOS**.
