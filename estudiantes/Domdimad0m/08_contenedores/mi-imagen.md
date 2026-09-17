# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub: Domdimad0m
- Usuario de Docker Hub: dominiqueont

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL:

https://hub.docker.com/r/dominiqueont/domdimad0m-info

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' dominiqueont/domdimad0m-info:v1

dominiqueont/domdimad0m-info@sha256:8ad06a32df0dc22931599fda07e95377098ad92e11947de9fe7bcb7787c132e7

```

## Cómo la corro yo

Comando exacto:

```text
docker run --rm dominiqueont/domdimad0m-info:v1
```

Salida que debo esperar:

```text
GitHub: Domdimad0m
Fecha de construccion: 2026-09-17
Mensaje: Hola desde mi primera imagen de Docker
```

## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
Removing login credentials for https://index.docker.io/v1/

docker rmi -f dominiqueont/domdimad0m-info:v1 domdimad0m-info:v1
Untagged: dominiqueont/domdimad0m-info:v1
Untagged: domdimad0m-info:v1
Deleted: sha256:8ad06a32df0dc22931599fda07e95377098ad92e11947de9fe7bcb7787c132e7

docker run --rm dominiqueont/domdimad0m-info:v1
Unable to find image 'dominiqueont/domdimad0m-info:v1' locally
v1: Pulling from dominiqueont/domdimad0m-info
ca22feacae7f: Pull complete
797f896a72e2: Pull complete
f9588ec6460c: Pull complete
9df6de43c0f6: Download complete
Digest: sha256:8ad06a32df0dc22931599fda07e95377098ad92e11947de9fe7bcb7787c132e7
Status: Downloaded newer image for dominiqueont/domdimad0m-info:v1
GitHub: Domdimad0m
Fecha de construccion: 2026-09-17
Mensaje: Hola desde mi primera imagen de Docker
```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images dominiqueont/domdimad0m-info:v1

IMAGE                              ID             DISK USAGE   CONTENT SIZE
dominiqueont/domdimad0m-info:v1    8ad06a32df0d   117MB        29.8MB
```
