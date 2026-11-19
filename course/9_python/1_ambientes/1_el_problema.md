---
id: el-problema-de-los-ambientes
title: "El problema: un solo Python para todo"
nav_title: "El problema"
summary: "Sin ambientes, todos tus proyectos comparten los mismos paquetes, y el sistema operativo ya no te deja instalarlos encima de su Python."
status: ready
estimated_time: 5m
tags: [ambiente, site-packages, pep-668, pip]
prerequisites: [ambientes-python]
---

# El problema: un solo Python para todo

**Página 1 de 10 · Ambientes**

Meta: ver los dos errores que hacen necesarios los ambientes.

::: figure {#py-choque title="Dos proyectos, un solo Python"}
![Dos columnas. A la izquierda, sin ambientes: proyecto-a pide pandas 1.5 y proyecto-b pide pandas 2.2, y los dos apuntan al único site-packages del Python del sistema, donde sólo cabe una versión, la 2.2; la flecha de proyecto-a termina en rojo. A la derecha, con un .venv por proyecto: cada proyecto tiene su propio site-packages con su versión.](../_assets/py-choque.svg)
:::

## En corto

- Sin ambientes, **todos tus proyectos comparten un solo `site-packages/`**: instalar una versión borra la otra.
- En Ubuntu 24.04 y en macOS con Homebrew, **el sistema ya no te deja** hacer `pip install` sobre su Python (PEP 668).
- La salida: **un ambiente por proyecto**.

## Falla 1: una versión borra a la otra

`site-packages/` es la carpeta donde Python guarda los paquetes instalados. Sin ambientes hay **una sola**.

| Paso | Qué haces | Qué queda en `site-packages/` |
|---|---|---|
| Lunes | `pip install pandas==1.5` para `proyecto-a` | pandas 1.5 |
| Jueves | `pip install pandas==2.2` para `proyecto-b` | pandas 2.2 — **la 1.5 ya no está** |
| Lunes siguiente | corres `proyecto-a` | truena con una versión que no conoce |

`pip` es el instalador de paquetes que viene con Python; `pip install pandas==1.5` baja pandas de PyPI (`pypi.org`, el registro público de paquetes) y `==1.5` pide exactamente esa versión.

Nadie tocó el código de `proyecto-a`. Lo rompió una instalación de otro proyecto.

## Falla 2: el sistema te lo prohíbe

En Ubuntu 24.04, `pip install` sobre el Python del sistema:

```bash
pip install rich
```

**Qué hace cada pieza:**

- `pip install rich` — pide a `pip` que baje el paquete `rich` y lo instale en el `site-packages/` del Python del sistema.

Si tu sistema tiene su `pip` instalado (paquete `python3-pip`), **sale esto** (salida real, recortada):

```text
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
hint: See PEP 668 for the detailed specification.
```

`apt install python3-xyz`, en el mensaje, es el instalador de paquetes de Ubuntu; `python3 -m venv` crea un ambiente (lo haces en [[lab-venv-y-pip]]). Si tu sistema no trae `pip`, sale `pip: command not found`: tampoco te da un `pip` global.

Ese Python lo usa el propio sistema operativo para sus herramientas. Si le cambias paquetes, las puedes romper. Por eso, desde 2023, Debian, Ubuntu y Homebrew lo bloquean. PEP 668 es el documento de Python (una PEP es una propuesta de cambio aprobada) que define ese bloqueo.

## Lo que vas a usar

| Problema | Lo resuelve |
|---|---|
| Versiones que chocan entre proyectos | Un `.venv/` por proyecto |
| «En mi máquina sí funciona» | `uv.lock`, con la versión exacta de cada paquete |
| El Python del sistema bloqueado | No lo tocas: uv instala y usa el suyo |

`uv.lock` es el **lockfile**: un archivo que escribe `uv lock` con la versión exacta de cada paquete. El Python propio lo baja `uv python install`. Los dos se explican en [[las-piezas-de-un-ambiente]] y [[lab-uv]].

::: problem {#py-problema-pisa title="¿Quién se rompió?"}
Instalaste `pandas==1.5` para la tarea del lunes y el jueves `pandas==2.2` para otra, las dos con `pip install` sin ambiente. El lunes siguiente corres la primera y truena. ¿Qué pasó, si no tocaste su código?
:::

::: hint {of="py-problema-pisa"}
¿Cuántas carpetas `site-packages/` hay en tu máquina sin ambientes?
:::

::: answer {of="py-problema-pisa"}
- Una sola. El segundo `pip install` reemplazó la 1.5 por la 2.2.
- La tarea del lunes ahora corre con una versión que no conoce.
- Con un `.venv/` por proyecto, cada uno guarda la suya y no se tocan.
:::

Sigue con [[las-piezas-de-un-ambiente]]: las nueve palabras que vas a leer en todo README de Python.

> [!NOTE]
> **Si sólo recuerdas una cosa:** sin ambientes, todos tus proyectos comparten los mismos paquetes, y el último que instala gana.
