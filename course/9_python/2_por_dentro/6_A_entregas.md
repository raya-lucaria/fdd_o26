---
id: entregas-por-dentro
title: "Las entregas de Python por dentro"
nav_title: "A. Entregas"
summary: "El tablero de la sección: qué vence cuándo, desde qué branch, en qué carpeta y con qué archivos, con el ritual de entrega escrito para copiar."
status: ready
estimated_time: 8m
tags: [entrega, pull-request, branch, datacamp, revision-de-codigo, prompt, tablero]
prerequisites: [el-flujo-del-curso]
---

# Las entregas de Python por dentro

**Anexo A** · el tablero de la sección

Una entrega, por pull request. Esta página es la versión en tabla de lo que dice el objeto oficial: **el contrato manda**.

::: table {#py-dentro-entregas-resumen title="La entrega de Python por dentro"}

| # | Entrega | Vence | Vale | Branch | Carpeta |
|---:|---|---|---:|---|---|
| 1 | DataCamp *Intermediate Python for Developers*, revisión de `revisa_esto.py` y tu prompt | 2026-10-13 | 20 | `tarea-09-por-dentro` | `09_python/por_dentro/` |

:::

**Esta vez el certificado no va en `python/`**: va en `09_python/por_dentro/certificado.md`. `python/` es la carpeta de la entrega de *Introduction to Python*, y ésa ya cerró.

Se entrega tarde con un punto menos por día, contando el día en que entregas.

Los comandos son para la terminal de **Linux, WSL2 o macOS**. `{tu_fork_de_la_clase}` es la carpeta donde clonaste tu fork: escribe la tuya, sin las llaves.

## 1 · DataCamp intermedio y revisión de código de IA

| | |
|---|---|
| **Vence** | 2026-10-13 |
| **Vale** | 20 puntos |
| **Branch** | `tarea-09-por-dentro` |
| **Carpeta** | `estudiantes/<tu-login>/09_python/por_dentro/` |
| **IA** | Permitida, pero explicas sin ayuda lo de abajo |

**La branch es la de la clase.** El ritual de [[python-por-dentro]] crea `tarea-09-por-dentro` al copiar la plantilla: en ella haces la clase, en ella haces la tarea, y ésa es la que subes. **No repitas el ritual**: volver a copiar pisa lo que ya llenaste.

**La entrega tiene tres partes: el curso, el ejercicio y el notebook terminado.**

**Entregas cuatro archivos y una captura**, todos dentro de `por_dentro/`:

- `certificado.md` con sus tres secciones llenas: tus usuarios de GitHub y de DataCamp (nada de nombre completo ni correo: el repo es público); la fecha en que terminaste, **en formato `AAAA-MM-DD`**, y la **URL del Statement of Accomplishment**; y una cosa concreta que aprendiste.
- `intermedio-python-developers.png`: el curso terminado, con **tu nombre visible**: la página del curso al 100 % o tu Statement of Accomplishment. Con ese nombre exacto, porque `certificado.md` ya lo enlaza. Si te sale en `jpg`, corrige el enlace dentro del archivo.
- `por_dentro.ipynb`, **corrido de principio a fin**: ya trae la explicación y el código de cada celda; lo corres en orden, celda por celda, y puedes agregar tus notas o tus pruebas. Sin salidas (abajo).
- `revision.md`: los cinco errores de `revisa_esto.py`, uno por sección (`## Error 1` a `## Error 5`). Cada uno con sus cuatro rótulos llenos: `Síntoma:`, `Línea:`, `Por qué pasa:` y `Qué le pedirías a la IA:`.
- `prompt.md`: en `## Mi prompt`, el prompt que le darías a una IA para la tarea de `## La tarea`. Como mínimo: versión de Python y cómo se corre, qué entra y qué sale, qué hacer con los casos borde y cómo vas a verificar.

Los síntomas salen de correr `revisa_esto.py` (la celda 0.1 del notebook, o `uv run revisa_esto.py` en `por_dentro/`); la tabla de síntomas está en [[python-por-dentro]]. **La línea y la causa no las da ninguna página**: ésa es la tarea.

**Viajan también**, porque viven en la misma carpeta: los `.py` de los labs, `ventas.csv` y los archivos del proyecto.

**Antes de entregar, limpia el notebook**: el código se queda, las salidas se van. En VS Code, con `por_dentro.ipynb` abierto: *Clear All Outputs* (en la barra de arriba del notebook) y guarda con Ctrl+S. Las salidas guardan rutas de tu máquina, y la revisión automática rechaza un notebook que las traiga.

**El ritual de entrega**

Después del ritual de [[python-por-dentro]] estás dentro de `por_dentro/`. El `git add` usa una ruta desde la raíz del fork, así que el ritual empieza volviendo a ella.

```bash
cd {tu_fork_de_la_clase}
git switch tarea-09-por-dentro
git add estudiantes/$GHUSER/09_python/por_dentro
git diff --cached --stat
git commit -m "unidad 09: notebook, DataCamp intermedio, revisión y prompt"
git push -u origin tarea-09-por-dentro
```

**Qué hace cada pieza:**

- `cd {tu_fork_de_la_clase}` — vuelves a la raíz de tu fork, donde la ruta del `git add` existe. Escribe tu ruta, sin las llaves.
- `git switch tarea-09-por-dentro` — **sin** `-c`: la branch ya existe, sólo te aseguras de estar en ella. Si ya estabas, dice `Already on 'tarea-09-por-dentro'`.
- `git add estudiantes/$GHUSER/09_python/por_dentro` — eliges para el commit **sólo** `por_dentro/`. Nunca `09_python` a secas: subiría también `uv_docker/` y `ambientes/`, que son de otra entrega.
- `git diff --cached --stat` — lista lo que ya elegiste para el commit, archivo por archivo. **Deberías ver sólo rutas de `por_dentro/`.** Si aparece otra carpeta, detente antes del commit.
- `git commit -m "…"` — guardas lo elegido en tu historial; `-m` da el mensaje en la misma línea.
- `git push -u origin tarea-09-por-dentro` — subes la branch a tu fork (`origin`). `-u` la deja enlazada: el siguiente push basta con `git push`.

**Deberías ver**, en el `git diff --cached --stat` (con tu login en lugar de `ana`; git recorta con `...` las rutas largas):

```text
 estudiantes/ana/09_python/por_dentro/certificado.md     |   1 +
 .../por_dentro/intermedio-python-developers.png         | Bin 0 -> 60000 bytes
 estudiantes/ana/09_python/por_dentro/prompt.md          |   2 ++
 estudiantes/ana/09_python/por_dentro/revision.md        |   3 +++
 4 files changed, 6 insertions(+)
```

Los números cambian con lo que escribiste, y `por_dentro.ipynb`, si lo tocaste, aparece en la lista. Si `git status` lista `uv_docker/` como *Untracked*, es normal: lo que importa es que no esté en lo que eligió el `git add`.

**No se entrega**: `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`, nada de `uv_docker/` ni de `ambientes/`, ni el archivo de gasolina, que no existe: sólo escribes el prompt para él.

**Acabaste cuando** el pull request está abierto y su revisión en verde. Si no terminaste el curso, sube lo que sí hiciste y dilo en `certificado.md`: pon la fecha de tu avance y la URL del curso; la revisión sólo avisa, y reportar el pendiente cuenta como entrega.

Si la revisión sale roja, corrige y haz push a la **misma** branch: no vuelvas a correr `git switch -c`, que ya existe.

## Qué debes poder explicar sin ayuda

La IA está permitida, y en esta entrega es parte del tema. Lo que se califica es que entiendas:

- por qué `b = a` no copia una lista;
- por qué cuatro hilos no aceleran un cálculo con GIL, y qué sí lo acelera;
- qué pasa con un argumento por defecto `log=[]` entre una llamada y otra;
- por qué `0.1 + 0.2 != 0.3`, y qué usar para dinero;
- qué esconde un `except` que no hace nada;
- qué hacen `*args` y `**kwargs` (del curso de DataCamp);
- cada error de tu `revision.md`, contado sin leerlo.

Quien revisa puede pedirte que expliques cualquiera de estos puntos, en el pull request o en clase; contestarlo sin ayuda es parte de la calificación.

## Qué revisa la revisión automática

| Revisa | No revisa (lo reviso yo) |
|---|---|
| Que todo viva dentro de `09_python/` y la branch se llame como debe | Que la captura sea tuya y de este curso |
| Que esté la captura, con su nombre | Que la URL abra tu certificado |
| Que las nueve secciones de los tres archivos estén llenas; fecha `AAAA-MM-DD`; URL presente | Que la línea y la causa de cada error sean las correctas |
| Que el notebook venga y no traiga salidas (salvo si pesa más de 1 MB); que cada `Línea:` sea un número | Que tu prompt sirva como especificación |

**Lo que no distingue**: dentro de `09_python/` no sabe si un archivo es de esta entrega o de la de uv y Docker, porque las dos comparten esa carpeta. Un pull request que mezcle `por_dentro/` con `uv_docker/` puede salir en verde; lo revisa una persona.

Un notebook de más de 1 MB no se puede leer desde la revisión automática y no se revisa: lo abre una persona.

Si ya subiste un commit con las salidas del notebook, avísalo en el pull request antes de pedir revisión: el historial de tu fork es público.

Los mensajes dicen **qué** está mal, **por qué** importa y **dónde investigar**; no dicen cómo arreglarlo.
