---
id: entregas-contenedores
title: "Las cinco entregas"
nav_title: "Entregas"
summary: "El tablero de la unidad: qué vence cuándo, desde qué branch, en qué carpeta y con qué archivos, con el ritual escrito para copiar."
status: ready
estimated_time: 9m
tags: [entrega, pull-request, branch, datacamp, docker-hub, tablero]
prerequisites: [el-flujo-del-curso]
---

# Las cinco entregas

**Anexo D** · el tablero de la unidad

Cinco entregas en ocho días, y cuatro de ellas por pull request. Esta página es la versión legible de lo que cada objeto oficial dice en su contrato: **el contrato manda**, y aquí está en forma de tabla para que puedas entregar sin leer nada más.

Las tres del martes 22 y la del jueves 24 vencen **el mismo día de clase, antes de que empiece la sesión**. No es un detalle de estilo: la sesión del 22 da por tecleado lo que entrena *Introduction to Docker*, y la del 24 da por sabidos los capítulos 1 y 2 de *Intermediate Docker*.

## El mes de un golpe

::: table {#cont-anexod-resumen title="Las cinco entregas de la unidad"}

| # | Entrega | Vence | Vale | Branch | Carpeta |
|---:|---|---|---:|---|---|
| 1 | Instalar Docker y Podman | martes 22 de septiembre | — | ninguna | ninguna |
| 2 | DataCamp: *Introduction to Docker* | martes 22 de septiembre | 10 | `tarea-08-datacamp-intro` | `docker/` |
| 3 | Tu imagen en Docker Hub | martes 22 de septiembre | 10 | `tarea-08-imagen` | `08_contenedores/` |
| 4 | DataCamp: *Intermediate*, capítulos 1 y 2 | jueves 24 de septiembre | 10 | `tarea-08-datacamp-inter-1` | `docker/` |
| 5 | DataCamp: *Intermediate*, capítulos 3 y 4 | martes 29 de septiembre | 10 | `tarea-08-datacamp-inter-2` | `docker/` |

:::

**Treinta puntos son de DataCamp y diez de tu imagen**, y la primera —la que no lleva puntos— es de la que dependen las otras cuatro.

Fíjate en la columna de la carpeta: son **dos**, y la división no es arbitraria. Las tres entregas de DataCamp comparten un solo `certificaciones.md` que se llena una sección por entrega, espejo de `codigo/docker/`; el trabajo de la unidad vive aparte, en `08_contenedores/`. Cada pull request toca **una sola** de las dos.

## 1 · Instalar Docker y Podman

| | |
|---|---|
| **Vence** | martes 22 de septiembre |
| **Vale** | no lleva puntos |
| **Branch** | ninguna: no se entrega por pull request |
| **Carpeta** | ninguna: no se sube nada |

**No entregas nada.** Es hacerlo y que te quede funcionando, con las instrucciones de [[instalar-docker-y-podman]] y, si algo falla, [[planes-b-de-instalacion]].

**El ritual**

```bash
docker run --rm hello-world      # sin sudo
podman run --rm hello-world      # sin sudo
docker login                     # y después el prepull de seis imágenes
```

**Acabaste cuando** los dos imprimen el saludo, los corriste **tú**, en **tu** máquina, en una terminal recién abierta y **sin escribir `sudo` en ninguno de los dos**. Si uno pide `sudo` o responde permiso denegado, todavía no terminaste.

> [!WARNING]
> **Si el sábado 19 no te funciona, dilo el sábado 19.** Una instalación atorada que se reporta el sábado se arregla en veinte minutos; la misma el lunes a medianoche te cuesta la clase del martes y las dos entregas que vencen esa mañana.

## 2 · DataCamp: Introduction to Docker

| | |
|---|---|
| **Vence** | martes 22 de septiembre |
| **Vale** | 10 puntos |
| **Branch** | `tarea-08-datacamp-intro` |
| **Carpeta** | `estudiantes/<tu-login>/docker/` |

**Entregas dos archivos**

- `certificaciones.md` con la sección *Introduction to Docker* llena: la fecha en que lo terminaste y la **URL del Statement of Accomplishment**. Las otras tres secciones se quedan vacías, que son para las entregas 4 y 5: la 5 llena dos.
- `introduccion-a-docker.png`: el curso terminado, con **tu nombre y el 100 % visibles**. Con ese nombre exacto, porque la plantilla ya lo enlaza; si te sale en `jpg`, corrige el enlace dentro del archivo.

**El ritual**

```bash
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-08-datacamp-intro
mkdir -p estudiantes/$GHUSER/docker
cp -r codigo/docker/. estudiantes/$GHUSER/docker/
#   ... llenas certificaciones.md y guardas la captura ...
git add estudiantes/$GHUSER/docker
git commit -m "unidad 08: DataCamp Introduction to Docker"
git push -u origin tarea-08-datacamp-intro
```

Es `docker`, **no `github`**: la de `github` es la de las certificaciones de la unidad pasada y ya está cerrada. Y ojo con la barra y el punto al final del origen del `cp`.

**Acabaste cuando** el pull request está abierto y su revisión en verde.

## 3 · Tu imagen en Docker Hub

| | |
|---|---|
| **Vence** | martes 22 de septiembre |
| **Vale** | 10 puntos |
| **Branch** | `tarea-08-imagen` |
| **Carpeta** | `estudiantes/<tu-login>/08_contenedores/` |

**Entregas cuatro archivos**

- `info/info.sh` modificado: **tres líneas de código**, no de comentario —tu login de GitHub, la fecha de construcción y una tercera tuya—, y sin el `echo` de depuración que trae el original.
- `roto/Dockerfile` arreglado: base pineada, `COPY` partido en dos, `USER` no `root`. Los tres defectos están explicados en [[arreglar-un-dockerfile]].
- `bitacora.md`: la salida de `docker version`, de `docker images` y del `docker history` de tu imagen, los tres defectos en una línea cada uno, y la cosa que se te rompió.
- `mi-imagen.md`: la **URL pública** `hub.docker.com/r/<tu-usuario>/<tu-imagen>`, tus dos nombres de usuario, el digest, el comando exacto que debo correr, la salida que debo esperar, y la prueba de que se baja del registro — `docker logout`, `docker rmi -f`, `docker run`, con sus líneas `Unable to find image ... locally` y `Pulling from`.

**El ritual**

```bash
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-08-imagen
mkdir -p estudiantes/$GHUSER/08_contenedores
cp -r codigo/08_contenedores/. estudiantes/$GHUSER/08_contenedores/
#   ... trabajas ahí dentro, y publicas tu imagen ...
git add estudiantes/$GHUSER/08_contenedores
git commit -m "unidad 08: mi imagen en Docker Hub"
git push -u origin tarea-08-imagen
```

Las tres que se rompen siempre: la imagen pesa **menos de 300 MB**, y eso se elige en la primera línea del `Dockerfile`, no borrando cosas al final; si tu laptop es Apple Silicon, construye con `docker buildx build --platform linux/amd64` o publicas algo que sólo corre en máquinas como la tuya; y **nunca pegues la salida de `docker login`**, que lleva tu token adentro.

No se entregan: `volumenes/predicciones.md`, `output.txt` ni `__pycache__/`. La imagen tampoco se sube como archivo — lo que se entrega es la URL.

**Acabaste cuando** el pull request está abierto, su revisión en verde, y la URL pública abre en una **ventana privada**.

## 4 · DataCamp: Intermediate Docker, capítulos 1 y 2

| | |
|---|---|
| **Vence** | jueves 24 de septiembre |
| **Vale** | 10 puntos |
| **Branch** | `tarea-08-datacamp-inter-1` |
| **Carpeta** | `estudiantes/<tu-login>/docker/` |

**Entregas dos cosas**

- `certificaciones.md` con la sección *Intermediate Docker · capítulos 1 y 2* llena, con la fecha. **Aquí no hay Statement of Accomplishment y no lo busques**: medio curso no da certificado.
- `intermedio-1-2.png`: la página del curso donde se vean sus **cuatro capítulos**, los dos primeros marcados como completados, y tu nombre. Una captura de un ejercicio suelto no sirve.

**El ritual**

```bash
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-08-datacamp-inter-1
#   la carpeta docker/ ya está ahí desde el martes: NO la vuelvas a copiar.
#   ... llenas la segunda sección y guardas la captura ...
git add estudiantes/$GHUSER/docker
git commit -m "unidad 08: DataCamp Intermediate 1 y 2"
git push -u origin tarea-08-datacamp-inter-1
```

La branch nace de `main` actualizado, **no de la branch de la entrega anterior**. Una branch por tarea, sin excepciones.

**Acabaste cuando** el pull request está abierto y su revisión en verde.

## 5 · DataCamp: Intermediate Docker, capítulos 3 y 4

| | |
|---|---|
| **Vence** | martes 29 de septiembre |
| **Vale** | 10 puntos |
| **Branch** | `tarea-08-datacamp-inter-2` |
| **Carpeta** | `estudiantes/<tu-login>/docker/` |

**Entregas dos cosas**

- `certificaciones.md` con la sección *Intermediate Docker · capítulos 3 y 4* llena: la fecha y la **URL del Statement of Accomplishment**, que esta vez sí existe porque el curso queda completo. En el mismo archivo va la última sección, **«Una cosa que aprendiste y no sabías»**: dos o tres líneas sobre algo concreto de cualquiera de los dos cursos. Se lee.
- `intermedio-3-4.png`: el curso terminado, con tu nombre y el 100 % visibles.

**El ritual**

```bash
git switch main && git fetch upstream && git merge upstream/main
git switch -c tarea-08-datacamp-inter-2
#   la carpeta docker/ sigue ahí: sólo llenas la tercera sección.
git add estudiantes/$GHUSER/docker
git commit -m "unidad 08: DataCamp Intermediate 3 y 4"
git push -u origin tarea-08-datacamp-inter-2
```

**Acabaste cuando** el pull request está abierto y su revisión en verde. Con ésta cierras los cuarenta puntos de la unidad.

## Qué comprueba, y qué no, la revisión automática

Corren **tres** revisiones en cada pull request:

| Revisión | Qué comprueba |
|---|---|
| **Forma** | Que todo lo que tocaste viva en `estudiantes/<tu-login>/`, con tu login exacto; **una sola** subcarpeta, la que tu branch tiene asignada; sin basura; no desde la branch default; branch con forma `tarea-NN-nombre` |
| **Contenido mínimo** | Que estén los archivos que pide la tarea, con su nombre exacto; que las secciones no sigan como la plantilla; que traigan fecha, y URL cuando se pide; que la captura no esté vacía |
| **Reglas de la tarea** | Desde las entregas de *Intermediate Docker*, cada tarea trae su propia ficha con comprobaciones propias. Sus mensajes dicen **qué** está mal, **por qué** y **dónde investigar**; el cómo te toca a ti |

Lo que **ninguna** comprueba, y por eso hay que decirlo aquí:

- **Si lo que dicen tus archivos es cierto o está bien hecho.** Una bitácora puede estar llena y describir otra cosa.
- **Qué muestra tu captura.**
- **El resto de la regla del espejo**: que la subcarpeta más profunda se llame igual que en `codigo/`.
- **Que tu imagen se baje de verdad.** Eso lo corro yo, con el comando que tú me escribiste.

Por eso el verde **no es la aprobación**: la aprobación es mía, y la ves como la etiqueta `entrega-aceptada` en tu pull request.

Tres fechas que conviene tener claras, porque dos reglas dejan de avisar y empiezan a rechazar justo en esta unidad:

- **Desde el 18 de septiembre**, entregar desde la branch default de tu fork se **rechaza**; antes sólo avisaba.
- **Desde el 22 de septiembre** —el día de tus dos primeras entregas—, un pull request **abierto** con un nombre de branch que no tenga la forma `tarea-NN-nombre` se **rechaza**; a uno abierto antes sólo le avisa.
- La regla de **una sola carpeta** no tiene periodo de gracia: rechaza desde el primer día. Es la que impide que los tres pull requests de DataCamp se peleen por el mismo `certificaciones.md`.

Y el reflejo que ahorra la mitad de los sustos: **un pull request rechazado se corrige haciendo `push` a la misma branch.** No abras otro; el pull request se actualiza solo y la revisión vuelve a correr. La única excepción es que lo rechazado sea la branch misma: ahí la entrega va en una branch nueva y cierras el viejo.

> [!NOTE]
> **Si sólo recuerdas una cosa:** una branch por tarea, una carpeta por pull request, y el verde sólo dice que no rompiste el repositorio — no que entregaste.
