# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub: geraVillV
- Usuario de Docker Hub: geraplayer

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL: https://hub.docker.com/r/geraplayer/roto-fix

## El digest

```text
geraplayer/roto-fix@sha256:a067676c0ba0af0f01454256a898c7eb78216d0645fff0adde140ff3cdaa350f

```

## Cómo la corro yo

Comando exacto:

```text
docker run --rm geraplayer/roto-fix:latest
```

Salida que debo esperar:

```text
Corriendo como: appuser
requests 2.32.3
```

## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
docker rmi -f geraplayer/roto-fix:latest
docker run --rm geraplayer/roto-fix:latest

Removing login credentials for https://index.docker.io/v1/
Untagged: geraplayer/roto-fix:latest
Unable to find image 'geraplayer/roto-fix:latest' locally
latest: Pulling from geraplayer/roto-fix
Digest: sha256:a067676c0ba0af0f01454256a898c7eb78216d0645fff0adde140ff3cdaa350f
Status: Downloaded newer image for geraplayer/roto-fix:latest
Corriendo como: appuser
requests 2.32.3

```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images geraplayer/roto-fix

REPOSITORY          TAG       DISK USAGE   CONTENT SIZE
geraplayer/roto-fix latest    206MB        51.7MB

```
