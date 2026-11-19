---
id: las-herramientas-de-ambientes
title: "Las herramientas, con pros y contras"
nav_title: "Las herramientas"
summary: "pip, venv, pip-tools, pipenv, poetry, pdm, hatch, conda, pixi, pyenv, pipx y uv: qué trabajo hace cada una, sus pros y contras, y por qué en este curso usamos uv."
status: ready
estimated_time: 12m
tags: [uv, pip, poetry, conda, pixi, pdm, hatch, pyenv, pipx, pipenv]
prerequisites: [los-archivos-del-ambiente]
---

# Las herramientas, con pros y contras

**Página 5 de 10 · Ambientes**

Meta: reconocer cada herramienta cuando la veas en un repo ajeno, y saber por qué aquí usamos uv.

::: figure {#py-trabajos title="Cinco trabajos, doce herramientas"}
![Matriz de doce herramientas contra cinco trabajos: instalar paquetes, aislar, proyecto + lock, versiones de Python y herramientas de terminal. pip sólo instala; venv sólo aísla; pip-tools sólo fija versiones; pipenv y poetry instalan, aíslan y manejan proyecto con lock; pdm y hatch además instalan versiones de Python; conda hace casi todo y su lock es a medias; pixi y uv hacen los cinco; pyenv sólo versiones de Python; pipx instala herramientas de terminal aisladas. La fila de uv está resaltada.](../_assets/py-trabajos.svg)
:::

## En corto

- Cada herramienta resuelve **uno o varios de cinco trabajos**: instalar paquetes, aislar, proyecto + lock, versiones de Python, herramientas de terminal.
- **uv hace los cinco, y rápido.** No instala paquetes que no son de Python.
- Las vas a encontrar todas en proyectos ajenos: hay que reconocerlas, no dominarlas.

## Las palabras de la tabla

- **PyPI** — el registro público de paquetes de Python, de donde descargan pip y uv.
- **Transitivas** — los paquetes que tus paquetes instalan por su cuenta (`rich` trae `pygments`).
- **Lock** — archivo que la herramienta escribe con la versión exacta de cada paquete, transitivas incluidas.
- **Resolver** — calcular qué versión de cada paquete cumple todos los rangos a la vez; lo hace la herramienta antes de instalar.
- **Paquetes de fuera de Python** — librerías escritas en C o C++ que no vienen en PyPI como paquete de Python: CUDA (GPU de NVIDIA), GDAL (mapas).
- **Programa de terminal** (CLI) — algo que corres por nombre en la shell, `ruff check .`, en lugar de importarlo en tu código.
- **Publicar** — subir tu proyecto a PyPI para que otros lo instalen con `pip install`.

## La tabla

::: table {#py-tabla-herramientas title="Las herramientas, con pros y contras"}

| Herramienta | Desde | Qué hace | 👍 | 👎 | Dónde la vas a ver |
|---|---|---|---|---|---|
| **pip** | 2008 | Descarga paquetes de PyPI y los instala en el Python activo | Viene con Python | No aísla; no fija las transitivas | Todos los tutoriales |
| **venv** | 2012 (Python 3.3) | Crea una carpeta `.venv/` con un Python y sus paquetes aparte | Viene con Python | Sólo aísla; lo demás lo haces tú | READMEs, Dockerfiles |
| pip-tools | 2012 | Lee tu lista corta (`requirements.in`) y escribe `requirements.txt` con cada versión exacta, transitivas incluidas | Simple, encima de pip | Sólo hace eso | Proyectos maduros |
| pipenv | 2017 | Instala, crea el ambiente y escribe un lock; sus archivos son `Pipfile` y `Pipfile.lock` | Fue el primer todo-en-uno | Lento; perdió impulso | Proyectos de 2018 a 2020 |
| **poetry** | 2018 | Escribe `pyproject.toml` y `poetry.lock`, instala, y publica en PyPI | Maduro, muy usado | Más lento; formato propio hasta su versión 2 (2025) | Muchas empresas |
| pdm | 2019 | Lo mismo que poetry (`pdm.lock`), escribiendo sólo secciones estándar | Muy estándar | Comunidad chica | Librerías |
| hatch | 2017 | Crea varios ambientes por proyecto (uno por versión de Python a probar) y publica en PyPI | El más cómodo para publicar librerías | Menos pensado para aplicaciones | Librerías open source |
| **conda** / mamba | 2012 | Instala paquetes de Python **y de fuera de Python**, y su propio Python, desde su registro (conda-forge); mamba es una versión más rápida | CUDA, GDAL, R | Pesado; otro registro de paquetes; la distribución Anaconda cobra licencia a organizaciones grandes (términos de 2024) | Ciencia, academia |
| pixi | 2023 | Instala los paquetes de conda y escribe un lock (`pixi.lock`) | Lo de conda con un flujo moderno | Joven | GPU, geoespacial |
| pyenv | 2012 | Descarga e instala varias versiones de Python, y escoge cuál usa cada carpeta | Hace bien una sola cosa | uv ya lo hace | Máquinas de desarrolladores |
| pipx | 2018 | Instala un programa de terminal hecho en Python en su propio ambiente, y lo deja en tu `PATH` | Sencillo | uv tiene `uvx` | `pipx install ruff` |
| **uv** | 2024 | **Los cinco trabajos**: instala, crea `.venv/`, escribe `uv.lock`, instala Pythons y programas de terminal | 10 a 100 veces más rápido que pip; un solo binario; sigue los estándares | Es de una empresa (Astral), cuya compra anunció OpenAI el 2026-03-19; no instala paquetes de fuera de Python | **Este curso** |

:::

Los comandos de la tabla:

- `pipx install ruff` — instala `ruff` (un revisor de estilo de Python) en un ambiente propio; después tecleas `ruff` en cualquier carpeta y corre.
- `uvx ruff check .` — `uvx` (abreviatura de `uv tool run`) descarga `ruff` a un ambiente temporal y lo corre una vez, sin instalarlo en tu proyecto.

## Por qué uv

- **Velocidad**: resuelve (calcula las versiones) e instala en segundos lo que con pip o poetry tarda minutos. En clase se nota.
- **Un solo programa** (un binario: un ejecutable que no necesita Python para correr): hace el trabajo de pip, venv, pip-tools, pyenv y pipx. Menos cosas que instalar y que se contradigan.
- **Archivos estándar**: escribe `pyproject.toml` (PEP 621) y exporta `pylock.toml` (PEP 751); un PEP es el documento que fija una regla de Python, y cualquier herramienta puede leer esos archivos. Si mañana cambias de herramienta, tu `pyproject.toml` sirve igual.

## Lo que uv no te da

- **Paquetes de fuera de Python** (CUDA, GDAL, compiladores): para eso, pixi o conda.
- **Independencia de una empresa**: uv es open source (licencias MIT y Apache), pero lo desarrolla una sola compañía. El seguro es el mismo: los archivos son estándar.

Una que ya no vas a ver en proyectos nuevos: **rye** (2023). Astral la tomó en 2024 y hoy recomienda uv en su lugar.

## ¿Cuál uso?

::: figure {#py-cual-uso title="¿Cuál uso?"}
![Árbol de decisión de tres preguntas. ¿Necesitas paquetes que no son de Python, como CUDA o GDAL? Sí: pixi, o conda. No: ¿el proyecto ya usa poetry, pdm o hatch? Sí: usa esa y lee su pyproject.toml. No: ¿es un script suelto? Sí: uv run script.py con sus dependencias dentro, PEP 723. No: uv init y uv add, que es el caso de este curso.](../_assets/py-cual-uso.svg)
:::

Lo que nombran las hojas del árbol:

- `uv run script.py` — corre el script; si el script declara sus dependencias en un comentario al inicio (PEP 723), uv las instala antes en un ambiente temporal.
- `uv init` y `uv add` — crean el proyecto y le agregan paquetes; los usas paso a paso en [[lab-uv]].

**Regla práctica**: en un repo ajeno, **usa la herramienta que ya usa el repo**. Su lock (`poetry.lock`, `uv.lock`, `pixi.lock`) te lo dice.

::: problem {#py-herramientas-elige title="Tres repos, tres herramientas"}
Te pasan tres repos: (a) un notebook que entrena un modelo con CUDA y trae `environment.yml`; (b) una API que trae `pyproject.toml` y `poetry.lock`; (c) tu tarea de este curso. ¿Con qué herramienta trabajas cada uno?
:::

::: hint {of="py-herramientas-elige"}
Mira qué archivo de lock o de ambiente trae cada repo, y la figura «¿Cuál uso?».
:::

::: answer {of="py-herramientas-elige"}
- (a) conda o pixi: necesita CUDA, que no es un paquete de Python, y ya trae `environment.yml`.
- (b) poetry: el lock es suyo. Mezclar herramientas en un mismo repo produce dos locks que se contradicen.
- (c) uv.
:::

Fuentes: [Which Python package manager should I use? (pydevtools, 2026)](https://pydevtools.com/handbook/explanation/which-python-package-manager-should-i-use/) · [OpenAI to acquire Astral (2026-03-19)](https://openai.com/index/openai-to-acquire-astral/) · [Documentación de uv](https://docs.astral.sh/uv/).

Sigue con [[ambiente-conda-docker]]: qué aísla cada una, comparado con un contenedor.

> [!NOTE]
> **Si sólo recuerdas una cosa:** las herramientas cambian; pyproject.toml se queda.
