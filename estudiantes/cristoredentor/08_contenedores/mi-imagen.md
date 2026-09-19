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

URL: https://hub.docker.com/r/cristophergongs/hola 

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' <tu-usuario>/<tu-imagen>


```

## Cómo la corro yo

Comando exacto:

```text

docker run --rm cristophergongs/hola:v1


```

Salida que debo esperar:

```text
Unable to find image 'cristophergongs/hola:v1' locally
v1: Pulling from cristophergongs/hola
Digest: sha256:b8fbf3117ec8eaf952efe8e55feb1f29e4e80a9ffee879ba6abb00c8eedc4596
Status: Downloaded newer image for cristophergongs/hola:v1
hola desde mi imagen


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
cris@laptop-cris:~/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/08_contenedores$ docker rmi -f cristophergongs/hola:v1
Untagged: cristophergongs/hola:v1
cris@laptop-cris:~/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/08_contenedores$ docker run --rm cristophergongs/hola:v1
Unable to find image 'cristophergongs/hola:v1' locally
v1: Pulling from cristophergongs/hola
Digest: sha256:b8fbf3117ec8eaf952efe8e55feb1f29e4e80a9ffee879ba6abb00c8eedc4596
Status: Downloaded newer image for cristophergongs/hola:v1
hola desde mi imagen

```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images <tu-usuario>/<tu-imagen>
IMAGE                     ID             DISK USAGE   CONTENT SIZE   EXTRA
cristophergongs/hola:v1   b8fbf3117ec8       12.1MB         3.63MB        
hola:latest               b8fbf3117ec8       12.1MB         3.63MB        
roto:v2                   dc15e7f2df23       1.64GB          421MB        
roto:v3                   d5ef7057461e        198MB         48.8MB        
ubuntu:latest             da6fc2be5478        160MB         45.3MB    U   


```
