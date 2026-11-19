---
id: entregas-ambientes
title: "Las entregas de ambientes"
nav_title: "B. Entregas"
summary: "El tablero de la sección: las dos entregas, qué vence cuándo, desde qué branch, en qué carpeta y con qué archivos, con el ritual escrito para copiar."
status: ready
estimated_time: 8m
tags: [entrega, pull-request, branch, datacamp, docker-hub, uv, tablero]
prerequisites: [el-flujo-del-curso]
---

# Las entregas de ambientes

**Anexo B** · el tablero de la sección

Dos entregas, las dos por pull request. Esta página es la versión en tabla de lo que dice cada objeto oficial: **el contrato manda**.

::: table {#py-entregas-resumen title="Las dos entregas de ambientes"}

| # | Entrega | Vence | Vale | Branch | Carpeta |
|---:|---|---|---:|---|---|
| 1 | DataCamp: *Introduction to Python for Developers* | 2026-10-06 | 20 | `tarea-09-datacamp-python` | `python/` |
| 2 | Tu ambiente uv dentro de Docker | 2026-10-06 | 10 | `tarea-09-uv-docker` | `09_python/uv_docker/` |

:::

**Dos carpetas, dos branches, dos pull requests**, las dos branches nacidas de `main` y ninguna de la otra. El error que más se va a repetir: la de DataCamp es `python/`, **sin** número; la de Docker es `09_python/`, **con** el cero.

Se entrega tarde con un punto menos por día, contando el día en que entregas.

Los comandos son para la terminal de **Linux, WSL2 o macOS**, la misma donde instalaste Docker en la unidad 8. `{tu_fork_de_la_clase}` es la carpeta donde clonaste tu fork: escribe la tuya, sin las llaves.

## 1 · DataCamp: Introduction to Python for Developers

| | |
|---|---|
| **Vence** | 2026-10-06 |
| **Vale** | 20 puntos |
| **Branch** | `tarea-09-datacamp-python` |
| **Carpeta** | `estudiantes/<tu-login>/python/` |

**Entregas dos archivos**

- `certificaciones.md` con sus tres secciones llenas: tus usuarios de GitHub y de DataCamp (nada de nombre completo ni correo: el repo es público); la fecha en que lo terminaste, **en formato `AAAA-MM-DD`**, y la **URL del Statement of Accomplishment**; y una cosa concreta que aprendiste.
- `introduccion-python-developers.png`: el curso terminado, con **tu nombre visible**: la página del curso al 100 % o tu Statement of Accomplishment. Con ese nombre exacto, porque la plantilla ya lo enlaza. Si te sale en `jpg`, corrige el enlace dentro del archivo.

**El ritual**

```bash
cd {tu_fork_de_la_clase}
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-09-datacamp-python
mkdir -p estudiantes/$GHUSER/python
cp -r codigo/python/. estudiantes/$GHUSER/python/
#   ... llenas certificaciones.md y guardas la captura ...
git add estudiantes/$GHUSER/python
git commit -m "unidad 09: DataCamp Introduction to Python for Developers"
git push -u origin tarea-09-datacamp-python
```

**Qué hace cada pieza:**

- `cd {tu_fork_de_la_clase}` — entras a tu fork. Escribe tu ruta, sin las llaves.
- `git switch main` — te cambias a `main`: de ahí nace cada branch de entrega.
- `&&` — corre el comando siguiente sólo si el anterior salió bien.
- `git fetch upstream` — bajas lo nuevo del repo del curso (`upstream`), sin tocar tus archivos todavía.
- `git merge upstream/main` — mezclas eso en tu `main`. Así te llega `codigo/python/`.
- `git switch -c tarea-09-datacamp-python` — `-c` crea la branch y te cambia a ella. El nombre exacto es el que busca la revisión.
- `mkdir -p estudiantes/$GHUSER/python` — creas tu carpeta. `-p` crea también las intermedias y no truena si ya existe. `$GHUSER` es tu login de GitHub: `echo $GHUSER` lo muestra.
- `cp -r codigo/python/. estudiantes/$GHUSER/python/` — copias la plantilla. `-r` incluye subcarpetas; el `/.` final copia el *contenido*: sin él te queda `python/python/`.
- `#   ...` — una línea que empieza con `#` es comentario: la shell la ignora. Ahí va tu trabajo.
- `git add estudiantes/$GHUSER/python` — eliges para el commit sólo tu carpeta, nada más del repo.
- `git commit -m "…"` — guardas esos cambios en tu historial; `-m` da el mensaje en la misma línea.
- `git push -u origin tarea-09-datacamp-python` — subes la branch a tu fork (`origin`). `-u` la deja enlazada: el siguiente push basta con `git push`.

**No se entrega** la captura de un ejercicio suelto ni la del panel de inicio: la captura es la página del curso terminado o tu Statement of Accomplishment, con tu nombre.

**Acabaste cuando** el pull request está abierto y su revisión en verde. Si no terminaste el curso, sube lo que sí hiciste y dilo en el archivo.

## 2 · Tu ambiente uv dentro de Docker

| | |
|---|---|
| **Vence** | 2026-10-06 |
| **Vale** | 10 puntos |
| **Branch** | `tarea-09-uv-docker` |
| **Carpeta** | `estudiantes/<tu-login>/09_python/`: la entrega en `uv_docker/`, tus labs en `ambientes/` |

Un programa que reporta su propio ambiente. Lo corres en tu máquina y dentro de un contenedor, y explicas qué salió igual y qué no.

![Las cinco etapas de un Dockerfile con uv en orden: imagen base con Python, el binario de uv, los dos archivos que describen el ambiente, crear el ambiente desde el lock sin dejar que cambie, y el programa.](../_assets/py-uv-docker.svg)

**Entregas seis archivos**, todos dentro de `uv_docker/`:

| Archivo | Qué debe tener |
|---|---|
| `reporte.py` | Tu fila en `fila_propia()`, usando un paquete que tú elegiste |
| `pyproject.toml` | `rich` y tu paquete, agregado con uv. **No corras `uv init`**: la plantilla ya es el proyecto |
| `uv.lock` | El que genera uv. Nunca a mano |
| `Dockerfile` | Los tres huecos llenos, cada instrucción debajo de su comentario, en el orden de la figura. Los comentarios pueden quedarse |
| `.dockerignore` | La línea que deja fuera tu ambiente local. La plantilla no la trae a propósito |
| `bitacora.md` | Todas sus secciones llenas |

**El ritual**

Si ya hiciste el ritual en clase ([[ambientes-python]], «Antes de clase»), **no lo repitas**: la branch ya existe y volver a copiar pisaría tus cambios. Sólo entra:

```bash
cd {tu_fork_de_la_clase}
git switch tarea-09-uv-docker
cd estudiantes/$GHUSER/09_python/uv_docker
```

- `git switch tarea-09-uv-docker` — **sin** `-c`: la branch ya existe, sólo te cambias a ella.
- `cd estudiantes/$GHUSER/09_python/uv_docker` — entras a la carpeta de la entrega. Los pasos de abajo se corren aquí.

Si no lo hiciste:

```bash
cd {tu_fork_de_la_clase}
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-09-uv-docker
mkdir -p estudiantes/$GHUSER/09_python
cp -r codigo/09_python/ambientes codigo/09_python/uv_docker estudiantes/$GHUSER/09_python/
cd estudiantes/$GHUSER/09_python/uv_docker
```

Son las mismas piezas del ritual de DataCamp, con otra branch y otra carpeta: `-c` crea `tarea-09-uv-docker`, y `cp -r` trae `ambientes/` y `uv_docker/` por nombre. Si ves `por_dentro/` en tu carpeta, es de la sección 9.2 y va en otra branch. El `cd` final te deja en la carpeta de la entrega.

**Los pasos**, cada uno con lo que ya viste en [[lab-uv]] y en la unidad 8:

1. `uv add <tu-paquete>` — agrega un paquete al proyecto: lo anota en `pyproject.toml`, fija su versión exacta (y la de sus dependencias) en `uv.lock` y lo instala en `.venv/`. Escribe el nombre del paquete sin `< >`.
2. Escribe tu fila en `reporte.py` y córrela con `uv run reporte.py`: corre el script con el Python de `.venv/`, sin activar nada, y antes revisa que el ambiente coincida con el lock. Pega la salida en la bitácora.
3. Llena los tres huecos del `Dockerfile` y la línea de `.dockerignore`. Qué va en cada hueco lo dice su comentario; el orden, la figura.
4. Construye para la arquitectura del revisor: `docker buildx build --platform linux/amd64 -t <usuario-docker-hub>/reporte .`
    - `docker buildx build` — construye una imagen siguiendo el `Dockerfile` de la carpeta.
    - `--platform linux/amd64` — para procesadores Intel/AMD de 64 bits, los del revisor. En Apple Silicon, sin ella, sale una imagen ARM.
    - `-t <usuario-docker-hub>/reporte` — le pone nombre (*tag*). El prefijo con tu usuario de Docker Hub es lo que deja hacer push a tu cuenta.
    - `.` — el contexto: la carpeta actual es lo que Docker recibe para construir; entra todo lo que `.dockerignore` no excluya.
5. Córrela: `docker run --rm --platform linux/amd64 <usuario-docker-hub>/reporte`. Pega la salida en la bitácora.
    - `docker run` — crea un contenedor desde la imagen y ejecuta su comando.
    - `--rm` — borra el contenedor al terminar; la imagen se queda.
    - `--platform linux/amd64` — pide la variante amd64, la que construiste. En Apple Silicon se emula.
6. Inicia sesión y publícala: `docker login`, luego `docker push <usuario-docker-hub>/reporte`. Pega en la bitácora la línea `digest: sha256:…` que imprime el push.
    - `docker login` — pide tu usuario y contraseña (o token) de Docker Hub. Sin sesión, el push se rechaza.
    - `docker push` — sube la imagen al registro con el nombre que le diste en `-t`. El `digest` es la huella `sha256` de lo que subiste.
7. La prueba, en este orden: `docker logout`, `docker rmi -f <usuario-docker-hub>/reporte`, `docker run --rm --platform linux/amd64 <usuario-docker-hub>/reporte`.
    - `docker logout` — cierras sesión: la prueba corre sin tu cuenta, igual que para el revisor.
    - `docker rmi -f` — borras la imagen de tu disco; `-f` fuerza el borrado aunque un contenedor viejo la use.
    - `docker run …` — ya no la encuentra local (`Unable to find image`) y la baja de Docker Hub (`Pulling from`).

**Con Podman también vale.** Los mismos pasos con `podman`, nombrando la imagen completa, `docker.io/<usuario-docker-hub>/reporte`:

- `podman login docker.io` y `podman logout docker.io` — inicias y cierras sesión en Docker Hub.
- `podman push --digestfile digest.txt docker.io/<usuario-docker-hub>/reporte` — `podman push` no imprime el digest; `--digestfile` lo guarda en `digest.txt`, y ése es el que pegas en la bitácora.
- `podman rmi -f` y `podman run --rm --platform linux/amd64 docker.io/<usuario-docker-hub>/reporte` — la descarga se ve como `Trying to pull` y `Copying blob`, en lugar de `Unable to find image` y `Pulling from`.

`<usuario-docker-hub>` es tu usuario de **Docker Hub**, no el de GitHub: con otro usuario, el push se rechaza.

```bash
cd {tu_fork_de_la_clase}
git add estudiantes/$GHUSER/09_python/ambientes estudiantes/$GHUSER/09_python/uv_docker
git status        # .venv/ NO debe aparecer
git commit -m "unidad 09: labs de ambientes y mi ambiente uv en Docker"
git push -u origin tarea-09-uv-docker
```

- `cd {tu_fork_de_la_clase}` — vuelves a la raíz del repo, donde la ruta de `git add` existe.
- `git add estudiantes/$GHUSER/09_python/ambientes estudiantes/$GHUSER/09_python/uv_docker` — eliges labs y entrega juntos, por nombre. `por_dentro/`, si existe, se queda fuera.
- `git status` — lista lo que va a entrar al commit. Si ves `.venv/`, detente antes de hacer commit.
- `git commit -m` y `git push -u origin` — igual que en DataCamp, con esta branch.

**No se entrega**: `.venv/`, `__pycache__/`, la imagen como archivo, ni la salida de `docker login`. Los labs de `ambientes/` **sí** van, en este mismo pull request: viven en tu carpeta `09_python/`, igual que la entrega.

**Tres cosas que se rompen**

| Qué haces | Qué pasa |
|---|---|
| Construyes en Apple Silicon sin `--platform linux/amd64` | La imagen corre en tu Mac y en la del revisor no |
| Copias todo el proyecto a la imagen sin excluir tu `.venv/` | Truena al correr (salida real, abajo) |
| Cambias `pyproject.toml` y no regeneras el lock | La construcción falla: `The lockfile at uv.lock needs to be updated` |

Lo que sale cuando tu `.venv/` local entra a la imagen:

```text
warning: Ignoring existing virtual environment linked to non-existent Python interpreter
Removed virtual environment at: .venv
Creating virtual environment at: .venv
Traceback (most recent call last):
  File "/app/reporte.py", line 10, in <module>
    import humanize
ModuleNotFoundError: No module named 'humanize'
```

La URL que sirve es la pública, `https://hub.docker.com/r/<usuario-docker-hub>/reporte`, con su `https://`; la de tu panel (`/repository/…`) da 404 a los demás. Ábrela en una ventana privada.

**Acabaste cuando** el pull request está abierto y su revisión en verde. La prueba del paso 7 es lo que muestra que tu imagen se baja del registro y no de tu disco.

Si la revisión sale roja, corrige y haz push a la **misma** branch: no vuelvas a correr `git switch -c`, que ya existe.

## Qué revisa la revisión automática

| Revisa | No revisa (lo reviso yo) |
|---|---|
| Que estén los archivos y la captura, con su nombre | Que la captura sea tuya y de este curso |
| Que las secciones estén llenas; fecha `AAAA-MM-DD`; URL presente | Que la URL abra tu certificado |
| Imagen base y los tres huecos llenos con instrucciones, no comentarios; el ambiente creado exigiendo que el lock coincida | Que la imagen exista, corra y salga de tus archivos |
| `.venv` en `.dockerignore`; tu fila con un paquete importado; una dependencia además de `rich`; un `uv.lock` con la forma que genera uv | Que las salidas pegadas salgan de tu imagen y coincidan con tu lock |
| URL pública con `https://`; digest completo; prueba con `Unable to find image` y `Pulling from` (Docker) o `Trying to pull` y `Copying blob` (Podman); sin `Login Succeeded` | Lo que debes poder explicar sin ayuda |

Los mensajes dicen **qué** está mal, **por qué** importa y **dónde investigar**; no dicen cómo arreglarlo.
