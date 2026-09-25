# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre: David Fernando Ávila Díaz
- Usuario de GitHub: DabtcAvila
- Usuario de Docker Hub: davidtechnologies

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text
$ docker version
Client:
 Version:           29.4.0
 API version:       1.54
 Go version:        go1.26.1
 Git commit:        9d7ad9f
 Built:             Tue Apr  7 08:34:32 2026
 OS/Arch:           darwin/arm64
 Context:           desktop-linux

Server: Docker Desktop 4.69.0 (224084)
 Engine:
  Version:          29.4.0
  API version:      1.54 (minimum version 1.40)
  Go version:       go1.26.1
  Git commit:       daa0cb7
  Built:            Tue Apr  7 08:36:25 2026
  OS/Arch:          linux/arm64
  Experimental:     false
 containerd:
  Version:          v2.2.1
  GitCommit:        dea7da592f5d1d2b7755e3a161be07f43fad8f75
 runc:
  Version:          1.3.4
  GitCommit:        v1.3.4-0-gd6d73eb8
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0

$ docker images
IMAGE                                            ID             DISK USAGE   CONTENT SIZE   EXTRA
dafel-technologies-frontend:latest               4c8f50c2fd1b       1.22GB          243MB   U    
davidtechnologies/fdd-roto:v1                    27ddf4225455        221MB           48MB        
deploy-api-backend:latest                        2ebc0b886f0b       1.01GB          227MB   U    
deploy-web-frontend:latest                       bc17b6de3c06       81.4MB         23.1MB   U    
docker/welcome-to-docker:latest                  c4d56c24da4f       22.9MB         6.35MB   U    
dpage/pgadmin4:latest                            50700ac17936        835MB          184MB   U    
hello-world:latest                               5e2309035332       22.6kB         10.3kB        
memoria-soberana-api-backend:latest              8ec3d6ceaceb       1.07GB          242MB        
memoria-soberana-web-frontend:latest             80b68ef9e81d        1.3GB          217MB        
mysql:8.0                                        18dee92bbc23       1.06GB          232MB   U    
nginx:alpine                                     d67ea0d64d51       80.1MB         22.9MB   U    
opensearchproject/opensearch-dashboards:2.11.1   223eaaca192b       2.39GB          446MB        
opensearchproject/opensearch:2.11.1              cbca8e35fb33       2.13GB          876MB   U    
panda-frontend:latest                            d34c3f844420       1.22GB          243MB   U    
postgres:15                                      42283dfbd8b9        648MB          157MB   U    
postgres:15-alpine                               1414298ea931        379MB          105MB   U    
postgres:16                                      468e1f126ca5        663MB          165MB   U    
postgres:16-alpine                               8ffca822c193        382MB          106MB   U    
postgres:18.1-trixie                             2d417d4c8805        665MB          161MB   U    
postgres:latest                                  bfe50b2b0ddd        665MB          161MB   U    
proyectodatosv1-db:latest                        033b46de132e        665MB          161MB        
proyectodatosv1:latest                           af3c115cea35        314MB         71.5MB   U    
redis:7-alpine                                   bb186d083732       61.4MB         17.7MB   U

$ docker history davidtechnologies/fdd-roto:v1
IMAGE          CREATED       CREATED BY                                      SIZE      COMMENT
27ddf4225455   3 hours ago   CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      3 hours ago   USER app                                        0B        buildkit.dockerfile.v0
<missing>      3 hours ago   RUN /bin/sh -c useradd -m app && chown -R ap…   86kB      buildkit.dockerfile.v0
<missing>      3 hours ago   COPY . . # buildkit                             16.4kB    buildkit.dockerfile.v0
<missing>      3 hours ago   RUN /bin/sh -c pip install --no-cache-dir -r…   13.5MB    buildkit.dockerfile.v0
<missing>      3 hours ago   COPY requirements.txt . # buildkit              12.3kB    buildkit.dockerfile.v0
<missing>      3 hours ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      5 days ago    CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      5 days ago    RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      5 days ago    RUN /bin/sh -c set -eux;   savedAptMark="$(a…   44.6MB    buildkit.dockerfile.v0
<missing>      5 days ago    ENV PYTHON_SHA256=5c8462af5790baf43a321a1559…   0B        buildkit.dockerfile.v0
<missing>      5 days ago    ENV PYTHON_VERSION=3.12.14                      0B        buildkit.dockerfile.v0
<missing>      5 days ago    ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      5 days ago    RUN /bin/sh -c set -eux;  apt-get update;  a…   4.99MB    buildkit.dockerfile.v0
<missing>      5 days ago    ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      5 days ago    ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      7 days ago    # debian.sh --arch 'arm64' out/ 'trixie' '@1…   110MB     debuerreotype 0.17
```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1. `FROM python:latest`: el tag se mueve y pesa ~1 GB; cambié a `FROM python:3.12-slim`, pineado y chico.
2. `COPY . .` antes del `pip install`: cualquier cambio en `app.py` tiraba el caché de la instalación; partí el COPY, primero `requirements.txt`, luego el código.
3. Sin `USER`: el proceso corría como root; agregué `useradd -m app && chown -R app /app` y `USER app`, ahora imprime `Corriendo como: app`.

## Una cosa que se me rompió

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.

La primera versión la construí solo para linux/amd64, como dice la guía para Apple Silicon. Al hacer la prueba de descarga en mi Mac, `docker run` falló con `no matching manifest for linux/arm64/v8`. Lo resolví reconstruyendo con `--platform linux/amd64,linux/arm64` y volviendo a subir: ahora corre en las dos sin banderas.
