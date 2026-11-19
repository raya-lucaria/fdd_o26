---
id: apis-y-http
title: "APIs y HTTP"
nav_title: "1. APIs y HTTP"
summary: "Qué es una API, qué viaja por la red cuando la llamas, qué prometen los métodos y los códigos de estado, y en qué se distinguen HTTP, REST y CRUD. Con un servidor local que imprime cada petición que recibe."
status: ready
tags: [apis, http, rest, crud, requests, notebook]
---

# APIs y HTTP

**Sección 1** · 4 páginas · unos 90 min · sesión del martes 20 de octubre, 19:00–20:30

Meta: entender qué pasa entre tu código y otra máquina cuando le pides datos, con las palabras exactas que usa la industria.

## En corto

- **Una API es un contrato entre dos programas.** Esta sección estudia las APIs web: el otro programa vive en otra máquina y el contrato se cumple con mensajes HTTP. No toda API cruza la red, y no todo lo que cruza la red es HTTP.
- **Un mensaje HTTP/1.1 tiene un formato fijo**: una línea inicial y headers en texto, una línea en blanco y un body de bytes. Lo vas a escribir a mano.
- **Toda la clase corre contra un servidor que tú arrancas**, y que imprime en su terminal cada petición que recibe: ves los dos lados de la conversación.

## Las páginas

| # | Página | Qué contesta | Min |
|---:|---|---|---:|
| 1 | [[que-es-una-api]] | Qué es una API y qué cambia cuando la llamada cruza la red | 10 |
| 2 | [[el-mensaje-http]] | Qué viaja exactamente: línea inicial, headers, body, URL | 25 |
| 3 | [[metodos-y-status]] | Qué promete cada método y cada código de estado, y qué pasa si no se cumple | 28 |
| 4 | [[http-rest-y-crud]] | Por qué HTTP, REST y CRUD son tres cosas distintas, y cuándo usar REST | 17 |

## Antes de clase

Necesitas lo de la unidad de Python: **uv** instalado, VS Code con las extensiones **Python** y **Jupyter**, y tu fork clonado con `upstream` configurado ([[el-ritual-del-curso]]).

**Esta sección no tiene entrega.** Trabajas en una branch propia, `clase-10-apis`, para no meter commits en tu `main`: tu `main` sólo avanza con el del curso.

**Haz 1 · actualiza main y crea la branch de la clase:**

```bash
cd {tu_fork_de_la_clase}
git switch main && git fetch upstream && git merge --ff-only upstream/main
git switch -c clase-10-apis
```

**Qué hace cada pieza:**

- `cd {tu_fork_de_la_clase}` — entras a tu fork. Escribe tu carpeta, sin las llaves.
- `git switch main && git fetch upstream && git merge --ff-only upstream/main` — el ritual de siempre: trae lo nuevo del curso a tu `main`.
- `git switch -c clase-10-apis` — crea la branch de esta clase y te cambia a ella.

**Deberías ver** `Fast-forward` (o `Already up to date.`) y al final `Switched to a new branch 'clase-10-apis'`.

**Haz 2 · copia la plantilla y crea el ambiente:**

```bash
[ -n "$GHUSER" ] && mkdir -p estudiantes/$GHUSER/10_apis \
  && cp -r codigo/10_apis/. estudiantes/$GHUSER/10_apis/ \
  && cd estudiantes/$GHUSER/10_apis && uv sync
```

**Qué hace cada pieza:**

- `[ -n "$GHUSER" ]` — comprueba que `$GHUSER` (tu usuario de GitHub) no está vacío; si lo está, no se copia nada fuera de tu carpeta.
- `mkdir -p estudiantes/$GHUSER/10_apis` — crea tu carpeta de la unidad.
- `cp -r codigo/10_apis/. estudiantes/$GHUSER/10_apis/` — copia el **contenido** de la plantilla (`/.`) dentro de tu carpeta.
- `uv sync` — crea `.venv/` con Python y `requests`, la librería con la que el notebook hace peticiones.

**Deberías ver** al final una línea `Installed … packages`. En tu carpeta quedan:

| Archivo | Qué es |
|---|---|
| `servidor.py` | Un servidor de ventas que corre en tu máquina. Imprime cada petición que recibe |
| `cable.py` | Dos ayudas: `a_mano()` manda HTTP escrito a mano y `ver()` imprime lo que viajó |
| `apis.ipynb` | El notebook de la clase: las mismas celdas de estas páginas, con su explicación |

**Haz 3 · arranca el servidor** en una terminal aparte (en VS Code: *Terminal → Split Terminal*), dentro de tu carpeta `10_apis`:

```bash
uv run python servidor.py
```

**Qué hace cada pieza:**

- `uv run python servidor.py` — corre el servidor con el Python del ambiente. Se queda escuchando en el puerto 8026 hasta que lo apagues con Ctrl+C.

**Deberías ver:**

```text
Servidor de ventas en http://127.0.0.1:8026  (Ctrl+C para apagarlo)
```

- **Deja esta terminal visible toda la clase.** Cada vez que el notebook haga una petición, aquí aparece completa.

**Haz 4 · abre el notebook:** abre `apis.ipynb` en VS Code y elige como kernel (arriba a la derecha) el `.venv` de `10_apis`. El **kernel** es el proceso de Python que corre las celdas del notebook.

**Sin internet.** Todo corre contra tu servidor local, salvo cuatro celdas que salen a internet: 2.2 (example.com), 3.7 (jsonplaceholder), 4.1 (la mitad de PokeAPI) y 4.3 (GitHub, sólo el profesor). Si la red falla en clase, su «Deberías ver» es la salida real, obtenida el 20 de octubre de 2026: léela desde la página y sigue.

## Arranque del notebook

**Haz (celda 0.1):** importa lo de la clase y comprueba que el servidor contesta.

```python
import re
import time

import requests
from cable import TOKEN, URL, a_mano, total, ver

r = requests.get(f"{URL}/ventas", timeout=5)
print(r.status_code, "· ventas guardadas:", total())
```

**Qué hace cada línea:**

- `import requests` — la librería que manda peticiones HTTP desde Python.
- `from cable import …` — trae de `cable.py` la dirección del servidor (`URL`), el token para escribir (`TOKEN`) y las ayudas `a_mano`, `ver` y `total`.
- `requests.get(f"{URL}/ventas", timeout=5)` — le pide al servidor la lista de ventas; si en 5 segundos no contesta, se rinde.
- `total()` — cuenta las ventas que el servidor tiene guardadas.

**Deberías ver:**

```text
200 · ventas guardadas: 4
```

- Si sale `ConnectionError` (*connection refused*), el servidor no está corriendo: vuelve al Haz 3.
- En la terminal del servidor aparecieron dos peticiones: la tuya y la de `total()`.

Sigue con [[que-es-una-api]].
