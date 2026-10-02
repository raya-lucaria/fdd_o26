# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre: Fernanda León
- Usuario de GitHub: fernandalh25
- Usuario de Docker Hub: fersy25

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text
docker version
Client:
 Version:           29.1.3
 API version:       1.52
 Go version:        go1.25.5
 Git commit:        f52814d
 Built:             Fri Dec 12 14:48:46 2025
 OS/Arch:           darwin/arm64
 Context:           desktop-linux

Server: Docker Desktop 4.56.0 (214940)
 Engine:
  Version:          29.1.3
  API version:      1.52 (minimum version 1.44)
  Go version:       go1.25.5
  Git commit:       fbf3ed2
  Built:            Fri Dec 12 14:50:40 2025
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


docker images
                                                                                    i Info →   U  In Use
IMAGE                           ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine:3.20                     d9e853e87e55       13.7MB         4.17MB        
apache/hadoop:3.4.3             127774dadab4        2.2GB          750MB        
cassandra:5.0                   d07910a14210        569MB          170MB        
fersy25/fersy-tarea-08:latest   2ee243c76ecc        206MB         50.7MB      
hello-world:latest              5e2309035332       22.6kB         10.3kB    U   
mongo:7.0                       4510cf3d7050       1.09GB          274MB        
neo4j:5                         b357872da95a        982MB          355MB        
neo4j:ubi9                      d28090e169be       1.14GB          383MB        
postgres:16                     a3b7f434b2dc        663MB          165MB        
postgres:17                     f4c66b820c6f        667MB          166MB        
python:3.12-slim                2f17fc044b57        382MB           89MB        
ubuntu:24.04                    008173c23f95        141MB         30.9MB   

docker history fersy25/fersy-tarea-08 

IMAGE          CREATED             CREATED BY                                      SIZE      COMMENT
2ee243c76ecc   3 minutes ago       CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      3 minutes ago       USER appuser                                    0B        buildkit.dockerfile.v0
<missing>      3 minutes ago       RUN /bin/sh -c useradd -m appuser # buildkit    69.6kB    buildkit.dockerfile.v0
<missing>      About an hour ago   RUN /bin/sh -c pip install -r requirements.t…   16.1MB    buildkit.dockerfile.v0
<missing>      About an hour ago   COPY app.py . # buildkit                        12.3kB    buildkit.dockerfile.v0
<missing>      About an hour ago   COPY requirements.txt . # buildkit              12.3kB    buildkit.dockerfile.v0
<missing>      About an hour ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      9 days ago          CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      9 days ago          RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      9 days ago          RUN /bin/sh -c set -eux;   savedAptMark="$(a…   43.1MB    buildkit.dockerfile.v0
<missing>      9 days ago          ENV PYTHON_SHA256=3b48dac8fb59f62eaa67ac83c1…   0B        buildkit.dockerfile.v0
<missing>      9 days ago          ENV PYTHON_VERSION=3.14.7                       0B        buildkit.dockerfile.v0
<missing>      9 days ago          RUN /bin/sh -c set -eux;  apt-get update;  a…   10.4MB    buildkit.dockerfile.v0
<missing>      9 days ago          ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      10 days ago         # debian.sh --arch 'amd64' out/ 'bookworm' '…   85.3MB    debuerreotype 0.17
```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1.Añadí el tag al FROM ya que tenía latest y podría tener una versión que no tiene mi programa, lo cambié a una fija que encontré en la página oficial de imagenes de pyhton : 3.14.7-slim-bookworm
2.Completé el COPY . . que estaba trayendo archivos innecesarios, sólo dejé el requirements.txt y añadí otro copy con appy.py porque estaba en el CMD, que de un inició si se incluía en el COPY . ., pero al modificarlo era necesario añadir ese archivo específico: COPY app.py .
3.Cambié el user para que no fuera el de root

## Una cosa que se me rompió
No utilicé el comando correcto para construir la imagen y que se abriera en linux dado mi sistema operativo, lo borré y volví a construir

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.
Al inicio no entendia bien el flujo completo de Docker: Dockerfile, construccion de la imagen y creacion del contenedor. Confundia que instrucciones ocurrian al hacer docker build y cuales al hacer docker run. Con la practica entendi que primero se construye una imagen a partir del Dockerfile y despues, a partir de esa imagen, se crean y ejecutan los contenedores. Esto me ayudo a entender mejor que estaba haciendo cada comando y en que etapa del proceso ocurrian los errores.
