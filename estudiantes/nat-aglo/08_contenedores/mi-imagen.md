# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub:nat-aglo
- Usuario de Docker Hub:nataglo

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL:https://hub.docker.com/layers/nataglo/primera_imagen/latest/images/sha256-1695a2169fb2c82de8f08cc7d6b93558351a9c839277165e0341ebc42b4f7c89

## El digest

```
docker inspect --format '{{index .RepoDigests 0}}' nataglo/primera_imagen:latest

primera_imagen@sha256:1bfc3e0dc5d3f7d23910caceda385811fbcf2090657760e9b6641bcce0ab67ea

```

## Cómo la corro yo

```
Comando exacto: docker run nataglo/primera_imagen:latest

```

Salida que debo esperar:

```
original

```


## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
Removing login credentials for https://index.docker.io/v1/

docker rmi -f nataglo/primera_imagen:latest
Untagged: nataglo/primera_imagen:latest

docker run --rm nataglo/primera_imagen:latest
Unable to find image 'nataglo/primera_imagen:latest' locally
latest: Pulling from nataglo/primera_imagen
Digest: sha256:1bfc3e0dc5d3f7d23910caceda385811fbcf2090657760e9b6641bcce0ab67ea
Status: Downloaded newer image for nataglo/primera_imagen:latest
original

```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```
docker images nataglo/primera_imagen:latest
IMAGE                           ID             DISK USAGE   CONTENT SIZE   EXTRA
nataglo/primera_imagen:latest   1bfc3e0dc5d3        177MB         43.3MB    U   

```

