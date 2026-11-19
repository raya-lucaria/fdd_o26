---
id: trampas-de-ambientes
title: "Las trampas"
nav_title: "Las trampas"
summary: "Nueve errores de ambientes, cada uno con su síntoma, su causa y dónde mirar. Casi todos son «corriste otro Python del que crees»."
status: ready
estimated_time: 8m
tags: [errores, modulenotfounderror, pep-668, dockerignore, lockfile]
prerequisites: [ambientes-en-vs-code]
---

# Las trampas

**Página 10 de 10 · Ambientes**

Meta: reconocer el error antes de reinstalar nada.

## En corto

- Casi todo error de ambientes es **«corriste otro Python del que crees»**.
- `quien_soy.py` lo diagnostica en un segundo: dice qué Python corre y si tiene el paquete.
- La tabla dice síntoma, causa y dónde mirar.

## Síntoma, causa, dónde mirar

::: table {#py-tabla-trampas title="Síntoma, causa y dónde mirar"}

| Síntoma | Causa | Dónde mirar |
|---|---|---|
| `ModuleNotFoundError` con el paquete «instalado» | Corres otro Python: terminal sin activar, o VS Code con otro intérprete | `uv run quien_soy.py` (dice qué Python corre); la barra de estado de VS Code (dice qué intérprete eligió) |
| `error: externally-managed-environment` | `pip install` sobre el Python del sistema (PEP 668) | [[el-problema-de-los-ambientes]] |
| `pip install` «funcionó» pero el programa no lo ve | `pip` y `python` son de Pythons distintos | `python3 -m pip --version`: corre el pip **de ese** `python3` e imprime la carpeta donde instala |
| `ensurepip is not available` al crear un venv | En Ubuntu o WSL falta el paquete `python3-venv` | `sudo apt install python3-venv python3-pip`, una sola vez: instala con permisos de administrador los dos paquetes de Ubuntu que traen `venv` y `pip` |
| `python: command not found` | En tu sistema se llama `python3`, o no hay ambiente activo | `which python3`: imprime la ruta del `python3` que tu shell encuentra primero; si no imprime nada, no hay ninguno |
| La revisión de entregas rechaza tu PR por `.venv` | Subiste el ambiente al repo | [[lab-uv]], «Qué subes a git» |
| La imagen de Docker trae un `.venv` que no corre | Copiaste todo el proyecto a la imagen, y con él tu `.venv/` local | `.dockerignore`: lista de rutas que `docker build` no copia; debe traer `.venv`. Ver [[entregas-ambientes]] |
| `uv sync --locked` falla: «The lockfile at `uv.lock` needs to be updated» | Cambiaste `pyproject.toml` y no regeneraste el lock | `uv lock`: vuelve a calcular las versiones desde `pyproject.toml` y reescribe `uv.lock`; luego `uv sync` |
| Dos proyectos y las versiones «se mezclan» | Los dos usan el mismo ambiente, o ninguno | `ls -a` en cada proyecto: lista también lo oculto (`-a`), y `.venv/` empieza con punto. ¿Cada uno tiene el suyo? |

:::

## El diagnóstico en tres comandos

**Haz:** en la terminal donde algo falla,

```bash
which python3
python3 -m pip --version
uv run quien_soy.py
```

**Qué hace cada pieza:**

- `which python3` — la ruta del `python3` que corre esta terminal cuando escribes `python3`.
- `python3 -m pip --version` — `-m pip` corre el pip que pertenece a ese mismo `python3`; `--version` imprime su versión y la carpeta donde instala.
- `uv run quien_soy.py` — corre el script con el Python del `.venv/` del proyecto y dice cuál es.

**Deberías ver:** si las dos primeras apuntan fuera de tu proyecto y la tercera dice `.venv`, el problema es la terminal, no el paquete.

## El `.venv` que viaja a Docker

Si tu `Dockerfile` copia **todo** el proyecto a la imagen, tu `.venv/` local viaja con él y pisa el que uv creó dentro. Trae enlaces al Python de **tu** máquina: en la imagen apuntan a rutas que no existen, o a un Python de otro sistema operativo. A veces funciona por casualidad, cuando tu máquina y la imagen coinciden; en la del revisor no.

::: problem {#py-trampa-diagnostico title="Lo instalé tres veces"}
Tu compañero dice: «instalé pandas tres veces, con `pip install pandas`, y sigue diciendo `ModuleNotFoundError`». ¿Qué le pides que corra antes de un cuarto intento, y qué esperas ver?
:::

::: hint {of="py-trampa-diagnostico"}
¿Qué te dice `python3 -m pip --version` que no te dice `pip install`?
:::

::: answer {of="py-trampa-diagnostico"}
- `python3 -m pip --version` y `which python3`: dicen en qué Python está instalando y cuál está corriendo.
- Lo más probable: `pip` instala en un Python y su programa corre con otro.
- Arreglo en un proyecto uv: `uv add pandas` y `uv run`, que usan siempre el mismo `.venv`.
:::

Sigue con [[cheatsheet-ambientes]]: todos los comandos de la sección en una tabla.

> [!NOTE]
> **Si sólo recuerdas una cosa:** antes de reinstalar nada, pregunta qué Python está corriendo.
