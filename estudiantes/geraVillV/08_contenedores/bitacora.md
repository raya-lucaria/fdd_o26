# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre: Gerardo Villanueva Vargas
- Usuario de GitHub: geraVillV
- Usuario de Docker Hub: geraplayer

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text
docker version
Client: Docker Engine - Community
 Version:           29.8.1
 API version:       1.56
 Go version:        go1.26.8
 Git commit:        4a63305
 Built:             Tue Sep 15 16:30:07 2026
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          29.8.1
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.8
  Git commit:       464cd50
  Built:            Tue Sep 15 16:25:58 2026
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
IMAGE                        ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine:3.20                  d9e853e87e55       13.2MB         3.71MB        
cassandra:5.0                da9dad3aaf67        550MB          174MB    U   
geraplayer/roto-fix:latest   a067676c0ba0        206MB         51.7MB        
hello-world:latest           5e2309035332       21.8kB         9.49kB    U   
info-test:latest             a8bf6fd16efa        115MB         29.8MB        
mongo:7.0                    9854f7139445       1.18GB          299MB    U   
neo4j:ubi9                   93a9e81f4da7       1.04GB          374MB    U   
postgres:16                  f1c3376c26f2        639MB          166MB        
postgres:17                  67f41722b7a8        643MB          167MB        
python:3.12-slim             78387bc3881b        189MB         48.4MB        
roto-fix:latest              a067676c0ba0        206MB         51.7MB        
ubuntu:24.04                 b3cc40b72b93        117MB         31.7MB 


docker history geraplayer/roto-fix:latest
IMAGE          CREATED        CREATED BY                                      SIZE      COMMENT
a067676c0ba0   5 hours ago    CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      5 hours ago    USER appuser                                    0B        buildkit.dockerfile.v0
<missing>      5 hours ago    RUN /bin/sh -c useradd --create-home appuser…   53.2kB    buildkit.dockerfile.v0
<missing>      5 hours ago    COPY . . # buildkit                             16.4kB    buildkit.dockerfile.v0
<missing>      27 hours ago   RUN /bin/sh -c pip install -r requirements.t…   13.8MB    buildkit.dockerfile.v0
<missing>      27 hours ago   COPY requirements.txt . # buildkit              4.1kB     buildkit.dockerfile.v0
<missing>      27 hours ago   WORKDIR /app                                    0B        buildkit.dockerfile.v0
```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1. `FROM python:latest` usaba una imagen base sin versión fija y con más paquetes de los necesarios, lo que infla el tamaño final y hace el build no reproducible entre corridas. Cambié a `python:3.12-slim`, y el tamaño final quedó en 206MB (disk usage) / 51.7MB (content size), bajo el límite de 300MB.
2. `COPY . .` estaba antes de `RUN pip install -r requirements.txt`, así que cualquier cambio en el código invalidaba el cache de la capa de instalación de dependencias, obligando a reinstalarlas en cada build. Reordené a `COPY requirements.txt .` + `RUN pip install` primero, y `COPY . .` al final. Se confirma en `docker history`: la capa de `pip install` (13.8MB) quedó separada de la capa de `COPY . .` (16.4kB), así que un cambio en el código solo invalida esa última capa pequeña.
3. El Dockerfile no declaraba con qué usuario correr el proceso, así que el contenedor seguía ejecutándose como `root` por defecto. Esto importa porque cualquier archivo que el proceso escriba en una carpeta montada desde la máquina host queda a nombre de root, y luego no se puede borrar sin privilegios elevados. Agregué `RUN useradd --create-home appuser` después de instalar las dependencias, y `USER appuser` antes del `CMD`, para que el proceso corra con un usuario sin privilegios. Confirmado: la salida de `docker run` ahora dice "Corriendo como: appuser" en vez de root, y en `docker history` aparece la capa `USER appuser` como último paso antes del `CMD`.

## Una cosa que se me rompió

La verdad no se me rimpio nada, pero la parte que mas me costo entender fue el orden del COPY. 
A la hora de subirlo al git me detecto un error ya que no habia cambiado del root a un user para que pudiera correr sin privilegios. Pero ya en esta nueva version ya lo modifique.
