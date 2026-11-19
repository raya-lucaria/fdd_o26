# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre: Cristopher Góngora
- Usuario de GitHub: cristoredentor
- Usuario de Docker Hub: cristophergongs

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text

docker version

Client: Docker Engine - Community
 Version:           29.8.1
 API version:       1.56
 Go version:        go1.26.8
 Git commit:        4a63305
 Built:             Tue Sep 15 16:25:42 2026
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          29.8.1
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.8
  Git commit:       464cd50
  Built:            Tue Sep 15 16:25:42 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.3.5
  GitCommit:        1294c24a7da8e5a793ed378161673abe94118892
 runc:
  Version:          1.5.1
  GitCommit:        v1.5.1-0-g8f2685a4
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0


docker images
IMAGE                     ID             DISK USAGE   CONTENT SIZE   EXTRA
cristophergongs/hola:v1   b8fbf3117ec8       12.1MB         3.63MB        
cristophergongs/roto:v1   b39db0c9863d        198MB         48.8MB    U   
hello-world:latest        5e2309035332       25.9kB         9.49kB        
hola-amb:latest           18abc4038a99       12.1MB         3.63MB        
hola-cmd:latest           b85016c28647       12.1MB         3.63MB        
hola-ent:latest           3d32d48328b2       12.1MB         3.63MB        
hola:latest               b8fbf3117ec8       12.1MB         3.63MB        
info:latest               c6be3da306cb        117MB         29.8MB        
roto:v1                   b39db0c9863d        198MB         48.8MB    U   
roto:v2                   dc15e7f2df23       1.64GB          421MB        
roto:v3                   d5ef7057461e        198MB         48.8MB    U   
ubuntu:latest             da6fc2be5478        160MB         45.3MB    U   


docker history <tu-usuario>/<tu-imagen>
IMAGE          CREATED      CREATED BY                                      SIZE      COMMENT
b39db0c9863d   4 days ago   CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      4 days ago   USER app                                        0B        buildkit.dockerfile.v0
<missing>      4 days ago   RUN /bin/sh -c useradd -m app && chown -R ap…   86kB      buildkit.dockerfile.v0
<missing>      4 days ago   COPY . . # buildkit                             16.4kB    buildkit.dockerfile.v0
<missing>      4 days ago   RUN /bin/sh -c pip install -r requirements.t…   14.8MB    buildkit.dockerfile.v0
<missing>      4 days ago   COPY requirements.txt . # buildkit              12.3kB    buildkit.dockerfile.v0
<missing>      4 days ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      5 days ago   CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      5 days ago   RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      5 days ago   RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.4MB    buildkit.dockerfile.v0
<missing>      5 days ago   ENV PYTHON_SHA256=5c8462af5790baf43a321a1559…   0B        buildkit.dockerfile.v0
<missing>      5 days ago   ENV PYTHON_VERSION=3.12.14                      0B        buildkit.dockerfile.v0
<missing>      5 days ago   ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      5 days ago   RUN /bin/sh -c set -eux;  apt-get update;  a…   4.95MB    buildkit.dockerfile.v0
<missing>      5 days ago   ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      5 days ago   ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      6 days ago   # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.7MB    debuerreotype 0.17


```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1.En la primera línea del Dockerfile Utiliza python latest, la cual puede hacer que un código que corra hoy no lo haga después por incompatibilidad de versiones. 
Lo que hice fue cambiarlo  por `python:3.12-slim` para fijar la versión y reducir el tamaño.

2.Tiene copy .. antes del run pip install, esto esta mál pues cualquier cambio en tu código invalidaría la caché y reinstalaría todas las
 dependencias cada vez.  Separé primero `COPY requirements.txt .`, después `RUN pip install -r requirements.txt` y al final `COPY . .`.

 
3.No se asignaba un  user, por lo que el programa se ejecutaba como `root`. Para arreglarlo cree el usuario app.
 Lo comprobé con `docker run --rm roto:v1 id`, que mostró uid=1000(app) gid=1000(app) groups=1000(app). 

## Una cosa que se me rompió

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.

Se me complicó comprobar que la imágen pudiera replicarse desde otro dispositivo, sin embargo me ayudó mucho llevar el curso Introductorio de Docker para aprender a usar varios comandos utilizados en esta tarea. 
