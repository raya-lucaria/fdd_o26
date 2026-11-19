---
id: ambientes-en-vs-code
title: "Ambientes en VS Code"
nav_title: "VS Code"
summary: "Que VS Code use el .venv de tu proyecto: elegirlo con Ctrl+Shift+P, verlo en la barra de estado y en la terminal integrada."
status: ready
estimated_time: 10m
tags: [vs-code, interprete, venv, jupyter, kernel]
prerequisites: [lab-uv]
---

# Ambientes en VS Code

**Página 9 de 10 · Ambientes**

Meta: que VS Code use el `.venv/` de tu proyecto, y saber comprobarlo.

## En corto

- **Ctrl+Shift+P** (macOS: **Cmd+Shift+P**) → *Python: Select Interpreter* → el `.venv` del proyecto.
- **El intérprete activo se ve abajo a la derecha**, en la barra de estado.
- La terminal integrada que abras después **se activa sola** con ese intérprete.

## Tres palabras antes de empezar

- **Intérprete:** el programa `python` que ejecuta tu código; cada `.venv/` trae el suyo en `.venv/bin/python`.
- **Barra de estado:** la franja delgada al pie de la ventana de VS Code; a la derecha dice qué intérprete usa.
- **Paleta de comandos:** el buscador de todas las acciones de VS Code; se abre con **Ctrl+Shift+P** (macOS: **Cmd+Shift+P**).

VS Code no corre tu proyecto con el `.venv` por su cuenta: usa el intérprete que tenga elegido. Si eliges otro, marca errores en paquetes que sí instalaste.

## Requisito

La extensión **Python** de Microsoft (`ms-python.python`). Es la que agrega los comandos `Python: …` a la paleta.

- Si no la tienes: **Ctrl+Shift+X** abre el panel de extensiones; busca «Python», elige la de Microsoft, *Install*.

## Elegir el ambiente que hizo uv

1. Abre **tu fork** en VS Code desde la terminal: `code {tu_fork_de_la_clase}` (escribe tu ruta, sin llaves).
2. **Ctrl+Shift+P** abre la paleta de comandos.
3. Escribe `Python: Select Interpreter` y presiona Enter.
4. Elige el `.venv` **del proyecto en el que trabajas**. La ruta dice cuál es: `./estudiantes/<tu-login>/09_python/ambientes/demo/.venv/bin/python`.
5. Abre un archivo `.py` y mira la barra de estado: ahora dice la versión y el nombre del ambiente. Sin un `.py` abierto, no aparece.

**Qué hace cada pieza:**

- `code {tu_fork_de_la_clase}` — abre VS Code con esa carpeta. En macOS, si la terminal dice `command not found`, corre una vez en la paleta *Shell Command: Install 'code' command in PATH*. En WSL2, `code` abre VS Code conectado a Linux.
- *Python: Select Interpreter* — le dice a VS Code con qué `python` analizar, correr y depurar el código de esta carpeta. Lo recuerda para la próxima vez.
- `.venv/bin/python` — es el intérprete del ambiente: elegirlo es elegir el ambiente, con sus paquetes.

Si el `.venv` no aparece en la lista, todavía no existe. En la terminal, dentro de la carpeta del proyecto:

```bash
uv sync
```

**Qué hace cada pieza:**

- `uv sync` — lee `pyproject.toml` y `uv.lock`, crea `.venv/` si falta e instala ahí exactamente las versiones del lock. Después repite desde el paso 2.

## Crear uno desde VS Code

**Ctrl+Shift+P** → `Python: Create Environment` → *Venv* → la versión de Python → (opcional) marca `requirements.txt` para instalarlo.

- *Python: Create Environment* — crea un ambiente nuevo y lo deja elegido como intérprete.
- *Venv* — lo crea con el módulo `venv` de Python y le instala paquetes con `pip`, **no con uv**: no escribe nada en `pyproject.toml` ni en `uv.lock`.
- Lo crea en la **raíz de lo que tengas abierto**: con tu fork abierto, en la raíz del repo, no en tu carpeta.

Por eso en este curso el ambiente lo crea uv, en la terminal y dentro de tu carpeta; VS Code **sólo lo elige**.

## Notebooks: el kernel

Un **kernel** es el proceso de Python que ejecuta las celdas de un notebook `.ipynb`. Para que el notebook use tu `.venv`, el `.venv` necesita el paquete `ipykernel`:

```bash
uv add --dev ipykernel
```

**Qué hace cada pieza:**

- `uv add ipykernel` — instala `ipykernel` en el `.venv` y lo anota en `pyproject.toml` y `uv.lock`. Es el paquete que deja a VS Code arrancar ese Python como kernel.
- `--dev` — lo anota como dependencia **de desarrollo**: la usas tú al trabajar, pero tu programa no la importa. `uv sync --no-dev` (por ejemplo en Docker) la deja fuera.

Luego, con el notebook abierto: **Select Kernel** (arriba a la derecha del notebook) → *Python Environments* → el mismo `.venv`.

## Comprobar que está bien

| Dónde | Qué ves si está bien |
|---|---|
| Barra de estado, abajo a la derecha, con un `.py` abierto | La versión de Python y el ambiente; el rótulo exacto cambia con la versión de la extensión |
| Una terminal integrada nueva (Ctrl+ñ o Ctrl+\`) | El prompt empieza con `(demo)` |
| `quien_soy.py` corrido con el botón ▶ | `¿en un ambiente?  : sí` |
| Un notebook `.ipynb` → *Select Kernel* | El mismo `.venv` |

- **Terminal integrada:** la terminal dentro de VS Code. Al abrirla, VS Code corre ahí mismo el `activate` del intérprete elegido; por eso aparece `(demo)`.
- **Botón ▶** (arriba a la derecha de un `.py`): corre el archivo con el intérprete elegido.

La terminal integrada sólo se activa sola si la abres **después** de elegir el intérprete. Una que ya estaba abierta sigue igual: ciérrala y abre otra.

::: problem {#py-vscode-rojo title="Subrayado en rojo"}
`from rich import print` sale subrayado en amarillo o rojo en VS Code, con el aviso «Import "rich" could not be resolved». Pero `uv run hola.py` en la terminal funciona. ¿Qué está mal?
:::

::: hint {of="py-vscode-rojo"}
¿Qué intérprete dice la barra de estado?
:::

::: answer {of="py-vscode-rojo"}
- VS Code está analizando tu código con otro Python, normalmente el del sistema, que no tiene `rich`.
- `uv run` usa el `.venv`; VS Code no lo sabe hasta que se lo dices.
- Arreglo: Ctrl+Shift+P → *Python: Select Interpreter* → `.venv`. El código estaba bien.
:::

Sigue con [[trampas-de-ambientes]]: los errores de ambientes y dónde mirar.

> [!NOTE]
> **Si sólo recuerdas una cosa:** VS Code no adivina tu ambiente: se lo dices con Select Interpreter y lo compruebas en la barra de estado.
