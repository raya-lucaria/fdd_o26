# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre:Fernando Arellano Gonzalez
- Usuario de GitHub:FerArGo56
- Usuario de Docker Hub:ferargo

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text
docker version
MacBook-Air-de-Ana-3:08_contenedores anamari$ docker version
Client:
 Version:           29.8.0
 API version:       1.56
 Go version:        go1.26.8
 Git commit:        88096ef
 Built:             Thu Sep  3 21:49:43 2026
 OS/Arch:           darwin/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.92.0 (240144)
 Engine:
  Version:          29.8.0
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.8
  Git commit:       3ce5872
  Built:            Thu Sep  3 21:51:20 2026
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
MacBook-Air-de-Ana-3:08_contenedores anamari$ docker version
Client:
 Version:           29.8.0
 API version:       1.56
 Go version:        go1.26.8
 Git commit:        88096ef
 Built:             Thu Sep  3 21:49:43 2026
 OS/Arch:           darwin/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.92.0 (240144)
 Engine:
  Version:          29.8.0
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.8
  Git commit:       3ce5872
  Built:            Thu Sep  3 21:51:20 2026
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
MacBook-Air-de-Ana-3:08_contenedores anamari$ docker images
                                                            i Info →   U  In Use
IMAGE                           ID             DISK USAGE   CONTENT SIZE   EXTRA
ferargo/08_contenedores:latest
                                5c2d452b851f        117MB         29.8MB        
hello-world:latest              5e2309035332       25.9kB         9.49kB    U   
postgres:16                     f992505e18f1        641MB          166MB  

docker history <tu-usuario>/<tu-imagen>
MacBook-Air-de-Ana-3:08_contenedores anamari$ docker history ferargo/08_contenedores:latest
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
5c2d452b851f   30 minutes ago   CMD ["./info.sh"]                               0B        buildkit.dockerfile.v0
<missing>      30 minutes ago   RUN /bin/sh -c chmod +x info.sh # buildkit      12.3kB    buildkit.dockerfile.v0
<missing>      30 minutes ago   COPY info.sh . # buildkit                       12.3kB    buildkit.dockerfile.v0
<missing>      30 minutes ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      11 days ago      /bin/sh -c #(nop)  CMD ["/bin/bash"]            0B        
<missing>      11 days ago      /bin/sh -c #(nop) ADD file:43d479b270bbaf479…   87.6MB    
<missing>      11 days ago      /bin/sh -c #(nop)  LABEL org.opencontainers.…   0B        
<missing>      11 days ago      /bin/sh -c #(nop)  ARG LAUNCHPAD_BUILD_ARCH     0B        
<missing>      11 days ago      /bin/sh -c #(nop)  ARG RELEASE                  0B        
MacBook-Air-de-Ana-3:08_contenedores anamari$ 

```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1. El script usaba `#!/bin/bash`, pero Alpine no viene con bash instalado. Consecuencia: Al correr el contenedor me tiraba error de que no encontraba el archivo. Cambio: Cambié la primera línea de `info.sh` a `#!/bin/sh`.
2. Le faltaba la barra `/` a la ruta del archivo en el `ENTRYPOINT`. Consecuencia: Docker no sabía en qué carpeta buscar el script para ejecutarlo. Cambio: Lo arreglé poniendo la ruta completa `ENTRYPOINT ["/info.sh"]`.
3. La instrucción `COPY` no tenía bien marcado el destino. Consecuencia: No copiaba `info.sh` dentro de la raíz del contenedor al hacer el build. Cambio: Dejé la línea correcta como `COPY info.sh /info.sh`.

## Una cosa que se me rompió

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.
Al intentar subir la imagen a Docker Hub me daba error porque estaba usando
mi usuario de GitHub (FerArGo56) en mayúsculas en vez de mi usuario de Docker
Hub (ferargo).Lo solucioné etiquetando de nuevo la imagen en minúsculas con
docker tag, iniciando sesión explícita con docker login -u ferargo.
Lo que más me costó entender fue cómo se relacionan las etiquetas (tags)
con el usuario de Docker Hub y por qué Docker se confundía con las mayúsculas.
