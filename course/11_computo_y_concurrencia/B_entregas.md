---
id: entregas-computo
title: "Las entregas de cómputo y concurrencia"
nav_title: "B. Entregas"
summary: "El tablero de la unidad: la tarea de FastAPI con su branch, su carpeta y su ritual, y el aviso de instalar Antigravity, que no se entrega."
status: ready
estimated_time: 5m
tags: [entrega, pull-request, branch, datacamp, fastapi, antigravity, tablero]
prerequisites: [el-flujo-del-curso]
---

# Las entregas de cómputo y concurrencia

**Anexo B** · el tablero de la unidad

Una entrega por pull request y un aviso sin entrega. Esta página es la versión en tabla de lo que dicen los objetos oficiales: **el contrato manda**.

::: table {#cmp-entregas-resumen title="La tarea y el aviso de la unidad 11"}

| # | Qué | Vence | Vale | Branch | Carpeta |
|---:|---|---|---:|---|---|
| 1 | DataCamp: *Introduction to FastAPI* (≈ 4 h) | 2026-11-03 | 20 | `tarea-11-datacamp-fastapi` | `fastapi/` |
| 2 | Instalar Antigravity y comprobar que abre | 2026-11-03 | 0 | no se entrega | no se entrega |

:::

Se entrega tarde con un punto menos por día, contando el día en que entregas.

Los comandos son para la terminal de **Linux, WSL2 o macOS**, la misma de las unidades anteriores. `{tu_fork_de_la_clase}` es la carpeta donde clonaste tu fork: escribe la tuya, sin las llaves.

## 1 · DataCamp: Introduction to FastAPI

| | |
|---|---|
| **Vence** | 2026-11-03 |
| **Vale** | 20 puntos |
| **Branch** | `tarea-11-datacamp-fastapi` |
| **Carpeta** | `estudiantes/<tu-login>/fastapi/` |

El curso son tres capítulos: lo básico de FastAPI, parámetros y `async`, y una API CRUD en JSON con pruebas. Entras con la cuenta del grupo de DataCamp del ITAM.

**Entregas dos archivos**

- `certificaciones.md` con sus tres secciones llenas: tus usuarios de GitHub y de DataCamp (nada de nombre completo ni correo: el repo es público); la fecha en que lo terminaste, **en formato `AAAA-MM-DD`**, y la **URL del Statement of Accomplishment**; y una cosa concreta que aprendiste.
- `introduccion-fastapi.png`: el curso terminado, con **tu nombre visible**: la página del curso al 100 % o tu Statement of Accomplishment. Con ese nombre exacto, porque la plantilla ya lo enlaza. Si te sale en `jpg`, corrige el enlace dentro del archivo.

**El ritual**

```bash
cd {tu_fork_de_la_clase}
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-11-datacamp-fastapi
mkdir -p estudiantes/$GHUSER/fastapi
cp -r codigo/fastapi/. estudiantes/$GHUSER/fastapi/
#   ... llenas certificaciones.md y guardas la captura ...
git add estudiantes/$GHUSER/fastapi
git commit -m "unidad 11: DataCamp Introduction to FastAPI"
git push -u origin tarea-11-datacamp-fastapi
```

**Qué hace cada pieza:**

- `cd {tu_fork_de_la_clase}` — entras a tu fork. Escribe tu ruta, sin las llaves.
- `git switch main` — te cambias a `main`: de ahí nace cada branch de entrega.
- `&&` — corre el comando siguiente sólo si el anterior salió bien.
- `git fetch upstream` — bajas lo nuevo del repo del curso (`upstream`), sin tocar tus archivos todavía.
- `git merge upstream/main` — mezclas eso en tu `main`. Así te llega `codigo/fastapi/`.
- `git switch -c tarea-11-datacamp-fastapi` — `-c` crea la branch y te cambia a ella. El nombre exacto es el que busca la revisión.
- `mkdir -p estudiantes/$GHUSER/fastapi` — creas tu carpeta. `-p` crea también las intermedias y no truena si ya existe. `$GHUSER` es tu login de GitHub: `echo $GHUSER` lo muestra.
- `cp -r codigo/fastapi/. estudiantes/$GHUSER/fastapi/` — copias la plantilla. `-r` incluye subcarpetas; el `/.` final copia el *contenido*: sin él te queda `fastapi/fastapi/`.
- `#   ...` — una línea que empieza con `#` es comentario: la shell la ignora. Ahí va tu trabajo.
- `git add estudiantes/$GHUSER/fastapi` — eliges para el commit sólo tu carpeta, nada más del repo.
- `git commit -m "…"` — guardas esos cambios en tu historial; `-m` da el mensaje en la misma línea.
- `git push -u origin tarea-11-datacamp-fastapi` — subes la branch a tu fork (`origin`). `-u` la deja enlazada: el siguiente push basta con `git push`.

**No se entrega** la captura de un ejercicio suelto ni la del panel de inicio: la captura es la página del curso terminado o tu Statement of Accomplishment, con tu nombre. Tu carpeta `clase-11-computo/`, la de las demostraciones, **no** viaja en este pull request: va en otra branch y nunca se vuelve pull request.

**Debes poder explicar, sin ayuda:** qué es una ruta y qué hace el decorador que la declara; qué distingue un parámetro de ruta de uno de consulta; qué hace FastAPI cuando el cuerpo de la petición no cumple el modelo; qué cambia entre `def` y `async def`. La IA vale para estudiar; la explicación es tuya.

**Acabaste cuando** el pull request está abierto y su revisión en verde. Si no terminaste el curso, sube lo que sí hiciste y dilo en el archivo.

## 2 · Instalar Antigravity y comprobar que abre

| | |
|---|---|
| **Vence** | 2026-11-03 |
| **Vale** | 0 puntos |
| **Se entrega** | nada: sin pull request, sin archivo, sin captura |

Lo vamos a usar en la clase del 3 de noviembre y en el aula no hay internet: lo que no esté instalado y probado antes, no se puede instalar ese día.

1. Descárgalo de [la página de descarga](https://antigravity.google/download), elige la versión de tu sistema operativo e instálalo.
2. Ábrelo. La primera vez pide iniciar sesión con una cuenta de Google: usa la tuya.
3. Abre dentro de él la carpeta de tu fork del curso.
4. Escríbele un mensaje corto al agente del programa, por ejemplo que te diga qué archivos hay en la carpeta.

**Acabaste cuando** el agente contesta. Si no abre, no te deja iniciar sesión o no contesta, anota qué pasó y cómo lo reproduces, y llévalo a la clase.
