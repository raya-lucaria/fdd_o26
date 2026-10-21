# Mi imagen en Docker Hub

## Quién soy
- Usuario de GitHub: goldzweigarie-bit
- Usuario de Docker Hub: goldz177

## URL pública
https://hub.docker.com/r/goldz177/app-docker

## Digest
sha256:77cb3e83124ac1402289b8f2dffd6d3aafcbb21a400ddb19b058999a4e61a

## Comando
docker run --rm --platform linux/amd64 goldz177/app-docker:latest

## Salida esperada
GitHub: goldzweigarie-bit
Fecha de build: Wed Sep 23 18:00:00 UTC 2026
Dato extra: Esta imagen corre en linux/amd64

## Prueba de descarga
docker logout
docker rmi -f goldz177/app-docker:latest
docker run --rm --platform linux/amd64 goldz177/app-docker:latest
Unable to find image 'goldz177/app-docker:latest' locally
latest: Pulling from goldz177/app-docker
... (descarga exitosa) ...

## Tamaño
docker images goldz177/app-docker
REPOSITORY          TAG       IMAGE ID       CREATED         SIZE
goldz177/app-docker   latest    fabdd58699c0   2 minutes ago   135MB
