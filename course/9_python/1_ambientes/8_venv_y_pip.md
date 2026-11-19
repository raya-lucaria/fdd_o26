---
id: lab-venv-y-pip
title: "Lab corto: venv y pip, la forma clásica"
nav_title: "Lab: venv y pip"
summary: "Crear, activar, instalar, congelar y borrar un ambiente con python -m venv y pip, y comprobar dónde instala pip cuando no hay ambiente activo."
status: ready
estimated_time: 10m
tags: [venv, pip, requirements, freeze, activate]
prerequisites: [lab-uv]
---

# Lab corto: venv y pip, la forma clásica

**Página 8 de 10 · Ambientes**

Meta: reconocer el flujo de `venv` + `pip` que trae casi todo README, y ver dónde instala `pip` cuando no hay ambiente activo.

## En corto

- **`python -m venv` + `pip` es la forma clásica**, y la vas a ver en casi todo README.
- **`pip` instala en el Python que esté primero en el `PATH`** (la lista de carpetas donde la shell busca programas), haya ambiente activo o no.
- uv hace lo mismo con menos pasos y con lock (`uv.lock`: versiones exactas y hashes).

### 1. Crear y activar

En Ubuntu o WSL recién instalados, `python3 -m venv` falla con `ensurepip is not available`: falta un paquete del sistema. Se arregla una vez con `sudo apt install python3-venv python3-pip`: `apt` es el instalador de paquetes de Ubuntu y Debian, y `sudo` lo corre como administrador porque toca el sistema. En macOS no hace falta.

**Haz:**

```bash
cd {tu_fork_de_la_clase}/estudiantes/$GHUSER/09_python/ambientes
python3 -m venv .venv
source .venv/bin/activate
python quien_soy.py
```

**Qué hace cada pieza:**

- `cd …/ambientes` — entras a tu carpeta de labs. `{tu_fork_de_la_clase}` es donde clonaste tu fork: pon la tuya, sin llaves.
- `python3 -m venv .venv` — `-m` (module) corre un módulo de Python como programa; el módulo `venv` crea un ambiente vacío en la carpeta `.venv/`. Se llama `.venv` porque es el nombre que uv y VS Code buscan.
- `source .venv/bin/activate` — lo activa: tu shell encuentra primero el `python` y el `pip` de `.venv/`. `source` corre el archivo dentro de tu shell actual; por eso puede cambiarle el `PATH`.
- `python quien_soy.py` — `quien_soy.py` imprime qué Python corre y si tiene `rich`. Activado ya existe `python` a secas: el de `.venv/bin/`.

**Deberías ver:** el prompt empieza con `(.venv)`, y (recortado)

```text
python que corre  : …/estudiantes/ana/09_python/ambientes/.venv/bin/python
sys.prefix        : …/estudiantes/ana/09_python/ambientes/.venv
¿en un ambiente?  : sí
rich              : NO instalado en este Python
```

El ambiente existe y está activo, pero vacío: `venv` no instala nada.

### 2. Instalar y congelar

**Haz:**

```bash
pip install -r requirements.txt
python hola.py
pip freeze
```

**Qué hace cada pieza:**

- `requirements.txt` — archivo de texto con un paquete por línea; viene en tu carpeta de labs.
- `pip install -r requirements.txt` — baja de PyPI (el repositorio público de paquetes de Python) e instala cada paquete de la lista (`-r`: lee los nombres de ese archivo) en el ambiente activo.
- `python hola.py` — corre el hola mundo, que necesita `rich`: comprueba que la instalación sirvió.
- `pip freeze` — lista todo lo instalado en el ambiente activo, con su versión exacta (`==`).

**Deberías ver:**

```text
Hola desde un Python que sí tiene rich instalado.
markdown-it-py==4.2.0
mdurl==0.1.2
Pygments==2.21.0
rich==15.0.0
```

`pip freeze` lista **todo** lo instalado con su versión. `pip freeze > requirements.txt` es la forma clásica de «fijar» versiones: `>` guarda la salida en ese archivo (lo sobrescribe). Copia lo que hay, sin hash (la huella que comprueba que el archivo bajado es el mismo) y sin distinguir lo que pediste de lo que vino arrastrado (las dependencias **transitivas**: `rich` pidió las otras tres).

### 3. El experimento: pip sin activar

Antes de correrlo, **escribe tu predicción**: sin ambiente activo, ¿dónde va a instalar `pip`?

**Haz:**

```bash
deactivate
python3 hola.py
python3 -m pip install rich
python3 quien_soy.py
```

**Qué hace cada pieza:**

- `deactivate` — sales del ambiente: tu shell vuelve a encontrar el Python del sistema.
- `python3 hola.py` — intentas correr el hola mundo fuera del ambiente. Sin activar se escribe `python3`: en muchos Linux no existe `python` a secas.
- `python3 -m pip install rich` — usa el `pip` de ese mismo `python3` para instalar `rich`. Con `-m pip` sabes a qué Python le instalas; un `pip` a secas puede ser de otro.
- `python3 quien_soy.py` — compruebas dónde quedó.

**Deberías ver:** `python3 hola.py` truena con `ModuleNotFoundError: No module named 'rich'`, porque ya no estás en el ambiente. Y luego, una de dos cosas según tu sistema:

| Tu sistema | Qué pasa |
|---|---|
| Ubuntu 24.04, Debian 12, macOS con Homebrew | `error: externally-managed-environment` ([[el-problema-de-los-ambientes]]): el sistema te frena |
| Ubuntu o WSL sin `python3-pip` | `No module named pip`: no hay `pip` global en dónde instalar |
| Un Python instalado a mano (sin esa protección) | **Instala en el Python global**, y `quien_soy.py` lo confirma: |

```text
¿en un ambiente?  : no
rich              : instalado, versión 15.0.0
```

Ésa es la trampa: `pip` no te avisa que no hay ambiente. Instaló en el Python de todo tu sistema. Si te pasó, `python3 -m pip uninstall rich` lo deshace.

### 4. Borrar

**Haz:**

```bash
rm -rf .venv
ls -a
```

**Qué hace cada pieza:**

- `rm -rf .venv` — borra la carpeta del ambiente con todo lo de adentro (`-r`: recursivo; `-f`: sin preguntar).
- `ls -a` — lista lo que queda, también lo oculto (`-a`): `.venv` empieza con punto y `ls` a secas no lo mostraría.

**Deberías ver:** ya no está `.venv`; tus archivos sí. Borrar el ambiente es borrar la carpeta.

## venv + pip contra uv

| Paso | venv + pip | uv |
|---|---|---|
| Crear el ambiente | `python3 -m venv .venv` | automático con `uv add` o `uv run` |
| Activar | `source .venv/bin/activate` | no hace falta: `uv run` |
| Instalar | `pip install rich` | `uv add rich` |
| Fijar versiones | `pip freeze > requirements.txt` | `uv.lock`, automático |
| Recrear en otra máquina | `python3 -m venv .venv` + activar + `pip install -r requirements.txt` | `uv sync` |

- `uv sync` — deja `.venv/` idéntico a `uv.lock`, sin activar nada.

::: problem {#py-pip-global title="Instaló, pero ¿dónde?"}
Abres una terminal, entras a tu proyecto (que tiene `.venv/`), corres `pip install pandas` y sale bien. Luego `uv run analisis.py` dice `ModuleNotFoundError: No module named 'pandas'`. ¿Dónde quedó pandas?
:::

::: hint {of="py-pip-global"}
¿La terminal estaba activada cuando corriste `pip`?
:::

::: answer {of="py-pip-global"}
- Sin activar, `pip` instaló en el Python que encontró primero en el `PATH`: el del sistema (o el de otro ambiente).
- `uv run` usa el `.venv/` del proyecto, que no tiene pandas.
- Arreglo: `uv add pandas`. Y, si quedó en el global, `python3 -m pip uninstall pandas`.
:::

Sigue con [[ambientes-en-vs-code]]: que el editor use el ambiente correcto.

> [!NOTE]
> **Si sólo recuerdas una cosa:** pip instala donde apunta tu PATH; si no sabes dónde es, corre quien_soy.py antes.
