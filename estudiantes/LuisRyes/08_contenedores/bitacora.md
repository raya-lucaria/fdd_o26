# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre:Luis Fernando Reyes Altamirano
- Usuario de GitHub:LuisRyes
- Usuario de Docker Hub:luisryes

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text
docker version
Client:
 Version:           29.7.2
 API version:       1.55
 Go version:        go1.26.5
 Git commit:        a7dcaa6
 Built:             Wed Aug  5 18:27:50 2026
 OS/Arch:           darwin/arm64
 Context:           desktop-linux

Server: Docker Desktop 4.87.0 (236836)
 Engine:
  Version:          29.7.2
  API version:      1.55 (minimum version 1.40)
  Go version:       go1.26.5
  Git commit:       6a43e3d
  Built:            Wed Aug  5 18:28:35 2026
  OS/Arch:          linux/arm64
  Experimental:     false
 containerd:
  Version:          v2.2.5
  GitCommit:        e53c7c1516c3b2bff98eb76f1f4117477e6f4e66
 runc:
  Version:          1.3.6
  GitCommit:        v1.3.6-0-g491b69ba
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0


docker images
                                                                                                                                                                                      i Info →   U  In Use
IMAGE                   ID             DISK USAGE   CONTENT SIZE   EXTRA
luisryes/mi-imagen:v1   6c445695389b        195MB         47.7MB        


docker history luisryes/mi-imagen:v1
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
6c445695389b   21 minutes ago   CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      21 minutes ago   COPY . . # buildkit                             16.4kB    buildkit.dockerfile.v0
<missing>      21 minutes ago   RUN /bin/sh -c pip install --no-cache-dir -r…   13.3MB    buildkit.dockerfile.v0
<missing>      21 minutes ago   COPY requirements.txt . # buildkit              12.3kB    buildkit.dockerfile.v0
<missing>      21 minutes ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      5 days ago       CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      5 days ago       RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      5 days ago       RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.4MB    buildkit.dockerfile.v0
<missing>      5 days ago       ENV PYTHON_SHA256=5c8462af5790baf43a321a1559…   0B        buildkit.dockerfile.v0
<missing>      5 days ago       ENV PYTHON_VERSION=3.12.14                      0B        buildkit.dockerfile.v0
<missing>      5 days ago       ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      5 days ago       RUN /bin/sh -c set -eux;  apt-get update;  a…   4.95MB    buildkit.dockerfile.v0
<missing>      5 days ago       ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      5 days ago       ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      6 days ago       # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.6MB    debuerreotype 0.17


```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1.La version que usaba de python era muy pesada y no cumplia con lo pedido, por eso la cambie a una más ligera
2.El COPY . . no usaba eficientemente las capas de docker, por eso puse la instalacion arriba de COPY . . 
3.el pip install no tenia banderas de limpieza de cache por eso se lo añadi y no habia USER que no sea root, y las instrucciones pedian otro,
 asi que puse el nobody

## Una cosa que se me rompió

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.

Como mi compu tiene el Apple silicone, tuve que configurar que corriera en linux, pero a mi no me corrio por tener Mac. Al final lo
que hice fue ponerle que corriera con linux/amd64 como las instruccione decian. Me costo entender bien que estaba haciendo en algunas partes, pero
lo investigue y al final con los cursos de datacamp y viendo las notas le entendí.
