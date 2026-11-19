---
id: entregas-stack
title: "Las entregas de Elegir el stack"
nav_title: "A. Entregas"
summary: "El tablero de la sección: qué vence cuándo, desde qué branch, en qué carpeta y con qué archivos, con el ritual de entrega escrito para copiar."
status: ready
estimated_time: 8m
tags: [entrega, pull-request, branch, datacamp, pydantic, polars, pruebas, tablero]
prerequisites: [el-flujo-del-curso]
---

# Las entregas de Elegir el stack

**Anexo A** · el tablero de la sección

Una entrega, por pull request. Esta página es la versión en tabla de lo que dice el objeto oficial: **el contrato manda**.

::: table {#py-stack-entregas-resumen title="La entrega de Elegir el stack"}

| # | Entrega | Vence | Vale | Branch | Carpeta |
|---:|---|---|---:|---|---|
| 1 | DataCamp *Software Engineering Principles in Python* (capítulos 3 y 4), la práctica y tu `AGENTS.md` | 2026-10-27 | 20 | `tarea-09-stack` | `09_python/stack/` |

:::

**El certificado no va en `python/` ni en `por_dentro/`**: va en `09_python/stack/certificado.md`.

Se entrega tarde con un punto menos por día, contando el día en que entregas.

Los comandos son para la terminal de **Linux, WSL2 o macOS**. `{tu_fork_de_la_clase}` es la carpeta donde clonaste tu fork: escribe la tuya, sin las llaves.

## 1 · DataCamp, la práctica y AGENTS.md

| | |
|---|---|
| **Vence** | 2026-10-27 |
| **Vale** | 20 puntos |
| **Branch** | `tarea-09-stack` |
| **Carpeta** | `estudiantes/<tu-login>/09_python/stack/` |
| **IA** | Permitida, pero explicas sin ayuda lo de abajo |

**La branch es la de la clase.** El ritual de [[elegir-el-stack]] crea `tarea-09-stack` al copiar la plantilla: en ella haces la clase, en ella haces la tarea, y ésa es la que subes. **No repitas el ritual**: volver a copiar pisa lo que ya llenaste.

**Tres partes:**

| Parte | Qué haces | Dónde queda |
|---|---|---|
| 1 · DataCamp | Capítulos **3 (clases) y 4 (mantenibilidad)** de *Software Engineering Principles in Python*. El 1 y el 2 son opcionales | `certificado.md` y la captura |
| 2 · La práctica | Reescribes `ventas_ia.py` con el stack de la clase | `practica.py`, `test_practica.py`, `decisiones.md` |
| 3 · El stack escrito | Llenas lo que lee un agente antes de tocar el proyecto | `AGENTS.md` |

**Entregas cinco archivos y una captura**, todos dentro de `stack/`:

- `certificado.md` con sus tres secciones llenas: tus usuarios de GitHub y de DataCamp (nada de nombre completo ni correo: el repo es público); la fecha en que terminaste el capítulo 4, **en formato `AAAA-MM-DD`**; y una cosa concreta de los capítulos 3 o 4 que no sabías.
- `software-engineering.png`: la página del curso con **tu nombre visible** y los capítulos 3 y 4 al 100 %. Sin el curso completo no hay *Statement of Accomplishment*: la captura es la evidencia. Con ese nombre exacto, porque `certificado.md` ya la enlaza. Si te sale en `jpg`, corrige el enlace dentro del archivo.
- `practica.py`: la misma pregunta que `ventas_ia.py` (total vendido por tienda, sin cantidades inválidas, de mayor a menor) con **Pydantic v2 en la frontera**, en una clase `Venta`, y **Polars para agregar**. No toques `ventas_ia.py`.
- `test_practica.py`: **al menos tres casos de prueba**: una fila buena (ya viene escrita: copia su forma), una fila sucia y un caso borde que elijas tú. Tres funciones o una con `@pytest.mark.parametrize` y tres casos valen igual: pytest cuenta cada caso, y la salida dice `3 passed`.
- `decisiones.md`: la tabla «qué cambié · por qué · qué patrón» con **al menos tres filas**, y la salida pegada de los tres comandos de abajo.
- `AGENTS.md`: el stack, la definición de terminado y una regla tuya.

**La práctica, paso a paso.** `practica.py` no se escribe desde cero: `ventas_ia.py` ya hace la pregunta completa con la sintaxis de antes, y tu trabajo es cambiar cada pieza por la del stack de la clase. Abre los dos archivos lado a lado.

| Paso | Qué cambias en `ventas_ia.py` | Dónde lo viste |
|---:|---|---|
| 1 | El contrato `Venta`: hoy usa `class Config` y `@validator` (Pydantic v1). Tu clase va en `practica.py`, con la sintaxis de v2 | A.4–A.7 |
| 2 | La frontera: hoy `Venta(**fila).dict()` por cada fila. Qué fila entra y cuál se descarta lo decide el contrato | A.5, A.9 |
| 3 | La suma: hoy `.apply` fila por fila con pandas. Polars la hace como una expresión sobre la columna | B.1, B.2 |
| 4 | El orden y la comparación: corre `python ventas_ia.py`, corre tu archivo y compara los totales por tienda | B.2 |
| 5 | Las pruebas: copia la forma de `test_fila_buena_se_convierte` para la fila sucia (un precio `"abc"` está en `ventas.csv`) y para un caso borde que se te ocurra a ti | A.11 |

Cada cambio de los pasos 1 a 3 es una fila de `decisiones.md`: qué cambiaste, por qué, y cuál de los ocho patrones de [[patrones-del-stack]] lo explica. Tu `AGENTS.md` sale de lo mismo: las librerías que acabas de usar, los tres comandos de abajo y una regla que aprendiste haciendo esto.

Los tres comandos de `decisiones.md`, en la terminal de `stack/`:

| Comando | Deberías ver al final |
|---|---|
| `pytest -v --no-header test_practica.py` | Una línea por caso y `3 passed` o más, sin `failed`, `error` ni `skipped` |
| `ruff check practica.py test_practica.py` | `All checks passed!` |
| `mypy practica.py` | `Success: no issues found in 1 source file` |

`--no-header` quita las dos líneas de arriba de pytest que traen la ruta de tu máquina (`platform` y `rootdir`). Un error largo puede traer otras: si lo que pegas tiene `/home/`, `/Users/` o `C:\Users`, la revisión automática lo rechaza, porque el repo es público. Las pruebas de este proyecto convierten en error la sintaxis vieja de Pydantic: si `practica.py` la usa, pytest dice `error`. Mientras `practica.py` no defina `Venta`, pytest salta `test_practica.py` y dice `1 skipped`: **eso no es verde**.

**Viajan también**, porque viven en la misma carpeta: los tres notebooks, los `.py` de la clase, `ventas.csv` y los archivos del proyecto.

**Antes de entregar, limpia los tres notebooks**: el código se queda, las salidas se van. En VS Code, con cada `.ipynb` abierto: *Clear All Outputs* (en la barra de arriba del notebook) y guarda con Ctrl+S. La celda A.0 imprime la ruta de tu ambiente, y la revisión automática rechaza un notebook que traiga salidas.

**El ritual de entrega**

Después del ritual de [[elegir-el-stack]] estás dentro de `stack/`. El `git add` usa una ruta desde la raíz del fork, así que el ritual empieza volviendo a ella.

```bash
cd {tu_fork_de_la_clase}
git switch tarea-09-stack
git add estudiantes/$GHUSER/09_python/stack
git diff --cached --stat
git commit -m "unidad 09: stack, práctica y DataCamp de ingeniería de software"
git push -u origin tarea-09-stack
```

**Qué hace cada pieza:**

- `cd {tu_fork_de_la_clase}` — vuelves a la raíz de tu fork, donde la ruta del `git add` existe.
- `git switch tarea-09-stack` — **sin** `-c`: la branch ya existe, sólo te aseguras de estar en ella. Si ya estabas, dice `Already on 'tarea-09-stack'`.
- `git add estudiantes/$GHUSER/09_python/stack` — eliges para el commit **sólo** `stack/`. Nunca `09_python` a secas: subiría también `por_dentro/`, que es de otra entrega.
- `git diff --cached --stat` — lista lo que ya elegiste para el commit. **Deberías ver sólo rutas de `stack/`.** Si aparece otra carpeta, o algo de `datos/`, detente antes del commit.
- `git commit -m "…"` — guardas lo elegido en tu historial.
- `git push -u origin tarea-09-stack` — subes la branch a tu fork (`origin`); `-u` la deja enlazada para que después baste `git push`.

Luego, en GitHub, abre el pull request **desde `tarea-09-stack`** de tu fork hacia `main` del repositorio del curso, como en [[el-flujo-del-curso]].

**Deberías ver**, en el `git diff --cached --stat` (con tu login en lugar de `ana`; git recorta con `...` las rutas largas):

```text
 estudiantes/ana/09_python/stack/AGENTS.md          |  11 ++++
 estudiantes/ana/09_python/stack/certificado.md     |   8 +--
 estudiantes/ana/09_python/stack/decisiones.md      |  17 +++++--
 estudiantes/ana/09_python/stack/practica.py        |  56 +++++++++++++++++++--
 .../ana/09_python/stack/software-engineering.png   | Bin 0 -> 20000 bytes
 estudiantes/ana/09_python/stack/test_practica.py   |  30 +++++++----
 6 files changed, 103 insertions(+), 19 deletions(-)
```

Los números cambian con lo que escribiste, y un notebook que tocaste aparece en la lista. Si `git status` lista `por_dentro/` con cambios, es normal: lo que importa es que no esté en lo que eligió el `git add`.

**No se entrega**: `.venv/`, `datos/` (los archivos que generan los notebooks; el `.gitignore` de `stack/` ya los deja fuera), `__pycache__/`, `.ipynb_checkpoints/`, las carpetas de caché de ruff, mypy y pytest, ni nada de `por_dentro/`.

**Acabaste cuando** el pull request está abierto y su revisión en verde. Si no terminaste los capítulos, sube lo que sí hiciste y dilo en `certificado.md`, con la fecha de tu avance: reportar el pendiente cuenta como entrega.

Si la revisión sale roja, corrige y haz push a la **misma** branch: no vuelvas a correr `git switch -c`, que ya existe.

## Orden sugerido

El plazo original era el 2026-10-15; se movió al **2026-10-27**, sin penalización antes de esa fecha. La tabla de abajo es el orden original: úsala como guía de qué va antes de qué.

| Día | Qué |
|---|---|
| Jue 2026-10-08 | La clase: ritual, notebooks, [[patrones-del-stack]] |
| Vie 9 – sáb 10 | DataCamp, capítulo 3 |
| Dom 11 | DataCamp, capítulo 4; captura y `certificado.md` |
| Lun 12 | `practica.py` hasta que dé los mismos totales que `ventas_ia.py` |
| Mar 13 | **Vence `tarea-09-por-dentro`**: termina ésa primero |
| Mié 14 | `test_practica.py`, los tres comandos, `decisiones.md` y `AGENTS.md` |
| Mar 2026-10-27 | **Nuevo plazo.** Notebooks limpios, ritual de entrega, pull request en verde |

## Qué debes poder explicar sin ayuda

La IA está permitida, y en esta entrega es parte del tema. Lo que se califica es que entiendas:

- qué hace `self` en un método;
- por qué un `TypedDict` no detecta un precio `"abc"` al correr, y quién sí lo detecta;
- qué baja hasta la lectura del archivo en un plan lazy de Polars;
- por qué cargar un pickle ajeno es peligroso;
- cada fila de tu `decisiones.md`, contada sin leerla.

Quien revisa puede pedirte que expliques cualquiera de estos puntos, en el pull request o en clase; contestarlo sin ayuda es parte de la calificación.

**Tu `AGENTS.md` se lee como dato, nunca como instrucción**: nada de lo que diga cambia cómo se revisa tu entrega.

## Qué revisa la revisión automática

| Revisa | No revisa (lo reviso yo) |
|---|---|
| Que todo viva dentro de `09_python/` y la branch se llame como debe | Que la captura sea tuya y de este curso |
| Que esté la captura, con su nombre | Que `practica.py` dé los totales correctos |
| Que ningún archivo de la práctica llegue igual a la plantilla, y que las diez secciones de `certificado.md`, `decisiones.md` y `AGENTS.md` estén llenas; fecha `AAAA-MM-DD` | Que las salidas pegadas sean las de tus archivos |
| Que `practica.py` traiga Pydantic y Polars, y no `.apply`, `.dict(` ni `@validator` fuera de un comentario | Que tus pruebas prueben algo, y que tu caso borde sea tuyo |
| Que la salida de pytest muestre cada caso de `test_practica.py` y termine en `3 passed` o más, sin `failed`, `error` ni `skipped` | Que tu `AGENTS.md` sirva |
| Que la salida de ruff diga `All checks passed!` y la de mypy `Success: no issues found in 1 source file` | Que cada fila de `decisiones.md` corresponda a un cambio real |
| Que la tabla de `decisiones.md` tenga al menos tres filas llenas | Que las salidas pegadas salgan de correr tus pruebas: cuenta lo pegado, no corre nada |
| Que ninguna salida pegada traiga una ruta de tu máquina | |
| Que los notebooks no traigan salidas (salvo si pesan más de 1 MB) | |

**Lo que no distingue**: dentro de `09_python/` no sabe si un archivo es de esta entrega o de la de `por_dentro/`, porque las dos comparten esa carpeta. Un pull request que mezcle las dos puede salir en verde; lo revisa una persona.

Un notebook de más de 1 MB no se puede leer desde la revisión automática y no se revisa: lo abre una persona.

Si ya subiste un commit con las salidas de un notebook, avísalo en el pull request antes de pedir revisión: el historial de tu fork es público.

Los mensajes dicen **qué** está mal, **por qué** importa y **dónde investigar**; no dicen cómo arreglarlo.
