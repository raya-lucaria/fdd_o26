---
id: las-piezas-de-un-ambiente
title: "Las piezas"
nav_title: "Las piezas"
summary: "Nueve palabras que vas a leer en todo README de Python: qué es cada una y con qué comando la ves en tu máquina."
status: ready
estimated_time: 8m
tags: [interprete, paquete, pypi, pip, lockfile, toml, dependencia-transitiva]
prerequisites: [el-problema-de-los-ambientes]
---

# Las piezas

**Página 2 de 10 · Ambientes**

Meta: nombrar cada pieza y saber dónde verla en tu máquina.

## En corto

- Nueve palabras, y el comando que muestra cada una.
- **Un paquete es código de otros**, instalado como carpeta en `site-packages/`.
- **Un lockfile fija la versión exacta de cada paquete**, también de los que no pediste.

## Las nueve

::: table {#py-tabla-piezas title="Las piezas de un ambiente"}

| Término | Qué es | Lo ves con |
|---|---|---|
| Intérprete | El programa `python` que ejecuta tu código | `which python3` · `python3 --version` |
| Paquete | Código de otros, instalado como carpeta en `site-packages/` | `ls .venv/lib/python3.*/site-packages/` |
| PyPI | El registro público de paquetes de Python, en `pypi.org` | `uv add rich` lo baja de ahí |
| pip | El instalador que viene con Python | `python3 -m pip --version` |
| Dependencia transitiva | Un paquete que no pediste, pero que pide uno que sí | `uv tree` |
| Ambiente | Una carpeta con su intérprete y sus paquetes, aparte del sistema | `ls -a .venv` |
| Resolver | La parte del gestor que escoge versiones compatibles entre sí | `uv lock` |
| Lockfile | Archivo con la versión exacta y el hash de cada paquete | `cat uv.lock` |
| TOML | Formato de texto para configuración: `clave = valor` y `[secciones]` | `cat pyproject.toml` |

:::

Los comandos de la tercera columna; los de `.venv`, `uv` y `cat` se corren dentro de un proyecto uv, como el `hola/` de la página siguiente:

- `which python3` — dice qué archivo se ejecuta al escribir `python3`: el primero que encuentra en el `PATH`, la lista de carpetas donde la shell busca programas.
- `python3 --version` — imprime la versión del intérprete.
- `ls .venv/lib/python3.*/site-packages/` — lista los paquetes del ambiente; la shell cambia `python3.*` por la carpeta que exista (`python3.13`, por ejemplo).
- `uv add rich` — anota `rich` en `pyproject.toml`, lo baja de PyPI y lo instala en `.venv/`.
- `python3 -m pip --version` — `-m pip` corre pip como módulo de ese `python3`; la salida dice a qué Python pertenece.
- `uv tree` — dibuja el árbol de dependencias del proyecto, transitivas incluidas.
- `ls -a .venv` — lista la carpeta del ambiente, ocultos incluidos (`-a`).
- `uv lock` — corre el resolver y escribe el resultado en `uv.lock`, sin instalar nada.
- `cat uv.lock`, `cat pyproject.toml` — imprimen el archivo en la terminal.

El **hash** del lockfile es una huella de 64 caracteres calculada del archivo del paquete: si cambia un byte, ya no coincide y uv se niega a instalarlo.

## Lo que hace el resolver

Pediste `rich`. `rich` pide `pygments` y `markdown-it-py`, y éste pide `mdurl`. El resolver arma el árbol completo y elige versiones que encajen todas:

```text
demo v0.1.0
└── rich v15.0.0
    ├── markdown-it-py v4.2.0
    │   └── mdurl v0.1.2
    └── pygments v2.21.0
```

Ese árbol, con versiones exactas, es lo que se guarda en `uv.lock`.

## pip y uv, frente a frente

| Trabajo | pip | uv |
|---|---|---|
| Instalar paquetes de PyPI | ✅ | ✅ |
| Crear el ambiente | ❌ lo hace `venv`, aparte | ✅ |
| Fijar versiones exactas, transitivas incluidas | ❌ `pip freeze` sólo copia lo que hay | ✅ `uv.lock` |
| Instalar una versión de Python | ❌ | ✅ `uv python install` |

- `venv` — módulo que trae Python para crear ambientes: `python3 -m venv .venv`.
- `pip freeze` — imprime lo instalado ahora, con `==versión`; no distingue lo que pediste de lo que llegó como transitiva.
- `uv python install` — descarga un intérprete de Python que administra uv, aparte del sistema.

::: problem {#py-piezas-transitiva title="Un paquete que no pediste"}
Corriste sólo `uv add rich`. Abres `uv.lock` y aparece `pygments`. ¿De dónde salió, y qué pasaría si borras su entrada a mano?
:::

::: hint {of="py-piezas-transitiva"}
Corre `uv tree` y busca `pygments`.
:::

::: answer {of="py-piezas-transitiva"}
- `pygments` es una dependencia **transitiva**: `rich` la necesita para colorear código.
- El lock no se edita a mano: lo escribe uv. Si lo cambias, el siguiente `uv lock` lo regenera, y `uv sync --locked` falla porque ya no coincide con `pyproject.toml` (`uv sync` instala lo que dice el lock; `--locked` le prohíbe reescribirlo y lo hace fallar si está desactualizado).
:::

Sigue con [[un-ambiente-por-dentro]]: dónde vive cada una de estas piezas en tu disco.

> [!NOTE]
> **Si sólo recuerdas una cosa:** paquete, ambiente y lockfile son tres cosas distintas: código, carpeta y lista exacta.
