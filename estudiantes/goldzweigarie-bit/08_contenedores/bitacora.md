# Bitácora de la unidad 08

## Quién soy

- Nombre: Arié Goldzweig
- Usuario de GitHub: goldzweigarie-bit
- Usuario de Docker Hub: goldz177

## Qué corrí

```text
$ docker version
Client:
 Version:           29.7.2
 API version:       1.55
 Go version:        go1.26.5
 Git commit:        a7dcaa6
 Built:             Wed Aug  5 18:27:50 2026
 OS/Arch:           darwin/arm64
 Context:           desktop-linux

Server: Docker Desktop 4.86.0 (236216)
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

$ docker images goldz177/app-docker
IMAGE                        ID             DISK USAGE   CONTENT SIZE   EXTRA
goldz177/app-docker:latest   4f2bb0ecd65f        117MB         29.8MB        

$ docker history --no-trunc goldz177/app-docker:latest
IMAGE                                                                     CREATED          CREATED BY                                                                                          SIZE      COMMENT
sha256:4f2bb0ecd65ff4d51a3adc34ae8204bd24e30249de1a6913ef3f263d6dac5596   38 seconds ago   CMD ["./info.sh"]                                                                                   0B        buildkit.dockerfile.v0
<missing>                                                                 38 seconds ago   RUN /bin/sh -c chmod +x info.sh && date -u '+%Y-%m-%d %H:%M:%S UTC' > /app/fecha_build # buildkit   28.7kB    buildkit.dockerfile.v0
<missing>                                                                 39 seconds ago   COPY info.sh . # buildkit                                                                           12.3kB    buildkit.dockerfile.v0
<missing>                                                                 39 seconds ago   WORKDIR /app                                                                                        8.19kB    buildkit.dockerfile.v0
<missing>                                                                 2 months ago     /bin/sh -c #(nop)  CMD ["/bin/bash"]                                                                0B        
<missing>                                                                 2 months ago     /bin/sh -c #(nop) ADD file:43d479b270bbaf47965cfc86b37f4c517bda83ddefda6f708f98c3b2b7d15396 in /    87.6MB    
<missing>                                                                 2 months ago     /bin/sh -c #(nop)  LABEL org.opencontainers.image.version=24.04                                     0B        
<missing>                                                                 2 months ago     /bin/sh -c #(nop)  ARG LAUNCHPAD_BUILD_ARCH                                                         0B        
<missing>                                                                 2 months ago     /bin/sh -c #(nop)  ARG RELEASE                                                                      0B        
```

## Los tres defectos de `roto/Dockerfile`

1. `FROM python:latest`: `latest` es una etiqueta que se mueve, así que la imagen de hoy no es la de mañana (otro Python, otro digest) y además pesa cerca de un giga. Se comprueba con `docker images python`. Lo cambié por `FROM python:3.12-slim`, una versión fija y varias veces más chica.
2. `COPY . .` antes del `RUN pip install`: como copia también `app.py`, cualquier cambio de una línea de código invalida esa capa y vuelve a correr todo el `pip install`. Se comprueba tocando `app.py` y reconstruyendo: el paso de `pip install` corre otra vez, sin `CACHED`. Lo partí en dos: primero `COPY requirements.txt .` y `RUN pip install`, y después `COPY . .`, así la capa de dependencias se queda en caché.
3. No había ninguna instrucción `USER`: el proceso corría como `root`, y lo que escribiera en un volumen montado quedaría de `root`. Se comprueba con `docker run --rm` y la línea `Corriendo como: root` que imprime `app.py`. Agregué `RUN useradd -m appuser` y `USER appuser` después de instalar y copiar, para que la app corra sin privilegios.

## Una cosa que se me rompió

Usé usuario de GitHub en vez de Docker Hub (error de auth). En Mac ARM64, docker run falló buscando arm64. Solución: tag correcto goldz177 y --platform linux/amd64.
