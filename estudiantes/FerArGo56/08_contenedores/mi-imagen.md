# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub:FerArGo56
- Usuario de Docker Hub: ferargo

## La URL pública

URL:https://hub.docker.com/r/ferargo/08_contenedores

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' ferargo/08_contenedores_latest
ferargo/08_contenedores@sha256:5c2d452b851fa757ac5cdc583c2a73d88815bd1dd6bb3fcd4c5b1decd2949272
```

## Cómo la corro yo
Comando exacto:
```text
docker run --rm ferargo/08_contenedores:latest
```
Salida que debo esperar:
```text
FerArGo56
Tue Sep 22 17:15:02 UTC 2026
7.0.12-linuxkit
```
## La prueba de que se baja del registro
```text
docker logout
docker rmi -f ferargo/08_contenedores:latest
docker run --rm ferargo/08_contenedores:latest
respuesta: 
MacBook-Air-de-Ana-3:08_contenedores anamari$ docker run --rm ferargo/08_contenedores:latest
Unable to find image 'ferargo/08_contenedores:latest' locally
latest: Pulling from ferargo/08_contenedores
d5f0cab2eb80: Pull complete 
57c8bd483af3: Pull complete 
c208b5cb1a65: Pull complete 
44136fa355b3: Download complete 
1b13166a1800: Download complete 
Digest: sha256:5c2d452b851fa757ac5cdc583c2a73d88815bd1dd6bb3fcd4c5b1decd2949272
Status: Downloaded newer image for ferargo/08_contenedores:latest
FerArGo56
Tue Sep 22 17:16:46 UTC 2026
7.0.12-linuxkit
```
## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:
```text
docker images ferargo/08_contenedores:latest
respuesta: 
MacBook-Air-de-Ana-3:08_contenedores anamari$ docker images ferargo/08_contenedores:latest
                                                            i Info →   U  In Use
IMAGE                           ID             DISK USAGE   CONTENT SIZE   EXTRA
ferargo/08_contenedores:latest
                                5c2d452b851f        117MB         29.8MB 
```
