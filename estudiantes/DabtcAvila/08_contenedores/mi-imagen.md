# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub: DabtcAvila
- Usuario de Docker Hub: davidtechnologies

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL: https://hub.docker.com/r/davidtechnologies/fdd-roto

## El digest

```text
$ docker inspect --format '{{index .RepoDigests 0}}' davidtechnologies/fdd-roto:v1
davidtechnologies/fdd-roto@sha256:27ddf4225455f170bebb67b2758765f7a3e4a8c606322fdc4c11f5d5cba0e15e
```

## Cómo la corro yo

Comando exacto:

```text
docker run --rm davidtechnologies/fdd-roto:v1
```

Salida que debo esperar:

```text
Corriendo como: app
requests 2.32.3
```

## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
Removing login credentials for https://index.docker.io/v1/

docker rmi -f davidtechnologies/fdd-roto:v1
Untagged: davidtechnologies/fdd-roto:v1
Deleted: sha256:27ddf4225455f170bebb67b2758765f7a3e4a8c606322fdc4c11f5d5cba0e15e

docker run --rm davidtechnologies/fdd-roto:v1
Unable to find image 'davidtechnologies/fdd-roto:v1' locally
v1: Pulling from davidtechnologies/fdd-roto
cfdcf60485b7: Pulling fs layer
c6f11af8376b: Pulling fs layer
ca08c2c190db: Pulling fs layer
c36c043f92ca: Pulling fs layer
45876c6121ec: Pulling fs layer
c36c043f92ca: Already exists
cfdcf60485b7: Already exists
c6f11af8376b: Already exists
45876c6121ec: Already exists
ca08c2c190db: Already exists
c6f11af8376b: Pull complete
ca08c2c190db: Pull complete
c36c043f92ca: Pull complete
cfdcf60485b7: Pull complete
45876c6121ec: Pull complete
660eb784c0e1: Download complete
Digest: sha256:27ddf4225455f170bebb67b2758765f7a3e4a8c606322fdc4c11f5d5cba0e15e
Status: Downloaded newer image for davidtechnologies/fdd-roto:v1
Corriendo como: app
requests 2.32.3
```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
$ docker images davidtechnologies/fdd-roto:v1
IMAGE                           ID             DISK USAGE   CONTENT SIZE   EXTRA
davidtechnologies/fdd-roto:v1   27ddf4225455        221MB           48MB
```

La imagen está publicada para linux/amd64 y linux/arm64, así que el mismo comando corre en Linux, en Mac Intel y en Apple Silicon sin `--platform`.
