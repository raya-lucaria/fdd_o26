---
id: ambiente-conda-docker
title: "Ambiente, conda y Docker"
nav_title: "Ambiente, conda y Docker"
summary: "Qué capa aísla cada uno: un .venv sólo los paquetes de Python, conda y pixi también el intérprete y algunas librerías, Docker todo menos el kernel."
status: ready
estimated_time: 6m
tags: [venv, conda, pixi, docker, aislamiento]
prerequisites: [las-herramientas-de-ambientes]
---

# Ambiente, conda y Docker

**Página 6 de 10 · Ambientes**

Meta: saber qué parte de tu máquina queda fija con cada herramienta, y qué parte no.

::: figure {#py-aislamiento title="Qué capa aísla cada uno"}
![Cuatro capas apiladas de abajo hacia arriba: kernel, librerías y programas del sistema, intérprete de Python y paquetes de Python. Tres barras muestran qué cubre cada herramienta: el .venv de uv cubre los paquetes y el intérprete si uv lo instaló; conda y pixi cubren paquetes, intérprete y las librerías del sistema que empaquetan; Docker cubre todo menos el kernel.](../_assets/py-aislamiento.svg)
:::

## En corto

- **Un `.venv` aísla paquetes de Python, y nada más.**
- conda y pixi agregan el intérprete y las librerías del sistema que ellos empaquetan.
- **Docker aísla todo menos el kernel**, y adentro también se usa uv.

La comparación entre `venv` y un contenedor ya apareció en [[en-mi-maquina-si-funciona]]. Aquí se agregan uv y pixi.

## Qué queda fijo con cada uno

::: table {#py-tabla-aislamiento title="Qué aísla cada uno"}

| Qué queda aislado | `.venv` (uv) | conda / pixi | Docker |
|---|---|---|---|
| Paquetes de Python | ✅ | ✅ | ✅ |
| Versión del intérprete | ✅ si la instaló uv | ✅ | ✅ |
| Librerías del sistema (`libc`, CUDA, GDAL) | ❌ | ✅ las que empaqueta | ✅ |
| Programas (`bash`, `grep`) y sistema de archivos | ❌ | ❌ | ✅ |
| Procesos y red | ❌ | ❌ | ✅ |
| Kernel | ❌ | ❌ | ❌ |

:::

- `libc` — la librería de C del sistema; casi todo programa la usa, Python incluido.
- CUDA, GDAL — librerías de C/C++ para GPU de NVIDIA y para mapas; no se instalan con `uv add`.
- Kernel — el núcleo del sistema operativo; un contenedor usa el del host, nunca uno propio.

## Qué se rompe con cada uno

| Usas | Se te rompe cuando… |
|---|---|
| Sólo `.venv` | tu código llama a una librería del sistema que la otra máquina no tiene (`libgdal`, un driver de CUDA) |
| conda / pixi | dependes de un programa del sistema (`grep`, `ffmpeg`) o de una configuración de la máquina |
| Docker | dependes del kernel o del hardware (una GPU que el host no expone) |

## Se combinan

No se elige uno: se apilan. En la [[entregas-ambientes|entrega de esta sección]] construyes una imagen de Docker y, **dentro** de ella, uv crea un `.venv` desde tu `uv.lock` (instala exactamente esas versiones, sin resolver de nuevo). Docker fija el sistema; el lock fija los paquetes.

::: figure {#py-uv-docker title="El ambiente primero, el código al final"}
![Las cinco etapas de un Dockerfile con uv, apiladas en orden: una imagen base que ya trae Python; el binario de uv, copiado de su imagen oficial; los dos archivos que describen el ambiente; crear el ambiente desde el lock, sin dejar que cambie; y al final el programa. La tercera y la cuarta forman una capa en caché que sólo se rehace si cambia el lock; la quinta cambia cada vez que editas el código. Abajo, en rojo: el .venv de tu máquina nunca entra a la imagen.](../_assets/py-uv-docker.svg)
:::

El orden importa por la caché de capas de [[capas-y-cache]]: el ambiente cambia poco y va primero; el código cambia siempre y va al final.

::: problem {#py-aislamiento-libc title="Una librería del sistema"}
Tu código usa un paquete de Python que, por dentro, llama a `libgdal`, una librería del sistema. En tu máquina funciona con `uv run` (corre el script con el Python del `.venv/` del proyecto). En la de tu compañero, con el mismo `uv.lock`, truena al importar. ¿Por qué no bastó el lock, y qué lo arreglaría?
:::

::: hint {of="py-aislamiento-libc"}
Busca `libgdal` en la tabla: ¿en qué fila cae, y qué columnas tienen ✅?
:::

::: answer {of="py-aislamiento-libc"}
- `uv.lock` fija paquetes de Python. `libgdal` es una librería del sistema: está en tu máquina y no en la de él.
- Lo arregla pixi o conda, que empaquetan `libgdal`, o una imagen de Docker que la instale.
:::

Sigue con [[lab-uv]]: el ciclo completo de un proyecto uv.

> [!NOTE]
> **Si sólo recuerdas una cosa:** cada herramienta aísla una capa más; elige la que cubre lo que se te rompe.
