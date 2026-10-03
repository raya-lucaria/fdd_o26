# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub: cristoredentor
- Usuario de Docker Hub: cristophergongs

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL: https://hub.docker.com/r/cristophergongs/roto 

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' <tu-usuario>/<tu-imagen>

docker inspect --format '{{index .RepoDigests 0}}' cristophergongs/roto:v1
cristophergongs/roto@sha256:b39db0c9863d47eb95ef134382dc4fa63e87f542aaabbb23bf9df986f3639632

```

## Cómo la corro yo

Comando exacto:

```text

docker pull cristophergongs/roto:v1
docker run cristophergongs/roto:v1

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
docker rmi -f <tu-usuario>/<tu-imagen>
docker run --rm <tu-usuario>/<tu-imagen>

cris@laptop-cris:~/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/08_contenedores$ docker logout
Removing login credentials for https://index.docker.io/v1/
cris@laptop-cris:~/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/08_contenedores$ docker rmi -f cristophergongs/roto:v1    
docker run --rm cristophergongs/roto:v1
Untagged: cristophergongs/roto:v1
Unable to find image 'cristophergongs/roto:v1' locally
v1: Pulling from cristophergongs/roto
Digest: sha256:b39db0c9863d47eb95ef134382dc4fa63e87f542aaabbb23bf9df986f3639632
Status: Downloaded newer image for cristophergongs/roto:v1
Corriendo como: app
requests 2.32.3


```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images <tu-usuario>/<tu-imagen>
cris@laptop-cris:~/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/08_contenedores$ docker images cristophergongs/roto:v1
                                                                                                                                            i Info →   U  In Use
IMAGE                     ID             DISK USAGE   CONTENT SIZE   EXTRA
cristophergongs/roto:v1   b39db0c9863d        198MB         48.8MB    U   


```
