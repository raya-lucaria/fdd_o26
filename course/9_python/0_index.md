---
id: python
title: "Python"
nav_title: "Python"
summary: "Python para trabajar con datos de forma profesional, en tres secciones: los ambientes con uv, lo que hace Python por dentro cuando corre tu código, y cómo elegir el stack midiendo."
status: ready
estimated_time: 300m
tags: [python, uv, ambientes, venv, pip, polars, duckdb, pydantic]
prerequisites: [contenedores]
---

# Python

**Tres secciones** · 24 páginas · unos 300 min

## En corto

- La unidad es Python para trabajar con datos de forma profesional: código que corre igual en tu máquina, en la de otra persona y en un contenedor.
- **Empieza por los ambientes**; sigue con lo que hace Python cuando corre tu código. Los ambientes contestan dónde viven tus paquetes y qué versión de cada uno usa tu proyecto, con **uv**.
- Las demás secciones se agregan aquí cuando llega su clase.

## Las secciones

| # | Sección | Qué contesta | Sesión | Páginas | Min |
|---:|---|---|---|---:|---:|
| 1 | [[ambientes-python]] | Dónde viven tus paquetes, y cómo hacer que tu proyecto corra igual en otra máquina | jueves 1 de octubre, 19:00–20:00 | 12 | 120 |
| 2 | [[python-por-dentro]] | Qué hace Python cuando corre tu código, para pedirle bien a la IA y revisar lo que te entrega | martes 6 de octubre, 19:00–20:30 | 6 | 90 |
| 3 | [[elegir-el-stack]] | Qué librerías y formatos usar para datos en 2026, decidido midiendo y no por lo que la IA vio más | jueves 8 de octubre, 19:00–20:30 | 6 | 90 |

## Antes de empezar

**uv** es un programa de terminal, publicado en 2024 por la empresa Astral, que hace con un solo comando lo que antes pedía cuatro herramientas: crear el ambiente, instalar paquetes, fijar sus versiones e instalar Python mismo.

Necesitas **uv instalado antes de clase**, en la terminal donde trabajas el repo: Linux, WSL2 o macOS, la misma donde instalaste Docker en la unidad 8.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Qué hace cada pieza:**

- `curl -LsSf <url>` — descarga el instalador oficial de uv (`-L` sigue redirecciones, `-sS` sin barra de progreso pero con errores, `-f` falla si el servidor responde con error).
- `| sh` — se lo pasa a la shell, que lo ejecuta: instala `uv` en `~/.local/bin` y agrega esa carpeta a tu `PATH`.

El `PATH` es la lista de carpetas donde la shell busca un programa cuando escribes su nombre. El instalador lo cambia en el archivo de configuración de tu shell, y ese archivo sólo se lee al abrir una terminal. Por eso: cierra la terminal, abre otra y comprueba:

```bash
uv --version
```

**Qué hace cada pieza:**

- `uv --version` — `--version` le pide a uv que imprima su versión y salga. Si responde, uv está instalado y la shell lo encuentra.

**Deberías ver** una línea `uv 0.12.…` o más nueva. Docker, de la unidad anterior, lo necesitas para una de las entregas.
