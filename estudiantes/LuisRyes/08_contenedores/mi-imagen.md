# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub:LuisRyes
- Usuario de Docker Hub:luisryes

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL:https://hub.docker.com/r/luisryes/mi-imagen

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' <tu-usuario>/<tu-imagen>
luisfernandoreyesaltamirano@MacBook-Air-de-Luis-4 fdd_o26_LuisRyes % docker inspect --format '{{index .RepoDigests 0}}' luisryes/mi-imagen:v1
luisryes/mi-imagen@sha256:a940beaf906aeae3e56f5a40fb4762addb902d685fd870a6f3c2ca5dad77e6da
```

## Cómo la corro yo

Comando exacto:

```text
docker run --rm luisryes/mi-imagen:v1
```

Salida que debo esperar:

```text
Corriendo como: nobody
requests 2.32.3

```

## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
docker rmi -f <tu-usuario>/<tu-imagen>
docker run --rm <tu-usuario>/<tu-imagen>

luisfernandoreyesaltamirano@MacBook-Air-de-Luis-4 fdd_o26_LuisRyes % docker logout
Removing login credentials for https://index.docker.io/v1/
luisfernandoreyesaltamirano@MacBook-Air-de-Luis-4 fdd_o26_LuisRyes % docker run --platform linux/amd64 --rm luisryes/mi-imagen:v1
Corriendo como: nobody
requests 2.32.3
luisfernandoreyesaltamirano@MacBook-Air-de-Luis-4 fdd_o26_LuisRyes % nano estudiantes/LuisRyes/08_contenedores/mi-imagen.md
luisfernandoreyesaltamirano@MacBook-Air-de-Luis-4 fdd_o26_LuisRyes % docker rmi -f luisryes/mi-imagen:v1
Untagged: luisryes/mi-imagen:v1
Deleted: sha256:a940beaf906aeae3e56f5a40fb4762addb902d685fd870a6f3c2ca5dad77e6da
luisfernandoreyesaltamirano@MacBook-Air-de-Luis-4 fdd_o26_LuisRyes % docker run --platform linux/amd64 --rm luisryes/mi-imagen:v1
Unable to find image 'luisryes/mi-imagen:v1' locally
v1: Pulling from luisryes/mi-imagen
13140c87cc71: Pull complete 
29ca634d3e9b: Pull complete 
0380fc010d91: Pull complete 
61fd4a0539f5: Pull complete 
44136fa355b3: Already exists 
8d7d07ef499b: Download complete 
Digest: sha256:a940beaf906aeae3e56f5a40fb4762addb902d685fd870a6f3c2ca5dad77e6da
Status: Downloaded newer image for luisryes/mi-imagen:v1
Corriendo como: nobody
requests 2.32.3
```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images <tu-usuario>/<tu-imagen>

luisfernandoreyesaltamirano@MacBook-Air-de-Luis-4 fdd_o26_LuisRyes % docker images luisryes/mi-imagen:v1
                                                                                                                                                                                      i Info →   U  In Use
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
luisryes/mi-imagen:v1   6c445695389b        195MB         47.7MB     
```
