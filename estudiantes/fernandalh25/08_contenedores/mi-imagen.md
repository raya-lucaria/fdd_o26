# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub: fernandalh25
- Usuario de Docker Hub: fersy25

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL: https://hub.docker.com/r/fersy25/fersy-tarea-08

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' fersy25/fersy-tarea-08
fersy25/fersy-tarea-08@sha256:4935ce213dbb7ca1d3ef21600e4d9a2157598847875f321df0439c0643ed00e8
```

## Cómo la corro yo

Comando exacto:

```text
docker run fersy25/fersy-tarea-08
```

Salida que debo esperar 

```text
Unable to find image 'fersy25/fersy-tarea-08:latest' locally
latest: Pulling from fersy25/fersy-tarea-08
774043ccc8cc: Pull complete
fae068737816: Pull complete
e5c850752c51: Pull complete
1cb952ef3002: Pull complete
70c33d8f5da8: Pull complete
3209c9ff24e6: Pull complete
41278486fe09: Pull complete
e4a4941c8989: Pull complete
713469e7520c: Pull complete
Digest: sha256:4935ce213dbb7ca1d3ef21600e4d9a2157598847875f321df0439c0643ed00e8
Status: Downloaded newer image for fersy25/fersy-tarea-08:latest
Corriendo como: appuser
requests 2.32.3
```

## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
Removing login credentials for https://index.docker.io/v1/

docker rmi -f fersy25/fersy-tarea-08
Untagged: fersy25/fersy-tarea-08:latest

docker run --rm fersy25/fersy-tarea-08
Unable to find image 'fersy25/fersy-tarea-08:latest' locally
latest: Pulling from fersy25/fersy-tarea-08
774043ccc8cc: Pull complete
fae068737816: Pull complete
e5c850752c51: Pull complete
1cb952ef3002: Pull complete
70c33d8f5da8: Pull complete
3209c9ff24e6: Pull complete
41278486fe09: Pull complete
e4a4941c8989: Pull complete
713469e7520c: Pull complete
Digest: sha256:4935ce213dbb7ca1d3ef21600e4d9a2157598847875f321df0439c0643ed00e8
Status: Downloaded newer image for fersy25/fersy-tarea-08:latest
Corriendo como: appuser
requests 2.32.3
```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images fersy25/fersy-tarea-08
REPOSITORY               TAG       IMAGE ID       CREATED          SIZE
fersy25/fersy-tarea-08   latest    cd0f50c1ee7c   27 minutes ago   136MB
```
